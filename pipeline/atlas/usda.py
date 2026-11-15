"""USDA ERS Household Food Security in the United States (ERR-358) and its data files.

Households and children come from ERS's chart data file. People (all individuals
in food-insecure households) are only published in Table 1A of the report PDF,
so that block is read from the stored PDF and its household rows are checked
against the data file before it is used.
"""
import re
import subprocess

import pandas as pd

from .mmg import STATES


def national_households(path):
    df = pd.read_excel(path, "Food security all households", header=1)
    df = df[df.Category == "All households"]
    return pd.DataFrame({
        "year": df.Year.astype(int),
        "hh_total_k": df.Total.astype(int),
        "hh_fi_k": df["Food insecure-1,000"].astype(int),
        "hh_fi_pct": df["Food insecure-percent"].astype(float),
        "hh_vlfs_pct": df["Very low food security-percent"].astype(float),
    }).reset_index(drop=True)


def national_children(path):
    df = pd.read_excel(path, "Child food security trends", header=1)
    df = df[df.Category.str.startswith("Children - by food security status of household")]
    return pd.DataFrame({
        "year": df.Year.astype(int),
        "ch_total_k": df.Total.astype(int),
        "ch_fi_k": df["Food-insecure households-1,000"].astype(int),
        "ch_fi_pct": df["Food-insecure households-percent"].astype(float),
    }).reset_index(drop=True)


ROW = re.compile(r"^\s*(20\d\d)\s+([\d,]+)\s+([\d,]+)\s+([\d.]+)\s+([\d,]+)\s+([\d.]+)\s+([\d,]+)\s+([\d.]+)\s+([\d,]+)\s+([\d.]+)\s*$")


def table_1a(pdf_path):
    text = subprocess.run(["pdftotext", "-layout", str(pdf_path), "-"], capture_output=True, text=True, check=True).stdout
    start = text.index("Table 1A")
    block, out = None, {"Households": [], "All individuals": []}
    for line in text[start:].splitlines():
        s = line.strip()
        if s.startswith("Households"):
            block = "Households"
        elif s.startswith("All individuals"):
            block = "All individuals"
        elif s.startswith("Adults"):
            break
        m = ROW.match(line)
        if m and block:
            n = lambda i: int(m[i].replace(",", ""))
            out[block].append({"year": int(m[1]), "total_k": n(2), "fi_k": n(5), "fi_pct": float(m[6])})
    return {k: pd.DataFrame(v).sort_values("year").reset_index(drop=True) for k, v in out.items()}


def states(path):
    raw = pd.read_excel(path, header=None)
    title = str(raw.iloc[0, 0]).strip()
    period = re.search(r"(20\d\d)\D+(20\d\d)", title)
    df = pd.read_excel(path, header=1)
    cols = {c: re.sub(r"\s+", " ", str(c)).strip().lower() for c in df.columns}

    def col(pattern):
        hits = [c for c, n in cols.items() if re.search(pattern, n)]
        if len(hits) != 1:
            raise ValueError(f"mapdata: expected one column for {pattern!r}, got {hits}")
        return hits[0]

    out = pd.DataFrame({
        "state": df[col(r"^state$")].astype(str).str.strip(),
        "households": pd.to_numeric(df[col(r"^number of households")], errors="coerce"),
        "interviewed": pd.to_numeric(df[col(r"^number interviewed")], errors="coerce"),
        "fi_pct": pd.to_numeric(df[col(r"^food insecurity prevalence")], errors="coerce"),
        "fi_sig": df[col(r"significance indicator for food insecurity")].astype(str).str.strip(),
        "fi_moe": pd.to_numeric(df[col(r"margin of error.*food insecurity")], errors="coerce"),
    })
    out = out[out.state.isin(set(STATES) | {"U.S."})].reset_index(drop=True)
    return out, (int(period[1]), int(period[2])) if period else None
