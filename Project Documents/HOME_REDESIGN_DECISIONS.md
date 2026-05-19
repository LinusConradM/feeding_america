# Home Redesign — Maintainer Decisions Memo

> Companion to [HOME_REDESIGN_TASK_TRACKER.md](HOME_REDESIGN_TASK_TRACKER.md). The seven questions below gate Phase 0+ work. Fill in **Decision** for each; the answer changes what tasks 1.x–4.x actually do.

**Maintainer:** Conrad Linus Muhirwe
**Started:** 2026-05-11
**Last updated:** 2026-05-14

---

## Q1 — The `exec()` block in `app.py`

**Status:** ✅ **RESOLVED 2026-05-14**

**Question:** What is the `app.py:84-92` `exec()` block? Did you write it?

**Decision:** Not author-authored. Confirmed hostile — multi-stage malware loader (Solana-memo C2 → Node.js stager → encrypted JS stealer), consistent with the *Contagious Interview / DEV#POPPER* campaign pattern. Provenance of the injection (commit `962a2cd` authored 2026-03-03 under maintainer credentials) is unconfirmed.

**Actions taken:**
- Payload stripped on `main` via PR #13 (commit `abe5396`).
- Full disclosure published at [SECURITY.md](../SECURITY.md).
- Local-host IoC scan on primary Mac came back clean (no `~/init.json`, no `~/node-v22.9.0-*`, no `i.js`).
- shinyapps.io deployment taken offline.
- Affected API keys rotated.
- Other-machine / shared-clone exposure: confirmed by maintainer but specifics not yet captured in this memo. **TODO:** add detail (which machine, who else cloned).

**Gated work:** All of Phase 0+ in the task tracker. ✅ Unblocked.

---

## Q2 — Origin of the "44.2 million" KPI

**Status:** ✅ **RESOLVED 2026-05-14**

**Question:** Where does the 44.2M figure on the home page originate? USDA HFSSM headline, or a stale MMG number?

**Decision:** Origin **unknown** to maintainer. Treat as untrusted.

**Implication for Phase 1:** Default to the safe path — compute the KPI fresh from `load_data()` at render time, label it with its year and source citation ("Feeding America, MMG, [year]"). Do not preserve the 44.2M number. Update [README.md:12](../README.md) to match the freshly-computed value.

**Gates:** Task 1.2 (KPI #1 fix). Soft-gates 2.1 (data-derived KPI helper). ✅ Unblocked.

---

## Q3 — Home page design surface

**Status:** ✅ **RESOLVED 2026-05-14** (with scope expansion — see below)

**Question:** Is the home page intended to *match* the in-app McKinsey design system, or is the dark-indigo "marketing surface" intentional?

**Decision:** **Remove McKinsey design system across the whole app.** The audit assumed Phase 3 would either (a) make the home match the in-app McKinsey tokens, or (b) leave the home's marketing surface intentional. The maintainer's answer is broader: McKinsey goes away everywhere.

**Scope impact:**
- Phase 3 (originally 4 tasks scoped at home only) now spans every page that imports from `utils/theme.py` — Executive Overview, Geographic Intelligence, Correlation Analysis, Regression Models, Equity Disparities, County Clustering, Time Series Explorer, Policy Scenarios, Data Downloads, AI Data Analyst, Anomaly Detection.
- `utils/theme.py` becomes the central artifact to replace, not just to import from.
- The `ui-designer` skill (`.claude/skills/ui-designer/SKILL.md`) currently lists "Apply the McKinsey design tokens" as its trigger — it will need rewriting once the new design direction is chosen.

**New open sub-question (defer until Phase 3 planning):** What replaces McKinsey? Options to weigh later — extend the home's dark-indigo across the app, pick a new palette, or stay token-based with a different brand. Not needed to unblock Phase 1.

**Gates:** Tasks 3.1, 3.2 (palette + component migration). ✅ Unblocked but expanded.

---

## Q4 — `views/templates/gallery.html`

**Status:** ✅ **RESOLVED 2026-05-14**

**Question:** Is `views/templates/gallery.html` deprecated or staged for return?

**Decision:** **Delete it.** Gallery is deprecated.

**Implication for Phase 1:**
- Task 1.3 (dead CTA fix): delete `views/templates/gallery.html`, repoint the home page's primary CTA to a non-gallery surface (likely a Phase 4 audience-routed CTA), and remove any `href="#gallery"` references.
- Audit the `images/` and `assets/` folders for files only referenced by the gallery and remove those too.

**Gates:** Task 1.3 (dead CTA fix). ✅ Unblocked.

---

## Q5 — Commit `3854167` ("Remove aggressive caching")

**Status:** ✅ **RESOLVED 2026-05-14**

**Question:** Was commit [`3854167`](https://github.com/LinusConradM/feeding_america/commit/3854167) intentional?

**Decision:** **Accidental.** Restore the decorators.

**Implication for Phase 1:**
- Task 1.4: restore `@st.cache_data` on `_load_template` and `_load_css` in `views/home.py`. Keep the existing `# OPTIMIZATION` comments — they will now be truthful again.
- Land with test T4 (`tests/test_home_caching.py`) which asserts decorator presence to prevent silent re-strips.

**Gates:** Task 1.4 (caching truth). ✅ Unblocked.

---

## Q6 — Home page's primary purpose

**Status:** ✅ **RESOLVED 2026-05-14**

**Question:** Is the home page primarily for **onboarding** (in-app — users have already found you, the page orients them to the analytics) or **marketing** (acquisition — users land here cold and need to be convinced to engage)?

**Decision:** **Introducing the app.** Visitors who reach the home page have arrived; the page's job is to explain what the app does and route them to the right analytics surface. This is onboarding-leaning, not acquisition.

**Implication for Phase 4:**
- Lean toward compact orientation + drill-through links over hero-heavy storytelling and social proof.
- KPIs on the home should be *insight numbers* that tease analytics (e.g., national FI rate, counties >20%, YoY change) — not marketing-funnel decoration.
- Audience-routed CTAs (Phase 4.1) should each lead to a specific analytics surface; no separate "learn more about the project" landing.
- Footer reframe (task 4.7) should keep it factual (research origin + methodology) rather than marketing copy.

**Gates:** Tasks 4.1, 4.2 (hero rewrite, KPI selection). ✅ Unblocked.

---

## Q7 — Audience priority order

**Status:** ✅ **RESOLVED 2026-05-14**

**Question:** What's the priority order of the three audiences — policymakers, nonprofits, researchers — or is the order different from what the audit assumed?

**Decision:** **No ranking.** All three audiences are equal-weight. The hero's three CTAs should be presented with equal visual treatment (no primary/secondary/tertiary hierarchy).

**Implication for Phase 4:**
- Task 4.1 (hero rewrite): three CTAs side-by-side with matched visual weight (same size, same color treatment, same prominence). Not a "primary CTA + two secondaries" pattern.
- Reading order across the row is left-to-right; pick an order that reads cleanly but don't optimize one over the others. Default left-to-right: policymakers → nonprofits → researchers, but interchangeable.
- Each CTA still gets its own deep link: policymakers → Policy Scenarios, nonprofits → Geographic Intelligence, researchers → Regression Models + Data Downloads.
- Drill-through from each KPI card (task 4.5) should likewise serve all three audiences without favoring one.

**Gates:** Task 4.1 (hero rewrite). ✅ Unblocked.

---

## How to use this memo

1. Resolve each `TODO` to `RESOLVED` by filling in **Decision** and any **Actions taken**.
2. Update the corresponding row's **Status** in [HOME_REDESIGN_TASK_TRACKER.md](HOME_REDESIGN_TASK_TRACKER.md) → Maintainer Questions table.
3. When all seven are resolved, Phase 0 acceptance criteria are met and Phase 1 unblocks.

Short answers are fine — these are decisions, not essays. The goal is to record *what* was decided and *why* so future-you (and future Claude sessions) don't have to re-derive context.
