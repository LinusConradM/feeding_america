"""
Time Series Explorer - Temporal trends and pattern analysis.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import warnings
from statsmodels.tsa.statespace.sarimax import SARIMAX
from utils.theme import enforce_landscape_on_mobile, inject_tailwind, COLORS, PLOTLY_LAYOUT, SEQUENTIAL_COLORS, page_header
from utils.components import kpi_row, section_header, stat_card, llm_explainer_ui
from utils.data_loader import load_data, get_variable_label, STATE_NAMES


data = load_data()

# Sidebar
with st.sidebar:
    st.markdown('<p class="text-white font-semibold text-sm mb-2">Controls</p>', unsafe_allow_html=True)

    ts_variable = st.selectbox(
        "Variable",
        ["overall_food_insecurity_rate", "child_food_insecurity_rate",
         "poverty_rate", "unemployment_rate", "median_income", "cost_per_meal"],
        format_func=get_variable_label,
    )
    year_range = st.slider(
        "Year Range",
        int(data["year"].min()), int(data["year"].max()),
        (int(data["year"].min()), int(data["year"].max())),
    )
    compare_states = st.multiselect(
        "Compare States",
        sorted(data["state"].dropna().unique().tolist()),
        default=[],
    )

enforce_landscape_on_mobile()
page_header("Time Series Explorer",
            "Analyze temporal patterns and trends in food insecurity", "clock")

filtered = data[(data["year"] >= year_range[0]) & (data["year"] <= year_range[1])]
is_rate = "rate" in ts_variable

# --- PERIOD KPIs ---
period_data = filtered[ts_variable].dropna()
start_year_data = filtered[filtered["year"] == year_range[0]][ts_variable].dropna()
end_year_data = filtered[filtered["year"] == year_range[1]][ts_variable].dropna()

fmt_val = lambda v: f"{v:.1%}" if is_rate else f"${v:,.2f}" if "income" in ts_variable or "cost" in ts_variable else f"{v:,.0f}"

if len(start_year_data) > 0 and len(end_year_data) > 0:
    start_avg = start_year_data.mean()
    end_avg = end_year_data.mean()
    change = end_avg - start_avg
    pct_change = (change / start_avg * 100) if start_avg != 0 else 0

    kpi_row([
        {"title": f"Start ({year_range[0]})", "value": fmt_val(start_avg), "icon": "play", "gradient": "sapphire"},
        {"title": f"End ({year_range[1]})", "value": fmt_val(end_avg), "icon": "flag-checkered", "gradient": "navy"},
        {"title": "Change", "value": f"{pct_change:+.1f}%", "icon": "exchange-alt",
         "gradient": "emerald" if (is_rate and change < 0) or (not is_rate and "income" in ts_variable and change > 0) else "coral"},
        {"title": "Peak Year", "value": str(int(filtered.groupby("year", observed=True)[ts_variable].mean().idxmax())),
         "icon": "mountain", "gradient": "amethyst"},
    ])

st.markdown("<div class='h-6'></div>", unsafe_allow_html=True)

# LLM Insight Engine
context_dict = {
    "Variable": get_variable_label(ts_variable),
    "Date Range": f"{year_range[0]} - {year_range[1]}",
    "Start Average": fmt_val(start_avg) if len(start_year_data) > 0 else "N/A",
    "End Average": fmt_val(end_avg) if len(end_year_data) > 0 else "N/A",
    "Percent Change": f"{pct_change:+.1f}%" if len(start_year_data) > 0 else "N/A",
    "Filtered States": ", ".join(compare_states) if compare_states else "National (All States)"
}
llm_explainer_ui("Time Series Explorer", context_dict)

# --- NATIONAL TREND ---
section_header("National Trend", icon="chart-line")

nat_trend = filtered.groupby("year", observed=True)[ts_variable].agg(["mean", "median", "std"]).reset_index()
nat_trend.columns = ["Year", "Mean", "Median", "Std"]

fig_trend = go.Figure()

# Confidence band
fig_trend.add_trace(go.Scatter(
    x=list(nat_trend["Year"]) + list(nat_trend["Year"][::-1]),
    y=list(nat_trend["Mean"] + nat_trend["Std"]) + list((nat_trend["Mean"] - nat_trend["Std"])[::-1]),
    fill="toself", fillcolor="rgba(34,81,255,0.1)",
    line=dict(color="rgba(0,0,0,0)"),
    name="±1 Std Dev",
    hoverinfo="skip",
))

fig_trend.add_trace(go.Scatter(
    x=nat_trend["Year"], y=nat_trend["Mean"],
    mode="lines+markers",
    line=dict(color=COLORS["blue"], width=3),
    marker=dict(size=8),
    name="Mean",
))
fig_trend.add_trace(go.Scatter(
    x=nat_trend["Year"], y=nat_trend["Median"],
    mode="lines+markers",
    line=dict(color=COLORS["teal"], width=2, dash="dash"),
    marker=dict(size=6),
    name="Median",
))

# Event markers
fig_trend.add_vrect(x0=2009, x1=2010, fillcolor="rgba(192,57,43,0.08)", line_width=0,
                    annotation_text="Recession", annotation_position="top left")
fig_trend.add_vrect(x0=2020, x1=2021, fillcolor="rgba(192,57,43,0.08)", line_width=0,
                    annotation_text="COVID-19", annotation_position="top left")

fig_trend.update_layout(
    **PLOTLY_LAYOUT, title="", height=450,
    yaxis_title=get_variable_label(ts_variable),
    yaxis_tickformat=".0%" if is_rate else "",
)
st.plotly_chart(fig_trend, width='stretch')

# --- STATE COMPARISON ---
if compare_states:
    section_header("State Comparison", icon="flag-usa")

    state_trend = (filtered[filtered["state"].isin(compare_states)]
                   .groupby(["year", "state"])[ts_variable].mean().reset_index())
    state_trend["State Name"] = state_trend["state"].map(STATE_NAMES)

    fig_states = px.line(
        state_trend, x="year", y=ts_variable, color="State Name",
        markers=True,
        color_discrete_sequence=SEQUENTIAL_COLORS,
    )
    fig_states.update_layout(
        **PLOTLY_LAYOUT, title="", height=400,
        yaxis_title=get_variable_label(ts_variable),
        yaxis_tickformat=".0%" if is_rate else "",
        xaxis_title="Year",
    )
    st.plotly_chart(fig_states, width='stretch')

# --- REGIONAL TRENDS ---
section_header("Regional Trends", icon="globe-americas")

if "census_region" in filtered.columns:
    regional = (filtered.groupby(["year", "census_region"])[ts_variable]
                .mean().reset_index())
    regional = regional.dropna(subset=["census_region"])

    fig_reg = px.line(
        regional, x="year", y=ts_variable, color="census_region",
        markers=True,
        color_discrete_sequence=SEQUENTIAL_COLORS,
    )
    fig_reg.update_layout(
        **PLOTLY_LAYOUT, title="", height=400,
        yaxis_title=get_variable_label(ts_variable),
        yaxis_tickformat=".0%" if is_rate else "",
        legend_title="Region",
    )
    st.plotly_chart(fig_reg, width='stretch')

# --- PRE/POST COVID ANALYSIS ---
section_header("Pre/Post COVID-19 Comparison", icon="virus")

pre_covid = filtered[filtered["year"].between(2017, 2019)][ts_variable].dropna()
covid = filtered[filtered["year"].between(2020, 2021)][ts_variable].dropna()
post_covid = filtered[filtered["year"].between(2022, 2023)][ts_variable].dropna()

col1, col2, col3 = st.columns(3)
with col1:
    stat_card("Pre-COVID (2017-2019)", fmt_val(pre_covid.mean()) if len(pre_covid) > 0 else "N/A", color="blue")
with col2:
    stat_card("COVID (2020-2021)", fmt_val(covid.mean()) if len(covid) > 0 else "N/A", color="red")
with col3:
    stat_card("Post-COVID (2022-2023)", fmt_val(post_covid.mean()) if len(post_covid) > 0 else "N/A", color="green")

# --- YEAR-OVER-YEAR CHANGES ---
section_header("Year-over-Year Change", icon="exchange-alt")

yoy = filtered.groupby("year", observed=True)[ts_variable].mean().reset_index()
yoy["Change"] = yoy[ts_variable].pct_change(fill_method=None) * 100
yoy = yoy.dropna(subset=["Change"])

fig_yoy = go.Figure()
fig_yoy.add_trace(go.Bar(
    x=yoy["year"], y=yoy["Change"],
    marker_color=[COLORS["teal"] if c < 0 and is_rate else
                  COLORS["rose"] if c > 0 and is_rate else
                  COLORS["teal"] if c > 0 else COLORS["rose"]
                  for c in yoy["Change"]],
    hovertemplate="<b>%{x}</b><br>Change: %{y:+.1f}%<extra></extra>",
))
fig_yoy.update_layout(
    **PLOTLY_LAYOUT, title="", height=350,
    yaxis_title="% Change from Previous Year",
    xaxis_title="Year",
)
fig_yoy.add_hline(y=0, line_dash="dash", line_color=COLORS["silver"])
st.plotly_chart(fig_yoy, width='stretch')

# --- DISTRIBUTION EVOLUTION ---
section_header("Distribution Over Time", icon="chart-area")

# Select a few years for box comparison
sample_years = sorted(filtered["year"].unique())
if len(sample_years) > 6:
    step = max(1, len(sample_years) // 6)
    sample_years = sample_years[::step]

box_data = filtered[filtered["year"].isin(sample_years)]

fig_box = px.box(
    box_data, x="year", y=ts_variable,
    color="year",
    color_discrete_sequence=SEQUENTIAL_COLORS,
)
fig_box.update_layout(
    **PLOTLY_LAYOUT, title="", height=400,
    showlegend=False,
    yaxis_title=get_variable_label(ts_variable),
    yaxis_tickformat=".0%" if is_rate else "",
    xaxis_title="Year",
)
st.plotly_chart(fig_box, width='stretch')

# --- FORECASTING (SARIMAX) ---
section_header("Predictive Forecasting", "Projected 3-year forecast using SARIMAX statistical modeling", "chart-line")

st.markdown(
    '<p class="text-sm text-gray-600 mb-4">This module uses a Seasonal Auto-Regressive Integrated Moving Average (SARIMAX) model to project historical temporal data into the future, complete with 95% confidence intervals.</p>',
    unsafe_allow_html=True
)

target_data = None
forecast_name = ""

if compare_states:
    if len(compare_states) == 1:
        st_name = compare_states[0]
        target_data = filtered[filtered["state"] == st_name].groupby("year", observed=True)[ts_variable].mean().reset_index()
        forecast_name = STATE_NAMES.get(st_name, st_name)
    else:
        info_banner("Forecasting is disabled when comparing multiple states. Please clear the state comparison or select a single state.", "info")
else:
    target_data = nat_trend[["Year", "Mean"]].rename(columns={"Year": "year", "Mean": ts_variable})
    forecast_name = "National Average"

if target_data is not None and len(target_data) >= 10:
    target_data = target_data.sort_values("year").set_index("year")
    
    with st.spinner(f"Training SARIMAX model for {forecast_name}..."):
        try:
            # Suppress specific statsmodels index warnings for clean UI
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                
                # Fit standard ARIMA(1,1,0) - simplified for dashboard speed
                mod = SARIMAX(target_data[ts_variable], order=(1, 1, 0), enforce_stationarity=False, enforce_invertibility=False)
                res = mod.fit(disp=False)
                
                # Predict 3 years out
                forecast_steps = 3
                forecast = res.get_forecast(steps=forecast_steps)
                pred_mean = forecast.predicted_mean
                pred_ci = forecast.conf_int(alpha=0.05)
                
                last_year = target_data.index[-1]
                future_years = np.arange(last_year + 1, last_year + 1 + forecast_steps)
                
                # Create Forecast Figure
                fig_forecast = go.Figure()

                # Historical Data
                fig_forecast.add_trace(go.Scatter(
                    x=target_data.index, y=target_data[ts_variable],
                    mode="lines+markers",
                    line=dict(color=COLORS["blue"], width=3),
                    marker=dict(size=8),
                    name="Historical",
                    hovertemplate="<b>%{x}</b><br>Actual: %{y:.1%}<extra></extra>" if is_rate else "<b>%{x}</b><br>Actual: %{y:,.2f}<extra></extra>",
                ))

                # Confidence Interval Band
                fig_forecast.add_trace(go.Scatter(
                    x=list(future_years) + list(future_years)[::-1],
                    y=list(pred_ci.iloc[:, 1]) + list(pred_ci.iloc[:, 0])[::-1],
                    fill="toself",
                    fillcolor="rgba(231, 76, 60, 0.15)",
                    line=dict(color="rgba(255,255,255,0)"),
                    hoverinfo="skip",
                    name="95% Confidence Interval",
                ))

                # Forecast Line
                fig_forecast.add_trace(go.Scatter(
                    x=future_years, y=pred_mean,
                    mode="lines+markers",
                    line=dict(color=COLORS["rose"], width=3, dash="dot"),
                    marker=dict(size=8),
                    name="Forecast",
                    hovertemplate="<b>%{x}</b><br>Projected: %{y:.1%}<extra></extra>" if is_rate else "<b>%{x}</b><br>Projected: %{y:,.2f}<extra></extra>",
                ))

                # Connect last historical to first forecast
                fig_forecast.add_trace(go.Scatter(
                    x=[last_year, future_years[0]],
                    y=[target_data[ts_variable].iloc[-1], pred_mean.iloc[0]],
                    mode="lines",
                    line=dict(color=COLORS["rose"], width=3, dash="dot"),
                    showlegend=False,
                    hoverinfo="skip",
                ))

                fig_forecast.update_layout(
                    **PLOTLY_LAYOUT, title=f"3-Year Projection: {forecast_name}", height=450,
                    yaxis_title=get_variable_label(ts_variable),
                    xaxis_title="Year",
                    yaxis_tickformat=".0%" if is_rate else "",
                )
                
                st.plotly_chart(fig_forecast, width="stretch")
                
                # Metrics
                st.markdown("<div class='h-2'></div>", unsafe_allow_html=True)
                col1, col2, col3 = st.columns(3)
                
                end_hist = target_data[ts_variable].iloc[-1]
                end_proj = pred_mean.iloc[-1]
                proj_change = (end_proj - end_hist) / end_hist if end_hist != 0 else 0
                
                with col1:
                    stat_card(f"Current ({last_year})", fmt_val(end_hist), color="blue")
                with col2:
                    stat_card(f"Projected ({future_years[-1]})", fmt_val(end_proj), color="purple")
                with col3:
                    is_bad = (is_rate and proj_change > 0) or (not is_rate and "income" in ts_variable and proj_change < 0)
                    stat_card("Estimated Trajectory", f"{proj_change:+.1%}", color="red" if is_bad else "green")

        except Exception as e:
            st.error(f"Could not generate forecast: {e}")
elif target_data is not None:
    info_banner("Insufficient historical data to generate a reliable statistical forecast (minimum 10 years required).", "warning")

