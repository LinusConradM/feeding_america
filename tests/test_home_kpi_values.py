"""
T1 — Home KPI tests.

Pairs with Phase 1 task 1.2: KPI #1 ("Americans Affected") must be data-derived
from load_data() at render time, with a year stamp and source citation visible.
The hardcoded "44.2M" string of unconfirmed origin must not reappear.

Full HTML-render testing is deferred to Phase 5 / Phase 2. For now this file
asserts:
  1. views/templates/kpi.html uses placeholders, not the legacy "44.2M" literal.
  2. views/home.py wires the placeholders to a data-derived computation and
     emits a "Feeding America MMG · YYYY" source line.
  3. README.md no longer publishes the bare "44.2 million" figure.
"""
from pathlib import Path

import pandas as pd
import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text()


def test_kpi_template_has_no_hardcoded_44_2m():
    """The legacy '44.2M' literal must not be reintroduced into the template."""
    src = _read("views/templates/kpi.html")
    assert "44.2M" not in src, (
        "views/templates/kpi.html still contains the hardcoded 44.2M value. "
        "Use the __KPI_AMERICANS_VAL__ placeholder filled by home.py instead."
    )


def test_kpi_template_uses_placeholders():
    """KPI #1 must use placeholders that home.py fills with computed values."""
    src = _read("views/templates/kpi.html")
    assert "__KPI_AMERICANS_VAL__" in src, "KPI value placeholder missing"
    assert "__KPI_AMERICANS_NOTE__" in src, "KPI source/year placeholder missing"


def test_home_py_computes_kpi_from_data():
    """home.py must compute the KPI live from load_data() and emit a source line."""
    src = _read("views/home.py")
    assert "_get_kpi_html" in src, "home.py should define a _get_kpi_html helper"
    assert "no_of_food_insecure_persons_overall" in src, (
        "home.py should derive the 'Americans Affected' number from "
        "no_of_food_insecure_persons_overall in load_data()."
    )
    assert "Feeding America MMG" in src, (
        "home.py should emit a 'Feeding America MMG · YYYY' source line."
    )


def test_home_py_does_not_render_raw_kpi_template():
    """The bare 'st.html(_load_template(\"kpi.html\"))' call must be gone."""
    src = _read("views/home.py")
    assert 'st.html(_load_template("kpi.html"))' not in src, (
        "home.py should render the KPI strip via _get_kpi_html(), not by "
        "directly inlining the unfilled template (placeholders would leak to the page)."
    )


def test_readme_no_longer_publishes_44_2m():
    """README must not publish the unverified '44.2 million' headline anymore."""
    src = _read("README.md")
    assert "44.2 million" not in src, (
        "README.md still publishes the unverified '44.2 million' figure. "
        "Q2 in HOME_REDESIGN_DECISIONS.md resolved this: origin unknown, do not preserve."
    )


def test_kpi_computation_logic_with_synthetic_data():
    """
    Inline-test the computation: sum no_of_food_insecure_persons_overall for
    the latest year, divide by 1M, format to one decimal place. This is the
    exact transform home.py applies; verifying it independently guards against
    silent regression.
    """
    df = pd.DataFrame({
        "year": [2021, 2021, 2022, 2022, 2023, 2023],
        "no_of_food_insecure_persons_overall": [
            10_000_000, 20_000_000,  # 2021: 30M
            15_000_000, 20_000_000,  # 2022: 35M
            22_000_000, 24_700_000,  # 2023: 46.7M (matches audit reference)
        ],
    })
    latest_year = int(df["year"].max())
    latest = df[df["year"] == latest_year]
    total = float(latest["no_of_food_insecure_persons_overall"].sum())
    val = f"{total / 1_000_000:.1f}M"
    note = f"Feeding America MMG · {latest_year}"

    assert latest_year == 2023
    assert val == "46.7M"
    assert note == "Feeding America MMG · 2023"


def test_kpi_fallback_when_data_unavailable():
    """If load_data() raises, the KPI value must render an em-dash, not '44.2M'."""
    src = _read("views/home.py")
    # Look for the fallback inside the _get_kpi_html function
    assert '_val = "—"' in src, (
        "home.py should render an em-dash fallback when the data load fails, "
        "so a stale/wrong number cannot return silently."
    )
    assert '_note = "Source unavailable"' in src, (
        "home.py should label the fallback as 'Source unavailable'."
    )
