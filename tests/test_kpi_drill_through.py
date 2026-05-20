"""
T-Phase4.5 — KPI drill-through link tests.

Pairs with Phase 4 task 4.5: each home-page KPI card must link to a
relevant analytics page so the headline numbers aren't dead-ended. The
audit found all 4 cards were static divs, leaving the user with no
"what should I do with this?" affordance after reading the strip.

Mapping (in kpi.html row order):
  k1 Americans Affected   → /1_Executive_Overview
  k2 Counties Analyzed    → /2_Geographic_Intelligence
  k3 Longitudinal Span    → /7_Time_Series_Explorer
  k4 County-Year Obs.     → /0_Data_Explorer
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _kpi_html() -> str:
    return (REPO_ROOT / "views" / "templates" / "kpi.html").read_text()


EXPECTED_LINKS = {
    "k1": "/1_Executive_Overview",
    "k2": "/2_Geographic_Intelligence",
    "k3": "/7_Time_Series_Explorer",
    "k4": "/0_Data_Explorer",
}


def test_each_kpi_card_is_an_anchor():
    """Every KPI card (k1-k4) must be rendered as an <a class="kpi-glass kN ..."> anchor."""
    src = _kpi_html()
    for slot in EXPECTED_LINKS:
        # We expect: <a class="kpi-glass k1 kpi-card-link" ...>  (or similar order)
        pattern = re.compile(rf'<a[^>]*\bclass="[^"]*\bkpi-glass\b[^"]*\b{slot}\b[^"]*"')
        assert pattern.search(src), (
            f"KPI card slot '{slot}' is not an <a> anchor. Phase 4.5 requires "
            f"each KPI card to be a link to a relevant analytics page so the "
            f"headline number has a drill-through path."
        )


def test_each_kpi_has_the_right_href():
    """Each KPI card must link to its mapped analytics page."""
    src = _kpi_html()
    for slot, expected_href in EXPECTED_LINKS.items():
        # Find the anchor for this slot and verify its href
        pattern = re.compile(
            rf'<a[^>]*\bclass="[^"]*\b{slot}\b[^"]*"[^>]*\bhref="([^"]+)"',
            re.DOTALL,
        )
        m = pattern.search(src)
        if not m:
            # Try href first, then class
            pattern = re.compile(
                rf'<a[^>]*\bhref="([^"]+)"[^>]*\bclass="[^"]*\b{slot}\b[^"]*"',
                re.DOTALL,
            )
            m = pattern.search(src)
        assert m is not None, f"Could not parse href for slot '{slot}'"
        assert m.group(1) == expected_href, (
            f"KPI slot '{slot}' links to {m.group(1)!r}, expected {expected_href!r}. "
            "If this mapping has changed, update both the template and this test."
        )


def test_each_kpi_anchor_has_aria_label():
    """Each KPI anchor must carry an aria-label.

    Screen readers announce links by their accessible name. KPI cards
    contain a formatted number ("46.8M") as the visible value, but
    "46.8M" alone doesn't tell a screen-reader user where the link goes.
    aria-label provides a meaningful destination announcement.
    """
    src = _kpi_html()
    for slot in EXPECTED_LINKS:
        pattern = re.compile(
            rf'<a[^>]*\b{slot}\b[^>]*\baria-label="[^"]+"',
            re.DOTALL,
        )
        assert pattern.search(src), (
            f"KPI slot '{slot}' is missing aria-label. Each drill-through "
            f"link needs an accessible name so screen-reader users know "
            f"where it leads."
        )


def test_kpi_card_link_class_styled():
    """home.css must define `.kpi-card-link` so anchor defaults don't override the design."""
    home_css = (REPO_ROOT / "views" / "home.css").read_text()
    kpi_card_link_block = re.search(
        r"\.kpi-card-link\s*\{[^}]*\}",
        home_css,
        re.DOTALL,
    )
    assert kpi_card_link_block, (
        "views/home.css should define `.kpi-card-link` styles to neutralize "
        "the browser's default anchor underline + blue color so the KPI "
        "visual treatment matches the pre-link design."
    )
    # The card must explicitly drop the underline (otherwise text-decoration cascades)
    assert "text-decoration: none" in kpi_card_link_block.group(0), (
        "The .kpi-card-link rule should set text-decoration: none."
    )


def test_no_legacy_kpi_div_remains():
    """All four KPI slots must be anchors — no leftover `<div class="kpi-glass kN">`."""
    src = _kpi_html()
    for slot in EXPECTED_LINKS:
        legacy = re.compile(rf'<div\s+class="kpi-glass\s+{slot}"')
        assert not legacy.search(src), (
            f"kpi.html still has a `<div class=\"kpi-glass {slot}\">` — "
            f"that slot should be an <a> after Phase 4.5."
        )
