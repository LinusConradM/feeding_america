"""
T-Phase3C — accessibility polish tests for inject_tailwind().

Pairs with Phase 3.C (task 3.4): every interactive element must have a
keyboard focus indicator (WCAG 2.4.7 Focus Visible), and the app must
respect the OS-level `prefers-reduced-motion` preference (WCAG 2.3.3
Animation from Interactions).

inject_tailwind() is the single global CSS injection called from app.py;
adding the rules there once propagates them to every page. These tests
read the CSS string the function emits and assert the relevant rules
are present.
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _theme_source() -> str:
    return (REPO_ROOT / "utils" / "theme.py").read_text()


def test_focus_visible_rule_present():
    """A `:focus-visible` rule must exist somewhere in inject_tailwind's CSS."""
    src = _theme_source()
    assert ":focus-visible" in src, (
        "utils/theme.py inject_tailwind() should define a `:focus-visible` rule "
        "for keyboard focus accessibility (WCAG 2.4.7). Even one universal "
        "selector is enough to provide an app-wide focus indicator."
    )


def test_focus_visible_uses_visible_outline():
    """The focus indicator must use a non-transparent outline (visible)."""
    src = _theme_source()
    # Find the :focus-visible block and ensure it has an `outline:` declaration
    # with a non-zero / non-none value. Catches regressions like `outline: none`
    # which is a common 'just remove the focus ring' anti-pattern.
    assert "*:focus-visible" in src, "Expected universal :focus-visible selector"
    # The rule should set an outline width (we use 2px). Guard against
    # someone "fixing" the rule by setting outline: none.
    assert "outline: 2px" in src, (
        "Focus-visible rule should set a visible outline (currently `2px`). "
        "Setting `outline: none` removes the keyboard indicator entirely — "
        "a known WCAG 2.4.7 violation."
    )


def test_prefers_reduced_motion_block_present():
    """A `@media (prefers-reduced-motion: reduce)` block must be defined."""
    src = _theme_source()
    assert "prefers-reduced-motion: reduce" in src, (
        "utils/theme.py inject_tailwind() should define a "
        "`@media (prefers-reduced-motion: reduce)` block (WCAG 2.3.3). "
        "Home page has at least 4 long-running animations (FI ticker, "
        "marquee, KPI orbit, pulse) plus the AI Data Analyst status dot — "
        "users with vestibular disorders need a way to opt out."
    )


def test_reduced_motion_uses_universal_selector():
    """The reduced-motion override must catch every animation, not just enumerated ones."""
    src = _theme_source()
    # Look for the universal selector pattern (`*, *::before, *::after`) inside
    # the reduced-motion block. Enumerated selectors (e.g., `.fi-ticker`) miss
    # any animation added later — defense in depth via universal selector.
    rm_idx = src.find("prefers-reduced-motion: reduce")
    assert rm_idx != -1
    # Take a window after the block start to scan for the selector
    window = src[rm_idx : rm_idx + 800]
    assert "*, *::before, *::after" in window, (
        "Reduced-motion block should use the universal selector "
        "`*, *::before, *::after` so animations added in later commits "
        "or inline <style> blocks (e.g., the AI Data Analyst pulse-dot) "
        "are auto-covered."
    )


def test_reduced_motion_uses_important_to_override_inline_animation():
    """The animation-duration override must use !important to defeat inline `animation: ... 2s` declarations."""
    src = _theme_source()
    rm_idx = src.find("prefers-reduced-motion: reduce")
    window = src[rm_idx : rm_idx + 800]
    assert "animation-duration: 0.01ms !important" in window, (
        "Reduced-motion block should declare "
        "`animation-duration: 0.01ms !important` so it overrides any "
        "inline `animation: name 2s infinite` declaration from home.css "
        "or the AI Data Analyst inline <style>."
    )
