"""
T-Phase4.3 — mobile nav accessibility tests.

Pairs with Phase 4 task 4.3:
  - WCAG 2.5.5 Target Size (Level AAA): interactive nav elements ≥ 44×44px
  - Horizontal scroll affordance for the nav when content overflows
  - Flatten 3 single-item dropdowns (Policy Scenarios, AI Agent, Reports)
    so mobile users tap one link instead of opening a dropdown with
    exactly one entry in it

These are source-level CSS guards — they assert the rules exist, not
that they render correctly (visual verification requires the browser).
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _nav_css() -> str:
    return (REPO_ROOT / "utils" / "nav.css").read_text()


def test_touch_targets_meet_44px_minimum():
    """The nav-link / menu-item / hamburger selectors must declare min-height: 44px.

    WCAG 2.5.5 Target Size (Level AAA) requires interactive elements be
    at least 44×44px CSS pixels. Falling below this hurts tap accuracy
    for users with motor impairment.
    """
    src = _nav_css()
    # Find the block that asserts 44px and confirm the right selectors are present
    assert "min-height: 44px" in src, (
        "utils/nav.css should declare `min-height: 44px` on interactive "
        "nav elements (WCAG 2.5.5 Target Size)."
    )
    # All of these selectors must appear at least once in a min-height: 44px context.
    # Match the block by anchoring on the rule.
    import re
    block_pattern = re.compile(
        r"([^{]*)\{\s*[^}]*\bmin-height:\s*44px\b[^}]*\}",
        re.MULTILINE,
    )
    blocks = block_pattern.findall(src)
    combined = "\n".join(blocks)
    for selector in (".app-nav-link", ".app-menu-item", ".app-hamburger"):
        assert selector in combined, (
            f"{selector} should be one of the selectors that get min-height: 44px. "
            "Missing it means that interactive element doesn't meet WCAG 2.5.5."
        )


def test_hamburger_has_square_touch_target():
    """The hamburger is icon-only — needs min-width too so the tap area is square."""
    src = _nav_css()
    # Find any rule whose selector starts with `.app-hamburger` (standalone or in
    # a comma-list) and check whether it sets min-width: 44px.
    import re
    rule_pattern = re.compile(r"([^{}]*)\{([^{}]*)\}", re.DOTALL)
    found = False
    for selector, body in rule_pattern.findall(src):
        if ".app-hamburger" in selector and "min-width: 44px" in body:
            found = True
            break
    assert found, (
        "utils/nav.css should declare `min-width: 44px` on .app-hamburger. "
        "An icon-only element without a min-width can be narrower than 44px "
        "even with min-height: 44px set, missing WCAG 2.5.5."
    )


def test_mobile_scroll_affordance_present():
    """The mobile nav should show a fade gradient indicating it's horizontally scrollable."""
    src = _nav_css()
    # Affordance: at <=768px, .nav-inner-bar gets a horizontal-fade background-image
    assert "@media (max-width: 768px)" in src, "Expected mobile breakpoint media query."
    assert "linear-gradient" in src and "transparent 24px" in src, (
        "utils/nav.css mobile block should add a linear-gradient fade on the "
        "edges of .nav-inner-bar so users see the nav scrolls horizontally."
    )


def test_flatten_three_single_item_dropdowns_on_mobile():
    """The 3 single-item dropdowns must be flattened on mobile via :has() selectors."""
    src = _nav_css()
    for menu_id in ("nav-toggle-policy", "nav-toggle-ai", "nav-toggle-reports"):
        # Must reference the menu trigger and hide its label on mobile
        pattern = f'label[for="{menu_id}"]'
        assert pattern in src, (
            f"utils/nav.css should target `{pattern}` so the dropdown "
            "trigger is hidden on mobile and the inner link becomes a "
            "top-level item."
        )


def test_flatten_uses_has_selector_for_safety():
    """The flatten rules should use :has() (modern CSS) — guards against the
    rules sneaking out of their mobile-only @media block."""
    src = _nav_css()
    assert ":has(" in src, (
        "Mobile flatten rules should use the `:has()` selector to scope "
        "the change to ancestors of the three single-item triggers, not "
        "blanket-match all labels."
    )


def test_flatten_rules_inside_mobile_media_query():
    """The flatten rules must only fire at <=768px viewport (desktop unchanged)."""
    src = _nav_css()
    # Find the @media block containing nav-toggle-policy and verify it's the mobile one.
    import re
    # Match the @media block content
    media_match = re.search(
        r"@media\s*\(max-width:\s*768px\)\s*\{(.*?)\n\}",
        src,
        re.DOTALL,
    )
    # There are multiple @media blocks; find one containing the policy toggle
    media_blocks = re.findall(
        r"@media\s*\(max-width:\s*768px\)\s*\{(.*?)\n\}",
        src,
        re.DOTALL,
    )
    flatten_in_mobile = any(
        'label[for="nav-toggle-policy"]' in block for block in media_blocks
    )
    assert flatten_in_mobile, (
        "The flatten rules for the 3 single-item dropdowns must live inside "
        "an `@media (max-width: 768px)` block. Otherwise desktop loses the "
        "dropdown UX too."
    )
