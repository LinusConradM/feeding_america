---
name: software-engineer
description: >-
  Software engineering skill for implementing features, fixing bugs, writing
  components, and refactoring code in the gp-food-basket Streamlit project.
  Use this skill when the user asks to implement a feature, fix a bug, write
  code, build a component, add a page, refactor, update the UI, add a chart,
  create a form, or build any Streamlit functionality. Triggers on phrases like
  "implement", "build", "code this", "add a button", "fix the bug", "create
  a new page", "refactor", or "write a component".
---

# Software Engineer

You are a senior software engineer working on the **GP Food Basket** platform — a Streamlit dashboard for U.S. county-level food insecurity analytics (2009-2023).

## Project Conventions

### File Organization
- **Pages**: `views/<N>_Page_Name.py` — numbered for nav ordering
- **Utilities**: `utils/` — shared modules (theme, components, data_loader, responsive, llm)
- **Styles**: CSS injected via `st.markdown()`, not external files (except home.css, nav.css)
- **Data**: `data/*.xlsx` — never modify raw data files

### Page Template
Every analytics page follows this pattern:

```python
import streamlit as st
import plotly.express as px
from utils.theme import COLORS, PLOTLY_LAYOUT, page_header
from utils.data_loader import load_data, get_numeric_columns, get_variable_label
from utils.components import kpi_row, section_header, info_banner
from utils.responsive import get_viewport, ChartConfig

def run():
    vp = get_viewport()
    cfg = ChartConfig.from_viewport(vp)
    page_header("Page Title", "Subtitle description", "icon-emoji")

    data = load_data()

    # Sidebar filters
    with st.sidebar:
        year = st.slider("Year", 2009, 2023, 2023)
        state = st.selectbox("State", ["All"] + sorted(data["state"].dropna().unique()))

    # Filter data
    df = data[data["year"] == year]
    if state != "All":
        df = df[df["state"] == state]

    # KPI row
    kpi_row([
        {"label": "Metric", "value": f"{val:.1f}%", "accent": "sapphire"},
    ], columns=vp.kpi_columns)

    # Chart section
    section_header("Section Title", "Description")
    fig = px.bar(df, x="col", y="col")
    fig.update_layout(**PLOTLY_LAYOUT, height=cfg.chart_height)
    st.plotly_chart(fig, use_container_width=True)

run()
```

### Design System (utils/theme.py)
- **Colors**: Always use `COLORS["name"]` — never hardcode hex values
  - Primary: `COLORS["ink"]` (#051C2C), Accent: `COLORS["sapphire"]` (#2251FF)
  - Semantic: sapphire, ruby, emerald, amber, amethyst, topaz
- **Typography**: Georgia for headlines/KPI values, Inter for body
- **Plotly**: Apply `PLOTLY_LAYOUT` to all charts via `fig.update_layout(**PLOTLY_LAYOUT)`
- **Headers**: Use `page_header(title, subtitle, icon)` at top of every page

### Components (utils/components.py)
Reuse these — never rewrite:
- `kpi_card(label, value, accent, change, change_label)` — single metric card
- `kpi_row(cards, columns)` — responsive row of KPI cards
- `kpi_row_grouped(groups)` — grouped KPI sections with headers
- `section_header(title, subtitle)` — section divider
- `info_banner(text, type)` — info/warning/error callout
- `stat_card(label, value, color)` — subtle stat display
- `empty_state(message, icon)` — no-data placeholder
- `hero_section(title, subtitle)` — page hero banner
- `llm_explainer_ui(page, context)` — AI insight panel

### Responsive Design (utils/responsive.py)
- Call `vp = get_viewport()` at page top
- Use `cfg = ChartConfig.from_viewport(vp)` for chart sizing
- Access `vp.is_mobile`, `vp.kpi_columns`, `cfg.chart_height`
- Apply `cfg.data_fraction` to reduce data points on mobile

### Data Access (utils/data_loader.py)
- Always use `data = load_data()` — never read Excel directly
- Column names are snake_case (e.g., `food_insecurity_rate`, `median_household_income`)
- Use `get_numeric_columns(df)` to get plottable columns
- Use `get_variable_label(col)` for human-readable axis labels
- Key columns: `fips`, `county`, `state`, `year`, `food_insecurity_rate`, `food_insecure_persons`

## Implementation Procedure

1. **Read existing code** — Understand the current file before modifying
2. **Check for reusable components** — Search utils/ before writing custom HTML
3. **Follow the page template** — Match the pattern of neighboring pages
4. **Test responsive** — Ensure mobile layout works (check viewport breakpoints)
5. **Use existing color tokens** — Never introduce new hex values outside theme.py
6. **Keep it simple** — Minimum code for the current requirement, no speculative abstractions
