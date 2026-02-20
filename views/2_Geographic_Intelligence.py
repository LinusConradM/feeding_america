"""
Geographic Intelligence - Interactive choropleth maps and spatial analysis.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils.theme import inject_tailwind, COLORS, PLOTLY_LAYOUT, page_header
from utils.components import kpi_row, section_header, stat_card, info_banner, llm_explainer_ui
from utils.data_loader import load_data, get_variable_label, STATE_NAMES


data = load_data()

if "geo_selected_state" not in st.session_state:
    st.session_state.geo_selected_state = "All States"

# Sidebar controls
with st.sidebar:
    st.markdown('<p class="text-white font-semibold text-sm mb-2">Map Controls</p>', unsafe_allow_html=True)

    map_variable = st.selectbox(
        "Primary Variable",
        ["overall_food_insecurity_rate", "child_food_insecurity_rate",
         "poverty_rate", "unemployment_rate", "median_income", "cost_per_meal"],
        format_func=get_variable_label,
    )
    
    map_variable_secondary = st.selectbox(
        "Secondary Variable (Bivariate Map)",
        ["None", "overall_food_insecurity_rate", "child_food_insecurity_rate",
         "poverty_rate", "unemployment_rate", "median_income", "cost_per_meal"],
        format_func=lambda x: "None (Standard Map)" if x == "None" else get_variable_label(x)
    )

    map_year = st.slider("Year", int(data["year"].min()), int(data["year"].max()),
                         int(data["year"].max()))

    state_options = ["All States"] + sorted(data["state"].dropna().unique().tolist())
    try:
        current_index = state_options.index(st.session_state.geo_selected_state)
    except ValueError:
        current_index = 0

    sidebar_state = st.selectbox(
        "Focus State",
        state_options,
        index=current_index
    )
    
    # Catch manual sidebar change immediately and sync global state
    if sidebar_state != st.session_state.geo_selected_state:
        st.session_state.geo_selected_state = sidebar_state
        st.rerun()
        
    selected_state = st.session_state.geo_selected_state

page_header("Geographic Intelligence",
            "Spatial analysis of food insecurity across U.S. counties", "map-marked-alt")

# Filter data
year_data = data[data["year"] == map_year].copy()
if selected_state != "All States":
    focus_data = year_data[year_data["state"] == selected_state]
else:
    focus_data = year_data

# Spatial KPIs
is_rate = "rate" in map_variable or map_variable in ["poverty_rate", "unemployment_rate"]
vals = focus_data[map_variable].dropna()

if len(vals) > 0:
    fmt = lambda v: f"{v:.1%}" if is_rate else (f"${v:,.2f}" if "cost" in map_variable or "income" in map_variable else f"{v:,.0f}")

    hotspot_thresh = vals.quantile(0.9)
    coldspot_thresh = vals.quantile(0.1)
    hotspots = (vals >= hotspot_thresh).sum()
    coldspots = (vals <= coldspot_thresh).sum()

    kpi_row([
        {"title": "Hot-Spot Counties", "value": str(hotspots),
         "icon": "fire", "gradient": "coral"},
        {"title": "Cold-Spot Counties", "value": str(coldspots),
         "icon": "snowflake", "gradient": "sapphire"},
        {"title": f"Avg {get_variable_label(map_variable)}", "value": fmt(vals.mean()) if len(vals) > 0 else "N/A",
         "icon": "chart-bar", "gradient": "amethyst"},
        {"title": "Counties Analyzed", "value": f"{len(vals):,}",
         "icon": "map-pin", "gradient": "emerald"},
    ])

st.markdown("<div class='h-4'></div>", unsafe_allow_html=True)

# LLM Insight Engine
context_dict = {
    "Year": map_year,
    "Selected Geography": selected_state,
    "Analyzed Variable": get_variable_label(map_variable),
    "Average Value": fmt(vals.mean()) if len(vals) > 0 else "N/A",
    "Hot-Spot Counties": str(hotspots) if len(vals) > 0 else "0",
    "Cold-Spot Counties": str(coldspots) if len(vals) > 0 else "0",
    "Total Counties": f"{len(vals):,}"
}
llm_explainer_ui("Geographic Intelligence", context_dict)

# --- STATE CHOROPLETH MAP ---
is_bivariate = map_variable_secondary != "None" and map_variable_secondary != map_variable
map_title = f"{get_variable_label(map_variable)} ({map_year})" if not is_bivariate else f"Bivariate: {get_variable_label(map_variable)} + {get_variable_label(map_variable_secondary)}"
section_header("State-Level Map", map_title, "map")

if not is_bivariate:
    # Standard Univariate Map
    state_agg = (year_data.groupby("state", observed=True)[map_variable].mean().reset_index())
    state_agg.columns = ["State", "Value"]
    state_agg["State Name"] = state_agg["State"].map(STATE_NAMES)

    # Choose color scale direction
    if map_variable == "median_income":
        color_scale = [COLORS["ruby"], COLORS["amber"], COLORS["emerald"]]
    else:
        color_scale = [COLORS["emerald"], COLORS["amber"], COLORS["ruby"]]

    fig_map = px.choropleth(
        state_agg, locations="State", locationmode="USA-states",
        color="Value", color_continuous_scale=color_scale,
        scope="usa", hover_name="State Name",
        labels={"Value": get_variable_label(map_variable)},
    )
    fig_map.update_layout(
        **PLOTLY_LAYOUT, title="", height=550,
        geo=dict(bgcolor="rgba(0,0,0,0)", lakecolor="rgba(0,0,0,0)",
                 showlakes=True),
        coloraxis_colorbar=dict(
            tickformat=".0%" if is_rate else "$,.0f" if "income" in map_variable else ",.0f",
            title=get_variable_label(map_variable),
        ),
    )
else:
    # Bivariate Application
    state_agg = (year_data.groupby("state", observed=True)[[map_variable, map_variable_secondary]].mean().reset_index())
    state_agg.columns = ["State", "Var1", "Var2"]
    state_agg["State Name"] = state_agg["State"].map(STATE_NAMES)
    
    # Needs to handle inverse scales like Income (High Income is actually 'Low' vulnerability)
    invert_1 = map_variable == "median_income"
    invert_2 = map_variable_secondary == "median_income"
    
    # 3x3 Bins
    try:
        # qcut fails if there are duplicate bin edges, we drop duplicates or add jitter
        v1_quantiles = pd.qcut(state_agg["Var1"].rank(method='first'), 3, labels=[1, 2, 3])
        v2_quantiles = pd.qcut(state_agg["Var2"].rank(method='first'), 3, labels=[1, 2, 3])
        
        # Invert the rank integer logic if higher is "better" (Income)
        if invert_1: v1_quantiles = 4 - v1_quantiles.astype(int)
        else: v1_quantiles = v1_quantiles.astype(int)
            
        if invert_2: v2_quantiles = 4 - v2_quantiles.astype(int)
        else: v2_quantiles = v2_quantiles.astype(int)
            
        state_agg["Bivariate_Class"] = v1_quantiles.astype(str) + "-" + v2_quantiles.astype(str)
    
        # 3x3 Color Matrix (Teal/Pink schema is standard for Bivariate)
        bi_colors = {
            "1-1": "#e8e8e8", "1-2": "#ace4e4", "1-3": "#5ac8c8", # Low Var1
            "2-1": "#dfb0d6", "2-2": "#a5add3", "2-3": "#5698b9", # Med Var1
            "3-1": "#be64ac", "3-2": "#8c62aa", "3-3": "#3b4994"  # High Var1 (High Overlap = Dark Blue)
        }
        
        # Helper string for hover text
        def get_rating(val):
            return "Low" if val == "1" else ("Med" if val == "2" else "High")
            
        state_agg["Profile"] = state_agg["Bivariate_Class"].apply(lambda x: f"{get_variable_label(map_variable)}: {get_rating(x[0])}<br>{get_variable_label(map_variable_secondary)}: {get_rating(x[2])}")
        state_agg["Color"] = state_agg["Bivariate_Class"].map(bi_colors)
        
        fig_map = go.Figure()
        for b_class in bi_colors.keys():
            df_sub = state_agg[state_agg["Bivariate_Class"] == b_class]
            if len(df_sub) > 0:
                fig_map.add_trace(go.Choropleth(
                    locations=df_sub["State"], locationmode="USA-states",
                    z=np.ones(len(df_sub)),
                    colorscale=[[0, bi_colors[b_class]], [1, bi_colors[b_class]]],
                    showscale=False,
                    text=df_sub["State Name"] + "<br><br>" + df_sub["Profile"],
                    hoverinfo="text",
                    name=f"Overlap Tier: {b_class}"
                ))
    
        fig_map.update_layout(
            **PLOTLY_LAYOUT, title="", height=550,
            geo=dict(scope="usa", bgcolor="rgba(0,0,0,0)", lakecolor="rgba(0,0,0,0)", showlakes=True),
        )
    except Exception as e:
        info_banner("Not enough variance to compute a 3x3 bivariate matrix.", "warning")
        fig_map = go.Figure()

# Add state initials as a text overlay
fig_map.add_trace(go.Scattergeo(
    locations=state_agg["State"],
    locationmode="USA-states",
    text=state_agg["State"],
    mode="text",
    textfont=dict(color="#0f172a", size=10, family="Inter, sans-serif"),
    hoverinfo="skip"
))

# Highlight selected state
if selected_state != "All States":
    fig_map.add_trace(go.Choropleth(
        locations=[selected_state], locationmode="USA-states",
        z=[1], colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
        showscale=False,
        marker_line_color="black", marker_line_width=3,
        hoverinfo="skip",
    ))

map_event = st.plotly_chart(fig_map, width='stretch', on_select="rerun", selection_mode="points")

if map_event and "selection" in map_event and "points" in map_event["selection"] and len(map_event["selection"]["points"]) > 0:
    clicked_state = map_event["selection"]["points"][0].get("location")
    if clicked_state and clicked_state != st.session_state.geo_selected_state:
        st.session_state.geo_selected_state = clicked_state
        st.rerun()

# --- STATE DETAIL (if selected) ---
if selected_state != "All States":
    section_header(
        f"{STATE_NAMES.get(selected_state, selected_state)} Detail",
        "County-level breakdown", "search-location",
    )

    state_data = year_data[year_data["state"] == selected_state].copy()

    if len(state_data) > 0:
        col1, col2 = st.columns([3, 2])

        with col1:
            # County bar chart
            county_data = (state_data[["county", map_variable]].dropna()
                          .sort_values(map_variable, ascending=True).tail(20))

            fig_county = px.bar(
                county_data, x=map_variable, y="county", orientation="h",
                color=map_variable, color_continuous_scale=color_scale,
            )
            fig_county.update_layout(
                **PLOTLY_LAYOUT, title="Top 20 Counties", height=500,
                showlegend=False, coloraxis_showscale=False,
                xaxis_tickformat=".0%" if is_rate else "",
                yaxis_title="",
            )
            st.plotly_chart(fig_county, width='stretch')

        with col2:
            st.markdown("<div class='mt-6'></div>", unsafe_allow_html=True)
            s_vals = state_data[map_variable].dropna()
            stat_card("State Average", fmt(s_vals.mean()) if len(s_vals) > 0 else "N/A", color="blue")
            stat_card("Minimum", fmt(s_vals.min()) if len(s_vals) > 0 else "N/A", color="green")
            stat_card("Maximum", fmt(s_vals.max()) if len(s_vals) > 0 else "N/A", color="red")
            stat_card("Std Deviation", fmt(s_vals.std()) if len(s_vals) > 1 else "N/A", color="purple")
            stat_card("Counties", f"{len(s_vals):,}", color="gray")

# --- TIME ANIMATION ---
section_header("Temporal Evolution", "How the selected variable changes over time", "clock")

time_agg = (data.groupby(["year", "state"])[map_variable].mean()
            .reset_index())
time_agg["State Name"] = time_agg["state"].map(STATE_NAMES)

# National trend line
nat_trend = data.groupby("year", observed=True)[map_variable].mean().reset_index()
nat_trend.columns = ["Year", "Value"]

fig_time = go.Figure()
fig_time.add_trace(go.Scatter(
    x=nat_trend["Year"], y=nat_trend["Value"],
    mode="lines+markers",
    line=dict(color=COLORS["sapphire"], width=3),
    marker=dict(size=8),
    fill="tozeroy", fillcolor="rgba(34,81,255,0.06)",
    name="National Average",
    hovertemplate="<b>%{x}</b><br>Value: %{y:.1%}<extra></extra>" if is_rate else "<b>%{x}</b><br>Value: %{y:,.2f}<extra></extra>",
))

if selected_state != "All States":
    state_trend = time_agg[time_agg["state"] == selected_state]
    fig_time.add_trace(go.Scatter(
        x=state_trend["year"], y=state_trend[map_variable],
        mode="lines+markers",
        line=dict(color=COLORS["ruby"], width=2, dash="dash"),
        marker=dict(size=6),
        name=STATE_NAMES.get(selected_state, selected_state),
    ))

fig_time.update_layout(
    **PLOTLY_LAYOUT, title="", height=400,
    yaxis_title=get_variable_label(map_variable),
    xaxis_title="Year",
    yaxis_tickformat=".0%" if is_rate else "",
)
st.plotly_chart(fig_time, width='stretch')

# --- DISTRIBUTION ---
section_header("Distribution Analysis", icon="chart-area")

col_hist, col_box = st.columns(2)

with col_hist:
    fig_hist = px.histogram(
        focus_data, x=map_variable, nbins=40,
        color_discrete_sequence=[COLORS["sapphire"]],
        labels={map_variable: get_variable_label(map_variable)},
    )
    fig_hist.update_layout(
        **PLOTLY_LAYOUT, title="Histogram", height=350,
        xaxis_tickformat=".0%" if is_rate else "",
        yaxis_title="County Count",
    )
    st.plotly_chart(fig_hist, width='stretch')

with col_box:
    if "census_region" in focus_data.columns:
        fig_box = px.box(
            focus_data.dropna(subset=[map_variable, "census_region"]),
            x="census_region", y=map_variable,
            color="census_region",
            color_discrete_sequence=[COLORS["sapphire"], COLORS["ruby"],
                                     COLORS["emerald"], COLORS["amber"]],
        )
        fig_box.update_layout(
            **PLOTLY_LAYOUT, title="By Region", height=350,
            showlegend=False,
            yaxis_tickformat=".0%" if is_rate else "",
            xaxis_title="",
        )
        st.plotly_chart(fig_box, width='stretch')

st.markdown(
    '<div class="text-center py-4 text-gray-400 text-xs">'
    'Source: Feeding America Map the Meal Gap &bull; U.S. Census ACS</div>',
    unsafe_allow_html=True,
)
