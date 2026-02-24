"""
Property-based tests for map pinch-zoom functionality.

Tests validate Property 34 from the executive-overview-redesign spec:
- Property 34: Map Pinch-Zoom Support

Uses Hypothesis for property-based testing with 20 iterations per test.
"""

import pytest
from hypothesis import given, strategies as st, settings
from utils.responsive import ViewportProfile
from utils.components import geographic_section
from unittest.mock import MagicMock, patch, call
import pandas as pd
import numpy as np
import streamlit


# Strategy for generating sample year data
@st.composite
def year_data_strategy(draw):
    """Generate valid year data with geographic information."""
    num_states = draw(st.integers(min_value=5, max_value=51))
    
    # Generate state codes
    all_states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL",
                  "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME",
                  "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH",
                  "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI",
                  "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
    
    states = draw(st.lists(
        st.sampled_from(all_states),
        min_size=num_states,
        max_size=num_states,
        unique=True
    ))
    
    # Generate data
    data = {
        "state": states,
        "overall_food_insecurity_rate": draw(st.lists(
            st.floats(min_value=0.05, max_value=0.25, allow_nan=False, allow_infinity=False),
            min_size=num_states,
            max_size=num_states
        )),
        "census_region": draw(st.lists(
            st.sampled_from(["Northeast", "South", "Midwest", "West"]),
            min_size=num_states,
            max_size=num_states
        )),
        "urban_rural": draw(st.lists(
            st.sampled_from(["Urban", "Rural", "Mixed"]),
            min_size=num_states,
            max_size=num_states
        ))
    }
    
    return pd.DataFrame(data)


class TestMapPinchZoomProperties:
    """Property-based tests for map pinch-zoom functionality."""
    
    @given(
        year_data=year_data_strategy(),
        selected_year=st.integers(min_value=2009, max_value=2023),
        viewport_width=st.integers(min_value=320, max_value=767)
    )
    @settings(max_examples=20, deadline=None)
    def test_property_34_map_pinch_zoom_enabled_on_mobile(
        self, year_data, selected_year, viewport_width
    ):
        """
        **Validates: Requirements 10.4**
        
        Property 34: Map Pinch-Zoom Support
        
        For any map visualization on viewport width < 768px, pinch-to-zoom 
        gestures SHALL be enabled.
        
        This test verifies that:
        1. Mobile viewports (<768px) have scrollZoom: true in Plotly config
        2. Mobile viewports have dragmode: 'zoom' in layout
        3. Desktop viewports have standard behavior (scrollZoom: false)
        """
        # Create mobile viewport profile
        profile = ViewportProfile(
            width=viewport_width,
            is_mobile=True,
            is_portrait=True
        )
        
        # Verify it's mobile
        assert profile.breakpoint_name == "mobile", \
            f"Width {viewport_width}px should be mobile breakpoint"
        
        # Track plotly_chart calls to inspect config
        plotly_calls = []
        
        def mock_plotly_chart(fig, use_container_width=False, config=None):
            plotly_calls.append({
                'fig': fig,
                'use_container_width': use_container_width,
                'config': config
            })
        
        # Mock Streamlit components
        with patch.object(streamlit, 'plotly_chart', side_effect=mock_plotly_chart):
            with patch.object(streamlit, 'markdown'):
                with patch.object(streamlit, 'columns', return_value=[MagicMock(), MagicMock()]):
                    # Render the component
                    geographic_section(year_data, selected_year, profile)
        
        # Verify at least one chart was rendered (the map)
        assert len(plotly_calls) >= 1, \
            "Geographic section should render at least the map"
        
        # Check the first chart (map) for pinch-zoom configuration
        map_call = plotly_calls[0]
        config = map_call.get('config')
        
        # Verify config is provided
        assert config is not None, \
            "Map should have Plotly config on mobile viewports"
        
        # Verify scrollZoom is enabled for mobile
        assert 'scrollZoom' in config, \
            "Map config should include scrollZoom setting"
        assert config['scrollZoom'] is True, \
            f"Map scrollZoom should be True on mobile (width={viewport_width}px), got {config['scrollZoom']}"
        
        # Verify displayModeBar is set appropriately for mobile
        assert 'displayModeBar' in config, \
            "Map config should include displayModeBar setting"
        assert config['displayModeBar'] is True, \
            f"Map displayModeBar should be True on mobile, got {config['displayModeBar']}"
        
        # Check the figure layout for dragmode
        fig = map_call['fig']
        if hasattr(fig, 'layout') and hasattr(fig.layout, 'dragmode'):
            assert fig.layout.dragmode == 'zoom', \
                f"Map dragmode should be 'zoom' on mobile, got {fig.layout.dragmode}"
    
    @given(
        year_data=year_data_strategy(),
        selected_year=st.integers(min_value=2009, max_value=2023),
        viewport_width=st.integers(min_value=1025, max_value=2560)
    )
    @settings(max_examples=20, deadline=None)
    def test_property_34_map_standard_behavior_on_desktop(
        self, year_data, selected_year, viewport_width
    ):
        """
        **Validates: Requirements 10.4**
        
        Property 34: Map Pinch-Zoom Support (Desktop Behavior)
        
        For any map visualization on viewport width >= 1025px (desktop), 
        standard behavior SHALL be maintained (scrollZoom: false).
        
        This ensures pinch-zoom is only enabled on mobile devices where it's needed.
        """
        # Create desktop viewport profile
        profile = ViewportProfile(
            width=viewport_width,
            is_mobile=False,
            is_portrait=False
        )
        
        # Verify it's desktop
        assert profile.breakpoint_name == "desktop", \
            f"Width {viewport_width}px should be desktop breakpoint"
        
        # Track plotly_chart calls to inspect config
        plotly_calls = []
        
        def mock_plotly_chart(fig, use_container_width=False, config=None):
            plotly_calls.append({
                'fig': fig,
                'use_container_width': use_container_width,
                'config': config
            })
        
        # Mock Streamlit components
        with patch.object(streamlit, 'plotly_chart', side_effect=mock_plotly_chart):
            with patch.object(streamlit, 'markdown'):
                with patch.object(streamlit, 'columns', return_value=[MagicMock(), MagicMock()]):
                    # Render the component
                    geographic_section(year_data, selected_year, profile)
        
        # Verify at least one chart was rendered (the map)
        assert len(plotly_calls) >= 1, \
            "Geographic section should render at least the map"
        
        # Check the first chart (map) for standard configuration
        map_call = plotly_calls[0]
        config = map_call.get('config')
        
        # Verify config is provided
        assert config is not None, \
            "Map should have Plotly config on desktop viewports"
        
        # Verify scrollZoom is disabled for desktop
        assert 'scrollZoom' in config, \
            "Map config should include scrollZoom setting"
        assert config['scrollZoom'] is False, \
            f"Map scrollZoom should be False on desktop (width={viewport_width}px), got {config['scrollZoom']}"
        
        # Verify displayModeBar is set to 'hover' for desktop
        assert 'displayModeBar' in config, \
            "Map config should include displayModeBar setting"
        assert config['displayModeBar'] == 'hover', \
            f"Map displayModeBar should be 'hover' on desktop, got {config['displayModeBar']}"
        
        # Check the figure layout - dragmode should NOT be 'zoom' on desktop
        fig = map_call['fig']
        if hasattr(fig, 'layout') and hasattr(fig.layout, 'dragmode'):
            # On desktop, dragmode should not be explicitly set to 'zoom'
            # It may be None or a different value
            assert fig.layout.dragmode != 'zoom' or fig.layout.dragmode is None, \
                f"Map dragmode should not be 'zoom' on desktop, got {fig.layout.dragmode}"
    
    @given(
        year_data=year_data_strategy(),
        selected_year=st.integers(min_value=2009, max_value=2023),
        viewport_width=st.integers(min_value=768, max_value=1024)
    )
    @settings(max_examples=20, deadline=None)
    def test_property_34_map_behavior_on_tablet(
        self, year_data, selected_year, viewport_width
    ):
        """
        **Validates: Requirements 10.4**
        
        Property 34: Map Pinch-Zoom Support (Tablet Behavior)
        
        For any map visualization on viewport width 768-1024px (tablet), 
        behavior should follow desktop pattern (scrollZoom: false).
        
        Tablets are treated as desktop for pinch-zoom purposes.
        """
        # Create tablet viewport profile
        profile = ViewportProfile(
            width=viewport_width,
            is_mobile=False,
            is_portrait=False
        )
        
        # Verify it's tablet
        assert profile.breakpoint_name == "tablet", \
            f"Width {viewport_width}px should be tablet breakpoint"
        
        # Track plotly_chart calls to inspect config
        plotly_calls = []
        
        def mock_plotly_chart(fig, use_container_width=False, config=None):
            plotly_calls.append({
                'fig': fig,
                'use_container_width': use_container_width,
                'config': config
            })
        
        # Mock Streamlit components
        with patch.object(streamlit, 'plotly_chart', side_effect=mock_plotly_chart):
            with patch.object(streamlit, 'markdown'):
                with patch.object(streamlit, 'columns', return_value=[MagicMock(), MagicMock()]):
                    # Render the component
                    geographic_section(year_data, selected_year, profile)
        
        # Verify at least one chart was rendered (the map)
        assert len(plotly_calls) >= 1, \
            "Geographic section should render at least the map"
        
        # Check the first chart (map) for configuration
        map_call = plotly_calls[0]
        config = map_call.get('config')
        
        # Verify config is provided
        assert config is not None, \
            "Map should have Plotly config on tablet viewports"
        
        # Verify scrollZoom is disabled for tablet (follows desktop behavior)
        assert 'scrollZoom' in config, \
            "Map config should include scrollZoom setting"
        assert config['scrollZoom'] is False, \
            f"Map scrollZoom should be False on tablet (width={viewport_width}px), got {config['scrollZoom']}"


class TestMapPinchZoomBoundaryConditions:
    """Test boundary conditions for map pinch-zoom configuration."""
    
    def test_mobile_upper_boundary_767px_enables_pinch_zoom(self):
        """Test that 767px (mobile upper boundary) enables pinch-zoom."""
        profile = ViewportProfile(width=767, is_mobile=True, is_portrait=False)
        assert profile.breakpoint_name == "mobile"
        
        # Create sample data
        data = pd.DataFrame({
            "state": ["CA", "TX", "NY"],
            "overall_food_insecurity_rate": [0.12, 0.15, 0.10],
            "census_region": ["West", "South", "Northeast"],
            "urban_rural": ["Urban", "Mixed", "Urban"]
        })
        
        plotly_calls = []
        
        def mock_plotly_chart(fig, use_container_width=False, config=None):
            plotly_calls.append({'fig': fig, 'config': config})
        
        with patch.object(streamlit, 'plotly_chart', side_effect=mock_plotly_chart):
            with patch.object(streamlit, 'markdown'):
                with patch.object(streamlit, 'columns', return_value=[MagicMock(), MagicMock()]):
                    geographic_section(data, 2023, profile)
        
        # Verify pinch-zoom is enabled
        map_config = plotly_calls[0]['config']
        assert map_config['scrollZoom'] is True, \
            "767px should enable pinch-zoom (mobile boundary)"
    
    def test_tablet_lower_boundary_768px_disables_pinch_zoom(self):
        """Test that 768px (tablet lower boundary) disables pinch-zoom."""
        profile = ViewportProfile(width=768, is_mobile=False, is_portrait=False)
        assert profile.breakpoint_name == "tablet"
        
        # Create sample data
        data = pd.DataFrame({
            "state": ["CA", "TX", "NY"],
            "overall_food_insecurity_rate": [0.12, 0.15, 0.10],
            "census_region": ["West", "South", "Northeast"],
            "urban_rural": ["Urban", "Mixed", "Urban"]
        })
        
        plotly_calls = []
        
        def mock_plotly_chart(fig, use_container_width=False, config=None):
            plotly_calls.append({'fig': fig, 'config': config})
        
        with patch.object(streamlit, 'plotly_chart', side_effect=mock_plotly_chart):
            with patch.object(streamlit, 'markdown'):
                with patch.object(streamlit, 'columns', return_value=[MagicMock(), MagicMock()]):
                    geographic_section(data, 2023, profile)
        
        # Verify pinch-zoom is disabled
        map_config = plotly_calls[0]['config']
        assert map_config['scrollZoom'] is False, \
            "768px should disable pinch-zoom (tablet boundary)"
    
    def test_desktop_lower_boundary_1025px_disables_pinch_zoom(self):
        """Test that 1025px (desktop lower boundary) disables pinch-zoom."""
        profile = ViewportProfile(width=1025, is_mobile=False, is_portrait=False)
        assert profile.breakpoint_name == "desktop"
        
        # Create sample data
        data = pd.DataFrame({
            "state": ["CA", "TX", "NY"],
            "overall_food_insecurity_rate": [0.12, 0.15, 0.10],
            "census_region": ["West", "South", "Northeast"],
            "urban_rural": ["Urban", "Mixed", "Urban"]
        })
        
        plotly_calls = []
        
        def mock_plotly_chart(fig, use_container_width=False, config=None):
            plotly_calls.append({'fig': fig, 'config': config})
        
        with patch.object(streamlit, 'plotly_chart', side_effect=mock_plotly_chart):
            with patch.object(streamlit, 'markdown'):
                with patch.object(streamlit, 'columns', return_value=[MagicMock(), MagicMock()]):
                    geographic_section(data, 2023, profile)
        
        # Verify pinch-zoom is disabled
        map_config = plotly_calls[0]['config']
        assert map_config['scrollZoom'] is False, \
            "1025px should disable pinch-zoom (desktop boundary)"
    
    def test_minimum_mobile_width_320px_enables_pinch_zoom(self):
        """Test that 320px (minimum mobile width) enables pinch-zoom."""
        profile = ViewportProfile(width=320, is_mobile=True, is_portrait=True)
        assert profile.breakpoint_name == "mobile"
        
        # Create sample data
        data = pd.DataFrame({
            "state": ["CA", "TX", "NY"],
            "overall_food_insecurity_rate": [0.12, 0.15, 0.10],
            "census_region": ["West", "South", "Northeast"],
            "urban_rural": ["Urban", "Mixed", "Urban"]
        })
        
        plotly_calls = []
        
        def mock_plotly_chart(fig, use_container_width=False, config=None):
            plotly_calls.append({'fig': fig, 'config': config})
        
        with patch.object(streamlit, 'plotly_chart', side_effect=mock_plotly_chart):
            with patch.object(streamlit, 'markdown'):
                with patch.object(streamlit, 'columns', return_value=[MagicMock(), MagicMock()]):
                    geographic_section(data, 2023, profile)
        
        # Verify pinch-zoom is enabled
        map_config = plotly_calls[0]['config']
        assert map_config['scrollZoom'] is True, \
            "320px should enable pinch-zoom (minimum mobile width)"


class TestMapPinchZoomConfiguration:
    """Test specific configuration details for map pinch-zoom."""
    
    def test_mobile_config_includes_double_click_reset(self):
        """Test that mobile config includes doubleClick: 'reset' for user convenience."""
        profile = ViewportProfile(width=375, is_mobile=True, is_portrait=True)
        
        # Create sample data
        data = pd.DataFrame({
            "state": ["CA", "TX", "NY"],
            "overall_food_insecurity_rate": [0.12, 0.15, 0.10],
            "census_region": ["West", "South", "Northeast"],
            "urban_rural": ["Urban", "Mixed", "Urban"]
        })
        
        plotly_calls = []
        
        def mock_plotly_chart(fig, use_container_width=False, config=None):
            plotly_calls.append({'fig': fig, 'config': config})
        
        with patch.object(streamlit, 'plotly_chart', side_effect=mock_plotly_chart):
            with patch.object(streamlit, 'markdown'):
                with patch.object(streamlit, 'columns', return_value=[MagicMock(), MagicMock()]):
                    geographic_section(data, 2023, profile)
        
        # Verify doubleClick is configured
        map_config = plotly_calls[0]['config']
        assert 'doubleClick' in map_config, \
            "Map config should include doubleClick setting"
        assert map_config['doubleClick'] == 'reset', \
            "Map doubleClick should be 'reset' for easy zoom reset"
    
    def test_mobile_layout_includes_dragmode_zoom(self):
        """Test that mobile layout includes dragmode: 'zoom' for pinch-zoom support."""
        profile = ViewportProfile(width=375, is_mobile=True, is_portrait=True)
        
        # Create sample data
        data = pd.DataFrame({
            "state": ["CA", "TX", "NY"],
            "overall_food_insecurity_rate": [0.12, 0.15, 0.10],
            "census_region": ["West", "South", "Northeast"],
            "urban_rural": ["Urban", "Mixed", "Urban"]
        })
        
        plotly_calls = []
        
        def mock_plotly_chart(fig, use_container_width=False, config=None):
            plotly_calls.append({'fig': fig, 'config': config})
        
        with patch.object(streamlit, 'plotly_chart', side_effect=mock_plotly_chart):
            with patch.object(streamlit, 'markdown'):
                with patch.object(streamlit, 'columns', return_value=[MagicMock(), MagicMock()]):
                    geographic_section(data, 2023, profile)
        
        # Verify dragmode in layout
        map_fig = plotly_calls[0]['fig']
        if hasattr(map_fig, 'layout') and hasattr(map_fig.layout, 'dragmode'):
            assert map_fig.layout.dragmode == 'zoom', \
                "Map layout dragmode should be 'zoom' on mobile"
    
    def test_desktop_config_display_mode_bar_hover(self):
        """Test that desktop config uses displayModeBar: 'hover' for cleaner UI."""
        profile = ViewportProfile(width=1920, is_mobile=False, is_portrait=False)
        
        # Create sample data
        data = pd.DataFrame({
            "state": ["CA", "TX", "NY"],
            "overall_food_insecurity_rate": [0.12, 0.15, 0.10],
            "census_region": ["West", "South", "Northeast"],
            "urban_rural": ["Urban", "Mixed", "Urban"]
        })
        
        plotly_calls = []
        
        def mock_plotly_chart(fig, use_container_width=False, config=None):
            plotly_calls.append({'fig': fig, 'config': config})
        
        with patch.object(streamlit, 'plotly_chart', side_effect=mock_plotly_chart):
            with patch.object(streamlit, 'markdown'):
                with patch.object(streamlit, 'columns', return_value=[MagicMock(), MagicMock()]):
                    geographic_section(data, 2023, profile)
        
        # Verify displayModeBar is 'hover' on desktop
        map_config = plotly_calls[0]['config']
        assert map_config['displayModeBar'] == 'hover', \
            "Desktop should use displayModeBar: 'hover' for cleaner UI"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
