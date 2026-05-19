"""
Executive Overview - National KPIs, trends, regional comparisons.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd
import numpy as np
from utils.theme import COLORS, PLOTLY_LAYOUT
from utils.components import kpi_row_grouped, section_header, llm_explainer_ui, collapsible_section, geographic_section
from utils.data_loader import load_data, STATE_NAMES, weighted_rate, weighted_rate_by_group
from utils.responsive import get_viewport_profile
from utils.llm import explain_plot


data = load_data()
viewport = get_viewport_profile()
IS_MOBILE = viewport.is_mobile
IS_PORTRAIT = viewport.is_portrait

# Sidebar controls
with st.sidebar:
    # Clean Home button
    if st.button("🏠 Home", use_container_width=True, type="primary"):
        st.switch_page("views/home.py")
    
    st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
    
    st.markdown('<p class="text-white font-semibold text-sm mb-2">Data Selectors</p>', unsafe_allow_html=True)
    selected_year = st.slider("Year", int(data["year"].min()), int(data["year"].max()),
                              int(data["year"].max()))

year_data = data[data["year"] == selected_year]
prev_data = data[data["year"] == selected_year - 1] if selected_year > data["year"].min() else None


# --- KPI CALCULATIONS ---
def safe_pct_change(current, previous):
    if previous is None or previous == 0 or pd.isna(current) or pd.isna(previous):
        return ""
    change = ((current - previous) / previous) * 100
    sign = "+" if change > 0 else ""
    return f"{sign}{change:.1f}%"


# Calculate national metrics (population-weighted for rates)
def calc_metrics(df):
    """Calculate all KPI metrics from a DataFrame, using population-weighted means for rates."""
    # SNAP rate may not exist in all year ranges
    snap = weighted_rate(df, "snap_rate") if "snap_rate" in df.columns and df["snap_rate"].notna().any() else np.nan
    rent = weighted_rate(df, "rent_burden") if "rent_burden" in df.columns and df["rent_burden"].notna().any() else np.nan
    fi_children = df["no_of_food_insecure_children"].sum() if "no_of_food_insecure_children" in df.columns else np.nan
    return {
        "fi_rate": weighted_rate(df, "overall_food_insecurity_rate"),
        "fi_persons": df["no_of_food_insecure_persons_overall"].sum(),
        "child_fi": weighted_rate(df, "child_food_insecurity_rate"),
        "fi_children": fi_children,
        "cost_meal": weighted_rate(df, "cost_per_meal"),
        "poverty": weighted_rate(df, "poverty_rate"),
        "med_income": df["median_income"].median(),
        "unemp": weighted_rate(df, "unemployment_rate"),
        "shortfall": weighted_rate(df, "weighted_annual_food_budget_shortfall"),
        "snap_rate": snap,
        "rent_burden": rent,
    }

m = calc_metrics(year_data)
fi_rate, fi_persons, child_fi = m["fi_rate"], m["fi_persons"], m["child_fi"]
fi_children = m["fi_children"]
cost_meal, poverty, med_income = m["cost_meal"], m["poverty"], m["med_income"]
unemp, shortfall = m["unemp"], m["shortfall"]
snap_rate, rent_burden = m["snap_rate"], m["rent_burden"]

if prev_data is not None:
    pm = calc_metrics(prev_data)
    prev_fi, prev_persons, prev_child = pm["fi_rate"], pm["fi_persons"], pm["child_fi"]
    prev_fi_children = pm["fi_children"]
    prev_cost, prev_poverty, prev_med_income = pm["cost_meal"], pm["poverty"], pm["med_income"]
    prev_unemp, prev_shortfall = pm["unemp"], pm["shortfall"]
    prev_snap, prev_rent = pm["snap_rate"], pm["rent_burden"]
else:
    prev_fi = prev_persons = prev_child = prev_fi_children = prev_cost = None
    prev_poverty = prev_med_income = prev_unemp = prev_shortfall = None
    prev_snap = prev_rent = None

# Store national metrics for comparison
national_fi_rate = fi_rate
national_fi_persons = fi_persons
national_child_fi = child_fi
national_fi_children = fi_children
national_cost_meal = cost_meal
national_poverty = poverty
national_med_income = med_income
national_unemp = unemp
national_shortfall = shortfall
national_snap = snap_rate
national_rent = rent_burden


def format_comparison(state_val, national_val, is_percentage=False):
    """Format comparison between state and national values."""
    if pd.isna(state_val) or pd.isna(national_val):
        return ""
    diff = state_val - national_val
    if is_percentage:
        return f"(National: {national_val:.1%})"
    else:
        return f"(National: {national_val:,.0f})"


# ── Page Header ───────────────────────────────────────────────────────────────
st.markdown(f"""
<div role="banner" aria-label="Executive Overview header"
     style="text-align:center;padding:1.5rem 1rem 1rem;margin-bottom:1.5rem;
            border-bottom:2px solid {COLORS['pearl']};">
    <h1 style="font-family:Georgia,serif;color:{COLORS['ink']};font-size:clamp(2rem,5vw,3rem);
               font-weight:800;line-height:1.1;margin:0 0 0.25rem 0;letter-spacing:-0.02em">
        Executive Overview
    </h1>
    <p style="font-family:Georgia,serif;color:{COLORS['slate']};
              font-size:clamp(1.1rem,3vw,1.5rem);font-weight:600;
              line-height:1.2;margin:0 0 1rem 0">
        Where Hunger Persists — and Why
    </p>
    <p style="font-family:Inter,sans-serif;color:{COLORS['steel']};font-size:clamp(0.9rem,1.8vw,1.05rem);
              line-height:1.6;max-width:700px;margin:0 auto">
        Investigating patterns, disparities, and socioeconomic drivers of food insecurity across
        <strong style="color:{COLORS['ink']}">3,100+ U.S. counties</strong> — 15 years of longitudinal data,
        built for policymakers, researchers, and practitioners.
    </p>
</div>
""", unsafe_allow_html=True)

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
        sm = calc_metrics(state_year_data)
        fi_rate, fi_persons, child_fi = sm["fi_rate"], sm["fi_persons"], sm["child_fi"]
        fi_children = sm["fi_children"]
        cost_meal, poverty, med_income = sm["cost_meal"], sm["poverty"], sm["med_income"]
        unemp, shortfall = sm["unemp"], sm["shortfall"]
        snap_rate, rent_burden = sm["snap_rate"], sm["rent_burden"]

        if state_prev_data is not None and not state_prev_data.empty:
            spm = calc_metrics(state_prev_data)
            prev_fi, prev_persons, prev_child = spm["fi_rate"], spm["fi_persons"], spm["child_fi"]
            prev_fi_children = spm["fi_children"]
            prev_cost, prev_poverty, prev_med_income = spm["cost_meal"], spm["poverty"], spm["med_income"]
            prev_unemp, prev_shortfall = spm["unemp"], spm["shortfall"]
            prev_snap, prev_rent = spm["snap_rate"], spm["rent_burden"]

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
                    "title": "Food Insecure Children",
                    "value": f"{fi_children/1e6:.1f}M" if pd.notna(fi_children) and fi_children > 0 else "N/A",
                    "change": safe_pct_change(fi_children, prev_fi_children) if not st.session_state.get('selected_state') else "",
                    "icon": "child",
                    "gradient": "coral",
                    "tooltip": "Total number of children under 18 experiencing food insecurity"
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
                    "title": "SNAP Rate",
                    "value": f"{snap_rate:.1%}" if pd.notna(snap_rate) else "N/A",
                    "change": safe_pct_change(snap_rate, prev_snap) if not st.session_state.get('selected_state') else format_comparison(snap_rate, national_snap, is_percentage=True),
                    "icon": "id-card",
                    "gradient": "navy",
                    "tooltip": "SNAP (food stamps) participation rate"
                },
                {
                    "title": "Rent Burden",
                    "value": f"{rent_burden:.1%}" if pd.notna(rent_burden) else "N/A",
                    "change": safe_pct_change(rent_burden, prev_rent) if not st.session_state.get('selected_state') else format_comparison(rent_burden, national_rent, is_percentage=True),
                    "icon": "home",
                    "gradient": "coral",
                    "tooltip": "Share of households spending 30%+ of income on rent"
                },
            ]
        }
    ],
    viewport_profile=viewport
)

st.markdown("<div class='gap-section'></div>", unsafe_allow_html=True)


# ============================================================================
# DS-8: COUNTIES IN CRISIS CALLOUT
# ============================================================================
if "fi_category" in year_data.columns:
    crisis_counts = year_data["fi_category"].value_counts()
    very_high = int(crisis_counts.get("Very High", 0))
    high = int(crisis_counts.get("High", 0))
    total_counties = len(year_data)
    if very_high > 0 or high > 0:
        # Top 5 worst counties
        worst_5 = year_data.nlargest(5, "overall_food_insecurity_rate")[["county", "state", "overall_food_insecurity_rate"]]
        worst_list = " &bull; ".join(
            f"<strong>{r['county']}, {r['state']}</strong> ({r['overall_food_insecurity_rate']:.1%})"
            for _, r in worst_5.iterrows()
        )
        crisis_html = f"""
        <div role="alert" aria-label="Counties in crisis"
             style="background:linear-gradient(135deg, #1a0000 0%, #3b0d0d 100%);
                    border:1px solid {COLORS['ruby']};border-radius:1rem;padding:1.5rem 2rem;
                    margin-bottom:1.5rem;box-shadow:0 4px 12px rgba(214,48,49,0.15);">
            <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.75rem;">
                <span style="font-size:1.5rem;">&#9888;</span>
                <h3 style="font-family:Georgia,serif;color:{COLORS['white']};font-size:1.15rem;font-weight:700;margin:0;">
                    Counties in Crisis ({selected_year})
                </h3>
            </div>
            <div style="display:flex;gap:2rem;margin-bottom:0.75rem;flex-wrap:wrap;">
                <div>
                    <span style="font-family:Georgia,serif;font-size:1.8rem;font-weight:800;color:{COLORS['ruby']};">{very_high:,}</span>
                    <span style="color:rgba(255,255,255,0.6);font-size:0.875rem;margin-left:0.4rem;">Very High (&gt;20%)</span>
                </div>
                <div>
                    <span style="font-family:Georgia,serif;font-size:1.8rem;font-weight:800;color:{COLORS['amber']};">{high:,}</span>
                    <span style="color:rgba(255,255,255,0.6);font-size:0.875rem;margin-left:0.4rem;">High (15-20%)</span>
                </div>
                <div>
                    <span style="font-family:Georgia,serif;font-size:1.8rem;font-weight:800;color:rgba(255,255,255,0.4);">{total_counties - very_high - high:,}</span>
                    <span style="color:rgba(255,255,255,0.6);font-size:0.875rem;margin-left:0.4rem;">Below 15%</span>
                </div>
            </div>
            <p style="color:rgba(255,255,255,0.5);font-size:0.85rem;margin:0;">
                <strong style="color:rgba(255,255,255,0.7);">Worst 5:</strong> {worst_list}
            </p>
        </div>
        """
        st.markdown(crisis_html, unsafe_allow_html=True)


# ============================================================================
# DS-5: DISPARITY SNAPSHOT
# ============================================================================
def _render_disparity_snapshot():
    """Render Gini, Urban-Rural gap, and Racial FI gap as compact cards."""
    items = []
    # Gini
    if "gini" in year_data.columns and year_data["gini"].notna().any():
        gini_val = weighted_rate(year_data, "gini")
        items.append(("Gini Coefficient", f"{gini_val:.3f}", COLORS["amethyst"], "Income inequality index (0=equal, 1=unequal)"))
    # Urban-Rural gap
    if "urban_rural" in year_data.columns:
        rural = year_data[year_data["urban_rural"] == "Rural"]
        urban = year_data[year_data["urban_rural"] == "Urban"]
        if not rural.empty and not urban.empty:
            rural_fi = weighted_rate(rural, "overall_food_insecurity_rate")
            urban_fi = weighted_rate(urban, "overall_food_insecurity_rate")
            gap = rural_fi - urban_fi
            items.append(("Rural-Urban Gap", f"{gap:+.1%}", COLORS["sapphire"], "FI rate difference: rural minus urban counties"))
    # Racial gap (post-2019 data)
    black_col = "food_insecurity_rate_among_black_persons_all_ethnicities"
    white_col = "food_insecurity_rate_among_white_non_hispanic_persons"
    if black_col in year_data.columns and white_col in year_data.columns:
        b = year_data[black_col].dropna()
        w = year_data[white_col].dropna()
        if len(b) > 50 and len(w) > 50:
            racial_gap = b.mean() - w.mean()
            items.append(("Black-White FI Gap", f"{racial_gap:+.1%}", COLORS["ruby"], "FI rate difference between Black and White populations"))

    if items:
        section_header("Disparity Snapshot", f"Inequality indicators for {selected_year}", "balance-scale")
        cols = st.columns(len(items))
        for col, (label, value, color, tip) in zip(cols, items):
            with col:
                st.markdown(
                    f"""<div style="background:{COLORS['snow']};border-radius:1rem;padding:1.2rem;text-align:center;
                                   border-left:4px solid {color};min-height:100px;" title="{tip}">
                        <div style="font-family:Inter,sans-serif;font-size:0.875rem;font-weight:600;color:{COLORS['slate']};
                                   text-transform:uppercase;letter-spacing:0.04em;margin-bottom:0.4rem;">{label}</div>
                        <div style="font-family:Georgia,serif;font-size:1.8rem;font-weight:800;color:{color};">{value}</div>
                    </div>""",
                    unsafe_allow_html=True
                )
        st.markdown("<div class='gap-section'></div>", unsafe_allow_html=True)

_render_disparity_snapshot()


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

# Prepare state rankings (population-weighted) — reused in rankings section below
state_rankings = weighted_rate_by_group(year_data, "overall_food_insecurity_rate", "state").reset_index()
state_rankings.columns = ["State", "FI Rate"]
state_rankings = state_rankings.sort_values("FI Rate")
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
    
    # Create a styled summary card using COLORS tokens
    card_metrics = [
        ("FI Rate", display_dict['FI Rate']),
        ("Rank", display_dict['Rank']),
        ("Food Insecure", display_dict['Food Insecure']),
        ("Cost/Meal", display_dict['Cost/Meal']),
        ("Poverty Rate", display_dict['Poverty']),
    ]
    metrics_html = "".join(
        f"""<div>
            <div style="color:{COLORS['slate']};font-family:Inter,sans-serif;font-size:0.875rem;font-weight:600;
                       text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.25rem;">{label}</div>
            <div style="color:{COLORS['ink']};font-family:Georgia,serif;font-size:1.5rem;font-weight:700;">{val}</div>
        </div>"""
        for label, val in card_metrics
    )
    st.markdown(
        f"""
        <div role="region" aria-label="State summary for {display_dict['State']}"
             style="background:linear-gradient(135deg, {COLORS['snow']} 0%, {COLORS['pearl']} 100%);
                    border:2px solid {COLORS['sapphire']};border-radius:1rem;padding:1.5rem;
                    margin-top:1rem;margin-bottom:1.5rem;
                    box-shadow:0 4px 6px -1px rgba(34,81,255,0.1);">
            <h3 style="color:{COLORS['ink']};font-family:Georgia,serif;font-size:1.25rem;font-weight:700;
                       margin-bottom:1rem;display:flex;align-items:center;gap:0.5rem;">
                <i class="fas fa-map-marker-alt" aria-hidden="true"></i>
                {display_dict['State']}
            </h3>
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:1rem;">
                {metrics_html}
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

# Prepare trend data (population-weighted)
trend = weighted_rate_by_group(data, "overall_food_insecurity_rate", "year").reset_index()
trend.columns = ["Year", "FI Rate"]

# DS-3: Compute +/- 1 std dev band for confidence visualization
trend_std = data.groupby("year", observed=True)["overall_food_insecurity_rate"].std().reset_index()
trend_std.columns = ["Year", "Std"]
trend = trend.merge(trend_std, on="Year", how="left")
trend["Upper"] = trend["FI Rate"] + trend["Std"]
trend["Lower"] = (trend["FI Rate"] - trend["Std"]).clip(lower=0)

# DS-2: Child FI trend overlay
child_trend = weighted_rate_by_group(data, "child_food_insecurity_rate", "year").reset_index()
child_trend.columns = ["Year", "Child FI Rate"]

# Apply data point reduction for mobile viewports (30% reduction = keep 70%)
if chart_config.data_point_reduction < 1.0:
    total_points = len(trend)
    points_to_keep = int(total_points * chart_config.data_point_reduction)
    indices = np.linspace(0, total_points - 1, points_to_keep, dtype=int)
    trend = trend.iloc[indices].reset_index(drop=True)
    child_trend = child_trend.iloc[indices].reset_index(drop=True)

fig_trend = go.Figure()
fill_color = f"rgba(34, 81, 255, {'0.05' if IS_MOBILE else '0.08'})"

# DS-3: Add confidence band (±1 std dev)
fig_trend.add_trace(go.Scatter(
    x=pd.concat([trend["Year"], trend["Year"][::-1]]),
    y=pd.concat([trend["Upper"], trend["Lower"][::-1]]),
    fill="toself",
    fillcolor="rgba(34, 81, 255, 0.08)",
    line=dict(color="rgba(0,0,0,0)"),
    name="±1 Std Dev",
    showlegend=True,
    hoverinfo="skip",
))

# Add national trend line
fig_trend.add_trace(go.Scatter(
    x=trend["Year"], y=trend["FI Rate"],
    mode="lines+markers",
    line=dict(color=COLORS["blue"], width=chart_config.line_width),
    marker=dict(size=chart_config.marker_size, color=COLORS["blue"]),
    fill="tozeroy",
    fillcolor=fill_color,
    name="Overall FI Rate",
    hovertemplate="<b>%{x}</b><br>Overall FI Rate: %{y:.1%}<extra></extra>",
))

# DS-2: Add child FI trend overlay
fig_trend.add_trace(go.Scatter(
    x=child_trend["Year"], y=child_trend["Child FI Rate"],
    mode="lines+markers",
    line=dict(color=COLORS["amethyst"], width=chart_config.line_width, dash="dash"),
    marker=dict(size=chart_config.marker_size - 1, color=COLORS["amethyst"]),
    name="Child FI Rate",
    hovertemplate="<b>%{x}</b><br>Child FI Rate: %{y:.1%}<extra></extra>",
))

# Add state-specific trend line if a state is selected
if st.session_state.selected_state:
    state_data_for_trend = data[data["state"] == st.session_state.selected_state]
    state_trend = weighted_rate_by_group(state_data_for_trend, "overall_food_insecurity_rate", "year").reset_index()
    state_trend.columns = ["Year", "FI Rate"]
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

# DS-7: Policy event annotations + recession/COVID bands
fig_trend.add_vrect(x0=2009, x1=2010, fillcolor="rgba(192,57,43,0.08)",
                    line_width=0, annotation_text="Recession", annotation_position="top left")
fig_trend.add_vrect(x0=2020, x1=2021, fillcolor="rgba(192,57,43,0.08)",
                    line_width=0, annotation_text="COVID-19", annotation_position="top left")
# Policy milestones
for yr, label in [(2010, "Hunger-Free Kids Act"), (2014, "ACA Medicaid Expansion"),
                  (2021, "Child Tax Credit"), (2023, "SNAP Emergency End")]:
    fig_trend.add_vline(x=yr, line=dict(color="rgba(148,163,184,0.4)", width=1, dash="dot"))
    fig_trend.add_annotation(x=yr, y=1.02, yref="paper", text=label,
                             showarrow=False, font=dict(size=9, color="#94a3b8"),
                             textangle=-45 if IS_MOBILE else 0)

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
/* Desktop: show on hover */
@media (hover: hover) {
    .trend-wrap:hover .trend-explainer {
        opacity: 1;
        visibility: visible;
        transform: translateY(0);
        pointer-events: auto;
    }
}
/* Mobile/touch: toggle on tap via JS class */
.trend-explainer.is-visible {
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
  <button onclick="var el=this.nextElementSibling;el.classList.toggle('is-visible');"
          aria-label="Toggle chart explanation"
          style="position:absolute;top:8px;right:8px;z-index:10;
                 width:36px;height:36px;border-radius:50%;border:1px solid rgba(255,255,255,0.2);
                 background:rgba(26,35,126,0.8);color:#e5eaff;cursor:pointer;
                 font-size:1.1rem;display:flex;align-items:center;justify-content:center;
                 backdrop-filter:blur(8px);">
    ?
  </button>
  <div class="trend-explainer" role="tooltip" aria-label="Chart explanation">
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
section_header("Geographic Analysis", f"Spatial patterns for {selected_year}", "map")

# Render consolidated geographic section with state map, regional comparison, and urban/rural comparison
geographic_section(year_data, selected_year, viewport, selected_state=st.session_state.get('selected_state'))

st.markdown("<div class='gap-section'></div>", unsafe_allow_html=True)


# ============================================================================
# SECTION 4: STATE RANKINGS
# ============================================================================

def render_state_rankings():
    """Render state rankings content with responsive layout."""
    # Reuse population-weighted state_rankings computed earlier
    state_avg = state_rankings.copy()
    state_avg["State Name"] = state_avg["State"].map(STATE_NAMES)
    
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
    title=f"State Rankings ({selected_year})",
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
    """Render statistical details with distribution histogram + summary cards."""
    import plotly.express as px
    fi_vals = year_data["overall_food_insecurity_rate"].dropna()
    weighted_avg = weighted_rate(year_data, "overall_food_insecurity_rate")

    # Summary stat cards (compact row above histogram)
    cards = [
        ("Median", f"{fi_vals.median():.1%}", COLORS["sapphire"], COLORS["snow"]),
        ("Std Dev", f"{fi_vals.std():.1%}", COLORS["amethyst"], "#f8efff"),
        ("Range", f"{fi_vals.min():.1%}-{fi_vals.max():.1%}", COLORS["amber"], "#fff8e6"),
        ("Above Avg", f"{(fi_vals > weighted_avg).sum():,}", COLORS["ruby"], "#fff1f1"),
    ]
    stat_cards_html = '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:1rem;" role="list" aria-label="Statistical summary">'
    for title, value, fg, bg in cards:
        stat_cards_html += f"""
<div role="listitem" style="background:{bg};border-radius:12px;padding:0.75rem 0.5rem;text-align:center;
     box-shadow:0 1px 4px rgba(0,0,0,0.04);border:1px solid rgba(0,0,0,0.04);">
    <div style="font-family:Inter,sans-serif;font-size:0.75rem;font-weight:700;color:{COLORS['slate']};
               text-transform:uppercase;letter-spacing:0.04em;margin-bottom:0.2rem;">{title}</div>
    <div style="font-family:Georgia,serif;font-size:1.1rem;font-weight:800;color:{fg};">{value}</div>
</div>"""
    stat_cards_html += "</div>"
    st.markdown(stat_cards_html, unsafe_allow_html=True)

    # DS-6: Distribution histogram colored by fi_category
    hist_data = year_data[["overall_food_insecurity_rate", "fi_category"]].dropna()
    if not hist_data.empty:
        cat_order = ["Low", "Moderate", "High", "Very High"]
        cat_colors = {
            "Low": COLORS["sapphire"], "Moderate": COLORS["amber"],
            "High": "#e67e22", "Very High": COLORS["ruby"],
        }
        fig_hist = px.histogram(
            hist_data, x="overall_food_insecurity_rate", color="fi_category",
            nbins=35, category_orders={"fi_category": cat_order},
            color_discrete_map=cat_colors,
            labels={"overall_food_insecurity_rate": "Food Insecurity Rate", "fi_category": "Category"},
        )
        # Add weighted average reference line
        fig_hist.add_vline(x=weighted_avg, line=dict(color=COLORS["ink"], width=2, dash="dash"),
                           annotation_text=f"Weighted Avg: {weighted_avg:.1%}",
                           annotation_position="top right",
                           annotation_font=dict(size=11, color=COLORS["ink"]))
        hist_layout = dict(PLOTLY_LAYOUT)
        hist_layout["margin"] = dict(l=40, r=20, t=20, b=40)
        hist_layout["legend"] = dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10))
        hist_layout.pop("title", None)
        fig_hist.update_layout(
            **hist_layout,
            title="",
            height=280 if IS_MOBILE else 320,
            xaxis_tickformat=".0%",
            yaxis_title="Counties",
            bargap=0.05,
        )
        st.plotly_chart(fig_hist, use_container_width=True, key="fi_distribution_hist")

collapsible_section(
    title=f"Statistical Details ({selected_year})",
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
