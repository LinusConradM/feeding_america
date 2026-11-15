import argparse
import sys

from . import fetch
from .paths import MMG_DIR


def cmd_fetch(args):
    from . import mmg
    store = fetch.Store()
    editions = mmg.discover(MMG_DIR) if MMG_DIR.exists() else []
    latest_year = max((e.data_years[-1] for e in editions), default=args.geo_year)
    fetch.fetch_usda(store)
    fetch.fetch_acs(store)
    fetch.fetch_geo(store, [latest_year, latest_year - 1])
    newer = fetch.watch_mmg(store, [e.edition for e in editions])
    store.save()
    print("changed:", ", ".join(store.changed) or "nothing")
    errors = {k: v["error"] for k, v in store.checks.items() if v.get("status") == "error"}
    for k, v in errors.items():
        print(f"ERROR {k}: {v}", file=sys.stderr)
    if newer:
        print(f"NEW_MMG_EDITION={newer}")
    return 1 if errors and args.strict else 0


def cmd_build(args):
    from . import build
    return build.main(strict=args.strict)


def main():
    p = argparse.ArgumentParser(prog="atlas")
    sub = p.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch", help="check every public source and store new versions")
    f.add_argument("--strict", action="store_true", help="exit non-zero if any source fails")
    f.add_argument("--geo-year", type=int, default=2024)
    f.set_defaults(fn=cmd_fetch)
    b = sub.add_parser("build", help="parse raw files, validate, write site data")
    b.add_argument("--strict", action="store_true")
    b.set_defaults(fn=cmd_build)
    args = p.parse_args()
    sys.exit(args.fn(args))


main()
