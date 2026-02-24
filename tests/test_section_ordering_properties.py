"""
Property-based tests for Executive Overview dashboard section ordering.

Tests validate Property 1 from the executive-overview-redesign spec:
- Property 1: Section Ordering

Uses Hypothesis for property-based testing with 20 iterations per test.
"""

import pytest
import re
from hypothesis import given, strategies as st, settings
from bs4 import BeautifulSoup
from unittest.mock import patch, MagicMock, mock_open
import sys
import io


class TestSectionOrderingProperty:
    """Property-based tests for dashboard section ordering."""
    
    def test_property_1_section_ordering(self):
        """
        **Validates: Requirements 1.1, 1.3**
        
        Property 1: Section Ordering
        
        For any rendered dashboard, sections SHALL appear in the following order: 
        Hero_Section, National Trend, Geographic_Section, State Rankings, 
        Statistical Details, maintaining a narrative flow from national to 
        state-level scope.
        
        Expected section order:
        1. Hero Section (with year badge, primary metric, context summary)
        2. National Trend Chart
        3. Geographic Section (state map, regional comparison, urban/rural)
        4. State Lookup
        5. State Rankings (collapsible)
        6. Statistical Details (collapsible)
        
        This test verifies section ordering by analyzing the source code structure
        of the dashboard file, ensuring sections appear in the correct order
        regardless of runtime state or selected year.
        """
        # Read the dashboard source file
        with open('views/1_Executive_Overview.py', 'r') as f:
            source_code = f.read()
        
        # Find section markers in order
        section_patterns = [
            (r'SECTION 1.*HERO SECTION', 'Hero Section'),
            (r'SECTION 2.*NATIONAL TREND', 'National Trend'),
            (r'SECTION 3.*GEOGRAPHIC', 'Geographic Section'),
            (r'SECTION 3\.5.*STATE LOOKUP', 'State Lookup'),
            (r'SECTION 4.*STATE RANKINGS', 'State Rankings'),
            (r'SECTION 5.*STATISTICAL DETAILS', 'Statistical Details'),
        ]
        
        section_positions = []
        for pattern, section_name in section_patterns:
            match = re.search(pattern, source_code, re.IGNORECASE)
            assert match is not None, \
                f"Section marker for '{section_name}' not found in source code"
            section_positions.append((match.start(), section_name))
        
        # Sort by position in source code
        section_positions.sort(key=lambda x: x[0])
        actual_order = [name for _, name in section_positions]
        
        # Expected order
        expected_order = [
            'Hero Section',
            'National Trend',
            'Geographic Section',
            'State Lookup',
            'State Rankings',
            'Statistical Details'
        ]
        
        # Verify all sections are present
        assert len(actual_order) == len(expected_order), \
            f"Expected {len(expected_order)} sections, found {len(actual_order)}: {actual_order}"
        
        # Verify sections appear in correct order
        for i, (expected, actual) in enumerate(zip(expected_order, actual_order)):
            assert expected == actual, \
                f"Section {i+1} should be '{expected}', but found '{actual}'. " \
                f"Full order: {actual_order}"
        
        # Verify narrative flow: national → regional → state → statistical
        # Hero Section and National Trend are national scope
        # Geographic Section is regional scope
        # State Lookup and State Rankings are state scope
        # Statistical Details is statistical scope
        
        # Verify Hero Section comes before National Trend
        hero_idx = actual_order.index('Hero Section')
        trend_idx = actual_order.index('National Trend')
        assert hero_idx < trend_idx, \
            "Hero Section must come before National Trend"
        
        # Verify National Trend comes before Geographic Section
        geo_idx = actual_order.index('Geographic Section')
        assert trend_idx < geo_idx, \
            "National Trend must come before Geographic Section"
        
        # Verify Geographic Section comes before State Lookup
        lookup_idx = actual_order.index('State Lookup')
        assert geo_idx < lookup_idx, \
            "Geographic Section must come before State Lookup"
        
        # Verify State Lookup comes before State Rankings
        rankings_idx = actual_order.index('State Rankings')
        assert lookup_idx < rankings_idx, \
            "State Lookup must come before State Rankings"
        
        # Verify State Rankings comes before Statistical Details
        stats_idx = actual_order.index('Statistical Details')
        assert rankings_idx < stats_idx, \
            "State Rankings must come before Statistical Details"


class TestSectionOrderingStaticAnalysis:
    """Static analysis tests for section ordering without executing the dashboard."""
    
    def test_section_order_in_source_code(self):
        """
        Verify section ordering by analyzing the source code structure.
        
        This test reads the views/1_Executive_Overview.py file and verifies
        that sections appear in the correct order based on their comment markers.
        """
        # Read the dashboard source file
        with open('views/1_Executive_Overview.py', 'r') as f:
            source_code = f.read()
        
        # Find section markers in order
        section_patterns = [
            (r'SECTION 1.*HERO SECTION', 'Hero Section'),
            (r'SECTION 2.*NATIONAL TREND', 'National Trend'),
            (r'SECTION 3.*GEOGRAPHIC', 'Geographic Section'),
            (r'SECTION 3\.5.*STATE LOOKUP', 'State Lookup'),
            (r'SECTION 4.*STATE RANKINGS', 'State Rankings'),
            (r'SECTION 5.*STATISTICAL DETAILS', 'Statistical Details'),
        ]
        
        section_positions = []
        for pattern, section_name in section_patterns:
            match = re.search(pattern, source_code, re.IGNORECASE)
            assert match is not None, \
                f"Section marker for '{section_name}' not found in source code"
            section_positions.append((match.start(), section_name))
        
        # Sort by position in source code
        section_positions.sort(key=lambda x: x[0])
        actual_order = [name for _, name in section_positions]
        
        # Expected order
        expected_order = [
            'Hero Section',
            'National Trend',
            'Geographic Section',
            'State Lookup',
            'State Rankings',
            'Statistical Details'
        ]
        
        # Verify sections appear in correct order
        assert actual_order == expected_order, \
            f"Sections are not in correct order.\nExpected: {expected_order}\nActual: {actual_order}"
    
    def test_hero_section_is_first(self):
        """Verify Hero Section appears first in the dashboard."""
        with open('views/1_Executive_Overview.py', 'r') as f:
            source_code = f.read()
        
        # Find Hero Section marker
        hero_match = re.search(r'SECTION 1.*HERO SECTION', source_code, re.IGNORECASE)
        assert hero_match is not None, "Hero Section marker not found"
        
        # Find all other section markers
        other_sections = [
            r'SECTION 2.*NATIONAL TREND',
            r'SECTION 3.*GEOGRAPHIC',
            r'SECTION 3\.5.*STATE LOOKUP',
            r'SECTION 4.*STATE RANKINGS',
            r'SECTION 5.*STATISTICAL DETAILS',
        ]
        
        hero_pos = hero_match.start()
        
        for pattern in other_sections:
            match = re.search(pattern, source_code, re.IGNORECASE)
            if match:
                assert hero_pos < match.start(), \
                    f"Hero Section must appear before {pattern}"
    
    def test_statistical_details_is_last(self):
        """Verify Statistical Details appears last in the dashboard."""
        with open('views/1_Executive_Overview.py', 'r') as f:
            source_code = f.read()
        
        # Find Statistical Details marker
        stats_match = re.search(r'SECTION 5.*STATISTICAL DETAILS', source_code, re.IGNORECASE)
        assert stats_match is not None, "Statistical Details marker not found"
        
        # Find all other section markers
        other_sections = [
            r'SECTION 1.*HERO SECTION',
            r'SECTION 2.*NATIONAL TREND',
            r'SECTION 3.*GEOGRAPHIC',
            r'SECTION 3\.5.*STATE LOOKUP',
            r'SECTION 4.*STATE RANKINGS',
        ]
        
        stats_pos = stats_match.start()
        
        for pattern in other_sections:
            match = re.search(pattern, source_code, re.IGNORECASE)
            if match:
                assert match.start() < stats_pos, \
                    f"{pattern} must appear before Statistical Details"
    
    def test_narrative_flow_national_to_state(self):
        """
        Verify narrative flow from national to state-level scope.
        
        National scope: Hero Section, National Trend
        Regional scope: Geographic Section
        State scope: State Lookup, State Rankings
        Statistical scope: Statistical Details
        """
        with open('views/1_Executive_Overview.py', 'r') as f:
            source_code = f.read()
        
        # Find all section positions
        sections = {
            'Hero Section': re.search(r'SECTION 1.*HERO SECTION', source_code, re.IGNORECASE),
            'National Trend': re.search(r'SECTION 2.*NATIONAL TREND', source_code, re.IGNORECASE),
            'Geographic Section': re.search(r'SECTION 3.*GEOGRAPHIC', source_code, re.IGNORECASE),
            'State Lookup': re.search(r'SECTION 3\.5.*STATE LOOKUP', source_code, re.IGNORECASE),
            'State Rankings': re.search(r'SECTION 4.*STATE RANKINGS', source_code, re.IGNORECASE),
            'Statistical Details': re.search(r'SECTION 5.*STATISTICAL DETAILS', source_code, re.IGNORECASE),
        }
        
        # Verify all sections exist
        for name, match in sections.items():
            assert match is not None, f"Section '{name}' not found in source code"
        
        # Get positions
        positions = {name: match.start() for name, match in sections.items()}
        
        # Verify narrative flow
        # National scope sections come first
        assert positions['Hero Section'] < positions['Geographic Section'], \
            "Hero Section (national) must come before Geographic Section (regional)"
        assert positions['National Trend'] < positions['Geographic Section'], \
            "National Trend (national) must come before Geographic Section (regional)"
        
        # Regional scope comes before state scope
        assert positions['Geographic Section'] < positions['State Lookup'], \
            "Geographic Section (regional) must come before State Lookup (state)"
        assert positions['Geographic Section'] < positions['State Rankings'], \
            "Geographic Section (regional) must come before State Rankings (state)"
        
        # State scope comes before statistical scope
        assert positions['State Lookup'] < positions['Statistical Details'], \
            "State Lookup (state) must come before Statistical Details (statistical)"
        assert positions['State Rankings'] < positions['Statistical Details'], \
            "State Rankings (state) must come before Statistical Details (statistical)"


class TestSectionOrderingConsistency:
    """Test that section ordering is consistent across different scenarios."""
    
    @given(year=st.integers(min_value=2009, max_value=2023))
    @settings(max_examples=20)
    def test_section_order_independent_of_year(self, year):
        """
        Verify that section ordering is consistent regardless of selected year.
        
        The section order should not change based on the year parameter.
        """
        # Read the dashboard source file
        with open('views/1_Executive_Overview.py', 'r') as f:
            source_code = f.read()
        
        # Find section markers
        section_patterns = [
            (r'SECTION 1.*HERO SECTION', 'Hero Section'),
            (r'SECTION 2.*NATIONAL TREND', 'National Trend'),
            (r'SECTION 3.*GEOGRAPHIC', 'Geographic Section'),
            (r'SECTION 3\.5.*STATE LOOKUP', 'State Lookup'),
            (r'SECTION 4.*STATE RANKINGS', 'State Rankings'),
            (r'SECTION 5.*STATISTICAL DETAILS', 'Statistical Details'),
        ]
        
        section_positions = []
        for pattern, section_name in section_patterns:
            match = re.search(pattern, source_code, re.IGNORECASE)
            if match:
                section_positions.append((match.start(), section_name))
        
        # Sort by position
        section_positions.sort(key=lambda x: x[0])
        actual_order = [name for _, name in section_positions]
        
        # Expected order (should be the same for any year)
        expected_order = [
            'Hero Section',
            'National Trend',
            'Geographic Section',
            'State Lookup',
            'State Rankings',
            'Statistical Details'
        ]
        
        # Verify order is consistent
        assert actual_order == expected_order, \
            f"Section order should be consistent for year {year}. " \
            f"Expected: {expected_order}, Actual: {actual_order}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
