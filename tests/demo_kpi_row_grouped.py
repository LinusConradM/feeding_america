"""
Demo script to verify kpi_row_grouped component implementation.
"""

import streamlit as st
from utils.components import kpi_row_grouped
from utils.responsive import get_viewport_profile

st.set_page_config(page_title="KPI Row Grouped Demo", layout="wide")

# Get viewport profile
viewport = get_viewport_profile()

st.title("KPI Row Grouped Component Demo")

st.write(f"**Viewport Info:** Width: {viewport.width}px, Breakpoint: {viewport.breakpoint_name}, Columns: {viewport.kpi_columns}")

# Define row groups
row_groups = [
    {
        "title": "Core Food Insecurity Metrics",
        "cards": [
            {
                "title": "National FI Rate",
                "value": "12.8%",
                "change": "+0.5%",
                "icon": "chart-line",
                "gradient": "sapphire"
            },
            {
                "title": "Food Insecure Persons",
                "value": "42.2M",
                "change": "+1.2M",
                "icon": "users",
                "gradient": "ruby"
            },
            {
                "title": "Child FI Rate",
                "value": "17.3%",
                "change": "+0.8%",
                "icon": "child",
                "gradient": "emerald"
            },
            {
                "title": "Cost Per Meal",
                "value": "$3.42",
                "change": "+$0.12",
                "icon": "dollar-sign",
                "gradient": "amber"
            }
        ]
    },
    {
        "title": "Economic Drivers",
        "cards": [
            {
                "title": "Poverty Rate",
                "value": "11.5%",
                "change": "-0.3%",
                "icon": "chart-bar",
                "gradient": "amethyst"
            },
            {
                "title": "Median Income",
                "value": "$70,784",
                "change": "+$2,100",
                "icon": "money-bill-wave",
                "gradient": "teal"
            },
            {
                "title": "Unemployment",
                "value": "3.7%",
                "change": "-0.2%",
                "icon": "briefcase",
                "gradient": "coral"
            },
            {
                "title": "Budget Shortfall",
                "value": "$8.4B",
                "change": "+$0.5B",
                "icon": "wallet",
                "gradient": "navy"
            }
        ]
    }
]

# Render the component
kpi_row_grouped(row_groups, viewport)

st.markdown("---")
st.write("### Expected Behavior:")
st.write(f"- **Desktop (>1024px):** 4 columns per row")
st.write(f"- **Tablet (768-1024px):** 2 columns per row")
st.write(f"- **Mobile (<768px):** 1 column per row")
st.write(f"- Row groupings maintained in all viewports")
st.write(f"- Row group headers displayed above each group")
