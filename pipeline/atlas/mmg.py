"""Read Map the Meal Gap files exactly as Feeding America distributes them.

Every edition has its own sheet names, header rows and column labels, so columns
are matched by pattern and each match must be unique. Nothing is renamed by
position. The files come from the private data repo, never from this repo.
"""
import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import pandas as pd

STATES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "DC": "District of Columbia",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois",
    "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana",
    "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
    "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon",
    "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota",
    "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia",
    "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
}

FILE_RE = re.compile(r"MMG(?P<ed>20\d\d)_(?P<y0>20\d\d)(?:-(?P<y1>20\d\d))?_?Data_?To_?Share(?P<v>_v\d+)?\.xlsx$", re.I)
DATE_RE = re.compile(r"last updated on ([A-Z][a-z]+ \d{1,2}, \d{4})")

EXCL_GROUP = r"child|black|hispanic|white|senior|older|latino"
COLUMNS = {
    "fi_rate": (r"food insecurity rate|^fi rate$", EXCL_GROUP),
    "fi_n": (r"(#|number).*food insecure (persons|individuals)", r"child"),
    "child_rate": (r"child.*(food insecurity|fi) rate", r"black|hispanic|white"),
    "child_n": (r"(#|number).*food insecure children", r"%|185"),
}
COUNTY_COLUMNS = {
    **COLUMNS,
    "cost_per_meal": (r"cost per meal", None),
    "shortfall": (r"annual food budget shortfall", None),
    "rucc2023": (r"continuum code.*2023", None),
}


@dataclass
class Edition:
    edition: int
    data_years: list
    path: Path
    version: str | None
    release_date: str | None = None
    sha256: str = ""
    notes: list = field(default_factory=list)

    @property
    def label(self):
        return f"Map the Meal Gap {self.edition}" + (f" ({self.version})" if self.version else "")


def discover(folder):
    eds = []
    for p in sorted(Path(folder).rglob("*.xlsx")):
        m = FILE_RE.search(p.name)
        if not m:
            continue
        y0 = int(m["y0"])
        y1 = int(m["y1"] or y0)
        ed = Edition(int(m["ed"]), list(range(y0, y1 + 1)), p, (m["v"] or "").lstrip("_") or None)
        ed.sha256 = hashlib.sha256(p.read_bytes()).hexdigest()
        ed.release_date = read_release_date(p)
        eds.append(ed)
    # Keep only the newest version of each edition (e.g. MMG 2025 v2 over v1).
    best = {}
    for e in eds:
        if e.edition not in best or (e.version or "") > (best[e.edition].version or ""):
            best[e.edition] = e
    return sorted(best.values(), key=lambda e: e.edition)


def read_release_date(path):
    """The 'last updated' date from the Read Me sheet. Older editions have none: return None."""
    xl = pd.ExcelFile(path)
    sheet = next((s for s in xl.sheet_names if s.strip().lower() == "read me"), None)
    if sheet is None:
        return None
    text = " ".join(str(v) for v in xl.parse(sheet, header=None).to_numpy().ravel() if isinstance(v, str))
    m = DATE_RE.search(text)
    return datetime.strptime(m[1], "%B %d, %Y").date().isoformat() if m else None


def norm(s):
    return re.sub(r"\s+", " ", str(s)).strip().lower()


def pick(columns, pattern, exclude):
    hits = [c for c in columns if re.search(pattern, norm(c)) and not (exclude and re.search(exclude, norm(c)))]
    if len(hits) != 1:
        raise ValueError(f"expected one column matching {pattern!r}, found {hits}")
    return hits[0]


def find_sheet(xl, kind):
    names = [s for s in xl.sheet_names if kind in s.lower() and "test" not in s.lower() and "aggr" not in s.lower()
             and "cong" not in s.lower() and "district" not in s.lower() and "metro" not in s.lower()]
    if len(names) != 1:
        raise ValueError(f"expected one {kind} sheet, found {names}")
    return names[0]


def read_sheet(xl, sheet):
    raw = xl.parse(sheet, header=None, nrows=6)
    for i, row in raw.iterrows():
        cells = {norm(v) for v in row if isinstance(v, str)}
        if {"fips", "state", "state name"} & cells:
            return xl.parse(sheet, header=i)
    raise ValueError(f"no header row in sheet {sheet}")


def state_column(df):
    best, score = None, 0
    for c in df.columns:
        vals = df[c].dropna().astype(str).str.strip()
        n = vals.isin(STATES).sum()
        if n > score:
            best, score = c, n
    if score < 51:
        raise ValueError("no column of state abbreviations")
    return best


def year_column(df, ed):
    if "Year" in df.columns:
        return pd.to_numeric(df["Year"], errors="coerce")
    if len(ed.data_years) != 1:
        raise ValueError(f"{ed.path.name} spans several years but has no Year column")
    return pd.Series(ed.data_years[0], index=df.index)


def read_states(ed):
    xl = pd.ExcelFile(ed.path)
    df = read_sheet(xl, find_sheet(xl, "state"))
    st = state_column(df)
    cols = {k: pick(df.columns, *v) for k, v in COLUMNS.items()}
    out = pd.DataFrame({"state": df[st].astype(str).str.strip(), "year": year_column(df, ed)})
    for k, c in cols.items():
        out[k] = pd.to_numeric(df[c], errors="coerce")
    out = out[out.state.isin(STATES) & out.year.isin(ed.data_years) & out.fi_rate.notna()].copy()
    out["year"] = out.year.astype(int)
    out["edition"] = ed.edition
    return out.reset_index(drop=True)


def read_counties(ed, year):
    xl = pd.ExcelFile(ed.path)
    df = read_sheet(xl, find_sheet(xl, "county"))
    cols = {k: pick(df.columns, *v) for k, v in COUNTY_COLUMNS.items()}
    name = pick(df.columns, r"^county, state$", None)
    out = pd.DataFrame({
        "fips": pd.to_numeric(df["FIPS"], errors="coerce"),
        "state": df["State"].astype(str).str.strip(),
        "name": df[name].astype(str).str.rsplit(",", n=1).str[0].str.strip(),
        "year": year_column(df, ed),
    })
    for k, c in cols.items():
        out[k] = pd.to_numeric(df[c], errors="coerce")
    out = out[(out.year == year) & out.fips.notna()].copy()
    out["fips"] = out.fips.astype(int).astype(str).str.zfill(5)
    out["year"] = out.year.astype(int)
    return out.reset_index(drop=True)


def edition_for_year(editions, year):
    """The newest edition that contains a year (a revised file supersedes the original)."""
    hits = [e for e in editions if year in e.data_years]
    return max(hits, key=lambda e: e.edition) if hits else None


def state_series(editions):
    frames = []
    for year in sorted({y for e in editions for y in e.data_years}):
        ed = edition_for_year(editions, year)
        df = read_states(ed)
        frames.append(df[df.year == year])
    return pd.concat(frames, ignore_index=True)


RACE_COLUMNS = {
    "black": r"food insecurity rate among black persons",
    "hispanic": r"food insecurity rate among hispanic persons",
    "white_nh": r"food insecurity rate among white, non-hispanic persons",
}


def read_state_race(ed, year):
    """State rates by race and ethnicity, as Feeding America publishes them (rounded,
    blank where it does not release an estimate). Returns None for files without them."""
    xl = pd.ExcelFile(ed.path)
    df = read_sheet(xl, find_sheet(xl, "state"))
    try:
        cols = {k: pick(df.columns, v, None) for k, v in RACE_COLUMNS.items()}
    except ValueError:
        return None
    out = pd.DataFrame({"state": df[state_column(df)].astype(str).str.strip(), "year": year_column(df, ed)})
    for k, c in cols.items():
        out[k] = pd.to_numeric(df[c], errors="coerce")
    return out[out.state.isin(STATES) & (out.year == year)].drop(columns="year").reset_index(drop=True)
