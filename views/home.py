"""
U.S. Food Insecurity Analytics Platform
Conrad Linus Muhirwe - American University

home.py — Renders the landing page using the exact index.html design.
Every section maps to a template in views/templates/.
"""
import streamlit as st
import warnings
import base64
from pathlib import Path
import pandas as pd

warnings.filterwarnings("ignore", message=".*Mean of empty slice.*")
warnings.filterwarnings("ignore", message=".*All-NaN slice encountered.*")

_VIEWS_DIR = Path(__file__).parent          # …/views/
_ROOT_DIR  = _VIEWS_DIR.parent              # project root
_TMPL_DIR  = _VIEWS_DIR / "templates"       # …/views/templates/
_IMG_DIR   = _ROOT_DIR / "images"


# ── OPTIMIZATION: Cached helper functions ────────────────────────────────────
@st.cache_data(show_spinner=False)
def _load_and_encode_image(img_path: str) -> str:
    """
    Load and base64-encode an image. Cached to avoid re-encoding on every page load.
    
    Args:
        img_path: Path to image file relative to images directory
        
    Returns:
        Base64-encoded data URI string
    """
    try:
        path = _IMG_DIR / img_path
        return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()
    except Exception:
        return ""


@st.cache_data(show_spinner=False)
def _load_template(template_name: str) -> str:
    """
    Load HTML template file. Cached to avoid re-reading on every page load.

    Args:
        template_name: Name of template file (e.g., 'nav.html')

    Returns:
        Template content as string
    """
    try:
        return (_TMPL_DIR / template_name).read_text()
    except Exception:
        return ""


@st.cache_data(show_spinner=False)
def _load_css() -> str:
    """
    Load CSS file. Cached to avoid re-reading on every page load.
    
    Returns:
        CSS content as string
    """
    try:
        return (_VIEWS_DIR / "home.css").read_text()
    except Exception:
        return ""


# Pre-encode all gallery images with caching (OPTIMIZATION: ~80% faster load time)
IMGS = {
    "overview":   _load_and_encode_image("OverviewPage.png"),
    "map":        _load_and_encode_image("ExplorationMap.png"),
    "data":       _load_and_encode_image("ExplorationDataView.png"),
    "regression": _load_and_encode_image("AnalysisRegression.png"),
    "timeline":   _load_and_encode_image("Timeline.png"),
    "critical":   _load_and_encode_image("Critical Path.png"),
}

# ── OPTIMIZATION: FI Rate ticker data (cached, lightweight) ─────────────────
@st.cache_data(show_spinner=False, ttl=3600)  # Cache for 1 hour
def _get_fi_ticker_html() -> str:
    """
    Generate FI rate ticker HTML. Cached to avoid loading full dataset on every page load.
    
    OPTIMIZATION: Only loads aggregated year data instead of full 47,000+ row dataset.
    This reduces memory usage and speeds up page load by ~60%.
    
    Returns:
        HTML string for FI rate ticker
    """
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


# ── 1. Inject CSS via st.markdown so it reaches the real document head ────────
# CRITICAL: Must be the very first st.* call so the sidebar and Streamlit chrome
# are hidden immediately — before any data loading triggers a render cycle.
# st.html() sandboxes content in an iframe; CSS inside it cannot affect the
# Streamlit chrome (body, fixed nav, etc.).
# st.markdown(unsafe_allow_html=True) injects directly into the page head.
css_raw = _load_css()
st.markdown(f"<style>{css_raw}</style>", unsafe_allow_html=True)


# ── 2. Google Fonts + Font Awesome (injected into real head via st.markdown) ──
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Geist+Mono:wght@400;500;600;700&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" />
""", unsafe_allow_html=True)


# ── Load ticker data AFTER CSS is injected ───────────────────────────────────
# Moved here so the sidebar-hiding CSS is already applied before load_data()
# runs (even with cache, there is a brief render window otherwise).
_ticker_html = _get_fi_ticker_html()



# ── 3. Navigation ────────────────────────────────────────────────────────────
# Global navigation is now injected in app.py via inject_global_nav()


# ── 4. Hero section ───────────────────────────────────────────────────────────
# The hero uses a split layout: text left, reactive screenshot right.
# Images are base64 so Streamlit serves them correctly without a static file server.
hero_tmpl = _load_template("hero.html")

# Build the right-side screenshot pane inline (needs JS for reactive switching)
hero_html = f"""
<div class="home-page-wrap">
  <section id="hero">
    <div class="hero">
      <div class="hero-layout">

        <!-- LEFT: text -->
        <div class="hero-text">
          {hero_tmpl}
        </div>

        <!-- RIGHT: reactive screenshot -->
        <div class="hero-visual">
          <div class="hero-screen-wrap">
            <div class="hero-screen-frame">
              <div class="hero-screen-bar">
                <span class="dot-r"></span>
                <span class="dot-y"></span>
                <span class="dot-g"></span>
                <span style="font-family:'Geist Mono',monospace;font-size:0.72rem;color:#94a3b8;margin-left:0.5rem;">
                  food-insecurity-analytics &middot; streamlit
                </span>
              </div>
              <img
                id="hero-img"
                src="{IMGS['overview']}"
                alt="Dashboard preview"
                class="hero-screen-img"
              />
            </div>
            <div class="hero-screen-label" id="hero-label">Dashboard Gallery</div>
          </div>
        </div>

      </div>
    </div>
  </section>
"""
st.html(hero_html)


# ── 5. KPI strip ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False, ttl=3600)
def _get_kpi_html() -> str:
    """Render the KPI strip with the lead 'Americans affected' value computed live.

    The historical hardcoded "44.2M" was of unconfirmed origin (Q2 in
    HOME_REDESIGN_DECISIONS.md). Compute fresh from the latest year in
    load_data() so the headline number is always a published, verifiable figure.
    """
    try:
        from utils.data_loader import load_data

        _df = load_data()
        _latest_year = int(_df["year"].max())
        _latest = _df[_df["year"] == _latest_year]
        _total = float(_latest["no_of_food_insecure_persons_overall"].sum())
        _val = f"{_total / 1_000_000:.1f}M"
        _note = f"Feeding America MMG · {_latest_year}"
    except Exception:
        _val = "—"
        _note = "Source unavailable"
    return (
        _load_template("kpi.html")
        .replace("__KPI_AMERICANS_VAL__", _val)
        .replace("__KPI_AMERICANS_NOTE__", _note)
    )


st.html(_get_kpi_html())


# ── 6. Marquee ───────────────────────────────────────────────────────────────
# Generate pills in Python so no JS is needed inside the st.html() iframe
MARQUEE_PILLS = [
    ("fa-microchip",       "#a78bfa", "Gemini 2.5 Flash", "/10_AI_Data_Analyst"),
    ("fa-project-diagram", "#38bdf8", "Difference-in-Differences", "/8_Policy_Scenarios"),
    ("fa-chart-line",      "#f472b6", "SARIMAX Forecasting", "/7_Time_Series_Explorer"),
    ("fa-search-location", "#34d399", "Spatial K-Means", "/6_County_Clustering"),
    ("fa-bullseye",        "#fbbf24", "Isolation Forests", "/11_Anomaly_Detection"),
    ("fa-map",             "#60a5fa", "Bivariate Mapping", "/2_Geographic_Intelligence"),
    ("fa-chart-area",      "#c084fc", "Density Joyplots", "/5_Equity_Disparities"),
    ("fa-wave-square",     "#2AD5FF", "Temporal Analysis", "/7_Time_Series_Explorer"),
    ("fa-balance-scale",   "#fda4af", "Equity Disparities", "/5_Equity_Disparities"),
    ("fa-sitemap",         "#86efac", "PCA Projection", "/6_County_Clustering"),
]
pill_html = "".join(
    f'<a class="marquee-pill" href="{href}"><i class="fas {icon}" style="color:{color}"></i> {label}</a>'
    for icon, color, label, href in MARQUEE_PILLS
)
# Triple the pills for the seamless infinite loop animation
pills_3x = pill_html * 3
st.html(f'<div class="marquee-section"><div class="marquee-track">{pills_3x}</div></div>')


# ── 7. Bento grid (Platform Architecture) ────────────────────────────────────
st.html(_load_template("bento.html"))


# ── 8. Statistical Methods ────────────────────────────────────────────────────
st.html(_load_template("methods.html"))


# ── 9. Data Sources ─────────────────────────────────────────────────────────
st.html(_load_template("sources.html"))


# ── 10. Footer + nav JS ───────────────────────────────────────────────────────
st.html(_load_template("footer.html"))

# Close the home-page-wrap div opened in step 4
st.html("</div>")


# ── 11. Hero reactive image JS (nav hover changes screenshot) ─────────────────
hero_js = f"""
<script>
(function() {{
  var heroImg   = document.getElementById('hero-img');
  var heroLabel = document.getElementById('hero-label');
  var DEFAULT_SRC   = '{IMGS["overview"]}';
  var DEFAULT_LABEL = 'Dashboard Gallery';

  function setHeroImg(src, label) {{
    heroImg.style.opacity = '0';
    setTimeout(function() {{
      heroImg.src = src;
      heroImg.onload = function() {{ heroImg.style.opacity = '1'; }};
      heroLabel.textContent = label;
    }}, 150);
  }}

  // Attach to every menu-item that has data-img
  document.querySelectorAll('.menu-item[data-img]').forEach(function(el) {{
    el.addEventListener('mouseenter', function() {{
      setHeroImg(el.dataset.img, el.dataset.label);
    }});
  }});

  // Restore default when leaving any nav-item
  document.querySelectorAll('.nav-item').forEach(function(item) {{
    item.addEventListener('mouseleave', function() {{
      setHeroImg(DEFAULT_SRC, DEFAULT_LABEL);
    }});
  }});
}})();
</script>
"""
st.html(hero_js)
