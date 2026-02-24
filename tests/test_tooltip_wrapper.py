"""
Unit tests for tooltip_wrapper component.

Tests verify the tooltip_wrapper component implementation meets requirements:
- Desktop: CSS-only hover tooltip (200ms delay)
- Mobile: Tap icon to show tooltip in modal/popover
- Touch target: 44x44px minimum
- Dismissible on outside click
- Supports positioning (top, bottom, left, right)

Validates Requirements: 6.3, 6.4, 6.5, 10.1
"""

import pytest
from unittest.mock import Mock, patch
from utils.components import tooltip_wrapper


def test_tooltip_wrapper_basic_rendering():
    """Test tooltip_wrapper renders with basic parameters."""
    # Mock streamlit
    with patch('utils.components.st') as mock_st:
        mock_st.html = Mock()
        mock_st.markdown = Mock()
        
        # Call tooltip_wrapper
        tooltip_wrapper(
            content="Test Content",
            tooltip_text="This is help text",
            icon="info-circle",
            position="top"
        )
        
        # Verify either st.html or st.markdown was called
        assert mock_st.html.called or mock_st.markdown.called


def test_tooltip_wrapper_contains_content():
    """Test tooltip_wrapper includes the main content."""
    with patch('utils.components.st') as mock_st:
        mock_st.html = Mock()
        
        tooltip_wrapper(
            content="Main Content",
            tooltip_text="Help text",
            icon="info-circle",
            position="top"
        )
        
        # Get the HTML that was rendered
        call_args = mock_st.html.call_args
        html_output = call_args[0][0] if call_args else ""
        
        # Verify content is in the output
        assert "Main Content" in html_output
        assert "Help text" in html_output


def test_tooltip_wrapper_contains_tooltip_text():
    """Test tooltip_wrapper includes the tooltip text."""
    with patch('utils.components.st') as mock_st:
        mock_st.html = Mock()
        
        tooltip_wrapper(
            content="Content",
            tooltip_text="This is the tooltip explanation",
            icon="info-circle",
            position="top"
        )
        
        call_args = mock_st.html.call_args
        html_output = call_args[0][0] if call_args else ""
        
        assert "This is the tooltip explanation" in html_output


def test_tooltip_wrapper_has_mobile_touch_target():
    """Test tooltip_wrapper has 44x44px minimum touch target for mobile (Requirement 10.1)."""
    with patch('utils.components.st') as mock_st:
        mock_st.html = Mock()
        
        tooltip_wrapper(
            content="Content",
            tooltip_text="Help",
            icon="info-circle",
            position="top"
        )
        
        call_args = mock_st.html.call_args
        html_output = call_args[0][0] if call_args else ""
        
        # Verify mobile icon has 44x44px minimum dimensions
        assert "min-width: 44px" in html_output
        assert "min-height: 44px" in html_output


def test_tooltip_wrapper_has_200ms_delay():
    """Test tooltip_wrapper has 200ms delay for desktop hover (Requirement 6.3)."""
    with patch('utils.components.st') as mock_st:
        mock_st.html = Mock()
        
        tooltip_wrapper(
            content="Content",
            tooltip_text="Help",
            icon="info-circle",
            position="top"
        )
        
        call_args = mock_st.html.call_args
        html_output = call_args[0][0] if call_args else ""
        
        # Verify 200ms transition delay is present
        assert "transition-delay: 200ms" in html_output


def test_tooltip_wrapper_supports_all_positions():
    """Test tooltip_wrapper supports all position options."""
    positions = ["top", "bottom", "left", "right"]
    
    for position in positions:
        with patch('utils.components.st') as mock_st:
            mock_st.html = Mock()
            
            tooltip_wrapper(
                content="Content",
                tooltip_text="Help",
                icon="info-circle",
                position=position
            )
            
            # Should not raise any errors
            assert mock_st.html.called


def test_tooltip_wrapper_has_dismissible_modal():
    """Test tooltip_wrapper modal is dismissible on outside click (Requirement 6.5)."""
    with patch('utils.components.st') as mock_st:
        mock_st.html = Mock()
        
        tooltip_wrapper(
            content="Content",
            tooltip_text="Help",
            icon="info-circle",
            position="top"
        )
        
        call_args = mock_st.html.call_args
        html_output = call_args[0][0] if call_args else ""
        
        # Verify modal has click handler for dismissal
        assert "onclick=" in html_output
        assert "closeTooltipModal" in html_output


def test_tooltip_wrapper_has_mobile_popover():
    """Test tooltip_wrapper uses popover/modal for mobile (Requirement 6.4)."""
    with patch('utils.components.st') as mock_st:
        mock_st.html = Mock()
        
        tooltip_wrapper(
            content="Content",
            tooltip_text="Help",
            icon="info-circle",
            position="top"
        )
        
        call_args = mock_st.html.call_args
        html_output = call_args[0][0] if call_args else ""
        
        # Verify modal structure exists
        assert "tooltip-modal" in html_output
        assert "tooltip-modal-content" in html_output


def test_tooltip_wrapper_custom_icon():
    """Test tooltip_wrapper accepts custom icon parameter."""
    with patch('utils.components.st') as mock_st:
        mock_st.html = Mock()
        
        tooltip_wrapper(
            content="Content",
            tooltip_text="Help",
            icon="question-circle",
            position="top"
        )
        
        call_args = mock_st.html.call_args
        html_output = call_args[0][0] if call_args else ""
        
        # Verify custom icon is used
        assert "fa-question-circle" in html_output


def test_tooltip_wrapper_default_parameters():
    """Test tooltip_wrapper works with default parameters."""
    with patch('utils.components.st') as mock_st:
        mock_st.html = Mock()
        
        # Call with only required parameters
        tooltip_wrapper(
            content="Content",
            tooltip_text="Help"
        )
        
        call_args = mock_st.html.call_args
        html_output = call_args[0][0] if call_args else ""
        
        # Verify defaults are applied
        assert "fa-info-circle" in html_output  # Default icon
        assert "Content" in html_output
        assert "Help" in html_output


def test_tooltip_wrapper_has_desktop_hover_styles():
    """Test tooltip_wrapper has CSS for desktop hover behavior."""
    with patch('utils.components.st') as mock_st:
        mock_st.html = Mock()
        
        tooltip_wrapper(
            content="Content",
            tooltip_text="Help",
            icon="info-circle",
            position="top"
        )
        
        call_args = mock_st.html.call_args
        html_output = call_args[0][0] if call_args else ""
        
        # Verify desktop hover styles exist
        assert ".tooltip-hover" in html_output
        assert "@media (min-width: 768px)" in html_output
        assert ":hover" in html_output


def test_tooltip_wrapper_has_mobile_only_icon():
    """Test tooltip_wrapper shows icon only on mobile."""
    with patch('utils.components.st') as mock_st:
        mock_st.html = Mock()
        
        tooltip_wrapper(
            content="Content",
            tooltip_text="Help",
            icon="info-circle",
            position="top"
        )
        
        call_args = mock_st.html.call_args
        html_output = call_args[0][0] if call_args else ""
        
        # Verify mobile-specific styles
        assert "@media (max-width: 767px)" in html_output
        assert "tooltip-icon-mobile" in html_output


def test_tooltip_wrapper_has_escape_key_handler():
    """Test tooltip_wrapper modal can be closed with Escape key."""
    with patch('utils.components.st') as mock_st:
        mock_st.html = Mock()
        
        tooltip_wrapper(
            content="Content",
            tooltip_text="Help",
            icon="info-circle",
            position="top"
        )
        
        call_args = mock_st.html.call_args
        html_output = call_args[0][0] if call_args else ""
        
        # Verify Escape key handler exists
        assert "event.key === 'Escape'" in html_output


def test_tooltip_wrapper_has_aria_labels():
    """Test tooltip_wrapper has proper ARIA labels for accessibility."""
    with patch('utils.components.st') as mock_st:
        mock_st.html = Mock()
        
        tooltip_wrapper(
            content="Content",
            tooltip_text="Help",
            icon="info-circle",
            position="top"
        )
        
        call_args = mock_st.html.call_args
        html_output = call_args[0][0] if call_args else ""
        
        # Verify ARIA labels exist
        assert "aria-label" in html_output


def test_tooltip_wrapper_unique_ids():
    """Test tooltip_wrapper generates unique IDs for multiple instances."""
    with patch('utils.components.st') as mock_st:
        mock_st.html = Mock()
        
        # Create two tooltips
        tooltip_wrapper(content="Content1", tooltip_text="Help1")
        first_call = mock_st.html.call_args[0][0]
        
        tooltip_wrapper(content="Content2", tooltip_text="Help2")
        second_call = mock_st.html.call_args[0][0]
        
        # Extract IDs from both calls
        import re
        first_ids = re.findall(r'tooltip-wrapper-(\w+)', first_call)
        second_ids = re.findall(r'tooltip-wrapper-(\w+)', second_call)
        
        # Verify IDs are different
        assert first_ids[0] != second_ids[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
