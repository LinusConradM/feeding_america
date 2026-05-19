"""
Global Navigation Ribbon extracted from home.py
"""
import streamlit as st
import base64
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_UTILS_DIR = Path(__file__).parent
_ROOT_DIR = _UTILS_DIR.parent
_VIEWS_DIR = _ROOT_DIR / "views"
_TMPL_DIR = _VIEWS_DIR / "templates"
_IMG_DIR = _ROOT_DIR / "images"

@st.cache_data(show_spinner=False)
def _load_and_encode_image(img_path: str) -> str:
    """Load and base64-encode an image. Logs warnings on failure so missing
    files / encode errors are visible in logs (task 2.4) instead of being
    silently swallowed into an empty string."""
    path = _IMG_DIR / img_path
    if not path.exists():
        logger.warning("Image file not found: %s (resolved: %s)", img_path, path)
        return ""
    try:
        return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()
    except Exception:
        logger.exception("Failed to base64-encode image: %s", path)
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

# FI rate ticker lives in utils/ticker.py (task 2.2: single source of truth
# shared with views/home.py to avoid two load_data() reads per page).
from utils.ticker import get_fi_ticker_html as _get_fi_ticker_html

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
        "critical":   _load_and_encode_image("critical_path.png"),
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
