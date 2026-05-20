"""
T-Phase4.1 — hero audience CTA tests.

Pairs with Phase 4 task 4.1: the hero subhead is rewritten to drop
builder-voice phrasing ("Investigating patterns…") and the two
buttons (Explore Dashboard + GitHub) are replaced with three
audience-routed CTAs (policymaker / nonprofit / researcher).

Q7 in HOME_REDESIGN_DECISIONS.md resolved to "no ranking, equal
weight" for the three audiences, so all three CTAs must be styled
the same — no primary/secondary distinction.
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = REPO_ROOT / "views" / "templates"


def _hero() -> str:
    return (TEMPLATE_DIR / "hero.html").read_text()


# ── Subhead rewrite ──────────────────────────────────────────────────────────


def test_subhead_drops_builder_voice():
    """The 'Investigating patterns...' phrasing must not return."""
    src = _hero()
    assert "Investigating patterns" not in src, (
        "hero.html subhead still uses the builder-voice 'Investigating "
        "patterns' phrase. Phase 4.1 rewrote to audience-facing copy."
    )


def test_subhead_keeps_scale_facts():
    """The new subhead should still anchor on the dataset's scale (counties + years)."""
    src = _hero()
    # 3,100+ U.S. counties is the canonical scale number on the home page
    assert "3,100+" in src, (
        "Subhead should keep the '3,100+' counties anchor — that's the "
        "single most-cited fact about the dataset."
    )
    assert "15 years" in src, (
        "Subhead should mention the 15-year longitudinal span; it's the "
        "second-most-cited fact and signals the temporal depth."
    )


# ── Three audience CTAs ──────────────────────────────────────────────────────


EXPECTED_CTAS = {
    "audience-policymaker": ("/8_Policy_Scenarios", "policymaker"),
    "audience-nonprofit":   ("/2_Geographic_Intelligence", "nonprofit"),
    "audience-researcher":  ("/1_Executive_Overview", "researcher"),
}


def test_three_audience_cards_exist():
    """All 3 audience-card classes must be present, exactly once each."""
    src = _hero()
    for cls in EXPECTED_CTAS:
        # Count occurrences — should be exactly one
        count = len(re.findall(rf'\bclass="audience-card\s+{cls}\b', src))
        assert count == 1, (
            f"Expected exactly 1 '{cls}' card in hero.html, found {count}. "
            "Three audience cards (policymaker, nonprofit, researcher) must "
            "each appear once."
        )


def test_each_audience_card_links_to_right_route():
    """Each audience CTA must link to its mapped page (per Q7 resolution)."""
    src = _hero()
    for cls, (expected_href, audience_label) in EXPECTED_CTAS.items():
        pattern = re.compile(
            rf'<a[^>]*\bclass="audience-card\s+{cls}\b[^"]*"[^>]*href="([^"]+)"',
            re.DOTALL,
        )
        m = pattern.search(src)
        if not m:
            # Try href before class
            pattern = re.compile(
                rf'<a[^>]*href="([^"]+)"[^>]*class="audience-card\s+{cls}\b',
                re.DOTALL,
            )
            m = pattern.search(src)
        assert m, f"Could not find {cls} anchor in hero.html"
        assert m.group(1) == expected_href, (
            f"{audience_label} CTA links to {m.group(1)!r}, expected "
            f"{expected_href!r}. The Q7 decision in "
            f"HOME_REDESIGN_DECISIONS.md routes {audience_label}s to "
            f"{expected_href}."
        )


def test_each_audience_card_has_aria_label():
    """Screen-reader users need a meaningful destination announcement."""
    src = _hero()
    for cls in EXPECTED_CTAS:
        pattern = re.compile(
            rf'<a[^>]*\bclass="audience-card\s+{cls}\b[^"]*"[^>]*\baria-label="[^"]+"',
            re.DOTALL,
        )
        if not pattern.search(src):
            # Try aria-label before class
            pattern = re.compile(
                rf'<a[^>]*\baria-label="[^"]+"[^>]*\bclass="audience-card\s+{cls}\b',
                re.DOTALL,
            )
        assert pattern.search(src), (
            f"{cls} CTA must carry an aria-label so screen readers "
            f"announce a meaningful destination."
        )


def test_legacy_hero_buttons_removed():
    """The old hero-btn-primary / hero-btn-ghost buttons must be gone from hero.html."""
    src = _hero()
    for legacy in ("hero-btn-primary", "hero-btn-ghost"):
        assert legacy not in src, (
            f"hero.html still references '{legacy}'. Phase 4.1 replaced "
            "the two-button hero CTA with three audience-card CTAs."
        )


def test_cta_grid_marked_as_navigation():
    """The CTA grid should have role='navigation' + aria-label for landmark a11y."""
    src = _hero()
    # role="navigation" on the container so screen readers can jump straight
    # to the audience-routing region
    assert 'role="navigation"' in src and 'aria-label="Audience paths"' in src, (
        "hero.html .hero-cta-grid container should declare "
        "role='navigation' aria-label='Audience paths' so screen-reader "
        "users can navigate to the CTA region as a landmark."
    )


# ── Equal weight (Q7) ────────────────────────────────────────────────────────


def test_no_primary_secondary_distinction_in_audience_cards():
    """Q7 says no ranking, equal weight — no card should be labeled 'primary'."""
    src = _hero()
    audience_block = src
    # If any audience card has a 'primary' or 'secondary' modifier class, that
    # violates equal weight.
    for label in ("audience-primary", "audience-secondary", "audience-featured"):
        assert label not in audience_block, (
            f"hero.html contains '{label}' — Q7 in "
            f"HOME_REDESIGN_DECISIONS.md says all three audiences have "
            f"equal weight, no ranking. Style cards identically."
        )
