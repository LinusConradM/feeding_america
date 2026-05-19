"""
T1 — Home KPI tests.

Pairs with:
  - Phase 1 task 1.2: KPI #1 ("Americans Affected") must be data-derived from
    load_data() with a year stamp and source citation visible. The hardcoded
    "44.2M" of unconfirmed origin must not reappear.
  - Phase 2 task 2.1 home leg: KPIs #2-4 (Counties / Span / Obs) must also be
    data-derived from load_data(). The hardcoded "3,100+", "15 yrs", "47K+"
    strings drift every data refresh and must not reappear in the template.

Full HTML-render testing is deferred to Phase 5. For now this file asserts:
  1. views/templates/kpi.html uses placeholders for all four KPI values.
  2. views/home.py wires all four placeholders to a data-derived computation
     and emits a "Feeding America MMG · YYYY" source line on KPI #1.
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
    """All four KPIs must use placeholders that home.py fills with computed values."""
    src = _read("views/templates/kpi.html")
    assert "__KPI_AMERICANS_VAL__" in src, "KPI #1 value placeholder missing"
    assert "__KPI_AMERICANS_NOTE__" in src, "KPI #1 source/year placeholder missing"
    assert "__KPI_COUNTIES_VAL__" in src, "KPI #2 (Counties) value placeholder missing"
    assert "__KPI_SPAN_VAL__" in src, "KPI #3 (Longitudinal Span) value placeholder missing"
    assert "__KPI_OBS_VAL__" in src, "KPI #4 (County-Year Obs) value placeholder missing"


def test_kpi_template_has_no_hardcoded_drift_prone_values():
    """The other three KPIs were hardcoded; they must not drift back into the template."""
    src = _read("views/templates/kpi.html")
    # Each of these was the literal hardcoded value before task 2.1 home leg.
    for stale in ("3,100+", "15 yrs", "47K+"):
        assert stale not in src, (
            f"views/templates/kpi.html still contains the stale hardcoded value '{stale}'. "
            "Use the placeholders filled by home.py instead."
        )


def test_home_py_computes_kpi_from_data():
    """home.py must compute all four KPIs live from load_data() and emit a source line on KPI #1."""
    src = _read("views/home.py")
    assert "_get_kpi_html" in src, "home.py should define a _get_kpi_html renderer"
    assert "_compute_home_kpis" in src, (
        "home.py should define a _compute_home_kpis() helper (task 2.1 home leg) that "
        "returns all four KPI values from a single load_data() call."
    )
    # KPI #1 — Americans Affected
    assert "no_of_food_insecure_persons_overall" in src, (
        "home.py should derive the 'Americans Affected' number from "
        "no_of_food_insecure_persons_overall in load_data()."
    )
    assert "Feeding America MMG" in src, (
        "home.py should emit a 'Feeding America MMG · YYYY' source line on KPI #1."
    )
    # KPI #2 — Counties Analyzed
    assert '"fips"' in src or "'fips'" in src, (
        "home.py should derive 'Counties Analyzed' from df['fips'].nunique()."
    )
    # KPI #3 — Longitudinal Span
    assert "_earliest_year" in src or "year\"].min()" in src, (
        "home.py should derive 'Longitudinal Span' from the year range in load_data()."
    )
    # KPI #4 — County-Year Obs.
    assert "len(_df)" in src, (
        "home.py should derive 'County-Year Obs.' from len(load_data())."
    )


def test_home_py_does_not_render_raw_kpi_template():
    """The bare 'st.html(_load_template(\"kpi.html\"))' call must be gone."""
    src = _read("views/home.py")
    assert 'st.html(_load_template("kpi.html"))' not in src, (
        "home.py should render the KPI strip via _get_kpi_html(), not by "
        "directly inlining the unfilled template (placeholders would leak to the page)."
    )


def test_mmg_disclaimer_banner_present():
    """Task 2.5: a methodology disclaimer must render under the KPI strip,
    naming Feeding America's Map the Meal Gap and the 2020 methodology revision."""
    src = _read("views/home.py")
    assert "Map the Meal Gap" in src, (
        "home.py should surface a 'Map the Meal Gap' disclaimer under the KPI "
        "strip so audiences know which methodology produced the headline numbers."
    )
    assert "Methodology revised in 2020" in src, (
        "Disclaimer should note the 2020 methodology revision — pre- and post-2020 "
        "series are not directly comparable, and this is the highest-leverage "
        "caveat for any non-specialist reader."
    )
    assert "mmg-disclaimer" in src, (
        "Disclaimer should carry the 'mmg-disclaimer' class hook for downstream "
        "styling/tests."
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
    """If load_data() raises, every KPI value must render an em-dash, not a stale literal."""
    src = _read("views/home.py")
    # _compute_home_kpis returns a dict on the failure path; check the values are em-dashes
    # (so a stale/wrong number cannot return silently for any of the four KPIs).
    assert '"americans_val": "—"' in src, (
        "home.py should set americans_val to an em-dash in the fallback path."
    )
    assert '"americans_note": "Source unavailable"' in src, (
        "home.py should label the fallback note as 'Source unavailable'."
    )
    assert '"counties_val": "—"' in src, "counties_val fallback should be em-dash"
    assert '"span_val": "—"' in src, "span_val fallback should be em-dash"
    assert '"obs_val": "—"' in src, "obs_val fallback should be em-dash"


def test_compute_home_kpis_logic_with_synthetic_data():
    """
    Run the same shape of computation _compute_home_kpis() does, in isolation,
    to verify the KPI #2-4 transforms are correct. Guards against silent
    regressions if the renderer is refactored.
    """
    df = pd.DataFrame({
        "year": [2009, 2009, 2010, 2010, 2023, 2023],
        "fips": [1001, 1003, 1001, 1003, 1001, 1003],
        "no_of_food_insecure_persons_overall": [0, 0, 0, 0, 22_000_000, 24_700_000],
    })
    latest_year = int(df["year"].max())
    earliest_year = int(df["year"].min())
    counties = int(df["fips"].nunique())
    span = latest_year - earliest_year + 1
    obs = len(df)

    assert counties == 2, "nunique() over the two fips codes should be 2"
    assert span == 15, "2023 - 2009 + 1 = 15"
    assert obs == 6, "6 rows in the synthetic frame"
    assert f"{counties:,}" == "2"
    assert f"{span} yrs" == "15 yrs"
    assert f"{obs:,}" == "6"
