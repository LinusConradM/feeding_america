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
from utils.theme import enforce_landscape_on_mobile, inject_tailwind, COLORS, PLOTLY_LAYOUT, SEQUENTIAL_COLORS, page_header
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

    cluster_year = st.slider("Base Year (T1)", int(data["year"].min()), int(data["year"].max()),
                             int(data["year"].max()) - 5)
    
    compare_year = st.selectbox(
        "Compare Year (T2 - Sankey Matrix)",
        ["None"] + sorted(data["year"].unique().tolist(), reverse=True),
        index=1 # Default to the most recent year
    )
    
    n_clusters = st.slider("Number of Clusters", 2, 8, 4)
    selected_vars = st.multiselect(
        "Clustering Variables",
        available_vars,
        default=available_vars[:5],
        format_func=get_variable_label,
    )
    
    st.markdown('<p class="text-white font-semibold text-sm mt-4 mb-2">Spatial Contiguity</p>', unsafe_allow_html=True)
    spatial_weight = st.slider(
        "Geographic Proximity Weight", 0.0, 5.0, 0.0, 0.5,
        help="0 = standard clustering based solely on economic traits. > 0 = forces the algorithm to prioritize grouping counties that are physically close together."
    )

enforce_landscape_on_mobile()
page_header("County Clustering",
            "Segment counties by food insecurity characteristics", "layer-group")

if len(selected_vars) < 2:
    info_banner("Select at least 2 variables for clustering.", "warning")
    st.stop()

# Prepare data
year_data = data[data["year"] == cluster_year].copy()
cluster_data = year_data[["fips", "county", "state", "lat", "lon"] + selected_vars].dropna()

if len(cluster_data) < n_clusters * 3:
    info_banner("Insufficient data for clustering. Try different year or variables.", "warning")
    st.stop()

run_clustering = st.button("Run Clustering", type="primary", width='stretch')

if run_clustering or "cluster_results" in st.session_state:
    if run_clustering:
        # 1. Scale Socioeconomic Vars
        X_econ = cluster_data[selected_vars].values
        scaler_econ = StandardScaler()
        X_econ_scaled = scaler_econ.fit_transform(X_econ)
        
        # 2. Scale Geographic Vars
        X_geo = cluster_data[["lat", "lon"]].values
        scaler_geo = StandardScaler()
        X_geo_scaled = scaler_geo.fit_transform(X_geo) * spatial_weight
        
        # 3. Combine Features
        X_combined = np.hstack([X_econ_scaled, X_geo_scaled])

        # K-Means T1
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_combined)
        cluster_data["Cluster"] = labels
        
        # Calculate T2 if active
        sankey_data = None
        if compare_year != "None":
            t2_data = data[data["year"] == compare_year][["fips"] + selected_vars + ["lat", "lon"]].dropna()
            
            # Inner join to ensure we only track counties that exist in both years
            # We only merge the essential T1 IDs to avoid destroying the main cluster_data column names with suffixes
            merged_flow = pd.merge(cluster_data[["fips", "Cluster"]].rename(columns={"Cluster": "Cluster_t1"}), 
                                   t2_data, on="fips")
            
            if len(merged_flow) > 0:
                # 1. Scale T2 Socioeconomic Vars (no suffix needed now since we didn't suffix T1 columns)
                X_econ_t2 = merged_flow[selected_vars].values
                X_econ_scaled_t2 = scaler_econ.transform(X_econ_t2) # Use T1 scaler to keep relative space
                
                # 2. Scale T2 Geographic Vars
                X_geo_t2 = merged_flow[["lat", "lon"]].values
                X_geo_scaled_t2 = scaler_geo.transform(X_geo_t2) * spatial_weight
                
                # 3. Combine T2 Features
                X_combined_t2 = np.hstack([X_econ_scaled_t2, X_geo_scaled_t2])
                
                # Predict T2 Clusters using T1 model spaces
                labels_t2 = kmeans.predict(X_combined_t2)
                merged_flow["Cluster_t2"] = labels_t2
                

                
                sankey_data = merged_flow.groupby(["Cluster_t1", "Cluster_t2"]).size().reset_index(name="Count")

        # Silhouette
        sil = silhouette_score(X_combined, labels) if n_clusters > 1 else 0

        # PCA - For the 2D visualization, we still just want to see the economic variance, not the raw lat/lon splits
        pca = PCA(n_components=min(2, X_econ_scaled.shape[1]))
        X_pca = pca.fit_transform(X_econ_scaled)

        # Elbow analysis
        inertias = []
        K_range = range(2, min(10, len(cluster_data) // 3))
        for k in K_range:
            km = KMeans(n_clusters=k, random_state=42, n_init=10)
            km.fit(X_combined)
            inertias.append(km.inertia_)

        st.session_state["cluster_results"] = {
            "data": cluster_data.copy(),
            "X_pca": X_pca, "pca": pca,
            "sil": sil, "inertia": kmeans.inertia_,
            "labels": labels,
            "inertias": list(zip(K_range, inertias)),
            "var_explained": pca.explained_variance_ratio_,
            "sankey_data": sankey_data,
            "compare_year": compare_year
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
            color_discrete_sequence=[COLORS["blue"]],
        )
        fig_elbow.update_layout(
            **PLOTLY_LAYOUT, title="", height=300,
            xaxis_title="Number of Clusters (K)",
            yaxis_title="Inertia (Within-Cluster SS)",
        )
        # Mark selected k
        fig_elbow.add_vline(x=n_clusters, line_dash="dash", line_color=COLORS["rose"])
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

    # Transition Matrix (Sankey)
    if res.get("sankey_data") is not None:
        section_header("Cluster Transition Matrix", f"Flow of counties between Vulnerability Profiles ({cluster_year} vs {res['compare_year']})", "random")
        
        s_df = res["sankey_data"]
        
        # Sankey parameters
        # Nodes: T1 clusters (0 to n-1) + T2 clusters (n to 2n-1)
        node_labels = [f"T1 Cluster {i}" for i in range(n_clusters)] + [f"T2 Cluster {i}" for i in range(n_clusters)]
        
        # Colors - match the standard sequence
        c_len = len(SEQUENTIAL_COLORS)
        node_colors = [SEQUENTIAL_COLORS[i % c_len] for i in range(n_clusters)] * 2
        
        # Links
        source = s_df["Cluster_t1"].tolist()
        target = (s_df["Cluster_t2"] + n_clusters).tolist()
        value = s_df["Count"].tolist()
        
        # Link colors (lighter version of source node)
        link_colors = [node_colors[src].replace("rgb", "rgba").replace(")", ", 0.4)") if "rgb" in node_colors[src] else node_colors[src] for src in source]
        
        fig_sankey = go.Figure(data=[go.Sankey(
            node = dict(
              pad = 15,
              thickness = 20,
              line = dict(color = "black", width = 0.5),
              label = node_labels,
              color = node_colors
            ),
            link = dict(
              source = source,
              target = target,
              value = value,
              color = link_colors
          ))])
          
        fig_sankey.update_layout(
            **PLOTLY_LAYOUT, title="", height=500,
            font=dict(size=12, family="Inter, sans-serif")
        )
        st.plotly_chart(fig_sankey, width='stretch')
        
    # Geographic distribution
    section_header("Geographic Distribution", f"View the clustered contiguous zones (T1: {cluster_year})", "map")

    # Force cluster to string for discrete colors
    cluster_data_map = cluster_data.copy()
    cluster_data_map["Cluster"] = cluster_data_map["Cluster"].astype(str)
    
    fig_geo = px.scatter_mapbox(
        cluster_data_map, 
        lat="lat", lon="lon", 
        color="Cluster",
        hover_name="county", hover_data=["state"] + selected_vars,
        color_discrete_sequence=SEQUENTIAL_COLORS,
        zoom=3.5, center={"lat": 39.8283, "lon": -98.5795}
    )
    
    fig_geo.update_layout(
        **PLOTLY_LAYOUT, title="County Clusters Mapping", height=600,
        mapbox_style="carto-positron",
        margin={"r":0,"t":40,"l":0,"b":0}
    )
    st.plotly_chart(fig_geo, width='stretch')
