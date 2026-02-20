"""
Reusable UI components — McKinsey-grade design.
White cards, left accent bars, Georgia serif numbers, high-contrast.
"""

import streamlit as st


# ── KPI Card ─────────────────────────────────────────────────────────────────
_ACCENT_MAP = {
    "sapphire": "accent-blue",
    "blue": "accent-blue",
    "ruby": "accent-red",
    "coral": "accent-red",
    "emerald": "accent-green",
    "teal": "accent-green",
    "amber": "accent-amber",
    "amethyst": "accent-purple",
    "plum": "accent-purple",
    "navy": "accent-dark",
    "dark": "accent-dark",
}


def kpi_card(
    title: str,
    value: str,
    change: str = "",
    icon: str = "chart-line",
    gradient: str = "sapphire",   # kept param name for backwards compat
):
    """Render a McKinsey-style KPI card — white bg, left accent bar, serif value."""
    accent = _ACCENT_MAP.get(gradient, "accent-blue")

    change_html = ""
    if change:
        is_up = change.startswith("+") or change.startswith("↑")
        cls = "up" if is_up else "down"
        arrow = "&#9650;" if is_up else "&#9660;"
        change_html = f'<div class="kpi-change {cls}">{arrow} {change}</div>'

    st.markdown(
        f"""
        <div class="kpi-card {accent}">
            <div class="kpi-label">
                <i class="fas fa-{icon}" style="margin-right:.35rem;opacity:.5"></i>{title}
            </div>
            <div class="kpi-value">{value}</div>
            {change_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_row(cards: list[dict]):
    """Render a row of KPI cards using a CSS Grid layout for perfect responsiveness."""
    cards_html = f'<div style="display:grid;grid-template-columns:repeat({len(cards)},1fr);gap:1.5rem;margin-bottom:2rem">'
    
    for card in cards:
        title = card.get("title", "")
        value = card.get("value", "")
        change = card.get("change", "")
        icon = card.get("icon", "chart-line")
        accent = _ACCENT_MAP.get(card.get("gradient", "blue"), "accent-blue")
        
        change_html = ""
        if change:
            is_up = change.startswith("+") or change.startswith("↑")
            cls = "up" if is_up else "down"
            arrow = "&#9650;" if is_up else "&#9660;"
            change_html = f'<div class="kpi-change {cls}">{arrow} {change}</div>'
            
        cards_html += f"""
            <div class="kpi-card {accent}">
                <div class="kpi-label">
                    <i class="fas fa-{icon}" style="margin-right:.25rem;opacity:.5"></i>{title}
                </div>
                <div class="kpi-value">{value}</div>
                {change_html}
            </div>
        """
        
    cards_html += '</div>'
    
    if hasattr(st, "html"):
        st.html(cards_html)
    else:
        st.markdown(cards_html, unsafe_allow_html=True)


# ── Stat Card ────────────────────────────────────────────────────────────────
_STAT_COLORS = {
    "blue":   ("#EFF6FF", "#1D4ED8", "#DBEAFE"),
    "green":  ("#ECFDF5", "#047857", "#D1FAE5"),
    "red":    ("#FEF2F2", "#B91C1C", "#FECACA"),
    "purple": ("#FAF5FF", "#7E22CE", "#F3E8FF"),
    "amber":  ("#FFFBEB", "#92400E", "#FDE68A"),
    "gray":   ("#F9FAFB", "#374151", "#E5E7EB"),
}


def stat_card(label: str, value: str, description: str = "", color: str = "blue"):
    """Clean stat card with subtle background tint."""
    bg, val_color, brd = _STAT_COLORS.get(color, _STAT_COLORS["blue"])
    desc_html = (
        f'<div style="color:#6B7F95;font-size:.78rem;margin-top:.25rem">{description}</div>'
        if description else ""
    )
    st.markdown(
        f"""
        <div style="background:{bg};border:1px solid {brd};border-radius:.75rem;padding:1.15rem 1.25rem">
            <div style="font-size:.7rem;font-weight:600;letter-spacing:.05em;
                        text-transform:uppercase;color:#6B7F95;margin-bottom:.25rem">{label}</div>
            <div style="font-family:'Inter',sans-serif;font-size:1.35rem;font-weight:700;
                        color:{val_color};line-height:1.25">{value}</div>
            {desc_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Section Header ───────────────────────────────────────────────────────────
def section_header(title: str, subtitle: str = "", icon: str = ""):
    """McKinsey-style section divider — bold line, serif heading."""
    ico = (
        f'<i class="fas fa-{icon}" style="color:#2251FF;margin-right:.5rem;font-size:.85em"></i>'
        if icon else ""
    )
    sub = f'<p>{subtitle}</p>' if subtitle else ""
    st.markdown(
        f"""
        <div class="section-hdr">
            <h2>{ico}{title}</h2>
            {sub}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Info Banner ──────────────────────────────────────────────────────────────
_BANNER = {
    "info":    ("#EFF6FF", "#1E40AF", "#2251FF", "fa-info-circle"),
    "warning": ("#FFFBEB", "#92400E", "#F59E0B", "fa-exclamation-triangle"),
    "success": ("#ECFDF5", "#065F46", "#00B894", "fa-check-circle"),
    "error":   ("#FEF2F2", "#991B1B", "#D63031", "fa-times-circle"),
}


def info_banner(text: str, type: str = "info"):
    """Styled alert banner."""
    bg, txt, accent, fa = _BANNER.get(type, _BANNER["info"])
    st.markdown(
        f"""
        <div style="background:{bg};border-left:4px solid {accent};
                    border-radius:.5rem;padding:.85rem 1rem;
                    display:flex;align-items:flex-start;gap:.65rem;margin-bottom:1rem">
            <i class="fas {fa}" style="color:{accent};margin-top:.15rem"></i>
            <span style="color:{txt};font-size:.875rem;line-height:1.45">{text}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Metric Badge ─────────────────────────────────────────────────────────────
def metric_badge(label: str, value: str, color: str = "blue"):
    """Inline pill badge."""
    _map = {
        "blue":   ("bg-blue-100", "text-blue-800"),
        "green":  ("bg-emerald-100", "text-emerald-800"),
        "red":    ("bg-red-100", "text-red-800"),
        "purple": ("bg-purple-100", "text-purple-800"),
    }
    bg_cls, txt_cls = _map.get(color, _map["blue"])
    return (
        f'<span class="{bg_cls} {txt_cls}" '
        f'style="font-size:.75rem;font-weight:600;padding:.2rem .65rem;border-radius:9999px">'
        f'{label}: {value}</span>'
    )


# ── Empty State ──────────────────────────────────────────────────────────────
def empty_state(message: str, icon: str = "chart-bar"):
    """Placeholder for empty content areas."""
    st.markdown(
        f"""
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                    padding:4rem 1rem;color:#A3B1BF">
            <i class="fas fa-{icon}" style="font-size:2.5rem;margin-bottom:1rem;opacity:.4"></i>
            <p style="font-size:1rem;font-weight:500;margin:0">{message}</p>
            <p style="font-size:.8rem;margin-top:.35rem">Adjust filters or parameters to see results</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── LLM Explainer UI ──────────────────────────────────────────────────────────
from utils.llm import generate_insights

def llm_explainer_ui(page_name: str, context_dict: dict):
    """
    Renders an expandable LLM insight generator using the Gemini API.
    """
    st.markdown("<div class='h-4'></div>", unsafe_allow_html=True)
    with st.expander("✨ Generate Insights"):
        st.markdown(
            """<p style="font-size:0.85rem;color:#64748b;margin-bottom:1rem;">
            Click below to generate insights from the data on this page</p>""",
            unsafe_allow_html=True
        )
        if st.button("Generate Insights", key=f"btn_llm_{page_name.replace(' ', '_')}", type="primary"):
            with st.spinner("Analyzing data with Google Gemini..."):
                response = generate_insights(page_name, context_dict)
                st.info(response, icon="💡")
