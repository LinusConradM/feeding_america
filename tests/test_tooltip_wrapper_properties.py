"""
Property-based tests for tooltip_wrapper component using Hypothesis.

This module validates Properties 20, 21, 22, 31 from the executive-overview-redesign spec:
- Property 20: Desktop Tooltip Timing - Hover tooltip displays within 200ms
- Property 21: Mobile Tooltip Interaction - Tap icon displays tooltip
- Property 22: Tooltip Dismissal - Click/tap outside dismisses tooltip
- Property 31: Mobile Touch Target Sizing - Touch targets are 44x44px minimum

**Validates: Requirements 6.3, 6.4, 6.5, 10.1**
"""

import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import patch, MagicMock
import re


# ============================================================================
# Test Strategies (Generators)
# ============================================================================

# Content text generator (non-empty strings)
content_texts = st.text(
    min_size=5, 
    max_size=100, 
    alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'),
        whitelist_characters='.,!?-'
    )
)

# Tooltip text generator (help text)
tooltip_texts = st.text(
    min_size=10, 
    max_size=300, 
    alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'),
        whitelist_characters='.,!?-'
    )
)

# Icon generator (common FontAwesome icons)
icons = st.sampled_from([
    "info-circle",
    "question-circle",
    "lightbulb",
    "exclamation-circle",
    "help",
    "info"
])

# Position generator
positions = st.sampled_from(["top", "bottom", "left", "right"])

# Viewport width generator covering all breakpoints
viewport_widths = st.one_of(
    st.integers(min_value=320, max_value=767),   # mobile
    st.integers(min_value=768, max_value=1024),  # tablet
    st.integers(min_value=1025, max_value=2560)  # desktop
)


# ============================================================================
# Helper Functions
# ============================================================================

def extract_transition_delay_from_html(html: str) -> int | None:
    """Extract transition delay in milliseconds from tooltip CSS."""
    # Look for transition-delay: XXXms
    delay_match = re.search(r'transition-delay:\s*(\d+)ms', html)
    if delay_match:
        return int(delay_match.group(1))
    return None


def extract_touch_target_dimensions_from_html(html: str) -> tuple[int, int] | None:
    """Extract min-width and min-height from mobile icon touch target."""
    # Look for tooltip-icon-mobile class and its min-width/min-height
    icon_section = re.search(
        r'\.tooltip-icon-mobile\s*\{[^}]*\}',
        html,
        re.DOTALL
    )
    
    if not icon_section:
        return None
    
    icon_css = icon_section.group(0)
    
    # Extract min-width
    width_match = re.search(r'min-width:\s*(\d+)px', icon_css)
    # Extract min-height
    height_match = re.search(r'min-height:\s*(\d+)px', icon_css)
    
    if width_match and height_match:
        return (int(width_match.group(1)), int(height_match.group(1)))
    
    return None


def has_mobile_media_query(html: str) -> bool:
    """Check if HTML contains mobile-specific media query."""
    # Look for @media (max-width: 767px)
    return bool(re.search(r'@media\s*\([^)]*max-width:\s*767px[^)]*\)', html))


def has_desktop_media_query(html: str) -> bool:
    """Check if HTML contains desktop-specific media query."""
    # Look for @media (min-width: 768px)
    return bool(re.search(r'@media\s*\([^)]*min-width:\s*768px[^)]*\)', html))


def has_hover_interaction(html: str) -> bool:
    """Check if HTML contains hover interaction for desktop."""
    # Look for :hover pseudo-class
    return ':hover' in html


def has_click_dismissal(html: str) -> bool:
    """Check if HTML contains click/tap dismissal functionality."""
    # Look for onclick handlers and close functions
    return 'onclick=' in html and 'closeTooltipModal' in html


def has_escape_key_handler(html: str) -> bool:
    """Check if HTML contains Escape key handler for dismissal."""
    # Look for keydown event listener checking for Escape
    return "event.key === 'Escape'" in html or "event.keyCode === 27" in html


def extract_modal_structure(html: str) -> bool:
    """Check if HTML contains proper modal structure for mobile."""
    # Look for modal container, content, and close button
    has_modal = 'tooltip-modal' in html
    has_modal_content = 'tooltip-modal-content' in html
    has_close_button = 'tooltip-modal-close' in html
    
    return has_modal and has_modal_content and has_close_button


def has_aria_labels(html: str) -> bool:
    """Check if HTML contains ARIA labels for accessibility."""
    return 'aria-label' in html


def extract_close_button_dimensions(html: str) -> tuple[int, int] | None:
    """Extract min-width and min-height from modal close button."""
    # Look for tooltip-modal-close class and its dimensions
    close_section = re.search(
        r'\.tooltip-modal-close\s*\{[^}]*\}',
        html,
        re.DOTALL
    )
    
    if not close_section:
        return None
    
    close_css = close_section.group(0)
    
    # Extract min-width
    width_match = re.search(r'min-width:\s*(\d+)px', close_css)
    # Extract min-height
    height_match = re.search(r'min-height:\s*(\d+)px', close_css)
    
    if width_match and height_match:
        return (int(width_match.group(1)), int(height_match.group(1)))
    
    return None


# ============================================================================
# Property 20: Desktop Tooltip Timing
# ============================================================================

@given(
    content=content_texts,
    tooltip_text=tooltip_texts,
    icon=icons,
    position=positions
)
@settings(max_examples=20, deadline=None)
def test_property_20_desktop_tooltip_timing(
    content: str,
    tooltip_text: str,
    icon: str,
    position: str
):
    """
    **Validates: Requirements 6.3**
    
    Property 20: Desktop Tooltip Timing
    
    For any KPI_Card hover event on viewport width > 768px, the associated 
    tooltip SHALL display within 200 milliseconds.
    """
    from utils.components import tooltip_wrapper
    
    # Mock streamlit functions to capture HTML output
    captured_html = []
    
    def mock_html(content_html):
        captured_html.append(content_html)
    
    def mock_markdown(content_html, **kwargs):
        captured_html.append(content_html)
    
    with patch('streamlit.html', side_effect=mock_html), \
         patch('streamlit.markdown', side_effect=mock_markdown):
        
        # Call tooltip_wrapper with generated inputs
        tooltip_wrapper(
            content=content,
            tooltip_text=tooltip_text,
            icon=icon,
            position=position
        )
    
    # Verify HTML was generated
    assert len(captured_html) > 0, "Tooltip wrapper should generate HTML output"
    
    tooltip_html = captured_html[0]
    
    # Property 20 Assertion 1: Desktop hover interaction SHALL exist
    assert has_desktop_media_query(tooltip_html), \
        "Tooltip must have desktop-specific media query (@media min-width: 768px)"
    
    assert has_hover_interaction(tooltip_html), \
        "Tooltip must have hover interaction for desktop"
    
    # Property 20 Assertion 2: Transition delay SHALL be 200ms
    transition_delay = extract_transition_delay_from_html(tooltip_html)
    assert transition_delay is not None, \
        "Tooltip must have transition-delay specified"
    
    assert transition_delay == 200, \
        f"Desktop tooltip transition delay must be 200ms, but found {transition_delay}ms"
    
    # Property 20 Assertion 3: Tooltip should have opacity/visibility transitions
    assert 'opacity' in tooltip_html and 'visibility' in tooltip_html, \
        "Tooltip must use opacity and visibility for smooth transitions"


# ============================================================================
# Property 21: Mobile Tooltip Interaction
# ============================================================================

@given(
    content=content_texts,
    tooltip_text=tooltip_texts,
    icon=icons,
    position=positions
)
@settings(max_examples=20, deadline=None)
def test_property_21_mobile_tooltip_interaction(
    content: str,
    tooltip_text: str,
    icon: str,
    position: str
):
    """
    **Validates: Requirements 6.4**
    
    Property 21: Mobile Tooltip Interaction
    
    For any tooltip info icon tap on viewport width < 768px, the associated 
    tooltip SHALL display.
    """
    from utils.components import tooltip_wrapper
    
    # Mock streamlit functions to capture HTML output
    captured_html = []
    
    def mock_html(content_html):
        captured_html.append(content_html)
    
    def mock_markdown(content_html, **kwargs):
        captured_html.append(content_html)
    
    with patch('streamlit.html', side_effect=mock_html), \
         patch('streamlit.markdown', side_effect=mock_markdown):
        
        # Call tooltip_wrapper with generated inputs
        tooltip_wrapper(
            content=content,
            tooltip_text=tooltip_text,
            icon=icon,
            position=position
        )
    
    # Verify HTML was generated
    assert len(captured_html) > 0, "Tooltip wrapper should generate HTML output"
    
    tooltip_html = captured_html[0]
    
    # Property 21 Assertion 1: Mobile media query SHALL exist
    assert has_mobile_media_query(tooltip_html), \
        "Tooltip must have mobile-specific media query (@media max-width: 767px)"
    
    # Property 21 Assertion 2: Mobile icon button SHALL exist
    assert 'tooltip-icon-mobile' in tooltip_html, \
        "Tooltip must have mobile icon button for tap interaction"
    
    # Property 21 Assertion 3: Icon button SHALL have onclick handler
    assert 'onclick=' in tooltip_html and 'openTooltipModal' in tooltip_html, \
        "Mobile icon must have onclick handler to open tooltip modal"
    
    # Property 21 Assertion 4: Modal structure SHALL exist for displaying tooltip
    assert extract_modal_structure(tooltip_html), \
        "Tooltip must have proper modal structure (modal, content, close button) for mobile"
    
    # Property 21 Assertion 5: Tooltip text SHALL be present in modal
    assert tooltip_text in tooltip_html, \
        f"Tooltip text '{tooltip_text}' must be present in the HTML output"
    
    # Property 21 Assertion 6: Icon SHALL be displayed
    assert f'fa-{icon}' in tooltip_html, \
        f"Icon 'fa-{icon}' must be present in the HTML output"


# ============================================================================
# Property 22: Tooltip Dismissal
# ============================================================================

@given(
    content=content_texts,
    tooltip_text=tooltip_texts,
    icon=icons,
    position=positions
)
@settings(max_examples=20, deadline=None)
def test_property_22_tooltip_dismissal(
    content: str,
    tooltip_text: str,
    icon: str,
    position: str
):
    """
    **Validates: Requirements 6.5**
    
    Property 22: Tooltip Dismissal
    
    For any visible tooltip, clicking or tapping outside the tooltip area 
    SHALL dismiss it.
    """
    from utils.components import tooltip_wrapper
    
    # Mock streamlit functions to capture HTML output
    captured_html = []
    
    def mock_html(content_html):
        captured_html.append(content_html)
    
    def mock_markdown(content_html, **kwargs):
        captured_html.append(content_html)
    
    with patch('streamlit.html', side_effect=mock_html), \
         patch('streamlit.markdown', side_effect=mock_markdown):
        
        # Call tooltip_wrapper with generated inputs
        tooltip_wrapper(
            content=content,
            tooltip_text=tooltip_text,
            icon=icon,
            position=position
        )
    
    # Verify HTML was generated
    assert len(captured_html) > 0, "Tooltip wrapper should generate HTML output"
    
    tooltip_html = captured_html[0]
    
    # Property 22 Assertion 1: Click dismissal SHALL be implemented
    assert has_click_dismissal(tooltip_html), \
        "Tooltip must have click/tap dismissal functionality (onclick + closeTooltipModal)"
    
    # Property 22 Assertion 2: Modal backdrop SHALL have onclick handler
    # The modal container should have onclick to close when clicking outside
    assert 'tooltip-modal' in tooltip_html, \
        "Tooltip must have modal container for dismissal"
    
    # Property 22 Assertion 3: Close button SHALL exist
    assert 'tooltip-modal-close' in tooltip_html, \
        "Tooltip must have close button for explicit dismissal"
    
    # Property 22 Assertion 4: Escape key handler SHALL exist
    assert has_escape_key_handler(tooltip_html), \
        "Tooltip must support Escape key for dismissal"
    
    # Property 22 Assertion 5: stopPropagation SHALL prevent modal content clicks from closing
    assert 'stopPropagation' in tooltip_html, \
        "Tooltip modal content must use stopPropagation to prevent accidental dismissal"


# ============================================================================
# Property 31: Mobile Touch Target Sizing
# ============================================================================

@given(
    content=content_texts,
    tooltip_text=tooltip_texts,
    icon=icons,
    position=positions
)
@settings(max_examples=20, deadline=None)
def test_property_31_mobile_touch_target_sizing(
    content: str,
    tooltip_text: str,
    icon: str,
    position: str
):
    """
    **Validates: Requirements 10.1**
    
    Property 31: Mobile Touch Target Sizing
    
    For any interactive element on viewport width < 768px, the touch target 
    SHALL have minimum dimensions of 44x44 pixels.
    """
    from utils.components import tooltip_wrapper
    
    # Mock streamlit functions to capture HTML output
    captured_html = []
    
    def mock_html(content_html):
        captured_html.append(content_html)
    
    def mock_markdown(content_html, **kwargs):
        captured_html.append(content_html)
    
    with patch('streamlit.html', side_effect=mock_html), \
         patch('streamlit.markdown', side_effect=mock_markdown):
        
        # Call tooltip_wrapper with generated inputs
        tooltip_wrapper(
            content=content,
            tooltip_text=tooltip_text,
            icon=icon,
            position=position
        )
    
    # Verify HTML was generated
    assert len(captured_html) > 0, "Tooltip wrapper should generate HTML output"
    
    tooltip_html = captured_html[0]
    
    # Property 31 Assertion 1: Mobile icon touch target SHALL have 44x44px minimum
    icon_dimensions = extract_touch_target_dimensions_from_html(tooltip_html)
    assert icon_dimensions is not None, \
        "Mobile icon must have min-width and min-height specified"
    
    width, height = icon_dimensions
    assert width >= 44, \
        f"Mobile icon touch target width must be >= 44px, but found {width}px"
    
    assert height >= 44, \
        f"Mobile icon touch target height must be >= 44px, but found {height}px"
    
    # Property 31 Assertion 2: Modal close button SHALL have 44x44px minimum
    close_dimensions = extract_close_button_dimensions(tooltip_html)
    assert close_dimensions is not None, \
        "Modal close button must have min-width and min-height specified"
    
    close_width, close_height = close_dimensions
    assert close_width >= 44, \
        f"Modal close button width must be >= 44px, but found {close_width}px"
    
    assert close_height >= 44, \
        f"Modal close button height must be >= 44px, but found {close_height}px"


# ============================================================================
# Additional Property Tests for Robustness
# ============================================================================

@given(
    content=content_texts,
    tooltip_text=tooltip_texts,
    position=positions
)
@settings(max_examples=10, deadline=None)
def test_tooltip_content_and_text_present(
    content: str,
    tooltip_text: str,
    position: str
):
    """
    Verify that both content and tooltip text are present in the output.
    """
    from utils.components import tooltip_wrapper
    
    captured_html = []
    
    def mock_html(content_html):
        captured_html.append(content_html)
    
    def mock_markdown(content_html, **kwargs):
        captured_html.append(content_html)
    
    with patch('streamlit.html', side_effect=mock_html), \
         patch('streamlit.markdown', side_effect=mock_markdown):
        
        tooltip_wrapper(
            content=content,
            tooltip_text=tooltip_text,
            position=position
        )
    
    tooltip_html = captured_html[0]
    
    # Both content and tooltip text must be present
    assert content in tooltip_html, \
        f"Content '{content}' must be present in tooltip HTML"
    
    assert tooltip_text in tooltip_html, \
        f"Tooltip text '{tooltip_text}' must be present in tooltip HTML"


@given(
    content=content_texts,
    tooltip_text=tooltip_texts,
    icon=icons,
    position=positions
)
@settings(max_examples=10, deadline=None)
def test_tooltip_accessibility_features(
    content: str,
    tooltip_text: str,
    icon: str,
    position: str
):
    """
    Verify that tooltip has proper accessibility features (ARIA labels).
    """
    from utils.components import tooltip_wrapper
    
    captured_html = []
    
    def mock_html(content_html):
        captured_html.append(content_html)
    
    def mock_markdown(content_html, **kwargs):
        captured_html.append(content_html)
    
    with patch('streamlit.html', side_effect=mock_html), \
         patch('streamlit.markdown', side_effect=mock_markdown):
        
        tooltip_wrapper(
            content=content,
            tooltip_text=tooltip_text,
            icon=icon,
            position=position
        )
    
    tooltip_html = captured_html[0]
    
    # Must have ARIA labels for accessibility
    assert has_aria_labels(tooltip_html), \
        "Tooltip must have aria-label attributes for accessibility"


@given(
    content=content_texts,
    tooltip_text=tooltip_texts,
    position=positions
)
@settings(max_examples=10, deadline=None)
def test_tooltip_position_applied(
    content: str,
    tooltip_text: str,
    position: str
):
    """
    Verify that tooltip position parameter is applied correctly.
    """
    from utils.components import tooltip_wrapper
    
    captured_html = []
    
    def mock_html(content_html):
        captured_html.append(content_html)
    
    def mock_markdown(content_html, **kwargs):
        captured_html.append(content_html)
    
    with patch('streamlit.html', side_effect=mock_html), \
         patch('streamlit.markdown', side_effect=mock_markdown):
        
        tooltip_wrapper(
            content=content,
            tooltip_text=tooltip_text,
            position=position
        )
    
    tooltip_html = captured_html[0]
    
    # Position-specific CSS should be present
    # Each position has different transform and positioning
    position_indicators = {
        'top': 'bottom: 100%',
        'bottom': 'top: 100%',
        'left': 'right: 100%',
        'right': 'left: 100%'
    }
    
    expected_indicator = position_indicators[position]
    assert expected_indicator in tooltip_html, \
        f"Tooltip with position '{position}' must have CSS '{expected_indicator}'"


@given(
    content=content_texts,
    tooltip_text=tooltip_texts,
    icon=icons
)
@settings(max_examples=10, deadline=None)
def test_tooltip_unique_ids_generated(
    content: str,
    tooltip_text: str,
    icon: str
):
    """
    Verify that each tooltip instance generates unique IDs.
    """
    from utils.components import tooltip_wrapper
    
    captured_html_1 = []
    captured_html_2 = []
    
    def mock_html_1(content_html):
        captured_html_1.append(content_html)
    
    def mock_html_2(content_html):
        captured_html_2.append(content_html)
    
    # Create first tooltip
    with patch('streamlit.html', side_effect=mock_html_1), \
         patch('streamlit.markdown', side_effect=mock_html_1):
        tooltip_wrapper(content=content, tooltip_text=tooltip_text, icon=icon)
    
    # Create second tooltip with different content
    with patch('streamlit.html', side_effect=mock_html_2), \
         patch('streamlit.markdown', side_effect=mock_html_2):
        tooltip_wrapper(content=content + " different", tooltip_text=tooltip_text, icon=icon)
    
    html_1 = captured_html_1[0]
    html_2 = captured_html_2[0]
    
    # Extract tooltip IDs
    id_match_1 = re.search(r'tooltip-wrapper-(\w+)', html_1)
    id_match_2 = re.search(r'tooltip-wrapper-(\w+)', html_2)
    
    assert id_match_1 and id_match_2, \
        "Both tooltips must have unique IDs"
    
    id_1 = id_match_1.group(1)
    id_2 = id_match_2.group(1)
    
    assert id_1 != id_2, \
        f"Tooltip IDs must be unique, but both have ID: {id_1}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
