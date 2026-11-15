import math
from pathlib import Path

import numpy as np
import pytest

from atlas import acs, usda
from atlas.build import latest
from atlas.fetch import load
from atlas.paths import MANIFEST

M = load(MANIFEST, {"sources": {}})


def test_proportion_moe_matches_census_formula():
    # Census ACS Handbook ch. 8: MOE(p) = sqrt(MOE_x^2 - p^2 MOE_y^2) / y
    p, moe = acs.share(np.array([400.0]), np.array([60.0]), np.array([2000.0]), np.array([90.0]))
    assert p[0] == pytest.approx(0.2)
    assert moe[0] == pytest.approx(math.sqrt(60**2 - 0.04 * 90**2) / 2000)


def test_proportion_moe_falls_back_to_ratio_formula():
    p, moe = acs.share(np.array([50.0]), np.array([5.0]), np.array([60.0]), np.array([40.0]))
    assert moe[0] == pytest.approx(math.sqrt(5**2 + (50 / 60) ** 2 * 40**2) / 60)


@pytest.mark.skipif(latest(M, "usda-err358-pdf") is None, reason="USDA files not fetched")
def test_table_1a_matches_published_2024_headline():
    t = usda.table_1a(latest(M, "usda-err358-pdf")["abs"])
    hh = t["Households"].set_index("year").loc[2024]
    ppl = t["All individuals"].set_index("year").loc[2024]
    assert (hh.fi_pct, ppl.fi_k, ppl.fi_pct) == (13.7, 47900, 14.4)


@pytest.mark.skipif(latest(M, "usda-mapdata") is None, reason="USDA files not fetched")
def test_state_file_has_every_state_with_moe():
    st, period = usda.states(latest(M, "usda-mapdata")["abs"])
    assert period == (2022, 2024)
    assert len(st) == 52 and st.fi_moe.notna().all()
