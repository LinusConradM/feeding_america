"""
Property-based tests for hero_section component using Hypothesis.

This module validates Properties 2 and 51 from the executive-overview-redesign spec:
- Property 2: Hero Section Content Completeness
- Property 51: Hero Section Primary Metric Typography

**Validates: Requirements 1.2, 15.2, 15.3, 15.4**
"""

import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import patch, MagicMock
import re


# ============================================================================
# Test Strategies (Generators)
# ============================================================================

# Year generator covering dataset range
years = st.integers(min_value=2009, max_value=2023)

# FI rate generator (realistic range: 8% to 20%)
fi_rates = st.floats(min_value=0.08, max_value=0.20, allow_nan=False, allow_infinity=False)

# Context summary generator (non-empty strings)
context_summaries = st.text(min_size=10, max_size=200, alphabet=st.characters(
    whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs', 'Pc'),
    whitelist_characters='.,-'
))

# Previous metric generator (can be None or a valid FI rate)
previous_metrics = st.one_of(
    st.none(),
    st.floats(min_value=0.08, max_value=0.20, allow_nan=False, allow_infinity=False)
)


# ============================================================================
# Helper Functions
# ============================================================================

def extract_year_from_html(html: str) -> int | None:
    """Extract year from hero section HTML."""
    # Look for year in badge: <i class="fas fa-calendar-alt"...>{year}</i>
    year_match = re.search(r'fa-calendar-alt.*?(\d{4})', html, re.DOTALL)
    if year_match:
        return int(year_match.group(1))
    return None


def extract_primary_metric_from_html(html: str) -> float | None:
    """Extract primary metric (FI rate) from hero section HTML."""
    # Look for percentage in the primary metric div
    # Pattern: <div class="text-5xl...>{percentage}%</div>
    # The percentage is formatted as X.X% (e.g., 12.5%)
    metric_match = re.search(r'text-5xl[^>]*>[\s\n]*([\d.]+)%', html, re.DOTALL)
    if metric_match:
        return float(metric_match.group(1)) / 100.0
    return None


def extract_context_summary_from_html(html: str) -> str | None:
    """Extract context summary from hero section HTML."""
    # Look for context summary in the last div
    # It's after "National Food Insecurity Rate" and before the closing div
    summary_match = re.search(
        r'National Food Insecurity Rate.*?<div[^>]*>(.*?)</div>\s*</div>\s*$',
        html,
        re.DOTALL
    )
    if summary_match:
        # Clean HTML tags and extract text
        summary = summary_match.group(1)
        # Remove span tags but keep content
        summary = re.sub(r'<span[^>]*>', '', summary)
        summary = re.sub(r'</span>', '', summary)
        summary = summary.strip()
        return summary
    return None


def extract_font_size_from_html(html: str) -> str | None:
    """Extract font size class from primary metric."""
    # Look for text-{size} class in primary metric div
    size_match = re.search(r'class="[^"]*text-(\w+)[^"]*"', html)
    if size_match:
        return size_match.group(1)
    return None


def extract_font_weight_from_html(html: str) -> str | None:
    """Extract font weight class from primary metric."""
    # Look for font-bold or font-{weight} class
    weight_match = re.search(r'class="[^"]*font-(bold|semibold|medium|normal)[^"]*"', html)
    if weight_match:
        return weight_match.group(1)
    return None


def convert_tailwind_size_to_rem(size_class: str) -> float:
    """Convert Tailwind text size class to rem value."""
    size_map = {
        'xs': 0.75,
        'sm': 0.875,
        'base': 1.0,
        'lg': 1.125,
        'xl': 1.25,
        '2xl': 1.5,
        '3xl': 1.875,
        '4xl': 2.25,
        '5xl': 3.0,  # This is what we expect (3rem)
        '6xl': 3.75,
        '7xl': 4.5,
        '8xl': 6.0,
        '9xl': 8.0,
    }
    return size_map.get(size_class, 0.0)


def convert_tailwind_weight_to_numeric(weight_class: str) -> int:
    """Convert Tailwind font weight class to numeric value."""
    weight_map = {
        'thin': 100,
        'extralight': 200,
        'light': 300,
        'normal': 400,
        'medium': 500,
        'semibold': 600,
        'bold': 700,  # This is what we expect (700)
        'extrabold': 800,
        'black': 900,
    }
    return weight_map.get(weight_class, 0)


# ============================================================================
# Property 2: Hero Section Content Completeness
# ============================================================================

@given(
    year=years,
    primary_metric=fi_rates,
    previous_metric=previous_metrics,
    context_summary=context_summaries
)
@settings(max_examples=20, deadline=None)
def test_property_2_hero_section_content_completeness(
    year: int,
    primary_metric: float,
    previous_metric: float | None,
    context_summary: str
):
    """
    **Validates: Requirements 1.2, 15.2, 15.3, 15.4**
    
    Property 2: Hero Section Content Completeness
    
    For any selected year with available data, the Hero_Section SHALL display 
    the year, national FI rate as primary metric, and a contextual summary sentence.
    """
    from utils.components import hero_section
    
    # Mock streamlit functions to capture HTML output
    captured_html = []
    
    def mock_html(content):
        captured_html.append(content)
    
    mock_session = {}
    
    with patch('streamlit.html', side_effect=mock_html), \
         patch('streamlit.session_state', mock_session), \
         patch('streamlit.button', return_value=False):
        
        # Call hero_section with generated inputs
        hero_section(
            year=year,
            primary_metric=primary_metric,
            previous_metric=previous_metric,
            context_summary=context_summary,
            show_quick_tips=False  # Disable quick tips for focused testing
        )
    
    # Verify HTML was generated
    assert len(captured_html) > 0, "Hero section should generate HTML output"
    
    hero_html = captured_html[0]
    
    # Property 2 Assertion 1: Year SHALL be displayed
    extracted_year = extract_year_from_html(hero_html)
    assert extracted_year == year, \
        f"Hero section must display year {year}, but found {extracted_year}"
    
    # Property 2 Assertion 2: National FI rate SHALL be displayed as primary metric
    extracted_metric = extract_primary_metric_from_html(hero_html)
    assert extracted_metric is not None, \
        "Hero section must display primary metric (national FI rate)"
    
    # Allow small floating point tolerance (0.1% difference)
    assert abs(extracted_metric - primary_metric) < 0.001, \
        f"Primary metric should be {primary_metric:.1%}, but found {extracted_metric:.1%}"
    
    # Property 2 Assertion 3: Context summary SHALL be displayed
    extracted_summary = extract_context_summary_from_html(hero_html)
    assert extracted_summary is not None, \
        "Hero section must display context summary"
    
    # Verify context summary contains the provided text
    # (may have additional comparison text appended)
    assert context_summary.strip() in extracted_summary, \
        f"Context summary must contain '{context_summary}', but found '{extracted_summary}'"


# ============================================================================
# Property 51: Hero Section Primary Metric Typography
# ============================================================================

@given(
    year=years,
    primary_metric=fi_rates,
    previous_metric=previous_metrics,
    context_summary=context_summaries
)
@settings(max_examples=20, deadline=None)
def test_property_51_hero_section_primary_metric_typography(
    year: int,
    primary_metric: float,
    previous_metric: float | None,
    context_summary: str
):
    """
    **Validates: Requirements 15.3**
    
    Property 51: Hero Section Primary Metric Typography
    
    For any Hero_Section, the national FI rate SHALL be displayed with 
    font-size >= 2.5rem and font-weight >= 700.
    """
    from utils.components import hero_section
    
    # Mock streamlit functions to capture HTML output
    captured_html = []
    
    def mock_html(content):
        captured_html.append(content)
    
    mock_session = {}
    
    with patch('streamlit.html', side_effect=mock_html), \
         patch('streamlit.session_state', mock_session), \
         patch('streamlit.button', return_value=False):
        
        # Call hero_section with generated inputs
        hero_section(
            year=year,
            primary_metric=primary_metric,
            previous_metric=previous_metric,
            context_summary=context_summary,
            show_quick_tips=False
        )
    
    # Verify HTML was generated
    assert len(captured_html) > 0, "Hero section should generate HTML output"
    
    hero_html = captured_html[0]
    
    # Property 51 Assertion 1: Font size SHALL be >= 2.5rem
    font_size_class = extract_font_size_from_html(hero_html)
    assert font_size_class is not None, \
        "Primary metric must have a font size class"
    
    font_size_rem = convert_tailwind_size_to_rem(font_size_class)
    assert font_size_rem >= 2.5, \
        f"Primary metric font size must be >= 2.5rem, but found {font_size_rem}rem (text-{font_size_class})"
    
    # Property 51 Assertion 2: Font weight SHALL be >= 700
    font_weight_class = extract_font_weight_from_html(hero_html)
    assert font_weight_class is not None, \
        "Primary metric must have a font weight class"
    
    font_weight_numeric = convert_tailwind_weight_to_numeric(font_weight_class)
    assert font_weight_numeric >= 700, \
        f"Primary metric font weight must be >= 700, but found {font_weight_numeric} (font-{font_weight_class})"


# ============================================================================
# Additional Property Tests for Robustness
# ============================================================================

@given(
    year=years,
    primary_metric=fi_rates,
    previous_metric=fi_rates
)
@settings(max_examples=10, deadline=None)
def test_property_2_year_over_year_comparison_displayed(
    year: int,
    primary_metric: float,
    previous_metric: float
):
    """
    Property 2 Extension: When previous_metric is provided, 
    year-over-year comparison SHALL be displayed.
    
    **Validates: Requirements 15.4**
    """
    from utils.components import hero_section
    
    captured_html = []
    
    def mock_html(content):
        captured_html.append(content)
    
    with patch('streamlit.html', side_effect=mock_html), \
         patch('streamlit.session_state', {}), \
         patch('streamlit.button', return_value=False):
        
        hero_section(
            year=year,
            primary_metric=primary_metric,
            previous_metric=previous_metric,
            context_summary="Test summary",
            show_quick_tips=False
        )
    
    hero_html = captured_html[0]
    
    # When previous_metric is provided, comparison text should appear
    # Should contain "up" or "down" and the previous year
    assert ("up" in hero_html.lower() or "down" in hero_html.lower()), \
        "Year-over-year comparison should indicate direction (up/down)"
    
    assert str(year - 1) in hero_html, \
        f"Year-over-year comparison should reference previous year {year - 1}"


@given(
    year=years,
    primary_metric=fi_rates,
    context_summary=context_summaries
)
@settings(max_examples=10, deadline=None)
def test_property_2_no_comparison_when_previous_metric_none(
    year: int,
    primary_metric: float,
    context_summary: str
):
    """
    Property 2 Extension: When previous_metric is None, 
    no year-over-year comparison SHALL be displayed.
    
    **Validates: Requirements 15.4**
    """
    from utils.components import hero_section
    
    captured_html = []
    
    def mock_html(content):
        captured_html.append(content)
    
    with patch('streamlit.html', side_effect=mock_html), \
         patch('streamlit.session_state', {}), \
         patch('streamlit.button', return_value=False):
        
        hero_section(
            year=year,
            primary_metric=primary_metric,
            previous_metric=None,
            context_summary=context_summary,
            show_quick_tips=False
        )
    
    hero_html = captured_html[0]
    
    # When previous_metric is None, should not show comparison
    # The previous year should not appear in the HTML
    assert str(year - 1) not in hero_html, \
        f"Should not reference previous year {year - 1} when previous_metric is None"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
