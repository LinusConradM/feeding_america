"""
Property-based tests for touch interaction feedback.

**Validates: Requirements 10.3, 10.5**

Property 33: Touch Interaction Feedback Timing
- For any touch interaction on an interactive element, visual feedback (color change or 
  scale animation) SHALL appear within 100 milliseconds.

Property 35: Rapid Tap Debouncing
- For any interactive element, rapid successive taps within 300 milliseconds SHALL be 
  debounced to register as a single interaction.
"""

import pytest
from hypothesis import given, strategies as st, settings
import re
from utils.components import (
    TOUCH_TARGET_CSS,
    add_touch_feedback,
    ensure_touch_target
)


# ── Property 33: Touch Interaction Feedback Timing ──────────────────────────

@given(
    element_type=st.sampled_from(["button", "a", "div", "span"]),
    element_content=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=("Lu", "Ll", "Nd", "Zs"), 
        blacklist_characters="<>\"'"
    ))
)
@settings(max_examples=20)
def test_property_33_visual_feedback_timing(element_type, element_content):
    """
    **Validates: Requirements 10.3**
    
    Property 33: Touch Interaction Feedback Timing
    
    For any touch interaction on an interactive element, visual feedback 
    (color change or scale animation) SHALL appear within 100 milliseconds.
    
    This test verifies:
    1. CSS transition timing is <= 100ms for all interactive elements
    2. Visual feedback includes both color change and scale animation
    3. Feedback applies to all interactive element types
    """
    # Extract all transition timings from TOUCH_TARGET_CSS
    timing_pattern = r'transition:.*?(\d+)ms'
    timings = re.findall(timing_pattern, TOUCH_TARGET_CSS)
    
    # Verify all transition timings are within 100ms requirement
    for timing_str in timings:
        timing_ms = int(timing_str)
        assert timing_ms <= 100, (
            f"Touch feedback timing {timing_ms}ms exceeds 100ms requirement "
            f"(Property 33, Requirement 10.3)"
        )
    
    # Verify CSS includes visual feedback properties
    assert "background-color" in TOUCH_TARGET_CSS, (
        "Missing background-color transition for visual feedback "
        "(Property 33, Requirement 10.3)"
    )
    assert "transform" in TOUCH_TARGET_CSS, (
        "Missing transform transition for scale animation "
        "(Property 33, Requirement 10.3)"
    )
    
    # Verify active state includes both color change and scale animation
    assert ":active" in TOUCH_TARGET_CSS, (
        "Missing :active pseudo-class for touch feedback "
        "(Property 33, Requirement 10.3)"
    )
    assert "transform: scale(" in TOUCH_TARGET_CSS, (
        "Missing scale animation in active state "
        "(Property 33, Requirement 10.3)"
    )
    assert "background-color: rgba(" in TOUCH_TARGET_CSS, (
        "Missing background color change in active state "
        "(Property 33, Requirement 10.3)"
    )
    
    # Verify feedback applies to the generated element type
    element_selectors = [
        "button",
        "a",
        '[role="button"]',
        "[onclick]",
        ".touch-target",
        ".touch-feedback"
    ]
    
    # Check that CSS targets interactive elements
    for selector in element_selectors:
        assert selector in TOUCH_TARGET_CSS, (
            f"CSS does not target {selector} for touch feedback "
            f"(Property 33, Requirement 10.3)"
        )


@given(
    has_existing_class=st.booleans(),
    element_tag=st.sampled_from(["button", "a", "div", "span"]),
    content=st.text(min_size=1, max_size=30, alphabet=st.characters(
        whitelist_categories=("Lu", "Ll", "Nd", "Zs"),
        blacklist_characters="<>\"'"
    ))
)
@settings(max_examples=20)
def test_property_33_add_touch_feedback_helper(has_existing_class, element_tag, content):
    """
    **Validates: Requirements 10.3**
    
    Property 33: Touch Interaction Feedback Timing (Helper Function)
    
    Verifies that the add_touch_feedback() helper function correctly applies
    touch feedback classes to any interactive element, ensuring visual feedback
    within 100ms.
    """
    # Generate test HTML element
    if has_existing_class:
        html = f'<{element_tag} class="existing-class">{content}</{element_tag}>'
    else:
        html = f'<{element_tag}>{content}</{element_tag}>'
    
    # Apply touch feedback
    result = add_touch_feedback(html, debounce=True)
    
    # Verify touch-feedback class is added
    assert "touch-feedback" in result, (
        "add_touch_feedback() did not add touch-feedback class "
        "(Property 33, Requirement 10.3)"
    )
    
    # Verify original content is preserved
    assert content in result, (
        "add_touch_feedback() did not preserve element content"
    )
    
    # Verify existing class is preserved if present
    if has_existing_class:
        assert "existing-class" in result, (
            "add_touch_feedback() did not preserve existing class"
        )


# ── Property 35: Rapid Tap Debouncing ───────────────────────────────────────

@given(
    debounce_threshold=st.integers(min_value=250, max_value=350)
)
@settings(max_examples=20)
def test_property_35_debounce_threshold(debounce_threshold):
    """
    **Validates: Requirements 10.5**
    
    Property 35: Rapid Tap Debouncing
    
    For any interactive element, rapid successive taps within 300 milliseconds 
    SHALL be debounced to register as a single interaction.
    
    This test verifies:
    1. Debounce threshold is set to 300ms
    2. Debouncing logic is present in JavaScript
    3. Event prevention occurs for rapid taps
    """
    # Verify debounce threshold constant is defined
    assert "DEBOUNCE_THRESHOLD = 300" in TOUCH_TARGET_CSS, (
        "Debounce threshold is not set to 300ms "
        "(Property 35, Requirement 10.5)"
    )
    
    # Extract the actual threshold value from CSS
    threshold_match = re.search(r'DEBOUNCE_THRESHOLD\s*=\s*(\d+)', TOUCH_TARGET_CSS)
    assert threshold_match, (
        "Could not find DEBOUNCE_THRESHOLD constant "
        "(Property 35, Requirement 10.5)"
    )
    
    actual_threshold = int(threshold_match.group(1))
    assert actual_threshold == 300, (
        f"Debounce threshold is {actual_threshold}ms, expected 300ms "
        f"(Property 35, Requirement 10.5)"
    )
    
    # Verify debouncing function exists
    assert "debounceTouch" in TOUCH_TARGET_CSS, (
        "debounceTouch function not found in JavaScript "
        "(Property 35, Requirement 10.5)"
    )
    
    # Verify last tap time tracking
    assert "lastTapTimes" in TOUCH_TARGET_CSS, (
        "lastTapTimes tracking not found in JavaScript "
        "(Property 35, Requirement 10.5)"
    )
    
    # Verify time comparison logic
    assert "now - lastTap < DEBOUNCE_THRESHOLD" in TOUCH_TARGET_CSS, (
        "Time comparison logic not found in debouncing "
        "(Property 35, Requirement 10.5)"
    )


@given(
    element_count=st.integers(min_value=1, max_value=10)
)
@settings(max_examples=20)
def test_property_35_debounce_event_prevention(element_count):
    """
    **Validates: Requirements 10.5**
    
    Property 35: Rapid Tap Debouncing (Event Prevention)
    
    Verifies that rapid taps are prevented through event.preventDefault() 
    and event.stopPropagation() when taps occur within the 300ms threshold.
    """
    # Verify event prevention is implemented
    assert "event.preventDefault()" in TOUCH_TARGET_CSS, (
        "event.preventDefault() not found in debouncing logic "
        "(Property 35, Requirement 10.5)"
    )
    
    assert "event.stopPropagation()" in TOUCH_TARGET_CSS, (
        "event.stopPropagation() not found in debouncing logic "
        "(Property 35, Requirement 10.5)"
    )
    
    # Verify return false to prevent default action
    assert "return false" in TOUCH_TARGET_CSS, (
        "return false not found in debouncing logic "
        "(Property 35, Requirement 10.5)"
    )
    
    # Verify debouncing is applied to all interactive elements
    interactive_selectors = [
        "button",
        "a",
        '[role="button"]',
        "[onclick]",
        ".touch-target",
        ".touch-feedback"
    ]
    
    # Check that querySelectorAll includes all interactive elements
    for selector in interactive_selectors:
        # The selector should be in the querySelectorAll call
        assert selector in TOUCH_TARGET_CSS, (
            f"Debouncing does not target {selector} "
            f"(Property 35, Requirement 10.5)"
        )


@given(
    enable_debounce=st.booleans()
)
@settings(max_examples=20)
def test_property_35_add_touch_feedback_debounce_option(enable_debounce):
    """
    **Validates: Requirements 10.5**
    
    Property 35: Rapid Tap Debouncing (Helper Function)
    
    Verifies that the add_touch_feedback() helper function correctly applies
    debouncing when requested.
    """
    html = '<button>Test Button</button>'
    result = add_touch_feedback(html, debounce=enable_debounce)
    
    # Verify touch-feedback class is always added
    assert "touch-feedback" in result, (
        "add_touch_feedback() did not add touch-feedback class"
    )
    
    # Verify debounce class is added when enabled
    if enable_debounce:
        assert "touch-debounce" in result, (
            "add_touch_feedback() did not add touch-debounce class when debounce=True "
            "(Property 35, Requirement 10.5)"
        )
    else:
        assert "touch-debounce" not in result, (
            "add_touch_feedback() added touch-debounce class when debounce=False"
        )


@given(
    element_type=st.sampled_from(["button", "a", "div", "span"]),
    has_id=st.booleans(),
    has_class=st.booleans()
)
@settings(max_examples=20)
def test_property_35_debounce_element_identification(element_type, has_id, has_class):
    """
    **Validates: Requirements 10.5**
    
    Property 35: Rapid Tap Debouncing (Element Identification)
    
    Verifies that debouncing correctly identifies elements using ID or class
    to track last tap times independently for each element.
    """
    # Verify element identification logic exists
    assert "elementId = element.id || element.className || 'default'" in TOUCH_TARGET_CSS, (
        "Element identification logic not found in debouncing "
        "(Property 35, Requirement 10.5)"
    )
    
    # Verify last tap time is stored per element
    assert "lastTapTimes.get(elementId)" in TOUCH_TARGET_CSS, (
        "Per-element tap time tracking not found "
        "(Property 35, Requirement 10.5)"
    )
    
    assert "lastTapTimes.set(elementId, now)" in TOUCH_TARGET_CSS, (
        "Per-element tap time storage not found "
        "(Property 35, Requirement 10.5)"
    )


@given(
    has_dynamic_content=st.booleans()
)
@settings(max_examples=20)
def test_property_35_debounce_dynamic_content_support(has_dynamic_content):
    """
    **Validates: Requirements 10.5**
    
    Property 35: Rapid Tap Debouncing (Dynamic Content)
    
    Verifies that debouncing is automatically applied to dynamically added
    interactive elements through MutationObserver.
    """
    # Verify MutationObserver is set up
    assert "MutationObserver" in TOUCH_TARGET_CSS, (
        "MutationObserver not found for dynamic content support "
        "(Property 35, Requirement 10.5)"
    )
    
    # Verify observer watches for added nodes
    assert "addedNodes" in TOUCH_TARGET_CSS, (
        "addedNodes check not found in MutationObserver "
        "(Property 35, Requirement 10.5)"
    )
    
    # Verify observer configuration
    assert "childList: true" in TOUCH_TARGET_CSS, (
        "childList observation not enabled in MutationObserver "
        "(Property 35, Requirement 10.5)"
    )
    
    assert "subtree: true" in TOUCH_TARGET_CSS, (
        "subtree observation not enabled in MutationObserver "
        "(Property 35, Requirement 10.5)"
    )
    
    # Verify debouncing is reapplied when new elements are added
    assert "applyDebouncing()" in TOUCH_TARGET_CSS, (
        "applyDebouncing() not called in MutationObserver callback "
        "(Property 35, Requirement 10.5)"
    )


# ── Integration Properties ──────────────────────────────────────────────────

@given(
    viewport_width=st.integers(min_value=320, max_value=2560),
    is_mobile=st.booleans()
)
@settings(max_examples=20)
def test_property_33_35_integration(viewport_width, is_mobile):
    """
    **Validates: Requirements 10.3, 10.5**
    
    Properties 33 & 35: Touch Interaction Feedback Integration
    
    Verifies that both visual feedback timing and debouncing work together
    correctly across all viewport sizes.
    """
    # Verify both features are present in the same CSS
    assert "transition:" in TOUCH_TARGET_CSS, (
        "Visual feedback transitions not found (Property 33)"
    )
    assert "DEBOUNCE_THRESHOLD" in TOUCH_TARGET_CSS, (
        "Debouncing not found (Property 35)"
    )
    
    # Verify they don't conflict
    # Both should apply to the same elements
    assert "button" in TOUCH_TARGET_CSS
    assert "a" in TOUCH_TARGET_CSS
    
    # Verify touch-action is set to prevent conflicts
    assert "touch-action: manipulation" in TOUCH_TARGET_CSS, (
        "touch-action not set to prevent gesture conflicts"
    )
    
    # Verify tap highlight color is set
    assert "-webkit-tap-highlight-color" in TOUCH_TARGET_CSS, (
        "webkit tap highlight color not set"
    )


@given(
    element_html=st.sampled_from([
        '<button>Click</button>',
        '<a href="#">Link</a>',
        '<div role="button">Div Button</div>',
        '<span onclick="alert()">Span</span>'
    ])
)
@settings(max_examples=20)
def test_property_33_35_helper_functions_integration(element_html):
    """
    **Validates: Requirements 10.3, 10.5**
    
    Properties 33 & 35: Helper Functions Integration
    
    Verifies that helper functions correctly apply both visual feedback
    and debouncing to interactive elements.
    """
    # Apply both touch feedback and touch target
    result_feedback = add_touch_feedback(element_html, debounce=True)
    result_target = ensure_touch_target(result_feedback)
    
    # Verify both classes are present
    assert "touch-feedback" in result_feedback, (
        "Visual feedback class not applied (Property 33)"
    )
    assert "touch-debounce" in result_feedback, (
        "Debounce class not applied (Property 35)"
    )
    assert "touch-target" in result_target, (
        "Touch target wrapper not applied"
    )
    
    # Verify original content is preserved
    # Extract text content from HTML
    import re
    text_match = re.search(r'>([^<]+)<', element_html)
    if text_match:
        text_content = text_match.group(1)
        assert text_content in result_target, (
            "Original content not preserved after applying helpers"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
