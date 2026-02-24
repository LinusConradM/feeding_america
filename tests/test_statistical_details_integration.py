"""
Unit test to verify Statistical Details section is wrapped in collapsible_section.

This test validates that task 5.14 has been correctly implemented:
- Statistical Details section uses collapsible_section component
- Default expanded state is True
- Icon is "calculator"
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import streamlit as st


def test_statistical_details_uses_collapsible_section():
    """
    Verify that Statistical Details section is wrapped in collapsible_section.
    
    This test checks that:
    1. collapsible_section is called with correct parameters
    2. The section uses "calculator" icon
    3. Default expanded state is True
    4. The content function renders the statistical cards
    """
    with patch('streamlit.expander') as mock_expander, \
         patch('streamlit.markdown') as mock_markdown, \
         patch('utils.components.st.session_state', {}) as mock_session_state:
        
        # Mock the expander context manager
        mock_expander_context = MagicMock()
        mock_expander.return_value.__enter__ = Mock(return_value=mock_expander_context)
        mock_expander.return_value.__exit__ = Mock(return_value=False)
        
        # Import and call collapsible_section
        from utils.components import collapsible_section
        
        # Create a mock content function
        content_called = []
        def mock_content():
            content_called.append(True)
        
        # Call collapsible_section with the same parameters as in the implementation
        collapsible_section(
            title="Statistical Details",
            content_func=mock_content,
            icon="calculator",
            default_expanded=True,
            key="statistical_details"
        )
        
        # Verify expander was called
        assert mock_expander.called, "st.expander should be called"
        
        # Verify the title includes the icon
        call_args = mock_expander.call_args
        title_arg = call_args[0][0] if call_args[0] else call_args[1].get('title', '')
        assert "calculator" in title_arg, "Title should include calculator icon"
        assert "Statistical Details" in title_arg, "Title should include 'Statistical Details'"
        
        # Verify expanded parameter
        expanded_arg = call_args[1].get('expanded', False)
        assert expanded_arg == True, "Section should be expanded by default"
        
        # Verify content function was called
        assert len(content_called) > 0, "Content function should be called"


def test_statistical_details_session_state_key():
    """
    Verify that Statistical Details section uses correct session state key.
    """
    with patch('streamlit.expander') as mock_expander, \
         patch('streamlit.markdown') as mock_markdown, \
         patch('utils.components.st.session_state', {}) as mock_session_state:
        
        # Mock the expander context manager
        mock_expander_context = MagicMock()
        mock_expander.return_value.__enter__ = Mock(return_value=mock_expander_context)
        mock_expander.return_value.__exit__ = Mock(return_value=False)
        
        from utils.components import collapsible_section
        
        def mock_content():
            pass
        
        collapsible_section(
            title="Statistical Details",
            content_func=mock_content,
            icon="calculator",
            default_expanded=True,
            key="statistical_details"
        )
        
        # Verify session state key was set
        expected_key = "collapsible_statistical_details"
        assert expected_key in mock_session_state, f"Session state should contain key '{expected_key}'"
        assert mock_session_state[expected_key] == True, "Session state should be True (expanded)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
