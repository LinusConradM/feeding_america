# GP Food Basket — Project Onboarding Report

**Document purpose:** Brief a new development team on what this project is, where it stands, and who it serves.
**Author:** Conrad Linus Muhirwe (sole author/maintainer)
**Last reviewed:** 2026-05-05 · current branch: `executive_overview`

---

## 1. At a Glance

| Field | Value |
|---|---|
| Project name | U.S. Food Insecurity Analytics Platform (internal: `gp-food-basket`) |
| Type | Interactive multi-page web dashboard |
| Stack | Python 3.11 · Streamlit · Plotly · pandas · scikit-learn · statsmodels · Gemini/Groq LLMs |
| Codebase size | ~7,700 LOC across `app.py` + 7 utility modules + 13 view pages |
| Repo activity | 463 commits total · ~30 commits in the last 90 days · active branch `executive_overview` |
| Test footprint | 34 pytest files (unit, integration, Hypothesis property-based) — run locally; no CI yet |
| Data scale | ~47,000 county-year observations · 3,100+ U.S. counties · 2009–2023 (15 years) |
| Origins | Started as DATA-613 practicum (American University, Fall 2025); migrated R Shiny → Python Streamlit in Feb 2026 |

---

## 2. Project Objectives

### 2.1 Primary mission

Make 15 years of U.S. county-level food insecurity data legible and actionable to the people whose decisions shape food access, without requiring them to be data scientists.

The platform unifies two normally siloed datasets (Feeding America's *Map the Meal Gap* and Census ACS demographics) into one interface that supports descriptive exploration, statistical analysis, and policy simulation.

### 2.2 Concrete objectives (in priority order)

1. **Surface county-level food insecurity** with enough granularity that a county commissioner, food bank director, or grant writer can find their own jurisdiction in fewer than three clicks.
2. **Quantify socioeconomic drivers** through correlation, regression (OLS / Ridge / LASSO / Elastic Net / Random Forest), and clustering, exposing which factors most strongly track with food insecurity, not just whether they do.
3. **Expose equity gaps** along racial, ethnic, urban-rural, and income lines so disparities are first-class citizens of the analysis, not buried in an appendix.
4. **Simulate policy interventions** (Policy Scenarios page) so funding decisions can be stress-tested before commitment, with cost estimates attached.
5. **Make the underlying data downloadable** in CSV / Excel / JSON so researchers can reproduce findings or extend analyses outside the dashboard.
6. **Lower the cognitive cost of insight** via an AI Data Analyst page (LLM-powered natural-language queries with Gemini 2.5 Flash → Groq fallback).

### 2.3 What the project deliberately is NOT

- **Not a data warehouse.** Data is loaded from two static Excel files; there is no ingestion pipeline, no live API, no incremental refresh.
- **Not a transactional system.** Read-only analytics; no user accounts, no submissions, no PII storage.
- **Not a forecasting tool (yet).** Current models are explanatory and policy-simulation, not predictive of future years.
- **Not an academic publication interface.** Methodology is transparent but the audience is decision-makers, not peer reviewers.

---

## 3. Architecture Snapshot

### 3.1 Layered structure

```
app.py                          # Entry point: data pre-warm + landing page
│
├── views/                      # 13 pages (1 landing + 12 analytics)
│   ├── home.py + home.css      # Landing
│   ├── 0_Data_Explorer.py      # Raw data browser
│   ├── 1_Executive_Overview.py # National KPIs, rankings (892 LOC, largest page)
│   ├── 2_Geographic_Intelligence.py
│   ├── 3_Correlation_Analysis.py
│   ├── 4_Regression_Models.py  # 5 model families
│   ├── 5_Equity_Disparities.py
│   ├── 6_County_Clustering.py  # K-means + PCA
│   ├── 7_Time_Series_Explorer.py
│   ├── 8_Policy_Scenarios.py   # Intervention simulation
│   ├── 9_Data_Downloads.py
│   ├── 10_AI_Data_Analyst.py   # LLM-powered NL queries
│   └── 11_Anomaly_Detection.py # Isolation Forest + z-score
│
├── utils/                      # Shared modules (~2,800 LOC)
│   ├── theme.py                # McKinsey design tokens, single source of truth
│   ├── components.py           # 20+ reusable UI components (1,523 LOC)
│   ├── data_loader.py          # Cached pipeline + feature engineering
│   ├── responsive.py           # Viewport detection, ChartConfig
│   ├── navigation.py + nav.css # Global ribbon nav
│   └── llm.py                  # Gemini → Groq → static fallback chain
│
├── data/                       # 2 Excel files, 10.7 MB total
├── tests/                      # 34 pytest files
├── .claude/skills/             # 13 project-scoped agent skills
└── .streamlit/config.toml      # Theme + server config
```

### 3.2 Design system

McKinsey-inspired editorial aesthetic: Georgia serif for headlines and KPI values, Inter sans for body, navy `#051C2C` + sapphire `#2251FF` as primary palette, 4px-grid spacing, subtle shadows. All tokens centralized in `utils/theme.py`; all reusable UI in `utils/components.py`.

### 3.3 Data pipeline

```
data/feeding_america(2009-2018).xlsx ─┐
                                       ├─→ load_data() (@st.cache_data)
data/feeding_america(2019-2023).xlsx ─┘     │
                                             ├─→ Feature engineering:
                                             │    • urban_rural bins
                                             │    • fi_category bins
                                             │    • poverty/income/edu categories
                                             │    • FIPS → state abbreviation map
                                             │
                                             └─→ ~47K rows, ready for views/
```

**Quirks worth knowing:** post-2019 raw data uses numeric FIPS codes for state (mapped on load); raw Excel ships with duplicate columns (deduplicated on load); race columns use long names (`food_insecurity_rate_among_black_persons_all_ethnicities`).

### 3.4 LLM integration

Chain: Gemini 2.5 Flash (primary) → Groq Llama-3.3-70b (fallback) → static text (degraded mode). Reads keys from `st.secrets` or `.env`. Used by the AI Data Analyst page and the `llm_explainer_ui()` component embedded across analytics pages.

---

## 4. Development Status

### 4.1 What's working ("production-ready" per README v2.0.0)

| Capability | Status |
|---|---|
| 13 pages render and respond to filters | OK |
| 5 regression model families (OLS, Ridge, LASSO, Elastic Net, RF) | OK |
| K-means clustering with silhouette scoring + PCA viz | OK |
| Choropleth maps with state drill-down | OK |
| LLM-powered AI Data Analyst (Gemini → Groq fallback) | OK |
| Anomaly detection (Isolation Forest + z-score) | OK |
| Data export (CSV / Excel / JSON) | OK |
| Mobile responsive (after extensive Feb 2026 mobile nav work) | OK |
| McKinsey design system applied across all pages | OK |
| Local pytest suite (unit + integration + property-based) | OK |

### 4.2 Recent active work (last 90 days)

Reading the commit log, three workstreams dominate Q1 2026:

1. **Mobile navigation overhaul** (Feb 22–26): two weeks of CSS/JS work to fix iOS Safari iframe touch bugs in the dropdown menu, settled on a pure-CSS Checkbox Hack pattern.
2. **Performance optimization** (Mar 3): home page load speed, image base64 caching, FI ticker TTL caching, pre-warming `load_data()` in `app.py`. Documented in `Project Documents/Home Page Performance Optimization.md`.
3. **Executive Overview redesign + global navigation ribbon** (Mar 3, Mar 20): hero banner refresh and persistent top nav across pages.

Three uncommitted local changes on the current branch (`executive_overview`):

- `utils/data_loader.py`
- `views/1_Executive_Overview.py`
- `views/2_Geographic_Intelligence.py`

### 4.3 Known gaps the new team should plan for

| Gap | Impact | Owner skill |
|---|---|---|
| **No CI/CD pipeline.** `.github/` exists but is empty; tests run only locally | High. Every PR is unverified until manually tested | `devops-engineer` |
| **No deployment configuration.** No Dockerfile, no Streamlit Cloud / Render / Railway config committed | High. No documented prod target | `devops-engineer` |
| **Dependencies pinned with `>=` only.** `requirements.txt` allows version drift | Medium. Non-reproducible builds | `devops-engineer` |
| **Legacy R-Shiny artifacts still in repo.** `index.html`, `old_scenarios.py`, `rsconnect/` directory | Low. Confusing for newcomers, ~70KB dead weight | `refactor-cleaner` agent |
| **README is partly out of date.** Claims 9 pages (there are 12), shows `pages/` directory (actually `views/`), states DATA-613 Fall 2025 (active dev continued into 2026) | Low. Onboarding friction | `doc-updater` agent |
| **`team-assembler` and `team-workflow` skills don't list 3 newest roles.** `data-analyst`, `ui-designer`, `stakeholder-advocate` were added today and the orchestrator skills haven't been updated | Medium. Orchestrators won't route work to new lanes | One-time edit |
| **No data refresh story.** Excel files are static; no plan for 2024 data | Medium (when 2024 data publishes) | `data-scientist` + `devops-engineer` |
| **Some commits with low-quality messages.** `bye`, `thhtht`, `hth`, `made the following changes…` | Low. Historical only | N/A |

### 4.4 Test coverage

34 test files in `tests/`, heavy on property-based tests (15+ `test_*_properties.py` files using Hypothesis), a deliberate choice to validate invariants like viewport breakpoints, touch target sizing, KPI rendering across edge cases. Patterns to follow are documented in `.claude/skills/qa-tester/SKILL.md`.

Coverage is well-distributed across UI components, responsive logic, and integration paths, but no end-to-end browser tests (Playwright/Selenium) and no formal coverage threshold is enforced.

### 4.5 Branch state

```
main                       ← stable
executive_overview (HEAD)  ← current dev branch, 3 uncommitted files
```

The new team should align on a branching model before merging anything. There is no `CONTRIBUTING.md` or branch-protection policy committed.

---

## 5. Key Target Users

The dashboard is built for three distinct audiences, each with different time budgets, vocabulary tolerance, and decisions to make. Every feature should map to at least one. Features that serve none should be cut. (This is codified in `.claude/skills/stakeholder-advocate/SKILL.md`.)

### 5.1 Policymakers — the primary audience

| Attribute | Detail |
|---|---|
| Who | Federal program officers, state legislators, county commissioners, congressional staff |
| Goal | Justify a funding allocation, write a brief, defend a position to a committee |
| Time on site | 2–5 minutes per visit |
| Reading level | High literacy, low jargon tolerance. "Statistical significance" is fine; "heteroskedasticity" is not |
| Trust signals they need | Source attribution, year stamp, methodology link, peer-geography comparison |
| Pain points | Numbers that change without explanation; charts without takeaways; findings buried below the fold |
| Pages built for them | Executive Overview · Geographic Intelligence · Equity & Disparities · Policy Scenarios |
| Success metric | Can they screenshot a defensible chart for a brief in <5 minutes? |

### 5.2 Nonprofit practitioners — the recurring users

| Attribute | Detail |
|---|---|
| Who | Food bank directors, community advocacy orgs, grant writers, social workers, board members |
| Goal | Identify where need is highest, where their service area lags, what to put in a grant application |
| Time on site | 5–15 minutes; often returning users tracking their own region |
| Reading level | Mixed. Some former social workers, some program managers, some board members |
| Trust signals | County-level granularity, year-over-year deltas, demographic breakdowns |
| Pain points | Aggregations that hide local variation; filters that don't include their county; exports that aren't grant-ready |
| Pages built for them | Geographic Intelligence · Equity & Disparities · Time Series Explorer · Data & Downloads · AI Data Analyst |
| Success metric | Can a county director find their county and YoY change in <3 clicks? |

### 5.3 Researchers — the deep-dive users

| Attribute | Detail |
|---|---|
| Who | Academics, think tank analysts, graduate students, public health researchers |
| Goal | Replicate a finding, source data for a paper, explore a hypothesis |
| Time on site | 30+ minutes; will go deep |
| Reading level | Highest. Full tolerance for technical detail |
| Trust signals | Methodology transparency, raw data download, reproducibility, citation block |
| Pain points | Black-box transformations; missing version stamps; can't export the slice currently filtered |
| Pages built for them | Correlation Analysis · Regression Models · County Clustering · Anomaly Detection · Data Explorer · Data & Downloads |
| Success metric | Can someone reproduce a finding in R or Python from the downloaded data? |

### 5.4 Audience-to-page map (one-glance reference)

| Page | Primary audience | Secondary |
|---|---|---|
| Home | All three (entry router) | — |
| Executive Overview | Policymakers | Nonprofits |
| Geographic Intelligence | Nonprofits | Policymakers |
| Correlation Analysis | Researchers | Analysts |
| Regression Models | Researchers | — |
| Equity & Disparities | Policymakers | Nonprofits |
| County Clustering | Researchers | Nonprofits |
| Time Series Explorer | All three | — |
| Policy Scenarios | Policymakers | — |
| Data & Downloads | Researchers | Nonprofits |
| AI Data Analyst | Nonprofits | All three |
| Anomaly Detection | Researchers | — |
| Data Explorer | Researchers | — |

---

## 6. Recommended First-Week Plan for the New Team

### Day 1 — Read & Run

- Clone, install (`pip install -r requirements.txt`), run (`streamlit run app.py`).
- Click through all 13 pages on desktop, then resize to mobile. Note anything that breaks.
- Read `README.md`, this report, and `.claude/skills/software-engineer/SKILL.md`.

### Day 2 — Walk the architecture

- Read `utils/theme.py`, `utils/components.py`, `utils/data_loader.py`, `utils/responsive.py` in that order. These define every convention.
- Read `views/1_Executive_Overview.py` end-to-end as the canonical page template.
- Run `pytest tests/ -v` and confirm green.

### Day 3 — Meet the skills system

- Read each `.claude/skills/*/SKILL.md` to understand the agent roles. Pay attention to lane tables in `data-analyst`/`data-scientist` and `ui-designer`/`ux-designer`. These prevent ambiguity about who owns what.

### Day 4–5 — Plug the highest-leverage gaps

- Stand up CI on GitHub Actions (lint + pytest). See `.claude/skills/devops-engineer/SKILL.md` for a ready template.
- Pin dependency versions in `requirements.txt`.
- Update `team-assembler` and `team-workflow` skills to include the three newest roles.
- Update `README.md` page count (9 → 12) and directory references (`pages/` → `views/`).

---

## 7. Glossary (terms that recur in code & docs)

| Term | Meaning |
|---|---|
| FIPS | Federal Information Processing Standards code, a 5-digit unique county identifier |
| MMG / Map the Meal Gap | Feeding America's annual county-level food insecurity dataset, the project's primary source |
| ACS | American Community Survey, Census 5-year demographic estimates, the secondary source |
| FI rate | Food insecurity rate, % of population food insecure in a given county-year |
| FI category | Engineered bin: Low (<10%), Moderate (10–15%), High (15–20%), Very High (>20%) |
| Cost per meal | Average meal cost in dollars (varies geographically) |
| Budget shortfall | Annual dollar gap between what food-insecure households need and what they have |
| Urban / Suburban / Small Town / Rural | Engineered bins from county population thresholds (>250K / 50–250K / 10–50K / <10K) |
| `PLOTLY_LAYOUT` | Project-wide Plotly template; spread into every chart via `fig.update_layout(**PLOTLY_LAYOUT)` |
| `ChartConfig` | Viewport-aware chart-sizing helper from `utils/responsive.py` |
| `kpi_card` / `kpi_row` | The dashboard's signature headline-metric component (white card, sapphire accent bar) |
| `llm_explainer_ui` | Reusable AI-insight panel that wraps the Gemini→Groq fallback chain |
