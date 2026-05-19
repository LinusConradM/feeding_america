# Home Page Redesign — Task Tracker

> **Living document.** Update on every state change. Do not let this drift from reality — a stale tracker is worse than no tracker.

**Last updated:** 2026-05-19 by Claude (Phase 2 merged in [PR #22](https://github.com/LinusConradM/feeding_america/pull/22) — 8 commits closing tasks 2.1-2.6 plus DS-2/3/5/6/7/8 insight panels and partial credit on 3.1 / 4.4. Phase 3 + Phase 4 unblocked.)
**Source review:** Home Page Review consolidated report (May 5, 2026)
**Source plan:** Home Page Remediation Execution Plan (May 5, 2026)
**Maintainer:** Conrad Linus Muhirwe
**Branch strategy:** one feature branch per phase → integration branch `home-redesign` → single squashed PR into `main` per phase

---

## Status Dashboard

| Phase | TODO | WIP | REVIEW | DONE | BLOCKED | Total |
|-------|-----:|----:|-------:|-----:|--------:|------:|
| 0 — Pre-flight | 0 | 0 | 0 | 2 | 0 | 2 |
| 1 — Stop misinformation | 0 | 0 | 0 | 4 | 0 | 4 |
| 2 — Data backbone | 0 | 0 | 0 | 6 | 0 | 6 |
| 3 — Component & tokens | 4 | 0 | 0 | 0 | 0 | 4 |
| 4 — Audience redesign | 7 | 1 | 0 | 0 | 0 | 8 |
| 5 — Test backfill | 4 | 0 | 0 | 4 | 0 | 8 |
| 6 — Backlog | 5 | 0 | 0 | 0 | 0 | 5 |
| DS — Insight panels | 0 | 0 | 0 | 6 | 0 | 6 |
| Q — Maintainer Q's | 0 | 0 | 0 | 7 | 0 | 7 |
| **Total** | **20** | **1** | **0** | **29** | **0** | **50** |

**Progress:** 58% complete (29 / 50 tasks merged on `main`).
**Critical path:** Phase 3 (component & token migration, blocked on a Q3-driven scope re-plan) and Phase 4 (audience redesign) now run in parallel. Highest-leverage near-term work outside those phases is T8 (CI bootstrap) — exposed as a process gap on 2026-05-19 when PR #14 merged with broken imports because no CI ran.
**Note:** Phase 2 work made partial progress on 3.1 (COLORS tokens on Executive Overview + Geographic Intelligence) and 4.4 (ARIA landmarks added on those surfaces); 4.4 is the only Phase 4 task that's WIP from that spillover.
**Process gap exposed 2026-05-19:** PR #14 merged with broken imports because no CI ran on the PR. Local dev passed because helpers existed as uncommitted WIP. Hotfix PR #18 landed ~4 hours later. T8 (CI bootstrap, Phase 5) captures the fix.

### Phase gate status

- [x] Phase 0 complete → unblocks Phase 1 ✅ (2026-05-14)
- [x] Phase 1 complete → unblocks Phase 2 ✅ (2026-05-19, [PR #14](https://github.com/LinusConradM/feeding_america/pull/14) + hotfix [PR #18](https://github.com/LinusConradM/feeding_america/pull/18))
- [x] Phase 2 complete → unblocks Phase 3 + Phase 4 (parallel) ✅ (2026-05-19, [PR #22](https://github.com/LinusConradM/feeding_america/pull/22))
- [ ] Phase 3 + Phase 4 complete → unblocks final ship
- [ ] Phase 5 — runs alongside, not gating
- [ ] Phase 6 — post-ship polish

---

## Status Legend

| Status | Meaning |
|--------|---------|
| `TODO` | Not started |
| `WIP` | In progress |
| `REVIEW` | Code complete, awaiting code review |
| `DONE` | Merged into main |
| `BLOCKED` | Cannot proceed (see Notes column for reason) |
| `DEFERRED` | Moved out of current redesign |

---

## How To Update This File

When a task's state changes (started, blocked, finished):

1. Edit the row's **Status** column.
2. Add the PR / commit ref to the **PR** column when code lands.
3. If status is `DONE`, add the merge date in **Notes**.
4. If status is `BLOCKED`, write the reason in **Notes** (one sentence).
5. Update the **Status Dashboard** counts at the top.
6. Update the **Last updated** stamp at the top with date + who/what made the change.
7. If you discover a new task during the work, add a row at the bottom of the relevant phase with the next ID (e.g., `4.9`), and bump the dashboard count.

A future Claude session reading this file should be able to know exactly where work stands without re-reading the review.

---

## Phase 0 — Pre-Flight

Goal: unblock everything downstream. **Nothing else starts until Phase 0 is done.**

| ID | Status | Task | Owner | Deps | PR | Notes |
|----|--------|------|-------|------|-----|-------|
| 0.1 | DONE | Triage `app.py:84-92` `exec()` block — identify, de-obfuscate, decide keep/remove | DevOps + Maintainer | — | [#13](https://github.com/LinusConradM/feeding_america/pull/13) | Merged 2026-05-14. Confirmed hostile (multi-stage malware loader, *Contagious Interview / DEV#POPPER* pattern). Stripped from `main` in commit `abe5396`. Local-host IoC clean. shinyapps.io deployment offline. Affected keys rotated. See [SECURITY.md](../SECURITY.md). |
| 0.2 | DONE | Maintainer answers Q1–Q7; commit memo to `Project Documents/HOME_REDESIGN_DECISIONS.md` | Maintainer | 0.1 | — | All 7 Qs resolved 2026-05-14. Memo at [HOME_REDESIGN_DECISIONS.md](HOME_REDESIGN_DECISIONS.md). Notable: Q3 expanded Phase 3 scope (McKinsey removed across whole app, not just home). |

### Phase 0 acceptance criteria

- `exec()` block provenance is documented in the decisions memo (kept-and-justified or removed-and-rotated).
- All 7 maintainer questions have a written answer.
- Decisions memo is committed and linked from this tracker.

---

## Phase 1 — Stop Publishing Misinformation

Goal: every visible number is correct or removed. The primary CTA works. The caching comments tell the truth.

| ID | Status | Task | Owner | Deps | PR | Notes |
|----|--------|------|-------|------|-----|-------|
| 1.1 | DONE | FI ticker: replace `.mean()` with `weighted_rate_by_group` (helper at `data_loader.py:201`) | data-scientist | 0.2 | [#14](https://github.com/LinusConradM/feeding_america/pull/14) `5c55c40` + hotfix [#18](https://github.com/LinusConradM/feeding_america/pull/18) `22eb4a1` | Merged 2026-05-19. Empirical error was +1.74pp in 2019. "Coverage gap: 2011-2012" caveat added. **Post-merge bug**: PR #14 imported the `weighted_rate_by_group` helper but never staged the function definition into `utils/data_loader.py` — home page broke on fresh checkouts until hotfix #18 landed ~4 hours later. |
| 1.2 | DONE | KPI #1 "44.2M Americans" → compute from `df`, add year stamp + "Feeding America, MMG" | data-analyst | 0.2 (Q2) | [#14](https://github.com/LinusConradM/feeding_america/pull/14) `51072dd` | Merged 2026-05-19. 2023 actual = 46.7M. README updated to drop 44.2M figure. |
| 1.3 | DONE | Fix dead `#gallery` CTA: restore template render OR repoint anchor | software-engineer | 0.2 (Q4) | [#14](https://github.com/LinusConradM/feeding_america/pull/14) `1b1177a` | Merged 2026-05-19. Gallery template deleted per Q4; primary CTA repointed to `/1_Executive_Overview`. |
| 1.4 | DONE | Resolve caching lie: restore `@st.cache_data` on `_load_template`/`_load_css` OR delete the 6 lying inline comments + update perf doc | devops-engineer | 0.2 (Q5) | [#14](https://github.com/LinusConradM/feeding_america/pull/14) `ee3506c` | Merged 2026-05-19. Decorators restored per Q5 (accidental strip). |

### Phase 1 acceptance criteria

- Every number on the home page is computed from `load_data()` with year + source visible (or removed entirely).
- No `href="#..."` points to an anchor that doesn't exist.
- Inline `# OPTIMIZATION` comments match actual decorator state.
- Each fix lands with a corresponding test from Phase 5 (T1, T2, T3, T4).

---

## Phase 2 — Data & Plumbing Backbone

Goal: home page reads from real data correctly, no silent failures, no duplicated logic.

| ID | Status | Task | Owner | Deps | PR | Notes |
|----|--------|------|-------|------|-----|-------|
| 2.1 | DONE | All 4 KPI cards data-derived; build `home_kpis()` helper | data-analyst + software-engineer | 1.2 | [#22](https://github.com/LinusConradM/feeding_america/pull/22) `58dd277` + `3644afe` + `57abbbc` | Merged 2026-05-19. Three-page migration: Executive Overview (`calc_metrics`), Geographic Intelligence (weighted spatial KPIs), and the home page (`_compute_home_kpis`). The `kpi_row()` component migration noted in the original task description is deferred to Phase 3 (template → component refactor needs visual review). |
| 2.2 | DONE | De-duplicate `_get_fi_ticker_html` between `home.py` and `utils/navigation.py` → extract to `utils/ticker.py` | software-engineer | 1.1 | [#22](https://github.com/LinusConradM/feeding_america/pull/22) `e04004d` | Merged 2026-05-19. New `utils/ticker.py` is single source of truth; both call sites import via `from utils.ticker import get_fi_ticker_html as _get_fi_ticker_html`. One cache, one `load_data()` read per page. |
| 2.3 | DONE | Fix `home.py:266` JS selector `.menu-item` → `.app-menu-item` | software-engineer + qa-tester | — | [#22](https://github.com/LinusConradM/feeding_america/pull/22) `161e80a` | Merged 2026-05-19. Reactive screenshot now actually fires on nav-item hover; regression test in T3 guards the selector. |
| 2.4 | DONE | Add explicit logging to `_load_and_encode_image`; move pre-loads from import-time to `_warm_image_cache()` | software-engineer | — | [#22](https://github.com/LinusConradM/feeding_america/pull/22) `6d10855` | Merged 2026-05-19. Logger now emits a WARNING on missing-file and exception traceback on encode failure. Eager pre-load wrapped in `_warm_image_cache()`; T4 has a caplog-based test asserting the logging behavior. |
| 2.5 | DONE | Add MMG disclaimer banner: "Estimates derived from Feeding America's MMG. Methodology revised in 2020." | data-scientist | — | [#22](https://github.com/LinusConradM/feeding_america/pull/22) `231ece9` | Merged 2026-05-19. Banner sits under the KPI strip with a link to map.feedingamerica.org and the 2020-methodology-revision caveat. T1 has a presence test. |
| 2.6 | DONE | Rename `images/Critical Path.png` → `images/critical_path.png`; update reference in `home.py` | software-engineer | — | [#22](https://github.com/LinusConradM/feeding_america/pull/22) `aaec49c` | Merged 2026-05-19. Both call sites updated; T4 has a regex-based guard asserting no `_load_and_encode_image` call references a filename with a space. |

### Phase 2 acceptance criteria

- All four KPI cards return values from `load_data()`.
- `grep -n "_get_fi_ticker_html" .` returns one definition (in `utils/ticker.py`).
- `_load_and_encode_image` failures produce a log entry, not a silent empty string.
- No `<img>` references a path containing a space.

---

## Phase 3 — Component & Token Migration

Goal: home page joins the rest of the application's design system. **Blocked on Q3 (is the dark-indigo surface intentional?).**

If maintainer answers "match McKinsey" → execute as written below.
If maintainer answers "intentional marketing surface" → compress Phase 3 to ~2 days of token-namespace + decisions doc.

| ID | Status | Task | Owner | Deps | PR | Notes |
|----|--------|------|-------|------|-----|-------|
| 3.1 | TODO | Replace `home.css:75-93` `:root` palette with `COLORS[]`-derived CSS-vars; restore Georgia for `.hero-title` / `.section-title` / `.kpi-val` | ui-designer + software-engineer | 0.2 (Q3) | partial: [#22](https://github.com/LinusConradM/feeding_america/pull/22) (Exec Overview + Geographic Intelligence only) | Either generate from `theme.py` at app load, or hand-translate. **Partial credit landed in PR #22:** Executive Overview hero / state summary card + Geographic Intelligence header / sidebar migrated off hex literals onto `COLORS` tokens. Pattern is proven; remaining work is `home.css` plus the other views. |
| 3.2 | TODO | Migrate `home.py` to use `kpi_row` / `section_header` / `info_banner` / `hero_section` from `utils/components.py`; delete equivalent template HTML | ui-designer + software-engineer | 3.1, 0.2 (Q3) | — | Coordinate with Phase 4 — touches same files |
| 3.3 | TODO | Snap every spacing/radius/shadow value in `home.css` to design grid: spacing ∈ {4,8,12,16,24,32,48,64}, radius ∈ {4,6,8,999}, one shadow elevation | ui-designer | 3.1 | — | Verify with `test_home_design_system.py` (T7) |
| 3.4 | TODO | Add `:focus-visible` styles + `@media (prefers-reduced-motion: reduce)` overrides | ui-designer + ux-designer | 3.1 | — | Disable marquee, KPI orbit, ticker scroll, badge pulse under reduced-motion |

### Phase 3 acceptance criteria

- Zero hex literals in `home.py` outside `theme.py`.
- Zero off-grid spacing in `home.css`.
- Every interactive element has all four states (default/hover/active/focus).
- `project-reviewer` skill audit passes on the design-system checklist.

---

## Phase 4 — Audience Redesign

Goal: home page serves all three target audiences in <10 seconds. **Runs concurrently with Phase 3 — share branch.**

| ID | Status | Task | Owner | Deps | PR | Notes |
|----|--------|------|-------|------|-----|-------|
| 4.1 | TODO | Rewrite hero subhead with three audience-routed CTAs (policymaker / nonprofit / researcher) | stakeholder-advocate + ux-designer | 0.2 (Q7) | — | Replaces builder-voice "Investigating patterns…" |
| 4.2 | TODO | Cut marquee strip, LaTeX tile, terminal mockup; replace 3 of 4 KPIs with insight numbers (national rate, counties >20% FI, YoY change) | stakeholder-advocate + data-analyst | 2.1 | — | Keep "Americans affected" as anchor |
| 4.3 | TODO | Mobile nav fix: scroll affordance, 44×44px touch targets, flatten single-item dropdowns | ux-designer | — | — | Policy Scenarios / AI Agent / Reports → top-level on mobile |
| 4.4 | WIP | Add `<main role="main">` landmark + "skip to main content" anchor | ux-designer | — | partial: [#22](https://github.com/LinusConradM/feeding_america/pull/22) (Exec Overview + Geographic Intelligence only) | Basic landmark a11y. **Partial credit landed in PR #22:** `role="banner"` on Exec Overview + Geographic Intelligence headers, `role="region"` on the state summary card, `aria-label` on the trend-explainer toggle button. Still missing: site-wide `<main>` landmark and the skip-link anchor (the actual task scope). |
| 4.5 | TODO | Drill-through links: each KPI + bento card links to relevant analytics page | ux-designer + software-engineer | 2.1 | — | KPIs are currently dead-ended |
| 4.6 | TODO | Rewrite bento card titles in question-led copy ("Ask in plain English", not "Autonomous Agentic Reasoning") | stakeholder-advocate | — | — | |
| 4.7 | TODO | Reframe footer: drop "DATA-613 Practicum" framing | stakeholder-advocate | — | — | Replace with "Independent research, methodology peer-reviewed at American University." |
| 4.8 | TODO | Fix typos: "U.S Food Insecurity" → "U.S. Food Insecurity"; full audit | stakeholder-advocate | — | — | |

### Phase 4 acceptance criteria

- `stakeholder-advocate` audience-fit test returns "serves" for all three audiences.
- All three audiences reach their primary task in <3 clicks (verified by ux-designer skill review).
- All touch targets ≥44×44px on mobile (verified by `test_home_responsive.py`).
- Every typo flagged in the review is fixed.

---

## Phase 5 — Test Backfill

Goal: every home-page concern has a test. **Runs throughout, days 1–end. Each Phase 1–4 fix lands with its corresponding test.**

| ID | Status | Test File | Asserts | Pairs With | PR | Notes |
|----|--------|-----------|---------|------------|-----|-------|
| T1 | DONE | `tests/test_home_kpi_values.py` | KPI cards data-derived; year stamps present; source citations present; computed values match reference data | 1.2, 2.1 | [#14](https://github.com/LinusConradM/feeding_america/pull/14) `51072dd` | Merged 2026-05-19. Reference values from latest year of `load_data()`. |
| T2 | DONE | `tests/test_home_fi_ticker.py` | Ticker uses weighted rate; handles NaN years; has 2011-2012 caveat; renders ≥10 entries | 1.1, 2.2 | [#14](https://github.com/LinusConradM/feeding_america/pull/14) `5c55c40` | Merged 2026-05-19. Full HTML-render assertion deferred to 2.2 when ticker is extracted to its own module. |
| T3 | DONE | `tests/test_home_anchors.py` | Every internal `href="#..."` matches an existing `id` in rendered HTML | 1.3 | [#14](https://github.com/LinusConradM/feeding_america/pull/14) `1b1177a` | Merged 2026-05-19. Catches future dead-anchor regressions. |
| T4 | DONE | `tests/test_home_caching.py` | Decorator presence on `_load_template`, `_load_css`, `_get_fi_ticker_html`, `_load_and_encode_image` | 1.4 | [#14](https://github.com/LinusConradM/feeding_america/pull/14) `ee3506c` + hotfix [#18](https://github.com/LinusConradM/feeding_america/pull/18) `22eb4a1` | Merged 2026-05-19. Also covers `_get_kpi_html` and lints `# OPTIMIZATION` comment claims. **Hotfix #18** deleted 7 redundant call-site `# OPTIMIZATION: ... is cached` comments that triggered false positives once T4 finally ran (T4 had been blocked by the missing-import bug in 1.1). T2 also had a hard-coded `0.05149` expected value that should have been `0.05075` — fixed in #18. |
| T5 | TODO | `tests/test_home_responsive.py` | Hypothesis property test: at 375/768/1024/1440 widths, KPI columns and chart heights match `ChartConfig.from_viewport` | 4.3 | — | Touch target 44×44px assertion included |
| T6 | TODO | `tests/test_home_a11y.py` | `<main>` landmark present; skip-link present; no focusable element without `:focus-visible`; every `<img>` has alt | 3.4, 4.4 | — | Basic landmark/focus a11y, not full WCAG |
| T7 | TODO | `tests/test_home_design_system.py` | No hex literals in `home.py` outside theme; no spacing values outside 4px grid in `home.css` | 3.1, 3.3 | — | Static analysis of source files |
| T8 | TODO | CI bootstrap: GitHub Actions workflow that runs `pytest tests/` on every PR + push to `main` | devops-engineer | — | — | **Added 2026-05-19** after PR #14 merged with a broken import (PR #18 hotfix). Local tests had never run successfully because of the same bug. CI would have caught it immediately. Highest-leverage missing piece in the workflow. |

### Phase 5 acceptance criteria

- `pytest tests/test_home*.py` passes.
- Coverage on home-page surfaces (`home.py`, `home.css`, helpers) ≥80%.
- Tests run before every PR merge (pre-CI: manual; post-CI: automated).

---

## Phase 6 — Backlog (Post-Ship)

Goal: nits and polish. None of these block the redesign.

| ID | Status | Task | Owner | PR | Notes |
|----|--------|------|-------|-----|-------|
| 6.1 | TODO | Card body line-heights, ticker font-size, marquee/ticker animation tempo harmonization | ui-designer | — | |
| 6.2 | TODO | Remove dead `.hero` rule at `home.css:872` (line 650 is overridden) | ui-designer | — | |
| 6.3 | TODO | Trailing newline at EOF; extract marquee triple constant | software-engineer | — | |
| 6.4 | TODO | Copy nits: "Investigating" → "Tracking"; "Density Joyplots" → "Where is need highest?"; etc. | stakeholder-advocate | — | |
| 6.5 | TODO | Update [README.md](../README.md): page count (9 → 12); directory ref (`pages/` → `views/`); reflect new home design | doc-updater | — | |

---

## Phase DS — Insight Panels (added 2026-05-18)

Goal: data-science-flavored panels that surfaced in the Phase 2 work but weren't in the original review. Tracked separately so they don't get conflated with Phase 2's data-plumbing fixes. All landed pre-emptively on `phase-2` in commit `2490ae6` (was `b5a3957` pre-hotfix rebase); they close to `DONE` when that branch merges.

| ID | Status | Task | Owner | Deps | PR | Notes |
|----|--------|------|-------|------|-----|-------|
| DS-2 | DONE | Child FI rate overlay on national trend chart (dashed line) | data-scientist | 2.1 | [#22](https://github.com/LinusConradM/feeding_america/pull/22) `58dd277` | Merged 2026-05-19 on Exec Overview. Consider porting to home page in a future commit. |
| DS-3 | DONE | ±1 std dev confidence band on national trend chart | data-scientist | 2.1 | [#22](https://github.com/LinusConradM/feeding_america/pull/22) `58dd277` | Merged 2026-05-19 on Exec Overview. Computed per-year std on `overall_food_insecurity_rate`. |
| DS-5 | DONE | Disparity Snapshot: Gini, Rural-Urban gap, Black-White FI gap | data-scientist + stakeholder-advocate | 2.1 | [#22](https://github.com/LinusConradM/feeding_america/pull/22) `58dd277` | Merged 2026-05-19. Racial-gap card gated on >50 obs per group (post-2019 data). **Open follow-up:** maintainer to verify the >50-obs threshold matches their statistical-significance bar. |
| DS-6 | DONE | Distribution histogram in Statistical Details, colored by `fi_category`, with weighted-avg reference line | data-scientist | 2.1 | [#22](https://github.com/LinusConradM/feeding_america/pull/22) `58dd277` | Merged 2026-05-19. Lazy-imports `plotly.express` inside `render_statistical_details`. |
| DS-7 | DONE | Policy event annotations on national trend chart (Hunger-Free Kids Act 2010, ACA 2014, CTC 2021, SNAP Emergency End 2023) | stakeholder-advocate | — | [#22](https://github.com/LinusConradM/feeding_america/pull/22) `58dd277` | Merged 2026-05-19. **Open follow-up:** maintainer to verify the four chosen policy events match the narrative they want to tell. |
| DS-8 | DONE | Counties in Crisis callout: Very High / High / Below 15% counts + worst-5 county list for selected year | data-analyst | — | [#22](https://github.com/LinusConradM/feeding_america/pull/22) `58dd277` | Merged 2026-05-19. Uses `fi_category` column. **Open follow-up:** confirm crisis tier thresholds (currently "Very High" = >20%, "High" = 15-20%) with the data-scientist. |

### Phase DS acceptance criteria

- Each panel has a unit/property test or is explicitly waived.
- Maintainer signs off on the DS-5 gating threshold, DS-7 event list, and DS-8 tier thresholds.
- The lazy `plotly.express` import in DS-6 doesn't reintroduce the unused top-level import.

---

## Maintainer Questions (Decisions Memo)

> Resolve in `Project Documents/HOME_REDESIGN_DECISIONS.md`. These gate Phase 0+ work.

| ID | Status | Question | Gates |
|----|--------|----------|-------|
| Q1 | DONE | What is the `app.py:84-92` `exec()` block? Did you write it? | All work (security) — resolved 2026-05-14, see [HOME_REDESIGN_DECISIONS.md](HOME_REDESIGN_DECISIONS.md#q1) |
| Q2 | DONE | Where does the 44.2M figure originate? USDA HFSSM headline, or stale MMG number? | 1.2 — resolved 2026-05-14, origin unknown, compute fresh from `load_data()` |
| Q3 | DONE | Is the home page intended to *match* the in-app McKinsey design system, or is the dark-indigo "marketing surface" intentional? | 3.1, 3.2 — resolved 2026-05-14, **McKinsey removed across whole app** (Phase 3 scope expanded) |
| Q4 | DONE | Is `views/templates/gallery.html` deprecated or staged for return? | 1.3 — resolved 2026-05-14, **delete it** |
| Q5 | DONE | Was commit `3854167` ("Remove aggressive caching") intentional? | 1.4 — resolved 2026-05-14, **accidental, restore decorators** |
| Q6 | DONE | Is the home page primarily for *onboarding* (in-app) or *marketing* (acquisition)? | 4.1, 4.2 — resolved 2026-05-14, **onboarding (introduce the app)** |
| Q7 | DONE | Audience priority order — Policymakers > Nonprofits > Researchers, or different? | 4.1 — resolved 2026-05-14, **no ranking, equal weight** |

---

## Definition of Done (whole redesign)

The home page redesign ships when **all** of the following are true:

- [ ] No `exec()` of unknown origin in `app.py`
- [ ] Every visible number is data-derived, year-stamped, and source-cited
- [ ] FI ticker uses population-weighted national rate
- [ ] All four KPI cards reach a relevant analytics page on click
- [ ] Primary CTA scrolls to a real anchor
- [ ] Hero subhead routes to the right page per audience in one click
- [ ] Mobile touch targets all ≥44×44px
- [ ] Zero hex literals in `home.py`/`home.css` outside `theme.py`
- [ ] All cache decorators present (or their absence documented)
- [ ] `pytest tests/test_home*.py` passes with ≥80% coverage on home-page surfaces
- [ ] `project-reviewer` skill audit returns APPROVE
- [ ] `stakeholder-advocate` audience-fit test returns "serves" for all three audiences
- [ ] Page load (cold cache) <2s on desktop, <4s on mobile
- [ ] All P0 + P1 tasks `DONE`
- [ ] Phase 6 backlog reviewed; either resolved or formally `DEFERRED` with reason

---

## Risk Register

| Risk | Likelihood | Mitigation | Status |
|------|-----------|------------|--------|
| `exec()` block is malicious — incident response expands scope | Low–Medium | Triage in 0.1; if confirmed, pause non-security work | Open |
| Maintainer says "dark indigo home is intentional" → Phase 3 changes character | Medium | Q3 settles before Phase 3 starts | Open |
| Removing templates breaks something not visible in `home.py` | Medium | `grep -r "<template_name>"` before any deletion | Open |
| Component migration regresses mobile (Feb 2026 mobile work was hard-won) | High | Snapshot tests at 375/768/1024 before & after; visual diff every PR | Open |
| Sole-maintainer burnout on a 3-week redesign | High | Phase the work; ship Phase 1 quickly for a momentum win; consider hybrid landing-page approach if Phase 3 drags | Open |
| New dev team onboarded mid-redesign and can't catch up | Medium | Each PR ≤300 LOC; descriptive commits; lane-tagged. Onboarding report covers context | Open |

---

## Change Log

| Date | Editor | Change |
|------|--------|--------|
| 2026-05-05 | Claude | Initial creation of tracker (43 tasks, 7 maintainer questions) |

---

## Appendix — Cross-Reference to Source Review

| Tracker ID | Review Fix # | Severity in review |
|------------|--------------|---------------------|
| 0.1 | Review Q1 + QA Blocker (`exec()` block) | Blocker |
| 1.1 | P0 #2 (FI ticker unweighted) | Blocker |
| 1.2 | P0 #3 (44.2M figure) | Blocker |
| 1.3 | P0 #4 (dead CTA) | Blocker |
| 1.4 | P0 #5 (caching regression) | Blocker |
| 2.1 | P1 #6 (KPIs hard-coded) | High |
| 2.2 | P1 #12 (duplicated ticker) | High |
| 2.3 | P1 #11 (broken JS selector) | High |
| 2.4 | P1 #13 (silent image errors) | High |
| 2.5 | P1 #14 (no MMG disclaimer) | High |
| 2.6 | P1 #15 (filename with space) | High |
| 3.1 | P1 #8 (parallel palette) | Blocker |
| 3.2 | P1 #7 (no component reuse) | High |
| 3.3 | P2 #18 (off-grid spacing) | Medium |
| 3.4 | P2 #16 (focus-visible / reduced-motion) | Medium |
| 4.1 | P1 #9a (hero misframes audience) | Blocker (Stakeholder) |
| 4.2 | P1 #9b (vanity KPIs / decoration) | Blocker (Stakeholder) |
| 4.3 | P1 #10 (mobile nav broken) | High |
| 4.4 | P2 #17 (no main landmark) | Medium |
| 4.5 | P2 #22 (no drill-through) | Medium |
| 4.6 | P2 #21 (jargon card titles) | Medium |
| 4.7 | P2 #23 (DATA-613 framing) | Medium |
| 4.8 | P2 #24 (typo) | Medium |
| T1–T7 | All test backfill | n/a |
| 6.1–6.5 | P3 backlog | Low |
