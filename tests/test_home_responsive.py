"""
T5 — responsive layout tests at the four reference widths.

Pairs with Phase 5 task T5 / Phase 4.3. Two layout systems decide how
KPIs and charts reflow, and both are checked at 375 / 768 / 1024 / 1440:

  1. utils/responsive.py — the in-app pages build a ViewportProfile from
     the `vw` query param (get_viewport_profile) and size KPI columns and
     Plotly charts from it. ViewportProfile.chart_height must agree with
     ChartConfig.for_viewport().height, and neither KPI columns nor chart
     height may shrink as the viewport grows.
  2. views/home.css — the home page's KPI strip is pure CSS. The
     effective `.kpi-row` grid-template-columns is resolved by applying
     the stylesheet's @media blocks in source order.

Touch-target and nav-scroll assertions for the same widths live in
test_mobile_nav.py.
"""
import re
from pathlib import Path
from unittest.mock import patch

import pytest
from hypothesis import given, settings, strategies as st

from utils import responsive
from utils.responsive import ChartConfig, get_viewport_profile

REPO_ROOT = Path(__file__).resolve().parent.parent
HOME_CSS = REPO_ROOT / "views" / "home.css"

WIDTHS = [375, 768, 1024, 1440]


def _profile_at(width: int):
    """Run get_viewport_profile() as if the browser reported `width`."""
    with patch.object(responsive, "_sync_viewport_width"), \
         patch.object(responsive.st, "query_params", {"vw": str(width)}):
        return get_viewport_profile()


# ── 1. In-app ViewportProfile / ChartConfig ──────────────────────────────────


@pytest.mark.parametrize(
    "width, breakpoint, kpi_columns, chart_height",
    [
        (375, "mobile", 1, 240),
        (768, "mobile", 1, 280),   # < 820px default breakpoint, landscape phone
        (1024, "tablet", 2, 350),
        (1440, "desktop", 4, 450),
    ],
)
def test_reference_widths(width, breakpoint, kpi_columns, chart_height):
    profile = _profile_at(width)
    assert profile.width == width
    assert profile.breakpoint_name == breakpoint
    assert profile.kpi_columns == kpi_columns
    assert profile.chart_height == chart_height
    assert ChartConfig.for_viewport(profile).height == chart_height


@given(width=st.integers(min_value=320, max_value=2560))
@settings(max_examples=50, deadline=None)
def test_chart_height_matches_chart_config(width):
    profile = _profile_at(width)
    assert profile.chart_height == ChartConfig.for_viewport(profile).height


@given(
    a=st.integers(min_value=320, max_value=2560),
    b=st.integers(min_value=320, max_value=2560),
)
@settings(max_examples=50, deadline=None)
def test_layout_never_shrinks_as_viewport_grows(a, b):
    narrow, wide = _profile_at(min(a, b)), _profile_at(max(a, b))
    assert narrow.kpi_columns <= wide.kpi_columns
    assert narrow.chart_height <= wide.chart_height
    assert ChartConfig.for_viewport(narrow).font_size <= ChartConfig.for_viewport(wide).font_size


# ── 2. Home page KPI strip (home.css) ────────────────────────────────────────


def _rules(css: str, media: str = ""):
    """Yield (media_condition, selector, declarations) in source order.

    Handles one level of @media nesting, which is all home.css uses.
    """
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    i = 0
    while i < len(css):
        open_ = css.find("{", i)
        if open_ == -1:
            return
        head = css[i:open_].strip()
        depth, j = 1, open_ + 1
        while depth:
            depth += {"{": 1, "}": -1}.get(css[j], 0)
            j += 1
        body = css[open_ + 1:j - 1]
        if head.startswith("@media"):
            yield from _rules(body, head[len("@media"):].strip())
        elif not head.startswith("@"):
            yield media, head, body
        i = j


def _media_matches(cond: str, width: int) -> bool:
    for kind, px in re.findall(r"\((max|min)-width:\s*(\d+)px\)", cond):
        if kind == "max" and width > int(px):
            return False
        if kind == "min" and width < int(px):
            return False
    return True


def _column_count(value: str) -> int:
    rep = re.match(r"repeat\(\s*(\d+)", value)
    return int(rep.group(1)) if rep else len(value.split())


def _kpi_columns_at(width: int) -> int:
    columns = None
    for media, selector, body in _rules(HOME_CSS.read_text()):
        if ".kpi-row" not in [s.strip() for s in selector.split(",")]:
            continue
        if not _media_matches(media, width):
            continue
        decl = re.search(r"grid-template-columns\s*:\s*([^;]+)", body)
        if decl:
            columns = _column_count(decl.group(1).strip())
    return columns


@pytest.mark.parametrize(
    "width, expected",
    [
        (375, 2),   # 2x2 grid on phones (explicit @media (max-width: 480px) rule)
        (768, 2),
        (1024, 2),
        (1440, 4),  # single row of four
    ],
)
def test_home_kpi_row_columns(width, expected):
    assert _kpi_columns_at(width) == expected, (
        f".kpi-row in views/home.css resolves to {_kpi_columns_at(width)} "
        f"columns at {width}px, expected {expected}."
    )


@given(
    a=st.integers(min_value=320, max_value=2560),
    b=st.integers(min_value=320, max_value=2560),
)
@settings(max_examples=50, deadline=None)
def test_home_kpi_row_never_shrinks_as_viewport_grows(a, b):
    assert _kpi_columns_at(min(a, b)) <= _kpi_columns_at(max(a, b))
