import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
RAW = DATA / "raw"
MANIFEST = DATA / "manifest.json"
CHECKS = DATA / "checks.json"
SITE_DATA = ROOT / "site" / "src" / "data"
MMG_DIR = Path(os.environ.get("ATLAS_MMG_DIR", DATA / "private" / "mmg"))
