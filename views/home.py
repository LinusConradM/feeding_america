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

warnings.filterwarnings("ignore", message=".*Mean of empty slice.*")
warnings.filterwarnings("ignore", message=".*All-NaN slice encountered.*")

_VIEWS_DIR = Path(__file__).parent          # …/views/
_ROOT_DIR  = _VIEWS_DIR.parent              # project root
_TMPL_DIR  = _VIEWS_DIR / "templates"       # …/views/templates/
_IMG_DIR   = _ROOT_DIR / "images"


# ── Helper: embed image as base64 data-URI ────────────────────────────────────
def b64_img(path: Path) -> str:
    """Return a data:image/png;base64,… URI for the image at `path`."""
    try:
        return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()
    except Exception:
        return ""


# Pre-encode all gallery images so Streamlit can render them inside st.html()
IMGS = {
    "overview":   b64_img(_IMG_DIR / "OverviewPage.png"),
    "map":        b64_img(_IMG_DIR / "ExplorationMap.png"),
    "data":       b64_img(_IMG_DIR / "ExplorationDataView.png"),
    "regression": b64_img(_IMG_DIR / "AnalysisRegression.png"),
    "timeline":   b64_img(_IMG_DIR / "Timeline.png"),
    "critical":   b64_img(_IMG_DIR / "Critical Path.png"),
}


# ── 1. Inject CSS via st.markdown so it reaches the real document head ────────
# CRITICAL: st.html() sandboxes content in an iframe; CSS inside it cannot
# affect the Streamlit chrome (body, fixed nav, etc.).
# st.markdown(unsafe_allow_html=True) injects directly into the page head.
css_raw = (_VIEWS_DIR / "home.css").read_text()
st.markdown(f"<style>{css_raw}</style>", unsafe_allow_html=True)


# ── 2. Google Fonts + Font Awesome (injected into real head via st.markdown) ──
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Geist+Mono:wght@400;500;600;700&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" />
""", unsafe_allow_html=True)



# ── 3. Navigation ────────────────────────────────────────────────────────────
nav_tmpl = (_TMPL_DIR / "nav.html").read_text()
nav_html = (nav_tmpl
    .replace("___IMG_OVERVIEW___",   IMGS["overview"])
    .replace("___IMG_MAP___",        IMGS["map"])
    .replace("___IMG_REGRESSION___", IMGS["regression"])
    .replace("___IMG_TIMELINE___",   IMGS["timeline"])
)
st.html(nav_html)


# ── 4. Hero section ───────────────────────────────────────────────────────────
# The hero uses a split layout: text left, reactive screenshot right.
# Images are base64 so Streamlit serves them correctly without a static file server.
hero_tmpl = (_TMPL_DIR / "hero.html").read_text()

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
            <div class="hero-screen-label" id="hero-label">Executive Overview — National KPIs</div>
          </div>
        </div>

      </div>
    </div>
  </section>
"""
st.html(hero_html)


# ── 5. KPI strip ─────────────────────────────────────────────────────────────
st.html((_TMPL_DIR / "kpi.html").read_text())


# ── 6. Marquee ───────────────────────────────────────────────────────────────
# Generate pills in Python so no JS is needed inside the st.html() iframe
MARQUEE_PILLS = [
    ("fa-microchip",       "#a78bfa", "Gemini 2.5 Flash"),
    ("fa-project-diagram", "#38bdf8", "Difference-in-Differences"),
    ("fa-chart-line",      "#f472b6", "SARIMAX Forecasting"),
    ("fa-search-location", "#34d399", "Spatial K-Means"),
    ("fa-bullseye",        "#fbbf24", "Isolation Forests"),
    ("fa-map",             "#60a5fa", "Bivariate Mapping"),
    ("fa-chart-area",      "#c084fc", "Density Joyplots"),
    ("fa-wave-square",     "#2AD5FF", "Temporal Analysis"),
    ("fa-balance-scale",   "#fda4af", "Equity Disparities"),
    ("fa-sitemap",         "#86efac", "PCA Projection"),
]
pill_html = "".join(
    f'<span class="marquee-pill"><i class="fas {icon}" style="color:{color}"></i> {label}</span>'
    for icon, color, label in MARQUEE_PILLS
)
# Triple the pills for the seamless infinite loop animation
pills_3x = pill_html * 3
st.html(f'<div class="marquee-section"><div class="marquee-track">{pills_3x}</div></div>')


# ── 7. Bento grid (Platform Architecture) ────────────────────────────────────
st.html((_TMPL_DIR / "bento.html").read_text())


# ── 8. Dashboard Gallery ─────────────────────────────────────────────────────
gallery_tmpl = (_TMPL_DIR / "gallery.html").read_text()
gallery_html = (gallery_tmpl
    .replace("___IMG_OVERVIEW___",   IMGS["overview"])
    .replace("___IMG_MAP___",        IMGS["map"])
    .replace("___IMG_DATA___",       IMGS["data"])
    .replace("___IMG_REGRESSION___", IMGS["regression"])
    .replace("___IMG_TIMELINE___",   IMGS["timeline"])
    .replace("___IMG_CRITICAL___",   IMGS["critical"])
)
st.html(gallery_html)


# ── 9. Statistical Methods ────────────────────────────────────────────────────
st.html((_TMPL_DIR / "methods.html").read_text())


# ── 10. Data Sources ─────────────────────────────────────────────────────────
st.html((_TMPL_DIR / "sources.html").read_text())


# ── 11. Footer + nav JS ───────────────────────────────────────────────────────
st.html((_TMPL_DIR / "footer.html").read_text())

# Close the home-page-wrap div opened in step 4
st.html("</div>")


# ── 12. Hero reactive image JS (nav hover changes screenshot) ─────────────────
hero_js = f"""
<script>
(function() {{
  var heroImg   = document.getElementById('hero-img');
  var heroLabel = document.getElementById('hero-label');
  var DEFAULT_SRC   = '{IMGS["overview"]}';
  var DEFAULT_LABEL = 'Executive Overview — National KPIs';

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
