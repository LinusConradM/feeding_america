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

from utils.theme import inject_tailwind, inject_main_landmark
from utils.data_loader import load_data
from utils.navigation import inject_global_nav

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
# We no longer need sidebar branding since the global ribbon covers it


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

# Inject Global Navigation Ribbon
inject_global_nav()

# Phase 4.4: skip-link target. Must come AFTER inject_global_nav() so the
# anchor is positioned past the navigation in the DOM — that's what makes
# the skip-link a real time-saver for keyboard users.
inject_main_landmark()

# Run the selected page
pg.run()

