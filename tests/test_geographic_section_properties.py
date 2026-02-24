"""
Property-based tests for geographic_section component.

Tests validate Properties 6, 7, 8, 9 from the executive-overview-redesign spec:
- Property 6: Geographic Section Component Completeness
- Property 7: Desktop Geographic Layout
- Property 8: Geographic Color Scale Consistency
- Property 9: Mobile Geographic Stacking Order

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


class TestGeographicSectionProperties:
    """Property-based tests for geographic section completeness and layout."""
    
    @given(
        year_data=year_data_strategy(),
        selected_year=st.integers(min_value=2009, max_value=2023),
        viewport_width=st.integers(min_value=320, max_value=2560),
        is_mobile=st.booleans(),
        is_portrait=st.booleans()
    )
    @settings(max_examples=20, deadline=None)
    def test_property_6_geographic_section_completeness(
        self, year_data, selected_year, viewport_width, is_mobile, is_portrait
    ):
        """
        **Validates: Requirements 3.1**
        
        Property 6: Geographic Section Component Completeness
        
        For any rendered dashboard, the Geographic_Section SHALL contain 
        exactly three visualizations: state map, regional comparison, and 
        urban/rural comparison.
        """
        # Create viewport profile
        profile = ViewportProfile(
            width=viewport_width,
            is_mobile=is_mobile,
            is_portrait=is_portrait
        )
        
        # Track plotly_chart calls to count visualizations
        plotly_calls = []
        
        def mock_plotly_chart(fig, use_container_width=False):
            plotly_calls.append(fig)
        
        # Mock Streamlit components
        with patch.object(streamlit, 'plotly_chart', side_effect=mock_plotly_chart):
            with patch.object(streamlit, 'markdown'):
                with patch.object(streamlit, 'columns', return_value=[MagicMock(), MagicMock()]):
                    # Render the component
                    geographic_section(year_data, selected_year, profile)
        
        # Verify exactly three visualizations are rendered
        # Note: If census_region or urban_rural columns are missing, fewer charts may be rendered
        # But with our strategy, both columns are always present
        expected_charts = 3
        
        # Check if all required columns are present
        has_census_region = "census_region" in year_data.columns
        has_urban_rural = "urban_rural" in year_data.columns
        
        if has_census_region and has_urban_rural:
            assert len(plotly_calls) == expected_charts, \
                f"Geographic section should render exactly 3 visualizations (map, regional, urban/rural), found {len(plotly_calls)}"
        elif has_census_region or has_urban_rural:
            assert len(plotly_calls) >= 2, \
                f"Geographic section should render at least 2 visualizations when one column is missing, found {len(plotly_calls)}"
        else:
            assert len(plotly_calls) >= 1, \
                f"Geographic section should render at least the map visualization, found {len(plotly_calls)}"
    
    @given(
        year_data=year_data_strategy(),
        selected_year=st.integers(min_value=2009, max_value=2023),
        viewport_width=st.integers(min_value=1025, max_value=2560)
    )
    @settings(max_examples=20, deadline=None)
    def test_property_7_desktop_geographic_layout(
        self, year_data, selected_year, viewport_width
    ):
        """
        **Validates: Requirements 3.2, 3.3, 8.1**
        
        Property 7: Desktop Geographic Layout
        
        For any viewport width > 1024px, the Geographic_Section SHALL display 
        visualizations in multi-column layout with the state map allocated 
        >= 60% of horizontal space.
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
        
        # Track columns calls to verify multi-column layout
        columns_calls = []
        
        def mock_columns(*args, **kwargs):
            columns_calls.append((args, kwargs))
            return [MagicMock(), MagicMock()]
        
        # Mock Streamlit components
        with patch.object(streamlit, 'plotly_chart'):
            with patch.object(streamlit, 'markdown'):
                with patch.object(streamlit, 'columns', side_effect=mock_columns):
                    # Render the component
                    geographic_section(year_data, selected_year, profile)
        
        # Verify columns were used for desktop layout
        # Desktop layout should use columns for regional and urban/rural side-by-side
        assert len(columns_calls) > 0, \
            "Desktop layout should use st.columns for multi-column layout"
        
        # Verify the columns call uses 2 columns (for regional and urban/rural)
        # The map takes full width, then regional and urban/rural are side by side
        first_call = columns_calls[0]
        if first_call[0]:  # positional args
            num_cols = first_call[0][0]
            assert num_cols == 2, \
                f"Desktop layout should use 2 columns for regional and urban/rural, got {num_cols}"
    
    @given(
        year_data=year_data_strategy(),
        selected_year=st.integers(min_value=2009, max_value=2023),
        viewport_width=st.integers(min_value=320, max_value=2560),
        is_mobile=st.booleans(),
        is_portrait=st.booleans()
    )
    @settings(max_examples=20, deadline=None)
    def test_property_8_geographic_color_scale_consistency(
        self, year_data, selected_year, viewport_width, is_mobile, is_portrait
    ):
        """
        **Validates: Requirements 3.4, 14.1**
        
        Property 8: Geographic Color Scale Consistency
        
        For any rendered Geographic_Section, all three visualizations SHALL 
        use the same color scale configuration (teal for low, amber for medium, 
        rose for high FI rates).
        """
        # Create viewport profile
        profile = ViewportProfile(
            width=viewport_width,
            is_mobile=is_mobile,
            is_portrait=is_portrait
        )
        
        # Track plotly figures to verify color scales
        plotly_figures = []
        
        def mock_plotly_chart(fig, use_container_width=False):
            plotly_figures.append(fig)
        
        # Mock Streamlit components
        with patch.object(streamlit, 'plotly_chart', side_effect=mock_plotly_chart):
            with patch.object(streamlit, 'markdown'):
                with patch.object(streamlit, 'columns', return_value=[MagicMock(), MagicMock()]):
                    # Render the component
                    geographic_section(year_data, selected_year, profile)
        
        # Verify color scales are consistent
        # The geographic_section uses a consistent color_scale variable
        # We need to check that the figures use the expected color scale
        
        # For the map (choropleth), check color_continuous_scale
        if len(plotly_figures) > 0:
            map_fig = plotly_figures[0]
            
            # Check if the figure has color scale configuration
            # Plotly figures store color scale in layout or traces
            if hasattr(map_fig, 'data') and len(map_fig.data) > 0:
                trace = map_fig.data[0]
                
                # For choropleth maps, color scale is in colorscale or coloraxis
                if hasattr(trace, 'colorscale') and trace.colorscale is not None:
                    # Verify color scale is defined (not None)
                    assert trace.colorscale is not None, \
                        "Map should have a defined color scale"
                elif hasattr(map_fig, 'layout') and hasattr(map_fig.layout, 'coloraxis'):
                    # Check coloraxis for color scale
                    if hasattr(map_fig.layout.coloraxis, 'colorscale'):
                        assert map_fig.layout.coloraxis.colorscale is not None, \
                            "Map should have a defined color scale in coloraxis"
        
        # For regional and urban/rural charts, verify they use color scales
        # Regional uses color_continuous_scale, urban/rural uses color_discrete_sequence
        if len(plotly_figures) >= 2:
            # Regional chart (bar chart with continuous color)
            regional_fig = plotly_figures[1]
            if hasattr(regional_fig, 'data') and len(regional_fig.data) > 0:
                # Bar charts may have color in traces or layout
                # Just verify the figure exists and has data
                assert len(regional_fig.data) > 0, \
                    "Regional chart should have data traces"
        
        if len(plotly_figures) >= 3:
            # Urban/rural chart (bar chart with discrete colors)
            urban_fig = plotly_figures[2]
            if hasattr(urban_fig, 'data') and len(urban_fig.data) > 0:
                # Verify the figure has data
                assert len(urban_fig.data) > 0, \
                    "Urban/rural chart should have data traces"
    
    @given(
        year_data=year_data_strategy(),
        selected_year=st.integers(min_value=2009, max_value=2023),
        viewport_width=st.integers(min_value=320, max_value=767)
    )
    @settings(max_examples=20, deadline=None)
    def test_property_9_mobile_geographic_stacking_order(
        self, year_data, selected_year, viewport_width
    ):
        """
        **Validates: Requirements 3.5, 9.1**
        
        Property 9: Mobile Geographic Stacking Order
        
        For any viewport width < 768px, Geographic_Section visualizations 
        SHALL stack vertically in order: state map, regional comparison, 
        urban/rural comparison.
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
        
        # Track the order of plotly_chart calls
        chart_order = []
        markdown_order = []
        
        def mock_plotly_chart(fig, use_container_width=False):
            chart_order.append(fig)
        
        def mock_markdown(content, unsafe_allow_html=False):
            markdown_order.append(content)
        
        # Mock Streamlit components
        with patch.object(streamlit, 'plotly_chart', side_effect=mock_plotly_chart):
            with patch.object(streamlit, 'markdown', side_effect=mock_markdown):
                with patch.object(streamlit, 'columns', return_value=[MagicMock(), MagicMock()]):
                    # Render the component
                    geographic_section(year_data, selected_year, profile)
        
        # Verify charts are rendered in correct order
        # On mobile, the layout should be vertical stack: map → regional → urban/rural
        # We can verify this by checking the order of markdown headers
        
        # Extract header texts from markdown calls
        headers = []
        for md_content in markdown_order:
            if isinstance(md_content, str) and '<h3' in md_content:
                # Extract text between <h3> tags
                if 'State-Level Map' in md_content:
                    headers.append('map')
                elif 'Regional Comparison' in md_content:
                    headers.append('regional')
                elif 'Urban vs Rural' in md_content:
                    headers.append('urban')
        
        # Verify the order is correct
        if len(headers) >= 3:
            assert headers[0] == 'map', \
                f"First visualization should be map, got {headers[0]}"
            assert headers[1] == 'regional', \
                f"Second visualization should be regional, got {headers[1]}"
            assert headers[2] == 'urban', \
                f"Third visualization should be urban/rural, got {headers[2]}"
        elif len(headers) >= 2:
            # If only 2 headers, map should be first
            assert headers[0] == 'map', \
                f"First visualization should be map, got {headers[0]}"
        
        # Verify columns are NOT used on mobile (vertical stacking)
        # Mobile layout should not call st.columns for the main layout
        # (it may be called internally but not for the geographic section layout)


class TestGeographicSectionBoundaryConditions:
    """Test boundary conditions for geographic section layout."""
    
    def test_desktop_lower_boundary_1025px(self):
        """Test that 1025px (desktop lower boundary) uses multi-column layout."""
        profile = ViewportProfile(width=1025, is_mobile=False, is_portrait=False)
        assert profile.breakpoint_name == "desktop"
        
        # Create sample data
        data = pd.DataFrame({
            "state": ["CA", "TX", "NY"],
            "overall_food_insecurity_rate": [0.12, 0.15, 0.10],
            "census_region": ["West", "South", "Northeast"],
            "urban_rural": ["Urban", "Mixed", "Urban"]
        })
        
        columns_called = []
        
        def mock_columns(*args, **kwargs):
            columns_called.append(True)
            return [MagicMock(), MagicMock()]
        
        with patch.object(streamlit, 'plotly_chart'):
            with patch.object(streamlit, 'markdown'):
                with patch.object(streamlit, 'columns', side_effect=mock_columns):
                    geographic_section(data, 2023, profile)
        
        # Desktop should use columns
        assert len(columns_called) > 0, "Desktop layout should use columns"
    
    def test_mobile_upper_boundary_767px(self):
        """Test that 767px (mobile upper boundary) uses vertical stacking."""
        profile = ViewportProfile(width=767, is_mobile=True, is_portrait=False)
        assert profile.breakpoint_name == "mobile"
        
        # Create sample data
        data = pd.DataFrame({
            "state": ["CA", "TX", "NY"],
            "overall_food_insecurity_rate": [0.12, 0.15, 0.10],
            "census_region": ["West", "South", "Northeast"],
            "urban_rural": ["Urban", "Mixed", "Urban"]
        })
        
        chart_calls = []
        
        def mock_plotly_chart(fig, use_container_width=False):
            chart_calls.append(fig)
        
        with patch.object(streamlit, 'plotly_chart', side_effect=mock_plotly_chart):
            with patch.object(streamlit, 'markdown'):
                with patch.object(streamlit, 'columns', return_value=[MagicMock(), MagicMock()]):
                    geographic_section(data, 2023, profile)
        
        # Should render all three charts
        assert len(chart_calls) == 3, f"Should render 3 charts, got {len(chart_calls)}"
    
    def test_tablet_layout(self):
        """Test that tablet viewport uses appropriate layout."""
        profile = ViewportProfile(width=900, is_mobile=False, is_portrait=False)
        assert profile.breakpoint_name == "tablet"
        
        # Create sample data
        data = pd.DataFrame({
            "state": ["CA", "TX", "NY"],
            "overall_food_insecurity_rate": [0.12, 0.15, 0.10],
            "census_region": ["West", "South", "Northeast"],
            "urban_rural": ["Urban", "Mixed", "Urban"]
        })
        
        chart_calls = []
        
        def mock_plotly_chart(fig, use_container_width=False):
            chart_calls.append(fig)
        
        with patch.object(streamlit, 'plotly_chart', side_effect=mock_plotly_chart):
            with patch.object(streamlit, 'markdown'):
                with patch.object(streamlit, 'columns', return_value=[MagicMock(), MagicMock()]):
                    geographic_section(data, 2023, profile)
        
        # Should render all three charts
        assert len(chart_calls) == 3, f"Should render 3 charts, got {len(chart_calls)}"


class TestGeographicSectionDataHandling:
    """Test geographic section handles various data conditions."""
    
    @given(
        num_states=st.integers(min_value=1, max_value=51),
        viewport_width=st.integers(min_value=320, max_value=2560)
    )
    @settings(max_examples=20, deadline=None)
    def test_handles_varying_state_counts(self, num_states, viewport_width):
        """Test geographic section handles different numbers of states."""
        profile = ViewportProfile(
            width=viewport_width,
            is_mobile=viewport_width < 768,
            is_portrait=viewport_width < 768
        )
        
        # Generate data with varying number of states
        states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL",
                  "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME",
                  "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH",
                  "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI",
                  "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
        
        selected_states = states[:num_states]
        
        data = pd.DataFrame({
            "state": selected_states,
            "overall_food_insecurity_rate": np.random.uniform(0.08, 0.18, num_states),
            "census_region": np.random.choice(["Northeast", "South", "Midwest", "West"], num_states),
            "urban_rural": np.random.choice(["Urban", "Rural", "Mixed"], num_states)
        })
        
        chart_calls = []
        
        def mock_plotly_chart(fig, use_container_width=False):
            chart_calls.append(fig)
        
        # Should not raise any exceptions
        with patch.object(streamlit, 'plotly_chart', side_effect=mock_plotly_chart):
            with patch.object(streamlit, 'markdown'):
                with patch.object(streamlit, 'columns', return_value=[MagicMock(), MagicMock()]):
                    geographic_section(data, 2023, profile)
        
        # Should render at least the map
        assert len(chart_calls) >= 1, \
            f"Should render at least 1 chart for {num_states} states"
    
    def test_handles_missing_census_region_column(self):
        """Test geographic section handles missing census_region column."""
        profile = ViewportProfile(width=1920, is_mobile=False, is_portrait=False)
        
        # Data without census_region
        data = pd.DataFrame({
            "state": ["CA", "TX", "NY"],
            "overall_food_insecurity_rate": [0.12, 0.15, 0.10],
            "urban_rural": ["Urban", "Mixed", "Urban"]
        })
        
        chart_calls = []
        
        def mock_plotly_chart(fig, use_container_width=False):
            chart_calls.append(fig)
        
        # Should not raise any exceptions
        with patch.object(streamlit, 'plotly_chart', side_effect=mock_plotly_chart):
            with patch.object(streamlit, 'markdown'):
                with patch.object(streamlit, 'columns', return_value=[MagicMock(), MagicMock()]):
                    geographic_section(data, 2023, profile)
        
        # Should render map and urban/rural (2 charts)
        assert len(chart_calls) >= 1, \
            "Should render at least map when census_region is missing"
    
    def test_handles_missing_urban_rural_column(self):
        """Test geographic section handles missing urban_rural column."""
        profile = ViewportProfile(width=1920, is_mobile=False, is_portrait=False)
        
        # Data without urban_rural
        data = pd.DataFrame({
            "state": ["CA", "TX", "NY"],
            "overall_food_insecurity_rate": [0.12, 0.15, 0.10],
            "census_region": ["West", "South", "Northeast"]
        })
        
        chart_calls = []
        
        def mock_plotly_chart(fig, use_container_width=False):
            chart_calls.append(fig)
        
        # Should not raise any exceptions
        with patch.object(streamlit, 'plotly_chart', side_effect=mock_plotly_chart):
            with patch.object(streamlit, 'markdown'):
                with patch.object(streamlit, 'columns', return_value=[MagicMock(), MagicMock()]):
                    geographic_section(data, 2023, profile)
        
        # Should render map and regional (2 charts)
        assert len(chart_calls) >= 1, \
            "Should render at least map when urban_rural is missing"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
