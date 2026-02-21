"""
Executive Overview - National KPIs, trends, regional comparisons.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils.theme import enforce_landscape_on_mobile, inject_tailwind, COLORS, PLOTLY_LAYOUT, SEQUENTIAL_COLORS, page_header
from utils.components import kpi_row, section_header, stat_card, llm_explainer_ui
from utils.data_loader import load_data, STATE_NAMES




data = load_data()

# Sidebar controls
with st.sidebar:
    st.markdown('<p class="text-white font-semibold text-sm mb-2">Filters</p>', unsafe_allow_html=True)
    selected_year = st.slider("Year", int(data["year"].min()), int(data["year"].max()),
                              int(data["year"].max()))

year_data = data[data["year"] == selected_year]
prev_data = data[data["year"] == selected_year - 1] if selected_year > data["year"].min() else None

enforce_landscape_on_mobile()
page_header("Executive Overview", f"National food insecurity snapshot for {selected_year}", "chart-bar")


# --- KPI CALCULATIONS ---
def safe_pct_change(current, previous):
    if previous is None or previous == 0 or pd.isna(current) or pd.isna(previous):
        return ""
    change = ((current - previous) / previous) * 100
    sign = "+" if change > 0 else ""
    return f"{sign}{change:.1f}%"


fi_rate = year_data["overall_food_insecurity_rate"].mean()
fi_persons = year_data["no_of_food_insecure_persons_overall"].sum()
child_fi = year_data["child_food_insecurity_rate"].mean()
cost_meal = year_data["cost_per_meal"].mean()
poverty = year_data["poverty_rate"].mean()
med_income = year_data["median_income"].median()
unemp = year_data["unemployment_rate"].mean()
shortfall = year_data["weighted_annual_food_budget_shortfall"].mean()

prev_fi = prev_data["overall_food_insecurity_rate"].mean() if prev_data is not None else None
prev_persons = prev_data["no_of_food_insecure_persons_overall"].sum() if prev_data is not None else None
prev_child = prev_data["child_food_insecurity_rate"].mean() if prev_data is not None else None
prev_cost = prev_data["cost_per_meal"].mean() if prev_data is not None else None
prev_poverty = prev_data["poverty_rate"].mean() if prev_data is not None else None
prev_med_income = prev_data["median_income"].median() if prev_data is not None else None
prev_unemp = prev_data["unemployment_rate"].mean() if prev_data is not None else None
prev_shortfall = prev_data["weighted_annual_food_budget_shortfall"].mean() if prev_data is not None else None

kpi_row([
    {"title": "National FI Rate", "value": f"{fi_rate:.1%}" if pd.notna(fi_rate) else "N/A", "change": safe_pct_change(fi_rate, prev_fi), "icon": "utensils", "gradient": "coral"},
    {"title": "Food Insecure Persons", "value": f"{fi_persons/1e6:.1f}M" if pd.notna(fi_persons) else "N/A", "change": safe_pct_change(fi_persons, prev_persons), "icon": "users", "gradient": "navy"},
    {"title": "Child FI Rate", "value": f"{child_fi:.1%}" if pd.notna(child_fi) else "N/A", "change": safe_pct_change(child_fi, prev_child), "icon": "child", "gradient": "plum"},
    {"title": "Cost Per Meal", "value": f"${cost_meal:.2f}" if pd.notna(cost_meal) else "N/A", "change": safe_pct_change(cost_meal, prev_cost), "icon": "dollar-sign", "gradient": "amber"},
    {"title": "Poverty Rate", "value": f"{poverty:.1%}" if pd.notna(poverty) else "N/A", "change": safe_pct_change(poverty, prev_poverty), "icon": "hand-holding-usd", "gradient": "sapphire"},
    {"title": "Median Income", "value": f"${med_income:,.0f}" if pd.notna(med_income) else "N/A", "change": safe_pct_change(med_income, prev_med_income), "icon": "wallet", "gradient": "emerald"},
    {"title": "Unemployment", "value": f"{unemp:.1%}" if pd.notna(unemp) else "N/A", "change": safe_pct_change(unemp, prev_unemp), "icon": "briefcase", "gradient": "coral"},
    {"title": "Budget Shortfall", "value": f"${shortfall:,.0f}" if pd.notna(shortfall) else "N/A", "change": safe_pct_change(shortfall, prev_shortfall), "icon": "exclamation-triangle", "gradient": "navy"},
])

st.markdown("<div class='h-6'></div>", unsafe_allow_html=True)

# LLM Insight Engine
context_dict = {
    "Year": selected_year,
    "National FI Rate": f"{fi_rate:.1%}" if pd.notna(fi_rate) else "N/A",
    "Food Insecure Persons": f"{fi_persons/1e6:.1f}M" if pd.notna(fi_persons) else "N/A",
    "Child FI Rate": f"{child_fi:.1%}" if pd.notna(child_fi) else "N/A",
    "Cost Per Meal": f"${cost_meal:.2f}" if pd.notna(cost_meal) else "N/A",
    "Poverty Rate": f"{poverty:.1%}" if pd.notna(poverty) else "N/A",
    "Median Income": f"${med_income:,.0f}" if pd.notna(med_income) else "N/A",
    "Unemployment": f"{unemp:.1%}" if pd.notna(unemp) else "N/A",
    "Budget Shortfall": f"${shortfall:,.0f}" if pd.notna(shortfall) else "N/A"
}
llm_explainer_ui("Executive Overview", context_dict)

# --- NATIONAL TREND ---
section_header("National Trend (2009-2023)", "Average food insecurity rate over time", "chart-line")

trend = data.groupby("year", observed=True)["overall_food_insecurity_rate"].mean().reset_index()
trend.columns = ["Year", "FI Rate"]

fig_trend = go.Figure()
fig_trend.add_trace(go.Scatter(
    x=trend["Year"], y=trend["FI Rate"],
    mode="lines+markers",
    line=dict(color=COLORS["blue"], width=3),
    marker=dict(size=8, color=COLORS["blue"]),
    fill="tozeroy",
    fillcolor="rgba(34, 81, 255, 0.08)",
    name="Food Insecurity Rate",
    hovertemplate="<b>%{x}</b><br>FI Rate: %{y:.1%}<extra></extra>",
))

# Add recession/COVID bands
fig_trend.add_vrect(x0=2009, x1=2010, fillcolor="rgba(192,57,43,0.08)",
                    line_width=0, annotation_text="Recession", annotation_position="top left")
fig_trend.add_vrect(x0=2020, x1=2021, fillcolor="rgba(192,57,43,0.08)",
                    line_width=0, annotation_text="COVID-19", annotation_position="top left")

fig_trend.update_layout(
    **PLOTLY_LAYOUT,
    title="",
    yaxis_title="Food Insecurity Rate",
    xaxis_title="Year",
    yaxis_tickformat=".0%",
    height=400,
    showlegend=False,
)
st.plotly_chart(fig_trend, width='stretch')

# --- TWO-COLUMN: REGIONAL COMPARISON + KEY STATS ---
col1, col2 = st.columns([3, 2])

with col1:
    section_header("Regional Comparison", icon="globe-americas")
    if "census_region" in year_data.columns:
        regional = (year_data.groupby("census_region", observed=True)["overall_food_insecurity_rate"]
                    .mean().reset_index()
                    .sort_values("overall_food_insecurity_rate", ascending=True))
        regional.columns = ["Region", "FI Rate"]
        regional = regional.dropna(subset=["Region"])

        fig_reg = px.bar(
            regional, x="FI Rate", y="Region", orientation="h",
            color="FI Rate",
            color_continuous_scale=[COLORS["teal"], COLORS["amber"], COLORS["rose"]],
        )
        fig_reg.update_layout(
            **PLOTLY_LAYOUT, title="", height=300, showlegend=False,
            coloraxis_showscale=False,
            xaxis_tickformat=".0%",
        )
        fig_reg.update_traces(
            hovertemplate="<b>%{y}</b><br>FI Rate: %{x:.1%}<extra></extra>",
        )
        st.plotly_chart(fig_reg, width='stretch')

with col2:
    section_header("Key Statistics", icon="calculator")
    fi_vals = year_data["overall_food_insecurity_rate"].dropna()
    c1, c2 = st.columns(2, gap="medium")
    with c1:
        stat_card("Median FI Rate", f"{fi_vals.median():.1%}", color="blue")
    with c2:
        stat_card("Std Deviation", f"{fi_vals.std():.1%}", color="purple")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    c3, c4 = st.columns(2, gap="medium")
    with c3:
        stat_card("Range", f"{fi_vals.min():.1%} - {fi_vals.max():.1%}", color="amber")
    with c4:
        above_avg = (fi_vals > fi_vals.mean()).sum()
        stat_card("Above Average", f"{above_avg:,} counties", color="red")

# --- TOP/BOTTOM STATES ---
section_header("State Rankings", "Top and bottom 10 states by food insecurity rate", "trophy")

state_avg = (year_data.groupby("state", observed=True)["overall_food_insecurity_rate"]
             .mean().reset_index()
             .sort_values("overall_food_insecurity_rate"))
state_avg.columns = ["State", "FI Rate"]
state_avg["State Name"] = state_avg["State"].map(STATE_NAMES)

col_top, col_bot = st.columns(2)

with col_top:
    st.markdown(
        '<div class="bg-emerald-50 border border-emerald-200 rounded-xl p-4 mb-3">'
        '<h3 class="text-emerald-800 font-bold text-sm">Top 10 - Lowest Food Insecurity</h3></div>',
        unsafe_allow_html=True,
    )
    top10 = state_avg.head(10).copy()
    top10["Rank"] = range(1, 11)
    top10["FI Rate"] = top10["FI Rate"].apply(lambda x: f"{x:.1%}")
    st.dataframe(top10[["Rank", "State Name", "FI Rate"]], width='stretch', hide_index=True)

with col_bot:
    st.markdown(
        '<div class="bg-red-50 border border-red-200 rounded-xl p-4 mb-3">'
        '<h3 class="text-red-800 font-bold text-sm">Bottom 10 - Highest Food Insecurity</h3></div>',
        unsafe_allow_html=True,
    )
    bot10 = state_avg.tail(10).iloc[::-1].copy()
    bot10["Rank"] = range(1, 11)
    bot10["FI Rate"] = bot10["FI Rate"].apply(lambda x: f"{x:.1%}")
    st.dataframe(bot10[["Rank", "State Name", "FI Rate"]], width='stretch', hide_index=True)

# --- STATE MAP ---
section_header("State-Level Map", f"Food insecurity rate by state ({selected_year})", "map")

state_map = (year_data.groupby("state", observed=True)["overall_food_insecurity_rate"]
             .mean().reset_index())
state_map.columns = ["State", "FI Rate"]
state_map["State Name"] = state_map["State"].map(STATE_NAMES)

fig_map = px.choropleth(
    state_map, locations="State", locationmode="USA-states",
    color="FI Rate", color_continuous_scale=[COLORS["teal"], COLORS["amber"], COLORS["rose"]],
    scope="usa", hover_name="State Name",
    labels={"FI Rate": "Food Insecurity Rate"},
)
fig_map.update_layout(
    **PLOTLY_LAYOUT,
    title="",
    height=500,
    geo=dict(bgcolor="rgba(0,0,0,0)", lakecolor="rgba(0,0,0,0)"),
    coloraxis_colorbar=dict(tickformat=".0%", title="FI Rate"),
)
st.plotly_chart(fig_map, width='stretch')

# --- URBAN VS RURAL ---
section_header("Urban vs Rural Comparison", icon="city")

if "urban_rural" in year_data.columns:
    urban = (year_data.groupby("urban_rural", observed=True)["overall_food_insecurity_rate"]
             .mean().reset_index())
    urban.columns = ["Category", "FI Rate"]
    urban = urban.dropna()

    fig_urban = px.bar(
        urban, x="Category", y="FI Rate",
        color="Category",
        color_discrete_sequence=[COLORS["teal"], COLORS["amber"], COLORS["blue"]],
    )
    fig_urban.update_layout(
        **PLOTLY_LAYOUT, title="", height=350, showlegend=False,
        yaxis_tickformat=".0%", yaxis_title="Avg Food Insecurity Rate",
    )
    fig_urban.update_traces(
        hovertemplate="<b>%{x}</b><br>FI Rate: %{y:.1%}<extra></extra>",
    )
    st.plotly_chart(fig_urban, width='stretch')

# Footer
st.markdown(
    '<div class="text-center py-4 text-gray-400 text-xs">'
    'Source: Feeding America Map the Meal Gap &bull; U.S. Census ACS</div>',
    unsafe_allow_html=True,
)
