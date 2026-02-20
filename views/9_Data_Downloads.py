"""
Data & Downloads - Explore and export the dataset.
"""

import streamlit as st
import pandas as pd
import numpy as np
import io
from utils.theme import inject_tailwind, COLORS, page_header
from utils.components import kpi_row, section_header, stat_card, info_banner, llm_explainer_ui
from utils.data_loader import load_data, get_variable_label, STATE_NAMES


data = load_data()

# Sidebar filters
with st.sidebar:
    st.markdown('<p class="text-white font-semibold text-sm mb-2">Data Filters</p>', unsafe_allow_html=True)

    dl_years = st.slider(
        "Year Range",
        int(data["year"].min()), int(data["year"].max()),
        (int(data["year"].min()), int(data["year"].max())),
    )
    dl_states = st.multiselect(
        "States",
        sorted(data["state"].dropna().unique().tolist()),
        default=[],
        help="Leave empty for all states",
    )
    dl_urban = st.multiselect(
        "Urban/Rural",
        ["Metro", "Non-metro", "Rural"],
        default=[],
        help="Leave empty for all categories",
    )

page_header("Data & Downloads",
            "Explore, filter, and export the food insecurity dataset", "database")

# Apply filters
filtered = data[(data["year"] >= dl_years[0]) & (data["year"] <= dl_years[1])]
if dl_states:
    filtered = filtered[filtered["state"].isin(dl_states)]
if dl_urban:
    filtered = filtered[filtered["urban_rural"].isin(dl_urban)]

# Dataset KPIs
kpi_row([
    {"title": "Total Records", "value": f"{len(filtered):,}", "icon": "table", "gradient": "sapphire"},
    {"title": "Counties", "value": f"{filtered['fips'].nunique():,}", "icon": "map-pin", "gradient": "emerald"},
    {"title": "States", "value": f"{filtered['state'].nunique()}", "icon": "flag-usa", "gradient": "amethyst"},
    {"title": "Year Range", "value": f"{dl_years[0]}-{dl_years[1]}", "icon": "calendar", "gradient": "navy"},
])

st.markdown("<div class='h-6'></div>", unsafe_allow_html=True)

# LLM Insight Engine
context_dict = {
    "Total Records Filtered": f"{len(filtered):,}",
    "Counties Filtered": f"{filtered['fips'].nunique():,}",
    "States Filtered": f"{filtered['state'].nunique()}",
    "Year Range": f"{dl_years[0]}-{dl_years[1]}",
    "Columns Displayed": ", ".join([get_variable_label(c) for c in display_cols]) if 'display_cols' in locals() and display_cols else "None"
}
llm_explainer_ui("Data Downloads", context_dict)

# --- DATA EXPLORER ---
section_header("Data Explorer", "Browse and search the filtered dataset", "search")

# Column selector
all_cols = filtered.columns.tolist()
display_cols = st.multiselect(
    "Select Columns to Display",
    all_cols,
    default=[c for c in ["fips", "state", "county", "year", "overall_food_insecurity_rate",
                          "child_food_insecurity_rate", "poverty_rate", "median_income",
                          "unemployment_rate", "population", "urban_rural"]
             if c in all_cols],
)

if display_cols:
    display_data = filtered[display_cols].copy()

    # Format rate columns for display
    st.dataframe(
        display_data,
        width='stretch',
        height=500,
        column_config={
            col: st.column_config.NumberColumn(
                get_variable_label(col),
                format="%.1%%" if "rate" in col else "%.2f" if "cost" in col or "gini" in col else None,
            )
            for col in display_cols if col in filtered.select_dtypes(include=[np.number]).columns
        },
    )
else:
    info_banner("Select at least one column to display.", "warning")

# --- SUMMARY STATISTICS ---
section_header("Summary Statistics", icon="calculator")

numeric_cols = filtered.select_dtypes(include=[np.number]).columns.tolist()
exclude = {"lat", "lon"}
stat_cols = [c for c in numeric_cols if c not in exclude]

if stat_cols:
    summary = filtered[stat_cols].describe().T
    summary.columns = ["Count", "Mean", "Std Dev", "Min", "25%", "Median", "75%", "Max"]
    summary.index = [get_variable_label(c) for c in summary.index]

    st.dataframe(summary.round(4), width='stretch', height=400)

# --- MISSING DATA ---
section_header("Data Quality", icon="shield-alt")

col_q1, col_q2 = st.columns(2)

with col_q1:
    missing = filtered[stat_cols].isnull().sum().reset_index()
    missing.columns = ["Variable", "Missing Count"]
    missing["Variable"] = missing["Variable"].apply(get_variable_label)
    missing["Missing %"] = (missing["Missing Count"] / len(filtered) * 100).round(1)
    missing = missing[missing["Missing Count"] > 0].sort_values("Missing Count", ascending=False)

    if len(missing) > 0:
        st.markdown(
            '<div class="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-3">'
            '<h3 class="text-amber-800 font-bold text-sm">Variables with Missing Values</h3></div>',
            unsafe_allow_html=True,
        )
        st.dataframe(missing, width='stretch', hide_index=True)
    else:
        info_banner("No missing values in the filtered dataset.", "success")

with col_q2:
    # Data coverage by year
    coverage = filtered.groupby("year", observed=True)["fips"].nunique().reset_index()
    coverage.columns = ["Year", "Counties"]

    import plotly.express as px
    fig_cov = px.bar(
        coverage, x="Year", y="Counties",
        color_discrete_sequence=[COLORS["blue"]],
    )
    fig_cov.update_layout(
        paper_bgcolor="white", plot_bgcolor="white",
        title="County Coverage by Year", height=300,
        margin=dict(l=40, r=20, t=40, b=30),
        yaxis_title="Counties with Data",
    )
    st.plotly_chart(fig_cov, width='stretch')

# --- DOWNLOAD SECTION ---
section_header("Download Data", "Export filtered data in your preferred format", "download")

col_d1, col_d2, col_d3 = st.columns(3)

with col_d1:
    csv_data = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download CSV",
        data=csv_data,
        file_name=f"food_insecurity_{dl_years[0]}-{dl_years[1]}.csv",
        mime="text/csv",
        width='stretch',
        type="primary",
    )
    st.markdown(
        f'<p class="text-gray-500 text-xs text-center mt-1">{len(csv_data)/1024:.0f} KB</p>',
        unsafe_allow_html=True,
    )

with col_d2:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        filtered.to_excel(writer, index=False, sheet_name="Food Insecurity Data")
        if stat_cols:
            summary_df = filtered[stat_cols].describe().T
            summary_df.to_excel(writer, sheet_name="Summary Statistics")
    excel_data = buffer.getvalue()

    st.download_button(
        label="Download Excel",
        data=excel_data,
        file_name=f"food_insecurity_{dl_years[0]}-{dl_years[1]}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width='stretch',
    )
    st.markdown(
        f'<p class="text-gray-500 text-xs text-center mt-1">{len(excel_data)/1024:.0f} KB</p>',
        unsafe_allow_html=True,
    )

with col_d3:
    json_data = filtered.to_json(orient="records", indent=2).encode("utf-8")
    st.download_button(
        label="Download JSON",
        data=json_data,
        file_name=f"food_insecurity_{dl_years[0]}-{dl_years[1]}.json",
        mime="application/json",
        width='stretch',
    )
    st.markdown(
        f'<p class="text-gray-500 text-xs text-center mt-1">{len(json_data)/1024:.0f} KB</p>',
        unsafe_allow_html=True,
    )

# --- DATA DICTIONARY ---
section_header("Data Dictionary", icon="book")

dict_data = []
for col in data.columns:
    dtype = str(data[col].dtype)
    non_null = data[col].notna().sum()
    pct = non_null / len(data) * 100

    dict_data.append({
        "Variable": col,
        "Label": get_variable_label(col),
        "Type": dtype,
        "Non-Null": f"{non_null:,}",
        "Coverage": f"{pct:.0f}%",
    })

dict_df = pd.DataFrame(dict_data)

with st.expander("View Full Data Dictionary", expanded=False):
    st.dataframe(dict_df, width='stretch', hide_index=True, height=600)

# Footer
st.markdown(
    """
    <div class="bg-gray-50 rounded-2xl border border-gray-200 p-6 mt-6">
        <h3 class="text-sm font-bold text-gray-800 mb-2">
            <i class="fas fa-quote-left text-blue-500 mr-2"></i>Citation
        </h3>
        <p class="text-gray-600 text-sm font-mono">
            Muhirwe, C. L. (2025). U.S. Food Insecurity Analytics Platform.
            American University. Data: Feeding America Map the Meal Gap; U.S. Census ACS.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
