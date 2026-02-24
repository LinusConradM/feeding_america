"""
Property-based tests for quick_tips_callout component using Hypothesis.

This module validates Properties 23, 24, 52 from the executive-overview-redesign spec:
- Property 23: Quick Tips Content Range - Component contains 3-5 actionable tips
- Property 24: Quick Tips Dismissal Persistence - Dismissal stored in localStorage
- Property 52: Quick Tips Conditional Display - Display based on localStorage flag

**Validates: Requirements 7.2, 7.4, 7.5**
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import patch, MagicMock
import re


# ============================================================================
# Test Strategies (Generators)
# ============================================================================

# Generate lists of 3-5 tips (valid range per Property 23)
valid_tip_lists = st.lists(
    st.text(min_size=10, max_size=100, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs', 'Pc'),
        whitelist_characters='.,:-'
    )),
    min_size=3,
    max_size=5
)

# Generate lists outside valid range for boundary testing
invalid_tip_lists_too_few = st.lists(
    st.text(min_size=10, max_size=100),
    min_size=0,
    max_size=2
)

invalid_tip_lists_too_many = st.lists(
    st.text(min_size=10, max_size=100),
    min_size=6,
    max_size=10
)

# Boolean strategy for dismissible flag
dismissible_flags = st.booleans()


# ============================================================================
# Helper Functions
# ============================================================================

def extract_tips_from_html(html: str) -> list[str]:
    """Extract all tips from quick tips HTML."""
    # Look for <li> elements within the tips list
    tip_matches = re.findall(r'<li>(.*?)</li>', html, re.DOTALL)
    return [tip.strip() for tip in tip_matches]


def check_localStorage_operations(html: str) -> dict:
    """Check if localStorage operations are present in HTML."""
    return {
        'has_getItem': 'localStorage.getItem' in html,
        'has_setItem': 'localStorage.setItem' in html,
        'has_key': 'quick_tips_dismissed' in html,
        'has_dismiss_function': 'dismissQuickTips' in html
    }


def check_dismiss_button_present(html: str) -> bool:
    """Check if dismiss button is present in HTML."""
    return 'quick-tips-dismiss' in html and 'dismissQuickTips()' in html


def check_visibility_logic(html: str) -> bool:
    """Check if visibility logic based on localStorage is present."""
    # Should check localStorage and add 'visible' class if not dismissed
    return (
        'localStorage.getItem' in html and
        "classList.add('visible')" in html and
        "!dismissed" in html or "dismissed !== 'true'" in html
    )


# ============================================================================
# Property 23: Quick Tips Content Range
# ============================================================================

@given(tips=valid_tip_lists, dismissible=dismissible_flags)
@settings(max_examples=20, deadline=None)
def test_property_23_quick_tips_content_range(tips: list[str], dismissible: bool):
    """
    **Validates: Requirements 7.2**
    
    Property 23: Quick Tips Content Range
    
    For any rendered Quick_Tips component, it SHALL contain between 3 and 5 
    actionable tips.
    """
    from utils.components import quick_tips_callout
    
    # Mock st.components.v1.html to capture HTML output
    captured_html = []
    
    def mock_html(content, height=None):
        captured_html.append(content)
    
    with patch('streamlit.components.v1.html', side_effect=mock_html):
        # Call quick_tips_callout with generated tips
        quick_tips_callout(tips, dismissible=dismissible)
    
    # Verify HTML was generated
    assert len(captured_html) > 0, "Quick tips should generate HTML output"
    
    html_content = captured_html[0]
    
    # Extract tips from HTML
    extracted_tips = extract_tips_from_html(html_content)
    
    # Property 23 Assertion 1: Number of tips SHALL be between 3 and 5
    tip_count = len(extracted_tips)
    assert 3 <= tip_count <= 5, \
        f"Quick tips must contain 3-5 tips, but found {tip_count} tips"
    
    # Property 23 Assertion 2: All provided tips SHALL be present in HTML
    assert tip_count == len(tips), \
        f"Expected {len(tips)} tips in HTML, but found {tip_count}"
    
    # Property 23 Assertion 3: Each tip SHALL be rendered
    for i, tip in enumerate(tips):
        assert tip in html_content, \
            f"Tip {i+1} '{tip}' not found in rendered HTML"


# ============================================================================
# Property 24: Quick Tips Dismissal Persistence
# ============================================================================

@given(tips=valid_tip_lists)
@settings(max_examples=20, deadline=None)
def test_property_24_quick_tips_dismissal_persistence(tips: list[str]):
    """
    **Validates: Requirements 7.4, 7.5**
    
    Property 24: Quick Tips Dismissal Persistence
    
    For any Quick_Tips dismissal action, the dismissal preference SHALL be 
    stored in localStorage and the component SHALL not display on subsequent 
    page loads.
    """
    from utils.components import quick_tips_callout
    
    # Mock st.components.v1.html to capture HTML output
    captured_html = []
    
    def mock_html(content, height=None):
        captured_html.append(content)
    
    with patch('streamlit.components.v1.html', side_effect=mock_html):
        # Call quick_tips_callout with dismissible=True
        quick_tips_callout(tips, dismissible=True)
    
    # Verify HTML was generated
    assert len(captured_html) > 0, "Quick tips should generate HTML output"
    
    html_content = captured_html[0]
    
    # Property 24 Assertion 1: localStorage operations SHALL be present
    localStorage_ops = check_localStorage_operations(html_content)
    
    assert localStorage_ops['has_getItem'], \
        "Quick tips must check localStorage.getItem for dismissal state"
    
    assert localStorage_ops['has_setItem'], \
        "Quick tips must use localStorage.setItem to store dismissal preference"
    
    assert localStorage_ops['has_key'], \
        "Quick tips must use 'quick_tips_dismissed' key in localStorage"
    
    # Property 24 Assertion 2: Dismiss function SHALL be present
    assert localStorage_ops['has_dismiss_function'], \
        "Quick tips must have dismissQuickTips() function"
    
    # Property 24 Assertion 3: Dismiss button SHALL be present
    assert check_dismiss_button_present(html_content), \
        "Quick tips must have dismiss button that calls dismissQuickTips()"
    
    # Property 24 Assertion 4: Visibility logic SHALL check localStorage
    assert check_visibility_logic(html_content), \
        "Quick tips must check localStorage on load to determine visibility"


@given(tips=valid_tip_lists)
@settings(max_examples=10, deadline=None)
def test_property_24_non_dismissible_no_localStorage(tips: list[str]):
    """
    Property 24 Extension: When dismissible=False, localStorage operations 
    should not be needed (but may still be present for consistency).
    
    **Validates: Requirements 7.4**
    """
    from utils.components import quick_tips_callout
    
    captured_html = []
    
    def mock_html(content, height=None):
        captured_html.append(content)
    
    with patch('streamlit.components.v1.html', side_effect=mock_html):
        # Call quick_tips_callout with dismissible=False
        quick_tips_callout(tips, dismissible=False)
    
    html_content = captured_html[0]
    
    # When not dismissible, dismiss button should not be present
    # (localStorage may still be present for consistency, but dismiss button should not)
    has_dismiss_button = check_dismiss_button_present(html_content)
    
    # If dismissible=False, dismiss button should not be functional
    # (implementation may vary, but button should not be present or not functional)
    if not has_dismiss_button:
        # This is the expected behavior - no dismiss button when not dismissible
        assert True
    else:
        # If button is present, it should not be functional
        # Check that button is not rendered or is disabled
        assert '<button' not in html_content or 'dismissQuickTips()' not in html_content, \
            "Non-dismissible quick tips should not have functional dismiss button"


# ============================================================================
# Property 52: Quick Tips Conditional Display
# ============================================================================

@given(tips=valid_tip_lists)
@settings(max_examples=20, deadline=None)
def test_property_52_quick_tips_conditional_display(tips: list[str]):
    """
    **Validates: Requirements 7.5**
    
    Property 52: Quick Tips Conditional Display
    
    For any dashboard load where localStorage does not contain a Quick_Tips 
    dismissal flag, the Quick_Tips component SHALL be displayed in the Hero_Section.
    
    This test verifies that the component includes logic to check localStorage
    and display the component when the dismissal flag is not set.
    """
    from utils.components import quick_tips_callout
    
    captured_html = []
    
    def mock_html(content, height=None):
        captured_html.append(content)
    
    with patch('streamlit.components.v1.html', side_effect=mock_html):
        # Call quick_tips_callout with dismissible=True
        quick_tips_callout(tips, dismissible=True)
    
    html_content = captured_html[0]
    
    # Property 52 Assertion 1: Component SHALL check localStorage on load
    assert 'localStorage.getItem' in html_content, \
        "Quick tips must check localStorage on load"
    
    # Property 52 Assertion 2: Component SHALL display when flag is not set
    # Look for logic that adds 'visible' class when dismissed is not 'true'
    assert check_visibility_logic(html_content), \
        "Quick tips must add 'visible' class when localStorage flag is not set"
    
    # Property 52 Assertion 3: Component SHALL have initial display:none style
    # and become visible via JavaScript
    assert 'display: none' in html_content or 'display:none' in html_content, \
        "Quick tips banner should initially be hidden (display: none)"
    
    assert 'visible' in html_content, \
        "Quick tips should have 'visible' class mechanism for conditional display"
    
    # Property 52 Assertion 4: Visibility logic SHALL check for absence of flag
    # Should show when dismissed is null/undefined or not 'true'
    assert ('!dismissed' in html_content or "dismissed !== 'true'" in html_content), \
        "Quick tips must check if dismissal flag is not set or not 'true'"


# ============================================================================
# Boundary Condition Tests
# ============================================================================

@given(tips=st.lists(st.text(min_size=10, max_size=100), min_size=3, max_size=3))
@settings(max_examples=10, deadline=None)
def test_property_23_minimum_tips_boundary(tips: list[str]):
    """Test that exactly 3 tips (minimum) is valid."""
    from utils.components import quick_tips_callout
    
    captured_html = []
    
    def mock_html(content, height=None):
        captured_html.append(content)
    
    with patch('streamlit.components.v1.html', side_effect=mock_html):
        quick_tips_callout(tips, dismissible=True)
    
    html_content = captured_html[0]
    extracted_tips = extract_tips_from_html(html_content)
    
    assert len(extracted_tips) == 3, \
        f"Minimum boundary: Expected exactly 3 tips, found {len(extracted_tips)}"


@given(tips=st.lists(st.text(min_size=10, max_size=100), min_size=5, max_size=5))
@settings(max_examples=10, deadline=None)
def test_property_23_maximum_tips_boundary(tips: list[str]):
    """Test that exactly 5 tips (maximum) is valid."""
    from utils.components import quick_tips_callout
    
    captured_html = []
    
    def mock_html(content, height=None):
        captured_html.append(content)
    
    with patch('streamlit.components.v1.html', side_effect=mock_html):
        quick_tips_callout(tips, dismissible=True)
    
    html_content = captured_html[0]
    extracted_tips = extract_tips_from_html(html_content)
    
    assert len(extracted_tips) == 5, \
        f"Maximum boundary: Expected exactly 5 tips, found {len(extracted_tips)}"


# ============================================================================
# Integration Tests
# ============================================================================

@given(tips=valid_tip_lists, dismissible=dismissible_flags)
@settings(max_examples=10, deadline=None)
def test_quick_tips_complete_integration(tips: list[str], dismissible: bool):
    """
    Integration test verifying all three properties work together:
    - Property 23: 3-5 tips are rendered
    - Property 24: Dismissal persistence (if dismissible)
    - Property 52: Conditional display logic
    """
    from utils.components import quick_tips_callout
    
    captured_html = []
    
    def mock_html(content, height=None):
        captured_html.append(content)
    
    with patch('streamlit.components.v1.html', side_effect=mock_html):
        quick_tips_callout(tips, dismissible=dismissible)
    
    html_content = captured_html[0]
    
    # Verify Property 23: 3-5 tips
    extracted_tips = extract_tips_from_html(html_content)
    assert 3 <= len(extracted_tips) <= 5, \
        f"Integration: Expected 3-5 tips, found {len(extracted_tips)}"
    
    # Verify Property 24 & 52: localStorage logic (if dismissible)
    if dismissible:
        localStorage_ops = check_localStorage_operations(html_content)
        assert localStorage_ops['has_getItem'] and localStorage_ops['has_setItem'], \
            "Integration: Dismissible quick tips must have localStorage operations"
        
        assert check_visibility_logic(html_content), \
            "Integration: Dismissible quick tips must have conditional display logic"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
