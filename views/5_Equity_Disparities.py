"""
Equity & Disparities - Demographic and geographic disparity analysis.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils.theme import inject_tailwind, COLORS, PLOTLY_LAYOUT, SEQUENTIAL_COLORS, page_header
from utils.components import kpi_row, section_header, stat_card, llm_explainer_ui
from utils.data_loader import load_data, get_variable_label, STATE_NAMES


data = load_data()

# Sidebar
with st.sidebar:
    st.markdown('<p class="text-white font-semibold text-sm mb-2">Filters</p>', unsafe_allow_html=True)
    eq_year = st.slider("Year", int(data["year"].min()), int(data["year"].max()),
                        int(data["year"].max()))

page_header("Equity & Disparities",
            "Analyzing food insecurity gaps across demographics and geography", "balance-scale")

year_data = data[data["year"] == eq_year].copy()

# LLM Insight Engine
context_dict = {
    "Year": eq_year,
    "National Average FI": f"{year_data['overall_food_insecurity_rate'].mean():.1%}" if len(year_data) > 0 else "N/A",
    "Max County FI": f"{year_data['overall_food_insecurity_rate'].max():.1%}" if len(year_data) > 0 else "N/A"
}
llm_explainer_ui("Equity & Disparities", context_dict)

# --- RACIAL/ETHNIC DISPARITIES ---
section_header("Racial & Ethnic Food Insecurity", icon="users")

race_cols = {
    "overall_food_insecurity_rate": "Overall",
    "child_food_insecurity_rate": "Children",
}

# Check for race-specific columns (actual names from data)
race_candidates = {
    "food_insecurity_rate_among_black_persons_all_ethnicities": "Black",
    "food_insecurity_rate_among_hispanic_persons_any_race": "Hispanic",
    "food_insecurity_rate_among_white_non_hispanic_persons": "White Non-Hispanic",
}
for col_candidate, label in race_candidates.items():
    if col_candidate in year_data.columns:
        race_cols[col_candidate] = label

if len(race_cols) > 1:
    race_data = []
    for col, label in race_cols.items():
        if col in year_data.columns:
            val = year_data[col].mean()
            if pd.notna(val):
                race_data.append({"Group": label, "FI Rate": val})

    if race_data:
        race_df = pd.DataFrame(race_data).sort_values("FI Rate", ascending=True)

        fig_race = px.bar(
            race_df, x="FI Rate", y="Group", orientation="h",
            color="FI Rate",
            color_continuous_scale=[COLORS["emerald"], COLORS["amber"], COLORS["ruby"]],
        )
        fig_race.update_layout(
            **PLOTLY_LAYOUT, title="", height=300,
            showlegend=False, coloraxis_showscale=False,
            xaxis_tickformat=".0%",
            xaxis_title="Average Food Insecurity Rate",
            yaxis_title="",
        )
        fig_race.update_traces(
            hovertemplate="<b>%{y}</b><br>FI Rate: %{x:.1%}<extra></extra>",
        )
        st.plotly_chart(fig_race, width='stretch')

# --- URBAN VS RURAL GAP ---
section_header("Urban-Rural Divide", icon="city")

if "urban_rural" in year_data.columns:
    urban_fi = year_data.groupby("urban_rural", observed=True)["overall_food_insecurity_rate"].agg(["mean", "median", "std", "count"]).reset_index()
    urban_fi.columns = ["Category", "Mean", "Median", "Std Dev", "Counties"]

    col1, col2 = st.columns([3, 2])

    with col1:
        fig_urban = px.bar(
            urban_fi, x="Category", y="Mean",
            color="Category",
            color_discrete_sequence=[COLORS["emerald"], COLORS["amber"], COLORS["sapphire"]],
            error_y="Std Dev",
        )
        fig_urban.update_layout(
            **PLOTLY_LAYOUT, title="", height=400,
            showlegend=False,
            yaxis_tickformat=".0%",
            yaxis_title="Avg Food Insecurity Rate",
        )
        st.plotly_chart(fig_urban, width='stretch')

    with col2:
        for _, row in urban_fi.iterrows():
            stat_card(
                f"{row['Category']}",
                f"{row['Mean']:.1%}",
                f"{int(row['Counties']):,} counties | Median: {row['Median']:.1%}",
                color="blue" if row["Category"] == "Metro" else "amber" if row["Category"] == "Non-metro" else "green",
            )

    # Gap metric
    if len(urban_fi) >= 2:
        rural_val = urban_fi.loc[urban_fi["Category"] == "Rural", "Mean"]
        metro_val = urban_fi.loc[urban_fi["Category"] == "Metro", "Mean"]
        if len(rural_val) > 0 and len(metro_val) > 0:
            gap = rural_val.values[0] - metro_val.values[0]
            ratio = rural_val.values[0] / metro_val.values[0] if metro_val.values[0] > 0 else 0
            kpi_row([
                {"title": "Absolute Gap", "value": f"{gap:.1%}", "icon": "arrows-alt-h", "gradient": "coral"},
                {"title": "Rural/Metro Ratio", "value": f"{ratio:.2f}x", "icon": "balance-scale", "gradient": "amethyst"},
            ])

st.markdown("<div class='h-6'></div>", unsafe_allow_html=True)

# --- INCOME INEQUALITY ---
section_header("Income & Food Insecurity", icon="coins")

if "income_category" in year_data.columns:
    income_fi = (year_data.groupby("income_category", observed=True)["overall_food_insecurity_rate"]
                 .mean().reset_index())
    income_fi.columns = ["Income Category", "FI Rate"]
    income_fi = income_fi.dropna()

    fig_income = px.bar(
        income_fi, x="Income Category", y="FI Rate",
        color="Income Category",
        color_discrete_sequence=[COLORS["ruby"], COLORS["amber"], COLORS["emerald"]],
    )
    fig_income.update_layout(
        **PLOTLY_LAYOUT, title="FI Rate by Income Category", height=350,
        showlegend=False, yaxis_tickformat=".0%",
    )
    st.plotly_chart(fig_income, width='stretch')

# --- GINI COEFFICIENT ANALYSIS ---
if "gini" in year_data.columns:
    section_header("Income Inequality (Gini)", icon="chart-pie")

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        fig_gini = px.scatter(
            year_data.dropna(subset=["gini", "overall_food_insecurity_rate"]),
            x="gini", y="overall_food_insecurity_rate",
            color="urban_rural" if "urban_rural" in year_data.columns else None,
            opacity=0.5,
            trendline="ols",
            labels={"gini": "Gini Coefficient", "overall_food_insecurity_rate": "Food Insecurity Rate"},
            color_discrete_sequence=SEQUENTIAL_COLORS,
        )
        fig_gini.update_layout(
            **PLOTLY_LAYOUT, title="Inequality vs Food Insecurity", height=400,
            yaxis_tickformat=".0%",
        )
        st.plotly_chart(fig_gini, width='stretch')

    with col_g2:
        # Gini distribution
        fig_gini_hist = px.histogram(
            year_data.dropna(subset=["gini"]), x="gini", nbins=40,
            color_discrete_sequence=[COLORS["amethyst"]],
        )
        fig_gini_hist.update_layout(
            **PLOTLY_LAYOUT, title="Gini Distribution", height=400,
            xaxis_title="Gini Coefficient", yaxis_title="County Count",
        )
        st.plotly_chart(fig_gini_hist, width='stretch')

# --- EDUCATION DISPARITIES ---
if "education_category" in year_data.columns:
    section_header("Education & Food Insecurity", icon="graduation-cap")

    edu_fi = (year_data.groupby("education_category", observed=True)["overall_food_insecurity_rate"]
              .mean().reset_index())
    edu_fi.columns = ["Education Level", "FI Rate"]
    edu_fi = edu_fi.dropna()

    fig_edu = px.bar(
        edu_fi, x="Education Level", y="FI Rate",
        color="Education Level",
        color_discrete_sequence=[COLORS["emerald"], COLORS["amber"], COLORS["ruby"]],
    )
    fig_edu.update_layout(
        **PLOTLY_LAYOUT, title="FI Rate by Education Level", height=350,
        showlegend=False, yaxis_tickformat=".0%",
    )
    st.plotly_chart(fig_edu, width='stretch')

# --- TEMPORAL DISPARITY TRENDS ---
section_header("Disparity Trends Over Time", icon="chart-line")

if "urban_rural" in data.columns:
    urban_trend = (data.groupby(["year", "urban_rural"], observed=True)["overall_food_insecurity_rate"]
                   .mean().reset_index())
    urban_trend.columns = ["Year", "Category", "FI Rate"]

    fig_trend = px.line(
        urban_trend.dropna(), x="Year", y="FI Rate", color="Category",
        markers=True,
        color_discrete_sequence=[COLORS["emerald"], COLORS["amber"], COLORS["sapphire"]],
    )
    fig_trend.update_layout(
        **PLOTLY_LAYOUT, title="Urban-Rural Gap Over Time", height=400,
        yaxis_tickformat=".0%",
        yaxis_title="Avg Food Insecurity Rate",
    )
    st.plotly_chart(fig_trend, width='stretch')
