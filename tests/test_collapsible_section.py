"""
Unit tests for collapsible_section component.

Tests verify the collapsible_section component renders correctly with various inputs,
handles session state persistence, and applies custom styling.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
import streamlit as st


class MockSessionState:
    """Mock session state that behaves like Streamlit's session_state."""
    def __init__(self, initial_data=None):
        self._data = initial_data or {}
    
    def __contains__(self, key):
        return key in self._data
    
    def __getitem__(self, key):
        return self._data[key]
    
    def __setitem__(self, key, value):
        self._data[key] = value
    
    def __getattr__(self, key):
        if key == '_data':
            return super().__getattribute__(key)
        return self._data.get(key)
    
    def __setattr__(self, key, value):
        if key == '_data':
            super().__setattr__(key, value)
        else:
            self._data[key] = value
    
    def get(self, key, default=None):
        return self._data.get(key, default)


def test_collapsible_section_renders_with_title():
    """Test collapsible section renders with title."""
    from utils.components import collapsible_section
    
    mock_session = MockSessionState()
    content_func = Mock()
    
    with patch('streamlit.session_state', mock_session), \
         patch('streamlit.markdown') as mock_markdown, \
         patch('streamlit.expander') as mock_expander:
        
        # Setup mock expander context manager
        mock_expander.return_value.__enter__ = Mock()
        mock_expander.return_value.__exit__ = Mock()
        
        collapsible_section(
            title="Test Section",
            content_func=content_func,
            icon="",
            default_expanded=True,
            key="test"
        )
        
        # Verify expander was called with title
        assert mock_expander.called
        call_args = mock_expander.call_args
        assert "Test Section" in call_args[0][0]


def test_collapsible_section_renders_with_icon():
    """Test collapsible section renders with icon."""
    from utils.components import collapsible_section
    
    mock_session = MockSessionState()
    content_func = Mock()
    
    with patch('streamlit.session_state', mock_session), \
         patch('streamlit.markdown') as mock_markdown, \
         patch('streamlit.expander') as mock_expander:
        
        mock_expander.return_value.__enter__ = Mock()
        mock_expander.return_value.__exit__ = Mock()
        
        collapsible_section(
            title="Test Section",
            content_func=content_func,
            icon="chart-bar",
            default_expanded=True,
            key="test"
        )
        
        # Verify icon is rendered via st.markdown (not in expander title)
        markdown_calls = [str(call) for call in mock_markdown.call_args_list]
        icon_rendered = any("fa-chart-bar" in call for call in markdown_calls)
        assert icon_rendered, "Icon should be rendered via st.markdown"
        
        title_rendered = any("Test Section" in call for call in markdown_calls)
        assert title_rendered, "Title should be rendered via st.markdown when icon is present"



def test_collapsible_section_initializes_session_state():
    """Test collapsible section initializes session state with default_expanded."""
    from utils.components import collapsible_section
    
    mock_session = MockSessionState()
    content_func = Mock()
    
    with patch('streamlit.session_state', mock_session), \
         patch('streamlit.markdown'), \
         patch('streamlit.expander') as mock_expander:
        
        mock_expander.return_value.__enter__ = Mock()
        mock_expander.return_value.__exit__ = Mock()
        
        collapsible_section(
            title="Test Section",
            content_func=content_func,
            icon="",
            default_expanded=False,
            key="test_key"
        )
        
        # Verify session state was initialized
        assert "collapsible_test_key" in mock_session
        assert mock_session["collapsible_test_key"] == False


def test_collapsible_section_preserves_existing_session_state():
    """Test collapsible section preserves existing session state."""
    from utils.components import collapsible_section
    
    mock_session = MockSessionState({"collapsible_test_key": False})
    content_func = Mock()
    
    with patch('streamlit.session_state', mock_session), \
         patch('streamlit.markdown'), \
         patch('streamlit.expander') as mock_expander:
        
        mock_expander.return_value.__enter__ = Mock()
        mock_expander.return_value.__exit__ = Mock()
        
        collapsible_section(
            title="Test Section",
            content_func=content_func,
            icon="",
            default_expanded=True,  # Different from session state
            key="test_key"
        )
        
        # Verify session state was NOT overwritten
        assert mock_session["collapsible_test_key"] == False


def test_collapsible_section_calls_content_func():
    """Test collapsible section calls content_func when expanded."""
    from utils.components import collapsible_section
    
    mock_session = MockSessionState()
    content_func = Mock()
    
    with patch('streamlit.session_state', mock_session), \
         patch('streamlit.markdown'), \
         patch('streamlit.expander') as mock_expander:
        
        # Setup mock expander to execute the context
        def expander_context(*args, **kwargs):
            class ExpanderContext:
                def __enter__(self):
                    return self
                def __exit__(self, *args):
                    pass
            return ExpanderContext()
        
        mock_expander.side_effect = expander_context
        
        collapsible_section(
            title="Test Section",
            content_func=content_func,
            icon="",
            default_expanded=True,
            key="test"
        )
        
        # Verify content_func was called
        assert content_func.called


def test_collapsible_section_applies_custom_css():
    """Test collapsible section applies custom CSS for styling."""
    from utils.components import collapsible_section
    
    mock_session = MockSessionState()
    content_func = Mock()
    
    with patch('streamlit.session_state', mock_session), \
         patch('streamlit.markdown') as mock_markdown, \
         patch('streamlit.expander') as mock_expander:
        
        mock_expander.return_value.__enter__ = Mock()
        mock_expander.return_value.__exit__ = Mock()
        
        collapsible_section(
            title="Test Section",
            content_func=content_func,
            icon="",
            default_expanded=True,
            key="test"
        )
        
        # Verify CSS was applied via st.markdown
        assert mock_markdown.called
        css_call = mock_markdown.call_args_list[0]
        css_content = css_call[0][0]
        
        # Verify key CSS elements
        assert "<style>" in css_content
        assert "streamlit-expanderHeader" in css_content
        assert "transition" in css_content
        assert "chevron" in css_content.lower() or "svg" in css_content


def test_collapsible_section_generates_key_from_title():
    """Test collapsible section generates session key from title when key not provided."""
    from utils.components import collapsible_section
    
    mock_session = MockSessionState()
    content_func = Mock()
    
    with patch('streamlit.session_state', mock_session), \
         patch('streamlit.markdown'), \
         patch('streamlit.expander') as mock_expander:
        
        mock_expander.return_value.__enter__ = Mock()
        mock_expander.return_value.__exit__ = Mock()
        
        collapsible_section(
            title="My Test Section",
            content_func=content_func,
            icon="",
            default_expanded=True,
            key=""  # No key provided
        )
        
        # Verify session state key was generated from title
        assert "collapsible_my_test_section" in mock_session


def test_collapsible_section_expanded_state_from_session():
    """Test collapsible section uses expanded state from session_state."""
    from utils.components import collapsible_section
    
    mock_session = MockSessionState({"collapsible_test": False})
    content_func = Mock()
    
    with patch('streamlit.session_state', mock_session), \
         patch('streamlit.markdown'), \
         patch('streamlit.expander') as mock_expander:
        
        mock_expander.return_value.__enter__ = Mock()
        mock_expander.return_value.__exit__ = Mock()
        
        collapsible_section(
            title="Test Section",
            content_func=content_func,
            icon="",
            default_expanded=True,
            key="test"
        )
        
        # Verify expander was called with expanded=False from session state
        call_kwargs = mock_expander.call_args[1]
        assert call_kwargs['expanded'] == False


def test_collapsible_section_default_expanded_true():
    """Test collapsible section defaults to expanded when default_expanded=True."""
    from utils.components import collapsible_section
    
    mock_session = MockSessionState()
    content_func = Mock()
    
    with patch('streamlit.session_state', mock_session), \
         patch('streamlit.markdown'), \
         patch('streamlit.expander') as mock_expander:
        
        mock_expander.return_value.__enter__ = Mock()
        mock_expander.return_value.__exit__ = Mock()
        
        collapsible_section(
            title="Test Section",
            content_func=content_func,
            icon="",
            default_expanded=True,
            key="test"
        )
        
        # Verify session state was initialized to True
        assert mock_session["collapsible_test"] == True
        
        # Verify expander was called with expanded=True
        call_kwargs = mock_expander.call_args[1]
        assert call_kwargs['expanded'] == True


def test_collapsible_section_default_expanded_false():
    """Test collapsible section defaults to collapsed when default_expanded=False."""
    from utils.components import collapsible_section
    
    mock_session = MockSessionState()
    content_func = Mock()
    
    with patch('streamlit.session_state', mock_session), \
         patch('streamlit.markdown'), \
         patch('streamlit.expander') as mock_expander:
        
        mock_expander.return_value.__enter__ = Mock()
        mock_expander.return_value.__exit__ = Mock()
        
        collapsible_section(
            title="Test Section",
            content_func=content_func,
            icon="",
            default_expanded=False,
            key="test"
        )
        
        # Verify session state was initialized to False
        assert mock_session["collapsible_test"] == False
        
        # Verify expander was called with expanded=False
        call_kwargs = mock_expander.call_args[1]
        assert call_kwargs['expanded'] == False


def test_collapsible_section_icon_color():
    """Test collapsible section applies correct icon color."""
    from utils.components import collapsible_section
    
    mock_session = MockSessionState()
    content_func = Mock()
    
    with patch('streamlit.session_state', mock_session), \
         patch('streamlit.markdown') as mock_markdown, \
         patch('streamlit.expander') as mock_expander:
        
        mock_expander.return_value.__enter__ = Mock()
        mock_expander.return_value.__exit__ = Mock()
        
        collapsible_section(
            title="Test Section",
            content_func=content_func,
            icon="info-circle",
            default_expanded=True,
            key="test"
        )
        
        # Verify icon has correct color styling via st.markdown
        markdown_calls = [str(call) for call in mock_markdown.call_args_list]
        color_applied = any("#2251FF" in call for call in markdown_calls)
        assert color_applied, "Icon should have brand blue color #2251FF"



def test_collapsible_section_no_icon():
    """Test collapsible section works without icon."""
    from utils.components import collapsible_section
    
    mock_session = MockSessionState()
    content_func = Mock()
    
    with patch('streamlit.session_state', mock_session), \
         patch('streamlit.markdown'), \
         patch('streamlit.expander') as mock_expander:
        
        mock_expander.return_value.__enter__ = Mock()
        mock_expander.return_value.__exit__ = Mock()
        
        collapsible_section(
            title="Test Section",
            content_func=content_func,
            icon="",  # No icon
            default_expanded=True,
            key="test"
        )
        
        # Verify title doesn't contain icon markup
        call_args = mock_expander.call_args
        title_html = call_args[0][0]
        assert "fa-" not in title_html
        assert "Test Section" in title_html


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
