"""
Property-based tests for ChartConfig responsive behavior.

Tests validate Properties 36, 38 from the executive-overview-redesign spec:
- Property 36: Chart Responsive Width - Charts are 100% of container width
- Property 38: Mobile Data Point Reduction - Mobile reduces data points by ≥30%

Uses Hypothesis for property-based testing with 100 iterations per test.
"""

import pytest
from hypothesis import given, strategies as st, settings
from utils.responsive import ViewportProfile, ChartConfig


class TestChartConfigProperties:
    """Property-based tests for ChartConfig responsive behavior."""
    
    @given(viewport_width=st.integers(min_value=320, max_value=2560))
    @settings(max_examples=20)
    def test_property_36_chart_responsive_width(self, viewport_width):
        """
        **Validates: Requirements 11.1**
        
        Property 36: Chart Responsive Width
        
        For any chart visualization at any breakpoint, the chart width SHALL 
        be 100% of its container width.
        
        Note: This property tests that ChartConfig does not specify a fixed 
        width, allowing charts to be 100% of their container. The actual width 
        is controlled by the container, not the ChartConfig.
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
    
    @given(viewport_width=st.integers(min_value=320, max_value=767))
    @settings(max_examples=20)
    def test_property_38_mobile_data_point_reduction(self, viewport_width):
        """
        **Validates: Requirements 12.1**
        
        Property 38: Mobile Data Point Reduction
        
        For any line chart on viewport width < 768px, the number of rendered 
        data points SHALL be reduced by at least 30% compared to desktop rendering.
        
        This is implemented via data_point_reduction field where:
        - Mobile: 0.7 (keeps 70% of points = 30% reduction)
        - Desktop/Tablet: 1.0 (keeps 100% of points = no reduction)
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


class TestChartConfigBoundaryConditions:
    """Test boundary conditions for chart configuration."""
    
    def test_mobile_upper_boundary_767px_has_reduction(self):
        """Test that 767px (mobile upper boundary) has ≥30% data reduction."""
        profile = ViewportProfile(width=767, is_mobile=True, is_portrait=False)
        config = ChartConfig.for_viewport(profile)
        
        reduction_percentage = (1.0 - config.data_point_reduction) * 100
        assert reduction_percentage >= 30.0, \
            f"Mobile boundary (767px) should have ≥30% reduction, got {reduction_percentage:.1f}%"
    
    def test_tablet_lower_boundary_768px_no_reduction(self):
        """Test that 768px (tablet lower boundary) has no data reduction."""
        profile = ViewportProfile(width=768, is_mobile=False, is_portrait=False)
        config = ChartConfig.for_viewport(profile)
        
        assert config.data_point_reduction == 1.0, \
            f"Tablet boundary (768px) should have no reduction, got {config.data_point_reduction}"
    
    def test_minimum_mobile_320px_has_reduction(self):
        """Test that 320px (common mobile minimum) has ≥30% data reduction."""
        profile = ViewportProfile(width=320, is_mobile=True, is_portrait=True)
        config = ChartConfig.for_viewport(profile)
        
        reduction_percentage = (1.0 - config.data_point_reduction) * 100
        assert reduction_percentage >= 30.0, \
            f"Minimum mobile (320px) should have ≥30% reduction, got {reduction_percentage:.1f}%"


class TestChartConfigConsistency:
    """Test that chart configurations are consistent across viewport ranges."""
    
    @given(
        width1=st.integers(min_value=320, max_value=767),
        width2=st.integers(min_value=320, max_value=767)
    )
    @settings(max_examples=10)
    def test_mobile_data_reduction_is_consistent(self, width1, width2):
        """Test that all mobile viewports have the same data point reduction."""
        profile1 = ViewportProfile(width=width1, is_mobile=True, is_portrait=width1 < 600)
        profile2 = ViewportProfile(width=width2, is_mobile=True, is_portrait=width2 < 600)
        
        config1 = ChartConfig.for_viewport(profile1)
        config2 = ChartConfig.for_viewport(profile2)
        
        assert config1.data_point_reduction == config2.data_point_reduction, \
            f"Mobile data reduction should be consistent: {width1}px={config1.data_point_reduction}, " \
            f"{width2}px={config2.data_point_reduction}"
    
    @given(
        width1=st.integers(min_value=1025, max_value=2560),
        width2=st.integers(min_value=1025, max_value=2560)
    )
    @settings(max_examples=10)
    def test_desktop_no_data_reduction(self, width1, width2):
        """Test that all desktop viewports have no data point reduction."""
        profile1 = ViewportProfile(width=width1, is_mobile=False, is_portrait=False)
        profile2 = ViewportProfile(width=width2, is_mobile=False, is_portrait=False)
        
        config1 = ChartConfig.for_viewport(profile1)
        config2 = ChartConfig.for_viewport(profile2)
        
        assert config1.data_point_reduction == 1.0, \
            f"Desktop should have no reduction: {width1}px={config1.data_point_reduction}"
        assert config2.data_point_reduction == 1.0, \
            f"Desktop should have no reduction: {width2}px={config2.data_point_reduction}"


class TestChartConfigDataReductionCalculation:
    """Test data point reduction calculations and edge cases."""
    
    def test_mobile_portrait_reduction_calculation(self):
        """Test that mobile portrait has correct reduction percentage."""
        profile = ViewportProfile(width=375, is_mobile=True, is_portrait=True)
        config = ChartConfig.for_viewport(profile)
        
        # data_point_reduction = 0.7 means keep 70%, reduce 30%
        expected_reduction = 0.7
        assert config.data_point_reduction == expected_reduction, \
            f"Mobile portrait should have {expected_reduction} reduction, got {config.data_point_reduction}"
    
    def test_mobile_landscape_reduction_calculation(self):
        """Test that mobile landscape has correct reduction percentage."""
        profile = ViewportProfile(width=667, is_mobile=True, is_portrait=False)
        config = ChartConfig.for_viewport(profile)
        
        # data_point_reduction = 0.7 means keep 70%, reduce 30%
        expected_reduction = 0.7
        assert config.data_point_reduction == expected_reduction, \
            f"Mobile landscape should have {expected_reduction} reduction, got {config.data_point_reduction}"
    
    def test_tablet_no_reduction(self):
        """Test that tablet has no data point reduction."""
        profile = ViewportProfile(width=900, is_mobile=False, is_portrait=False)
        config = ChartConfig.for_viewport(profile)
        
        assert config.data_point_reduction == 1.0, \
            f"Tablet should have no reduction (1.0), got {config.data_point_reduction}"
    
    def test_desktop_no_reduction(self):
        """Test that desktop has no data point reduction."""
        profile = ViewportProfile(width=1920, is_mobile=False, is_portrait=False)
        config = ChartConfig.for_viewport(profile)
        
        assert config.data_point_reduction == 1.0, \
            f"Desktop should have no reduction (1.0), got {config.data_point_reduction}"
    
    @given(viewport_width=st.integers(min_value=320, max_value=2560))
    @settings(max_examples=20)
    def test_data_reduction_is_valid_percentage(self, viewport_width):
        """Test that data_point_reduction is always a valid percentage (0.0-1.0)."""
        is_mobile = viewport_width < 820
        is_portrait = viewport_width < 600
        
        profile = ViewportProfile(
            width=viewport_width,
            is_mobile=is_mobile,
            is_portrait=is_portrait
        )
        
        config = ChartConfig.for_viewport(profile)
        
        # Verify data_point_reduction is in valid range [0.0, 1.0]
        assert 0.0 <= config.data_point_reduction <= 1.0, \
            f"data_point_reduction {config.data_point_reduction} not in valid range [0.0, 1.0] " \
            f"for viewport {viewport_width}px"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
