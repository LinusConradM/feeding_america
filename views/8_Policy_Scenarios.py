"""
Policy Scenarios - Simulate intervention impacts on food insecurity.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from utils.theme import COLORS, PLOTLY_LAYOUT
from utils.components import kpi_row, section_header, stat_card, info_banner, llm_explainer_ui
from utils.data_loader import load_data, get_variable_label, STATE_NAMES

# inject_tailwind() is called globally in app.py — per-view call removed (Phase 3.D).
# page_header() replaced with section_header() below (Anomaly Detection template).

data = load_data()

# Clean data for DiD - drop na for our standard vars
did_vars = ["overall_food_insecurity_rate", "child_food_insecurity_rate", "poverty_rate", "snap_rate"]
clean_data = data.dropna(subset=did_vars + ["state", "year"]).copy()

# Sidebar
with st.sidebar:
    st.markdown('<p class="text-white font-semibold text-sm mb-2">Causal Inference (DiD) Controls</p>', unsafe_allow_html=True)

    treatment_state = st.selectbox(
        "Treatment State",
        sorted(clean_data["state"].unique().tolist()),
        index=sorted(clean_data["state"].unique().tolist()).index("CA") if "CA" in clean_data["state"].unique() else 0
    )
    
    intervention_year = st.slider(
        "Intervention Year", 
        int(clean_data["year"].min() + 1), 
        int(clean_data["year"].max() - 1),
        2020,
        help="The year the treatment state enacted the policy (e.g. Universal School Lunch programs)."
    )
    
    outcome_var = st.selectbox(
        "Outcome Variable",
        ["overall_food_insecurity_rate", "child_food_insecurity_rate"],
        format_func=get_variable_label
    )
    
    control_strategy = st.radio(
        "Control Group Strategy",
        ["National Average (Excl. Treatment)", "Synthetic Nearest Neighbors"],
        help="How to construct the baseline comparison group."
    )
    
    st.markdown('<p class="text-white font-semibold text-sm mb-2 mt-6">Predictive Scenario Controls</p>', unsafe_allow_html=True)

    scenario_year = st.slider("Baseline Year", int(data["year"].min()), int(data["year"].max()),
                              int(data["year"].max()))

    st.markdown('<p class="text-white font-semibold text-sm mb-2 mt-4">Intervention Levers</p>', unsafe_allow_html=True)

    snap_increase = st.slider("SNAP Participation Increase (%)", 0, 50, 10)
    poverty_reduction = st.slider("Poverty Rate Reduction (%)", 0, 30, 5)
    income_boost = st.slider("Median Income Increase (%)", 0, 30, 5)
    unemployment_reduction = st.slider("Unemployment Reduction (%)", 0, 50, 10)

st.title("Policy Scenarios")
st.caption("Causal Inference Engine using Difference-in-Differences (DiD)")

# --- DiD MODELING ---
with st.spinner("Constructing Control Group and running DiD Regression..."):
    # 1. Define Treatment Group
    clean_data['is_treated'] = (clean_data['state'] == treatment_state).astype(int)
    clean_data['post_intervention'] = (clean_data['year'] >= intervention_year).astype(int)
    clean_data['did_interaction'] = clean_data['post_intervention'] * clean_data['is_treated']
    
    # 2. Define Control Group
    if control_strategy.startswith("National"):
        model_data = clean_data.copy()
        control_label = "National Average"
    else:
        # Simple Synthetic Control (Nearest Neighbors on pre-intervention Poverty + SNAP)
        pre_treatment = clean_data[clean_data['year'] < intervention_year].groupby('state', observed=True)[['poverty_rate', 'snap_rate']].mean()
        target_profile = pre_treatment.loc[treatment_state]
        distances = ((pre_treatment - target_profile) ** 2).sum(axis=1)
        neighbors = distances.nsmallest(6).index.tolist()
        neighbors.remove(treatment_state) # Remove self
        model_data = clean_data[clean_data['state'].isin([treatment_state] + neighbors)].copy()
        control_label = f"Matched (Top 5 Peers)"
        
    # Standardize scale for regression printout
    model_data[outcome_var] = model_data[outcome_var] * 100 
    
    # 3. Run OLS
    try:
        mod = smf.ols(f"{outcome_var} ~ is_treated + post_intervention + did_interaction", data=model_data).fit()
        coeff = mod.params['did_interaction']
        p_val = mod.pvalues['did_interaction']
        
        # Determine significance formatting
        sig = "Significant" if p_val < 0.05 else "Not Significant"
        effect_color = "green" if coeff < 0 else "red"
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            stat_card("Causal ATET", f"{coeff:+.2f} pts", color=effect_color)
        with col2:
            stat_card("P-Value", f"{p_val:.3f}", color="blue" if p_val<0.05 else "gray")
        with col3:
            stat_card("Stat. Significance", sig, color="blue" if p_val<0.05 else "gray")
        with col4:
            stat_card("Observations", f"{len(model_data):,}", color="navy")
            
        st.markdown("<div class='h-4'></div>", unsafe_allow_html=True)
        
        # LLM Insight Engine
        context_dict = {
            "Treatment State": STATE_NAMES.get(treatment_state, treatment_state),
            "Intervention Year": intervention_year,
            "Control Group Concept": control_label,
            "Outcome Focus": get_variable_label(outcome_var),
            "Average Treatment Effect on Treated (ATET)": f"{coeff:+.2f} percentage points",
            "P-Value": f"{p_val:.3f}",
            "Statistical Conclusion": f"The policy had a {'significant' if p_val < 0.05 else 'statistically insignificant'} impact."
        }
        llm_explainer_ui("Causal Inference DiD", context_dict)
        
        # 4. Plot over time
        # Aggregate to state vs control per year
        yearly_means = model_data.groupby(['year', 'is_treated'], observed=True)[outcome_var].mean().reset_index()
        
        treated_trend = yearly_means[yearly_means['is_treated'] == 1]
        control_trend = yearly_means[yearly_means['is_treated'] == 0]
        
        fig = go.Figure()
        
        # Control Line
        fig.add_trace(go.Scatter(
            x=control_trend['year'], y=control_trend[outcome_var],
            mode='lines+markers',
            name=f"Control Group ({control_label})",
            line=dict(color=COLORS['slate'], width=3, dash='dash'),
            marker=dict(size=8, symbol='circle')
        ))
        
        # Treatment Line
        fig.add_trace(go.Scatter(
            x=treated_trend['year'], y=treated_trend[outcome_var],
            mode='lines+markers',
            name=f"Treatment State ({STATE_NAMES.get(treatment_state, treatment_state)})",
            line=dict(color=COLORS['sapphire'], width=4),
            marker=dict(size=10, symbol='diamond')
        ))
        
        # Intervention Line
        fig.add_vline(x=intervention_year - 0.5, line_width=2, line_dash="dash", line_color=COLORS['ruby'])
        fig.add_annotation(x=intervention_year - 0.5, y=treated_trend[outcome_var].max(),
                           text="Intervention", showarrow=False, xshift=40, font=dict(color=COLORS['ruby'], size=12))
        
        fig.update_layout(
            **PLOTLY_LAYOUT,
            title="Difference-in-Differences Longitudinal Trend",
            xaxis_title="Year",
            yaxis_title=f"{get_variable_label(outcome_var)} (%)",
            height=450,
        )
        fig.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0)
        )
        
        st.plotly_chart(fig, width='stretch')
        
        # Interpretation Block
        st.markdown(
            f"""
            <div class="bg-gray-50 rounded-2xl border border-gray-200 p-6 mt-6">
                <h3 class="text-sm font-bold text-gray-800 mb-3">
                    <i class="fas fa-microscope text-blue-500 mr-2"></i>Interpretation
                </h3>
                <p class="text-gray-600 text-sm leading-relaxed mb-4">
                    The Difference-in-Differences (DiD) model isolates the causal effect of an intervention by comparing the 
                    change in outcomes over time between a population enrolled in a program (the <b>treatment group</b>, {STATE_NAMES.get(treatment_state, treatment_state)}) 
                    and a population that is not (the <b>control group</b>, {control_label}).
                </p>
                <ul class="text-sm text-gray-600 space-y-2 list-disc ml-4">
                    <li><b>Baseline Shift:</b> Independent of the intervention, the control group saw outcomes shift post-{intervention_year}.</li>
                    <li><b>The Treatment Effect (ATET):</b> After subtracting this baseline shift, the unique causal impact attributable solely to the intervention in {treatment_state} was <b>{coeff:+.2f} percentage points</b>.</li>
                    <li><b>Confidence:</b> Because the p-value is {p_val:.3f} ({sig}), we {"can definitively conclude" if p_val < 0.05 else "cannot definitively conclude"} that the intervention caused a divergent shift from the control group beyond random statistical noise.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True
        )

    except Exception as e:
        st.error(f"Error computing DiD model: {e}")


# --- PREDICTIVE SCENARIO SIMULATIONS ---
st.markdown("<div class='h-8'></div>", unsafe_allow_html=True)
section_header("Predictive Policy Simulations", "Simulate the impact of hypothetical forward-looking interventions", "chart-pie")

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

# --- IMPACT BREAKDOWN ---
col1, col2 = st.columns(2)

with col1:
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
        color_continuous_scale=[[0, COLORS["teal"]], [1, COLORS["blue"]]],
    )
    fig_impact.update_layout(
        **PLOTLY_LAYOUT, title="Contribution Breakdown", height=300,
        showlegend=False, coloraxis_showscale=False,
        xaxis_title="Change in Food Insecurity Rate",
        xaxis_tickformat=".1%",
    )
    st.plotly_chart(fig_impact, width='stretch')

with col2:
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
                                 COLORS["blue"], COLORS["teal"], COLORS["violet"]],
    )
    fig_scenario.update_layout(
        **PLOTLY_LAYOUT, title="Magnitude Comparison", height=300,
        showlegend=False,
        yaxis_tickformat=".0%",
        yaxis_title="Projected Food Insecurity Rate",
    )
    fig_scenario.add_hline(y=baseline_fi, line_dash="dash", line_color=COLORS["rose"],
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
        color_continuous_scale=[COLORS["teal"], COLORS["amber"], COLORS["rose"]],
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
        color_discrete_sequence=[COLORS["teal"]],
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
            This predictive simulation tool uses simplified elasticity estimates derived from published research
            on SNAP effectiveness, poverty-food insecurity linkages, and employment impacts.
            The model applies linear adjustments and does not capture interaction effects,
            diminishing returns, or implementation lag. Results should be interpreted as
            directional estimates for policy discussion, not precise forecasts. Ensure empirical validation against the Difference-in-Differences history map above for true Causal Inference.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
