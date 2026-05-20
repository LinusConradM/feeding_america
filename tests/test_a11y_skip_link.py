"""
T-Phase4.4 — skip-link + main-content anchor tests.

Pairs with Phase 4 task 4.4 (originally "Add <main role='main'> landmark
+ 'skip to main content' anchor"). Streamlit's DOM does not allow
wrapping content in a literal <main> element, so the implementation
uses the WCAG-equivalent skip-link + named-anchor pattern:

  1. inject_tailwind() emits a `.skip-link` <a> at the top of the DOM
     that is offscreen until it receives keyboard focus.
  2. A new inject_main_landmark() emits a focusable
     <a id="main-content" tabindex="-1" class="sr-only"> sentinel after
     the global nav, which is what the skip-link targets.
  3. app.py wires the two together.

This test file reads source as text rather than rendering Streamlit,
to match the testing style used by the other home + a11y tests.
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text()


# ── inject_tailwind side: CSS rules + skip-link element ──────────────────────


def test_skip_link_css_rule_present():
    """utils/theme.py inject_tailwind() must define a `.skip-link` CSS rule."""
    src = _read("utils/theme.py")
    assert ".skip-link {" in src, (
        "utils/theme.py inject_tailwind() should define a `.skip-link` rule "
        "in its CSS block (Phase 4.4)."
    )


def test_skip_link_is_offscreen_until_focused():
    """The skip-link must be off-screen by default, on-screen on :focus.

    Catches the common bug of leaving the skip-link visible all the time
    (which clutters every page) or completely hidden with `display:none`
    (which removes it from the tab order, defeating its purpose)."""
    src = _read("utils/theme.py")
    # Default: top: -50px (or any negative top) — offscreen
    assert "top: -50px" in src, (
        ".skip-link default position should be top: -50px (offscreen). "
        "Don't use display:none — that removes it from the tab order."
    )
    # Focused: pulled into the viewport
    assert ".skip-link:focus" in src, (
        ".skip-link must have a :focus rule so it becomes visible when "
        "the keyboard user reaches it via Tab."
    )


def test_sr_only_helper_present():
    """The `.sr-only` (screen-reader-only) helper class must be defined."""
    src = _read("utils/theme.py")
    assert ".sr-only {" in src, (
        "utils/theme.py inject_tailwind() should define a `.sr-only` helper "
        "used by the #main-content sentinel and any future screen-reader-only "
        "content."
    )
    # The standard WCAG-recommended clip rect
    assert "clip: rect(0,0,0,0)" in src, (
        ".sr-only should use `clip: rect(0,0,0,0)` (with the other "
        "1px/-1px tricks) so content is announced by screen readers but "
        "not visible/clickable. Avoid `display:none` (also hides from AT)."
    )


def test_inject_tailwind_emits_skip_link_anchor():
    """inject_tailwind() must emit an <a class='skip-link'> element targeting #main-content."""
    src = _read("utils/theme.py")
    assert 'class="skip-link" href="#main-content"' in src, (
        "inject_tailwind() should emit `<a class=\"skip-link\" "
        "href=\"#main-content\">Skip to main content</a>` after its CSS "
        "block so the link sits at the top of the DOM."
    )
    assert "Skip to main content" in src, (
        "The skip-link text should be 'Skip to main content' (the WCAG-"
        "standard wording; screen readers and visual users both expect it)."
    )


# ── inject_main_landmark() side: the target sentinel ─────────────────────────


def test_inject_main_landmark_function_exists():
    """A function `inject_main_landmark` must be defined in utils/theme.py."""
    src = _read("utils/theme.py")
    assert "def inject_main_landmark(" in src, (
        "utils/theme.py should define `inject_main_landmark()` so app.py "
        "can call it after inject_global_nav() to position the skip-link "
        "target past the navigation."
    )


def test_inject_main_landmark_emits_named_anchor():
    """The function must emit `<a id="main-content" tabindex="-1">`."""
    src = _read("utils/theme.py")
    # The skip link targets `#main-content` — there must be exactly one
    # matching id in the emitted HTML.
    assert 'id="main-content"' in src, (
        "inject_main_landmark() should emit an element with id=\"main-content\" "
        "so the skip-link's href=\"#main-content\" has a target."
    )
    # tabindex=-1 so JS / browser can move focus to it programmatically
    # (clicking a same-page link focuses the target only if it's focusable).
    assert 'tabindex="-1"' in src, (
        "The #main-content anchor should carry `tabindex=\"-1\"`. Without "
        "it, the browser scrolls to the anchor but does not move keyboard "
        "focus there — defeating the skip-link's purpose for screen-reader "
        "and keyboard-only users."
    )
    # sr-only so the sentinel is not visually noisy
    assert 'class="sr-only"' in src, (
        "The #main-content anchor should be `class=\"sr-only\"` so it's "
        "announced by screen readers (when focus moves to it) but not "
        "rendered visually."
    )


# ── app.py side: wiring the two halves together ──────────────────────────────


def test_app_py_imports_inject_main_landmark():
    """app.py should import inject_main_landmark from utils.theme."""
    src = _read("app.py")
    assert "inject_main_landmark" in src, (
        "app.py should import and call inject_main_landmark() (Phase 4.4)."
    )


def test_app_py_calls_landmark_after_global_nav():
    """The landmark must be emitted AFTER inject_global_nav() — otherwise the
    skip-link target would sit before the navigation, defeating the point."""
    src = _read("app.py")
    # Match the actual call sites, not docstrings/comments that mention them.
    # Each callsite occupies its own line starting at column 0.
    lines = src.splitlines()
    nav_line = next(
        (i for i, line in enumerate(lines) if line.strip() == "inject_global_nav()"),
        None,
    )
    landmark_line = next(
        (i for i, line in enumerate(lines) if line.strip() == "inject_main_landmark()"),
        None,
    )
    pg_run_line = next(
        (i for i, line in enumerate(lines) if line.strip() == "pg.run()"),
        None,
    )

    assert nav_line is not None, "app.py should call inject_global_nav() at top level"
    assert landmark_line is not None, "app.py should call inject_main_landmark() at top level"
    assert pg_run_line is not None, "app.py should call pg.run() at top level"

    assert nav_line < landmark_line, (
        "inject_main_landmark() must be called AFTER inject_global_nav() "
        "so the #main-content anchor lives past the nav in the DOM. "
        "Otherwise skipping to #main-content lands the user BEFORE the nav."
    )
    assert landmark_line < pg_run_line, (
        "inject_main_landmark() must be called BEFORE pg.run() so the "
        "sentinel anchor exists in the DOM before the view module renders "
        "its own content."
    )
