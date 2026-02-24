"""
Lightweight viewport detection for responsive Plotly rendering.

We avoid external dependencies by syncing the window width into Streamlit
query params via a tiny JS snippet. The page reruns once width is captured,
so downstream code can branch on `is_mobile` / `is_portrait`.
"""

from __future__ import annotations

from dataclasses import dataclass

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


def get_viewport_profile(breakpoint: int = 820) -> "ViewportProfile":
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

    return ViewportProfile(
        width=width,
        is_mobile=is_mobile,
        is_portrait=is_portrait_phone,
    )


@dataclass
class ViewportProfile:
    """Viewport profile with responsive layout properties."""
    
    width: int | None
    is_mobile: bool
    is_portrait: bool
    
    @property
    def breakpoint_name(self) -> str:
        """Return breakpoint name: 'mobile', 'tablet', or 'desktop'."""
        if self.is_mobile:
            return "mobile"
        elif self.width and self.width <= 1024:
            return "tablet"
        else:
            return "desktop"
    
    @property
    def chart_height(self) -> int:
        """Return appropriate chart height for viewport."""
        if self.is_portrait:
            return 240
        elif self.is_mobile:
            return 280
        elif self.breakpoint_name == "tablet":
            return 350
        else:
            return 450
    
    @property
    def kpi_columns(self) -> int:
        """Return number of KPI card columns for viewport."""
        if self.is_mobile:
            return 1
        elif self.breakpoint_name == "tablet":
            return 2
        else:
            return 4

@dataclass
class ChartConfig:
    """Chart configuration with viewport-specific sizing and styling."""

    height: int
    margin: dict[str, int]
    font_size: int
    marker_size: int
    line_width: int
    show_legend: bool
    data_point_reduction: float  # 0.0-1.0, percentage to keep

    @classmethod
    def for_viewport(cls, viewport: ViewportProfile) -> "ChartConfig":
        """Generate chart config for viewport.

        Args:
            viewport: ViewportProfile instance with viewport metrics

        Returns:
            ChartConfig instance with viewport-specific settings
        """
        if viewport.is_mobile:
            return cls(
                height=240 if viewport.is_portrait else 280,
                margin={"l": 40, "r": 12, "t": 32, "b": 40},
                font_size=11,
                marker_size=5,
                line_width=2,
                show_legend=False,
                data_point_reduction=0.7  # Keep 70% of points
            )
        elif viewport.breakpoint_name == "tablet":
            return cls(
                height=350,
                margin={"l": 48, "r": 16, "t": 40, "b": 44},
                font_size=12,
                marker_size=6,
                line_width=2.5,
                show_legend=True,
                data_point_reduction=1.0
            )
        else:  # desktop
            return cls(
                height=450,
                margin={"l": 56, "r": 24, "t": 64, "b": 48},
                font_size=13,
                marker_size=8,
                line_width=3,
                show_legend=True,
                data_point_reduction=1.0
            )


@dataclass
class StateSummary:
    """State-level food insecurity summary data."""
    
    state_code: str
    state_name: str
    fi_rate: float
    rank: int  # 1-51 ranking
    total_states: int  # Always 51 (50 states + DC)
    food_insecure_persons: int
    cost_per_meal: float
    poverty_rate: float
    
    def to_display_dict(self) -> dict:
        """Convert to display-ready dictionary."""
        return {
            "State": self.state_name,
            "FI Rate": f"{self.fi_rate:.1%}",
            "Rank": f"{self.rank} of {self.total_states}",
            "Food Insecure": f"{self.food_insecure_persons:,}",
            "Cost/Meal": f"${self.cost_per_meal:.2f}",
            "Poverty": f"{self.poverty_rate:.1%}"
        }
