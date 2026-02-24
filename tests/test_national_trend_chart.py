"""
Integration test for National Trend Chart enhancements (Task 5.7).

Tests that the National Trend Chart section:
1. Uses ChartConfig.for_viewport() for responsive sizing
2. Reduces data points by 30% for mobile viewports
3. Has AI-generated insights tooltip on hover
"""

import re
import numpy as np
import pandas as pd
from utils.responsive import ViewportProfile, ChartConfig


def test_chart_config_applied():
    """Test that ChartConfig.for_viewport() is used in the National Trend Chart section."""
    with open("views/1_Executive_Overview.py", "r") as f:
        source_code = f.read()
    
    # Find the National Trend Chart section
    section_match = re.search(
        r'# SECTION 2.*NATIONAL TREND.*?(?=# SECTION|\Z)',
        source_code,
        re.DOTALL | re.IGNORECASE
    )
    
    assert section_match, "National Trend Chart section not found"
    section_code = section_match.group(0)
    
    # Verify ChartConfig import and usage
    assert "from utils.responsive import ChartConfig" in section_code, \
        "ChartConfig must be imported in National Trend section"
    
    assert "ChartConfig.for_viewport(viewport)" in section_code, \
        "ChartConfig.for_viewport() must be called with viewport"
    
    assert "chart_config = ChartConfig.for_viewport(viewport)" in section_code, \
        "chart_config variable must be assigned from ChartConfig.for_viewport()"
    
    print("✓ ChartConfig.for_viewport() is properly applied")


def test_responsive_sizing_properties():
    """Test that chart uses ChartConfig properties for responsive sizing."""
    with open("views/1_Executive_Overview.py", "r") as f:
        source_code = f.read()
    
    # Find the National Trend Chart section
    section_match = re.search(
        r'# SECTION 2.*NATIONAL TREND.*?(?=# SECTION|\Z)',
        source_code,
        re.DOTALL | re.IGNORECASE
    )
    
    assert section_match, "National Trend Chart section not found"
    section_code = section_match.group(0)
    
    # Verify chart uses chart_config properties
    assert "chart_config.line_width" in section_code, \
        "Chart must use chart_config.line_width"
    
    assert "chart_config.marker_size" in section_code, \
        "Chart must use chart_config.marker_size"
    
    assert "chart_config.height" in section_code, \
        "Chart must use chart_config.height"
    
    assert "chart_config.margin" in section_code, \
        "Chart must use chart_config.margin"
    
    assert "chart_config.show_legend" in section_code, \
        "Chart must use chart_config.show_legend"
    
    # Verify old hardcoded values are removed
    assert "line_width = 2 if IS_MOBILE else 3" not in section_code, \
        "Old hardcoded line_width should be removed"
    
    assert "marker_size = 5 if IS_MOBILE else 8" not in section_code, \
        "Old hardcoded marker_size should be removed"
    
    assert "height = 240 if IS_PORTRAIT" not in section_code, \
        "Old hardcoded height should be removed"
    
    print("✓ Chart uses ChartConfig properties for responsive sizing")


def test_data_point_reduction_for_mobile():
    """Test that data points are reduced by 30% for mobile viewports."""
    with open("views/1_Executive_Overview.py", "r") as f:
        source_code = f.read()
    
    # Find the National Trend Chart section
    section_match = re.search(
        r'# SECTION 2.*NATIONAL TREND.*?(?=# SECTION|\Z)',
        source_code,
        re.DOTALL | re.IGNORECASE
    )
    
    assert section_match, "National Trend Chart section not found"
    section_code = section_match.group(0)
    
    # Verify data point reduction logic exists
    assert "chart_config.data_point_reduction" in section_code, \
        "Chart must check chart_config.data_point_reduction"
    
    assert "data_point_reduction < 1.0" in section_code, \
        "Chart must check if data_point_reduction < 1.0"
    
    # Verify sampling logic
    assert "np.linspace" in section_code or "indices" in section_code, \
        "Chart must use sampling to reduce data points"
    
    print("✓ Data point reduction logic is implemented for mobile")


def test_data_point_reduction_calculation():
    """Test that data point reduction calculation is correct (30% reduction = 70% kept)."""
    # Create sample data
    trend = pd.DataFrame({
        "Year": range(2009, 2024),  # 15 years
        "FI Rate": np.random.uniform(0.10, 0.15, 15)
    })
    
    # Test mobile viewport (should reduce to 70% = ~10 points)
    mobile_viewport = ViewportProfile(width=600, is_mobile=True, is_portrait=True)
    mobile_config = ChartConfig.for_viewport(mobile_viewport)
    
    assert mobile_config.data_point_reduction == 0.7, \
        "Mobile viewport should have data_point_reduction = 0.7 (keep 70%)"
    
    total_points = len(trend)
    points_to_keep = int(total_points * mobile_config.data_point_reduction)
    
    assert points_to_keep == 10, \
        f"Mobile should keep 10 points (70% of 15), got {points_to_keep}"
    
    # Test desktop viewport (should keep all points)
    desktop_viewport = ViewportProfile(width=1920, is_mobile=False, is_portrait=False)
    desktop_config = ChartConfig.for_viewport(desktop_viewport)
    
    assert desktop_config.data_point_reduction == 1.0, \
        "Desktop viewport should have data_point_reduction = 1.0 (keep 100%)"
    
    print("✓ Data point reduction calculation is correct (30% reduction)")


def test_ai_insights_tooltip_present():
    """Test that AI-generated insights tooltip is present on hover."""
    with open("views/1_Executive_Overview.py", "r") as f:
        source_code = f.read()
    
    # Find the National Trend Chart section
    section_match = re.search(
        r'# SECTION 2.*NATIONAL TREND.*?(?=# SECTION|\Z)',
        source_code,
        re.DOTALL | re.IGNORECASE
    )
    
    assert section_match, "National Trend Chart section not found"
    section_code = section_match.group(0)
    
    # Verify AI insights are generated
    assert "explain_plot" in section_code, \
        "Chart must call explain_plot() to generate AI insights"
    
    assert "trend_explainer" in section_code, \
        "Chart must store AI insights in trend_explainer variable"
    
    # Verify tooltip/hover functionality
    assert "trend-explainer" in section_code, \
        "Chart must have trend-explainer CSS class for tooltip"
    
    assert ":hover" in section_code or "hover" in section_code, \
        "Chart must have hover functionality for tooltip"
    
    # Verify tooltip is rendered in HTML
    assert "st.components.v1.html" in section_code, \
        "Chart must render HTML with tooltip"
    
    print("✓ AI-generated insights tooltip is present on hover")


def test_tooltip_uses_chart_config_height():
    """Test that the HTML component height uses chart_config.height."""
    with open("views/1_Executive_Overview.py", "r") as f:
        source_code = f.read()
    
    # Find the National Trend Chart section
    section_match = re.search(
        r'# SECTION 2.*NATIONAL TREND.*?(?=# SECTION|\Z)',
        source_code,
        re.DOTALL | re.IGNORECASE
    )
    
    assert section_match, "National Trend Chart section not found"
    section_code = section_match.group(0)
    
    # Verify HTML component uses chart_config.height
    assert "st.components.v1.html(trend_html, height=chart_config.height" in section_code, \
        "HTML component must use chart_config.height"
    
    # Verify old hardcoded height is removed
    assert "height=height + 40" not in section_code, \
        "Old hardcoded height variable should be removed"
    
    print("✓ HTML component uses chart_config.height")


if __name__ == "__main__":
    print("\n=== Testing National Trend Chart Enhancements (Task 5.7) ===\n")
    
    test_chart_config_applied()
    test_responsive_sizing_properties()
    test_data_point_reduction_for_mobile()
    test_data_point_reduction_calculation()
    test_ai_insights_tooltip_present()
    test_tooltip_uses_chart_config_height()
    
    print("\n✅ All National Trend Chart enhancement tests passed!")
