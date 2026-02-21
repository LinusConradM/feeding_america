"""
U.S. Food Insecurity Analytics Platform
Conrad Linus Muhirwe - American University
"""
import streamlit as st
import warnings
import base64
import os

from utils.theme import inject_tailwind

# Suppress expected numpy warnings when calculating aggregations on all-NaN slices
warnings.filterwarnings("ignore", message=".*Mean of empty slice.*")
warnings.filterwarnings("ignore", message=".*All-NaN slice encountered.*")

def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        return ""

bg_img_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "hero_bg.png")
bg_url = f"url('data:image/png;base64,{get_base64_of_bin_file(bg_img_path)}')"


with open("views/home.css", "r") as f:
    custom_css = f.read()

custom_css = custom_css.replace('___BG_URL___', bg_url)

st.html(custom_css)
# ── HERO TEXT ────────────────────────────────────────────────────────────────
from pathlib import Path
st.html(Path("views/templates/hero.html").read_text())


# ── KPI GLASS ROW ────────────────────────────────────────────────────────────
st.html(Path("views/templates/kpi.html").read_text())

st.markdown("<div style='height: 1.5rem'></div>", unsafe_allow_html=True)

# ── NATIVE STREAMLIT CTA BUTTONS ─────────────────────────────────────────────
# This seamlessly flows within the Streamlit DOM, fixing the overlay mismatch.
col1, col2, _ = st.columns([1.5, 1.5, 7])
with col1:
    if st.button("Explore Dashboards", width='stretch'):
        st.switch_page("views/1_Executive_Overview.py")
with col2:
    if st.button("Launch AI Agent", width='stretch'):
        st.switch_page("views/10_AI_Data_Analyst.py")

# ── V2 TECH STACK MARQUEE ────────────────────────────────────────────────────
marquee_items = [
    ('<i class="fas fa-microchip" style="color:#a78bfa"></i> Gemini 2.5 Flash', 'AI_Data_Analyst'),
    ('<i class="fas fa-project-diagram" style="color:#38bdf8"></i> Difference-in-Differences', 'Policy_Scenarios'),
    ('<i class="fas fa-chart-line" style="color:#f472b6"></i> SARIMAX Forecasting', 'Time_Series_Explorer'),
    ('<i class="fas fa-search-location" style="color:#34d399"></i> Spatial K-Means', 'County_Clustering'),
    ('<i class="fas fa-bullseye" style="color:#fbbf24"></i> Isolation Forests', 'Anomaly_Detection'),
    ('<i class="fas fa-map" style="color:#60a5fa"></i> Bivariate Mapping', 'Geographic_Intelligence'),
    ('<i class="fas fa-chart-area" style="color:#a78bfa"></i> Density Joyplots', 'Data_Explorer'),
]
marquee_text = "".join([f'<a href="{url}" target="_self" class="marquee-item" style="text-decoration: none; cursor: pointer;">{item}</a>' for item, url in marquee_items])
marquee_text = marquee_text + marquee_text + marquee_text # Triple for smooth infinite loop

marquee_template = Path("views/templates/marquee.html").read_text()
st.html(marquee_template.format(marquee_text=marquee_text))



# ── V2 VIBRANT BENTO GRID ─────────────────────────────────────────────────────
st.markdown('<h2 style="font-family:\'SF Pro Display\',\'Inter\',sans-serif;font-size:2.2rem;font-weight:700;color:#FFFFFF;margin-bottom:2rem;letter-spacing:-0.02em;">Platform Architecture</h2>', unsafe_allow_html=True)

st.html(Path("views/templates/bento.html").read_text())




# ── FOOTER ───────────────────────────────────────────────────────────────────
st.html(Path("views/templates/footer.html").read_text())


