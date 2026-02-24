# Touch Target Sizing Implementation

## Overview

This document describes the implementation of touch target sizing for mobile devices in `utils/components.py`, fulfilling Requirements 10.1 and 10.2 from the executive-overview-redesign spec.

## Requirements

**Requirement 10.1:** All interactive elements SHALL have minimum dimensions of 44x44 pixels on mobile viewports (<768px)

**Requirement 10.2:** All adjacent interactive elements SHALL have minimum spacing of 8 pixels on mobile viewports (<768px)

## Implementation Details

### 1. Touch Target CSS Utilities

Added comprehensive CSS utilities at the top of `utils/components.py`:

```python
TOUCH_TARGET_CSS = """
<style>
/* Touch target sizing for mobile devices */
@media (max-width: 767px) {
    /* Ensure all interactive elements have minimum 44x44px touch targets */
    .touch-target,
    button:not(.no-touch-target),
    a:not(.no-touch-target),
    [role="button"]:not(.no-touch-target),
    [onclick]:not(.no-touch-target) {
        min-width: 44px !important;
        min-height: 44px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    /* Spacing between adjacent touch targets */
    .touch-target + .touch-target,
    button + button,
    a + a,
    button + a,
    a + button {
        margin-left: 8px !important;
    }
    
    /* Vertical spacing for stacked touch targets */
    .touch-target-stack > .touch-target,
    .touch-target-stack > button,
    .touch-target-stack > a {
        margin-bottom: 8px !important;
    }
}
</style>
"""
```

### 2. Helper Functions

**`inject_touch_target_css()`**
- Injects touch target CSS into the page
- Should be called once at the top of the main dashboard

**`ensure_touch_target(element_html, add_spacing=False)`**
- Wraps interactive elements with touch target classes
- Optionally adds spacing for adjacent elements

### 3. Component Updates

#### Quick Tips Callout
- Dismiss button has 44x44px touch target on mobile
- 8px spacing from content edges on mobile
- Media query ensures sizing only applies on mobile (<768px)

```css
@media (max-width: 767px) {
    .quick-tips-dismiss {
        min-width: 44px;
        min-height: 44px;
        top: 8px;
        right: 8px;
    }
}
```

#### Tooltip Wrapper
- Mobile info icon has 44x44px touch target
- Modal close button has 44x44px touch target
- 8px spacing between icon and adjacent elements
- Media queries ensure proper mobile-only application

```css
@media (max-width: 767px) {
    .tooltip-icon-mobile {
        display: inline-flex;
        min-width: 44px;
        min-height: 44px;
    }
    
    .tooltip-content-wrapper {
        gap: 8px;
    }
    
    .tooltip-modal-close {
        min-width: 44px;
        min-height: 44px;
    }
}
```

#### Streamlit Native Components
The following components use Streamlit's native widgets, which handle touch targets automatically:
- `state_lookup_component` (uses `st.selectbox`)
- `collapsible_section` (uses `st.expander`)
- `llm_explainer_ui` (uses `st.button`)

## Verification

### Manual Testing
1. Open the demo: `streamlit run demo_touch_target_sizing.py`
2. Open browser DevTools (F12)
3. Enable device toolbar (Ctrl+Shift+M or Cmd+Shift+M)
4. Select a mobile device (e.g., iPhone 12 Pro, 375x667)
5. Inspect interactive elements to verify:
   - `min-width: 44px`
   - `min-height: 44px`
   - `margin-left: 8px` (for adjacent elements)

### Automated Testing
Run existing component tests to ensure no regressions:
```bash
python -m pytest test_tooltip_wrapper.py -v
python -m pytest test_quick_tips_callout.py -v
python -m pytest test_collapsible_section.py -v
python -m pytest test_hero_section.py -v
```

All tests pass ✅

## Coverage

### Interactive Elements with Touch Target Sizing

| Component | Element | Touch Target | Spacing | Status |
|-----------|---------|--------------|---------|--------|
| quick_tips_callout | Dismiss button | 44x44px | 8px from edges | ✅ |
| tooltip_wrapper | Mobile info icon | 44x44px | 8px gap | ✅ |
| tooltip_wrapper | Modal close button | 44x44px | N/A | ✅ |
| state_lookup_component | Selectbox | Native | Native | ✅ |
| collapsible_section | Expander header | Native | Native | ✅ |
| llm_explainer_ui | Button | Native | Native | ✅ |

### Media Query Breakpoints

- **Mobile:** `max-width: 767px` - Touch target sizing applied
- **Tablet:** `768px - 1024px` - Default sizing
- **Desktop:** `> 1024px` - Default sizing

## Best Practices

1. **Use Media Queries:** Always wrap touch target sizing in `@media (max-width: 767px)` to ensure it only applies on mobile

2. **Minimum Dimensions:** All interactive elements should have `min-width: 44px` and `min-height: 44px`

3. **Spacing:** Adjacent interactive elements should have at least 8px spacing (use `gap`, `margin-left`, or `margin-bottom`)

4. **Flexbox Alignment:** Use `display: inline-flex`, `align-items: center`, and `justify-content: center` to ensure content is properly centered within the touch target

5. **Opt-out Class:** Use `.no-touch-target` class to exclude specific elements from automatic touch target sizing if needed

## Future Enhancements

1. Add touch feedback animations (scale, color change) within 100ms (Requirement 10.3)
2. Implement debouncing for rapid taps (300ms threshold) (Requirement 10.5)
3. Add visual touch target indicators for debugging (dev mode only)

## References

- [WCAG 2.1 Success Criterion 2.5.5: Target Size](https://www.w3.org/WAI/WCAG21/Understanding/target-size.html)
- [Apple Human Interface Guidelines: Touch Targets](https://developer.apple.com/design/human-interface-guidelines/ios/visual-design/adaptivity-and-layout/)
- [Material Design: Touch Targets](https://material.io/design/usability/accessibility.html#layout-and-typography)

## Task Status

- [x] Task 7.3: Implement touch target sizing for mobile in utils/components.py
- [ ] Task 7.4: Write property test for touch target sizing (next task)
