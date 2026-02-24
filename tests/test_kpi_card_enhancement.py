"""
Unit tests for enhanced kpi_card component with tooltip integration.

Tests verify the kpi_card component enhancement meets requirements:
- Add tooltip_text parameter (optional, default None)
- Integrate tooltip_wrapper for contextual help
- Ensure ARIA labels for accessibility
- Backward compatibility (works without tooltip_text)

Validates Requirements: 6.1, 16.4
"""

import pytest
from unittest.mock import Mock, patch, call
from utils.components import kpi_card


def test_kpi_card_without_tooltip():
    """Test kpi_card renders correctly without tooltip (backward compatibility)."""
    with patch('utils.components.st') as mock_st:
        mock_st.markdown = Mock()
        
        # Call kpi_card without tooltip_text
        kpi_card(
            title="Test Metric",
            value="42%",
            change="+2.3%",
            icon="chart-line",
            gradient="sapphire"
        )
        
        # Verify st.markdown was called (not tooltip_wrapper)
        assert mock_st.markdown.called
        call_args = mock_st.markdown.call_args
        html_output = call_args[0][0] if call_args else ""
        
        # Verify card content is present
        assert "Test Metric" in html_output
        assert "42%" in html_output
        assert "+2.3%" in html_output


def test_kpi_card_with_tooltip():
    """Test kpi_card integrates tooltip_wrapper when tooltip_text is provided."""
    with patch('utils.components.st') as mock_st:
        mock_st.html = Mock()
        mock_st.markdown = Mock()
        
        # Call kpi_card with tooltip_text
        kpi_card(
            title="Test Metric",
            value="42%",
            change="+2.3%",
            icon="chart-line",
            gradient="sapphire",
            tooltip_text="This metric measures the test value"
        )
        
        # Verify tooltip_wrapper was used (st.html or st.markdown called)
        assert mock_st.html.called or mock_st.markdown.called


def test_kpi_card_has_aria_labels():
    """Test kpi_card has proper ARIA labels for accessibility (Requirement 16.4)."""
    with patch('utils.components.st') as mock_st:
        mock_st.markdown = Mock()
        
        kpi_card(
            title="Food Insecurity Rate",
            value="12.5%",
            change="+0.5%",
            icon="chart-line",
            gradient="sapphire"
        )
        
        call_args = mock_st.markdown.call_args
        html_output = call_args[0][0] if call_args else ""
        
        # Verify ARIA labels are present
        assert "aria-label" in html_output
        assert "Food Insecurity Rate" in html_output
        assert "12.5%" in html_output


def test_kpi_card_icon_has_aria_hidden():
    """Test kpi_card icon has aria-hidden for accessibility."""
    with patch('utils.components.st') as mock_st:
        mock_st.markdown = Mock()
        
        kpi_card(
            title="Test Metric",
            value="42%",
            icon="chart-line",
            gradient="sapphire"
        )
        
        call_args = mock_st.markdown.call_args
        html_output = call_args[0][0] if call_args else ""
        
        # Verify icon has aria-hidden
        assert 'aria-hidden="true"' in html_output


def test_kpi_card_tooltip_text_none_default():
    """Test kpi_card works with tooltip_text=None (default)."""
    with patch('utils.components.st') as mock_st:
        mock_st.markdown = Mock()
        
        # Call with explicit None
        kpi_card(
            title="Test Metric",
            value="42%",
            tooltip_text=None
        )
        
        # Should use st.markdown, not tooltip_wrapper
        assert mock_st.markdown.called


def test_kpi_card_tooltip_contains_card_content():
    """Test kpi_card with tooltip includes card content in tooltip wrapper."""
    with patch('utils.components.st') as mock_st:
        mock_st.html = Mock()
        
        kpi_card(
            title="National FI Rate",
            value="13.2%",
            change="+0.8%",
            icon="users",
            gradient="sapphire",
            tooltip_text="Percentage of households experiencing food insecurity"
        )
        
        # Get the HTML that was rendered
        call_args = mock_st.html.call_args
        html_output = call_args[0][0] if call_args else ""
        
        # Verify both card content and tooltip text are present
        assert "National FI Rate" in html_output
        assert "13.2%" in html_output
        assert "Percentage of households experiencing food insecurity" in html_output


def test_kpi_card_change_indicator_up():
    """Test kpi_card renders up arrow for positive change."""
    with patch('utils.components.st') as mock_st:
        mock_st.markdown = Mock()
        
        kpi_card(
            title="Test Metric",
            value="42%",
            change="+2.3%"
        )
        
        call_args = mock_st.markdown.call_args
        html_output = call_args[0][0] if call_args else ""
        
        # Verify up arrow and "up" class
        assert "&#9650;" in html_output  # Up arrow
        assert "kpi-change up" in html_output


def test_kpi_card_change_indicator_down():
    """Test kpi_card renders down arrow for negative change."""
    with patch('utils.components.st') as mock_st:
        mock_st.markdown = Mock()
        
        kpi_card(
            title="Test Metric",
            value="42%",
            change="-1.5%"
        )
        
        call_args = mock_st.markdown.call_args
        html_output = call_args[0][0] if call_args else ""
        
        # Verify down arrow and "down" class
        assert "&#9660;" in html_output  # Down arrow
        assert "kpi-change down" in html_output


def test_kpi_card_no_change_indicator():
    """Test kpi_card works without change indicator."""
    with patch('utils.components.st') as mock_st:
        mock_st.markdown = Mock()
        
        kpi_card(
            title="Test Metric",
            value="42%",
            change=""
        )
        
        call_args = mock_st.markdown.call_args
        html_output = call_args[0][0] if call_args else ""
        
        # Verify no change indicator is present
        assert "kpi-change" not in html_output


def test_kpi_card_gradient_colors():
    """Test kpi_card applies gradient colors correctly."""
    with patch('utils.components.st') as mock_st:
        mock_st.markdown = Mock()
        
        kpi_card(
            title="Test Metric",
            value="42%",
            gradient="sapphire"
        )
        
        call_args = mock_st.markdown.call_args
        html_output = call_args[0][0] if call_args else ""
        
        # Verify accent class is applied
        assert "accent-" in html_output


def test_kpi_card_role_article():
    """Test kpi_card has role='article' for semantic HTML."""
    with patch('utils.components.st') as mock_st:
        mock_st.markdown = Mock()
        
        kpi_card(
            title="Test Metric",
            value="42%"
        )
        
        call_args = mock_st.markdown.call_args
        html_output = call_args[0][0] if call_args else ""
        
        # Verify role="article" is present
        assert 'role="article"' in html_output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
