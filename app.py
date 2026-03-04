"""
U.S. Food Insecurity Analytics Platform
Conrad Linus Muhirwe — American University
"""
import streamlit as st
import pandas as pd
import warnings

# Suppress expected numpy warnings when calculating aggregations on all-NaN slices
warnings.filterwarnings("ignore", message=".*Mean of empty slice.*")
warnings.filterwarnings("ignore", message=".*All-NaN slice encountered.*")

from utils.theme import inject_tailwind
from utils.data_loader import load_data

st.set_page_config(
    page_title="U.S. Food Insecurity Analytics",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_tailwind()

# ── Pre-warm data cache ───────────────────────────────────────────────────────
# load_data() reads ~10.7 MB of Excel files the first time it runs.
# Calling it here (before pg.run()) means the cache is hot before any page
# executes, so the home page — and every other page — never blocks on I/O.
# @st.cache_data ensures this only does real work once per Streamlit process;
# all subsequent calls return the cached DataFrame instantly.
load_data()

# ── Sidebar Branding ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center;padding:2rem 0 1.5rem">
            <div style="background: linear-gradient(135deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.25rem; margin-bottom: 0.5rem; filter: drop-shadow(0 0 10px rgba(56, 189, 248, 0.4));">🌾</div>
            <div style="font-family:'SF Pro Display','Inter',sans-serif;font-size:1.25rem;font-weight:800;letter-spacing:-0.02em;color:#f8fafc">
                Food Insecurity
            </div>
            <div style="font-family:'Inter',sans-serif;font-size:0.75rem;letter-spacing:0.15em;text-transform:uppercase;color:#94a3b8;margin-top:0.25rem;font-weight:600;">
                Analytics Engine
            </div>
        </div>
        <hr style="border:none;border-top:1px solid rgba(255,255,255,.05);margin:0 0 1.5rem">
        """,
        unsafe_allow_html=True,
    )

# ── Navigation Configuration ──────────────────────────────────────────────────
# Main group
home_page = st.Page("views/home.py", title="Home", icon="🏠", default=True, url_path="")
exec_page = st.Page(
    "views/1_Executive_Overview.py",
    title="Executive Overview",
    icon="📊",
    url_path="1_Executive_Overview",
)
geo_page = st.Page(
    "views/2_Geographic_Intelligence.py",
    title="Geographic Intelligence",
    icon="🗺️",
    url_path="2_Geographic_Intelligence",
)

# Analytics group bundle
explorer_page = st.Page("views/0_Data_Explorer.py", title="Data Explorer", icon="🔬", url_path="0_Data_Explorer")
corr_page = st.Page("views/3_Correlation_Analysis.py", title="Correlation Analysis", icon="📈", url_path="3_Correlation_Analysis")
reg_page = st.Page("views/4_Regression_Models.py", title="Regression Models", icon="📉", url_path="4_Regression_Models")
equity_page = st.Page("views/5_Equity_Disparities.py", title="Equity Disparities", icon="⚖️", url_path="5_Equity_Disparities")
cluster_page = st.Page("views/6_County_Clustering.py", title="County Clustering", icon="🧩", url_path="6_County_Clustering")
time_page = st.Page("views/7_Time_Series_Explorer.py", title="Time Series Explorer", icon="⏳", url_path="7_Time_Series_Explorer")
anomaly_page = st.Page("views/11_Anomaly_Detection.py", title="Anomaly Detection", icon="📡", url_path="11_Anomaly_Detection")

# Advanced AI
ai_page = st.Page("views/10_AI_Data_Analyst.py", title="AI Data Analyst", icon="🤖", url_path="10_AI_Data_Analyst")

# Planning & Data group
policy_page = st.Page("views/8_Policy_Scenarios.py", title="Policy Scenarios", icon="🔮", url_path="8_Policy_Scenarios")
data_page = st.Page("views/9_Data_Downloads.py", title="Data Downloads", icon="💾", url_path="9_Data_Downloads")

# Define the router without Streamlit's default flat visuals
pg = st.navigation([
    home_page, exec_page, geo_page,
    explorer_page, corr_page, reg_page, equity_page, cluster_page, anomaly_page, time_page,
    ai_page,
    policy_page, data_page
], position="hidden")

# Build the custom expandable sidebar menu
# Hide navigation on Executive Overview page (it has its own custom sidebar)
if pg != exec_page:
    with st.sidebar:
        st.page_link(home_page, label="Home", icon="🏠")
        st.page_link(exec_page, label="Executive Overview", icon="📊")
        st.page_link(geo_page, label="Geographic Intelligence", icon="🗺️")
        
        with st.expander("Analytics", expanded=False, icon="🧠"):
            st.page_link(explorer_page, label="Data Explorer", icon="🔬")
            st.page_link(corr_page, label="Correlation Analysis", icon="📈")
            st.page_link(reg_page, label="Regression Models", icon="📉")
            st.page_link(equity_page, label="Equity Disparities", icon="⚖️")
            st.page_link(cluster_page, label="County Clustering", icon="🧩")
            st.page_link(anomaly_page, label="Anomaly Detection", icon="📡")
            st.page_link(time_page, label="Time Series Explorer", icon="⏳")

        with st.expander("Agentic AI", expanded=False, icon="🤖"): # New expander for Agentic AI
            st.page_link(ai_page, label="AI Data Analyst", icon="🤖")
            
        st.page_link(policy_page, label="Policy Scenarios", icon="🔮")
        st.page_link(data_page, label="Data Downloads", icon="💾")

# Run the selected page
pg.run()
