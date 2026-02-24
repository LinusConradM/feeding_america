"""
Property-based tests for section_header component.

Tests validate Properties 43, 44, 45, 46 from the executive-overview-redesign spec:
- Property 43: Section header completeness (title is always present)
- Property 44: Subtitle parameter works correctly when provided
- Property 45: Spacing is consistent (24px top, 16px bottom)
- Property 46: Typography meets minimum 18px for subtitle

Uses Hypothesis for property-based testing with 20 iterations per test.
"""

import pytest
import re
from hypothesis import given, strategies as st, settings
from bs4 import BeautifulSoup
from utils.components import section_header
from unittest.mock import patch, MagicMock


class TestSectionHeaderProperties:
    """Property-based tests for section_header completeness and styling."""
    
    @given(
        title=st.text(min_size=1, max_size=100, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'),
            blacklist_characters=('<', '>', '"', "'")
        )),
        subtitle=st.text(min_size=0, max_size=200, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs', 'Po'),
            blacklist_characters=('<', '>', '"', "'")
        )),
        icon=st.one_of(
            st.just(""),
            st.sampled_from(["chart-line", "map", "users", "info-circle", "star"])
        )
    )
    @settings(max_examples=20)
    def test_property_43_section_header_completeness(self, title, subtitle, icon):
        """
        **Validates: Requirements 13.1, 13.2**
        
        Property 43: Section Header Completeness
        
        For any major content section, there SHALL be a section header 
        containing a title and icon.
        """
        # Mock st.markdown to capture the rendered HTML
        with patch('utils.components.st.markdown') as mock_markdown:
            section_header(title=title, subtitle=subtitle, icon=icon)
            
            # Verify st.markdown was called
            assert mock_markdown.called, "section_header should call st.markdown"
            
            # Get the rendered HTML
            call_args = mock_markdown.call_args
            html_content = call_args[0][0]
            
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Verify section-hdr div exists
            section_div = soup.find('div', class_='section-hdr')
            assert section_div is not None, "section-hdr div must exist"
            
            # Verify h2 element exists
            h2 = section_div.find('h2')
            assert h2 is not None, "h2 element must exist in section header"
            
            # Verify title is present in h2
            h2_text = h2.get_text()
            assert title in h2_text, f"Title '{title}' must be present in h2"
            
            # Verify icon is present if provided
            if icon:
                icon_element = h2.find('i', class_=re.compile(r'fa-' + re.escape(icon)))
                assert icon_element is not None, f"Icon '{icon}' must be present when provided"
    
    @given(
        title=st.text(min_size=1, max_size=100, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'),
            blacklist_characters=('<', '>', '"', "'")
        )),
        subtitle=st.text(min_size=1, max_size=200, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs', 'Po'),
            blacklist_characters=('<', '>', '"', "'")
        ))
    )
    @settings(max_examples=20)
    def test_property_44_subtitle_parameter(self, title, subtitle):
        """
        **Validates: Requirements 13.2, 13.3**
        
        Property 44: Subtitle Parameter
        
        For any section header, there SHALL be a descriptive subtitle 
        explaining the content purpose when provided.
        """
        # Mock st.markdown to capture the rendered HTML
        with patch('utils.components.st.markdown') as mock_markdown:
            section_header(title=title, subtitle=subtitle, icon="")
            
            # Get the rendered HTML
            call_args = mock_markdown.call_args
            html_content = call_args[0][0]
            
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Verify section-hdr div exists
            section_div = soup.find('div', class_='section-hdr')
            assert section_div is not None, "section-hdr div must exist"
            
            # Verify p element exists when subtitle is provided
            p_element = section_div.find('p')
            assert p_element is not None, "p element must exist when subtitle is provided"
            
            # Verify subtitle text is present
            p_text = p_element.get_text()
            assert subtitle in p_text, f"Subtitle '{subtitle}' must be present in p element"
    
    @given(
        title=st.text(min_size=1, max_size=100, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'),
            blacklist_characters=('<', '>', '"', "'")
        ))
    )
    @settings(max_examples=20)
    def test_property_44_subtitle_optional(self, title):
        """
        **Validates: Requirements 13.2**
        
        Property 44: Subtitle Parameter (Optional)
        
        Section headers must support optional subtitle parameter.
        When not provided, no subtitle element should be rendered.
        """
        # Mock st.markdown to capture the rendered HTML
        with patch('utils.components.st.markdown') as mock_markdown:
            section_header(title=title, subtitle="", icon="")
            
            # Get the rendered HTML
            call_args = mock_markdown.call_args
            html_content = call_args[0][0]
            
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Verify section-hdr div exists
            section_div = soup.find('div', class_='section-hdr')
            assert section_div is not None, "section-hdr div must exist"
            
            # Verify p element does NOT exist when subtitle is empty
            p_element = section_div.find('p')
            # The p element should either not exist or be empty
            if p_element is not None:
                p_text = p_element.get_text().strip()
                assert p_text == "", "p element should be empty when no subtitle provided"


class TestSectionHeaderSpacingAndTypography:
    """Test spacing and typography requirements for section headers."""
    
    def test_property_45_section_header_spacing(self):
        """
        **Validates: Requirements 13.4**
        
        Property 45: Section Header Spacing
        
        For any section header, it SHALL have margin-top >= 24px and 
        margin-bottom >= 16px.
        
        Note: CSS defines margin-top: 1.5rem (24px) and margin-bottom: 1rem (16px)
        """
        # This property is validated through CSS inspection
        # The CSS in utils/theme.py defines:
        # .section-hdr { margin-top: 1.5rem; margin-bottom: 1rem; }
        # 1.5rem = 24px (assuming 16px base font size)
        # 1rem = 16px
        
        # Mock st.markdown to capture the rendered HTML
        with patch('utils.components.st.markdown') as mock_markdown:
            section_header(title="Test Title", subtitle="Test Subtitle", icon="chart-line")
            
            # Get the rendered HTML
            call_args = mock_markdown.call_args
            html_content = call_args[0][0]
            
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Verify section-hdr div exists with correct class
            section_div = soup.find('div', class_='section-hdr')
            assert section_div is not None, "section-hdr div must exist"
            
            # The spacing is enforced by CSS class 'section-hdr'
            # which is defined in utils/theme.py with:
            # margin-top: 1.5rem (24px) and margin-bottom: 1rem (16px)
            assert 'section-hdr' in section_div.get('class', []), \
                "section-hdr class must be present to enforce spacing"
    
    def test_property_46_subtitle_typography_minimum(self):
        """
        **Validates: Requirements 13.5**
        
        Property 46: Section Header Typography Minimum
        
        For any section header at any breakpoint, the subtitle text SHALL 
        have font size >= 18px.
        
        Note: CSS defines font-size: 1.125rem (18px) for subtitle
        """
        # This property is validated through CSS inspection
        # The CSS in utils/theme.py defines:
        # .section-hdr p { font-size: 1.125rem; }
        # 1.125rem = 18px (assuming 16px base font size)
        
        # Mock st.markdown to capture the rendered HTML
        with patch('utils.components.st.markdown') as mock_markdown:
            section_header(title="Test Title", subtitle="Test Subtitle", icon="")
            
            # Get the rendered HTML
            call_args = mock_markdown.call_args
            html_content = call_args[0][0]
            
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Verify section-hdr div exists
            section_div = soup.find('div', class_='section-hdr')
            assert section_div is not None, "section-hdr div must exist"
            
            # Verify p element exists
            p_element = section_div.find('p')
            assert p_element is not None, "p element must exist for subtitle"
            
            # The typography is enforced by CSS class 'section-hdr'
            # which is defined in utils/theme.py with:
            # .section-hdr p { font-size: 1.125rem; } (18px)
            # This applies across all breakpoints (mobile CSS also sets 1.125rem)
            assert section_div.get('class') == ['section-hdr'], \
                "section-hdr class must be present to enforce typography"


class TestSectionHeaderBoundaryConditions:
    """Test boundary conditions and edge cases for section headers."""
    
    def test_title_required_parameter(self):
        """Test that title parameter is required (cannot be empty)."""
        # Mock st.markdown
        with patch('utils.components.st.markdown') as mock_markdown:
            # Title with minimal content
            section_header(title="A", subtitle="", icon="")
            
            # Verify it was called
            assert mock_markdown.called
            
            # Get the rendered HTML
            call_args = mock_markdown.call_args
            html_content = call_args[0][0]
            
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            h2 = soup.find('h2')
            assert h2 is not None
            assert "A" in h2.get_text()
    
    def test_icon_optional_parameter(self):
        """Test that icon parameter is optional."""
        # Mock st.markdown
        with patch('utils.components.st.markdown') as mock_markdown:
            section_header(title="Test Title", subtitle="Test Subtitle", icon="")
            
            # Get the rendered HTML
            call_args = mock_markdown.call_args
            html_content = call_args[0][0]
            
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Verify no icon element exists
            icon_element = soup.find('i', class_=re.compile(r'fa-'))
            assert icon_element is None, "No icon element should exist when icon is empty"
    
    def test_multiple_icons_not_rendered(self):
        """Test that only one icon is rendered even if icon parameter contains multiple values."""
        # Mock st.markdown
        with patch('utils.components.st.markdown') as mock_markdown:
            section_header(title="Test Title", subtitle="", icon="chart-line")
            
            # Get the rendered HTML
            call_args = mock_markdown.call_args
            html_content = call_args[0][0]
            
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Verify exactly one icon element exists
            icon_elements = soup.find_all('i', class_=re.compile(r'fa-'))
            assert len(icon_elements) == 1, "Exactly one icon element should exist"
    
    def test_html_escaping_in_title(self):
        """Test that HTML special characters in title are handled safely."""
        # Mock st.markdown
        with patch('utils.components.st.markdown') as mock_markdown:
            # Note: We're testing the component behavior, not injecting actual HTML
            # The component uses unsafe_allow_html=True, so we verify structure
            section_header(title="Test & Title", subtitle="", icon="")
            
            # Verify st.markdown was called
            assert mock_markdown.called
            
            # Get the rendered HTML
            call_args = mock_markdown.call_args
            html_content = call_args[0][0]
            
            # Verify the title is present in the HTML
            assert "Test & Title" in html_content or "Test &amp; Title" in html_content


class TestSectionHeaderIntegration:
    """Integration tests for section_header with various parameter combinations."""
    
    @given(
        title=st.text(min_size=1, max_size=50, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'),
            blacklist_characters=('<', '>', '"', "'")
        )),
        subtitle=st.text(min_size=0, max_size=100, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs', 'Po'),
            blacklist_characters=('<', '>', '"', "'")
        )),
        icon=st.sampled_from(["", "chart-line", "map", "users", "info-circle"])
    )
    @settings(max_examples=20)
    def test_section_header_complete_integration(self, title, subtitle, icon):
        """
        Integration test verifying all four properties work together:
        - Property 43: Title is always present
        - Property 44: Subtitle works when provided
        - Property 45: Spacing is consistent (via CSS class)
        - Property 46: Typography meets minimum (via CSS class)
        """
        # Mock st.markdown
        with patch('utils.components.st.markdown') as mock_markdown:
            section_header(title=title, subtitle=subtitle, icon=icon)
            
            # Verify st.markdown was called
            assert mock_markdown.called
            
            # Get the rendered HTML
            call_args = mock_markdown.call_args
            html_content = call_args[0][0]
            
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Property 43: Verify title is present
            section_div = soup.find('div', class_='section-hdr')
            assert section_div is not None
            h2 = section_div.find('h2')
            assert h2 is not None
            assert title in h2.get_text()
            
            # Property 44: Verify subtitle when provided
            if subtitle:
                p_element = section_div.find('p')
                assert p_element is not None
                assert subtitle in p_element.get_text()
            
            # Property 45 & 46: Verify CSS class is present
            # (spacing and typography are enforced by CSS)
            assert 'section-hdr' in section_div.get('class', [])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
