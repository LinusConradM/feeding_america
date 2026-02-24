"""
Unit tests for quick_tips_callout component.

Tests verify the quick_tips_callout component renders correctly with:
- List of 3-5 tips
- Dismissible functionality with localStorage
- Proper styling and accessibility
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import streamlit as st


def test_quick_tips_callout_renders_with_tips():
    """Test quick_tips_callout renders with provided tips."""
    from utils.components import quick_tips_callout
    
    tips = [
        "Tip 1: Use the dropdown",
        "Tip 2: Hover over charts",
        "Tip 3: Collapse sections"
    ]
    
    # Mock st.components.v1.html
    with patch('streamlit.components.v1.html') as mock_html:
        quick_tips_callout(tips, dismissible=True)
        
        # Verify html was called
        assert mock_html.called
        
        # Get the HTML content
        html_content = mock_html.call_args[0][0]
        
        # Verify all tips are in the HTML
        for tip in tips:
            assert tip in html_content
        
        # Verify styling elements
        assert "quick-tips-banner" in html_content
        assert "lightbulb" in html_content
        assert "Quick Tips" in html_content


def test_quick_tips_callout_with_dismissible_button():
    """Test quick_tips_callout includes dismiss button when dismissible=True."""
    from utils.components import quick_tips_callout
    
    tips = ["Tip 1", "Tip 2", "Tip 3"]
    
    with patch('streamlit.components.v1.html') as mock_html:
        quick_tips_callout(tips, dismissible=True)
        
        html_content = mock_html.call_args[0][0]
        
        # Verify dismiss button is present
        assert "quick-tips-dismiss" in html_content
        assert "dismissQuickTips()" in html_content
        assert "✕" in html_content


def test_quick_tips_callout_without_dismissible_button():
    """Test quick_tips_callout excludes dismiss button when dismissible=False."""
    from utils.components import quick_tips_callout
    
    tips = ["Tip 1", "Tip 2", "Tip 3"]
    
    with patch('streamlit.components.v1.html') as mock_html:
        quick_tips_callout(tips, dismissible=False)
        
        html_content = mock_html.call_args[0][0]
        
        # Verify dismiss button is NOT present
        assert "quick-tips-dismiss" not in html_content or "<button" not in html_content


def test_quick_tips_callout_localStorage_integration():
    """Test quick_tips_callout includes localStorage check and set."""
    from utils.components import quick_tips_callout
    
    tips = ["Tip 1", "Tip 2", "Tip 3"]
    
    with patch('streamlit.components.v1.html') as mock_html:
        quick_tips_callout(tips, dismissible=True)
        
        html_content = mock_html.call_args[0][0]
        
        # Verify localStorage operations
        assert "localStorage.getItem" in html_content
        assert "localStorage.setItem" in html_content
        assert "quick_tips_dismissed" in html_content


def test_quick_tips_callout_with_five_tips():
    """Test quick_tips_callout handles maximum of 5 tips."""
    from utils.components import quick_tips_callout
    
    tips = [
        "Tip 1: First tip",
        "Tip 2: Second tip",
        "Tip 3: Third tip",
        "Tip 4: Fourth tip",
        "Tip 5: Fifth tip"
    ]
    
    with patch('streamlit.components.v1.html') as mock_html:
        quick_tips_callout(tips, dismissible=True)
        
        html_content = mock_html.call_args[0][0]
        
        # Verify all 5 tips are present
        for tip in tips:
            assert tip in html_content


def test_quick_tips_callout_with_three_tips():
    """Test quick_tips_callout handles minimum of 3 tips."""
    from utils.components import quick_tips_callout
    
    tips = [
        "Tip 1: First tip",
        "Tip 2: Second tip",
        "Tip 3: Third tip"
    ]
    
    with patch('streamlit.components.v1.html') as mock_html:
        quick_tips_callout(tips, dismissible=True)
        
        html_content = mock_html.call_args[0][0]
        
        # Verify all 3 tips are present
        for tip in tips:
            assert tip in html_content


def test_quick_tips_callout_styling():
    """Test quick_tips_callout includes proper styling."""
    from utils.components import quick_tips_callout
    
    tips = ["Tip 1", "Tip 2", "Tip 3"]
    
    with patch('streamlit.components.v1.html') as mock_html:
        quick_tips_callout(tips, dismissible=True)
        
        html_content = mock_html.call_args[0][0]
        
        # Verify styling elements
        assert "#FFFBEB" in html_content  # Background color
        assert "#F59E0B" in html_content  # Border and icon color
        assert "border-left: 4px solid" in html_content
        assert "border-radius" in html_content


def test_quick_tips_callout_accessibility():
    """Test quick_tips_callout includes accessibility features."""
    from utils.components import quick_tips_callout
    
    tips = ["Tip 1", "Tip 2", "Tip 3"]
    
    with patch('streamlit.components.v1.html') as mock_html:
        quick_tips_callout(tips, dismissible=True)
        
        html_content = mock_html.call_args[0][0]
        
        # Verify accessibility features
        assert "aria-label" in html_content
        assert "min-width: 44px" in html_content  # Touch target size
        assert "min-height: 44px" in html_content  # Touch target size


def test_quick_tips_callout_javascript_functionality():
    """Test quick_tips_callout includes JavaScript for show/hide logic."""
    from utils.components import quick_tips_callout
    
    tips = ["Tip 1", "Tip 2", "Tip 3"]
    
    with patch('streamlit.components.v1.html') as mock_html:
        quick_tips_callout(tips, dismissible=True)
        
        html_content = mock_html.call_args[0][0]
        
        # Verify JavaScript functionality
        assert "<script>" in html_content
        assert "function dismissQuickTips()" in html_content
        assert "classList.add('visible')" in html_content
        assert "style.display = 'none'" in html_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
