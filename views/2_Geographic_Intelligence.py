"""
Geographic Intelligence - Interactive choropleth maps and spatial analysis.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils.theme import COLORS, PLOTLY_LAYOUT
from utils.components import kpi_row, section_header, stat_card, info_banner, llm_explainer_ui
from utils.data_loader import load_data, get_variable_label, STATE_NAMES, weighted_rate, weighted_rate_by_group
from utils.responsive import get_viewport_profile, ChartConfig


data = load_data()
viewport = get_viewport_profile()
IS_MOBILE = viewport.is_mobile
chart_config = ChartConfig.for_viewport(viewport)

if "geo_selected_state" not in st.session_state:
    st.session_state.geo_selected_state = "All States"

# ── Variable options (expanded with DS suggestions) ───────────────────────────
VARIABLE_OPTIONS = [
    "overall_food_insecurity_rate", "child_food_insecurity_rate",
    "poverty_rate", "unemployment_rate", "median_income", "cost_per_meal",
    "snap_rate", "rent_burden", "gini",
    "food_insecurity_rate_among_black_persons_all_ethnicities",
    "food_insecurity_rate_among_hispanic_persons_any_race",
    "food_insecurity_rate_among_white_non_hispanic_persons",
]
# Filter to columns that actually exist in the data
VARIABLE_OPTIONS = [v for v in VARIABLE_OPTIONS if v in data.columns]

# Sidebar controls
with st.sidebar:
    st.markdown(f'<p style="color:{COLORS["white"]};font-weight:600;font-size:0.875rem;margin-bottom:0.5rem;">Map Controls</p>', unsafe_allow_html=True)

    map_variable = st.selectbox("Primary Variable", VARIABLE_OPTIONS, format_func=get_variable_label)

    secondary_opts = ["None"] + VARIABLE_OPTIONS
    map_variable_secondary = st.selectbox(
        "Secondary Variable (Bivariate Map)",
        secondary_opts,
        format_func=lambda x: "None (Standard Map)" if x == "None" else get_variable_label(x)
    )

    map_year = st.slider("Year", int(data["year"].min()), int(data["year"].max()),
                         int(data["year"].max()))

    # Urban/Rural filter
    urban_rural_filter = "All"
    if "urban_rural" in data.columns:
        ur_options = ["All"] + sorted(data["urban_rural"].dropna().unique().tolist())
        urban_rural_filter = st.selectbox("Urban/Rural Filter", ur_options)

    state_options = ["All States"] + sorted(data["state"].dropna().unique().tolist())
    try:
        current_index = state_options.index(st.session_state.geo_selected_state)
    except ValueError:
        current_index = 0

    sidebar_state = st.selectbox("Focus State", state_options, index=current_index)

    if sidebar_state != st.session_state.geo_selected_state:
        st.session_state.geo_selected_state = sidebar_state
        st.rerun()

    selected_state = st.session_state.geo_selected_state


# ── Page Header ───────────────────────────────────────────────────────────────
st.markdown(f"""
<div role="banner" aria-label="Geographic Intelligence header"
     style="text-align:center;padding:1.5rem 1rem 1rem;margin-bottom:1.5rem;
            border-bottom:2px solid {COLORS['pearl']};">
    <h1 style="font-family:Georgia,serif;color:{COLORS['ink']};font-size:clamp(2rem,5vw,3rem);
               font-weight:800;line-height:1.1;margin:0 0 0.25rem 0;letter-spacing:-0.02em">
        Geographic Intelligence
    </h1>
    <p style="font-family:Inter,sans-serif;color:{COLORS['steel']};font-size:clamp(0.9rem,1.8vw,1.05rem);
              line-height:1.6;max-width:600px;margin:0 auto">
        Spatial analysis of food insecurity across U.S. counties
    </p>
</div>
""", unsafe_allow_html=True)


# ── Filter data ───────────────────────────────────────────────────────────────
year_data = data[data["year"] == map_year].copy()

# Apply urban/rural filter
if urban_rural_filter != "All" and "urban_rural" in year_data.columns:
    year_data = year_data[year_data["urban_rural"] == urban_rural_filter]

if selected_state != "All States":
    focus_data = year_data[year_data["state"] == selected_state]
else:
    focus_data = year_data

# ── Detect variable type ──────────────────────────────────────────────────────
is_rate = "rate" in map_variable or "gini" in map_variable
is_currency = "cost" in map_variable or "income" in map_variable or "shortfall" in map_variable


def fmt(v):
    """Format a value based on the selected variable type."""
    if pd.isna(v):
        return "N/A"
    if is_rate:
        return f"{v:.1%}"
    if is_currency:
        return f"${v:,.2f}" if "cost" in map_variable else f"${v:,.0f}"
    return f"{v:,.0f}"


# ── Spatial KPIs (absolute thresholds where possible) ─────────────────────────
vals = focus_data[map_variable].dropna()

# Use meaningful absolute thresholds for FI rate, else fall back to percentiles
if map_variable == "overall_food_insecurity_rate":
    hotspot_thresh, coldspot_thresh = 0.20, 0.10  # >20% Very High, <10% Low
    hotspot_label, coldspot_label = "Very High (>20%)", "Low (<10%)"
elif map_variable == "child_food_insecurity_rate":
    hotspot_thresh, coldspot_thresh = 0.25, 0.12
    hotspot_label, coldspot_label = "Very High (>25%)", "Low (<12%)"
elif map_variable == "poverty_rate":
    hotspot_thresh, coldspot_thresh = 0.20, 0.10
    hotspot_label, coldspot_label = "High Poverty (>20%)", "Low (<10%)"
else:
    hotspot_thresh = vals.quantile(0.9) if len(vals) > 0 else 0
    coldspot_thresh = vals.quantile(0.1) if len(vals) > 0 else 0
    hotspot_label, coldspot_label = "Hot-Spots (P90)", "Cold-Spots (P10)"

hotspots = int((vals >= hotspot_thresh).sum()) if len(vals) > 0 else 0
coldspots = int((vals <= coldspot_thresh).sum()) if len(vals) > 0 else 0
avg_val = weighted_rate(focus_data, map_variable) if len(vals) > 0 else np.nan

kpi_row([
    {"title": hotspot_label, "value": f"{hotspots:,}",
     "icon": "fire", "gradient": "coral"},
    {"title": coldspot_label, "value": f"{coldspots:,}",
     "icon": "snowflake", "gradient": "sapphire"},
    {"title": f"Avg {get_variable_label(map_variable)}", "value": fmt(avg_val),
     "icon": "chart-bar", "gradient": "amethyst"},
    {"title": "Counties Analyzed", "value": f"{len(vals):,}",
     "icon": "map-pin", "gradient": "emerald"},
])

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# LLM Insight Engine
context_dict = {
    "Year": map_year,
    "Selected Geography": selected_state,
    "Urban/Rural Filter": urban_rural_filter,
    "Analyzed Variable": get_variable_label(map_variable),
    "Average Value": fmt(avg_val),
    "Hot-Spot Counties": str(hotspots),
    "Cold-Spot Counties": str(coldspots),
    "Total Counties": f"{len(vals):,}"
}
llm_explainer_ui("Geographic Intelligence", context_dict)


# ── Color scale (defined once, used in both map and detail) ───────────────────
if map_variable == "median_income":
    color_scale = [COLORS["rose"], COLORS["amber"], COLORS["teal"]]
else:
    color_scale = [COLORS["teal"], COLORS["amber"], COLORS["rose"]]


# ============================================================================
# STATE CHOROPLETH MAP
# ============================================================================
is_bivariate = map_variable_secondary != "None" and map_variable_secondary != map_variable
map_title = (f"{get_variable_label(map_variable)} ({map_year})"
             if not is_bivariate
             else f"Bivariate: {get_variable_label(map_variable)} + {get_variable_label(map_variable_secondary)}")
section_header("State-Level Map", map_title, "map")

map_height = chart_config.height + 100  # Maps need more vertical space

if not is_bivariate:
    # Standard Univariate Map (population-weighted)
    state_agg = weighted_rate_by_group(year_data, map_variable, "state").reset_index()
    state_agg.columns = ["State", "Value"]
    state_agg["State Name"] = state_agg["State"].map(STATE_NAMES)

    tick_fmt = ".0%" if is_rate else ("$,.0f" if is_currency else ",.0f")

    fig_map = px.choropleth(
        state_agg, locations="State", locationmode="USA-states",
        color="Value", color_continuous_scale=color_scale,
        scope="usa", hover_name="State Name",
        labels={"Value": get_variable_label(map_variable)},
    )
    fig_map.update_layout(
        **PLOTLY_LAYOUT, title="", height=map_height,
        geo=dict(bgcolor="rgba(0,0,0,0)", lakecolor="rgba(0,0,0,0)", showlakes=True),
        coloraxis_colorbar=dict(tickformat=tick_fmt, title=get_variable_label(map_variable)),
    )
else:
    # Bivariate Map
    biv_cols = [map_variable, map_variable_secondary]
    state_agg = year_data.groupby("state", observed=True)[biv_cols].mean().reset_index()
    state_agg.columns = ["State", "Var1", "Var2"]
    state_agg["State Name"] = state_agg["State"].map(STATE_NAMES)

    invert_1 = map_variable == "median_income"
    invert_2 = map_variable_secondary == "median_income"

    try:
        v1_q = pd.qcut(state_agg["Var1"].rank(method='first'), 3, labels=[1, 2, 3])
        v2_q = pd.qcut(state_agg["Var2"].rank(method='first'), 3, labels=[1, 2, 3])

        v1_q = (4 - v1_q.astype(int)) if invert_1 else v1_q.astype(int)
        v2_q = (4 - v2_q.astype(int)) if invert_2 else v2_q.astype(int)

        state_agg["Bivariate_Class"] = v1_q.astype(str) + "-" + v2_q.astype(str)

        bi_colors = {
            "1-1": "#e8e8e8", "1-2": "#ace4e4", "1-3": "#5ac8c8",
            "2-1": "#dfb0d6", "2-2": "#a5add3", "2-3": "#5698b9",
            "3-1": "#be64ac", "3-2": "#8c62aa", "3-3": "#3b4994",
        }

        def get_rating(val):
            return "Low" if val == "1" else ("Med" if val == "2" else "High")

        state_agg["Profile"] = state_agg["Bivariate_Class"].apply(
            lambda x: f"{get_variable_label(map_variable)}: {get_rating(x[0])}<br>{get_variable_label(map_variable_secondary)}: {get_rating(x[2])}"
        )

        fig_map = go.Figure()
        for b_class, b_color in bi_colors.items():
            df_sub = state_agg[state_agg["Bivariate_Class"] == b_class]
            if len(df_sub) > 0:
                fig_map.add_trace(go.Choropleth(
                    locations=df_sub["State"], locationmode="USA-states",
                    z=np.ones(len(df_sub)),
                    colorscale=[[0, b_color], [1, b_color]],
                    showscale=False,
                    text=df_sub["State Name"] + "<br><br>" + df_sub["Profile"],
                    hoverinfo="text",
                    name=f"Tier: {b_class}"
                ))

        fig_map.update_layout(
            **PLOTLY_LAYOUT, title="", height=map_height,
            geo=dict(scope="usa", bgcolor="rgba(0,0,0,0)", lakecolor="rgba(0,0,0,0)", showlakes=True),
        )
    except Exception:
        info_banner("Not enough variance to compute a 3x3 bivariate matrix.", "warning")
        fig_map = go.Figure()

# Add state initials overlay
fig_map.add_trace(go.Scattergeo(
    locations=state_agg["State"],
    locationmode="USA-states",
    text=state_agg["State"],
    mode="text",
    textfont=dict(color=COLORS["ink"], size=10, family="Inter, sans-serif"),
    hoverinfo="skip"
))

# Highlight selected state
if selected_state != "All States":
    fig_map.add_trace(go.Choropleth(
        locations=[selected_state], locationmode="USA-states",
        z=[1], colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
        showscale=False,
        marker_line_color=COLORS["ink"], marker_line_width=3,
        hoverinfo="skip",
    ))

map_event = st.plotly_chart(fig_map, width='stretch', on_select="rerun", selection_mode="points")

if map_event and "selection" in map_event and "points" in map_event["selection"] and len(map_event["selection"]["points"]) > 0:
    clicked_state = map_event["selection"]["points"][0].get("location")
    if clicked_state and clicked_state != st.session_state.geo_selected_state:
        st.session_state.geo_selected_state = clicked_state
        st.rerun()


# ============================================================================
# STATE DETAIL (with county-level FIPS choropleth)
# ============================================================================
if selected_state != "All States":
    section_header(
        f"{STATE_NAMES.get(selected_state, selected_state)} Detail",
        "County-level breakdown", "search-location",
    )

    state_data = year_data[year_data["state"] == selected_state].copy()

    if len(state_data) > 0:
        # DS: County-level FIPS choropleth
        if "fips" in state_data.columns and state_data[map_variable].notna().any():
            from urllib.request import urlopen
            import json

            @st.cache_data(show_spinner=False, ttl=86400)
            def _load_counties_geojson():
                url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
                with urlopen(url) as response:
                    return json.loads(response.read().decode())

            try:
                counties_geo = _load_counties_geojson()
                county_map_data = state_data[["fips", "county", map_variable]].dropna()
                county_map_data["fips"] = county_map_data["fips"].astype(str).str.zfill(5)

                fig_county_map = px.choropleth(
                    county_map_data, geojson=counties_geo, locations="fips",
                    color=map_variable, color_continuous_scale=color_scale,
                    hover_name="county",
                    labels={map_variable: get_variable_label(map_variable)},
                )
                fig_county_map.update_geos(fitbounds="locations", visible=False)
                county_layout = dict(PLOTLY_LAYOUT)
                county_layout["margin"] = dict(l=0, r=0, t=0, b=0)
                fig_county_map.update_layout(
                    **county_layout, title="", height=chart_config.height,
                    coloraxis_colorbar=dict(
                        tickformat=".0%" if is_rate else ("$,.0f" if is_currency else ",.0f"),
                        title=get_variable_label(map_variable),
                    ),
                )
                st.plotly_chart(fig_county_map, use_container_width=True, key="county_fips_map")
            except Exception:
                pass  # Fall through to bar chart if GeoJSON fails

        col1, col2 = st.columns([3, 2])

        with col1:
            # County bar chart
            county_data = (state_data[["county", map_variable]].dropna()
                          .sort_values(map_variable, ascending=True).tail(20))

            fig_county = px.bar(
                county_data, x=map_variable, y="county", orientation="h",
                color=map_variable, color_continuous_scale=color_scale,
            )
            bar_layout = dict(PLOTLY_LAYOUT)
            bar_layout["margin"] = dict(l=10, r=10, t=30, b=10)
            fig_county.update_layout(
                **bar_layout, title="Top 20 Counties", height=chart_config.height,
                showlegend=False, coloraxis_showscale=False,
                yaxis_title="", yaxis_automargin=True,
            )
            if is_rate:
                fig_county.update_xaxes(tickformat=".0%")
            st.plotly_chart(fig_county, use_container_width=True, key="county_bar")

        with col2:
            st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)
            s_vals = state_data[map_variable].dropna()
            w_avg = weighted_rate(state_data, map_variable) if len(s_vals) > 0 else np.nan
            stat_card("Weighted Average", fmt(w_avg), color="blue")
            stat_card("Minimum", fmt(s_vals.min()) if len(s_vals) > 0 else "N/A", color="green")
            stat_card("Maximum", fmt(s_vals.max()) if len(s_vals) > 0 else "N/A", color="red")
            stat_card("Std Deviation", fmt(s_vals.std()) if len(s_vals) > 1 else "N/A", color="purple")
            stat_card("Counties", f"{len(s_vals):,}", color="gray")


# ============================================================================
# TEMPORAL EVOLUTION (population-weighted)
# ============================================================================
section_header("Temporal Evolution", "How the selected variable changes over time", "clock")

nat_trend = weighted_rate_by_group(data, map_variable, "year").reset_index()
nat_trend.columns = ["Year", "Value"]

fig_time = go.Figure()
fig_time.add_trace(go.Scatter(
    x=nat_trend["Year"], y=nat_trend["Value"],
    mode="lines+markers",
    line=dict(color=COLORS["blue"], width=chart_config.line_width),
    marker=dict(size=chart_config.marker_size),
    fill="tozeroy", fillcolor="rgba(34,81,255,0.06)",
    name="National Average",
    hovertemplate="<b>%{x}</b><br>Value: %{y:.1%}<extra></extra>" if is_rate else "<b>%{x}</b><br>Value: %{y:,.2f}<extra></extra>",
))

if selected_state != "All States":
    state_time = data[data["state"] == selected_state]
    state_trend = weighted_rate_by_group(state_time, map_variable, "year").reset_index()
    state_trend.columns = ["Year", "Value"]
    fig_time.add_trace(go.Scatter(
        x=state_trend["Year"], y=state_trend["Value"],
        mode="lines+markers",
        line=dict(color=COLORS["rose"], width=chart_config.line_width, dash="dash"),
        marker=dict(size=chart_config.marker_size - 1),
        name=STATE_NAMES.get(selected_state, selected_state),
    ))

time_layout = dict(PLOTLY_LAYOUT)
time_layout.pop("title", None)
fig_time.update_layout(
    **time_layout, title="", height=chart_config.height,
    yaxis_title=get_variable_label(map_variable),
    xaxis_title="Year",
    yaxis_tickformat=".0%" if is_rate else "",
)
st.plotly_chart(fig_time, use_container_width=True, key="geo_temporal")


# ============================================================================
# DISTRIBUTION ANALYSIS
# ============================================================================
section_header("Distribution Analysis", f"County-level spread for {map_year}", "chart-area")

col_hist, col_box = st.columns(2)

with col_hist:
    n_counties = focus_data[map_variable].notna().sum()
    nbins = min(40, max(10, n_counties // 3))
    fig_hist = px.histogram(
        focus_data, x=map_variable, nbins=nbins,
        color_discrete_sequence=[COLORS["blue"]],
        labels={map_variable: get_variable_label(map_variable)},
    )
    hist_layout = dict(PLOTLY_LAYOUT)
    hist_layout["margin"] = dict(l=40, r=10, t=20, b=40)
    hist_layout.pop("title", None)
    fig_hist.update_layout(
        **hist_layout, title="Histogram", height=chart_config.height - 50,
        yaxis_title="County Count",
    )
    if is_rate:
        fig_hist.update_xaxes(tickformat=".0%")
    st.plotly_chart(fig_hist, use_container_width=True, key="geo_hist")

with col_box:
    # Always show all regions for comparison (not filtered by state)
    if "census_region" in year_data.columns:
        box_data = year_data.dropna(subset=[map_variable, "census_region"])
        fig_box = px.box(
            box_data,
            x="census_region", y=map_variable,
            color="census_region",
            color_discrete_sequence=[COLORS["blue"], COLORS["rose"],
                                     COLORS["teal"], COLORS["amber"]],
        )
        box_layout = dict(PLOTLY_LAYOUT)
        box_layout.pop("title", None)
        fig_box.update_layout(
            **box_layout, title="By Region (All States)", height=chart_config.height - 50,
            showlegend=False,
            xaxis_title="",
        )
        if is_rate:
            fig_box.update_yaxes(tickformat=".0%")
        st.plotly_chart(fig_box, use_container_width=True, key="geo_box")

st.markdown(
    '<div style="text-align:center;padding:1rem;color:#9ca3af;font-size:0.75rem;">'
    'Source: Feeding America Map the Meal Gap &bull; U.S. Census ACS</div>',
    unsafe_allow_html=True,
)
