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


def test_hero_primary_cta_points_to_valid_route():
    """The hero's primary CTA must point at a real Streamlit page route."""
    hero = (TEMPLATE_DIR / "hero.html").read_text()
    cta_match = re.search(r'<a[^>]+class="hero-btn-primary"[^>]+href="([^"]+)"', hero)
    if cta_match is None:
        cta_match = re.search(r'<a[^>]+href="([^"]+)"[^>]+class="hero-btn-primary"', hero)
    assert cta_match is not None, (
        "hero.html should contain an <a class='hero-btn-primary' href='...'> element."
    )
    href = cta_match.group(1)
    assert not href.startswith("#"), (
        f"hero-btn-primary still points at an internal anchor ({href!r}). "
        "It should link to a Streamlit page route like /1_Executive_Overview."
    )
    assert href.startswith("/") or href.startswith("http"), (
        f"hero-btn-primary href {href!r} doesn't look like a route or external URL."
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
