"""
Policy Scenarios - Simulate intervention impacts on food insecurity.
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

# Sidebar
with st.sidebar:
    st.markdown('<p class="text-white font-semibold text-sm mb-2">Scenario Controls</p>', unsafe_allow_html=True)

    scenario_year = st.slider("Baseline Year", int(data["year"].min()), int(data["year"].max()),
                              int(data["year"].max()))

    st.markdown('<p class="text-white font-semibold text-sm mb-2 mt-4">Intervention Levers</p>', unsafe_allow_html=True)

    snap_increase = st.slider("SNAP Participation Increase (%)", 0, 50, 10)
    poverty_reduction = st.slider("Poverty Rate Reduction (%)", 0, 30, 5)
    income_boost = st.slider("Median Income Increase (%)", 0, 30, 5)
    unemployment_reduction = st.slider("Unemployment Reduction (%)", 0, 50, 10)

page_header("Policy Scenarios",
            "Simulate the impact of policy interventions on food insecurity", "landmark")

year_data = data[data["year"] == scenario_year].copy()

# Baseline metrics
baseline_fi = year_data["overall_food_insecurity_rate"].mean()
baseline_persons = year_data["no_of_food_insecure_persons_overall"].sum()
baseline_child = year_data["child_food_insecurity_rate"].mean()

# Simple scenario model: estimate impact based on correlations
# Using rough elasticities from literature
snap_effect = -0.003 * snap_increase  # ~0.3% FI reduction per 1% SNAP increase
poverty_effect = -0.005 * poverty_reduction  # FI closely tracks poverty
income_effect = -0.002 * income_boost  # Income effects
unemp_effect = -0.004 * unemployment_reduction  # Unemployment effects

total_effect = snap_effect + poverty_effect + income_effect + unemp_effect
projected_fi = max(0, baseline_fi + total_effect)
fi_change = projected_fi - baseline_fi
persons_change = fi_change * year_data["population"].sum()

kpi_row([
    {"title": "Baseline FI Rate", "value": f"{baseline_fi:.1%}", "icon": "chart-bar", "gradient": "coral"},
    {"title": "Projected FI Rate", "value": f"{projected_fi:.1%}", "icon": "bullseye", "gradient": "emerald"},
    {"title": "FI Reduction", "value": f"{abs(fi_change):.1%}", "icon": "arrow-down", "gradient": "sapphire"},
    {"title": "People Helped", "value": f"{abs(persons_change)/1e6:.1f}M", "icon": "hands-helping", "gradient": "amethyst"},
])

st.markdown("<div class='h-6'></div>", unsafe_allow_html=True)

# LLM Insight Engine
context_dict = {
    "Baseline Year": scenario_year,
    "Baseline FI Rate": f"{baseline_fi:.1%}",
    "Simulated SNAP Increase": f"+{snap_increase}%",
    "Simulated Poverty Reduction": f"-{poverty_reduction}%",
    "Simulated Income Boost": f"+{income_boost}%",
    "Simulated Unemployment Drop": f"-{unemployment_reduction}%",
    "Projected Output FI Rate": f"{projected_fi:.1%}",
    "Estimated People Helped": f"{abs(persons_change)/1e6:.1f}M" if abs(persons_change)>0 else "0"
}
llm_explainer_ui("Policy Scenarios", context_dict)

# --- IMPACT BREAKDOWN ---
section_header("Impact Breakdown", "Contribution of each policy lever", "puzzle-piece")

impact_data = pd.DataFrame({
    "Policy Lever": [
        f"SNAP +{snap_increase}%",
        f"Poverty -{poverty_reduction}%",
        f"Income +{income_boost}%",
        f"Unemployment -{unemployment_reduction}%",
    ],
    "FI Impact": [snap_effect, poverty_effect, income_effect, unemp_effect],
})
impact_data["Abs Impact"] = impact_data["FI Impact"].abs()

fig_impact = px.bar(
    impact_data, x="FI Impact", y="Policy Lever", orientation="h",
    color="FI Impact",
    color_continuous_scale=[[0, COLORS["emerald"]], [1, COLORS["sapphire"]]],
)
fig_impact.update_layout(
    **PLOTLY_LAYOUT, title="", height=300,
    showlegend=False, coloraxis_showscale=False,
    xaxis_title="Change in Food Insecurity Rate",
    xaxis_tickformat=".1%",
)
st.plotly_chart(fig_impact, width='stretch')

# --- SCENARIO COMPARISON ---
section_header("Scenario Comparison", icon="balance-scale-right")

scenarios = {
    "Baseline (No Change)": 0,
    "Modest Intervention": -0.01,
    "Moderate Intervention": -0.025,
    "Aggressive Intervention": -0.05,
    "Your Scenario": total_effect,
}

scenario_df = pd.DataFrame([
    {"Scenario": name, "Projected FI Rate": max(0, baseline_fi + effect)}
    for name, effect in scenarios.items()
])

fig_scenario = px.bar(
    scenario_df, x="Scenario", y="Projected FI Rate",
    color="Scenario",
    color_discrete_sequence=[COLORS["steel"], COLORS["amber"],
                             COLORS["sapphire"], COLORS["emerald"], COLORS["amethyst"]],
)
fig_scenario.update_layout(
    **PLOTLY_LAYOUT, title="", height=400,
    showlegend=False,
    yaxis_tickformat=".0%",
    yaxis_title="Projected Food Insecurity Rate",
)
fig_scenario.add_hline(y=baseline_fi, line_dash="dash", line_color=COLORS["ruby"],
                       annotation_text="Current Baseline")
st.plotly_chart(fig_scenario, width='stretch')

# --- STATE-LEVEL PROJECTIONS ---
section_header("State-Level Projections", icon="map")

state_baseline = (year_data.groupby("state", observed=True).agg(
    fi_rate=("overall_food_insecurity_rate", "mean"),
    population=("population", "sum"),
).reset_index())

state_baseline["Projected"] = (state_baseline["fi_rate"] + total_effect).clip(lower=0)
state_baseline["Reduction"] = state_baseline["fi_rate"] - state_baseline["Projected"]
state_baseline["People Helped"] = state_baseline["Reduction"] * state_baseline["population"]
state_baseline["State Name"] = state_baseline["state"].map(STATE_NAMES)

col1, col2 = st.columns(2)

with col1:
    fig_proj_map = px.choropleth(
        state_baseline, locations="state", locationmode="USA-states",
        color="Projected", scope="usa",
        color_continuous_scale=[COLORS["emerald"], COLORS["amber"], COLORS["ruby"]],
        hover_name="State Name",
        labels={"Projected": "Projected FI Rate"},
    )
    fig_proj_map.update_layout(
        **PLOTLY_LAYOUT, title="Projected FI Rate by State", height=450,
        geo=dict(bgcolor="rgba(0,0,0,0)"),
        coloraxis_colorbar=dict(tickformat=".0%"),
    )
    st.plotly_chart(fig_proj_map, width='stretch')

with col2:
    top_impact = state_baseline.nlargest(10, "People Helped")
    fig_top = px.bar(
        top_impact, x="People Helped", y="State Name", orientation="h",
        color_discrete_sequence=[COLORS["emerald"]],
    )
    fig_top.update_layout(
        **PLOTLY_LAYOUT, title="Top 10 States by People Helped", height=450,
    )
    fig_top.update_traces(
        hovertemplate="<b>%{y}</b><br>People Helped: %{x:,.0f}<extra></extra>",
    )
    st.plotly_chart(fig_top, width='stretch')

# --- COST ESTIMATION ---
section_header("Cost Estimation", icon="calculator")

info_banner(
    "Cost estimates are illustrative approximations based on published program costs. "
    "Actual costs depend on implementation details, administrative overhead, and local conditions.",
    "info",
)

snap_cost = snap_increase * 5e9 / 10  # ~$5B per 10% increase
income_cost = income_boost * 10e9 / 5  # ~$10B per 5%
unemp_cost = unemployment_reduction * 3e9 / 10  # ~$3B per 10%
poverty_cost = poverty_reduction * 8e9 / 5  # ~$8B per 5%
total_cost = snap_cost + income_cost + unemp_cost + poverty_cost

cost_per_person = total_cost / abs(persons_change) if persons_change != 0 else 0

col_c1, col_c2, col_c3 = st.columns(3)
with col_c1:
    stat_card("Total Estimated Cost", f"${total_cost/1e9:.1f}B", color="amber")
with col_c2:
    stat_card("Cost Per Person Helped", f"${cost_per_person:,.0f}", color="blue")
with col_c3:
    stat_card("Benefit-Cost Ratio",
              f"{abs(persons_change) / (total_cost / 1e6):.1f}" if total_cost > 0 else "N/A",
              "People helped per $1M invested", color="green")

# Methodology note
st.markdown(
    """
    <div class="bg-gray-50 rounded-2xl border border-gray-200 p-6 mt-6">
        <h3 class="text-sm font-bold text-gray-800 mb-3">
            <i class="fas fa-info-circle text-blue-500 mr-2"></i>Methodology Note
        </h3>
        <p class="text-gray-600 text-sm leading-relaxed">
            This scenario tool uses simplified elasticity estimates derived from published research
            on SNAP effectiveness, poverty-food insecurity linkages, and employment impacts.
            The model applies linear adjustments and does not capture interaction effects,
            diminishing returns, or implementation lag. Results should be interpreted as
            directional estimates for policy discussion, not precise forecasts.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
