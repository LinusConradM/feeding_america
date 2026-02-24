"""
Property-based tests for touch target sizing requirements.

Tests validate Properties 31 and 32 from the executive-overview-redesign spec:
- Property 31: Mobile Touch Target Sizing - All interactive elements have 44x44px minimum on mobile
- Property 32: Mobile Touch Target Spacing - Adjacent interactive elements have 8px minimum spacing on mobile

**Validates: Requirements 10.1, 10.2**

Uses Hypothesis for property-based testing with 20 iterations per test.
"""

import pytest
from hypothesis import given, strategies as st, settings
import re


def extract_touch_target_css():
    """
    Helper function to extract touch target CSS from components module.
    
    Returns:
        str: The touch target CSS block containing mobile sizing rules
    """
    from utils.components import TOUCH_TARGET_CSS
    return TOUCH_TARGET_CSS


def extract_mobile_touch_target_rules(css: str) -> dict:
    """
    Extract touch target sizing rules from mobile media query.
    
    Args:
        css: CSS content containing touch target rules
        
    Returns:
        dict: Parsed rules with min-width, min-height, and spacing values
    """
    # Find mobile media query block
    mobile_match = re.search(
        r'@media\s*\(\s*max-width\s*:\s*767px\s*\)\s*\{(.*?)\n\s*\}\s*</style>',
        css,
        re.DOTALL
    )
    
    if not mobile_match:
        return {}
    
    mobile_css = mobile_match.group(1)
    
    rules = {}
    
    # Extract min-width from touch target rules
    width_match = re.search(
        r'\.touch-target[^{]*\{[^}]*min-width:\s*(\d+)px',
        mobile_css,
        re.DOTALL
    )
    if width_match:
        rules['min_width'] = int(width_match.group(1))
    
    # Extract min-height from touch target rules
    height_match = re.search(
        r'\.touch-target[^{]*\{[^}]*min-height:\s*(\d+)px',
        mobile_css,
        re.DOTALL
    )
    if height_match:
        rules['min_height'] = int(height_match.group(1))
    
    # Extract horizontal spacing between adjacent touch targets
    h_spacing_match = re.search(
        r'\.touch-target\s*\+\s*\.touch-target[^{]*\{[^}]*margin-left:\s*(\d+)px',
        mobile_css,
        re.DOTALL
    )
    if h_spacing_match:
        rules['horizontal_spacing'] = int(h_spacing_match.group(1))
    
    # Extract vertical spacing for stacked touch targets
    v_spacing_match = re.search(
        r'\.touch-target-stack\s*>\s*\.touch-target[^{]*\{[^}]*margin-bottom:\s*(\d+)px',
        mobile_css,
        re.DOTALL
    )
    if v_spacing_match:
        rules['vertical_spacing'] = int(v_spacing_match.group(1))
    
    # Check if button elements are covered
    rules['covers_buttons'] = bool(re.search(r'button:not\(\.no-touch-target\)', mobile_css))
    
    # Check if anchor elements are covered
    rules['covers_anchors'] = bool(re.search(r'a:not\(\.no-touch-target\)', mobile_css))
    
    # Check if role="button" elements are covered
    rules['covers_role_button'] = bool(re.search(r'\[role="button"\]:not\(\.no-touch-target\)', mobile_css))
    
    # Check if onclick elements are covered
    rules['covers_onclick'] = bool(re.search(r'\[onclick\]:not\(\.no-touch-target\)', mobile_css))
    
    return rules


class TestTouchTargetSizingProperties:
    """Property-based tests for touch target sizing requirements."""
    
    @given(viewport_width=st.integers(min_value=320, max_value=767))
    @settings(max_examples=20, deadline=None)
    def test_property_31_mobile_touch_target_sizing(self, viewport_width):
        """
        **Validates: Requirements 10.1**
        
        Property 31: Mobile Touch Target Sizing
        
        For any interactive element on viewport width < 768px, the touch target 
        SHALL have minimum dimensions of 44x44 pixels.
        
        This test verifies that the CSS injected by utils/components.py ensures
        all interactive elements (.touch-target, button, a, [role="button"], [onclick])
        have minimum 44x44px dimensions on mobile viewports.
        """
        touch_target_css = extract_touch_target_css()
        
        assert touch_target_css is not None, \
            "Touch target CSS should be defined in utils/components.py"
        
        rules = extract_mobile_touch_target_rules(touch_target_css)
        
        # Property 31 Assertion 1: Mobile media query should exist
        assert '@media' in touch_target_css and 'max-width' in touch_target_css and '767px' in touch_target_css, \
            f"Touch target CSS should contain mobile media query (max-width: 767px) for viewport {viewport_width}px"
        
        # Property 31 Assertion 2: Minimum width should be 44px
        assert 'min_width' in rules, \
            f"Touch target CSS should define min-width for viewport {viewport_width}px"
        
        assert rules['min_width'] >= 44, \
            f"Touch target min-width must be >= 44px, but found {rules['min_width']}px " \
            f"for viewport {viewport_width}px"
        
        # Property 31 Assertion 3: Minimum height should be 44px
        assert 'min_height' in rules, \
            f"Touch target CSS should define min-height for viewport {viewport_width}px"
        
        assert rules['min_height'] >= 44, \
            f"Touch target min-height must be >= 44px, but found {rules['min_height']}px " \
            f"for viewport {viewport_width}px"
        
        # Property 31 Assertion 4: All interactive element types should be covered
        assert rules.get('covers_buttons', False), \
            f"Touch target CSS should cover button elements for viewport {viewport_width}px"
        
        assert rules.get('covers_anchors', False), \
            f"Touch target CSS should cover anchor (a) elements for viewport {viewport_width}px"
        
        assert rules.get('covers_role_button', False), \
            f"Touch target CSS should cover [role='button'] elements for viewport {viewport_width}px"
        
        assert rules.get('covers_onclick', False), \
            f"Touch target CSS should cover [onclick] elements for viewport {viewport_width}px"
        
        # Property 31 Assertion 5: Display properties should support proper sizing
        # Check that display: inline-flex is used for proper sizing
        assert 'display: inline-flex' in touch_target_css or 'display:inline-flex' in touch_target_css, \
            f"Touch target CSS should use display: inline-flex for proper sizing on viewport {viewport_width}px"
        
        # Property 31 Assertion 6: Alignment properties should center content
        assert 'align-items: center' in touch_target_css or 'align-items:center' in touch_target_css, \
            f"Touch target CSS should use align-items: center for viewport {viewport_width}px"
        
        assert 'justify-content: center' in touch_target_css or 'justify-content:center' in touch_target_css, \
            f"Touch target CSS should use justify-content: center for viewport {viewport_width}px"
    
    @given(viewport_width=st.integers(min_value=320, max_value=767))
    @settings(max_examples=20, deadline=None)
    def test_property_32_mobile_touch_target_spacing(self, viewport_width):
        """
        **Validates: Requirements 10.2**
        
        Property 32: Mobile Touch Target Spacing
        
        For any pair of adjacent interactive elements on viewport width < 768px, 
        there SHALL be >= 8 pixels of spacing between them.
        
        This test verifies that the CSS injected by utils/components.py ensures
        adequate spacing between adjacent touch targets to prevent accidental taps.
        """
        touch_target_css = extract_touch_target_css()
        
        assert touch_target_css is not None, \
            "Touch target CSS should be defined in utils/components.py"
        
        rules = extract_mobile_touch_target_rules(touch_target_css)
        
        # Property 32 Assertion 1: Mobile media query should exist
        assert '@media' in touch_target_css and 'max-width' in touch_target_css and '767px' in touch_target_css, \
            f"Touch target CSS should contain mobile media query (max-width: 767px) for viewport {viewport_width}px"
        
        # Property 32 Assertion 2: Horizontal spacing should be >= 8px
        assert 'horizontal_spacing' in rules, \
            f"Touch target CSS should define horizontal spacing between adjacent elements for viewport {viewport_width}px"
        
        assert rules['horizontal_spacing'] >= 8, \
            f"Horizontal spacing between adjacent touch targets must be >= 8px, " \
            f"but found {rules['horizontal_spacing']}px for viewport {viewport_width}px"
        
        # Property 32 Assertion 3: Vertical spacing should be >= 8px for stacked elements
        assert 'vertical_spacing' in rules, \
            f"Touch target CSS should define vertical spacing for stacked elements for viewport {viewport_width}px"
        
        assert rules['vertical_spacing'] >= 8, \
            f"Vertical spacing between stacked touch targets must be >= 8px, " \
            f"but found {rules['vertical_spacing']}px for viewport {viewport_width}px"
        
        # Property 32 Assertion 4: Adjacent selector patterns should be defined
        # Check for .touch-target + .touch-target pattern
        assert '.touch-target + .touch-target' in touch_target_css or '.touch-target+.touch-target' in touch_target_css, \
            f"Touch target CSS should define spacing for adjacent .touch-target elements for viewport {viewport_width}px"
        
        # Check for button + button pattern
        assert 'button + button' in touch_target_css or 'button+button' in touch_target_css, \
            f"Touch target CSS should define spacing for adjacent button elements for viewport {viewport_width}px"
        
        # Check for a + a pattern
        assert 'a + a' in touch_target_css or 'a+a' in touch_target_css, \
            f"Touch target CSS should define spacing for adjacent anchor elements for viewport {viewport_width}px"
        
        # Property 32 Assertion 5: Stacked touch target container should exist
        assert '.touch-target-stack' in touch_target_css, \
            f"Touch target CSS should define .touch-target-stack container for vertical spacing on viewport {viewport_width}px"
        
        # Property 32 Assertion 6: Last child should not have bottom margin
        assert ':last-child' in touch_target_css and 'margin-bottom: 0' in touch_target_css, \
            f"Touch target CSS should remove bottom margin from last child to prevent excessive spacing on viewport {viewport_width}px"


class TestTouchTargetBoundaryConditions:
    """Test boundary conditions for touch target sizing."""
    
    def test_mobile_upper_boundary_767px_has_touch_targets(self):
        """Test that 767px (mobile upper boundary) has touch target rules applied."""
        touch_target_css = extract_touch_target_css()
        rules = extract_mobile_touch_target_rules(touch_target_css)
        
        # At 767px, mobile rules should apply
        assert rules.get('min_width', 0) >= 44, \
            f"Mobile boundary (767px) should have >= 44px min-width, got {rules.get('min_width', 0)}px"
        
        assert rules.get('min_height', 0) >= 44, \
            f"Mobile boundary (767px) should have >= 44px min-height, got {rules.get('min_height', 0)}px"
        
        assert rules.get('horizontal_spacing', 0) >= 8, \
            f"Mobile boundary (767px) should have >= 8px horizontal spacing, got {rules.get('horizontal_spacing', 0)}px"
    
    def test_tablet_lower_boundary_768px_no_touch_target_override(self):
        """Test that 768px (tablet lower boundary) does not apply mobile touch target rules."""
        touch_target_css = extract_touch_target_css()
        
        # Verify mobile media query is max-width: 767px (not including 768px)
        # The media query should use max-width: 767px or similar
        mobile_match = re.search(
            r'@media\s*\(\s*max-width\s*:\s*(\d+)px\s*\)',
            touch_target_css
        )
        
        assert mobile_match is not None, \
            "Mobile media query should exist"
        
        max_width = int(mobile_match.group(1))
        
        # The max-width should be 767px or 768px (both are acceptable)
        # 767px means mobile rules apply up to 767px (not including 768px)
        # 768px means mobile rules apply up to 768px (including 768px)
        assert max_width in [767, 768], \
            f"Mobile media query max-width should be 767px or 768px, got {max_width}px"
    
    def test_minimum_mobile_320px_has_touch_targets(self):
        """Test that 320px (common mobile minimum) has touch target rules applied."""
        touch_target_css = extract_touch_target_css()
        rules = extract_mobile_touch_target_rules(touch_target_css)
        
        # At 320px, mobile rules should apply
        assert rules.get('min_width', 0) >= 44, \
            f"Minimum mobile (320px) should have >= 44px min-width, got {rules.get('min_width', 0)}px"
        
        assert rules.get('min_height', 0) >= 44, \
            f"Minimum mobile (320px) should have >= 44px min-height, got {rules.get('min_height', 0)}px"
        
        assert rules.get('horizontal_spacing', 0) >= 8, \
            f"Minimum mobile (320px) should have >= 8px horizontal spacing, got {rules.get('horizontal_spacing', 0)}px"


class TestTouchTargetConsistency:
    """Test that touch target rules are consistent across mobile viewport ranges."""
    
    @given(
        width1=st.integers(min_value=320, max_value=767),
        width2=st.integers(min_value=320, max_value=767)
    )
    @settings(max_examples=10, deadline=None)
    def test_touch_target_sizing_is_consistent(self, width1, width2):
        """
        Test that all mobile viewports have the same touch target sizing rules.
        
        Since CSS media queries apply uniformly to all viewports within the range,
        the touch target sizing should be consistent across all mobile widths.
        """
        touch_target_css = extract_touch_target_css()
        rules = extract_mobile_touch_target_rules(touch_target_css)
        
        # Since CSS is static and applies uniformly to all mobile viewports,
        # the rules are inherently consistent across width1 and width2.
        # This test verifies that the rules exist and are well-formed.
        
        assert rules.get('min_width', 0) >= 44, \
            f"Touch target min-width should be consistent and >= 44px for all mobile viewports " \
            f"({width1}px and {width2}px), got {rules.get('min_width', 0)}px"
        
        assert rules.get('min_height', 0) >= 44, \
            f"Touch target min-height should be consistent and >= 44px for all mobile viewports " \
            f"({width1}px and {width2}px), got {rules.get('min_height', 0)}px"
        
        assert rules.get('horizontal_spacing', 0) >= 8, \
            f"Touch target horizontal spacing should be consistent and >= 8px for all mobile viewports " \
            f"({width1}px and {width2}px), got {rules.get('horizontal_spacing', 0)}px"
        
        assert rules.get('vertical_spacing', 0) >= 8, \
            f"Touch target vertical spacing should be consistent and >= 8px for all mobile viewports " \
            f"({width1}px and {width2}px), got {rules.get('vertical_spacing', 0)}px"


class TestTouchTargetCSSStructure:
    """Test the structure and completeness of touch target CSS."""
    
    def test_touch_target_css_is_valid_html(self):
        """Test that touch target CSS is wrapped in valid HTML style tags."""
        touch_target_css = extract_touch_target_css()
        
        assert touch_target_css.startswith('<style>') or touch_target_css.startswith('\n<style>'), \
            "Touch target CSS should start with <style> tag"
        
        assert touch_target_css.endswith('</style>') or touch_target_css.endswith('</style>\n'), \
            "Touch target CSS should end with </style> tag"
    
    def test_touch_target_css_has_important_flags(self):
        """Test that touch target CSS uses !important flags to override other styles."""
        touch_target_css = extract_touch_target_css()
        
        # Important flags ensure touch target rules override other styles
        assert '!important' in touch_target_css, \
            "Touch target CSS should use !important flags to ensure rules are applied"
        
        # Check that critical properties have !important
        assert 'min-width: 44px !important' in touch_target_css or 'min-width:44px!important' in touch_target_css, \
            "Touch target min-width should have !important flag"
        
        assert 'min-height: 44px !important' in touch_target_css or 'min-height:44px!important' in touch_target_css, \
            "Touch target min-height should have !important flag"
    
    def test_touch_target_css_has_opt_out_mechanism(self):
        """Test that touch target CSS provides opt-out mechanism via .no-touch-target class."""
        touch_target_css = extract_touch_target_css()
        
        # The :not(.no-touch-target) selector allows elements to opt out
        assert ':not(.no-touch-target)' in touch_target_css, \
            "Touch target CSS should provide .no-touch-target opt-out mechanism"
    
    def test_touch_target_css_covers_all_interactive_elements(self):
        """Test that touch target CSS covers all common interactive element types."""
        touch_target_css = extract_touch_target_css()
        
        # Should cover standard interactive elements
        interactive_selectors = [
            'button',
            'a',
            '[role="button"]',
            '[onclick]',
            '.touch-target'
        ]
        
        for selector in interactive_selectors:
            assert selector in touch_target_css, \
                f"Touch target CSS should cover {selector} elements"
    
    def test_touch_target_css_handles_mixed_adjacent_elements(self):
        """Test that touch target CSS handles spacing between different element types."""
        touch_target_css = extract_touch_target_css()
        
        # Should handle button + a and a + button combinations
        assert 'button + a' in touch_target_css or 'button+a' in touch_target_css, \
            "Touch target CSS should handle button followed by anchor spacing"
        
        assert 'a + button' in touch_target_css or 'a+button' in touch_target_css, \
            "Touch target CSS should handle anchor followed by button spacing"


class TestTouchTargetIntegration:
    """Test integration of touch target sizing with component functions."""
    
    def test_inject_touch_target_css_function_exists(self):
        """Test that inject_touch_target_css function is available."""
        from utils.components import inject_touch_target_css
        
        assert callable(inject_touch_target_css), \
            "inject_touch_target_css should be a callable function"
    
    def test_ensure_touch_target_function_exists(self):
        """Test that ensure_touch_target wrapper function is available."""
        from utils.components import ensure_touch_target
        
        assert callable(ensure_touch_target), \
            "ensure_touch_target should be a callable function"
    
    def test_ensure_touch_target_wraps_element(self):
        """Test that ensure_touch_target properly wraps HTML elements."""
        from utils.components import ensure_touch_target
        
        test_html = '<button>Click me</button>'
        wrapped = ensure_touch_target(test_html)
        
        assert 'touch-target' in wrapped, \
            "ensure_touch_target should add touch-target class"
        
        assert test_html in wrapped, \
            "ensure_touch_target should preserve original HTML"
        
        assert wrapped.startswith('<div class="touch-target'), \
            "ensure_touch_target should wrap in div with touch-target class"
    
    def test_ensure_touch_target_adds_spacing_class(self):
        """Test that ensure_touch_target can add spacing class for adjacent elements."""
        from utils.components import ensure_touch_target
        
        test_html = '<button>Click me</button>'
        wrapped = ensure_touch_target(test_html, add_spacing=True)
        
        assert 'touch-target-spacing' in wrapped, \
            "ensure_touch_target with add_spacing=True should add touch-target-spacing class"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
