"""Turn the Census cartographic boundary zips into one small TopoJSON for the map.

mapshaper (an npm dev dependency of the site) projects to Albers USA with Alaska
and Hawaii inset, keeps only the GEOID, drops territories outside the 50 states
and DC, and simplifies. The original zips stay untouched in data/raw.
"""
import subprocess
import tempfile
import zipfile
from pathlib import Path

from .paths import ROOT

TERRITORIES = "'60','66','69','72','78'"


def build_topojson(county_zip, state_zip, out_path):
    mapshaper = ROOT / "site" / "node_modules" / ".bin" / "mapshaper"
    with tempfile.TemporaryDirectory() as tmp:
        shp = {}
        for name, z in (("counties", county_zip), ("states", state_zip)):
            d = Path(tmp) / name
            zipfile.ZipFile(z).extractall(d)
            src = next(d.glob("*.shp"))
            dst = d / f"{name}.shp"
            for f in d.glob(src.stem + ".*"):
                f.rename(d / f"{name}{''.join(f.suffixes[-1:])}")
            shp[name] = dst
        out_path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([
            str(mapshaper), "-i", str(shp["counties"]), str(shp["states"]), "combine-files",
            "-filter", f"[{TERRITORIES}].indexOf(STATEFP) < 0", "target=*",
            "-each", "id=GEOID", "target=*",
            "-filter-fields", "id", "target=*",
            "-proj", "albersusa", "target=*",
            "-simplify", "8%", "keep-shapes", "target=*",
            "-o", str(out_path), "format=topojson", "quantization=1e5", "target=*",
        ], check=True, capture_output=True, text=True)
    return out_path
