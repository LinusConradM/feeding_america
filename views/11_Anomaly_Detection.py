"""
Anomaly Detection - Unsupervised ML to find counties with decoupled metrics.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from utils.theme import inject_tailwind, COLORS, PLOTLY_LAYOUT, page_header
from utils.components import kpi_row, section_header, info_banner, stat_card, llm_explainer_ui
from utils.data_loader import load_data, get_variable_label, STATE_NAMES

st.set_page_config(page_title="Anomaly Search Engine", page_icon="📡", layout="wide")
inject_tailwind()

data = load_data()

# Clean data
ml_vars = [
    "overall_food_insecurity_rate", "child_food_insecurity_rate", 
    "poverty_rate", "unemployment_rate", "median_income", "snap_rate"
]

# Sidebar
with st.sidebar:
    st.markdown('<p class="text-white font-semibold text-sm mb-2">Isolation Forest Limits</p>', unsafe_allow_html=True)

    scan_year = st.slider("Scan Year", int(data["year"].min()), int(data["year"].max()),
                          int(data["year"].max()))
    
    contamination = st.slider(
        "Sensitivity (%)", 1, 10, 5,
        help="What percentage of counties should be mathematically flagged as the most severe anomalies? Lower values find only the most extreme outliers."
    )
    
    scan_state = st.selectbox(
        "Constrain to State",
        ["National Scan"] + sorted(data["state"].dropna().unique().tolist())
    )

page_header("Anomaly Search Engine",
            "Unsupervised Machine Learning scanning for severe macroeconomic decoupling", "satellite-dish")

# --- ISOLATION FOREST PIPELINE ---
filter_data = data[data["year"] == scan_year]
if scan_state != "National Scan":
    filter_data = filter_data[filter_data["state"] == scan_state]

# Drop NaNs for the ML algorithm
clean_ml = filter_data.dropna(subset=ml_vars + ["state", "county"]).copy()

if len(clean_ml) < 50:
    info_banner("Insufficient counties for an effective Anomaly Scan. Try a national scan or select a larger state.", "warning")
    st.stop()

with st.spinner("Training Isolation Forest... Scanning for outliers..."):
    # Target Isolation Forest Inputs
    X = clean_ml[ml_vars]
    
    # Train Unsupervised Model
    iso_forest = IsolationForest(
        n_estimators=100, 
        contamination=contamination/100.0, 
        random_state=42
    )
    
    # Predict (-1 is anomaly, 1 is normal)
    clean_ml['is_anomaly'] = iso_forest.fit_predict(X)
    clean_ml['anomaly_score'] = iso_forest.decision_function(X) # Lower is more anomalous
    
    anomalies = clean_ml[clean_ml['is_anomaly'] == -1].sort_values("anomaly_score")
    normals = clean_ml[clean_ml['is_anomaly'] == 1]
    
    kpi_row([
        {"title": "Counties Scanned", "value": f"{len(clean_ml):,}", "icon": "search", "gradient": "sapphire"},
        {"title": "Severe Anomalies", "value": f"{len(anomalies):,}", "icon": "exclamation-triangle", "gradient": "coral"},
        {"title": "Sensitivity Level", "value": f"{contamination}%", "icon": "sliders-h", "gradient": "amethyst"},
    ])
    
    st.markdown("<div class='h-4'></div>", unsafe_allow_html=True)
    
    # LLM Context
    top_5 = anomalies.head(5)[['county', 'state']].apply(lambda x: f"{x['county']} County, {x['state']}", axis=1).tolist()
    context_dict = {
        "Scope": "National" if scan_state == "National Scan" else STATE_NAMES.get(scan_state),
        "Total Scanned": f"{len(clean_ml):,} counties",
        "Number of Outliers Detected": len(anomalies),
        "Top 5 Most Severe Anomalies": ", ".join(top_5)
    }
    llm_explainer_ui("Isolation Forest Anomaly Scan", context_dict)
    
    # --- VISUALIZATION ---
    col1, col2 = st.columns([2, 1])
    
    with col1:
        section_header("Multivariate Outlier Scatter", "FI Rate vs Poverty Rate colored by Anomaly Score", "braille")
        
        # We plot FI vs Poverty, but remember the model clustered on 6 variables in N-dimensional space
        fig = px.scatter(
            clean_ml,
            x="poverty_rate", y="overall_food_insecurity_rate",
            color="is_anomaly",
            color_continuous_scale=[[0, COLORS["rose"]], [0.5, COLORS["rose"]], [0.5, COLORS["teal"]], [1, COLORS["teal"]]],
            hover_name="county",
            hover_data={"state": True, "anomaly_score": True, "is_anomaly": False},
            opacity=0.7
        )
        
        fig.update_layout(
            **PLOTLY_LAYOUT, height=500,
            xaxis_title="Poverty Rate",
            yaxis_title="Food Insecurity Rate",
            xaxis_tickformat=".0%", yaxis_tickformat=".0%",
            coloraxis_showscale=False
        )
        
        # Add annotation for anomalies
        for _, row in anomalies.head(5).iterrows():
            fig.add_annotation(
                x=row['poverty_rate'], y=row['overall_food_insecurity_rate'],
                text=f"{row['county']}, {row['state']}",
                showarrow=False, yshift=15,
                font=dict(color=COLORS["rose"], size=10)
            )
            
        st.plotly_chart(fig, width='stretch')
        
    with col2:
        section_header("Top 10 Anomalies", "Most extreme negative decoupling", "clipboard-list")
        
        display_df = anomalies.head(10)[["county", "state", "overall_food_insecurity_rate", "poverty_rate", "anomaly_score"]].copy()
        display_df["overall_food_insecurity_rate"] = display_df["overall_food_insecurity_rate"].apply(lambda x: f"{x:.1%}")
        display_df["poverty_rate"] = display_df["poverty_rate"].apply(lambda x: f"{x:.1%}")
        display_df["anomaly_score"] = display_df["anomaly_score"].apply(lambda x: f"{x:.3f}")
        display_df.rename(columns={
            "county": "County", "state": "St", 
            "overall_food_insecurity_rate": "FI Rate", 
            "poverty_rate": "Pov Rate", 
            "anomaly_score": "Isolation Score"
        }, inplace=True)
        
        st.dataframe(display_df, hide_index=True, use_container_width=True)

    # --- MAP RENDER ---
    section_header("Geographic Distribution of Anomalies", "Where are the systemic breakdowns located?", "map")
    
    map_data = clean_ml.groupby("state")['is_anomaly'].apply(lambda x: (x == -1).sum()).reset_index()
    map_data.columns = ["State", "Anomaly Count"]
    map_data["State Name"] = map_data["State"].map(STATE_NAMES)
    
    fig_map = px.choropleth(
        map_data, locations="State", locationmode="USA-states",
        color="Anomaly Count", 
        color_continuous_scale=[[0, COLORS["slate"]], [0.5, COLORS["amber"]], [1, COLORS["rose"]]],
        scope="usa", hover_name="State Name"
    )
    
    fig_map.update_layout(
        **PLOTLY_LAYOUT, height=450, title="",
        geo=dict(bgcolor="rgba(0,0,0,0)"),
        coloraxis_colorbar=dict(title="Anomalies Found")
    )
    st.plotly_chart(fig_map, width='stretch')
    
    # Interpretation Block
    st.markdown(
        f"""
        <div class="bg-gray-50 rounded-2xl border border-gray-200 p-6 mt-6">
            <h3 class="text-sm font-bold text-gray-800 mb-3">
                <i class="fas fa-satellite-dish text-blue-500 mr-2"></i>How Isolation Forests Work
            </h3>
            <p class="text-gray-600 text-sm leading-relaxed mb-4">
                Instead of profiling what "normal" counties look like, an Isolation Forest builds completely random decision trees to explicitly isolate 
                the weirdest, most abnormal data points. If a county is easy to mathematically separate from the rest of the herd using just a few random conditional splits, it is flagged as an anomaly.
            </p>
            <p class="text-gray-600 text-sm leading-relaxed mb-4">
                Because this scatter plot is only 2-dimensional (FI vs Poverty), some of the red anomalies may appear perfectly normal on this chart. 
                However, the ML model evaluated 6 dimensions simultaneously. If a county looks normal here but is colored red, it means their <i>Unemployment</i>, <i>SNAP utilization</i>, or <i>Median Income</i> is severely broken under the hood. <b>These are regions where systemic economic logic breaks down.</b>
            </p>
        </div>
        """, unsafe_allow_html=True
    )
