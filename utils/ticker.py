"""
FI rate ticker — shared between the home page and the global navigation ribbon.

Extracted from `views/home.py` and `utils/navigation.py` in task 2.2 so the
ticker reads `load_data()` once per render cycle instead of twice (one cache
per call site). The two original implementations were near-identical; this
module is the single source of truth.

The ticker renders the population-weighted national FI rate per year as a
horizontal scrolling strip, surfacing a "Coverage gap: YYYY-YYYY" caveat
span when consecutive years are missing in the source data (e.g., the MMG
2011-2012 coverage gap).
"""
from __future__ import annotations

import streamlit as st


_FALLBACK_HTML = (
    '<div class="fi-ticker"><div class="fi-ticker-track">'
    '<span class="fi-ticker-item">FI rates unavailable</span>'
    '</div></div>'
)


@st.cache_data(show_spinner=False, ttl=3600)
def get_fi_ticker_html() -> str:
    """Render the FI rate ticker as a self-contained HTML string.

    Reads `load_data()` once, computes the population-weighted national rate
    per year via `weighted_rate_by_group`, and emits the marquee markup.
    Falls back to an "FI rates unavailable" placeholder on any exception so
    the ticker never crashes the page.
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
        items: list[str] = []
        prev_year = None
        for y, v in _fi_years.items():
            y = int(y)
            if prev_year is not None and y - prev_year > 1:
                lo, hi = prev_year + 1, y - 1
                label = f"{lo}" if lo == hi else f"{lo}-{hi}"
                items.append(
                    f'<span class="fi-ticker-item fi-ticker-gap">Coverage gap: {label}</span>'
                )
            items.append(f'<span class="fi-ticker-item">{y} FI Rate = {v:.1%}</span>')
            prev_year = y
        _ticker_items = "".join(items) or '<span class="fi-ticker-item">FI rates unavailable</span>'
        return (
            '<div class="fi-ticker"><div class="fi-ticker-track">'
            f'{_ticker_items * 3}'
            '</div></div>'
        )
    except Exception:
        return _FALLBACK_HTML
