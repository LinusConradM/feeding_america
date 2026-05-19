# Project Context — GP Food Basket

> **Shared reference loaded by multiple skills. Do not duplicate this content into individual skill files — reference this file instead.**

## Project

**GP Food Basket** is a Streamlit dashboard analyzing U.S. county-level food insecurity from 2009-2023 across ~3,100 counties (~47K county-year observations). Data sources: Feeding America Map the Meal Gap + Census ACS. Audiences: policymakers, nonprofit practitioners, researchers.

## Architecture

```
app.py                          → Main router, data pre-warming
views/home.py                   → Landing page
views/0_Data_Explorer.py        → Raw data browser
views/1_Executive_Overview.py   → National KPIs
views/2_Geographic_Intelligence.py
views/3_Correlation_Analysis.py
views/4_Regression_Models.py
views/5_Equity_Disparities.py
views/6_County_Clustering.py
views/7_Time_Series_Explorer.py
views/8_Policy_Scenarios.py
views/9_Data_Downloads.py
views/10_AI_Data_Analyst.py
views/11_Anomaly_Detection.py
utils/theme.py                  → Design tokens (COLORS, PLOTLY_LAYOUT, page_header)
utils/components.py             → Reusable UI components
utils/data_loader.py            → Data pipeline, feature engineering
utils/responsive.py             → Viewport detection, ChartConfig
utils/navigation.py             → Global nav ribbon
utils/llm.py                    → LLM API (Gemini → Groq fallback)
data/*.xlsx                     → Cleaned datasets (never modify)
data_raw/                       → Raw source data (read-only)
tests/                          → pytest suite
```

## Design System (Editorial — light surfaces, serif headlines)

### Color Palette (`utils/theme.py` → `COLORS` dict)

| Token | Hex | Usage |
|-------|-----|-------|
| `ink` | #051C2C | Headings, nav background, primary dark |
| `sapphire` | #2251FF | Primary accent, CTAs, links, active states |
| `charcoal` | #2D3748 | Body text |
| `slate` | #4A5568 | Secondary text, axis labels |
| `steel` | #718096 | Muted text, borders |
| `silver` | #A0AEC0 | Disabled (never for body text — fails 4.5:1 contrast) |
| `pearl` | #E2E8F0 | Light borders, dividers |
| `snow` | #F7FAFC | Card tints, subtle backgrounds |
| `ruby` | #E63757 | Error, negative delta |
| `emerald` | #00AB6B | Success, positive delta |
| `amber` | #F5A623 | Warning |
| `amethyst` | #7C3AED | Tertiary accent (clustering, segmentation) |
| `topaz` | #FF6F3C | Highlight, secondary CTA |

**Plotly color sequence** (in `PLOTLY_LAYOUT`): `sapphire → ruby → emerald → amethyst → topaz → amber`.

### Typography

| Role | Family | Weight | Size |
|------|--------|--------|------|
| Page title | Georgia (serif) | 700 | 32-40px |
| Section header | Georgia | 600 | 24px |
| KPI value | Georgia | 700 | 32-40px |
| Body | Inter (sans) | 400 | 16px |
| KPI label | Inter | 600 uppercase | 11-13px, 0.08em letter-spacing |
| Chart label | Inter | 400 | 13px |
| Nav | Geist Mono | 500 | 13-14px |

Serif (Georgia) carries authority — reserve for titles and KPI numbers. Sans (Inter) for everything readable. Mono (Geist) only in nav.

### Spacing (4px base grid)

Allowed: `4 / 8 / 12 / 16 / 24 / 32 / 48 / 64` px. Never 5/7/13/18/22.

### Radius

Cards/banners: 8px. Buttons/badges: 6px. Pills/chips: 999px. Charts/maps: 4px.

### Shadow

Default: `box-shadow: 0 1px 3px rgba(5, 28, 44, 0.06), 0 1px 2px rgba(5, 28, 44, 0.04)`. Avoid heavier shadows.

### Borders

Default: `1px solid #E2E8F0` (`pearl`). Active/selected: `2px`. Accent bars: `3-4px solid sapphire`.

## Component Library (`utils/components.py`)

| Function | Usage |
|----------|-------|
| `kpi_card(label, value, accent, change, change_label)` | Single KPI, white bg, 3px sapphire top accent, optional delta badge |
| `kpi_row(cards, columns)` | Responsive 1-4 column KPI grid |
| `kpi_row_grouped(groups)` | Multi-section KPI block with subtitle |
| `section_header(title, subtitle, icon)` | Section divider with pearl bottom border |
| `info_banner(text, type)` | Callout — info/warning/error/success, 4px left border |
| `stat_card(label, value, color)` | Subtle tinted stat |
| `hero_section(title, subtitle)` | Gradient hero (ink → sapphire) |
| `quick_tips_callout(tips, dismissible)` | Scrolling tip strip |
| `empty_state(message, icon)` | No-data placeholder |
| `tooltip_wrapper(...)` | Hover-revealed help text |
| `collapsible_section(...)` | Lazy-loaded accordion |
| `metric_badge(label, value, color)` | Compact pill inside cards |
| `llm_explainer_ui(page, context)` | AI insight panel |
| `page_header(title, subtitle, icon)` (in `utils/theme.py`) | Page title with animated gradient bar |

**Always reuse these instead of writing custom HTML.**

## Responsive Breakpoints (`utils/responsive.py`)

| Breakpoint | Width | Layout |
|------------|-------|--------|
| Mobile | <768px | 1-2 col KPIs, 240-280px chart height, stacked |
| Tablet | 768-1024px | 2-3 col KPIs, 350px chart height |
| Desktop | >1024px | 3-4 col KPIs, 450px chart height |

Standard usage:
```python
from utils.responsive import get_viewport, ChartConfig
vp = get_viewport()
cfg = ChartConfig.from_viewport(vp)
# vp.is_mobile, vp.kpi_columns, cfg.chart_height, cfg.data_fraction
```

Mobile: 44×44px touch targets, ≥14px font, charts use `cfg.data_fraction` to reduce points.

## Data Access (`utils/data_loader.py`)

```python
from utils.data_loader import load_data, get_numeric_columns, get_variable_label
df = load_data()  # cleaned, feature-engineered, ~47K rows, cached
```

Never read Excel directly — always use `load_data()`. Never modify `data/*.xlsx`.

### Key Columns (snake_case throughout)

- **IDs:** `fips`, `county`, `state`, `year`
- **Headlines:** `food_insecurity_rate`, `food_insecure_persons`, `child_food_insecurity_rate`, `cost_per_meal`, `weighted_annual_food_budget_shortfall`
- **Demographics:** `median_household_income`, `poverty_rate`, `unemployment_rate`, `homeownership_rate`, `percent_african_american`, `percent_hispanic`, `percent_with_bachelor_degree_or_higher`
- **Race-specific FI rates:** `food_insecurity_rate_among_black_persons_all_ethnicities`, `food_insecurity_rate_among_hispanic_persons_any_race`, `food_insecurity_rate_among_white_non_hispanic_persons`
- **Engineered features:** `urban_rural` (Urban/Suburban/Small Town/Rural), `fi_category` (Low/Moderate/High/Very High), `poverty_category`, `income_category`, `education_category`

## Plotly Standard

```python
import plotly.express as px
from utils.theme import COLORS, PLOTLY_LAYOUT
from utils.responsive import get_viewport, ChartConfig
import streamlit as st

cfg = ChartConfig.from_viewport(get_viewport())
fig = px.scatter(df, x="poverty_rate", y="food_insecurity_rate")
fig.update_layout(**PLOTLY_LAYOUT, height=cfg.chart_height)
st.plotly_chart(fig, use_container_width=True)
```

Do NOT override `paper_bgcolor`, `plot_bgcolor`, or `font.family` — `PLOTLY_LAYOUT` sets them. Do NOT hard-code hex — use `COLORS["..."]`.

## Audiences

Three primary audiences:
1. **Policymakers** — 2-5 min visits, defensible numbers, screenshot-able charts.
2. **Nonprofit practitioners** — 5-15 min, county-level granularity, grant-ready exports.
3. **Researchers** — 30+ min, methodology transparency, raw data downloads.
