"""
Property-based tests for kpi_card tooltip functionality using Hypothesis.

This module validates Property 18 from the executive-overview-redesign spec:
- Property 18: KPI Card Tooltip Presence - When tooltip_text is provided, 
  tooltip_wrapper is used; when None, standard rendering

**Validates: Requirements 6.1**
"""

import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import patch, MagicMock, call
import re


# ============================================================================
# Test Strategies (Generators)
# ============================================================================

# KPI card title generator
kpi_titles = st.text(
    min_size=5,
    max_size=50,
    alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'),
        whitelist_characters='.,!?-%'
    )
)

# KPI value generator (formatted strings)
kpi_values = st.one_of(
    # Percentage values
    st.builds(
        lambda x: f"{x:.1f}%",
        st.floats(min_value=0.0, max_value=100.0, allow_nan=False)
    ),
    # Dollar values
    st.builds(
        lambda x: f"${x:,.2f}",
        st.floats(min_value=0.0, max_value=1000000.0, allow_nan=False)
    ),
    # Integer values with commas
    st.builds(
        lambda x: f"{x:,}",
        st.integers(min_value=0, max_value=10000000)
    )
)

# Change indicator generator
change_indicators = st.one_of(
    st.just(""),  # No change
    st.builds(
        lambda x: f"+{x:.1f}%",
        st.floats(min_value=0.1, max_value=50.0, allow_nan=False)
    ),
    st.builds(
        lambda x: f"-{x:.1f}%",
        st.floats(min_value=0.1, max_value=50.0, allow_nan=False)
    ),
    st.builds(
        lambda x: f"↑ {x:.1f}%",
        st.floats(min_value=0.1, max_value=50.0, allow_nan=False)
    ),
    st.builds(
        lambda x: f"↓ {x:.1f}%",
        st.floats(min_value=0.1, max_value=50.0, allow_nan=False)
    )
)

# Icon generator (common FontAwesome icons for KPI cards)
kpi_icons = st.sampled_from([
    "chart-line",
    "users",
    "child",
    "dollar-sign",
    "percentage",
    "coins",
    "briefcase",
    "chart-bar",
    "arrow-trend-up",
    "wallet"
])

# Gradient/accent generator
gradients = st.sampled_from([
    "sapphire",
    "emerald",
    "amber",
    "rose",
    "violet",
    "cyan"
])

# Tooltip text generator (help text explaining metrics)
tooltip_texts = st.text(
    min_size=20,
    max_size=200,
    alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'),
        whitelist_characters='.,!?-%'
    )
)

# Optional tooltip text (None or text)
optional_tooltip_texts = st.one_of(
    st.none(),
    tooltip_texts
)


# ============================================================================
# Helper Functions
# ============================================================================

def extract_kpi_card_html(html: str) -> str:
    """Extract the KPI card HTML structure."""
    # Look for kpi-card div
    match = re.search(r'<div class="kpi-card[^"]*"[^>]*>.*?</div>\s*</div>\s*</div>', html, re.DOTALL)
    if match:
        return match.group(0)
    return html


def has_tooltip_wrapper_structure(html: str) -> bool:
    """Check if HTML contains tooltip wrapper structure."""
    # Tooltip wrapper has specific classes and structure
    has_wrapper = 'tooltip-wrapper-container' in html
    has_hover = 'tooltip-hover' in html
    has_mobile_icon = 'tooltip-icon-mobile' in html
    has_modal = 'tooltip-modal' in html
    
    return has_wrapper and has_hover and has_mobile_icon and has_modal


def has_standalone_kpi_card(html: str) -> bool:
    """Check if HTML contains standalone KPI card without tooltip wrapper."""
    # Standalone card should have kpi-card class but no tooltip wrapper
    has_kpi_card = 'kpi-card' in html
    has_no_wrapper = 'tooltip-wrapper-container' not in html
    
    return has_kpi_card and has_no_wrapper


def extract_tooltip_text_from_html(html: str) -> str | None:
    """Extract tooltip text from HTML."""
    # Look for tooltip text in tooltip-hover div
    hover_match = re.search(r'<div class="tooltip-hover"[^>]*>(.*?)</div>', html, re.DOTALL)
    if hover_match:
        return hover_match.group(1).strip()
    
    # Also check modal body
    modal_match = re.search(r'<div class="tooltip-modal-body"[^>]*>(.*?)</div>', html, re.DOTALL)
    if modal_match:
        return modal_match.group(1).strip()
    
    return None


def extract_kpi_card_content(html: str) -> dict:
    """Extract KPI card content (title, value, change)."""
    content = {}
    
    # Extract title
    title_match = re.search(r'<div class="kpi-label"[^>]*>.*?</i>(.*?)</div>', html, re.DOTALL)
    if title_match:
        content['title'] = title_match.group(1).strip()
    
    # Extract value
    value_match = re.search(r'<div class="kpi-value"[^>]*>(.*?)</div>', html, re.DOTALL)
    if value_match:
        content['value'] = value_match.group(1).strip()
    
    # Extract change (if present)
    change_match = re.search(r'<div class="kpi-change[^"]*"[^>]*>.*?</div>', html, re.DOTALL)
    if change_match:
        content['has_change'] = True
    else:
        content['has_change'] = False
    
    return content


def has_aria_label(html: str) -> bool:
    """Check if HTML contains aria-label for accessibility."""
    return 'aria-label=' in html


# ============================================================================
# Property 18: KPI Card Tooltip Presence
# ============================================================================

@given(
    title=kpi_titles,
    value=kpi_values,
    change=change_indicators,
    icon=kpi_icons,
    gradient=gradients,
    tooltip_text=optional_tooltip_texts
)
@settings(max_examples=20, deadline=None)
def test_property_18_kpi_card_tooltip_presence(
    title: str,
    value: str,
    change: str,
    icon: str,
    gradient: str,
    tooltip_text: str | None
):
    """
    **Validates: Requirements 6.1**
    
    Property 18: KPI Card Tooltip Presence
    
    For any KPI_Card, when tooltip_text is provided, tooltip_wrapper SHALL be 
    used; when tooltip_text is None, standard rendering SHALL be used.
    """
    from utils.components import kpi_card
    
    # Mock streamlit functions to capture output
    captured_html = []
    captured_markdown = []
    
    def mock_html(content_html):
        captured_html.append(content_html)
    
    def mock_markdown(content_html, **kwargs):
        captured_markdown.append(content_html)
    
    with patch('streamlit.html', side_effect=mock_html), \
         patch('streamlit.markdown', side_effect=mock_markdown), \
         patch('utils.components.st.html', side_effect=mock_html), \
         patch('utils.components.st.markdown', side_effect=mock_markdown):
        
        # Call kpi_card with generated inputs
        kpi_card(
            title=title,
            value=value,
            change=change,
            icon=icon,
            gradient=gradient,
            tooltip_text=tooltip_text
        )
    
    # Combine all captured output
    all_output = captured_html + captured_markdown
    
    # Verify some output was generated
    assert len(all_output) > 0, "KPI card should generate HTML output"
    
    # Combine all HTML for analysis
    combined_html = '\n'.join(all_output)
    
    # Property 18 Assertion 1: When tooltip_text is provided, tooltip_wrapper SHALL be used
    if tooltip_text is not None:
        assert has_tooltip_wrapper_structure(combined_html), \
            "When tooltip_text is provided, KPI card must use tooltip_wrapper structure"
        
        # Property 18 Assertion 2: Tooltip text SHALL be present in the output
        extracted_tooltip = extract_tooltip_text_from_html(combined_html)
        assert extracted_tooltip is not None, \
            "Tooltip text must be present in HTML when tooltip_text is provided"
        
        assert tooltip_text in combined_html, \
            f"Provided tooltip_text '{tooltip_text}' must appear in the HTML output"
    
    # Property 18 Assertion 3: When tooltip_text is None, standard rendering SHALL be used
    else:
        # When tooltip_text is None, should use st.markdown directly without tooltip wrapper
        # The output should contain kpi-card but not tooltip wrapper structure
        assert 'kpi-card' in combined_html, \
            "KPI card HTML must be present in output"
        
        # Should NOT have tooltip wrapper when tooltip_text is None
        assert not has_tooltip_wrapper_structure(combined_html), \
            "When tooltip_text is None, KPI card must NOT use tooltip_wrapper structure"
    
    # Property 18 Assertion 4: KPI card content SHALL always be present
    card_content = extract_kpi_card_content(combined_html)
    
    assert 'title' in card_content, \
        "KPI card must contain title"
    
    assert 'value' in card_content, \
        "KPI card must contain value"
    
    # Verify title and value match inputs (allowing for HTML encoding)
    assert title in combined_html, \
        f"KPI card title '{title}' must be present in output"
    
    assert value in combined_html, \
        f"KPI card value '{value}' must be present in output"
    
    # Property 18 Assertion 5: Icon SHALL be present
    assert f'fa-{icon}' in combined_html, \
        f"KPI card icon 'fa-{icon}' must be present in output"
    
    # Property 18 Assertion 6: Accessibility - aria-label SHALL be present
    assert has_aria_label(combined_html), \
        "KPI card must have aria-label for accessibility"


# ============================================================================
# Additional Property Tests for Robustness
# ============================================================================

@given(
    title=kpi_titles,
    value=kpi_values,
    tooltip_text=tooltip_texts
)
@settings(max_examples=10, deadline=None)
def test_kpi_card_with_tooltip_contains_all_elements(
    title: str,
    value: str,
    tooltip_text: str
):
    """
    Verify that KPI card with tooltip contains both card content and tooltip.
    """
    from utils.components import kpi_card
    
    captured_html = []
    captured_markdown = []
    
    def mock_html(content_html):
        captured_html.append(content_html)
    
    def mock_markdown(content_html, **kwargs):
        captured_markdown.append(content_html)
    
    with patch('streamlit.html', side_effect=mock_html), \
         patch('streamlit.markdown', side_effect=mock_markdown), \
         patch('utils.components.st.html', side_effect=mock_html), \
         patch('utils.components.st.markdown', side_effect=mock_markdown):
        
        kpi_card(
            title=title,
            value=value,
            tooltip_text=tooltip_text
        )
    
    combined_html = '\n'.join(captured_html + captured_markdown)
    
    # Must contain KPI card structure
    assert 'kpi-card' in combined_html, \
        "Output must contain KPI card structure"
    
    # Must contain tooltip wrapper structure
    assert has_tooltip_wrapper_structure(combined_html), \
        "Output must contain tooltip wrapper structure"
    
    # Must contain both title and value
    assert title in combined_html, \
        f"KPI card title '{title}' must be in output"
    
    assert value in combined_html, \
        f"KPI card value '{value}' must be in output"
    
    # Must contain tooltip text
    assert tooltip_text in combined_html, \
        f"Tooltip text '{tooltip_text}' must be in output"


@given(
    title=kpi_titles,
    value=kpi_values,
    change=change_indicators
)
@settings(max_examples=10, deadline=None)
def test_kpi_card_without_tooltip_is_standalone(
    title: str,
    value: str,
    change: str
):
    """
    Verify that KPI card without tooltip is rendered standalone.
    """
    from utils.components import kpi_card
    
    captured_html = []
    captured_markdown = []
    
    def mock_html(content_html):
        captured_html.append(content_html)
    
    def mock_markdown(content_html, **kwargs):
        captured_markdown.append(content_html)
    
    with patch('streamlit.html', side_effect=mock_html), \
         patch('streamlit.markdown', side_effect=mock_markdown), \
         patch('utils.components.st.html', side_effect=mock_html), \
         patch('utils.components.st.markdown', side_effect=mock_markdown):
        
        kpi_card(
            title=title,
            value=value,
            change=change,
            tooltip_text=None
        )
    
    combined_html = '\n'.join(captured_html + captured_markdown)
    
    # Must contain KPI card
    assert 'kpi-card' in combined_html, \
        "Output must contain KPI card structure"
    
    # Must NOT contain tooltip wrapper
    assert not has_tooltip_wrapper_structure(combined_html), \
        "Output must NOT contain tooltip wrapper when tooltip_text is None"
    
    # Must contain title and value
    assert title in combined_html, \
        f"KPI card title '{title}' must be in output"
    
    assert value in combined_html, \
        f"KPI card value '{value}' must be in output"


@given(
    title=kpi_titles,
    value=kpi_values,
    icon=kpi_icons,
    gradient=gradients
)
@settings(max_examples=10, deadline=None)
def test_kpi_card_styling_elements_present(
    title: str,
    value: str,
    icon: str,
    gradient: str
):
    """
    Verify that KPI card contains proper styling elements.
    """
    from utils.components import kpi_card
    
    captured_html = []
    captured_markdown = []
    
    def mock_html(content_html):
        captured_html.append(content_html)
    
    def mock_markdown(content_html, **kwargs):
        captured_markdown.append(content_html)
    
    with patch('streamlit.html', side_effect=mock_html), \
         patch('streamlit.markdown', side_effect=mock_markdown), \
         patch('utils.components.st.html', side_effect=mock_html), \
         patch('utils.components.st.markdown', side_effect=mock_markdown):
        
        kpi_card(
            title=title,
            value=value,
            icon=icon,
            gradient=gradient,
            tooltip_text=None
        )
    
    combined_html = '\n'.join(captured_html + captured_markdown)
    
    # Must have kpi-card class
    assert 'kpi-card' in combined_html, \
        "KPI card must have kpi-card class"
    
    # Must have kpi-label class
    assert 'kpi-label' in combined_html, \
        "KPI card must have kpi-label class for title"
    
    # Must have kpi-value class
    assert 'kpi-value' in combined_html, \
        "KPI card must have kpi-value class for value"
    
    # Must have icon
    assert f'fa-{icon}' in combined_html, \
        f"KPI card must have icon 'fa-{icon}'"
    
    # Must have role="article" for accessibility
    assert 'role="article"' in combined_html, \
        "KPI card must have role='article' for accessibility"


@given(
    title=kpi_titles,
    value=kpi_values,
    change=change_indicators
)
@settings(max_examples=10, deadline=None)
def test_kpi_card_change_indicator_handling(
    title: str,
    value: str,
    change: str
):
    """
    Verify that KPI card handles change indicators correctly.
    """
    from utils.components import kpi_card
    
    captured_html = []
    captured_markdown = []
    
    def mock_html(content_html):
        captured_html.append(content_html)
    
    def mock_markdown(content_html, **kwargs):
        captured_markdown.append(content_html)
    
    with patch('streamlit.html', side_effect=mock_html), \
         patch('streamlit.markdown', side_effect=mock_markdown), \
         patch('utils.components.st.html', side_effect=mock_html), \
         patch('utils.components.st.markdown', side_effect=mock_markdown):
        
        kpi_card(
            title=title,
            value=value,
            change=change,
            tooltip_text=None
        )
    
    combined_html = '\n'.join(captured_html + captured_markdown)
    
    # If change is provided and non-empty, should have kpi-change class
    if change and change.strip():
        assert 'kpi-change' in combined_html, \
            "KPI card with change indicator must have kpi-change class"
        
        # Should have up or down class
        has_up_or_down = 'class="kpi-change up"' in combined_html or \
                         'class="kpi-change down"' in combined_html
        assert has_up_or_down, \
            "KPI card change indicator must have 'up' or 'down' class"
    else:
        # If no change, should not have kpi-change class
        assert 'kpi-change' not in combined_html, \
            "KPI card without change indicator should not have kpi-change class"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
