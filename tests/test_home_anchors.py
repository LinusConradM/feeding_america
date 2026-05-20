"""
T3 — Home internal-anchor integrity tests.

Pairs with Phase 1 task 1.3: every internal `href="#..."` on the home page must
point to an `id="..."` that exists somewhere in the rendered home content. The
audit's flagship example was `href="#gallery"` pointing at the deleted
gallery.html template — a dead primary CTA on a published page.

This test reads every HTML template in views/templates/, collects every internal
anchor and every id, and asserts the anchor set is a subset of the id set.
"""
import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = REPO_ROOT / "views" / "templates"


def _all_templates():
    return sorted(TEMPLATE_DIR.glob("*.html"))


def test_hero_reactive_js_targets_real_nav_selector():
    """Task 2.3: the hero reactive-screenshot JS must select `.app-menu-item`
    (matches nav.html), not the legacy `.menu-item` that never matched anything
    on the live site."""
    src = (REPO_ROOT / "views" / "home.py").read_text()
    nav = (TEMPLATE_DIR / "nav.html").read_text()
    assert "app-menu-item" in nav, (
        "views/templates/nav.html no longer uses .app-menu-item — this test's "
        "premise is stale; update both the selector and this guard."
    )
    assert ".menu-item[data-img]" not in src, (
        "views/home.py reactive-screenshot JS still uses '.menu-item[data-img]', "
        "which doesn't match anything on the live page. Use '.app-menu-item[data-img]'."
    )
    assert ".app-menu-item[data-img]" in src, (
        "views/home.py should select '.app-menu-item[data-img]' for the hero "
        "reactive-screenshot feature (matches the class in nav.html)."
    )


def test_gallery_template_deleted():
    """views/templates/gallery.html was deprecated per Q4 in HOME_REDESIGN_DECISIONS.md."""
    gallery = TEMPLATE_DIR / "gallery.html"
    assert not gallery.exists(), (
        "views/templates/gallery.html should be deleted. Q4 in "
        "HOME_REDESIGN_DECISIONS.md resolved this: gallery is deprecated."
    )


def test_no_template_links_to_gallery_anchor():
    """No surviving template may use href=\"#gallery\" — the target is gone."""
    offenders = []
    for tmpl in _all_templates():
        text = tmpl.read_text()
        if 'href="#gallery"' in text or "href='#gallery'" in text:
            offenders.append(tmpl.name)
    assert not offenders, (
        f"These templates still link to #gallery (which no longer exists): {offenders}. "
        "Repoint them to a valid surface (e.g., /1_Executive_Overview)."
    )


def test_hero_audience_ctas_point_to_valid_routes():
    """Phase 4.1: hero must have 3 audience-routed CTAs (policymaker /
    nonprofit / researcher) each pointing to a Streamlit page route.

    Replaces the legacy single `hero-btn-primary` button + GitHub link —
    Q7 says no ranking, equal weight across the three audiences.
    """
    hero = (TEMPLATE_DIR / "hero.html").read_text()
    # All three audience-card classes must be present
    cards = re.findall(
        r'<a[^>]*class="audience-card\s+([^"\s]+)"[^>]*href="([^"]+)"',
        hero,
    )
    audience_to_href = {role: href for role, href in cards}
    expected = {
        "audience-policymaker": "/8_Policy_Scenarios",
        "audience-nonprofit": "/2_Geographic_Intelligence",
        "audience-researcher": "/1_Executive_Overview",
    }
    for role, expected_href in expected.items():
        assert role in audience_to_href, (
            f"hero.html is missing the `{role}` CTA. Phase 4.1 requires "
            f"three audience-routed cards: policymaker / nonprofit / researcher."
        )
        href = audience_to_href[role]
        assert href == expected_href, (
            f"{role} card links to {href!r}, expected {expected_href!r}."
        )
        assert href.startswith("/"), (
            f"{role} href {href!r} should be a Streamlit page route "
            "(starts with /), not an internal anchor or external URL."
        )


def _internal_anchors(text: str):
    """Return all internal hrefs ('#foo'), excluding href='#' (no-op buttons)."""
    return {
        m.group(1)
        for m in re.finditer(r'href=[\'"]#([^\'">]+)[\'"]', text)
    }


def _ids(text: str):
    return {m.group(1) for m in re.finditer(r'id=[\'"]([^\'">]+)[\'"]', text)}


def test_every_internal_anchor_in_templates_has_matching_id():
    """
    Union all anchors across templates; union all ids across templates;
    assert anchors ⊆ ids. Catches dead anchors before they ship.
    """
    all_anchors = set()
    all_ids = set()
    for tmpl in _all_templates():
        text = tmpl.read_text()
        all_anchors |= _internal_anchors(text)
        all_ids |= _ids(text)

    # Also collect ids generated in views/home.py (e.g., hero-img, hero-label)
    home_py = (REPO_ROOT / "views" / "home.py").read_text()
    all_ids |= _ids(home_py)

    dangling = all_anchors - all_ids
    assert not dangling, (
        f"Internal anchors with no matching id in any home template or home.py: "
        f"{sorted(dangling)}. Either add the matching id, or repoint the href."
    )
