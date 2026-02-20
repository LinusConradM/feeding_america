"""
County Clustering - K-Means clustering and PCA visualization.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from utils.theme import inject_tailwind, COLORS, PLOTLY_LAYOUT, SEQUENTIAL_COLORS, page_header
from utils.components import kpi_row, section_header, stat_card, info_banner, llm_explainer_ui
from utils.data_loader import load_data, get_variable_label


data = load_data()

CLUSTER_VARS = [
    "overall_food_insecurity_rate", "poverty_rate", "unemployment_rate",
    "median_income", "cost_per_meal", "snap_rate",
]
available_vars = [v for v in CLUSTER_VARS if v in data.columns]

# Sidebar
with st.sidebar:
    st.markdown('<p class="text-white font-semibold text-sm mb-2">Clustering Controls</p>', unsafe_allow_html=True)

    cluster_year = st.slider("Year", int(data["year"].min()), int(data["year"].max()),
                             int(data["year"].max()))
    n_clusters = st.slider("Number of Clusters", 2, 8, 4)
    selected_vars = st.multiselect(
        "Clustering Variables",
        available_vars,
        default=available_vars[:5],
        format_func=get_variable_label,
    )

page_header("County Clustering",
            "Segment counties by food insecurity characteristics", "layer-group")

if len(selected_vars) < 2:
    info_banner("Select at least 2 variables for clustering.", "warning")
    st.stop()

# Prepare data
year_data = data[data["year"] == cluster_year].copy()
cluster_data = year_data[["fips", "county", "state"] + selected_vars].dropna()

if len(cluster_data) < n_clusters * 3:
    info_banner("Insufficient data for clustering. Try different year or variables.", "warning")
    st.stop()

run_clustering = st.button("Run Clustering", type="primary", width='stretch')

if run_clustering or "cluster_results" in st.session_state:
    if run_clustering:
        X = cluster_data[selected_vars].values
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # K-Means
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_scaled)
        cluster_data["Cluster"] = labels

        # Silhouette
        sil = silhouette_score(X_scaled, labels) if n_clusters > 1 else 0

        # PCA
        pca = PCA(n_components=min(2, X_scaled.shape[1]))
        X_pca = pca.fit_transform(X_scaled)

        # Elbow analysis
        inertias = []
        K_range = range(2, min(10, len(cluster_data) // 3))
        for k in K_range:
            km = KMeans(n_clusters=k, random_state=42, n_init=10)
            km.fit(X_scaled)
            inertias.append(km.inertia_)

        st.session_state["cluster_results"] = {
            "data": cluster_data.copy(),
            "X_pca": X_pca, "pca": pca,
            "sil": sil, "inertia": kmeans.inertia_,
            "labels": labels,
            "inertias": list(zip(K_range, inertias)),
            "var_explained": pca.explained_variance_ratio_,
        }

    res = st.session_state["cluster_results"]
    cluster_data = res["data"]

    # KPIs
    kpi_row([
        {"title": "Clusters", "value": str(n_clusters), "icon": "layer-group", "gradient": "sapphire"},
        {"title": "Silhouette Score", "value": f"{res['sil']:.3f}", "icon": "star", "gradient": "emerald"},
        {"title": "Inertia", "value": f"{res['inertia']:,.0f}", "icon": "compress-arrows-alt", "gradient": "amber"},
        {"title": "Counties", "value": f"{len(cluster_data):,}", "icon": "map-pin", "gradient": "navy"},
    ])

    st.markdown("<div class='h-6'></div>", unsafe_allow_html=True)

    # LLM Insight Engine
    context_dict = {
        "Year": cluster_year,
        "Clusters (k)": str(n_clusters),
        "Input Variables": [get_variable_label(v) for v in selected_vars],
        "Silhouette Score": f"{res['sil']:.3f}",
        "Analyzed Counties": f"{len(cluster_data):,}"
    }
    llm_explainer_ui("County Clustering", context_dict)

    # PCA Scatter
    col1, col2 = st.columns([3, 2])

    with col1:
        section_header("Cluster Visualization (PCA)", icon="braille")
        pca_df = pd.DataFrame({
            "PC1": res["X_pca"][:, 0],
            "PC2": res["X_pca"][:, 1] if res["X_pca"].shape[1] > 1 else 0,
            "Cluster": cluster_data["Cluster"].astype(str),
            "County": cluster_data["county"],
            "State": cluster_data["state"],
        })

        fig_pca = px.scatter(
            pca_df, x="PC1", y="PC2", color="Cluster",
            hover_data=["County", "State"],
            color_discrete_sequence=SEQUENTIAL_COLORS,
            opacity=0.7,
        )
        fig_pca.update_layout(
            **PLOTLY_LAYOUT, title="", height=500,
            xaxis_title=f"PC1 ({res['var_explained'][0]:.1%} variance)",
            yaxis_title=f"PC2 ({res['var_explained'][1]:.1%} variance)" if len(res["var_explained"]) > 1 else "PC2",
        )
        st.plotly_chart(fig_pca, width='stretch')

    with col2:
        section_header("Elbow Method", icon="hand-point-right")
        elbow_df = pd.DataFrame(res["inertias"], columns=["K", "Inertia"])
        fig_elbow = px.line(
            elbow_df, x="K", y="Inertia", markers=True,
            color_discrete_sequence=[COLORS["sapphire"]],
        )
        fig_elbow.update_layout(
            **PLOTLY_LAYOUT, title="", height=300,
            xaxis_title="Number of Clusters (K)",
            yaxis_title="Inertia (Within-Cluster SS)",
        )
        # Mark selected k
        fig_elbow.add_vline(x=n_clusters, line_dash="dash", line_color=COLORS["ruby"])
        st.plotly_chart(fig_elbow, width='stretch')

        # Cluster sizes
        section_header("Cluster Sizes", icon="chart-pie")
        sizes = cluster_data["Cluster"].value_counts().sort_index()
        for cl, count in sizes.items():
            pct = count / len(cluster_data) * 100
            stat_card(f"Cluster {cl}", f"{count:,} counties ({pct:.0f}%)",
                     color=["blue", "green", "purple", "amber", "red"][cl % 5])

    # Cluster profiles
    section_header("Cluster Profiles", "Average values per cluster", "id-card")

    profiles = cluster_data.groupby("Cluster")[selected_vars].mean()
    profiles.columns = [get_variable_label(v) for v in selected_vars]

    # Format display
    display_profiles = profiles.copy()
    for col in display_profiles.columns:
        if "Rate" in col or "%" in col:
            display_profiles[col] = display_profiles[col].apply(lambda x: f"{x:.1%}")
        elif "Income" in col or "Cost" in col or "Shortfall" in col:
            display_profiles[col] = display_profiles[col].apply(lambda x: f"${x:,.2f}")
        else:
            display_profiles[col] = display_profiles[col].apply(lambda x: f"{x:,.0f}")

    st.dataframe(display_profiles, width='stretch')

    # Radar chart per cluster
    section_header("Cluster Comparison (Radar)", icon="spider")

    # Normalize for radar
    norm_profiles = (profiles - profiles.min()) / (profiles.max() - profiles.min() + 1e-10)

    fig_radar = go.Figure()
    for cl in norm_profiles.index:
        fig_radar.add_trace(go.Scatterpolar(
            r=norm_profiles.loc[cl].values.tolist() + [norm_profiles.loc[cl].values[0]],
            theta=list(norm_profiles.columns) + [norm_profiles.columns[0]],
            fill="toself",
            name=f"Cluster {cl}",
            opacity=0.6,
        ))
    fig_radar.update_layout(
        **PLOTLY_LAYOUT, title="", height=500,
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
    )
    st.plotly_chart(fig_radar, width='stretch')

    # Geographic distribution
    section_header("Geographic Distribution", icon="map")

    state_cluster = (cluster_data.groupby(["state", "Cluster"]).size()
                     .reset_index(name="Count"))
    state_dominant = (state_cluster.sort_values("Count", ascending=False)
                      .drop_duplicates("state"))

    fig_geo = px.choropleth(
        state_dominant, locations="state", locationmode="USA-states",
        color="Cluster", scope="usa",
        color_discrete_sequence=SEQUENTIAL_COLORS,
        labels={"Cluster": "Dominant Cluster"},
    )
    fig_geo.update_layout(
        **PLOTLY_LAYOUT, title="Dominant Cluster by State", height=450,
        geo=dict(bgcolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(fig_geo, width='stretch')
