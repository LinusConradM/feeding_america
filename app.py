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

st.set_page_config(
    page_title="U.S. Food Insecurity Analytics",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_tailwind()

# ── Sidebar Branding ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center;padding:1.5rem 0 1rem">
            <div style="font-size:2rem;margin-bottom:.5rem">🌾</div>
            <div style="font-family:'Inter',sans-serif;font-size:1.1rem;font-weight:700;color:#fff">
                Food Insecurity
            </div>
            <div style="font-size:.72rem;letter-spacing:.08em;text-transform:uppercase;
                        color:rgba(255,255,255,.5);margin-top:.15rem">
                Analytics Platform
            </div>
        </div>
        <hr style="border:none;border-top:1px solid rgba(255,255,255,.12);margin:0 0 1rem">
        """,
        unsafe_allow_html=True,
    )

# ── Navigation Configuration ──────────────────────────────────────────────────
# Main group
home_page = st.Page("views/home.py", title="Home", icon="🏠", default=True)
exec_page = st.Page("views/1_Executive_Overview.py", title="Executive Overview", icon="📊")
geo_page = st.Page("views/2_Geographic_Intelligence.py", title="Geographic Intelligence", icon="🗺️")

# Analytics group bundle
corr_page = st.Page("views/3_Correlation_Analysis.py", title="Correlation Analysis", icon="📈")
reg_page = st.Page("views/4_Regression_Models.py", title="Regression Models", icon="📉")
equity_page = st.Page("views/5_Equity_Disparities.py", title="Equity Disparities", icon="⚖️")
cluster_page = st.Page("views/6_County_Clustering.py", title="County Clustering", icon="🧩")
time_page = st.Page("views/7_Time_Series_Explorer.py", title="Time Series Explorer", icon="⏳")

# Planning & Data group
policy_page = st.Page("views/8_Policy_Scenarios.py", title="Policy Scenarios", icon="🔮")
data_page = st.Page("views/9_Data_Downloads.py", title="Data Downloads", icon="💾")

# Define the router without Streamlit's default flat visuals
pg = st.navigation([
    home_page, exec_page, geo_page,
    corr_page, reg_page, equity_page, cluster_page, time_page,
    policy_page, data_page
], position="hidden")

# Build the custom expandable sidebar menu
with st.sidebar:
    st.page_link(home_page, label="Home", icon="🏠")
    st.page_link(exec_page, label="Executive Overview", icon="📊")
    st.page_link(geo_page, label="Geographic Intelligence", icon="🗺️")
    
    with st.expander("Analytics", expanded=False, icon="🧠"):
        st.page_link(corr_page, label="Correlation Analysis", icon="📈")
        st.page_link(reg_page, label="Regression Models", icon="📉")
        st.page_link(equity_page, label="Equity Disparities", icon="⚖️")
        st.page_link(cluster_page, label="County Clustering", icon="🧩")
        st.page_link(time_page, label="Time Series Explorer", icon="⏳")
        
    st.page_link(policy_page, label="Policy Scenarios", icon="🔮")
    st.page_link(data_page, label="Data Downloads", icon="💾")

# Run the selected page
pg.run()
