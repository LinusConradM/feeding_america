"""
Unit tests for hero_section component.

Tests verify the hero_section component renders correctly with various inputs
and handles edge cases like missing previous_metric gracefully.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import streamlit as st


class MockSessionState:
    """Mock session state that behaves like Streamlit's session_state."""
    def __init__(self, initial_data=None):
        self._data = initial_data or {}
    
    def __contains__(self, key):
        return key in self._data
    
    def __getattr__(self, key):
        return self._data.get(key)
    
    def __setattr__(self, key, value):
        if key == '_data':
            super().__setattr__(key, value)
        else:
            self._data[key] = value
    
    def get(self, key, default=None):
        return self._data.get(key, default)


def test_hero_section_renders_with_valid_data():
    """Test hero section renders correctly with valid year and metrics."""
    from utils.components import hero_section
    
    # Mock streamlit functions
    mock_session = MockSessionState()
    with patch('streamlit.html') as mock_html, \
         patch('streamlit.session_state', mock_session), \
         patch('streamlit.button', return_value=False):
        
        hero_section(
            year=2023,
            primary_metric=0.123,
            previous_metric=0.118,
            context_summary="Food insecurity remains elevated",
            show_quick_tips=True
        )
        
        # Verify st.html was called
        assert mock_html.called
        # Check the first call (hero section)
        html_content = mock_html.call_args_list[0][0][0]
        
        # Verify year is displayed
        assert "2023" in html_content
        
        # Verify primary metric is displayed (12.3%)
        assert "12.3%" in html_content
        
        # Verify context summary is included
        assert "Food insecurity remains elevated" in html_content
        
        # Verify year-over-year comparison is calculated
        assert "up" in html_content or "down" in html_content
        assert "2022" in html_content  # Previous year


def test_hero_section_handles_missing_previous_year():
    """Test hero section handles None for previous_metric gracefully."""
    from utils.components import hero_section
    
    mock_session = MockSessionState()
    with patch('streamlit.html') as mock_html, \
         patch('streamlit.session_state', mock_session), \
         patch('streamlit.button', return_value=False):
        
        hero_section(
            year=2009,
            primary_metric=0.145,
            previous_metric=None,
            context_summary="First year in dataset",
            show_quick_tips=True
        )
        
        assert mock_html.called
        # Check the first call (hero section)
        html_content = mock_html.call_args_list[0][0][0]
        
        # Verify year is displayed
        assert "2009" in html_content
        
        # Verify primary metric is displayed (14.5%)
        assert "14.5%" in html_content
        
        # Verify context summary is included
        assert "First year in dataset" in html_content
        
        # Verify no comparison text when previous_metric is None
        # The comparison should not appear
        assert "2008" not in html_content


def test_hero_section_calculates_increase():
    """Test hero section correctly calculates and displays increase."""
    from utils.components import hero_section
    
    with patch('streamlit.html') as mock_html, \
         patch('streamlit.session_state', {}), \
         patch('streamlit.button', return_value=False):
        
        hero_section(
            year=2023,
            primary_metric=0.125,
            previous_metric=0.120,
            context_summary="Slight increase observed",
            show_quick_tips=False
        )
        
        assert mock_html.called
        html_content = mock_html.call_args[0][0]
        
        # Verify "up" direction is shown
        assert "up" in html_content
        
        # Verify percentage change (0.5%)
        assert "0.5%" in html_content


def test_hero_section_calculates_decrease():
    """Test hero section correctly calculates and displays decrease."""
    from utils.components import hero_section
    
    with patch('streamlit.html') as mock_html, \
         patch('streamlit.session_state', {}), \
         patch('streamlit.button', return_value=False):
        
        hero_section(
            year=2023,
            primary_metric=0.115,
            previous_metric=0.120,
            context_summary="Improvement noted",
            show_quick_tips=False
        )
        
        assert mock_html.called
        html_content = mock_html.call_args[0][0]
        
        # Verify "down" direction is shown
        assert "down" in html_content
        
        # Verify percentage change (0.5%)
        assert "0.5%" in html_content


def test_hero_section_quick_tips_disabled():
    """Test hero section respects show_quick_tips=False."""
    from utils.components import hero_section
    
    with patch('streamlit.html') as mock_html, \
         patch('streamlit.session_state', {}):
        
        hero_section(
            year=2023,
            primary_metric=0.123,
            previous_metric=0.118,
            context_summary="Test summary",
            show_quick_tips=False
        )
        
        # Should only call st.html once (for hero, not for quick tips)
        assert mock_html.call_count == 1


def test_hero_section_quick_tips_enabled():
    """Test hero section displays quick tips when enabled."""
    from utils.components import hero_section
    
    mock_session = MockSessionState({'quick_tips_dismissed': False})
    with patch('streamlit.html') as mock_html, \
         patch('streamlit.components.v1.html') as mock_components_html, \
         patch('streamlit.session_state', mock_session), \
         patch('streamlit.button', return_value=False):
        
        hero_section(
            year=2023,
            primary_metric=0.123,
            previous_metric=0.118,
            context_summary="Test summary",
            show_quick_tips=True
        )
        
        # Should call st.html once (hero) and st.components.v1.html once (quick tips)
        assert mock_html.call_count == 1
        assert mock_components_html.call_count == 1
        
        # Components HTML call should contain quick tips
        tips_html = mock_components_html.call_args[0][0]
        assert "Quick Tips" in tips_html
        assert "State Lookup" in tips_html


def test_hero_section_quick_tips_dismissed():
    """Test hero section hides quick tips when dismissed."""
    from utils.components import hero_section
    
    mock_session = MockSessionState({'quick_tips_dismissed': True})
    with patch('streamlit.html') as mock_html, \
         patch('streamlit.session_state', mock_session):
        
        hero_section(
            year=2023,
            primary_metric=0.123,
            previous_metric=0.118,
            context_summary="Test summary",
            show_quick_tips=True
        )
        
        # Should only call st.html once (quick tips dismissed)
        assert mock_html.call_count == 1


def test_hero_section_responsive_typography():
    """Test hero section uses responsive typography classes."""
    from utils.components import hero_section
    
    with patch('streamlit.html') as mock_html, \
         patch('streamlit.session_state', {}), \
         patch('streamlit.button', return_value=False):
        
        hero_section(
            year=2023,
            primary_metric=0.123,
            previous_metric=0.118,
            context_summary="Test",
            show_quick_tips=False
        )
        
        html_content = mock_html.call_args[0][0]
        
        # Verify responsive typography class is used
        assert "text-5xl" in html_content
        
        # Verify font styling
        assert "font-bold" in html_content
        assert "font-serif" in html_content


def test_hero_section_gradient_background():
    """Test hero section applies gradient background styling."""
    from utils.components import hero_section
    
    with patch('streamlit.html') as mock_html, \
         patch('streamlit.session_state', {}), \
         patch('streamlit.button', return_value=False):
        
        hero_section(
            year=2023,
            primary_metric=0.123,
            previous_metric=0.118,
            context_summary="Test",
            show_quick_tips=False
        )
        
        html_content = mock_html.call_args[0][0]
        
        # Verify gradient background is applied
        assert "linear-gradient" in html_content
        assert "#051C2C" in html_content  # Dark navy color
        assert "#0D1452" in html_content  # Portfolio blue


def test_hero_section_year_badge_styling():
    """Test hero section displays year with badge styling."""
    from utils.components import hero_section
    
    with patch('streamlit.html') as mock_html, \
         patch('streamlit.session_state', {}), \
         patch('streamlit.button', return_value=False):
        
        hero_section(
            year=2023,
            primary_metric=0.123,
            previous_metric=0.118,
            context_summary="Test",
            show_quick_tips=False
        )
        
        html_content = mock_html.call_args[0][0]
        
        # Verify badge styling elements
        assert "border-radius:9999px" in html_content  # Pill shape
        assert "fa-calendar-alt" in html_content  # Calendar icon
        assert "backdrop-filter:blur" in html_content  # Glass effect


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
