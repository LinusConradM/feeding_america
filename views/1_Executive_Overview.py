"""
Executive Overview - National KPIs, trends, regional comparisons.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd
import numpy as np
from utils.theme import inject_tailwind, COLORS, PLOTLY_LAYOUT, SEQUENTIAL_COLORS, page_header
from utils.components import kpi_row, kpi_row_grouped, section_header, stat_card, llm_explainer_ui, hero_section, collapsible_section, geographic_section
from utils.data_loader import load_data, STATE_NAMES
from utils.responsive import get_viewport_profile
from utils.llm import explain_plot




data = load_data()
viewport = get_viewport_profile()
IS_MOBILE = viewport.is_mobile
IS_PORTRAIT = viewport.is_portrait


def layout_responsive(**kwargs):
    """Merge base Plotly layout with responsive overrides safely."""
    layout = dict(PLOTLY_LAYOUT)
    margin = kwargs.pop("margin", None)
    layout.update(kwargs)
    if margin:
        layout["margin"] = margin
    return layout

# Sidebar controls
with st.sidebar:
    st.markdown('<p class="text-white font-semibold text-sm mb-2">Filters</p>', unsafe_allow_html=True)
    selected_year = st.slider("Year", int(data["year"].min()), int(data["year"].max()),
                              int(data["year"].max()))

year_data = data[data["year"] == selected_year]
prev_data = data[data["year"] == selected_year - 1] if selected_year > data["year"].min() else None

page_header("Executive Overview", f"National food insecurity snapshot for {selected_year}", "chart-bar")


# --- KPI CALCULATIONS ---
def safe_pct_change(current, previous):
    if previous is None or previous == 0 or pd.isna(current) or pd.isna(previous):
        return ""
    change = ((current - previous) / previous) * 100
    sign = "+" if change > 0 else ""
    return f"{sign}{change:.1f}%"


# Calculate national metrics
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

# Store national metrics for comparison
national_fi_rate = fi_rate
national_fi_persons = fi_persons
national_child_fi = child_fi
national_cost_meal = cost_meal
national_poverty = poverty
national_med_income = med_income
national_unemp = unemp
national_shortfall = shortfall


def format_comparison(state_val, national_val, is_percentage=False):
    """Format comparison between state and national values."""
    if pd.isna(state_val) or pd.isna(national_val):
        return ""
    diff = state_val - national_val
    if is_percentage:
        return f"(National: {national_val:.1%})"
    else:
        return f"(National: {national_val:,.0f})"


# ============================================================================
# SECTION 1: HERO SECTION
# ============================================================================
section_header("Overview", f"National food insecurity for {selected_year}", "chart-bar")

# Generate contextual summary sentence
context_summary = ""
if prev_fi and pd.notna(prev_fi) and pd.notna(fi_rate):
    change = fi_rate - prev_fi
    change_pct = abs(change / prev_fi * 100)
    direction = "increased" if change > 0 else "decreased"
    context_summary = f"The national food insecurity rate has {direction} by {change_pct:.1f}% compared to {selected_year - 1}."
else:
    context_summary = f"National food insecurity data for {selected_year}."

# Render hero section component
from utils.components import hero_section
hero_section(
    year=selected_year,
    primary_metric=fi_rate if pd.notna(fi_rate) else 0.0,
    previous_metric=prev_fi if prev_fi and pd.notna(prev_fi) else None,
    context_summary=context_summary,
    show_quick_tips=True
)

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

# If a state is selected, recalculate metrics for that state
if st.session_state.get('selected_state'):
    state_code = st.session_state.selected_state
    state_year_data = year_data[year_data["state"] == state_code]
    state_prev_data = prev_data[prev_data["state"] == state_code] if prev_data is not None else None
    
    if not state_year_data.empty:
        # Recalculate metrics for selected state
        fi_rate = state_year_data["overall_food_insecurity_rate"].mean()
        fi_persons = state_year_data["no_of_food_insecure_persons_overall"].sum()
        child_fi = state_year_data["child_food_insecurity_rate"].mean()
        cost_meal = state_year_data["cost_per_meal"].mean()
        poverty = state_year_data["poverty_rate"].mean()
        med_income = state_year_data["median_income"].median()
        unemp = state_year_data["unemployment_rate"].mean()
        shortfall = state_year_data["weighted_annual_food_budget_shortfall"].mean()
        
        if state_prev_data is not None and not state_prev_data.empty:
            prev_fi = state_prev_data["overall_food_insecurity_rate"].mean()
            prev_persons = state_prev_data["no_of_food_insecure_persons_overall"].sum()
            prev_child = state_prev_data["child_food_insecurity_rate"].mean()
            prev_cost = state_prev_data["cost_per_meal"].mean()
            prev_poverty = state_prev_data["poverty_rate"].mean()
            prev_med_income = state_prev_data["median_income"].median()
            prev_unemp = state_prev_data["unemployment_rate"].mean()
            prev_shortfall = state_prev_data["weighted_annual_food_budget_shortfall"].mean()

# KPI Cards - Organized into two logical groups
# Update titles to show state name if selected
kpi_title_prefix = f"{STATE_NAMES.get(st.session_state.get('selected_state'), '')} " if st.session_state.get('selected_state') else "National "

kpi_row_grouped(
    row_groups=[
        {
            "title": "Core Food Insecurity Metrics",
            "cards": [
                {
                    "title": f"{kpi_title_prefix}FI Rate",
                    "value": f"{fi_rate:.1%}" if pd.notna(fi_rate) else "N/A",
                    "change": safe_pct_change(fi_rate, prev_fi) if not st.session_state.get('selected_state') else format_comparison(fi_rate, national_fi_rate, is_percentage=True),
                    "icon": "utensils",
                    "gradient": "coral",
                    "tooltip": "Percentage of the population experiencing food insecurity"
                },
                {
                    "title": "Food Insecure Persons",
                    "value": f"{fi_persons/1e6:.1f}M" if pd.notna(fi_persons) else "N/A",
                    "change": safe_pct_change(fi_persons, prev_persons) if not st.session_state.get('selected_state') else "",
                    "icon": "users",
                    "gradient": "navy",
                    "tooltip": "Total number of individuals facing food insecurity"
                },
                {
                    "title": f"{kpi_title_prefix}Child FI Rate",
                    "value": f"{child_fi:.1%}" if pd.notna(child_fi) else "N/A",
                    "change": safe_pct_change(child_fi, prev_child) if not st.session_state.get('selected_state') else format_comparison(child_fi, national_child_fi, is_percentage=True),
                    "icon": "child",
                    "gradient": "plum",
                    "tooltip": "Percentage of children under 18 experiencing food insecurity"
                },
                {
                    "title": "Cost Per Meal",
                    "value": f"${cost_meal:.2f}" if pd.notna(cost_meal) else "N/A",
                    "change": safe_pct_change(cost_meal, prev_cost) if not st.session_state.get('selected_state') else f"(National: ${national_cost_meal:.2f})",
                    "icon": "dollar-sign",
                    "gradient": "amber",
                    "tooltip": "Average cost to provide one meal to a food-insecure person"
                },
            ]
        },
        {
            "title": "Economic Drivers",
            "cards": [
                {
                    "title": "Poverty Rate",
                    "value": f"{poverty:.1%}" if pd.notna(poverty) else "N/A",
                    "change": safe_pct_change(poverty, prev_poverty) if not st.session_state.get('selected_state') else format_comparison(poverty, national_poverty, is_percentage=True),
                    "icon": "hand-holding-usd",
                    "gradient": "sapphire",
                    "tooltip": "Percentage of population living below the federal poverty line"
                },
                {
                    "title": "Median Income",
                    "value": f"${med_income:,.0f}" if pd.notna(med_income) else "N/A",
                    "change": safe_pct_change(med_income, prev_med_income) if not st.session_state.get('selected_state') else format_comparison(med_income, national_med_income),
                    "icon": "wallet",
                    "gradient": "emerald",
                    "tooltip": "Median household income across all counties"
                },
                {
                    "title": "Unemployment",
                    "value": f"{unemp:.1%}" if pd.notna(unemp) else "N/A",
                    "change": safe_pct_change(unemp, prev_unemp) if not st.session_state.get('selected_state') else format_comparison(unemp, national_unemp, is_percentage=True),
                    "icon": "briefcase",
                    "gradient": "coral",
                    "tooltip": "Percentage of labor force that is unemployed"
                },
                {
                    "title": "Budget Shortfall",
                    "value": f"${shortfall:,.0f}" if pd.notna(shortfall) else "N/A",
                    "change": safe_pct_change(shortfall, prev_shortfall),
                    "icon": "exclamation-triangle",
                    "gradient": "navy",
                    "tooltip": "Annual funding gap to meet food security needs"
                },
            ]
        }
    ],
    viewport_profile=viewport
)

st.markdown("<div class='gap-section'></div>", unsafe_allow_html=True)


# ============================================================================
# SECTION 2: STATE LOOKUP
# ============================================================================
section_header("State Lookup", "Find detailed metrics for a specific state", "search")

# Import state_lookup_component and StateSummary
from utils.components import state_lookup_component
from utils.responsive import StateSummary

# Initialize session state for selected state
if 'selected_state' not in st.session_state:
    st.session_state.selected_state = None

# Prepare state rankings for rank calculation
state_rankings = (year_data.groupby("state", observed=True)["overall_food_insecurity_rate"]
                  .mean().reset_index()
                  .sort_values("overall_food_insecurity_rate"))
state_rankings.columns = ["State", "FI Rate"]
state_rankings["Rank"] = range(1, len(state_rankings) + 1)

# Callback function to handle state selection
def on_state_select(state_code: str):
    """Handle state selection and display summary card."""
    # Store selected state in session state
    st.session_state.selected_state = state_code
    
    # Get state data
    state_data = year_data[year_data["state"] == state_code]
    
    if state_data.empty:
        st.warning(f"No data available for {STATE_NAMES.get(state_code, state_code)}")
        return
    
    # Calculate state metrics
    fi_rate = state_data["overall_food_insecurity_rate"].mean()
    food_insecure_persons = state_data["no_of_food_insecure_persons_overall"].sum()
    cost_per_meal = state_data["cost_per_meal"].mean()
    poverty_rate = state_data["poverty_rate"].mean()
    
    # Get rank from state_rankings
    rank_row = state_rankings[state_rankings["State"] == state_code]
    rank = int(rank_row["Rank"].iloc[0]) if not rank_row.empty else 0
    
    # Create StateSummary
    summary = StateSummary(
        state_code=state_code,
        state_name=STATE_NAMES.get(state_code, state_code),
        fi_rate=fi_rate if pd.notna(fi_rate) else 0.0,
        rank=rank,
        total_states=len(state_rankings),
        food_insecure_persons=int(food_insecure_persons) if pd.notna(food_insecure_persons) else 0,
        cost_per_meal=cost_per_meal if pd.notna(cost_per_meal) else 0.0,
        poverty_rate=poverty_rate if pd.notna(poverty_rate) else 0.0
    )
    
    # Display summary card
    display_dict = summary.to_display_dict()
    
    # Create a styled summary card
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
                    border: 2px solid #2251FF;
                    border-radius: 1rem;
                    padding: 1.5rem;
                    margin-top: 1rem;
                    margin-bottom: 1.5rem;
                    box-shadow: 0 4px 6px -1px rgba(34, 81, 255, 0.1);">
            <h3 style="color: #1E40AF; font-size: 1.25rem; font-weight: 700; 
                       margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
                <i class="fas fa-map-marker-alt"></i>
                {display_dict['State']}
            </h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); 
                        gap: 1rem;">
                <div>
                    <div style="color: #6B7280; font-size: 0.75rem; font-weight: 600; 
                               text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem;">
                        FI Rate
                    </div>
                    <div style="color: #1E40AF; font-size: 1.5rem; font-weight: 700;">
                        {display_dict['FI Rate']}
                    </div>
                </div>
                <div>
                    <div style="color: #6B7280; font-size: 0.75rem; font-weight: 600; 
                               text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem;">
                        Rank
                    </div>
                    <div style="color: #1E40AF; font-size: 1.5rem; font-weight: 700;">
                        {display_dict['Rank']}
                    </div>
                </div>
                <div>
                    <div style="color: #6B7280; font-size: 0.75rem; font-weight: 600; 
                               text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem;">
                        Food Insecure
                    </div>
                    <div style="color: #1E40AF; font-size: 1.5rem; font-weight: 700;">
                        {display_dict['Food Insecure']}
                    </div>
                </div>
                <div>
                    <div style="color: #6B7280; font-size: 0.75rem; font-weight: 600; 
                               text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem;">
                        Cost/Meal
                    </div>
                    <div style="color: #1E40AF; font-size: 1.5rem; font-weight: 700;">
                        {display_dict['Cost/Meal']}
                    </div>
                </div>
                <div>
                    <div style="color: #6B7280; font-size: 0.75rem; font-weight: 600; 
                               text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem;">
                        Poverty Rate
                    </div>
                    <div style="color: #1E40AF; font-size: 1.5rem; font-weight: 700;">
                        {display_dict['Poverty']}
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Render state lookup component
selected_state = state_lookup_component(
    year_data=year_data,
    state_names=STATE_NAMES,
    on_state_select=on_state_select
)

# Add Clear Selection button if a state is selected
if st.session_state.selected_state:
    if st.button("🔄 Clear Selection - Return to National View", type="secondary"):
        st.session_state.selected_state = None
        st.rerun()

st.markdown("<div class='gap-section'></div>", unsafe_allow_html=True)


# ============================================================================
# SECTION 3: NATIONAL TREND CHART
# ============================================================================
section_header("National Trend (2009-2023)", "Average food insecurity rate over time", "chart-line")

# Get viewport-specific chart configuration
from utils.responsive import ChartConfig
chart_config = ChartConfig.for_viewport(viewport)

# Prepare trend data
trend = data.groupby("year", observed=True)["overall_food_insecurity_rate"].mean().reset_index()
trend.columns = ["Year", "FI Rate"]

# Apply data point reduction for mobile viewports (30% reduction = keep 70%)
if chart_config.data_point_reduction < 1.0:
    # Calculate number of points to keep
    total_points = len(trend)
    points_to_keep = int(total_points * chart_config.data_point_reduction)
    # Sample evenly across the range
    indices = np.linspace(0, total_points - 1, points_to_keep, dtype=int)
    trend = trend.iloc[indices].reset_index(drop=True)

fig_trend = go.Figure()
fill_color = "rgba(34, 81, 255, 0.05)" if IS_MOBILE else "rgba(34, 81, 255, 0.08)"

# Add national trend line
fig_trend.add_trace(go.Scatter(
    x=trend["Year"], y=trend["FI Rate"],
    mode="lines+markers",
    line=dict(color=COLORS["blue"], width=chart_config.line_width),
    marker=dict(size=chart_config.marker_size, color=COLORS["blue"]),
    fill="tozeroy",
    fillcolor=fill_color,
    name="National Average",
    hovertemplate="<b>%{x}</b><br>National FI Rate: %{y:.1%}<extra></extra>",
))

# Add state-specific trend line if a state is selected
if st.session_state.selected_state:
    state_trend = data[data["state"] == st.session_state.selected_state].groupby("year", observed=True)["overall_food_insecurity_rate"].mean().reset_index()
    state_trend.columns = ["Year", "FI Rate"]
    
    # Apply same data point reduction for mobile
    if chart_config.data_point_reduction < 1.0:
        total_points = len(state_trend)
        points_to_keep = int(total_points * chart_config.data_point_reduction)
        indices = np.linspace(0, total_points - 1, points_to_keep, dtype=int)
        state_trend = state_trend.iloc[indices].reset_index(drop=True)
    
    state_name = STATE_NAMES.get(st.session_state.selected_state, st.session_state.selected_state)
    fig_trend.add_trace(go.Scatter(
        x=state_trend["Year"], y=state_trend["FI Rate"],
        mode="lines+markers",
        line=dict(color=COLORS["rose"], width=chart_config.line_width, dash="dot"),
        marker=dict(size=chart_config.marker_size, color=COLORS["rose"]),
        name=f"{state_name}",
        hovertemplate=f"<b>%{{x}}</b><br>{state_name} FI Rate: %{{y:.1%}}<extra></extra>",
    ))

# Add recession/COVID bands
fig_trend.add_vrect(x0=2009, x1=2010, fillcolor="rgba(192,57,43,0.08)",
                    line_width=0, annotation_text="Recession", annotation_position="top left")
fig_trend.add_vrect(x0=2020, x1=2021, fillcolor="rgba(192,57,43,0.08)",
                    line_width=0, annotation_text="COVID-19", annotation_position="top left")

# Apply responsive tick spacing
dtick = 2 if IS_MOBILE else None

layout_kwargs = dict(PLOTLY_LAYOUT)
layout_kwargs["margin"] = chart_config.margin

fig_trend.update_layout(
    **layout_kwargs,
    title="",
    yaxis_title="Food Insecurity Rate",
    xaxis_title="Year",
    yaxis_tickformat=".0%",
    height=chart_config.height,
    showlegend=chart_config.show_legend or st.session_state.selected_state is not None,
)
fig_trend.update_xaxes(dtick=dtick)
trend_context = {
    "Years covered": f"{int(trend['Year'].min())}-{int(trend['Year'].max())}",
    "Latest rate": f"{trend['FI Rate'].iloc[-1]:.1%}",
    "Change since start": f"{(trend['FI Rate'].iloc[-1] - trend['FI Rate'].iloc[0]):+.1%}",
    "Max year": int(trend["Year"].max()),
}
trend_explainer = explain_plot("National Food Insecurity Trend (2009-2023)", trend_context)

# Render plot + hover explainer as a custom HTML block so hover reveals card
trend_div = pio.to_html(
    fig_trend,
    include_plotlyjs="cdn",
    full_html=False,
    config={"responsive": True, "displayModeBar": False},
)

overlay_css = """
<style>
.trend-wrap {
    position: relative;
    width: 100%;
    height: auto;
    margin-bottom: var(--space-4);
}
.trend-wrap .plotly-graph-div {
    width: 100% !important;
}
.trend-explainer {
    position: absolute;
    top: -20px;
    right: 12px;
    max-width: 440px;
    background: rgba(26, 35, 126, 0.9);
    color: #ffffff;
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 14px 32px rgba(0,0,0,0.38), 0 0 0 1px rgba(255,255,255,0.12);
    opacity: 0;
    visibility: hidden;
    transform: translateY(-8px);
    transition: opacity 0.18s ease, transform 0.18s ease;
    pointer-events: none;
    border: 1px solid rgba(255, 255, 255, 0.16);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    z-index: 5;
}
.trend-explainer::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, rgba(255,255,255,0.14), rgba(255,255,255,0.08));
    border-radius: 14px 14px 0 0;
}
.trend-wrap:hover .trend-explainer {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
    pointer-events: auto;
}
.trend-explainer h4 {
    margin: 0 0 8px 0;
    font-size: 1.05rem;
    font-weight: 800;
    letter-spacing: 0.01em;
    color: #e5eaff;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.trend-explainer ul {
    margin: 0;
    padding-left: 1rem;
    font-size: 0.95rem;
    line-height: 1.6;
    color: #f2f4ff;
}
.trend-icon {
    width: 32px;
    height: 32px;
    border-radius: 10px;
    background: linear-gradient(135deg, #a78bfa 0%, #8b5cf6 100%);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: #0d1024;
    font-size: 1rem;
    box-shadow: 0 10px 20px rgba(167,139,250,0.35);
}
@media (max-width: 768px) {
    .trend-explainer {
        left: 8px;
        right: 8px;
        top: -40px;
        bottom: auto;
        max-width: unset;
    }
    .trend-wrap {
        margin-bottom: var(--space-3);
    }
}
</style>
"""
trend_html = f"""
{overlay_css}
<div class="trend-wrap">
  {trend_div}
  <div class="trend-explainer">
    <p style="margin:0;font-size:1.02rem;line-height:1.55;color:#f8fafc;">
      {trend_explainer.replace(chr(10), ' ')}
    </p>
  </div>
</div>
"""

st.components.v1.html(trend_html, height=chart_config.height + 40)


# ============================================================================
# SECTION 3: GEOGRAPHIC SECTION
# ============================================================================
section_header("Geographic Analysis", "Spatial patterns of food insecurity", "map")

# Render consolidated geographic section with state map, regional comparison, and urban/rural comparison
geographic_section(year_data, selected_year, viewport, selected_state=st.session_state.get('selected_state'))

st.markdown("<div class='gap-section'></div>", unsafe_allow_html=True)


# ============================================================================
# SECTION 4: STATE RANKINGS
# ============================================================================

# Prepare state rankings data
state_avg = (year_data.groupby("state", observed=True)["overall_food_insecurity_rate"]
             .mean().reset_index()
             .sort_values("overall_food_insecurity_rate"))
state_avg.columns = ["State", "FI Rate"]
state_avg["State Name"] = state_avg["State"].map(STATE_NAMES)

def render_state_rankings():
    """Render state rankings content with responsive layout."""
    # Responsive layout: 2 columns for desktop/tablet, 1 column for mobile
    if IS_MOBILE:
        # Mobile: 1-column layout (top 10 above bottom 10)
        st.markdown(
            '<div class="bg-emerald-50 border border-emerald-200 rounded-xl p-4 mb-3">'
            '<h3 class="text-emerald-800 font-bold text-sm">Top 10 - Lowest Food Insecurity</h3></div>',
            unsafe_allow_html=True,
        )
        top10 = state_avg.head(10).copy()
        top10["Rank"] = range(1, 11)
        top10["FI Rate"] = top10["FI Rate"].apply(lambda x: f"{x:.1%}")
        st.dataframe(top10[["Rank", "State Name", "FI Rate"]], width='stretch', hide_index=True)
        
        st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
        
        st.markdown(
            '<div class="bg-red-50 border border-red-200 rounded-xl p-4 mb-3">'
            '<h3 class="text-red-800 font-bold text-sm">Bottom 10 - Highest Food Insecurity</h3></div>',
            unsafe_allow_html=True,
        )
        bot10 = state_avg.tail(10).iloc[::-1].copy()
        bot10["Rank"] = range(1, 11)
        bot10["FI Rate"] = bot10["FI Rate"].apply(lambda x: f"{x:.1%}")
        st.dataframe(bot10[["Rank", "State Name", "FI Rate"]], width='stretch', hide_index=True)
    else:
        # Desktop/Tablet: 2-column layout (top 10 | bottom 10)
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

# Wrap in collapsible section, default to expanded
collapsible_section(
    title="State Rankings",
    content_func=render_state_rankings,
    icon="trophy",
    default_expanded=True,
    key="state_rankings"
)

st.markdown("<div class='gap-section'></div>", unsafe_allow_html=True)


# ============================================================================
# SECTION 5: STATISTICAL DETAILS
# ============================================================================

def render_statistical_details():
    """Render statistical details content."""
    fi_vals = year_data["overall_food_insecurity_rate"].dropna()
    cards = [
        ("Median FI Rate", f"{fi_vals.median():.1%}", "#2251FF", "#eef4ff"),
        ("Std Deviation", f"{fi_vals.std():.1%}", "#7C3AED", "#f8efff"),
        ("Range", f"{fi_vals.min():.1%} - {fi_vals.max():.1%}", "#B45309", "#fff8e6"),
        ("Above Average", f"{(fi_vals > fi_vals.mean()).sum():,} counties", "#B91C1C", "#fff1f1"),
    ]
    stat_cards_html = """
<style>
.stat-grid { display:grid; grid-template-columns: repeat(2,minmax(0,1fr)); gap:14px; }
@media (max-width: 820px) { .stat-grid { gap:12px; } }
@media (max-width: 580px) { .stat-grid { gap:10px; } }
.stat-card-box {
    border-radius:16px; padding:1.05rem 0.9rem;
    text-align:center; box-shadow:0 1px 4px rgba(0,0,0,0.04);
    border:1px solid rgba(0,0,0,0.04); height:100%;
}
.stat-card-title {
    font-size:0.78rem; font-weight:700; letter-spacing:0.04em;
    color:#6B7280; margin-bottom:0.35rem; text-transform:uppercase;
}
.stat-card-value {
    font-size:1.35rem; font-weight:800; margin:0;
}
</style>
<div class="stat-grid">
"""
    for title, value, fg, bg in cards:
        stat_cards_html += f"""
<div class="stat-card-box" style="background:{bg};">
    <div class="stat-card-title">{title}</div>
    <div class="stat-card-value" style="color:{fg};">{value}</div>
</div>
"""
    stat_cards_html += "</div>"
    st.markdown(stat_cards_html, unsafe_allow_html=True)

collapsible_section(
    title="Statistical Details",
    content_func=render_statistical_details,
    icon="calculator",
    default_expanded=True,
    key="statistical_details"
)

# Footer
st.markdown(
    '<div class="text-center py-4 text-gray-400 text-xs">'
    'Source: Feeding America Map the Meal Gap &bull; U.S. Census ACS</div>',
    unsafe_allow_html=True,
)
