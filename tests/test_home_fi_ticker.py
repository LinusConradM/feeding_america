"""
T2 — FI ticker tests.

Pairs with Phase 1 task 1.1: the home/nav FI ticker must use a population-weighted
national mean per year (not a simple mean across counties), and must surface a
caveat span for any year gap in the underlying data (e.g., MMG coverage gap 2011-2012).

Direct HTML-output testing is deferred until task 2.2 extracts the ticker into
utils/ticker.py. For now this file asserts:
  1. The two ticker call sites (views/home.py, utils/navigation.py) import the
     population-weighted helper and do not compute FI rate via groupby.mean().
  2. weighted_rate_by_group produces population-weighted means that differ from
     a simple groupby.mean() when populations are unequal — the bug the audit
     measured at +1.74pp in 2019.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from utils.data_loader import weighted_rate_by_group


REPO_ROOT = Path(__file__).resolve().parent.parent


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text()


@pytest.mark.parametrize("source_path", ["views/home.py", "utils/navigation.py"])
def test_ticker_imports_weighted_helper(source_path):
    """Both ticker call sites must import the population-weighted helper."""
    src = _read(source_path)
    assert "weighted_rate_by_group" in src, (
        f"{source_path} should import weighted_rate_by_group from utils.data_loader. "
        "Simple groupby().mean() over-weights small-population counties and produces "
        "a +1.74pp error vs published 2019 national rate."
    )


@pytest.mark.parametrize("source_path", ["views/home.py", "utils/navigation.py"])
def test_ticker_does_not_use_unweighted_mean(source_path):
    """Regression guard: the buggy .mean() pattern should not return."""
    src = _read(source_path)
    forbidden = '["overall_food_insecurity_rate"]\n            .mean()'
    forbidden_compact = '["overall_food_insecurity_rate"].mean()'
    assert forbidden not in src and forbidden_compact not in src, (
        f"{source_path} still computes FI rate via unweighted .mean(). "
        "Use weighted_rate_by_group(_df, 'overall_food_insecurity_rate', 'year') instead."
    )


@pytest.mark.parametrize("source_path", ["views/home.py", "utils/navigation.py"])
def test_ticker_surfaces_coverage_gap(source_path):
    """Both ticker sites must render a 'Coverage gap' caveat when years are missing."""
    src = _read(source_path)
    assert "Coverage gap" in src, (
        f"{source_path} should emit a 'Coverage gap' span when consecutive years "
        "are missing (e.g., MMG 2011-2012)."
    )


def test_weighted_rate_by_group_differs_from_unweighted_when_populations_unequal():
    """
    The weighted helper must produce a different result than simple mean when
    counties have unequal populations — this is exactly the bug shape the audit
    documented at +1.74pp in 2019.
    """
    df = pd.DataFrame({
        "year": [2019, 2019, 2019, 2019],
        "overall_food_insecurity_rate": [0.05, 0.05, 0.20, 0.20],
        "population": [1_000_000, 1_000_000, 5_000, 5_000],
    })

    weighted = weighted_rate_by_group(df, "overall_food_insecurity_rate", "year").iloc[0]
    unweighted = df.groupby("year")["overall_food_insecurity_rate"].mean().iloc[0]

    expected_weighted = np.average(
        df["overall_food_insecurity_rate"], weights=df["population"]
    )
    assert weighted == pytest.approx(expected_weighted)
    # (0.05*1e6 + 0.05*1e6 + 0.20*5e3 + 0.20*5e3) / (1e6 + 1e6 + 5e3 + 5e3)
    # = 102_000 / 2_010_000 = 0.050746...
    assert weighted == pytest.approx(0.05075, abs=1e-4)
    assert unweighted == pytest.approx(0.125)
    assert abs(weighted - unweighted) > 0.05, (
        "Population-weighted mean should diverge sharply from simple mean when "
        "populations are unequal — the very bug the ticker had."
    )


def test_weighted_rate_by_group_handles_nan_rates():
    """NaN rates in the source data should be dropped, not propagate."""
    df = pd.DataFrame({
        "year": [2019, 2019, 2019],
        "overall_food_insecurity_rate": [0.10, np.nan, 0.20],
        "population": [100, 100, 100],
    })
    result = weighted_rate_by_group(df, "overall_food_insecurity_rate", "year").iloc[0]
    assert result == pytest.approx(0.15)


def test_weighted_rate_by_group_falls_back_when_weights_missing():
    """When weight col is missing, fall back to unweighted mean (per helper contract)."""
    df = pd.DataFrame({
        "year": [2019, 2019],
        "overall_food_insecurity_rate": [0.10, 0.20],
    })
    result = weighted_rate_by_group(df, "overall_food_insecurity_rate", "year").iloc[0]
    assert result == pytest.approx(0.15)
