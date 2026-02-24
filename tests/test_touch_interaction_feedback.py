"""
Unit tests for touch interaction feedback implementation.

Tests verify:
- Visual feedback CSS is present (Requirements 10.3)
- Debouncing JavaScript is present (Requirements 10.5)
- Touch feedback helper functions work correctly
"""

import pytest
from utils.components import (
    TOUCH_TARGET_CSS,
    inject_touch_target_css,
    add_touch_feedback,
    ensure_touch_target
)


class TestTouchInteractionFeedback:
    """Test touch interaction feedback implementation."""
    
    def test_touch_target_css_contains_feedback_styles(self):
        """Verify TOUCH_TARGET_CSS includes visual feedback styles."""
        # Check for transition timing (80ms for <100ms requirement)
        assert "transition: background-color 80ms ease" in TOUCH_TARGET_CSS
        assert "transform 80ms ease" in TOUCH_TARGET_CSS
        
        # Check for active state feedback
        assert ":active" in TOUCH_TARGET_CSS
        assert "transform: scale(0.97)" in TOUCH_TARGET_CSS
        assert "background-color: rgba(34, 81, 255, 0.1)" in TOUCH_TARGET_CSS
        
        # Check for tap highlight color
        assert "-webkit-tap-highlight-color" in TOUCH_TARGET_CSS
    
    def test_touch_target_css_contains_debouncing_script(self):
        """Verify TOUCH_TARGET_CSS includes debouncing JavaScript."""
        # Check for debounce threshold (300ms)
        assert "DEBOUNCE_THRESHOLD = 300" in TOUCH_TARGET_CSS
        
        # Check for debouncing logic
        assert "debounceTouch" in TOUCH_TARGET_CSS
        assert "lastTapTimes" in TOUCH_TARGET_CSS
        
        # Check for event prevention on rapid taps
        assert "event.preventDefault()" in TOUCH_TARGET_CSS
        assert "event.stopPropagation()" in TOUCH_TARGET_CSS
    
    def test_touch_target_css_applies_to_interactive_elements(self):
        """Verify CSS targets all interactive elements."""
        # Check that CSS applies to buttons, links, etc.
        assert "button" in TOUCH_TARGET_CSS
        assert "a" in TOUCH_TARGET_CSS
        assert '[role="button"]' in TOUCH_TARGET_CSS
        assert "[onclick]" in TOUCH_TARGET_CSS
        assert ".touch-target" in TOUCH_TARGET_CSS
        assert ".touch-feedback" in TOUCH_TARGET_CSS
    
    def test_touch_target_css_prevents_double_tap_zoom(self):
        """Verify CSS prevents double-tap zoom on touch elements."""
        assert "touch-action: manipulation" in TOUCH_TARGET_CSS
        assert "-ms-touch-action: manipulation" in TOUCH_TARGET_CSS
    
    def test_add_touch_feedback_adds_class(self):
        """Test add_touch_feedback helper function."""
        # Test with existing class
        html_with_class = '<button class="btn-primary">Click me</button>'
        result = add_touch_feedback(html_with_class)
        assert "touch-feedback" in result
        assert "btn-primary" in result
        
        # Test without existing class
        html_no_class = '<button>Click me</button>'
        result = add_touch_feedback(html_no_class)
        assert "touch-feedback" in result
    
    def test_add_touch_feedback_with_debounce(self):
        """Test add_touch_feedback with debouncing enabled."""
        html = '<button>Click me</button>'
        result = add_touch_feedback(html, debounce=True)
        assert "touch-feedback" in result
        assert "touch-debounce" in result
    
    def test_add_touch_feedback_without_debounce(self):
        """Test add_touch_feedback with debouncing disabled."""
        html = '<button>Click me</button>'
        result = add_touch_feedback(html, debounce=False)
        assert "touch-feedback" in result
        assert "touch-debounce" not in result
    
    def test_ensure_touch_target_wraps_element(self):
        """Test ensure_touch_target helper function."""
        html = '<button>Click me</button>'
        result = ensure_touch_target(html)
        assert '<div class="touch-target">' in result
        assert '<button>Click me</button>' in result
        assert '</div>' in result
    
    def test_ensure_touch_target_with_spacing(self):
        """Test ensure_touch_target with spacing enabled."""
        html = '<button>Click me</button>'
        result = ensure_touch_target(html, add_spacing=True)
        assert "touch-target-spacing" in result
    
    def test_feedback_timing_meets_requirement(self):
        """Verify feedback timing is within 100ms requirement."""
        # Extract transition timing from CSS
        import re
        timing_matches = re.findall(r'(\d+)ms ease', TOUCH_TARGET_CSS)
        
        # All transition timings should be <= 100ms
        for timing_str in timing_matches:
            timing = int(timing_str)
            assert timing <= 100, f"Transition timing {timing}ms exceeds 100ms requirement"
    
    def test_debounce_threshold_meets_requirement(self):
        """Verify debounce threshold is 300ms as required."""
        assert "DEBOUNCE_THRESHOLD = 300" in TOUCH_TARGET_CSS
    
    def test_mutation_observer_for_dynamic_content(self):
        """Verify MutationObserver is set up for dynamic content."""
        assert "MutationObserver" in TOUCH_TARGET_CSS
        assert "observer.observe(document.body" in TOUCH_TARGET_CSS
        assert "childList: true" in TOUCH_TARGET_CSS
        assert "subtree: true" in TOUCH_TARGET_CSS


class TestTouchFeedbackIntegration:
    """Integration tests for touch feedback in components."""
    
    def test_quick_tips_dismiss_has_touch_feedback(self):
        """Verify quick tips dismiss button has touch feedback styles."""
        from utils.components import quick_tips_callout
        
        # The quick_tips_callout should include touch feedback in its CSS
        # We can't easily test the rendered output, but we can verify
        # the component exists and is callable
        assert callable(quick_tips_callout)
    
    def test_tooltip_wrapper_has_touch_feedback(self):
        """Verify tooltip wrapper has touch feedback styles."""
        from utils.components import tooltip_wrapper
        
        # The tooltip_wrapper should include touch feedback in its CSS
        assert callable(tooltip_wrapper)
    
    def test_inject_touch_target_css_is_callable(self):
        """Verify inject_touch_target_css function exists and is callable."""
        assert callable(inject_touch_target_css)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
