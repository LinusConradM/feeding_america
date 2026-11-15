"""Parse the stored raw files, validate them, and write the JSON the site reads."""
import json
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from . import acs, geo, mmg, sources, usda
from .fetch import load
from .paths import CHECKS, MANIFEST, MMG_DIR, ROOT, SITE_DATA


class Checks:
    def __init__(self):
        self.items = []

    def add(self, area, name, ok, detail="", level="error"):
        self.items.append({"area": area, "check": name, "ok": bool(ok), "level": level, "detail": detail})
        return ok

    @property
    def failed(self):
        return [c for c in self.items if not c["ok"] and c["level"] == "error"]


def latest(manifest, sid):
    src = manifest["sources"].get(sid)
    if not src or not src["versions"]:
        return None
    v = dict(src["versions"][-1])
    v["url"] = src["url"]
    v["abs"] = ROOT / v["path"]
    return v


def r(x, n):
    return None if x is None or (isinstance(x, float) and np.isnan(x)) or pd.isna(x) else round(float(x), n)


def i(x):
    return None if x is None or pd.isna(x) else int(round(float(x)))


def ledger_entry(v):
    return None if v is None else {k: v.get(k) for k in ("url", "path", "sha256", "bytes", "retrieved_at", "last_modified")}


# ---------------------------------------------------------------- USDA

def build_usda(manifest, ck):
    inter, pdf, mapd = (latest(manifest, s) for s in ("usda-interactive", "usda-err358-pdf", "usda-mapdata"))
    if not (inter and pdf and mapd):
        ck.add("USDA", "files present", False, "USDA ERS files have not been fetched")
        return None
    hh = usda.national_households(inter["abs"])
    ch = usda.national_children(inter["abs"])
    t1 = usda.table_1a(pdf["abs"])
    ppl = t1["All individuals"]
    cross = t1["Households"].merge(hh, on="year")
    ck.add("USDA", "Table 1A households match the ERS data file",
           len(cross) == len(hh) and (cross.fi_k == cross.hh_fi_k).all() and (cross.fi_pct == cross.hh_fi_pct).all(),
           f"{len(cross)} years compared")
    years = list(range(2001, int(hh.year.max()) + 1))
    ck.add("USDA", "national series has every year from 2001", sorted(hh.year) == years and sorted(ppl.year) == years,
           f"{hh.year.min()}-{hh.year.max()}")
    nat = hh.merge(ppl.rename(columns={"total_k": "ppl_total_k", "fi_k": "ppl_fi_k", "fi_pct": "ppl_fi_pct"}), on="year") \
            .merge(ch, on="year", how="left")
    ck.add("USDA", "rates within 0-40%", nat[["hh_fi_pct", "ppl_fi_pct", "ch_fi_pct"]].stack().between(0, 40).all())
    ck.add("USDA", "people share = people in FI households / all people (±0.1 pt)",
           (abs(nat.ppl_fi_k / nat.ppl_total_k * 100 - nat.ppl_fi_pct) <= 0.1).all())

    st, period = usda.states(mapd["abs"])
    us = st[st.state == "U.S."].iloc[0]
    st = st[st.state != "U.S."]
    ck.add("USDA", "state file has all 50 states and DC", st.state.nunique() == 51 and len(st) == 51, f"{st.state.nunique()} rows")
    ck.add("USDA", "every state has a margin of error", st.fi_moe.notna().all())
    ck.add("USDA", "state rates within 3-30%", st.fi_pct.between(3, 30).all())

    def sig(row):
        if row.fi_sig.lower() != "yes":
            return "ns"
        return "higher" if row.fi_pct > us.fi_pct else "lower"

    return {
        "national": [{
            "year": int(x.year),
            "hh_pct": float(x.hh_fi_pct), "hh_k": int(x.hh_fi_k), "hh_total_k": int(x.hh_total_k),
            "ppl_pct": float(x.ppl_fi_pct), "ppl_k": int(x.ppl_fi_k), "ppl_total_k": int(x.ppl_total_k),
            "ch_pct": r(x.ch_fi_pct, 1), "ch_k": i(x.ch_fi_k),
        } for x in nat.itertuples()],
        "states": {
            "period": list(period) if period else None,
            "us": {"pct": r(us.fi_pct, 2), "moe": r(us.fi_moe, 2), "households": i(us.households), "interviewed": i(us.interviewed)},
            "rows": {x.state: {"pct": r(x.fi_pct, 2), "moe": r(x.fi_moe, 2), "sig": sig(x),
                               "households": i(x.households), "interviewed": i(x.interviewed)} for x in st.itertuples()},
        },
        "files": {"interactive": ledger_entry(inter), "pdf": ledger_entry(pdf), "mapdata": ledger_entry(mapd)},
    }


# ---------------------------------------------------------------- MMG

def build_mmg(ck):
    if not MMG_DIR.exists():
        ck.add("MMG", "files present", False, f"no Map the Meal Gap files at {MMG_DIR}")
        return None
    eds = mmg.discover(MMG_DIR)
    ck.add("MMG", "editions found", bool(eds), ", ".join(str(e.edition) for e in eds))
    if not eds:
        return None
    ck.add("MMG", "each edition is named two years after its newest data year",
           all(e.edition - e.data_years[-1] == 2 for e in eds))
    s = mmg.state_series(eds)
    for y, g in s.groupby("year"):
        ck.add("MMG", f"{y} state rows: 50 states + DC, unique", len(g) == 51 and g.state.nunique() == 51, f"{len(g)} rows")
    ck.add("MMG", "state rates within 2-40%", s.fi_rate.between(0.02, 0.40).all(),
           f"{s.fi_rate.min():.3f}-{s.fi_rate.max():.3f}")
    ck.add("MMG", "state child rates within 2-50%", s.child_rate.between(0.02, 0.50).all())
    ck.add("MMG", "no missing state counts", s[["fi_n", "child_n"]].notna().all().all())

    newest = eds[-1]
    year = newest.data_years[-1]
    c = mmg.read_counties(newest, year)
    ck.add("MMG", f"{year} county FIPS unique and 5 digits", c.fips.is_unique and c.fips.str.fullmatch(r"\d{5}").all(), f"{len(c)} rows")
    ck.add("MMG", f"{year} county rows between 3,100 and 3,250", 3100 <= len(c) <= 3250, f"{len(c)}")
    miss = c[c.fi_rate.isna()]
    ck.add("MMG", f"{year} counties without an estimate: 5 or fewer", len(miss) <= 5,
           ", ".join(f"{n}, {st}" for n, st in zip(miss.name, miss.state)))
    ck.add("MMG", "county rates within 0-60%", c.fi_rate.dropna().between(0, 0.6).all(),
           f"{c.fi_rate.min():.3f}-{c.fi_rate.max():.3f}")
    ck.add("MMG", "cost per meal within $1-$12", c.cost_per_meal.dropna().between(1, 12).all(),
           f"${c.cost_per_meal.min():.2f}-${c.cost_per_meal.max():.2f}")
    ck.add("MMG", "every county's state is a state in the file", c.state.isin(mmg.STATES).all())
    ck.add("MMG", "RUCC 2023 codes are 1-9", c.rucc2023.dropna().between(1, 9).all())
    # State figures are aggregated from congressional districts, not from counties, so the
    # two sums differ. Tolerate up to 6% and report the gap.
    st_sum = s[s.year == year].fi_n.sum()
    gap = abs(c.fi_n.sum() - st_sum) / st_sum
    ck.add("MMG", "county total within 6% of state total (states are built from districts)", gap <= 0.06,
           f"counties {c.fi_n.sum():,.0f}, states {st_sum:,.0f}, gap {gap:.1%}")

    def src(y):
        e = mmg.edition_for_year(eds, y)
        return e.edition

    states = {}
    for x in s.sort_values("year").itertuples():
        states.setdefault(x.state, []).append({
            "y": int(x.year), "fi": r(x.fi_rate, 4), "fn": i(x.fi_n), "ch": r(x.child_rate, 4), "cn": i(x.child_n),
            "orig": int(x.year) + 2, "file": int(x.edition),
        })
    editions = [{
        "edition": e.edition, "label": e.label, "data_years": e.data_years, "version": e.version,
        "release_date": e.release_date, "file": e.path.name, "sha256": e.sha256,
    } for e in eds]
    counties = {x.fips: [x.name, x.state, r(x.fi_rate, 3), i(x.fi_n), r(x.child_rate, 3), i(x.child_n),
                         r(x.cost_per_meal, 2), i(x.shortfall), i(x.rucc2023)] for x in c.itertuples()}
    return {"editions": editions, "states": states, "county_year": year, "county_edition": newest.edition,
            "counties": counties, "missing": [[n, st] for n, st in zip(miss.name, miss.state)],
            "county_df": c}


# ---------------------------------------------------------------- ACS + SNAP comparison

def build_snap(manifest, m, ck):
    v = latest(manifest, "acs-county")
    if v is None:
        ck.add("ACS", "files present", False, "ACS tables have not been fetched (the Census API needs CENSUS_API_KEY)", level="warn")
        return {"status": "blocked", "reason": "The Census API now requires a key. ACS SNAP data will appear once the pipeline has one."}
    vint = v.get("vintage")
    ac = acs.tidy(acs.read(v["abs"]))
    ck.add("ACS", "county FIPS unique", ac.fips.is_unique, f"{len(ac)} rows")
    ck.add("ACS", "SNAP shares within 0-100%", ac.snap_share.dropna().between(0, 1).all())
    us_v = latest(manifest, "acs-us")
    us = acs.tidy(acs.read(us_v["abs"])).iloc[0] if us_v else None

    c = m["county_df"].merge(ac, on="fips", how="left")
    unmatched = c[c.snap_share.isna() & c.fi_rate.notna()]
    ck.add("ACS", "MMG counties found in ACS", len(unmatched) <= 5, ", ".join(unmatched.fips))
    d = c.dropna(subset=["fi_rate", "snap_share", "poverty_rate"]).copy()
    d["dec"] = pd.qcut(d.fi_rate.rank(method="first"), 10, labels=False)
    deciles = []
    for k, g in d.groupby("dec"):
        deciles.append({"lo": r(g.fi_rate.min(), 3), "hi": r(g.fi_rate.max(), 3), "n": len(g),
                        "med": r(g.snap_share.median(), 4), "q1": r(g.snap_share.quantile(.25), 4),
                        "q3": r(g.snap_share.quantile(.75), 4)})
    d["med"] = d.dec.map({k: x["med"] for k, x in enumerate(deciles)})
    d["gap"] = d.snap_share - d.med
    # A county is flagged only when its gap is larger than its own ACS margin of error.
    d["flag"] = np.where(d.gap < -d.snap_moe, "lower", np.where(d.gap > d.snap_moe, "higher", ""))

    rr = d[["fi_rate", "snap_share", "poverty_rate"]].corr()
    r_xy, r_xz, r_yz = rr.loc["fi_rate", "snap_share"], rr.loc["fi_rate", "poverty_rate"], rr.loc["snap_share", "poverty_rate"]
    partial = (r_xy - r_xz * r_yz) / np.sqrt((1 - r_xz ** 2) * (1 - r_yz ** 2))
    rel = sources.ACS_RELEASES.get(vint, {})
    return {
        "status": "ok", "vintage": vint, "period": rel.get("period", f"{vint - 4}-{vint}"),
        "release_date": rel.get("release_date"), "release_cite": rel.get("release_cite"),
        "mmg_year": m["county_year"], "n": len(d),
        "r": r(r_xy, 2), "partial_r": r(partial, 2),
        "us": None if us is None else {"share": r(us.snap_share, 4), "moe": r(us.snap_moe, 4)},
        "deciles": deciles,
        "rows": {x.fips: [r(x.snap_share, 4), r(x.snap_moe, 4), int(x.dec), r(x.gap, 4), x.flag, r(x.poverty_rate, 4)]
                 for x in d.itertuples()},
        "counts": {"lower": int((d.flag == "lower").sum()), "higher": int((d.flag == "higher").sum())},
        "file": ledger_entry(v),
    }


# ---------------------------------------------------------------- main

def main(strict=False):
    ck = Checks()
    manifest = load(MANIFEST, {"sources": {}})
    checks = load(CHECKS, {})
    out = {}

    u = build_usda(manifest, ck)
    m = build_mmg(ck)
    snap = build_snap(manifest, m, ck) if m else {"status": "blocked", "reason": "Map the Meal Gap files are not available."}

    gc, gs = latest(manifest, "geo-county"), latest(manifest, "geo-state")
    if gc and gs:
        topo = geo.build_topojson(gc["abs"], gs["abs"], ROOT / "site" / "public" / "geo" / "us.json")
        ids = {g["properties"]["id"] for g in json.loads(topo.read_text())["objects"]["counties"]["geometries"]}
        if m:
            missing = sorted(set(m["counties"]) - ids)
            ck.add("Geography", "every MMG county has a boundary", not missing, ", ".join(missing[:10]))
    else:
        ck.add("Geography", "boundary files present", False, "Census boundaries have not been fetched")

    built = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    release_dates = [sources.USDA["release_date"]]
    if m:
        release_dates += [e["release_date"] for e in m["editions"] if e["release_date"]]
    if snap.get("release_date"):
        release_dates.append(snap["release_date"])
    meta = {
        "built_at": built,
        "data_updated": max(release_dates),
        "checked_at": max((v["checked_at"] for v in checks.values()), default=None),
        "checks": checks,
        "validation": ck.items,
        "sources": {"usda": sources.USDA, "acs": sources.ACS, "geo": sources.GEO, "mmg": sources.MMG,
                    "snap_underreporting": sources.SNAP_UNDERREPORTING},
        "files": {
            **({} if not u else {f"usda-{k}": v for k, v in u["files"].items()}),
            "geo-county": ledger_entry(gc), "geo-state": ledger_entry(gs),
            "geo_year": gc.get("boundary_year") if gc else None,
        },
        "mmg_editions": m["editions"] if m else [],
    }
    SITE_DATA.mkdir(parents=True, exist_ok=True)
    out = {
        "meta.json": meta,
        "national.json": u["national"] if u else None,
        "usda_states.json": u["states"] if u else None,
        "mmg_states.json": {"names": mmg.STATES, "series": m["states"]} if m else None,
        "counties.json": {k: m[k] for k in ("county_year", "county_edition", "counties", "missing")} if m else None,
        "snap.json": snap,
    }
    for name, obj in out.items():
        (SITE_DATA / name).write_text(json.dumps(obj, separators=(",", ":"), default=str))
    for c in ck.items:
        mark = "PASS" if c["ok"] else ("WARN" if c["level"] == "warn" else "FAIL")
        print(f"{mark:4} {c['area']:9} {c['check']}" + (f"  [{c['detail']}]" if c["detail"] else ""))
    if ck.failed:
        print(f"{len(ck.failed)} validation check(s) failed", file=sys.stderr)
        return 1 if strict else 0
    return 0
