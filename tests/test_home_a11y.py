"""
T6 — consolidated home-page accessibility tests.

Pairs with Phase 5 task T6. The earlier a11y tests
(test_a11y_focus_and_reduced_motion.py, test_a11y_skip_link.py) read
utils/theme.py as source text. This file renders the real home page
(app.py's default route) with Streamlit's AppTest harness and checks the
HTML a browser would receive, in document order:

  1. Landmark: the #main-content sentinel (the WCAG-equivalent of a
     <main> landmark; Streamlit gives us no wrappable element, see
     inject_main_landmark()) sits after the global <nav> and before the
     hero, so the skip-link actually bypasses the nav.
  2. Skip-link: it is the first focusable element on the page and its
     target id exists.
  3. Focus visibility: the rendered CSS has a universal :focus-visible
     outline and no rule anywhere strips outlines (`outline: none|0`).
  4. Images: every <img> has a non-empty alt.
  5. Names: every focusable element has an accessible name.
"""
import re
from pathlib import Path

import pytest
from bs4 import BeautifulSoup
from streamlit.testing.v1 import AppTest

REPO_ROOT = Path(__file__).resolve().parent.parent

FOCUSABLE = "a[href], button, input, select, textarea, [tabindex]"


@pytest.fixture(scope="module")
def home_bodies():
    """Ordered list of HTML/markdown bodies emitted on the home route."""
    at = AppTest.from_file(str(REPO_ROOT / "app.py"), default_timeout=120).run()
    assert not at.exception, f"Home page raised: {at.exception}"
    return [n.proto.body for n in at.main if n.type in ("html", "markdown")]


@pytest.fixture(scope="module")
def home_soup(home_bodies):
    return BeautifulSoup("\n".join(home_bodies), "html.parser")


@pytest.fixture(scope="module")
def home_css(home_soup):
    return "\n".join(tag.get_text() for tag in home_soup.find_all("style"))


def _index_of(bodies, needle):
    for i, body in enumerate(bodies):
        if needle in body:
            return i
    raise AssertionError(f"{needle!r} not found in rendered home page")


# ── 1. Landmark ──────────────────────────────────────────────────────────────


def test_main_content_sentinel_present(home_soup):
    target = home_soup.find(id="main-content")
    assert target is not None, "Rendered home page has no #main-content sentinel."
    assert target.get("tabindex") == "-1", (
        "#main-content must be programmatically focusable (tabindex=-1) so "
        "activating the skip-link moves focus there."
    )


def test_main_content_sits_between_nav_and_hero(home_bodies):
    nav = _index_of(home_bodies, 'id="main-nav"')
    main = _index_of(home_bodies, 'id="main-content"')
    hero = _index_of(home_bodies, 'id="hero"')
    assert nav < main < hero, (
        "#main-content must come after the global nav and before the hero, "
        f"otherwise the skip-link doesn't skip the nav (nav={nav}, "
        f"main-content={main}, hero={hero})."
    )


# ── 2. Skip-link ─────────────────────────────────────────────────────────────


def test_skip_link_is_first_focusable_element(home_soup):
    first = home_soup.select_one(FOCUSABLE)
    assert first is not None and "skip-link" in (first.get("class") or []), (
        f"First focusable element on the home page should be the skip-link, got: {first}"
    )


def test_skip_link_target_exists(home_soup):
    link = home_soup.select_one("a.skip-link")
    target_id = link["href"].lstrip("#")
    assert home_soup.find(id=target_id) is not None, (
        f"Skip-link points to #{target_id}, which isn't on the rendered page."
    )


# ── 3. Focus visibility ──────────────────────────────────────────────────────


def test_universal_focus_visible_outline_rendered(home_css):
    rule = re.search(r"\*:focus-visible\s*\{([^}]*)\}", home_css)
    assert rule, "Rendered CSS has no universal `*:focus-visible` rule."
    assert re.search(r"outline\s*:\s*[1-9]", rule.group(1)), (
        "`*:focus-visible` must set a visible outline width."
    )


def test_no_rule_strips_outline(home_css):
    offenders = [
        sel.strip()[-80:]
        for sel, body in re.findall(r"([^{}]*)\{([^{}]*)\}", home_css)
        if re.search(r"outline\s*:\s*(none|0)\b", body)
    ]
    assert not offenders, (
        "These rendered CSS rules remove the focus outline, which hides the "
        f"keyboard focus ring on matching elements: {offenders}"
    )


# ── 4. Images ────────────────────────────────────────────────────────────────


def test_every_img_has_alt(home_soup):
    imgs = home_soup.find_all("img")
    assert imgs, "Expected at least the hero screenshot <img> on the home page."
    missing = [img.get("id") or img.get("src", "")[:40] for img in imgs
               if not (img.get("alt") or "").strip()]
    assert not missing, f"<img> elements without alt text: {missing}"


# ── 5. Accessible names ──────────────────────────────────────────────────────


def _accessible_name(el, soup):
    if el.get("aria-label") or el.get("title"):
        return el.get("aria-label") or el.get("title")
    if el.get("aria-labelledby"):
        ref = soup.find(id=el["aria-labelledby"])
        return ref.get_text(" ", strip=True) if ref else ""
    if el.name == "input" and el.get("id"):
        labels = soup.select(f'label[for="{el["id"]}"]')
        return " ".join(l.get_text(" ", strip=True) for l in labels).strip()
    text = el.get_text(" ", strip=True)
    alts = " ".join(img.get("alt", "") for img in el.find_all("img"))
    return (text + " " + alts).strip()


def test_every_focusable_element_has_accessible_name(home_soup):
    unnamed = [
        str(el)[:120]
        for el in home_soup.select(FOCUSABLE)
        if el.get("tabindex") != "-1" and not _accessible_name(el, home_soup)
    ]
    assert not unnamed, (
        "Focusable elements a screen reader would announce with no name: "
        f"{unnamed}"
    )
