"""Download public sources, keep every distinct version unchanged, record it in the manifest.

A file is stored again only when its bytes change. Each version lands in
data/raw/<source>/<retrieved date>/<file name> and the manifest records the URL,
retrieval time, size, SHA-256 and the server's Last-Modified/ETag headers.
"""
import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import PurePosixPath
from urllib.parse import urlparse

from . import registry
from .paths import CHECKS, MANIFEST, RAW, ROOT

UA = "food-insecurity-atlas-pipeline/0.1 (+https://github.com/LinusConradM/feeding_america)"


def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load(path, default):
    return json.loads(path.read_text()) if path.exists() else default


def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def http_get(url, tries=4):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    for i in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.status, dict(r.headers), r.read()
        except urllib.error.HTTPError as e:
            if e.code in (404, 410):
                return e.code, dict(e.headers), b""
            if i == tries - 1:
                raise
        except (urllib.error.URLError, TimeoutError):
            if i == tries - 1:
                raise
        time.sleep(2 ** (i + 1))


class Store:
    def __init__(self):
        self.manifest = load(MANIFEST, {"sources": {}})
        self.checks = load(CHECKS, {})
        self.changed = []

    def record(self, sid, url, body, headers, filename=None, meta=None):
        sha = hashlib.sha256(body).hexdigest()
        src = self.manifest["sources"].setdefault(sid, {"versions": []})
        src["url"] = url
        self.checks[sid] = {"checked_at": now(), "status": "ok"}
        if src["versions"] and src["versions"][-1]["sha256"] == sha:
            return src["versions"][-1], False
        name = filename or PurePosixPath(urlparse(url).path).name
        day = now()[:10]
        path = RAW / sid / day / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
        version = {
            "path": str(path.relative_to(ROOT)),
            "sha256": sha,
            "bytes": len(body),
            "retrieved_at": now(),
            "last_modified": headers.get("Last-Modified"),
            "etag": headers.get("ETag"),
            **(meta or {}),
        }
        src["versions"].append(version)
        self.changed.append(sid)
        return version, True

    def fail(self, sid, err):
        self.checks[sid] = {"checked_at": now(), "status": "error", "error": str(err)[:300]}

    def save(self):
        save(MANIFEST, self.manifest)
        save(CHECKS, self.checks)


def fetch_usda(store):
    for sid, url in registry.USDA_FILES.items():
        try:
            status, headers, body = http_get(url)
            if status != 200 or not body:
                raise RuntimeError(f"HTTP {status}")
            store.record(sid, url, body, headers)
        except Exception as e:
            store.fail(sid, e)


def acs_vintages():
    """Every ACS 5-year vintage from the first one used up to the newest the API serves."""
    found, v = [], registry.ACS_FIRST_VINTAGE
    while True:
        status, _, body = http_get(registry.ACS_API.format(vintage=v))
        if status != 200 or not body:
            break
        found.append((v, body))
        v += 1
    return found


def fetch_acs(store):
    try:
        vintages = acs_vintages()
        if not vintages:
            raise RuntimeError("Census API returned no ACS 5-year vintage")
        vintage, meta_body = vintages[-1]
        base = registry.ACS_API.format(vintage=vintage)
        get = ",".join(registry.ACS_VARS)
        meta = json.loads(meta_body)
        ds = (meta.get("dataset") or [{}])[0]
        info = {"vintage": vintage, "api_modified": ds.get("modified"), "api_title": ds.get("title")}
        store.record("acs-meta", base, meta_body, {}, filename=f"acs5_{vintage}_meta.json", meta=info)
        for geo, q in [("us", "us:1"), ("state", "state:*"), ("county", "county:*")]:
            url = f"{base}?get={get}&for={q}"
            key = os.environ.get("CENSUS_API_KEY")
            if not key:
                raise RuntimeError("CENSUS_API_KEY is not set; the Census API now requires a key")
            status, headers, body = http_get(f"{url}&key={key}")
            if status != 200:
                raise RuntimeError(f"HTTP {status} for {url}")
            try:
                rows = json.loads(body)
            except ValueError:
                raise RuntimeError(f"non-JSON reply for {geo}: {body[:300]!r}")
            if len(rows) < 2:
                raise RuntimeError(f"empty ACS response for {geo}")
            store.record(f"acs-{geo}", url, body, headers, filename=f"acs5_{vintage}_{geo}.json", meta=info)
    except Exception as e:
        store.fail("acs-county", e)


def fetch_geo(store, years):
    for layer in ("county", "state"):
        sid = f"geo-{layer}"
        last = None
        for year in years:
            url = registry.GEO_URL.format(year=year, layer=layer)
            try:
                status, headers, body = http_get(url)
            except Exception as e:
                last = e
                continue
            if status == 200 and body:
                store.record(sid, url, body, headers, meta={"boundary_year": year})
                break
            last = f"HTTP {status} for {url}"
        else:
            store.fail(sid, last)


def released_editions(text):
    """Editions the page presents as released: "Map the Meal Gap N" followed within 400
    characters by its data year N-2 (every edition reports data from two years earlier).
    A bare mention, such as a planned future edition, does not count. Returns
    {edition: [context snippets]} for every mention, and the set that look released."""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    mentions, released = {}, set()
    for m in re.finditer(r"Map the Meal Gap (20\d\d)", text):
        ed = int(m[1])
        after = text[m.end(): m.end() + 400]
        snippet = text[max(0, m.start() - 120): m.end() + 200].strip()
        mentions.setdefault(ed, []).append(snippet)
        if str(ed - 2) in after:
            released.add(ed)
    return mentions, released


def watch_mmg(store, known_editions):
    """Look for a Map the Meal Gap edition newer than the newest file in the private repo."""
    mentions, released = {}, set()
    for url in registry.MMG_PAGES:
        try:
            status, _, body = http_get(url)
            if status == 200:
                m, r = released_editions(body.decode("utf-8", "replace"))
                for k, v in m.items():
                    mentions.setdefault(k, []).extend(v)
                released |= r
        except Exception as e:
            store.fail("mmg-watch", e)
            return None
    newest_site = max(released) if released else None
    newest_local = max(known_editions) if known_editions else None
    store.checks["mmg-watch"] = {
        "checked_at": now(),
        "status": "ok" if newest_site else "error",
        "newest_on_site": newest_site,
        "newest_in_data_repo": newest_local,
        "mentioned": sorted(mentions),
    }
    if newest_site and newest_local and newest_site > newest_local:
        (ROOT / "mmg_watch.txt").write_text("\n\n".join(f"> {s}" for s in mentions[newest_site][:3]))
        return newest_site
    return None
