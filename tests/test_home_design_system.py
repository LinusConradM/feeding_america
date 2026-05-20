"""
T7 — design-system static analysis tests.

Pairs with Phase 5 task T7 (the original spec asked for "no hex literals
in home.py outside theme; no spacing values outside 4px grid in home.css").

Scope-adjusted in this session because Phase 3.1/3.3 are DEFERRED per
Q3 Option B (the home page stays as the marketing surface). The test
therefore enforces design-system discipline on the *in-app* views that
Phase 3.D migrated, not on home.py / home.css. The spacing-grid test
exists as a skipped placeholder so the intent is visible if Option B
is ever revisited.

What this file guards:

  1. utils/theme.py defines a non-empty COLORS palette.
  2. Seven fully-migrated in-app views (Regression Models, Equity
     Disparities, County Clustering, Time Series Explorer, Policy
     Scenarios, Data Downloads, Anomaly Detection) have ZERO inline
     hex literals — they must use COLORS tokens or CSS variables.
     If a new hex literal sneaks in, this test catches it.
  3. The four views with documented semantic-hex exceptions
     (Executive Overview, Geographic Intelligence, Data Explorer,
     Correlation Analysis, AI Data Analyst) don't *exceed* their
     current hex count. Pure ratchet: the count can shrink, never
     grow without an explicit allowlist update.

These are source-level grep checks — they don't render or execute
the views.
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VIEWS_DIR = REPO_ROOT / "views"

# Six-digit hex literal. The `\b` rules out partial matches inside longer
# tokens; `[0-9A-Fa-f]` matches both uppercase and lowercase hex digits,
# so `#FFFFFF` and `#ffffff` both count.
HEX_RE = re.compile(r"#[0-9A-Fa-f]{6}\b")


def _count_hex(path: Path) -> int:
    return len(HEX_RE.findall(path.read_text(encoding="utf-8")))


# ── 1. theme.py is the palette source of truth ───────────────────────────────


def test_theme_defines_a_palette():
    """utils/theme.py must define a non-empty COLORS dict with the canonical token names."""
    from utils.theme import COLORS

    assert isinstance(COLORS, dict)
    # Canonical tokens used across the in-app views (per Phase 3.D migration)
    expected = {
        "ink", "pearl", "snow", "slate", "steel", "silver",
        "sapphire", "ruby", "emerald", "amber", "amethyst",
        "white",
    }
    missing = expected - set(COLORS.keys())
    assert not missing, (
        f"utils/theme.py COLORS palette is missing canonical tokens: {sorted(missing)}. "
        "These names are used by Phase 3.D-migrated views; removing them "
        "would break those views."
    )


def test_theme_color_values_are_valid_hex():
    """Every COLORS value must be a 7-character hex string ('#RRGGBB')."""
    from utils.theme import COLORS

    bad = {k: v for k, v in COLORS.items() if not (
        isinstance(v, str)
        and v.startswith("#")
        and len(v) == 7
        and HEX_RE.fullmatch(v)
    )}
    assert not bad, (
        f"COLORS values must be '#RRGGBB' strings; these aren't: {bad}. "
        "Mixed shorthand (#FFF) or rgba() values would break the editorial "
        "system's consistency."
    )


# ── 2. Ratchet: post-Phase-3.D views must stay at 0 inline hex ───────────────

# Views that Phase 3.D migrated FULLY (PR #25, #26, #27 batch for non-hex
# views). These should have zero hex literals in source — all colors come
# from COLORS / PLOTLY_LAYOUT or CSS variables. If a developer adds inline
# `color: #abc123` to one of these, T7 catches it.
FULLY_MIGRATED_VIEWS = [
    "4_Regression_Models.py",      # PR #27 mapped all 10 hex to COLORS
    "5_Equity_Disparities.py",     # PR #26 simple batch
    "6_County_Clustering.py",      # PR #26 simple batch
    "7_Time_Series_Explorer.py",   # PR #26 simple batch
    "8_Policy_Scenarios.py",       # PR #26 simple batch
    "9_Data_Downloads.py",         # PR #26 simple batch
    "11_Anomaly_Detection.py",     # PR #25 template + PR #29 harmonization
]


def test_fully_migrated_views_have_zero_inline_hex():
    """The 7 Phase 3.D-fully-migrated views must have no inline hex literals.

    They use COLORS tokens, PLOTLY_LAYOUT, or st.title/st.caption — never
    hard-coded hex. This is the ratchet that prevents drift back toward
    the pre-migration McKinsey-era pattern of inline color literals.
    """
    offenders = {}
    for fname in FULLY_MIGRATED_VIEWS:
        path = VIEWS_DIR / fname
        count = _count_hex(path)
        if count > 0:
            offenders[fname] = count

    assert not offenders, (
        "These views had zero hex literals after Phase 3.D migration and "
        "must stay that way; new inline hex was introduced: "
        f"{offenders}. Replace each hex with a COLORS[...] token from "
        "utils/theme.py, or add a documented exception to T7's allowlist."
    )


# ── 3. Allowlist: tolerated semantic-hex views have a documented budget ──────

# Views that intentionally keep some hex literals for semantic reasons:
# chart palette values, brand identity (AI page's purple gradient), or
# Tailwind-shade banner colors with no clean COLORS equivalent.
# The number is the CURRENT count at the time T7 was written; it must
# not grow. Lowering it is welcome (just update the constant).
HEX_ALLOWLIST = {
    # PR #28: AI Data Analyst has 42 hex (purple gradient + 6-color card
    # variety + status-dot green + Tailwind grays) that constitute the
    # page's intentional brand identity, documented in the PR description.
    "10_AI_Data_Analyst.py": 42,
    # PR #27: Executive Overview kept hex for chart palette + a few
    # decorative banner shades. Counted at PR-#27 merge time.
    "1_Executive_Overview.py": 15,
    # PR #27 / PR #22: Geographic Intelligence has chart palette + a few
    # decorative shades.
    "2_Geographic_Intelligence.py": 10,
    # PR #27: Data Explorer kept 6 hex — chart colorscale + amber warning
    # banner (Tailwind amber-50/200/800) + green success callout.
    "0_Data_Explorer.py": 6,
    # PR #27: 1 hex (#8B0000 dark red) in a chart color_discrete_sequence.
    "3_Correlation_Analysis.py": 1,
}


def test_hex_allowlist_views_do_not_exceed_budget():
    """Each allowlisted view must have <= its budget of hex literals.

    The budget reflects the count documented at the PR that established
    the exception. The test ratchets: counts may shrink, never grow.
    """
    overspent = {}
    for fname, budget in HEX_ALLOWLIST.items():
        path = VIEWS_DIR / fname
        count = _count_hex(path)
        if count > budget:
            overspent[fname] = (count, budget)

    assert not overspent, (
        "Hex-allowlist budget exceeded:\n"
        + "\n".join(
            f"  {f}: now {c} hex, budget was {b}"
            for f, (c, b) in overspent.items()
        )
        + "\n\nEither replace the new hex with a COLORS token, or update "
        "the budget in HEX_ALLOWLIST after documenting why each new hex "
        "is intentional."
    )


def test_only_allowlisted_views_have_hex():
    """Any view file that has hex literals must appear in HEX_ALLOWLIST.

    Catches the case where someone introduces a new view with inline
    hex without going through the allowlist process.
    """
    rogue = {}
    for path in sorted(VIEWS_DIR.glob("*.py")):
        fname = path.name
        if fname == "home.py":
            continue  # Marketing surface — Phase 3.1/3.3 deferred (Q3 Option B)
        count = _count_hex(path)
        if count > 0 and fname not in HEX_ALLOWLIST:
            rogue[fname] = count

    assert not rogue, (
        f"These view files have inline hex literals but aren't in HEX_ALLOWLIST: "
        f"{rogue}. Either replace the hex with COLORS tokens, or add the file "
        "to HEX_ALLOWLIST with a budget + comment explaining the exception."
    )


# ── 4. Spacing grid (Phase 3.3 deferred) ─────────────────────────────────────


import pytest


@pytest.mark.skip(
    reason="Phase 3.3 (home.css spacing grid snap) is DEFERRED per Q3 Option B. "
    "Re-enable this test if the home page is ever migrated off its marketing "
    "surface treatment. See HOME_REDESIGN_TASK_TRACKER.md row 3.3."
)
def test_home_css_spacing_snaps_to_grid():
    """home.css spacing/radius values should snap to the design grid.

    Spacing ∈ {4, 8, 12, 16, 24, 32, 48, 64}
    Radius  ∈ {4, 6, 8, 999}
    One shadow elevation.

    Currently skipped because 3.3 is deferred. When re-enabled, this should
    parse home.css for `padding:`, `margin:`, `border-radius:` declarations
    and assert each numeric value is in the allowed set.
    """
    raise NotImplementedError
