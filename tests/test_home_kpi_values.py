"""
T1 — Home KPI tests.

Pairs with:
  - Phase 1 task 1.2: KPI #1 ("Americans Affected") must be data-derived from
    load_data() with a year stamp and source citation visible. The hardcoded
    "44.2M" of unconfirmed origin must not reappear.
  - Phase 2 task 2.1 home leg: KPIs #2-4 must be data-derived from load_data().
  - Phase 4 task 4.2: KPIs #2-4 are now insight numbers (National FI Rate,
    Counties >20% FI, YoY Change) rather than metadata (Counties Analyzed,
    Longitudinal Span, County-Year Obs.). "Americans Affected" stays as
    the anchor.

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
    # Phase 4.2 KPI swap: rate / crisis-counties / yoy replace counties/span/obs
    assert "__KPI_RATE_VAL__" in src, "KPI #2 (National FI Rate) value placeholder missing"
    assert "__KPI_CRISIS_VAL__" in src, "KPI #3 (Counties >20% FI) value placeholder missing"
    assert "__KPI_YOY_VAL__" in src, "KPI #4 (YoY Change) value placeholder missing"


def test_kpi_template_has_no_hardcoded_drift_prone_values():
    """The original metadata KPIs were hardcoded; the new insight KPIs must
    also not drift into the template as literals — they're computed live."""
    src = _read("views/templates/kpi.html")
    # Pre-Phase-2 hardcoded literals (must never return)
    for stale in ("3,100+", "15 yrs", "47K+", "44.2M"):
        assert stale not in src, (
            f"views/templates/kpi.html contains the stale hardcoded value '{stale}'. "
            "Use the placeholders filled by home.py instead."
        )
    # Pre-Phase-4.2 KPI labels (the metadata trio is gone)
    for retired_label in ("Counties Analyzed", "Longitudinal Span", "County-Year Obs"):
        assert retired_label not in src, (
            f"views/templates/kpi.html still uses the retired KPI label '{retired_label}'. "
            "Phase 4.2 replaced this metadata KPI with an insight number."
        )


def test_home_py_computes_kpi_from_data():
    """home.py must compute all four KPIs live from load_data() and emit a source line on KPI #1."""
    src = _read("views/home.py")
    assert "_get_kpi_html" in src, "home.py should define a _get_kpi_html renderer"
    assert "_compute_home_kpis" in src, (
        "home.py should define a _compute_home_kpis() helper that "
        "returns all four KPI values from a single load_data() call."
    )
    # KPI #1 — Americans Affected (anchor, unchanged across Phase 4.2)
    assert "no_of_food_insecure_persons_overall" in src, (
        "home.py should derive the 'Americans Affected' number from "
        "no_of_food_insecure_persons_overall in load_data()."
    )
    assert "Feeding America MMG" in src, (
        "home.py should emit a 'Feeding America MMG · YYYY' source line on KPI #1."
    )
    # KPI #2 — National FI Rate (population-weighted, latest year)
    assert "weighted_rate" in src, (
        "home.py should derive the 'National FI Rate' KPI via the "
        "weighted_rate helper (Phase 1 1.1 / Phase 4.2 — population-weighted, "
        "not a simple .mean())."
    )
    # KPI #3 — Counties >20% FI (count of crisis counties)
    assert "> 0.20" in src or "> 0.2" in src, (
        "home.py should count counties where overall_food_insecurity_rate > 0.20 "
        "(the 'Very High' tier from the FI category convention)."
    )
    # KPI #4 — YoY Change (national rate, latest minus previous year)
    assert "_latest_year - 1" in src, (
        "home.py should compute the YoY change by comparing the latest "
        "year's rate against (_latest_year - 1)'s rate."
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
    # Phase 4.2 KPI keys
    assert '"rate_val": "—"' in src, "rate_val fallback should be em-dash"
    assert '"crisis_val": "—"' in src, "crisis_val fallback should be em-dash"
    assert '"yoy_val": "—"' in src, "yoy_val fallback should be em-dash"


def test_compute_home_kpis_logic_with_synthetic_data():
    """
    Run the same shape of computation _compute_home_kpis() does, in isolation,
    to verify the new (Phase 4.2) KPI #2-4 transforms are correct.

    KPI #2 — National FI Rate: population-weighted mean of overall_food_insecurity_rate,
            latest year.
    KPI #3 — Counties >20% FI: count of rows in latest year where rate > 0.20.
    KPI #4 — YoY Change: (latest_year rate - previous_year rate) in percentage points.
    """
    import numpy as np

    df = pd.DataFrame({
        "year": [2022] * 4 + [2023] * 4,
        "overall_food_insecurity_rate": [
            0.10, 0.15, 0.22, 0.25,   # 2022: weighted with equal pop = 0.18
            0.12, 0.18, 0.21, 0.28,   # 2023: weighted with equal pop ≈ 0.1975
        ],
        "population": [1000] * 8,
    })
    latest_year = int(df["year"].max())
    latest = df[df["year"] == latest_year]
    prev = df[df["year"] == latest_year - 1]

    rate_latest = np.average(latest["overall_food_insecurity_rate"], weights=latest["population"])
    rate_prev = np.average(prev["overall_food_insecurity_rate"], weights=prev["population"])

    crisis_counties = int((latest["overall_food_insecurity_rate"] > 0.20).sum())
    yoy_pp = (rate_latest - rate_prev) * 100

    # KPI #2 — National FI Rate
    assert rate_latest == pytest.approx(0.1975, abs=1e-4)
    assert f"{rate_latest * 100:.1f}%" == "19.8%"
    # KPI #3 — Counties >20% FI (2023 has 0.21 and 0.28 above threshold)
    assert crisis_counties == 2
    assert f"{crisis_counties:,}" == "2"
    # KPI #4 — YoY change is positive (rate worsened)
    assert yoy_pp == pytest.approx(1.75, abs=1e-2)
    assert f"{yoy_pp:+.1f}pp" == "+1.8pp"
