"""
Equity & Disparities - Demographic and geographic disparity analysis.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils.theme import COLORS, PLOTLY_LAYOUT, SEQUENTIAL_COLORS
from utils.components import kpi_row, section_header, stat_card, llm_explainer_ui
from utils.data_loader import load_data, get_variable_label, STATE_NAMES


data = load_data()

# Sidebar
with st.sidebar:
    st.markdown('<p class="text-white font-semibold text-sm mb-2">Filters</p>', unsafe_allow_html=True)
    eq_year = st.slider("Year", int(data["year"].min()), int(data["year"].max()),
                        int(data["year"].max()))

st.title("Equity & Disparities")
st.caption("Analyzing food insecurity gaps across demographics and geography")

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
            color_continuous_scale=[COLORS["teal"], COLORS["amber"], COLORS["rose"]],
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
        # Ridgeline Joyplot
        fig_urban = go.Figure()
        
        categories = ["Metro", "Non-metro", "Rural"]
        joy_colors = [COLORS["blue"], COLORS["amber"], COLORS["teal"]]
        
        for i, cat in enumerate(categories):
            cat_data = year_data[year_data["urban_rural"] == cat]["overall_food_insecurity_rate"].dropna()
            
            if len(cat_data) > 0:
                fig_urban.add_trace(go.Violin(
                    x=cat_data,
                    name=cat,
                    line_color=joy_colors[i],
                    side='positive', # creates the ridge/mountain effect
                    orientation='h',
                    width=2,
                    points=False, # cleaner look without scatter dots
                    meanline_visible=True, # shows true distribution mean inside the violin
                ))
                
        fig_urban.update_layout(
            **PLOTLY_LAYOUT, 
            title="Distribution Density (Joyplot)", 
            height=400,
            showlegend=False,
            xaxis_tickformat=".0%",
            xaxis_title="Food Insecurity Rate Distribution",
            violingap=0, violingroupgap=0, violinmode='overlay'
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
        color_discrete_sequence=[COLORS["rose"], COLORS["amber"], COLORS["teal"]],
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
            color_discrete_sequence=[COLORS["violet"]],
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
        color_discrete_sequence=[COLORS["teal"], COLORS["amber"], COLORS["rose"]],
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
        color_discrete_sequence=[COLORS["teal"], COLORS["amber"], COLORS["blue"]],
    )
    fig_trend.update_layout(
        **PLOTLY_LAYOUT, title="Urban-Rural Gap Over Time", height=400,
        yaxis_tickformat=".0%",
        yaxis_title="Avg Food Insecurity Rate",
    )
    st.plotly_chart(fig_trend, width='stretch')

st.markdown("<div class='h-6'></div>", unsafe_allow_html=True)

# ── NEW: RACIAL COMPOSITION vs FOOD INSECURITY ────────────────────────────────
demo_vars = [v for v in ["black_pct", "hispanic_pct"] if v in year_data.columns]
if demo_vars:
    section_header("Racial Demographics & Food Insecurity", "How racial composition correlates with county-level FI rates", "users")

    demo_col1, demo_col2 = st.columns(2)

    with demo_col1:
        if "black_pct" in year_data.columns:
            fig_black = px.scatter(
                year_data.dropna(subset=["black_pct", "overall_food_insecurity_rate"]),
                x="black_pct", y="overall_food_insecurity_rate",
                color="urban_rural" if "urban_rural" in year_data.columns else None,
                size="population" if "population" in year_data.columns else None,
                size_max=20,
                opacity=0.55,
                trendline="ols",
                labels={
                    "black_pct": "Black Population (%)",
                    "overall_food_insecurity_rate": "Food Insecurity Rate",
                    "urban_rural": "Area Type",
                },
                color_discrete_sequence=[COLORS["violet"], COLORS["amber"], COLORS["teal"]],
            )
            fig_black.update_layout(
                **PLOTLY_LAYOUT, title="Black Population % vs FI Rate",
                height=400, xaxis_tickformat=".0%", yaxis_tickformat=".0%",
            )
            st.plotly_chart(fig_black, width='stretch')

    with demo_col2:
        if "hispanic_pct" in year_data.columns:
            fig_hisp = px.scatter(
                year_data.dropna(subset=["hispanic_pct", "overall_food_insecurity_rate"]),
                x="hispanic_pct", y="overall_food_insecurity_rate",
                color="urban_rural" if "urban_rural" in year_data.columns else None,
                size="population" if "population" in year_data.columns else None,
                size_max=20,
                opacity=0.55,
                trendline="ols",
                labels={
                    "hispanic_pct": "Hispanic Population (%)",
                    "overall_food_insecurity_rate": "Food Insecurity Rate",
                    "urban_rural": "Area Type",
                },
                color_discrete_sequence=[COLORS["orange"], COLORS["amber"], COLORS["teal"]],
            )
            fig_hisp.update_layout(
                **PLOTLY_LAYOUT, title="Hispanic Population % vs FI Rate",
                height=400, xaxis_tickformat=".0%", yaxis_tickformat=".0%",
            )
            st.plotly_chart(fig_hisp, width='stretch')

    # Racial composition disparity trend over time
    if "black_pct" in data.columns:
        # Bin counties by black_pct quartile for the selected year and track over time
        try:
            year_data_copy = year_data.dropna(subset=["black_pct"]).copy()
            year_data_copy["black_pct_group"] = pd.qcut(
                year_data_copy["black_pct"], q=4,
                labels=["Q1 (Lowest)", "Q2", "Q3", "Q4 (Highest)"]
            )
            group_fips = year_data_copy.groupby("black_pct_group", observed=True)["fips"].apply(list).to_dict()

            trend_rows = []
            for yr in sorted(data["year"].dropna().unique()):
                yr_d = data[data["year"] == yr]
                for grp, fips_list in group_fips.items():
                    val = yr_d[yr_d["fips"].isin(fips_list)]["overall_food_insecurity_rate"].mean()
                    if pd.notna(val):
                        trend_rows.append({"Year": yr, "Black Population Quartile": str(grp), "FI Rate": val})

            if trend_rows:
                trend_df = pd.DataFrame(trend_rows)
                fig_btrend = px.line(
                    trend_df, x="Year", y="FI Rate", color="Black Population Quartile",
                    markers=True,
                    color_discrete_sequence=[COLORS["teal"], COLORS["blue"], COLORS["amber"], COLORS["rose"]],
                )
                fig_btrend.update_layout(
                    **PLOTLY_LAYOUT,
                    title="FI Rate Trend by Black Population Quartile",
                    height=380, yaxis_tickformat=".0%",
                )
                st.plotly_chart(fig_btrend, width='stretch')
        except Exception:
            pass

st.markdown("<div class='h-6'></div>", unsafe_allow_html=True)

# ── NEW: FEMALE-HEADED HOUSEHOLDS ─────────────────────────────────────────────
if "female_headed" in year_data.columns:
    section_header("Female-Headed Households & Food Insecurity",
                   "Single-parent female-led households are a key structural vulnerability indicator", "female")

    fh_col1, fh_col2 = st.columns([3, 2])

    with fh_col1:
        fig_fh = px.scatter(
            year_data.dropna(subset=["female_headed", "overall_food_insecurity_rate"]),
            x="female_headed", y="overall_food_insecurity_rate",
            color="income_category" if "income_category" in year_data.columns else None,
            opacity=0.55, trendline="ols",
            labels={
                "female_headed": "Female-Headed Households (%)",
                "overall_food_insecurity_rate": "Food Insecurity Rate",
                "income_category": "Income Level",
            },
            color_discrete_sequence=[COLORS["rose"], COLORS["amber"], COLORS["teal"]],
        )
        fig_fh.update_layout(
            **PLOTLY_LAYOUT, title="Female-Headed Households vs FI Rate",
            height=420, xaxis_tickformat=".0%", yaxis_tickformat=".0%",
        )
        st.plotly_chart(fig_fh, width='stretch')

    with fh_col2:
        # Box plot of FI rate by income × female_headed quintile
        try:
            fh_data = year_data.dropna(subset=["female_headed", "overall_food_insecurity_rate"]).copy()
            fh_data["fh_group"] = pd.qcut(
                fh_data["female_headed"], q=3,
                labels=["Low (0–33%)", "Medium (33–66%)", "High (66–100%)"]
            )
            fig_fh_box = px.box(
                fh_data, x="fh_group", y="overall_food_insecurity_rate",
                color="fh_group",
                color_discrete_sequence=[COLORS["teal"], COLORS["amber"], COLORS["rose"]],
                labels={
                    "fh_group": "Female-Headed Household Concentration",
                    "overall_food_insecurity_rate": "FI Rate",
                },
                points="outliers",
            )
            fig_fh_box.update_layout(
                **PLOTLY_LAYOUT, title="FI Rate by Female-Headed Household Tier",
                height=420, yaxis_tickformat=".0%", showlegend=False,
            )
            st.plotly_chart(fig_fh_box, width='stretch')
        except Exception:
            pass

    # KPIs
    fh_clean = year_data.dropna(subset=["female_headed", "overall_food_insecurity_rate"])
    if len(fh_clean) > 10:
        from scipy import stats as sp_stats
        r_fh, p_fh = sp_stats.pearsonr(fh_clean["female_headed"], fh_clean["overall_food_insecurity_rate"])
        kpi_row([
            {"title": "Correlation (r)", "value": f"{r_fh:.3f}", "icon": "link", "gradient": "sapphire"},
            {"title": "P-value", "value": f"{p_fh:.2e}" if p_fh < 0.001 else f"{p_fh:.4f}",
             "icon": "flask", "gradient": "emerald" if p_fh < 0.05 else "coral"},
            {"title": "Mean FI (High FH%)", "value": f"{fh_clean.nlargest(int(len(fh_clean)*0.25), 'female_headed')['overall_food_insecurity_rate'].mean():.1%}",
             "icon": "arrow-up", "gradient": "ruby"},
            {"title": "Mean FI (Low FH%)", "value": f"{fh_clean.nsmallest(int(len(fh_clean)*0.25), 'female_headed')['overall_food_insecurity_rate'].mean():.1%}",
             "icon": "arrow-down", "gradient": "emerald"},
        ])

st.markdown("<div class='h-6'></div>", unsafe_allow_html=True)

# ── NEW: TRANSPORTATION ACCESS (NO VEHICLE HOUSEHOLDS) ────────────────────────
if "no_vehicle" in year_data.columns:
    section_header("Transportation Access & Food Insecurity",
                   "Households without a vehicle face compounding barriers to food access", "car")

    nv_col1, nv_col2 = st.columns(2)

    with nv_col1:
        fig_nv = px.scatter(
            year_data.dropna(subset=["no_vehicle", "overall_food_insecurity_rate"]),
            x="no_vehicle", y="overall_food_insecurity_rate",
            color="urban_rural" if "urban_rural" in year_data.columns else None,
            opacity=0.5, trendline="ols",
            labels={
                "no_vehicle": "No Vehicle (%)",
                "overall_food_insecurity_rate": "Food Insecurity Rate",
                "urban_rural": "Area Type",
            },
            color_discrete_sequence=[COLORS["violet"], COLORS["amber"], COLORS["teal"]],
        )
        fig_nv.update_layout(
            **PLOTLY_LAYOUT, title="No Vehicle Households vs FI Rate",
            height=400, xaxis_tickformat=".0%", yaxis_tickformat=".0%",
        )
        st.plotly_chart(fig_nv, width='stretch')

    with nv_col2:
        # Bar chart: top 15 states by average no_vehicle rate
        state_nv = (year_data.groupby("state")[["no_vehicle", "overall_food_insecurity_rate"]]
                    .mean().reset_index().dropna())
        state_nv = state_nv.nlargest(15, "no_vehicle")

        fig_nv_bar = px.bar(
            state_nv.sort_values("no_vehicle", ascending=True),
            x="no_vehicle", y="state", orientation="h",
            color="overall_food_insecurity_rate",
            color_continuous_scale=[[0, COLORS["teal"]], [0.5, COLORS["amber"]], [1, COLORS["rose"]]],
            labels={
                "no_vehicle": "No Vehicle (%)",
                "state": "State",
                "overall_food_insecurity_rate": "FI Rate",
            },
        )
        fig_nv_bar.update_layout(
            **PLOTLY_LAYOUT, title="Top 15 States — No Vehicle Rate (colored by FI Rate)",
            height=400, xaxis_tickformat=".0%",
        )
        st.plotly_chart(fig_nv_bar, width='stretch')

    # Trend: no_vehicle vs FI over time nationally
    if "no_vehicle" in data.columns:
        nv_trend = (data.groupby("year")[["no_vehicle", "overall_food_insecurity_rate"]]
                    .mean().reset_index().dropna())

        fig_nv_dual = go.Figure()
        fig_nv_dual.add_trace(go.Scatter(
            x=nv_trend["year"], y=nv_trend["overall_food_insecurity_rate"],
            name="Food Insecurity Rate", mode="lines+markers",
            line=dict(color=COLORS["rose"], width=2),
            yaxis="y1",
        ))
        fig_nv_dual.add_trace(go.Scatter(
            x=nv_trend["year"], y=nv_trend["no_vehicle"],
            name="No Vehicle Rate", mode="lines+markers",
            line=dict(color=COLORS["violet"], width=2, dash="dash"),
            yaxis="y2",
        ))
        fig_nv_dual.update_layout(
            **PLOTLY_LAYOUT,
            title="No Vehicle Rate vs Food Insecurity Over Time",
            height=380,
        )
        fig_nv_dual.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            yaxis=dict(title="Food Insecurity Rate", tickformat=".0%", side="left"),
            yaxis2=dict(title="No Vehicle Rate", tickformat=".0%", side="right",
                        overlaying="y", showgrid=False),
        )
        st.plotly_chart(fig_nv_dual, width='stretch')

