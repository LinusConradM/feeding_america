"""
T-Phase4-content — home page copy regression tests.

Pairs with Phase 4 tasks 4.6 (bento card titles in question-led copy),
4.7 (drop DATA-613 Practicum framing from footer), and 4.8 (typo audit).

These tests guard against the old strings reappearing. They don't test
the *new* copy directly because exact wording may be tuned in follow-up
PRs without breaking the design intent — but the old strings are
specifically the ones the audit flagged, so their return would be a
real regression.
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = REPO_ROOT / "views" / "templates"


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text()


# ── Task 4.6: bento card titles must be question-led ─────────────────────────


def test_bento_no_legacy_builder_voice_titles():
    """Five bento card titles flagged in the audit must not return verbatim."""
    src = _read("views/templates/bento.html")
    legacy_titles = [
        "Autonomous Agentic Reasoning",
        "Causal Inference Engine",
        "Spatially-Weighted Clustering",
        "Time Series Forecasting",
        "Unsupervised Outlier Detection",
    ]
    offenders = [t for t in legacy_titles if t in src]
    assert not offenders, (
        f"bento.html still contains legacy builder-voice card titles: {offenders}. "
        "Phase 4.6 replaced them with question-led copy (e.g., 'Ask in plain English'). "
        "Either re-write the title in question form or update this test if the "
        "design has shifted."
    )


def test_bento_has_at_least_three_question_titles():
    """At least 3 of the 5 bento cards should have a question-led title (ends with ?)."""
    src = _read("views/templates/bento.html")
    import re
    # Match <div class="card-title"...>...?</div> where the inner text ends with ?
    titles = re.findall(r'<div class="card-title"[^>]*>([^<]+)</div>', src)
    question_titles = [t for t in titles if t.strip().endswith("?")]
    assert len(question_titles) >= 3, (
        f"Phase 4.6 asks for question-led bento card titles. Currently only "
        f"{len(question_titles)} title(s) end with '?': {question_titles}. "
        "Audit found 5 card titles — at least 3 should be questions."
    )


# ── Task 4.7: footer must drop "DATA-613 Practicum" framing ──────────────────


def test_footer_drops_practicum_framing():
    """Footer must not still reference 'DATA-613' or 'Practicum' framing.

    Q-driven rewording: the home page positions the project as
    independent research, not coursework. The footer used to read
    'Built at American University for DATA-613: Data Science Practicum.'
    """
    src = _read("views/templates/footer.html")
    for legacy in ("DATA-613", "Practicum", "Data Science Practicum"):
        assert legacy not in src, (
            f"views/templates/footer.html still contains '{legacy}'. "
            "Phase 4.7 reframed the footer as independent research; the "
            "course-internal framing was flagged in the audit."
        )


def test_footer_still_credits_american_university():
    """The reframed footer should still attribute the work to American University."""
    src = _read("views/templates/footer.html")
    assert "American University" in src, (
        "Footer should still credit American University, just without the "
        "'DATA-613 Practicum' coursework framing."
    )


# ── Task 4.8: typo audit ─────────────────────────────────────────────────────


def test_marquee_strip_removed():
    """Phase 4.2: the marquee pill strip and its CSS must be gone."""
    home_py = _read("views/home.py")
    home_css = _read("views/home.css")
    # The Python emission and its data structure must be removed
    assert "MARQUEE_PILLS" not in home_py, (
        "views/home.py still defines MARQUEE_PILLS. Phase 4.2 cut the marquee "
        "strip — the audit flagged it as builder-voice signal noise (method "
        "names instead of user questions)."
    )
    assert 'class="marquee-section"' not in home_py, (
        "views/home.py still emits the .marquee-section div. Remove the "
        "st.html() call along with MARQUEE_PILLS / pill_html."
    )
    # CSS for the marquee should be gone too (no dead styles left behind)
    for stale_class in (".marquee-section", ".marquee-track", ".marquee-pill"):
        assert stale_class + " {" not in home_css, (
            f"views/home.css still defines `{stale_class}`. Cut the styles "
            "alongside the markup so no dead CSS lingers."
        )
    assert "@keyframes marqueeScroll" not in home_css, (
        "views/home.css still defines @keyframes marqueeScroll. Cut it."
    )


def test_bento_terminal_mockup_removed():
    """Phase 4.2: the fake terminal mockup inside the AI bento card must be gone."""
    src = _read("views/templates/bento.html")
    for stale in ('class="terminal"', "term-dots", "term-line", "term-user", "term-agent"):
        assert stale not in src, (
            f"views/templates/bento.html still contains terminal-mockup markup ('{stale}'). "
            "Phase 4.2 cut the embedded terminal prop — the card body already "
            "describes the AI workflow."
        )


def test_bento_latex_did_tile_removed():
    """Phase 4.2: the DiD LaTeX estimator tile inside the causal card must be gone."""
    src = _read("views/templates/bento.html")
    # The mathematical formula was the distinctive marker — drop it
    assert "DiD Estimator" not in src, (
        "views/templates/bento.html still shows the 'DiD Estimator' tile. "
        "Phase 4.2 cut the LaTeX tile — the card body explains the technique."
    )
    # The Geist Mono LaTeX rendering was the visual marker
    assert "β̂" not in src, (
        "views/templates/bento.html still renders the β̂ formula tile. Cut it."
    )


def test_us_period_consistency_in_templates():
    """All home-page templates must use 'U.S.' with the trailing period."""
    import re
    # Match 'U.S' followed by a space or non-period character — that's the typo
    # shape. 'U.S.' (with period) is fine.
    typo_pattern = re.compile(r"\bU\.S(?!\.)\b")
    offenders = []
    for tmpl in sorted(TEMPLATE_DIR.glob("*.html")):
        text = tmpl.read_text()
        if typo_pattern.search(text):
            offenders.append(tmpl.name)
    assert not offenders, (
        f"Templates still contain 'U.S' without the trailing period: {offenders}. "
        "Phase 4.8 fixed views/templates/hero.html; this test guards against "
        "the typo returning anywhere in the home-page surface."
    )
