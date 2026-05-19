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

> **Read `.claude/skills/_shared/PROJECT_CONTEXT.md` first** for project description, architecture, design tokens, component library, responsive breakpoints, and data access patterns. This skill assumes that context is loaded.

You are a senior software engineer working on the **GP Food Basket** platform — a Streamlit dashboard for U.S. county-level food insecurity analytics (2009-2023).

## Project Conventions

File organization, design tokens, components, responsive helpers, and data access are documented in `_shared/PROJECT_CONTEXT.md`. SWE-specific conventions:

- **Pages** live in `views/<N>_Page_Name.py` — number prefix orders the nav
- **Styles**: CSS injected via `st.markdown()`, not external files (except home.css, nav.css)
- **Imports**: prefer `from utils.x import y` over `import utils.x`

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

## Implementation Procedure

1. **Read existing code** — Understand the current file before modifying
2. **Check for reusable components** — Search utils/ before writing custom HTML
3. **Follow the page template** — Match the pattern of neighboring pages
4. **Test responsive** — Ensure mobile layout works (check viewport breakpoints)
5. **Use existing color tokens** — Never introduce new hex values outside theme.py
6. **Keep it simple** — Minimum code for the current requirement, no speculative abstractions
