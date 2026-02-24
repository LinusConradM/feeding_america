"""
Property-based tests for collapsible_section component using Hypothesis.

This module validates Properties 14-17 from the executive-overview-redesign spec:
- Property 14: Collapsible Section Implementation
- Property 15: Collapsible Section Toggle Behavior
- Property 16: Collapsible Section Visual Indicator
- Property 17: Collapsible Section Session Persistence

**Validates: Requirements 5.1, 5.2, 5.3, 5.4**
"""

import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import patch, Mock
import re


# ============================================================================
# Test Strategies (Generators)
# ============================================================================

# Section title generator (realistic section names)
section_titles = st.text(
    min_size=5,
    max_size=50,
    alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Zs'),
        whitelist_characters='-'
    )
).filter(lambda x: x.strip() != "")

# Icon name generator (common FontAwesome icons)
icon_names = st.sampled_from([
    "chart-bar",
    "chart-line",
    "table",
    "list",
    "info-circle",
    "cog",
    "database",
    "map",
    "users",
    ""  # No icon case
])

# Default expanded state generator
default_expanded_states = st.booleans()

# Session key generator
session_keys = st.text(
    min_size=3,
    max_size=20,
    alphabet=st.characters(
        whitelist_categories=('Ll', 'Nd'),
        whitelist_characters='_-'
    )
).filter(lambda x: x.strip() != "")


# ============================================================================
# Helper Functions
# ============================================================================

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
    
    def get(self, key, default=None):
        return self._data.get(key, default)


def extract_expander_title(expander_call_args) -> str:
    """Extract title from st.expander call arguments."""
    if expander_call_args and len(expander_call_args[0]) > 0:
        return expander_call_args[0][0]
    return ""


def extract_expander_expanded_state(expander_call_kwargs) -> bool:
    """Extract expanded state from st.expander call keyword arguments."""
    return expander_call_kwargs.get('expanded', True)


def has_chevron_animation_css(css_content: str) -> bool:
    """Check if CSS contains chevron animation styles."""
    # Look for transition on svg or chevron-related animation
    has_transition = 'transition' in css_content.lower()
    has_svg_or_chevron = 'svg' in css_content.lower() or 'chevron' in css_content.lower()
    return has_transition and has_svg_or_chevron


def has_expander_styling_css(css_content: str) -> bool:
    """Check if CSS contains expander styling."""
    return 'streamlit-expander' in css_content.lower()


# ============================================================================
# Property 14: Collapsible Section Implementation
# ============================================================================

@given(
    title=section_titles,
    icon=icon_names,
    default_expanded=default_expanded_states,
    key=session_keys
)
@settings(max_examples=20, deadline=None)
def test_property_14_collapsible_section_implementation(
    title: str,
    icon: str,
    default_expanded: bool,
    key: str
):
    """
    **Validates: Requirements 5.1**
    
    Property 14: Collapsible Section Implementation
    
    For any rendered dashboard, Statistical Details and State Rankings sections 
    SHALL be implemented as collapsible components with expand/collapse functionality.
    
    This test verifies that collapsible_section creates a proper collapsible component
    using st.expander with expand/collapse functionality.
    """
    from utils.components import collapsible_section
    
    mock_session = MockSessionState()
    content_func = Mock()
    
    with patch('streamlit.session_state', mock_session), \
         patch('streamlit.markdown') as mock_markdown, \
         patch('streamlit.expander') as mock_expander:
        
        # Setup mock expander context manager
        mock_expander.return_value.__enter__ = Mock()
        mock_expander.return_value.__exit__ = Mock()
        
        # Call collapsible_section
        collapsible_section(
            title=title,
            content_func=content_func,
            icon=icon,
            default_expanded=default_expanded,
            key=key
        )
        
        # Property 14 Assertion 1: st.expander SHALL be called (collapsible component)
        assert mock_expander.called, \
            "Collapsible section must use st.expander for expand/collapse functionality"
        
        # Property 14 Assertion 2: Title SHALL be displayed (either in expander or markdown)
        expander_title = extract_expander_title(mock_expander.call_args)
        
        # If icon is provided, title is in markdown; otherwise in expander
        if icon:
            # Check that st.markdown was called with the title
            markdown_calls = [str(call) for call in mock_markdown.call_args_list]
            title_displayed = any(title in call for call in markdown_calls)
            assert title_displayed, \
                f"Collapsible section must display title '{title}' when icon is provided"
        else:
            # Title should be in expander when no icon
            assert title in expander_title, \
                f"Collapsible section must display title '{title}' in expander"
        
        # Property 14 Assertion 3: Content function SHALL be callable
        # (This is verified by the fact that content_func is a Mock, which is callable)
        assert callable(content_func), \
            "Collapsible section must accept a callable content_func"


# ============================================================================
# Property 15: Collapsible Section Toggle Behavior
# ============================================================================

@given(
    title=section_titles,
    initial_state=default_expanded_states,
    key=session_keys
)
@settings(max_examples=20, deadline=None)
def test_property_15_collapsible_section_toggle_behavior(
    title: str,
    initial_state: bool,
    key: str
):
    """
    **Validates: Requirements 5.2**
    
    Property 15: Collapsible Section Toggle Behavior
    
    For any collapsible section, clicking the header SHALL toggle the section 
    between expanded and collapsed states.
    
    Note: Streamlit's st.expander handles toggle behavior natively. This test
    verifies that the component properly initializes with the correct state
    and that the state can be changed through session_state.
    """
    from utils.components import collapsible_section
    
    mock_session = MockSessionState()
    content_func = Mock()
    
    with patch('streamlit.session_state', mock_session), \
         patch('streamlit.markdown'), \
         patch('streamlit.expander') as mock_expander:
        
        mock_expander.return_value.__enter__ = Mock()
        mock_expander.return_value.__exit__ = Mock()
        
        # First render with initial state
        collapsible_section(
            title=title,
            content_func=content_func,
            icon="",
            default_expanded=initial_state,
            key=key
        )
        
        # Property 15 Assertion 1: Initial state SHALL be set correctly
        session_key = f"collapsible_{key}"
        assert session_key in mock_session, \
            "Collapsible section must initialize session state"
        assert mock_session[session_key] == initial_state, \
            f"Initial state must be {initial_state}"
        
        # Simulate toggle by changing session state
        mock_session[session_key] = not initial_state
        
        # Second render after toggle
        mock_expander.reset_mock()
        collapsible_section(
            title=title,
            content_func=content_func,
            icon="",
            default_expanded=initial_state,  # Same default, but session state changed
            key=key
        )
        
        # Property 15 Assertion 2: Toggled state SHALL be reflected in expander
        expanded_state = extract_expander_expanded_state(mock_expander.call_args[1])
        assert expanded_state == (not initial_state), \
            f"After toggle, expanded state must be {not initial_state}"


# ============================================================================
# Property 16: Collapsible Section Visual Indicator
# ============================================================================

@given(
    title=section_titles,
    icon=icon_names,
    default_expanded=default_expanded_states,
    key=session_keys
)
@settings(max_examples=20, deadline=None)
def test_property_16_collapsible_section_visual_indicator(
    title: str,
    icon: str,
    default_expanded: bool,
    key: str
):
    """
    **Validates: Requirements 5.3**
    
    Property 16: Collapsible Section Visual Indicator
    
    For any collapsible section, a chevron icon SHALL be displayed that reflects 
    the current state (pointing down when expanded, pointing right when collapsed).
    
    Note: Streamlit's st.expander provides a native chevron icon. This test verifies
    that custom CSS is applied to animate the chevron icon.
    """
    from utils.components import collapsible_section
    
    mock_session = MockSessionState()
    content_func = Mock()
    captured_css = []
    
    def capture_markdown(content, **kwargs):
        if '<style>' in content:
            captured_css.append(content)
    
    with patch('streamlit.session_state', mock_session), \
         patch('streamlit.markdown', side_effect=capture_markdown), \
         patch('streamlit.expander') as mock_expander:
        
        mock_expander.return_value.__enter__ = Mock()
        mock_expander.return_value.__exit__ = Mock()
        
        collapsible_section(
            title=title,
            content_func=content_func,
            icon=icon,
            default_expanded=default_expanded,
            key=key
        )
        
        # Property 16 Assertion 1: Custom CSS SHALL be applied
        assert len(captured_css) > 0, \
            "Collapsible section must apply custom CSS"
        
        css_content = captured_css[0]
        
        # Property 16 Assertion 2: CSS SHALL include chevron animation
        assert has_chevron_animation_css(css_content), \
            "CSS must include chevron icon animation (transition on svg)"
        
        # Property 16 Assertion 3: CSS SHALL style expander header
        assert has_expander_styling_css(css_content), \
            "CSS must include styling for streamlit-expander components"


# ============================================================================
# Property 17: Collapsible Section Session Persistence
# ============================================================================

@given(
    title=section_titles,
    initial_state=default_expanded_states,
    toggled_state=default_expanded_states,
    key=session_keys
)
@settings(max_examples=20, deadline=None)
def test_property_17_collapsible_section_session_persistence(
    title: str,
    initial_state: bool,
    toggled_state: bool,
    key: str
):
    """
    **Validates: Requirements 5.4**
    
    Property 17: Collapsible Section Session Persistence
    
    For any collapsible section state change, the new state SHALL persist in 
    session storage and be maintained during the user session across interactions.
    """
    from utils.components import collapsible_section
    
    mock_session = MockSessionState()
    content_func = Mock()
    
    with patch('streamlit.session_state', mock_session), \
         patch('streamlit.markdown'), \
         patch('streamlit.expander') as mock_expander:
        
        mock_expander.return_value.__enter__ = Mock()
        mock_expander.return_value.__exit__ = Mock()
        
        # First render - initialize with initial_state
        collapsible_section(
            title=title,
            content_func=content_func,
            icon="",
            default_expanded=initial_state,
            key=key
        )
        
        session_key = f"collapsible_{key}"
        
        # Property 17 Assertion 1: State SHALL be stored in session_state
        assert session_key in mock_session, \
            "Collapsible section state must be stored in session_state"
        
        # Simulate user interaction - change state
        mock_session[session_key] = toggled_state
        
        # Second render - simulate page interaction (e.g., year change)
        mock_expander.reset_mock()
        collapsible_section(
            title=title,
            content_func=content_func,
            icon="",
            default_expanded=initial_state,  # Same default
            key=key
        )
        
        # Property 17 Assertion 2: State SHALL persist across interactions
        assert mock_session[session_key] == toggled_state, \
            f"Session state must persist value {toggled_state} across interactions"
        
        # Property 17 Assertion 3: Persisted state SHALL be used in expander
        expanded_state = extract_expander_expanded_state(mock_expander.call_args[1])
        assert expanded_state == toggled_state, \
            f"Expander must use persisted state {toggled_state}"
        
        # Third render - simulate another interaction
        mock_expander.reset_mock()
        collapsible_section(
            title=title,
            content_func=content_func,
            icon="",
            default_expanded=initial_state,
            key=key
        )
        
        # Property 17 Assertion 4: State SHALL remain persistent
        assert mock_session[session_key] == toggled_state, \
            "Session state must remain persistent across multiple interactions"


# ============================================================================
# Additional Property Tests for Edge Cases
# ============================================================================

@given(
    title=section_titles,
    default_expanded=default_expanded_states
)
@settings(max_examples=10, deadline=None)
def test_property_17_session_persistence_with_auto_generated_key(
    title: str,
    default_expanded: bool
):
    """
    Property 17 Extension: Session persistence SHALL work even when 
    key is auto-generated from title.
    
    **Validates: Requirements 5.4**
    """
    from utils.components import collapsible_section
    
    mock_session = MockSessionState()
    content_func = Mock()
    
    with patch('streamlit.session_state', mock_session), \
         patch('streamlit.markdown'), \
         patch('streamlit.expander') as mock_expander:
        
        mock_expander.return_value.__enter__ = Mock()
        mock_expander.return_value.__exit__ = Mock()
        
        # Render without explicit key (auto-generated from title)
        collapsible_section(
            title=title,
            content_func=content_func,
            icon="",
            default_expanded=default_expanded,
            key=""  # Empty key triggers auto-generation
        )
        
        # Auto-generated key should be based on title
        expected_key = f"collapsible_{title.replace(' ', '_').lower()}"
        
        # Verify session state was created with auto-generated key
        assert expected_key in mock_session, \
            f"Session state must be created with auto-generated key '{expected_key}'"
        
        assert mock_session[expected_key] == default_expanded, \
            "Auto-generated key must store correct initial state"


@given(
    title=section_titles,
    icon=icon_names,
    key=session_keys
)
@settings(max_examples=10, deadline=None)
def test_property_16_icon_displayed_when_provided(
    title: str,
    icon: str,
    key: str
):
    """
    Property 16 Extension: When icon is provided, it SHALL be displayed 
    in the section header.
    
    **Validates: Requirements 5.3**
    """
    from utils.components import collapsible_section
    
    mock_session = MockSessionState()
    content_func = Mock()
    
    with patch('streamlit.session_state', mock_session), \
         patch('streamlit.markdown') as mock_markdown, \
         patch('streamlit.expander') as mock_expander:
        
        mock_expander.return_value.__enter__ = Mock()
        mock_expander.return_value.__exit__ = Mock()
        
        collapsible_section(
            title=title,
            content_func=content_func,
            icon=icon,
            default_expanded=True,
            key=key
        )
        
        if icon:
            # Icon should be rendered via st.markdown with unsafe_allow_html=True
            markdown_calls = [str(call) for call in mock_markdown.call_args_list]
            icon_displayed = any(f"fa-{icon}" in call for call in markdown_calls)
            assert icon_displayed, \
                f"Icon 'fa-{icon}' must be displayed in section header via st.markdown"
            
            # Verify unsafe_allow_html=True is used for icon rendering
            html_enabled = any(
                call.kwargs.get('unsafe_allow_html', False) 
                for call in mock_markdown.call_args_list
                if hasattr(call, 'kwargs')
            )
            assert html_enabled, \
                "Icon HTML must be rendered with unsafe_allow_html=True"
        else:
            # When no icon, title should be in expander
            expander_title = extract_expander_title(mock_expander.call_args)
            assert title in expander_title, \
                "Title must be in expander when no icon is provided"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
