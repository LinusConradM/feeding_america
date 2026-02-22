"""
Lightweight viewport detection for responsive Plotly rendering.

We avoid external dependencies by syncing the window width into Streamlit
query params via a tiny JS snippet. The page reruns once width is captured,
so downstream code can branch on `is_mobile` / `is_portrait`.
"""

from __future__ import annotations

import streamlit as st
from streamlit.components.v1 import html


def _sync_viewport_width():
    """Inject JS that stores `vw` in query params if it changed."""
    html(
        """
        <script>
        (function() {
            let resizeTimer;
            const sendWidth = () => {
                const vw = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);
                const params = Object.fromEntries(new URLSearchParams(window.location.search).entries());
                if (params.vw !== String(vw)) {
                    params.vw = String(vw);
                    window.parent.postMessage({type: "streamlit:setQueryParams", queryParams: params}, "*");
                }
            };
            sendWidth();
            window.addEventListener('resize', () => {
                clearTimeout(resizeTimer);
                resizeTimer = setTimeout(sendWidth, 250);
            });
        })();
        </script>
        """,
        height=0,
    )


def get_viewport_profile(breakpoint: int = 820) -> dict:
    """Return viewport metrics with mobile/portrait flags.

    breakpoint: px threshold for treating layout as mobile (default 820 to
    cover most phone landscape widths).
    """

    _sync_viewport_width()

    # st.query_params returns str values (Streamlit >=1.30) or list in older versions
    params = st.query_params if hasattr(st, "query_params") else st.experimental_get_query_params()
    raw = params.get("vw")

    width = None
    if isinstance(raw, list):
        raw = raw[0] if raw else None
    if isinstance(raw, str) and raw.isdigit():
        width = int(raw)

    is_mobile = bool(width and width < breakpoint)
    is_portrait_phone = bool(width and width < 600)

    return {
        "width": width,
        "is_mobile": is_mobile,
        "is_portrait": is_portrait_phone,
    }

