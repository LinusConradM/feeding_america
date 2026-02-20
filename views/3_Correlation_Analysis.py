"""
Correlation Analysis - Bivariate and matrix correlation testing.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from scipy import stats
from utils.theme import inject_tailwind, COLORS, PLOTLY_LAYOUT, page_header
from utils.components import kpi_row, section_header, stat_card, info_banner, llm_explainer_ui
from utils.data_loader import load_data, get_variable_label, get_numeric_columns


data = load_data()
numeric_cols = get_numeric_columns(data)

ANALYSIS_VARS = [
    "overall_food_insecurity_rate", "child_food_insecurity_rate",
    "poverty_rate", "unemployment_rate", "median_income", "cost_per_meal",
    "snap_rate", "population", "hs_or_less", "gini",
    "weighted_annual_food_budget_shortfall",
]
available_vars = [v for v in ANALYSIS_VARS if v in data.columns]

# Sidebar
with st.sidebar:
    st.markdown('<p class="text-white font-semibold text-sm mb-2">Analysis Controls</p>', unsafe_allow_html=True)

    x_var = st.selectbox("X-axis Variable", available_vars,
                         index=available_vars.index("poverty_rate") if "poverty_rate" in available_vars else 0,
                         format_func=get_variable_label)
    y_var = st.selectbox("Y-axis Variable", available_vars,
                         index=available_vars.index("overall_food_insecurity_rate") if "overall_food_insecurity_rate" in available_vars else 0,
                         format_func=get_variable_label)
    corr_method = st.selectbox("Method", ["pearson", "spearman", "kendall"])
    corr_year = st.slider("Year", int(data["year"].min()), int(data["year"].max()),
                          int(data["year"].max()))

    geo_filter = st.selectbox("Geography", ["All Counties"] +
                              sorted(data["state"].dropna().unique().tolist()))

page_header("Correlation Analysis",
            "Explore relationships between food insecurity indicators", "project-diagram")

# Filter data
analysis_data = data[data["year"] == corr_year].copy()
if geo_filter != "All Counties":
    analysis_data = analysis_data[analysis_data["state"] == geo_filter]

# Run correlation
clean = analysis_data.dropna(subset=[x_var, y_var])

if len(clean) < 3:
    info_banner("Insufficient data for correlation analysis. Try a different year or geography.", "warning")
    st.stop()

if corr_method == "pearson":
    r, p = stats.pearsonr(clean[x_var], clean[y_var])
elif corr_method == "spearman":
    r, p = stats.spearmanr(clean[x_var], clean[y_var])
else:
    r, p = stats.kendalltau(clean[x_var], clean[y_var])
    
# Safely handle potential arrays if input was 2D
try:
    r = float(np.ravel(r)[0])
    p = float(np.ravel(p)[0])
except:
    pass

r2 = r ** 2
n = len(clean)

# KPI cards
p_str = f"{p:.2e}" if p < 0.001 else f"{p:.4f}"
sig = "Yes (p < 0.05)" if p < 0.05 else "No (p >= 0.05)"

kpi_row([
    {"title": "Correlation (r)", "value": f"{r:.4f}", "icon": "link", "gradient": "sapphire"},
    {"title": "R² (Variance)", "value": f"{r2:.4f}", "icon": "percentage", "gradient": "amethyst"},
    {"title": "P-value", "value": p_str, "icon": "flask", "gradient": "emerald" if p < 0.05 else "coral"},
    {"title": "Sample Size", "value": f"{n:,}", "icon": "database", "gradient": "navy"},
])

st.markdown("<div class='h-6'></div>", unsafe_allow_html=True)

# LLM Insight Engine
context_dict = {
    "Year": corr_year,
    "Geography": geo_filter,
    "Independent Variable (X)": get_variable_label(x_var),
    "Dependent Variable (Y)": get_variable_label(y_var),
    "Correlation (r)": f"{r:.4f}",
    "R-Squared (Variance Explained)": f"{r2:.4f}",
    "P-value (Statistical Significance)": p_str,
    "Sample Size (n)": f"{n:,}"
}
llm_explainer_ui("Correlation Analysis", context_dict)

# Scatter plot
section_header("Scatter Plot", f"{get_variable_label(x_var)} vs {get_variable_label(y_var)}", "braille")

color_col = None
if "fi_category" in analysis_data.columns:
    scatter_data = analysis_data[[x_var, y_var, "fi_category"]].dropna()
    color_col = "fi_category"
else:
    scatter_data = clean

fig_scatter = px.scatter(
    scatter_data, x=x_var, y=y_var,
    color=color_col if color_col else None,
    color_discrete_sequence=[COLORS["teal"], COLORS["amber"], COLORS["rose"], "#8B0000"],
    opacity=0.6,
    trendline="ols",
    labels={x_var: get_variable_label(x_var), y_var: get_variable_label(y_var)},
)

fig_scatter.update_layout(
    **PLOTLY_LAYOUT,
    title="",
    height=500,
    xaxis_tickformat=".0%" if "rate" in x_var else "",
    yaxis_tickformat=".0%" if "rate" in y_var else "",
    legend_title="FI Category" if color_col else "",
)

# Add R² annotation
fig_scatter.add_annotation(
    x=0.02, y=0.98, xref="paper", yref="paper",
    text=f"r = {r:.3f} | R² = {r2:.3f} | p = {p_str}",
    showarrow=False,
    font=dict(size=13, color=COLORS["slate"]),
    bgcolor="rgba(255,255,255,0.9)",
    bordercolor=COLORS["pearl"],
    borderwidth=1,
    borderpad=6,
)

st.plotly_chart(fig_scatter, width='stretch')

# --- CORRELATION MATRIX ---
section_header("Correlation Matrix", "Pairwise correlations among key variables", "th")

matrix_vars = [v for v in available_vars if v in data.columns]
matrix_data = analysis_data[matrix_vars].dropna()

if len(matrix_data) > 10:
    corr_matrix = matrix_data.corr(method=corr_method)

    labels = [get_variable_label(v) for v in corr_matrix.columns]

    fig_matrix = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=labels, y=labels,
        colorscale=[[0, COLORS["rose"]], [0.5, "white"], [1, COLORS["blue"]]],
        zmid=0, zmin=-1, zmax=1,
        text=np.round(corr_matrix.values, 2),
        texttemplate="%{text}",
        textfont=dict(size=11),
        hovertemplate="<b>%{x}</b> vs <b>%{y}</b><br>r = %{z:.3f}<extra></extra>",
    ))

    fig_matrix.update_layout(
        **PLOTLY_LAYOUT,
        title="",
        height=600,
    )
    fig_matrix.update_xaxes(tickangle=45, tickfont_size=10)
    fig_matrix.update_yaxes(tickfont_size=10)
    st.plotly_chart(fig_matrix, width='stretch')

# --- INTERPRETATION ---
section_header("Interpretation", icon="lightbulb")

strength = "very weak"
if abs(r) >= 0.7:
    strength = "strong"
elif abs(r) >= 0.4:
    strength = "moderate"
elif abs(r) >= 0.2:
    strength = "weak"

direction = "positive" if r > 0 else "negative"

st.markdown(
    f"""
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <div class="grid grid-cols-2 gap-6">
            <div>
                <h3 class="text-sm font-bold text-gray-800 mb-3">Correlation Summary</h3>
                <ul class="space-y-2 text-sm text-gray-600">
                    <li>The {corr_method.title()} correlation between
                        <strong>{get_variable_label(x_var)}</strong> and
                        <strong>{get_variable_label(y_var)}</strong> is
                        <strong class="text-blue-700">{r:.3f}</strong>.</li>
                    <li>This indicates a <strong>{strength} {direction}</strong> relationship.</li>
                    <li><strong>{r2:.1%}</strong> of the variance in {get_variable_label(y_var)}
                        is explained by {get_variable_label(x_var)}.</li>
                    <li>The relationship is <strong>{"statistically significant" if p < 0.05 else "not statistically significant"}</strong>
                        at the 0.05 level (p = {p_str}).</li>
                </ul>
            </div>
            <div>
                <h3 class="text-sm font-bold text-gray-800 mb-3">Methodology</h3>
                <ul class="space-y-2 text-sm text-gray-600">
                    <li><strong>Method:</strong> {corr_method.title()} correlation</li>
                    <li><strong>Year:</strong> {corr_year}</li>
                    <li><strong>Geography:</strong> {geo_filter}</li>
                    <li><strong>Observations:</strong> {n:,} (after removing missing values)</li>
                </ul>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
