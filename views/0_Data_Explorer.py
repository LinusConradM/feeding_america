"""
Data Explorer — Comprehensive EDA: Summary Statistics, Missingness, Distributions, Box Plots, Pair Plot, Rankings.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import pandas as pd
import numpy as np
from utils.theme import enforce_landscape_on_mobile, inject_tailwind, COLORS, PLOTLY_LAYOUT, page_header
from utils.components import kpi_row, section_header, llm_explainer_ui
from utils.data_loader import load_data, get_variable_label, get_numeric_columns

data = load_data()
numeric_cols = get_numeric_columns(data)

ANALYSIS_VARS = [
    "overall_food_insecurity_rate", "child_food_insecurity_rate",
    "poverty_rate", "unemployment_rate", "median_income", "cost_per_meal",
    "weighted_annual_food_budget_shortfall", "snap_rate", "gini",
]
available_vars = [v for v in ANALYSIS_VARS if v in data.columns]

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="text-white font-semibold text-sm mb-2">EDA Controls</p>', unsafe_allow_html=True)
    selected_year = st.slider("Year", int(data["year"].min()), int(data["year"].max()), int(data["year"].max()))
    geo_filter = st.selectbox("State Filter", ["All Counties"] + sorted(data["state"].dropna().unique().tolist()))
    hist_var = st.selectbox("Variable for Distribution / Box Plot", available_vars, format_func=get_variable_label)

enforce_landscape_on_mobile()
page_header("Data Explorer", "Exploratory Data Analysis — quality, distributions, and rankings", "microscope")

year_data = data[data["year"] == selected_year].copy()
if geo_filter != "All Counties":
    year_data = year_data[year_data["state"] == geo_filter]

# ── 1. SUMMARY STATISTICS ────────────────────────────────────────────────────
section_header("Summary Statistics", f"Descriptive stats across all numeric variables ({selected_year})", "table")

summary_vars = [v for v in available_vars if v in year_data.columns]
desc = year_data[summary_vars].describe().T.reset_index()
desc.columns = ["Variable", "Count", "Mean", "Std Dev", "Min", "25th Pct", "Median", "75th Pct", "Max"]
desc["Variable"] = desc["Variable"].apply(get_variable_label)

# Format numeric columns
for col in ["Mean", "Std Dev", "Min", "25th Pct", "Median", "75th Pct", "Max"]:
    desc[col] = desc[col].apply(lambda x: f"{x:,.4f}" if pd.notna(x) else "N/A")
desc["Count"] = desc["Count"].apply(lambda x: f"{int(x):,}")

st.dataframe(
    desc,
    width='stretch',
    hide_index=True,
)

# KPI summary cards
total_counties = len(year_data)
total_vars = len(summary_vars)
null_pct = year_data[summary_vars].isnull().mean().mean() * 100
complete_rows = year_data[summary_vars].dropna().shape[0]

kpi_row([
    {"title": "Counties in Dataset", "value": f"{total_counties:,}", "icon": "map-marker", "gradient": "sapphire"},
    {"title": "Variables Analyzed", "value": str(total_vars), "icon": "columns", "gradient": "amethyst"},
    {"title": "Avg. Nulls Across Vars", "value": f"{null_pct:.1f}%", "icon": "exclamation-triangle", "gradient": "ruby" if null_pct > 10 else "emerald"},
    {"title": "Complete-case Rows", "value": f"{complete_rows:,}", "icon": "check-circle", "gradient": "navy"},
])

st.markdown("<div class='h-6'></div>", unsafe_allow_html=True)

# ── 2. DATA QUALITY / MISSINGNESS REPORT ─────────────────────────────────────
section_header("Missingness Report", "% of missing values per variable and year", "eye-slash")

miss_by_year = data.groupby("year")[available_vars].apply(lambda g: g.isnull().mean() * 100).T
miss_by_year.index = [get_variable_label(v) for v in miss_by_year.index]

fig_miss = go.Figure(data=go.Heatmap(
    z=miss_by_year.values,
    x=[str(y) for y in miss_by_year.columns],
    y=miss_by_year.index.tolist(),
    colorscale=[[0, "#ECFDF5"], [0.3, COLORS["amber"]], [1, COLORS["rose"]]],
    zmin=0, zmax=50,
    text=np.round(miss_by_year.values, 1),
    texttemplate="%{text}%",
    textfont=dict(size=10),
    hovertemplate="<b>%{y}</b> in %{x}<br>Missing: %{z:.1f}%<extra></extra>",
))
fig_miss.update_layout(**PLOTLY_LAYOUT, title="", height=380)
st.plotly_chart(fig_miss, width='stretch')

st.markdown(
    """
    <div style="background:#FFFBEB;border:1px solid #FDE68A;border-radius:8px;padding:0.75rem 1rem;margin-top:-0.5rem;margin-bottom:1.5rem;font-size:0.85rem;color:#92400E;">
        <strong>⚠ Interpretation:</strong> Green = 0% missing (good). Amber = moderate gaps. Red = severe missingness that may bias analysis.
        Columns and years with &gt;20% missing should be treated with caution in regression and clustering models.
    </div>
    """,
    unsafe_allow_html=True,
)

# ── 3. DISTRIBUTION HISTOGRAM + KDE ──────────────────────────────────────────
section_header("Distribution Analysis", f"Histogram + density curve for {get_variable_label(hist_var)}", "chart-bar")

col1, col2 = st.columns([2, 1])

with col1:
    hist_data = year_data[hist_var].dropna()
    is_rate = "rate" in hist_var

    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(
        x=hist_data,
        nbinsx=40,
        name="Count",
        marker_color=COLORS["blue"],
        opacity=0.75,
        histnorm="probability density",
    ))

    # KDE overlay
    from scipy.stats import gaussian_kde
    if len(hist_data) > 10:
        kde_x = np.linspace(hist_data.min(), hist_data.max(), 300)
        kde = gaussian_kde(hist_data)
        fig_hist.add_trace(go.Scatter(
            x=kde_x, y=kde(kde_x),
            mode="lines", name="KDE", line=dict(color=COLORS["rose"], width=2.5)
        ))

    fig_hist.add_vline(x=float(hist_data.mean()), line_dash="dash", line_color=COLORS["amber"],
                       annotation_text=f"Mean {hist_data.mean():.3f}", annotation_position="top right")
    fig_hist.add_vline(x=float(hist_data.median()), line_dash="dot", line_color=COLORS["teal"],
                       annotation_text=f"Median {hist_data.median():.3f}", annotation_position="top left")

    fig_hist.update_layout(
        **PLOTLY_LAYOUT,
        title="",
        height=380,
        barmode="overlay",
        xaxis_tickformat=".0%" if is_rate else "",
    )
    st.plotly_chart(fig_hist, width='stretch')

with col2:
    skew = hist_data.skew()
    kurt = hist_data.kurtosis()
    skew_label = "Right-skewed" if skew > 0.5 else "Left-skewed" if skew < -0.5 else "Roughly symmetric"

    st.markdown(
        f"""
        <div style="background:#FFFFFF;border:1px solid #E5E7EB;border-radius:8px;padding:1.25rem;margin-top:0.5rem;">
            <h4 style="font-size:0.8rem;font-weight:700;color:#6B7280;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.75rem;">Shape Diagnostics</h4>
            <table style="width:100%;font-size:0.82rem;color:#111827;border-collapse:collapse;">
                <tr><td style="padding:0.3rem 0;color:#6B7280;">Mean</td><td style="font-weight:600;text-align:right;">{hist_data.mean():.4f}</td></tr>
                <tr><td style="padding:0.3rem 0;color:#6B7280;">Median</td><td style="font-weight:600;text-align:right;">{hist_data.median():.4f}</td></tr>
                <tr><td style="padding:0.3rem 0;color:#6B7280;">Std Dev</td><td style="font-weight:600;text-align:right;">{hist_data.std():.4f}</td></tr>
                <tr><td style="padding:0.3rem 0;color:#6B7280;">Skewness</td><td style="font-weight:600;text-align:right;">{skew:.3f}</td></tr>
                <tr><td style="padding:0.3rem 0;color:#6B7280;">Kurtosis</td><td style="font-weight:600;text-align:right;">{kurt:.3f}</td></tr>
                <tr><td style="padding:0.3rem 0;color:#6B7280;">Min</td><td style="font-weight:600;text-align:right;">{hist_data.min():.4f}</td></tr>
                <tr><td style="padding:0.3rem 0;color:#6B7280;">Max</td><td style="font-weight:600;text-align:right;">{hist_data.max():.4f}</td></tr>
            </table>
            <div style="margin-top:0.75rem;padding:0.5rem;background:#F0FDF4;border-radius:6px;font-size:0.8rem;color:#166534;font-weight:500;">
                📐 {skew_label}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── 4. BOX PLOTS BY STATE / REGION ────────────────────────────────────────────
section_header("Box Plots by State", f"Spread of {get_variable_label(hist_var)} across top/bottom 15 states", "box-open")

all_state_data = data[data["year"] == selected_year][["state", hist_var]].dropna()
state_medians = all_state_data.groupby("state")[hist_var].median().sort_values(ascending=False)
top_bottom = pd.concat([state_medians.head(8), state_medians.tail(7)]).index.tolist()
box_data = all_state_data[all_state_data["state"].isin(top_bottom)]
box_data = box_data.copy()
box_data["state"] = pd.Categorical(box_data["state"], categories=top_bottom, ordered=True)

fig_box = px.box(
    box_data.sort_values("state"),
    x="state", y=hist_var,
    color="state",
    color_discrete_sequence=px.colors.qualitative.Bold,
    labels={hist_var: get_variable_label(hist_var), "state": "State"},
    points="outliers",
)
fig_box.update_layout(**PLOTLY_LAYOUT, title="", height=420, showlegend=False,
                      yaxis_tickformat=".0%" if "rate" in hist_var else "")
fig_box.add_annotation(
    x=0.01, y=0.98, xref="paper", yref="paper", showarrow=False,
    text="Top 8 (highest median) ← — → Bottom 7 (lowest median)",
    font=dict(size=11, color=COLORS["slate"]), bgcolor="rgba(255,255,255,0.85)",
)
st.plotly_chart(fig_box, width='stretch')

# ── 5. PAIR PLOT (SCATTER MATRIX) ─────────────────────────────────────────────
section_header("Pair Plot", "All-vs-all scatter matrix for key numeric variables", "th")

pair_vars = [v for v in ["overall_food_insecurity_rate", "poverty_rate", "unemployment_rate",
                          "median_income", "cost_per_meal"] if v in year_data.columns]
pair_data = year_data[pair_vars].dropna().sample(min(800, len(year_data)), random_state=42)
pair_labels = {v: get_variable_label(v) for v in pair_vars}

fig_pair = px.scatter_matrix(
    pair_data,
    dimensions=pair_vars,
    labels=pair_labels,
    color_discrete_sequence=[COLORS["blue"]],
    opacity=0.4,
)
fig_pair.update_traces(diagonal_visible=True, showupperhalf=False, marker=dict(size=3))
fig_pair.update_layout(**PLOTLY_LAYOUT, title="", height=650)
st.plotly_chart(fig_pair, width='stretch')

# ── 6. PERCENTILE RANKINGS TABLE ──────────────────────────────────────────────
section_header("Percentile Rankings", "Top & bottom 10 counties by selected variable", "sort-amount-down")

col_a, col_b = st.columns(2)

rank_cols = ["county", "state", hist_var]
available_rank = [c for c in rank_cols if c in year_data.columns]
rank_df = year_data[available_rank].dropna(subset=[hist_var])
rank_df = rank_df.rename(columns={hist_var: get_variable_label(hist_var)})

with col_a:
    st.markdown("#### 🔴 Top 10 (Worst)")
    top10 = rank_df.nlargest(10, get_variable_label(hist_var)).reset_index(drop=True)
    top10.index += 1
    st.dataframe(top10, width='stretch')

with col_b:
    st.markdown("#### 🟢 Bottom 10 (Best)")
    bot10 = rank_df.nsmallest(10, get_variable_label(hist_var)).reset_index(drop=True)
    bot10.index += 1
    st.dataframe(bot10, width='stretch')

# ── LLM Insight Engine ────────────────────────────────────────────────────────
context_dict = {
    "Year": selected_year,
    "Geography Filter": geo_filter,
    "Variable Analyzed": get_variable_label(hist_var),
    "Total Counties": f"{total_counties:,}",
    "Average Missingness": f"{null_pct:.1f}%",
    "Complete-case Rows": f"{complete_rows:,}",
    "Mean": f"{hist_data.mean():.4f}",
    "Std Dev": f"{hist_data.std():.4f}",
    "Skewness": f"{skew:.3f}",
}
llm_explainer_ui("Data Explorer", context_dict)
