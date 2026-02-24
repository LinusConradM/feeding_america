"""
Property-based tests for state_lookup_component using Hypothesis.

This module validates Properties 10 and 13 from the executive-overview-redesign spec:
- Property 10: State Lookup Completeness
- Property 13: State Lookup Keyboard Accessibility

**Validates: Requirements 4.2, 4.5**
"""

import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import patch, MagicMock
import pandas as pd
from utils.data_loader import STATE_NAMES


# ============================================================================
# Test Strategies (Generators)
# ============================================================================

# All 51 state codes (50 states + DC)
ALL_STATE_CODES = list(STATE_NAMES.keys())

# Generate subsets of states for testing (at least 1 state, up to all 51)
state_subsets = st.lists(
    st.sampled_from(ALL_STATE_CODES),
    min_size=1,
    max_size=51,
    unique=True
)


# ============================================================================
# Helper Functions
# ============================================================================

def create_mock_year_data(state_codes: list[str]) -> pd.DataFrame:
    """Create a mock DataFrame with the given state codes."""
    return pd.DataFrame({
        'state': state_codes,
        'overall_food_insecurity_rate': [0.12] * len(state_codes)
    })


def extract_options_from_selectbox_call(mock_selectbox) -> list:
    """Extract the options list from a st.selectbox mock call."""
    if mock_selectbox.call_count == 0:
        return []
    
    # Get the call arguments
    # call_args is a tuple of (args, kwargs)
    call_args = mock_selectbox.call_args
    
    # Try to get from positional arguments first
    if call_args and call_args.args and len(call_args.args) > 1:
        return call_args.args[1]
    
    # Try to get from keyword arguments
    if call_args and call_args.kwargs and 'options' in call_args.kwargs:
        return call_args.kwargs['options']
    
    return []


def extract_format_func_from_selectbox_call(mock_selectbox):
    """Extract the format_func from a st.selectbox mock call."""
    if mock_selectbox.call_count == 0:
        return None
    
    # Get the call arguments
    call_args = mock_selectbox.call_args
    
    # Try to get from keyword arguments
    if call_args and call_args.kwargs:
        return call_args.kwargs.get('format_func', None)
    
    return None


def is_alphabetically_sorted(state_codes: list[str], state_names: dict[str, str]) -> bool:
    """Check if state codes are sorted alphabetically by their full names."""
    if not state_codes:
        return True
    
    # Get full names for the state codes
    full_names = [state_names.get(code, code) for code in state_codes]
    
    # Check if sorted
    return full_names == sorted(full_names)


# ============================================================================
# Property 10: State Lookup Completeness
# ============================================================================

@given(state_subset=state_subsets)
@settings(max_examples=20, deadline=None)
def test_property_10_state_lookup_completeness_with_full_dataset(state_subset: list[str]):
    """
    **Validates: Requirements 4.2**
    
    Property 10: State Lookup Completeness
    
    For any rendered dashboard, the State_Lookup dropdown SHALL contain 
    exactly 51 options (50 states + DC) in alphabetical order by state name.
    
    This test validates that when all 51 states are present in the data,
    the dropdown contains all 51 states in alphabetical order.
    """
    from utils.components import state_lookup_component
    
    # Only test when we have all 51 states
    if len(state_subset) != 51:
        return
    
    # Create mock year data with all states
    year_data = create_mock_year_data(state_subset)
    
    # Mock callback function
    mock_callback = MagicMock()
    
    # Mock streamlit selectbox
    with patch('streamlit.selectbox') as mock_selectbox:
        # Configure mock to return None (no selection)
        mock_selectbox.return_value = None
        
        # Call state_lookup_component
        state_lookup_component(
            year_data=year_data,
            state_names=STATE_NAMES,
            on_state_select=mock_callback
        )
        
        # Verify selectbox was called
        assert mock_selectbox.call_count == 1, \
            "state_lookup_component should call st.selectbox once"
        
        # Extract options from the selectbox call
        options = extract_options_from_selectbox_call(mock_selectbox)
        
        # Property 10 Assertion 1: Should have 52 options (None + 51 states)
        # The first option is None for "Select a state..."
        assert len(options) == 52, \
            f"State lookup should have 52 options (None + 51 states), but found {len(options)}"
        
        # Property 10 Assertion 2: First option should be None
        assert options[0] is None, \
            "First option should be None for 'Select a state...'"
        
        # Property 10 Assertion 3: Remaining 51 options should be state codes
        state_options = options[1:]
        assert len(state_options) == 51, \
            f"Should have exactly 51 state options, but found {len(state_options)}"
        
        # Property 10 Assertion 4: All 51 states should be present
        assert set(state_options) == set(ALL_STATE_CODES), \
            f"State options should contain all 51 states. Missing: {set(ALL_STATE_CODES) - set(state_options)}"
        
        # Property 10 Assertion 5: States should be in alphabetical order by full name
        assert is_alphabetically_sorted(state_options, STATE_NAMES), \
            "State options should be sorted alphabetically by state name"


@given(state_subset=state_subsets)
@settings(max_examples=20, deadline=None)
def test_property_10_state_lookup_alphabetical_ordering(state_subset: list[str]):
    """
    **Validates: Requirements 4.2**
    
    Property 10: State Lookup Completeness (Alphabetical Ordering)
    
    For any subset of states in the data, the State_Lookup dropdown SHALL 
    display states in alphabetical order by state name.
    """
    from utils.components import state_lookup_component
    
    # Create mock year data with subset of states
    year_data = create_mock_year_data(state_subset)
    
    # Mock callback function
    mock_callback = MagicMock()
    
    # Mock streamlit selectbox
    with patch('streamlit.selectbox') as mock_selectbox:
        # Configure mock to return None (no selection)
        mock_selectbox.return_value = None
        
        # Call state_lookup_component
        state_lookup_component(
            year_data=year_data,
            state_names=STATE_NAMES,
            on_state_select=mock_callback
        )
        
        # Extract options from the selectbox call
        options = extract_options_from_selectbox_call(mock_selectbox)
        
        # Remove the None option
        state_options = [opt for opt in options if opt is not None]
        
        # Property 10 Assertion: States should be in alphabetical order by full name
        assert is_alphabetically_sorted(state_options, STATE_NAMES), \
            f"State options should be sorted alphabetically by state name. " \
            f"Got: {[STATE_NAMES.get(code, code) for code in state_options]}"


def test_property_10_boundary_all_51_states():
    """
    Boundary test: Verify that with all 51 states, dropdown has exactly 51 options.
    """
    from utils.components import state_lookup_component
    
    # Create mock year data with all 51 states
    year_data = create_mock_year_data(ALL_STATE_CODES)
    
    # Mock callback function
    mock_callback = MagicMock()
    
    # Mock streamlit selectbox
    with patch('streamlit.selectbox') as mock_selectbox:
        mock_selectbox.return_value = None
        
        state_lookup_component(
            year_data=year_data,
            state_names=STATE_NAMES,
            on_state_select=mock_callback
        )
        
        options = extract_options_from_selectbox_call(mock_selectbox)
        state_options = [opt for opt in options if opt is not None]
        
        assert len(state_options) == 51, \
            f"Should have exactly 51 states, but found {len(state_options)}"


def test_property_10_alphabetical_order_verification():
    """
    Verify specific alphabetical ordering: Alabama should come before Wyoming.
    """
    from utils.components import state_lookup_component
    
    # Create mock year data with all states
    year_data = create_mock_year_data(ALL_STATE_CODES)
    
    # Mock callback function
    mock_callback = MagicMock()
    
    # Mock streamlit selectbox
    with patch('streamlit.selectbox') as mock_selectbox:
        mock_selectbox.return_value = None
        
        state_lookup_component(
            year_data=year_data,
            state_names=STATE_NAMES,
            on_state_select=mock_callback
        )
        
        options = extract_options_from_selectbox_call(mock_selectbox)
        state_options = [opt for opt in options if opt is not None]
        
        # Find positions of Alabama (AL) and Wyoming (WY)
        al_index = state_options.index("AL")
        wy_index = state_options.index("WY")
        
        assert al_index < wy_index, \
            "Alabama should come before Wyoming in alphabetical order"


# ============================================================================
# Property 13: State Lookup Keyboard Accessibility
# ============================================================================

@given(state_subset=state_subsets)
@settings(max_examples=20, deadline=None)
def test_property_13_state_lookup_keyboard_accessibility(state_subset: list[str]):
    """
    **Validates: Requirements 4.5**
    
    Property 13: State Lookup Keyboard Accessibility
    
    For any rendered State_Lookup component, it SHALL support keyboard 
    navigation (Tab, Arrow keys, Enter) and have proper ARIA attributes.
    
    Note: Streamlit's st.selectbox natively supports keyboard navigation
    (Tab, Arrow keys, Enter) and includes proper ARIA attributes. This test
    verifies that the component uses st.selectbox correctly.
    """
    from utils.components import state_lookup_component
    
    # Create mock year data
    year_data = create_mock_year_data(state_subset)
    
    # Mock callback function
    mock_callback = MagicMock()
    
    # Mock streamlit selectbox
    with patch('streamlit.selectbox') as mock_selectbox:
        mock_selectbox.return_value = None
        
        # Call state_lookup_component
        state_lookup_component(
            year_data=year_data,
            state_names=STATE_NAMES,
            on_state_select=mock_callback
        )
        
        # Property 13 Assertion 1: Component uses st.selectbox
        # (which natively supports keyboard navigation)
        assert mock_selectbox.call_count == 1, \
            "state_lookup_component should use st.selectbox for keyboard accessibility"
        
        # Property 13 Assertion 2: Verify help text is provided
        # (helps with accessibility by providing context)
        call_kwargs = mock_selectbox.call_args[1]
        assert 'help' in call_kwargs, \
            "state_lookup_component should provide help text for accessibility"
        
        help_text = call_kwargs['help']
        assert help_text is not None and len(help_text) > 0, \
            "Help text should be non-empty for accessibility"
        
        # Property 13 Assertion 3: Verify label is provided
        # (required for screen readers and ARIA attributes)
        call_args = mock_selectbox.call_args[0]
        label = call_args[0]
        assert label is not None and len(label) > 0, \
            "state_lookup_component should have a non-empty label for accessibility"
        
        # Property 13 Assertion 4: Verify unique key is provided
        # (ensures proper focus management)
        assert 'key' in call_kwargs, \
            "state_lookup_component should have a unique key for proper focus management"
        
        key = call_kwargs['key']
        assert key is not None and len(key) > 0, \
            "Key should be non-empty for proper component identification"


def test_property_13_selectbox_has_format_func():
    """
    Verify that format_func is provided for better accessibility
    (displays full state names instead of codes).
    """
    from utils.components import state_lookup_component
    
    # Create mock year data
    year_data = create_mock_year_data(["CA", "NY", "TX"])
    
    # Mock callback function
    mock_callback = MagicMock()
    
    # Mock streamlit selectbox
    with patch('streamlit.selectbox') as mock_selectbox:
        mock_selectbox.return_value = None
        
        state_lookup_component(
            year_data=year_data,
            state_names=STATE_NAMES,
            on_state_select=mock_callback
        )
        
        # Extract format_func
        format_func = extract_format_func_from_selectbox_call(mock_selectbox)
        
        assert format_func is not None, \
            "state_lookup_component should provide format_func for accessibility"
        
        # Test format_func with state codes
        assert format_func("CA") == "California", \
            "format_func should convert state codes to full names"
        assert format_func("NY") == "New York", \
            "format_func should convert state codes to full names"
        assert format_func(None) == "Select a state...", \
            "format_func should handle None option"


def test_property_13_keyboard_navigation_support():
    """
    Verify that the component configuration supports keyboard navigation.
    """
    from utils.components import state_lookup_component
    
    # Create mock year data with all states
    year_data = create_mock_year_data(ALL_STATE_CODES)
    
    # Mock callback function
    mock_callback = MagicMock()
    
    # Mock streamlit selectbox
    with patch('streamlit.selectbox') as mock_selectbox:
        mock_selectbox.return_value = None
        
        state_lookup_component(
            year_data=year_data,
            state_names=STATE_NAMES,
            on_state_select=mock_callback
        )
        
        # Verify that st.selectbox is used (which has native keyboard support)
        assert mock_selectbox.call_count == 1, \
            "Component should use st.selectbox which has native keyboard navigation"
        
        # Verify options are provided (required for keyboard navigation)
        options = extract_options_from_selectbox_call(mock_selectbox)
        assert len(options) > 0, \
            "Options must be provided for keyboard navigation to work"


# ============================================================================
# Additional Tests for Robustness
# ============================================================================

def test_state_lookup_with_empty_data():
    """
    Test that state_lookup_component handles empty data gracefully
    by falling back to all states.
    """
    from utils.components import state_lookup_component
    
    # Create empty DataFrame
    empty_data = pd.DataFrame()
    
    # Mock callback function
    mock_callback = MagicMock()
    
    # Mock streamlit selectbox
    with patch('streamlit.selectbox') as mock_selectbox:
        mock_selectbox.return_value = None
        
        state_lookup_component(
            year_data=empty_data,
            state_names=STATE_NAMES,
            on_state_select=mock_callback
        )
        
        # Should fall back to all states
        options = extract_options_from_selectbox_call(mock_selectbox)
        state_options = [opt for opt in options if opt is not None]
        
        assert len(state_options) == 51, \
            "With empty data, should fall back to all 51 states"


def test_state_lookup_callback_invoked_on_selection():
    """
    Test that the callback function is invoked when a state is selected.
    """
    from utils.components import state_lookup_component
    
    # Create mock year data
    year_data = create_mock_year_data(["CA", "NY", "TX"])
    
    # Mock callback function
    mock_callback = MagicMock()
    
    # Mock streamlit selectbox to return a selected state
    with patch('streamlit.selectbox') as mock_selectbox:
        mock_selectbox.return_value = "CA"
        
        result = state_lookup_component(
            year_data=year_data,
            state_names=STATE_NAMES,
            on_state_select=mock_callback
        )
        
        # Verify callback was invoked with the selected state
        mock_callback.assert_called_once_with("CA")
        
        # Verify return value is the selected state
        assert result == "CA", \
            "state_lookup_component should return the selected state"


def test_state_lookup_callback_not_invoked_when_none_selected():
    """
    Test that the callback function is NOT invoked when None is selected.
    """
    from utils.components import state_lookup_component
    
    # Create mock year data
    year_data = create_mock_year_data(["CA", "NY", "TX"])
    
    # Mock callback function
    mock_callback = MagicMock()
    
    # Mock streamlit selectbox to return None
    with patch('streamlit.selectbox') as mock_selectbox:
        mock_selectbox.return_value = None
        
        result = state_lookup_component(
            year_data=year_data,
            state_names=STATE_NAMES,
            on_state_select=mock_callback
        )
        
        # Verify callback was NOT invoked
        mock_callback.assert_not_called()
        
        # Verify return value is None
        assert result is None, \
            "state_lookup_component should return None when no state is selected"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
