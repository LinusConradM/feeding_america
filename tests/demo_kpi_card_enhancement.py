"""
Demo script to visually test the enhanced kpi_card component with tooltip integration.

This demo shows:
1. KPI card without tooltip (backward compatibility)
2. KPI card with tooltip (new feature)
3. Multiple KPI cards with different tooltips

Run with: streamlit run demo_kpi_card_enhancement.py
"""

import streamlit as st
from utils.components import kpi_card

st.set_page_config(page_title="KPI Card Enhancement Demo", layout="wide")

st.title("🎯 KPI Card Enhancement Demo")
st.markdown("---")

st.header("1. KPI Card Without Tooltip (Backward Compatibility)")
st.markdown("This demonstrates that existing code continues to work without changes.")

col1, col2, col3 = st.columns(3)

with col1:
    kpi_card(
        title="National FI Rate",
        value="13.2%",
        change="+0.8%",
        icon="users",
        gradient="sapphire"
    )

with col2:
    kpi_card(
        title="Food Insecure Persons",
        value="42.5M",
        change="+2.1M",
        icon="user-friends",
        gradient="emerald"
    )

with col3:
    kpi_card(
        title="Cost Per Meal",
        value="$3.42",
        change="-$0.05",
        icon="dollar-sign",
        gradient="amber"
    )

st.markdown("---")

st.header("2. KPI Card With Tooltip (New Feature)")
st.markdown("Hover over the cards on desktop or tap the info icon on mobile to see contextual help.")

col1, col2, col3 = st.columns(3)

with col1:
    kpi_card(
        title="National FI Rate",
        value="13.2%",
        change="+0.8%",
        icon="users",
        gradient="sapphire",
        tooltip_text="The percentage of households in the United States experiencing food insecurity, meaning they lack consistent access to adequate food."
    )

with col2:
    kpi_card(
        title="Food Insecure Persons",
        value="42.5M",
        change="+2.1M",
        icon="user-friends",
        gradient="emerald",
        tooltip_text="The total number of individuals living in food-insecure households across the nation."
    )

with col3:
    kpi_card(
        title="Cost Per Meal",
        value="$3.42",
        change="-$0.05",
        icon="dollar-sign",
        gradient="amber",
        tooltip_text="The average cost to provide a nutritionally adequate meal, calculated based on USDA food price data."
    )

st.markdown("---")

st.header("3. Economic Drivers with Tooltips")
st.markdown("Additional metrics with contextual help.")

col1, col2, col3, col4 = st.columns(4)

with col1:
    kpi_card(
        title="Poverty Rate",
        value="11.5%",
        change="+0.3%",
        icon="hand-holding-usd",
        gradient="rose",
        tooltip_text="The percentage of the population living below the federal poverty line, a key indicator of economic hardship."
    )

with col2:
    kpi_card(
        title="Median Income",
        value="$70,784",
        change="+$1,200",
        icon="money-bill-wave",
        gradient="violet",
        tooltip_text="The median household income in the United States, representing the middle point of income distribution."
    )

with col3:
    kpi_card(
        title="Unemployment",
        value="3.8%",
        change="-0.2%",
        icon="briefcase",
        gradient="cyan",
        tooltip_text="The percentage of the labor force that is unemployed and actively seeking employment."
    )

with col4:
    kpi_card(
        title="Budget Shortfall",
        value="$25.3B",
        change="+$2.1B",
        icon="chart-line",
        gradient="orange",
        tooltip_text="The estimated additional funding needed to close the food security gap and ensure all households have adequate access to food."
    )

st.markdown("---")

st.header("4. Accessibility Features")
st.markdown("""
The enhanced KPI card includes:
- ✅ **ARIA labels** for screen readers (role="article", aria-label with title and value)
- ✅ **aria-hidden="true"** on decorative icons
- ✅ **Keyboard navigation** support through tooltip_wrapper
- ✅ **44x44px touch targets** for mobile (info icon)
- ✅ **200ms hover delay** for desktop tooltips
- ✅ **Dismissible modal** for mobile tooltips
""")

st.markdown("---")

st.info("💡 **Tip**: Try resizing your browser window to see responsive behavior. On mobile viewports (<768px), the hover tooltip becomes a tappable info icon.")
