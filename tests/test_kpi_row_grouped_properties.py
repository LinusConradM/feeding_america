"""
Property-based tests for kpi_row_grouped component.

Tests validate Properties 3, 4, 5 from the executive-overview-redesign spec:
- Property 3: KPI Card Row Grouping
- Property 4: Desktop KPI Layout (4 columns)
- Property 5: Mobile KPI Layout Preservation (vertical stacking with row groupings)

Uses Hypothesis for property-based testing with 20 iterations per test.
"""

import pytest
from hypothesis import given, strategies as st, settings
from utils.responsive import ViewportProfile
from utils.components import kpi_row_grouped
from bs4 import BeautifulSoup
from unittest.mock import MagicMock, patch
import streamlit


# Strategy for generating KPI card configurations
@st.composite
def kpi_card_config(draw):
    """Generate a valid KPI card configuration."""
    return {
        "title": draw(st.text(min_size=1, max_size=30, alphabet=st.characters(whitelist_categories=("L", "N", " ")))),
        "value": draw(st.text(min_size=1, max_size=20)),
        "change": draw(st.one_of(
            st.just(""),
            st.text(min_size=1, max_size=10).map(lambda x: f"+{x}"),
            st.text(min_size=1, max_size=10).map(lambda x: f"-{x}")
        )),
        "icon": draw(st.sampled_from(["chart-line", "users", "dollar-sign", "percent", "briefcase"])),
        "gradient": draw(st.sampled_from(["blue", "teal", "amber", "rose"]))
    }


@st.composite
def row_group_config(draw, num_cards):
    """Generate a row group configuration with specified number of cards."""
    return {
        "title": draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=("L", "N", " ")))),
        "cards": [draw(kpi_card_config()) for _ in range(num_cards)]
    }


class TestKPIRowGroupingProperties:
    """Property-based tests for KPI row grouping and responsive layout."""
    
    @given(
        viewport_width=st.integers(min_value=320, max_value=2560),
        is_mobile=st.booleans(),
        is_portrait=st.booleans()
    )
    @settings(max_examples=20)
    def test_property_3_kpi_card_row_grouping(self, viewport_width, is_mobile, is_portrait):
        """
        **Validates: Requirements 2.1, 2.2, 2.3**
        
        Property 3: KPI Card Row Grouping
        
        For any rendered dashboard, KPI_Cards SHALL be organized into exactly 
        two rows: Row 1 containing [National FI Rate, Food Insecure Persons, 
        Child FI Rate, Cost Per Meal] and Row 2 containing [Poverty Rate, 
        Median Income, Unemployment, Budget Shortfall].
        """
        # Create viewport profile
        profile = ViewportProfile(
            width=viewport_width,
            is_mobile=is_mobile,
            is_portrait=is_portrait
        )
        
        # Define the two required row groups
        row_groups = [
            {
                "title": "Core Food Insecurity Metrics",
                "cards": [
                    {"title": "National FI Rate", "value": "12.3%", "change": "+0.5%", "icon": "chart-line", "gradient": "blue"},
                    {"title": "Food Insecure Persons", "value": "42.2M", "change": "+1.2M", "icon": "users", "gradient": "blue"},
                    {"title": "Child FI Rate", "value": "16.8%", "change": "+0.8%", "icon": "child", "gradient": "blue"},
                    {"title": "Cost Per Meal", "value": "$3.42", "change": "+$0.12", "icon": "dollar-sign", "gradient": "blue"}
                ]
            },
            {
                "title": "Economic Drivers",
                "cards": [
                    {"title": "Poverty Rate", "value": "11.5%", "change": "-0.3%", "icon": "percent", "gradient": "teal"},
                    {"title": "Median Income", "value": "$70,784", "change": "+$2,100", "icon": "dollar-sign", "gradient": "teal"},
                    {"title": "Unemployment", "value": "3.7%", "change": "-0.2%", "icon": "briefcase", "gradient": "teal"},
                    {"title": "Budget Shortfall", "value": "$8.4B", "change": "+$0.5B", "icon": "chart-line", "gradient": "teal"}
                ]
            }
        ]
        
        # Mock Streamlit's markdown and html methods to capture output
        captured_html = []
        
        def mock_markdown(content, unsafe_allow_html=False):
            if unsafe_allow_html:
                captured_html.append(content)
        
        def mock_html(content):
            captured_html.append(content)
        
        with patch.object(streamlit, 'markdown', side_effect=mock_markdown):
            with patch.object(streamlit, 'html', side_effect=mock_html):
                # Render the component
                kpi_row_grouped(row_groups, profile)
        
        # Combine all captured HTML
        full_html = "".join(captured_html)
        
        # Parse HTML
        soup = BeautifulSoup(full_html, 'html.parser')
        
        # Verify exactly two row group headers are present
        headers = soup.find_all('h3')
        assert len(headers) == 2, f"Expected 2 row group headers, found {len(headers)}"
        
        # Verify row group titles
        header_texts = [h.get_text(strip=True) for h in headers]
        assert "Core Food Insecurity Metrics" in header_texts[0], \
            f"First row group should be 'Core Food Insecurity Metrics', got '{header_texts[0]}'"
        assert "Economic Drivers" in header_texts[1], \
            f"Second row group should be 'Economic Drivers', got '{header_texts[1]}'"
        
        # Verify cards are present
        cards = soup.find_all('div', class_='kpi-card')
        assert len(cards) == 8, f"Expected 8 KPI cards total (4 per row), found {len(cards)}"
    
    @given(viewport_width=st.integers(min_value=1025, max_value=2560))
    @settings(max_examples=20)
    def test_property_4_desktop_kpi_layout(self, viewport_width):
        """
        **Validates: Requirements 2.4, 8.2**
        
        Property 4: Desktop KPI Layout
        
        For any viewport width > 1024px, each KPI row SHALL display 4 cards 
        in horizontal layout.
        """
        # Create desktop viewport profile
        profile = ViewportProfile(
            width=viewport_width,
            is_mobile=False,
            is_portrait=False
        )
        
        # Verify it's desktop
        assert profile.breakpoint_name == "desktop", \
            f"Width {viewport_width}px should be desktop breakpoint"
        assert profile.kpi_columns == 4, \
            f"Desktop should have 4 KPI columns, got {profile.kpi_columns}"
        
        # Create a single row group with 4 cards
        row_groups = [
            {
                "title": "Test Row",
                "cards": [
                    {"title": f"Card {i}", "value": f"{i}", "change": "", "icon": "chart-line", "gradient": "blue"}
                    for i in range(4)
                ]
            }
        ]
        
        # Mock Streamlit's markdown and html methods to capture output
        captured_html = []
        
        def mock_markdown(content, unsafe_allow_html=False):
            if unsafe_allow_html:
                captured_html.append(content)
        
        def mock_html(content):
            captured_html.append(content)
        
        with patch.object(streamlit, 'markdown', side_effect=mock_markdown):
            with patch.object(streamlit, 'html', side_effect=mock_html):
                # Render the component
                kpi_row_grouped(row_groups, profile)
        
        # Combine all captured HTML
        full_html = "".join(captured_html)
        
        # Verify grid-cols-4 class is present for desktop
        assert 'grid-cols-4' in full_html, \
            f"Desktop layout should use 'grid-cols-4' class for 4-column layout"
        
        # Parse HTML to verify card count
        soup = BeautifulSoup(full_html, 'html.parser')
        cards = soup.find_all('div', class_='kpi-card')
        assert len(cards) == 4, f"Expected 4 cards in desktop layout, found {len(cards)}"
    
    @given(viewport_width=st.integers(min_value=320, max_value=767))
    @settings(max_examples=20)
    def test_property_5_mobile_kpi_layout_preservation(self, viewport_width):
        """
        **Validates: Requirements 2.5, 9.2**
        
        Property 5: Mobile KPI Layout Preservation
        
        For any viewport width < 768px, KPI_Cards SHALL stack vertically while 
        maintaining row groupings (Row 1 cards appear before Row 2 cards).
        """
        # Create mobile viewport profile
        profile = ViewportProfile(
            width=viewport_width,
            is_mobile=True,
            is_portrait=True
        )
        
        # Verify it's mobile
        assert profile.breakpoint_name == "mobile", \
            f"Width {viewport_width}px should be mobile breakpoint"
        assert profile.kpi_columns == 1, \
            f"Mobile should have 1 KPI column, got {profile.kpi_columns}"
        
        # Define two row groups
        row_groups = [
            {
                "title": "Row 1",
                "cards": [
                    {"title": "Card 1A", "value": "1A", "change": "", "icon": "chart-line", "gradient": "blue"},
                    {"title": "Card 1B", "value": "1B", "change": "", "icon": "chart-line", "gradient": "blue"}
                ]
            },
            {
                "title": "Row 2",
                "cards": [
                    {"title": "Card 2A", "value": "2A", "change": "", "icon": "chart-line", "gradient": "teal"},
                    {"title": "Card 2B", "value": "2B", "change": "", "icon": "chart-line", "gradient": "teal"}
                ]
            }
        ]
        
        # Mock Streamlit's markdown and html methods to capture output
        captured_html = []
        
        def mock_markdown(content, unsafe_allow_html=False):
            if unsafe_allow_html:
                captured_html.append(content)
        
        def mock_html(content):
            captured_html.append(content)
        
        with patch.object(streamlit, 'markdown', side_effect=mock_markdown):
            with patch.object(streamlit, 'html', side_effect=mock_html):
                # Render the component
                kpi_row_grouped(row_groups, profile)
        
        # Combine all captured HTML
        full_html = "".join(captured_html)
        
        # Verify grid-cols-1 class is present for mobile
        assert 'grid-cols-1' in full_html, \
            f"Mobile layout should use 'grid-cols-1' class for single-column layout"
        
        # Parse HTML to verify ordering
        soup = BeautifulSoup(full_html, 'html.parser')
        
        # Find all row group headers
        headers = soup.find_all('h3')
        assert len(headers) == 2, f"Expected 2 row group headers, found {len(headers)}"
        
        # Verify row groupings are maintained in order
        header_texts = [h.get_text(strip=True) for h in headers]
        assert "Row 1" in header_texts[0], \
            f"First row group should be 'Row 1', got '{header_texts[0]}'"
        assert "Row 2" in header_texts[1], \
            f"Second row group should be 'Row 2', got '{header_texts[1]}'"
        
        # Verify all cards are present
        cards = soup.find_all('div', class_='kpi-card')
        assert len(cards) == 4, f"Expected 4 cards total, found {len(cards)}"


class TestKPIRowGroupingBoundaryConditions:
    """Test boundary conditions for KPI row grouping."""
    
    def test_desktop_lower_boundary_1025px(self):
        """Test that 1025px (desktop lower boundary) uses 4-column layout."""
        profile = ViewportProfile(width=1025, is_mobile=False, is_portrait=False)
        assert profile.breakpoint_name == "desktop"
        assert profile.kpi_columns == 4
    
    def test_tablet_uses_2_columns(self):
        """Test that tablet viewport uses 2-column layout."""
        profile = ViewportProfile(width=900, is_mobile=False, is_portrait=False)
        assert profile.breakpoint_name == "tablet"
        assert profile.kpi_columns == 2
    
    def test_mobile_upper_boundary_767px(self):
        """Test that 767px (mobile upper boundary) uses 1-column layout."""
        profile = ViewportProfile(width=767, is_mobile=True, is_portrait=False)
        assert profile.breakpoint_name == "mobile"
        assert profile.kpi_columns == 1
    
    def test_mobile_minimum_320px(self):
        """Test that 320px (common mobile minimum) uses 1-column layout."""
        profile = ViewportProfile(width=320, is_mobile=True, is_portrait=True)
        assert profile.breakpoint_name == "mobile"
        assert profile.kpi_columns == 1


class TestKPIRowGroupingConsistency:
    """Test that KPI column counts are consistent across viewport ranges."""
    
    @given(
        width1=st.integers(min_value=1025, max_value=2560),
        width2=st.integers(min_value=1025, max_value=2560)
    )
    @settings(max_examples=10)
    def test_desktop_columns_are_consistent(self, width1, width2):
        """Test that all desktop viewports return 4 columns."""
        profile1 = ViewportProfile(width=width1, is_mobile=False, is_portrait=False)
        profile2 = ViewportProfile(width=width2, is_mobile=False, is_portrait=False)
        
        assert profile1.kpi_columns == 4, f"Desktop should have 4 columns at {width1}px"
        assert profile2.kpi_columns == 4, f"Desktop should have 4 columns at {width2}px"
        assert profile1.kpi_columns == profile2.kpi_columns, \
            f"Desktop column counts should be consistent"
    
    @given(
        width1=st.integers(min_value=768, max_value=1024),
        width2=st.integers(min_value=768, max_value=1024)
    )
    @settings(max_examples=10)
    def test_tablet_columns_are_consistent(self, width1, width2):
        """Test that all tablet viewports return 2 columns."""
        profile1 = ViewportProfile(width=width1, is_mobile=False, is_portrait=False)
        profile2 = ViewportProfile(width=width2, is_mobile=False, is_portrait=False)
        
        assert profile1.kpi_columns == 2, f"Tablet should have 2 columns at {width1}px"
        assert profile2.kpi_columns == 2, f"Tablet should have 2 columns at {width2}px"
        assert profile1.kpi_columns == profile2.kpi_columns, \
            f"Tablet column counts should be consistent"
    
    @given(
        width1=st.integers(min_value=320, max_value=767),
        width2=st.integers(min_value=320, max_value=767)
    )
    @settings(max_examples=10)
    def test_mobile_columns_are_consistent(self, width1, width2):
        """Test that all mobile viewports return 1 column."""
        profile1 = ViewportProfile(width=width1, is_mobile=True, is_portrait=True)
        profile2 = ViewportProfile(width=width2, is_mobile=True, is_portrait=True)
        
        assert profile1.kpi_columns == 1, f"Mobile should have 1 column at {width1}px"
        assert profile2.kpi_columns == 1, f"Mobile should have 1 column at {width2}px"
        assert profile1.kpi_columns == profile2.kpi_columns, \
            f"Mobile column counts should be consistent"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
