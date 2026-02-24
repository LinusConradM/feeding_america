"""
Unit tests for utils/responsive.py ViewportProfile enhancements.

Tests verify the new properties added to ViewportProfile:
- breakpoint_name
- chart_height
- kpi_columns
"""

import pytest
from utils.responsive import ViewportProfile


class TestViewportProfileBreakpointName:
    """Test breakpoint_name property returns correct values."""
    
    def test_mobile_breakpoint(self):
        """Test mobile viewport returns 'mobile' breakpoint name."""
        profile = ViewportProfile(width=767, is_mobile=True, is_portrait=True)
        assert profile.breakpoint_name == "mobile"
    
    def test_tablet_breakpoint(self):
        """Test tablet viewport returns 'tablet' breakpoint name."""
        profile = ViewportProfile(width=900, is_mobile=False, is_portrait=False)
        assert profile.breakpoint_name == "tablet"
    
    def test_desktop_breakpoint(self):
        """Test desktop viewport returns 'desktop' breakpoint name."""
        profile = ViewportProfile(width=1920, is_mobile=False, is_portrait=False)
        assert profile.breakpoint_name == "desktop"
    
    def test_tablet_upper_boundary(self):
        """Test tablet upper boundary (1024px) returns 'tablet'."""
        profile = ViewportProfile(width=1024, is_mobile=False, is_portrait=False)
        assert profile.breakpoint_name == "tablet"
    
    def test_desktop_lower_boundary(self):
        """Test desktop lower boundary (1025px) returns 'desktop'."""
        profile = ViewportProfile(width=1025, is_mobile=False, is_portrait=False)
        assert profile.breakpoint_name == "desktop"


class TestViewportProfileChartHeight:
    """Test chart_height property returns correct heights."""
    
    def test_portrait_mobile_height(self):
        """Test portrait mobile returns 240px height."""
        profile = ViewportProfile(width=375, is_mobile=True, is_portrait=True)
        assert profile.chart_height == 240
    
    def test_landscape_mobile_height(self):
        """Test landscape mobile returns 280px height."""
        profile = ViewportProfile(width=767, is_mobile=True, is_portrait=False)
        assert profile.chart_height == 280
    
    def test_tablet_height(self):
        """Test tablet returns 350px height."""
        profile = ViewportProfile(width=900, is_mobile=False, is_portrait=False)
        assert profile.chart_height == 350
    
    def test_desktop_height(self):
        """Test desktop returns 450px height."""
        profile = ViewportProfile(width=1920, is_mobile=False, is_portrait=False)
        assert profile.chart_height == 450


class TestViewportProfileKpiColumns:
    """Test kpi_columns property returns correct column counts."""
    
    def test_mobile_columns(self):
        """Test mobile returns 1 column."""
        profile = ViewportProfile(width=767, is_mobile=True, is_portrait=True)
        assert profile.kpi_columns == 1
    
    def test_tablet_columns(self):
        """Test tablet returns 2 columns."""
        profile = ViewportProfile(width=900, is_mobile=False, is_portrait=False)
        assert profile.kpi_columns == 2
    
    def test_desktop_columns(self):
        """Test desktop returns 4 columns."""
        profile = ViewportProfile(width=1920, is_mobile=False, is_portrait=False)
        assert profile.kpi_columns == 4


class TestViewportProfileEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_none_width_defaults_to_desktop(self):
        """Test None width defaults to desktop breakpoint."""
        profile = ViewportProfile(width=None, is_mobile=False, is_portrait=False)
        assert profile.breakpoint_name == "desktop"
        assert profile.chart_height == 450
        assert profile.kpi_columns == 4
    
    def test_portrait_overrides_mobile_height(self):
        """Test portrait flag takes precedence for chart height."""
        profile = ViewportProfile(width=500, is_mobile=True, is_portrait=True)
        assert profile.chart_height == 240  # Portrait height, not mobile height
    
    def test_mobile_flag_determines_breakpoint(self):
        """Test is_mobile flag determines mobile breakpoint regardless of width."""
        profile = ViewportProfile(width=800, is_mobile=True, is_portrait=False)
        assert profile.breakpoint_name == "mobile"
        assert profile.kpi_columns == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
