"""
U.S. Food Insecurity Analytics Platform
Conrad Linus Muhirwe - American University

home.py — Renders the landing page using the exact index.html design.
Every section maps to a template in views/templates/.
"""
import streamlit as st
import warnings
import base64
import logging
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)

warnings.filterwarnings("ignore", message=".*Mean of empty slice.*")
warnings.filterwarnings("ignore", message=".*All-NaN slice encountered.*")

_VIEWS_DIR = Path(__file__).parent          # …/views/
_ROOT_DIR  = _VIEWS_DIR.parent              # project root
_TMPL_DIR  = _VIEWS_DIR / "templates"       # …/views/templates/
_IMG_DIR   = _ROOT_DIR / "images"


# ── OPTIMIZATION: Cached helper functions ────────────────────────────────────
@st.cache_data(show_spinner=False)
def _load_and_encode_image(img_path: str) -> str:
    """Load and base64-encode an image. Cached to avoid re-encoding on every page load.

    Returns an empty string on failure (so callers can keep building the page),
    but logs a warning so the failure is visible in logs instead of being
    silently swallowed — the pre-task-2.4 behavior masked missing-file bugs
    (e.g., the "Critical Path.png" -> "critical_path.png" rename in task 2.6)
    and exception types alike.
    """
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


def _warm_image_cache() -> dict:
    """Eagerly base64-encode every gallery image used on the home page (task 2.4).

    Previously this dict was built at module import time, so the first
    user-facing error from a missing image would surface at app startup —
    before any page even rendered. Wrapping the pre-load in a function lets
    home.py call it once at render time (where the result is needed) and
    keeps the @st.cache_data cache warm thereafter.
    """
    return {
        "overview":   _load_and_encode_image("OverviewPage.png"),
        "map":        _load_and_encode_image("ExplorationMap.png"),
        "data":       _load_and_encode_image("ExplorationDataView.png"),
        "regression": _load_and_encode_image("AnalysisRegression.png"),
        "timeline":   _load_and_encode_image("Timeline.png"),
        "critical":   _load_and_encode_image("critical_path.png"),
    }


IMGS = _warm_image_cache()

# FI rate ticker lives in utils/ticker.py (task 2.2: single source of truth
# shared with the global nav ribbon to avoid two load_data() reads per page).
from utils.ticker import get_fi_ticker_html as _get_fi_ticker_html


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
def _compute_home_kpis() -> dict:
    """Compute all four home-page KPIs from load_data() (task 2.1).

    Returns a dict of placeholder -> formatted string. All four values are
    derived from the same load_data() call so the page stays internally
    consistent even if the data file is updated.

    Falls back to em-dash + 'Source unavailable' on any exception — never
    silently returns the historical hardcoded values ('44.2M', '3,100+', etc).
    """
    try:
        from utils.data_loader import load_data

        _df = load_data()
        _latest_year = int(_df["year"].max())
        _earliest_year = int(_df["year"].min())
        _latest = _df[_df["year"] == _latest_year]

        _total_persons = float(_latest["no_of_food_insecure_persons_overall"].sum())
        _counties = int(_df["fips"].nunique())
        _span = _latest_year - _earliest_year + 1
        _obs = len(_df)

        return {
            "americans_val": f"{_total_persons / 1_000_000:.1f}M",
            "americans_note": f"Feeding America MMG · {_latest_year}",
            "counties_val": f"{_counties:,}",
            "span_val": f"{_span} yrs",
            "obs_val": f"{_obs:,}",
        }
    except Exception:
        return {
            "americans_val": "—",
            "americans_note": "Source unavailable",
            "counties_val": "—",
            "span_val": "—",
            "obs_val": "—",
        }


@st.cache_data(show_spinner=False, ttl=3600)
def _get_kpi_html() -> str:
    """Render the KPI strip with all four values computed live from load_data().

    The historical hardcoded values (44.2M, 3,100+, 15 yrs, 47K+) were either
    unverifiable (Q2 in HOME_REDESIGN_DECISIONS.md for 44.2M) or drift-prone
    snapshots that go stale every data refresh. _compute_home_kpis() fills all
    four placeholders from the latest load_data() so the strip always reflects
    the data actually being analyzed.
    """
    kpis = _compute_home_kpis()
    return (
        _load_template("kpi.html")
        .replace("__KPI_AMERICANS_VAL__", kpis["americans_val"])
        .replace("__KPI_AMERICANS_NOTE__", kpis["americans_note"])
        .replace("__KPI_COUNTIES_VAL__", kpis["counties_val"])
        .replace("__KPI_SPAN_VAL__", kpis["span_val"])
        .replace("__KPI_OBS_VAL__", kpis["obs_val"])
    )


st.html(_get_kpi_html())

# MMG methodology disclaimer (task 2.5). The Map the Meal Gap methodology was
# revised in 2020; before/after series are not perfectly comparable. Surface
# the caveat next to the headline numbers so policymaker/researcher audiences
# can interpret the figures correctly.
st.html(
    '<small class="mmg-disclaimer" '
    'style="display:block;text-align:center;font-size:0.78rem;line-height:1.45;'
    'color:rgba(220,225,240,0.55);margin:0.25rem auto 1.5rem;max-width:780px;'
    'padding:0 1rem;">'
    'Estimates derived from Feeding America\'s '
    '<a href="https://map.feedingamerica.org" target="_blank" rel="noopener" '
    'style="color:rgba(220,225,240,0.7);text-decoration:underline;">'
    'Map the Meal Gap'
    '</a>. Methodology revised in 2020; pre- and post-2020 series are not '
    'directly comparable.'
    '</small>'
)


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

  // Attach to every nav menu item that has data-img.
  // Selector matches `.app-menu-item` in views/templates/nav.html — the
  // previous `.menu-item` selector never matched, leaving the reactive-
  // screenshot feature dead on the live site (task 2.3).
  document.querySelectorAll('.app-menu-item[data-img]').forEach(function(el) {{
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
