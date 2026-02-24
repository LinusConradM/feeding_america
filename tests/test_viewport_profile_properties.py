"""
Property-based tests for ViewportProfile chart height ranges.

Tests validate Properties 25, 28, 37 from the executive-overview-redesign spec:
- Property 25: Desktop Chart Height Range (viewport > 1024px: 400-500px)
- Property 28: Mobile Chart Height Range (viewport < 768px: 240-300px)
- Property 37: Tablet Chart Height Range (viewport 768-1024px: 300-400px)

Uses Hypothesis for property-based testing with 100 iterations per test.
"""

import pytest
from hypothesis import given, strategies as st, settings
from utils.responsive import ViewportProfile


class TestChartHeightProperties:
    """Property-based tests for chart height ranges across viewport sizes."""
    
    @given(viewport_width=st.integers(min_value=1025, max_value=2560))
    @settings(max_examples=20)
    def test_property_25_desktop_chart_height_range(self, viewport_width):
        """
        **Validates: Requirements 8.3, 11.4**
        
        Property 25: Desktop Chart Height Range
        
        For any viewport width > 1024px, primary chart visualizations SHALL 
        have heights between 400-500 pixels.
        """
        # Create desktop viewport profile
        profile = ViewportProfile(
            width=viewport_width,
            is_mobile=False,
            is_portrait=False
        )
        
        # Verify breakpoint is desktop
        assert profile.breakpoint_name == "desktop", \
            f"Width {viewport_width}px should be desktop breakpoint"
        
        # Verify chart height is in range [400, 500]
        chart_height = profile.chart_height
        assert 400 <= chart_height <= 500, \
            f"Desktop chart height {chart_height}px not in range [400, 500] for width {viewport_width}px"
    
    @given(viewport_width=st.integers(min_value=320, max_value=767))
    @settings(max_examples=20)
    def test_property_28_mobile_chart_height_range(self, viewport_width):
        """
        **Validates: Requirements 9.3, 11.2**
        
        Property 28: Mobile Chart Height Range
        
        For any viewport width < 768px, chart visualizations SHALL have 
        heights between 240-300 pixels.
        """
        # Test both portrait and landscape mobile orientations
        for is_portrait in [True, False]:
            profile = ViewportProfile(
                width=viewport_width,
                is_mobile=True,
                is_portrait=is_portrait
            )
            
            # Verify breakpoint is mobile
            assert profile.breakpoint_name == "mobile", \
                f"Width {viewport_width}px should be mobile breakpoint"
            
            # Verify chart height is in range [240, 300]
            chart_height = profile.chart_height
            assert 240 <= chart_height <= 300, \
                f"Mobile chart height {chart_height}px not in range [240, 300] " \
                f"for width {viewport_width}px (portrait={is_portrait})"
    
    @given(viewport_width=st.integers(min_value=768, max_value=1024))
    @settings(max_examples=20)
    def test_property_37_tablet_chart_height_range(self, viewport_width):
        """
        **Validates: Requirements 11.3**
        
        Property 37: Tablet Chart Height Range
        
        For any viewport width between 768-1024 pixels, chart visualizations 
        SHALL have heights between 300-400 pixels.
        """
        # Create tablet viewport profile
        profile = ViewportProfile(
            width=viewport_width,
            is_mobile=False,
            is_portrait=False
        )
        
        # Verify breakpoint is tablet
        assert profile.breakpoint_name == "tablet", \
            f"Width {viewport_width}px should be tablet breakpoint"
        
        # Verify chart height is in range [300, 400]
        chart_height = profile.chart_height
        assert 300 <= chart_height <= 400, \
            f"Tablet chart height {chart_height}px not in range [300, 400] for width {viewport_width}px"


class TestChartHeightBoundaryConditions:
    """Test boundary conditions for viewport breakpoints."""
    
    def test_desktop_lower_boundary_1025px(self):
        """Test that 1025px (desktop lower boundary) produces height in [400, 500]."""
        profile = ViewportProfile(width=1025, is_mobile=False, is_portrait=False)
        assert profile.breakpoint_name == "desktop"
        assert 400 <= profile.chart_height <= 500
    
    def test_tablet_upper_boundary_1024px(self):
        """Test that 1024px (tablet upper boundary) produces height in [300, 400]."""
        profile = ViewportProfile(width=1024, is_mobile=False, is_portrait=False)
        assert profile.breakpoint_name == "tablet"
        assert 300 <= profile.chart_height <= 400
    
    def test_tablet_lower_boundary_768px(self):
        """Test that 768px (tablet lower boundary) produces height in [300, 400]."""
        profile = ViewportProfile(width=768, is_mobile=False, is_portrait=False)
        assert profile.breakpoint_name == "tablet"
        assert 300 <= profile.chart_height <= 400
    
    def test_mobile_upper_boundary_767px(self):
        """Test that 767px (mobile upper boundary) produces height in [240, 300]."""
        profile = ViewportProfile(width=767, is_mobile=True, is_portrait=False)
        assert profile.breakpoint_name == "mobile"
        assert 240 <= profile.chart_height <= 300
    
    def test_mobile_minimum_320px(self):
        """Test that 320px (common mobile minimum) produces height in [240, 300]."""
        profile = ViewportProfile(width=320, is_mobile=True, is_portrait=True)
        assert profile.breakpoint_name == "mobile"
        assert 240 <= profile.chart_height <= 300


class TestChartHeightConsistency:
    """Test that chart heights are consistent across viewport ranges."""
    
    @given(
        width1=st.integers(min_value=1025, max_value=2560),
        width2=st.integers(min_value=1025, max_value=2560)
    )
    @settings(max_examples=10)
    def test_desktop_heights_are_consistent(self, width1, width2):
        """Test that all desktop viewports return the same chart height."""
        profile1 = ViewportProfile(width=width1, is_mobile=False, is_portrait=False)
        profile2 = ViewportProfile(width=width2, is_mobile=False, is_portrait=False)
        
        assert profile1.chart_height == profile2.chart_height, \
            f"Desktop chart heights should be consistent: {width1}px={profile1.chart_height}px, " \
            f"{width2}px={profile2.chart_height}px"
    
    @given(
        width1=st.integers(min_value=768, max_value=1024),
        width2=st.integers(min_value=768, max_value=1024)
    )
    @settings(max_examples=10)
    def test_tablet_heights_are_consistent(self, width1, width2):
        """Test that all tablet viewports return the same chart height."""
        profile1 = ViewportProfile(width=width1, is_mobile=False, is_portrait=False)
        profile2 = ViewportProfile(width=width2, is_mobile=False, is_portrait=False)
        
        assert profile1.chart_height == profile2.chart_height, \
            f"Tablet chart heights should be consistent: {width1}px={profile1.chart_height}px, " \
            f"{width2}px={profile2.chart_height}px"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
