"""
Property-based tests for chart responsive sizing (Task 5.8).

Tests validate Properties 36, 37, 38 from the executive-overview-redesign spec:
- Property 36: Chart Responsive Width - Charts are 100% of container width
- Property 37: Chart Height Ranges - Height adapts to viewport (240-300px mobile, 300-400px tablet, 400-500px desktop)
- Property 38: Mobile Data Reduction - Mobile reduces data points by 30% (keeps 70%)

Uses Hypothesis for property-based testing with @settings(max_examples=20) for faster execution.
"""

import pytest
from hypothesis import given, strategies as st, settings
from utils.responsive import ViewportProfile, ChartConfig


class TestChartResponsiveSizingProperties:
    """Property-based tests for chart responsive sizing across all viewports."""
    
    @given(viewport_width=st.integers(min_value=320, max_value=2560))
    @settings(max_examples=20)
    def test_property_36_chart_responsive_width(self, viewport_width):
        """
        **Validates: Requirements 11.1**
        
        Property 36: Chart Responsive Width
        
        For any chart visualization at any breakpoint, the chart width SHALL 
        be 100% of its container width.
        
        This property verifies that ChartConfig does not specify a fixed width,
        allowing charts to stretch to 100% of their container width across all
        viewport sizes (mobile, tablet, desktop).
        """
        # Determine viewport characteristics
        is_mobile = viewport_width < 820
        is_portrait = viewport_width < 600
        
        # Create viewport profile
        profile = ViewportProfile(
            width=viewport_width,
            is_mobile=is_mobile,
            is_portrait=is_portrait
        )
        
        # Generate chart config
        config = ChartConfig.for_viewport(profile)
        
        # Verify ChartConfig does not have a width attribute
        # (charts should be 100% of container, not fixed width)
        assert not hasattr(config, 'width') or config.__dict__.get('width') is None, \
            f"ChartConfig should not specify fixed width for viewport {viewport_width}px. " \
            f"Charts must be 100% of container width."
        
        # Verify config has height (which is allowed to be fixed)
        assert hasattr(config, 'height') and config.height > 0, \
            f"ChartConfig should have height attribute for viewport {viewport_width}px"
    
    @given(viewport_width=st.integers(min_value=320, max_value=2560))
    @settings(max_examples=20)
    def test_property_37_chart_height_ranges(self, viewport_width):
        """
        **Validates: Requirements 11.2, 11.3, 11.4**
        
        Property 37: Chart Height Ranges
        
        Chart height must be viewport-specific:
        - Mobile (< 768px): 240-300px (240px portrait, 280px landscape)
        - Tablet (768-1024px): 300-400px (350px)
        - Desktop (> 1024px): 400-500px (450px)
        
        This property verifies that charts adapt their height appropriately
        for each viewport size to ensure readability without excessive scrolling.
        """
        # Determine viewport characteristics
        is_mobile = viewport_width < 820
        is_portrait = viewport_width < 600
        
        # Create viewport profile
        profile = ViewportProfile(
            width=viewport_width,
            is_mobile=is_mobile,
            is_portrait=is_portrait
        )
        
        # Generate chart config
        config = ChartConfig.for_viewport(profile)
        
        # Verify chart height is in correct range based on viewport
        if viewport_width < 768:
            # Mobile: 240-300px
            assert 240 <= config.height <= 300, \
                f"Mobile chart height {config.height}px not in range [240, 300] " \
                f"for viewport {viewport_width}px (portrait={is_portrait})"
        elif viewport_width <= 1024:
            # Tablet: 300-400px
            assert 300 <= config.height <= 400, \
                f"Tablet chart height {config.height}px not in range [300, 400] " \
                f"for viewport {viewport_width}px"
        else:
            # Desktop: 400-500px
            assert 400 <= config.height <= 500, \
                f"Desktop chart height {config.height}px not in range [400, 500] " \
                f"for viewport {viewport_width}px"
    
    @given(viewport_width=st.integers(min_value=320, max_value=767))
    @settings(max_examples=20)
    def test_property_38_mobile_data_reduction(self, viewport_width):
        """
        **Validates: Requirements 12.1**
        
        Property 38: Mobile Data Reduction
        
        For any line chart on viewport width < 768px, the number of rendered 
        data points SHALL be reduced by at least 30% compared to desktop rendering.
        
        This is implemented via data_point_reduction field where:
        - Mobile: 0.7 (keeps 70% of points = 30% reduction)
        - Desktop/Tablet: 1.0 (keeps 100% of points = no reduction)
        
        This optimization improves mobile performance by reducing the number
        of data points rendered in charts.
        """
        # Create mobile viewport profile
        is_portrait = viewport_width < 600
        profile = ViewportProfile(
            width=viewport_width,
            is_mobile=True,
            is_portrait=is_portrait
        )
        
        # Verify breakpoint is mobile
        assert profile.breakpoint_name == "mobile", \
            f"Width {viewport_width}px should be mobile breakpoint"
        
        # Generate chart config for mobile
        mobile_config = ChartConfig.for_viewport(profile)
        
        # Create desktop viewport for comparison
        desktop_profile = ViewportProfile(
            width=1920,
            is_mobile=False,
            is_portrait=False
        )
        desktop_config = ChartConfig.for_viewport(desktop_profile)
        
        # Verify mobile has data point reduction
        assert hasattr(mobile_config, 'data_point_reduction'), \
            "ChartConfig should have data_point_reduction attribute"
        
        # Calculate reduction percentage
        # data_point_reduction = 0.7 means 70% kept, so 30% reduced
        reduction_percentage = (1.0 - mobile_config.data_point_reduction) * 100
        
        # Verify at least 30% reduction on mobile
        assert reduction_percentage >= 30.0, \
            f"Mobile data point reduction {reduction_percentage:.1f}% is less than required 30% " \
            f"for viewport {viewport_width}px (data_point_reduction={mobile_config.data_point_reduction})"
        
        # Verify desktop has no reduction (or less reduction than mobile)
        assert desktop_config.data_point_reduction >= mobile_config.data_point_reduction, \
            f"Desktop should have equal or more data points than mobile. " \
            f"Desktop: {desktop_config.data_point_reduction}, Mobile: {mobile_config.data_point_reduction}"
        
        # Verify mobile reduction is strictly less than desktop (i.e., mobile reduces more)
        assert mobile_config.data_point_reduction < desktop_config.data_point_reduction, \
            f"Mobile should reduce more data points than desktop. " \
            f"Mobile: {mobile_config.data_point_reduction}, Desktop: {desktop_config.data_point_reduction}"


class TestChartResponsiveSizingBoundaryConditions:
    """Test boundary conditions for chart responsive sizing."""
    
    def test_mobile_upper_boundary_767px(self):
        """Test that 767px (mobile upper boundary) has correct sizing."""
        profile = ViewportProfile(width=767, is_mobile=True, is_portrait=False)
        config = ChartConfig.for_viewport(profile)
        
        # Verify height is in mobile range [240, 300]
        assert 240 <= config.height <= 300, \
            f"Mobile boundary (767px) height {config.height}px not in range [240, 300]"
        
        # Verify data reduction is ≥30%
        reduction_percentage = (1.0 - config.data_point_reduction) * 100
        assert reduction_percentage >= 30.0, \
            f"Mobile boundary (767px) should have ≥30% reduction, got {reduction_percentage:.1f}%"
    
    def test_tablet_lower_boundary_768px(self):
        """Test that 768px (tablet lower boundary) has correct sizing."""
        profile = ViewportProfile(width=768, is_mobile=False, is_portrait=False)
        config = ChartConfig.for_viewport(profile)
        
        # Verify height is in tablet range [300, 400]
        assert 300 <= config.height <= 400, \
            f"Tablet boundary (768px) height {config.height}px not in range [300, 400]"
        
        # Verify no data reduction
        assert config.data_point_reduction == 1.0, \
            f"Tablet boundary (768px) should have no reduction, got {config.data_point_reduction}"
    
    def test_tablet_upper_boundary_1024px(self):
        """Test that 1024px (tablet upper boundary) has correct sizing."""
        profile = ViewportProfile(width=1024, is_mobile=False, is_portrait=False)
        config = ChartConfig.for_viewport(profile)
        
        # Verify height is in tablet range [300, 400]
        assert 300 <= config.height <= 400, \
            f"Tablet boundary (1024px) height {config.height}px not in range [300, 400]"
        
        # Verify no data reduction
        assert config.data_point_reduction == 1.0, \
            f"Tablet boundary (1024px) should have no reduction, got {config.data_point_reduction}"
    
    def test_desktop_lower_boundary_1025px(self):
        """Test that 1025px (desktop lower boundary) has correct sizing."""
        profile = ViewportProfile(width=1025, is_mobile=False, is_portrait=False)
        config = ChartConfig.for_viewport(profile)
        
        # Verify height is in desktop range [400, 500]
        assert 400 <= config.height <= 500, \
            f"Desktop boundary (1025px) height {config.height}px not in range [400, 500]"
        
        # Verify no data reduction
        assert config.data_point_reduction == 1.0, \
            f"Desktop boundary (1025px) should have no reduction, got {config.data_point_reduction}"
    
    def test_minimum_mobile_320px(self):
        """Test that 320px (common mobile minimum) has correct sizing."""
        profile = ViewportProfile(width=320, is_mobile=True, is_portrait=True)
        config = ChartConfig.for_viewport(profile)
        
        # Verify height is in mobile range [240, 300]
        assert 240 <= config.height <= 300, \
            f"Minimum mobile (320px) height {config.height}px not in range [240, 300]"
        
        # Verify data reduction is ≥30%
        reduction_percentage = (1.0 - config.data_point_reduction) * 100
        assert reduction_percentage >= 30.0, \
            f"Minimum mobile (320px) should have ≥30% reduction, got {reduction_percentage:.1f}%"


class TestChartResponsiveSizingConsistency:
    """Test that chart sizing is consistent across viewport ranges."""
    
    @given(
        width1=st.integers(min_value=320, max_value=767),
        width2=st.integers(min_value=320, max_value=767)
    )
    @settings(max_examples=10)
    def test_mobile_sizing_is_consistent(self, width1, width2):
        """Test that all mobile viewports have consistent sizing properties."""
        profile1 = ViewportProfile(width=width1, is_mobile=True, is_portrait=width1 < 600)
        profile2 = ViewportProfile(width=width2, is_mobile=True, is_portrait=width2 < 600)
        
        config1 = ChartConfig.for_viewport(profile1)
        config2 = ChartConfig.for_viewport(profile2)
        
        # Data reduction should be consistent across all mobile viewports
        assert config1.data_point_reduction == config2.data_point_reduction, \
            f"Mobile data reduction should be consistent: {width1}px={config1.data_point_reduction}, " \
            f"{width2}px={config2.data_point_reduction}"
    
    @given(
        width1=st.integers(min_value=768, max_value=1024),
        width2=st.integers(min_value=768, max_value=1024)
    )
    @settings(max_examples=10)
    def test_tablet_sizing_is_consistent(self, width1, width2):
        """Test that all tablet viewports have consistent sizing properties."""
        profile1 = ViewportProfile(width=width1, is_mobile=False, is_portrait=False)
        profile2 = ViewportProfile(width=width2, is_mobile=False, is_portrait=False)
        
        config1 = ChartConfig.for_viewport(profile1)
        config2 = ChartConfig.for_viewport(profile2)
        
        # Height should be consistent across all tablet viewports
        assert config1.height == config2.height, \
            f"Tablet chart heights should be consistent: {width1}px={config1.height}px, " \
            f"{width2}px={config2.height}px"
        
        # Data reduction should be 1.0 (no reduction) for all tablet viewports
        assert config1.data_point_reduction == 1.0, \
            f"Tablet should have no reduction: {width1}px={config1.data_point_reduction}"
        assert config2.data_point_reduction == 1.0, \
            f"Tablet should have no reduction: {width2}px={config2.data_point_reduction}"
    
    @given(
        width1=st.integers(min_value=1025, max_value=2560),
        width2=st.integers(min_value=1025, max_value=2560)
    )
    @settings(max_examples=10)
    def test_desktop_sizing_is_consistent(self, width1, width2):
        """Test that all desktop viewports have consistent sizing properties."""
        profile1 = ViewportProfile(width=width1, is_mobile=False, is_portrait=False)
        profile2 = ViewportProfile(width=width2, is_mobile=False, is_portrait=False)
        
        config1 = ChartConfig.for_viewport(profile1)
        config2 = ChartConfig.for_viewport(profile2)
        
        # Height should be consistent across all desktop viewports
        assert config1.height == config2.height, \
            f"Desktop chart heights should be consistent: {width1}px={config1.height}px, " \
            f"{width2}px={config2.height}px"
        
        # Data reduction should be 1.0 (no reduction) for all desktop viewports
        assert config1.data_point_reduction == 1.0, \
            f"Desktop should have no reduction: {width1}px={config1.data_point_reduction}"
        assert config2.data_point_reduction == 1.0, \
            f"Desktop should have no reduction: {width2}px={config2.data_point_reduction}"


class TestChartResponsiveSizingIntegration:
    """Integration tests for chart responsive sizing across all properties."""
    
    @given(viewport_width=st.integers(min_value=320, max_value=2560))
    @settings(max_examples=20)
    def test_all_properties_together(self, viewport_width):
        """
        Test that all three properties (36, 37, 38) work together correctly
        for any viewport width.
        """
        # Determine viewport characteristics
        is_mobile = viewport_width < 820
        is_portrait = viewport_width < 600
        
        # Create viewport profile
        profile = ViewportProfile(
            width=viewport_width,
            is_mobile=is_mobile,
            is_portrait=is_portrait
        )
        
        # Generate chart config
        config = ChartConfig.for_viewport(profile)
        
        # Property 36: No fixed width (charts are 100% of container)
        assert not hasattr(config, 'width') or config.__dict__.get('width') is None, \
            f"Property 36 violation: ChartConfig should not specify fixed width"
        
        # Property 37: Height in correct range
        if viewport_width < 768:
            assert 240 <= config.height <= 300, \
                f"Property 37 violation: Mobile height {config.height}px not in [240, 300]"
        elif viewport_width <= 1024:
            assert 300 <= config.height <= 400, \
                f"Property 37 violation: Tablet height {config.height}px not in [300, 400]"
        else:
            assert 400 <= config.height <= 500, \
                f"Property 37 violation: Desktop height {config.height}px not in [400, 500]"
        
        # Property 38: Mobile data reduction ≥30%
        if viewport_width < 768:
            reduction_percentage = (1.0 - config.data_point_reduction) * 100
            assert reduction_percentage >= 30.0, \
                f"Property 38 violation: Mobile reduction {reduction_percentage:.1f}% < 30%"
        else:
            # Non-mobile should have no reduction
            assert config.data_point_reduction == 1.0, \
                f"Property 38 violation: Non-mobile should have no reduction, got {config.data_point_reduction}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
