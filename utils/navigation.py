"""
Global Navigation Ribbon extracted from home.py
"""
import streamlit as st
import base64
from pathlib import Path

_UTILS_DIR = Path(__file__).parent
_ROOT_DIR = _UTILS_DIR.parent
_VIEWS_DIR = _ROOT_DIR / "views"
_TMPL_DIR = _VIEWS_DIR / "templates"
_IMG_DIR = _ROOT_DIR / "images"

@st.cache_data(show_spinner=False)
def _load_and_encode_image(img_path: str) -> str:
    try:
        path = _IMG_DIR / img_path
        if path.exists():
            return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()
    except Exception:
        pass
    return ""

@st.cache_data(show_spinner=False)
def _load_template(template_name: str) -> str:
    try:
        path = _TMPL_DIR / template_name
        if path.exists():
            return path.read_text()
    except Exception:
        pass
    return ""

@st.cache_data(show_spinner=False, ttl=3600)
def _get_fi_ticker_html() -> str:
    try:
        from utils.data_loader import load_data, weighted_rate_by_group
        _df = load_data()
        _fi_years = (
            weighted_rate_by_group(_df, "overall_food_insecurity_rate", "year")
            .dropna()
            .round(4)
            .sort_index()
        )
        items = []
        prev_year = None
        for y, v in _fi_years.items():
            y = int(y)
            if prev_year is not None and y - prev_year > 1:
                lo, hi = prev_year + 1, y - 1
                label = f"{lo}" if lo == hi else f"{lo}-{hi}"
                items.append(
                    f'<span class=\"fi-ticker-item fi-ticker-gap\">Coverage gap: {label}</span>'
                )
            items.append(f'<span class=\"fi-ticker-item\">{y} FI Rate = {v:.1%}</span>')
            prev_year = y
        _ticker_items = "".join(items) or '<span class=\"fi-ticker-item\">FI rates unavailable</span>'
        return (
            '<div class=\"fi-ticker\"><div class=\"fi-ticker-track\">'
            f'{_ticker_items*3}'
            '</div></div>'
        )
    except Exception:
        return '<div class=\"fi-ticker\"><div class=\"fi-ticker-track\"><span class=\"fi-ticker-item\">FI rates unavailable</span></div></div>'

def inject_global_nav():
    """Injects the global top ribbon navigation bar into the app."""
    nav_tmpl = _load_template("nav.html")
    if not nav_tmpl:
        return

    IMGS = {
        "overview":   _load_and_encode_image("OverviewPage.png"),
        "map":        _load_and_encode_image("ExplorationMap.png"),
        "data":       _load_and_encode_image("ExplorationDataView.png"),
        "regression": _load_and_encode_image("AnalysisRegression.png"),
        "timeline":   _load_and_encode_image("Timeline.png"),
        "critical":   _load_and_encode_image("Critical Path.png"),
    }

    _ticker_html = _get_fi_ticker_html()

    nav_html = (nav_tmpl
        .replace("___IMG_OVERVIEW___",   IMGS["overview"])
        .replace("___IMG_MAP___",        IMGS["map"])
        .replace("___IMG_REGRESSION___", IMGS["regression"])
        .replace("___IMG_TIMELINE___",   IMGS["timeline"])
        .replace("__FI_TICKER__", _ticker_html)
    )

    css_path = _UTILS_DIR / "nav.css"
    nav_css = css_path.read_text() if css_path.exists() else ""
    
    # Hide Streamlit header at the top
    global_rules = """
        <style>
        header[data-testid="stHeader"] { display: none !important; }
        /* Add padding to Streamlit's main container so content doesn't hide behind the navbar */
        .block-container { padding-top: 80px !important; }
        </style>
    """

    st.markdown(global_rules, unsafe_allow_html=True)
    st.markdown(f"<style>{nav_css}</style>", unsafe_allow_html=True)
    
    st.html(nav_html)
