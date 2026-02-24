"""
Demo script to verify touch target sizing implementation.

This script demonstrates that all interactive elements in utils/components.py
have proper touch target sizing (44x44px minimum) and spacing (8px minimum)
on mobile viewports (<768px).

Requirements validated: 10.1, 10.2
"""

from utils.components import (
    inject_touch_target_css,
    quick_tips_callout,
    tooltip_wrapper,
    hero_section,
    state_lookup_component,
    collapsible_section
)
import streamlit as st


def main():
    st.set_page_config(page_title="Touch Target Sizing Demo", layout="wide")
    
    st.title("Touch Target Sizing Demo")
    st.markdown("""
    This demo shows that all interactive elements have proper touch target sizing on mobile.
    
    **Requirements:**
    - 10.1: All touch targets have minimum 44x44px dimensions on mobile (<768px)
    - 10.2: Minimum 8px spacing between adjacent touch targets on mobile
    
    **To test:**
    1. Open browser DevTools (F12)
    2. Toggle device toolbar (Ctrl+Shift+M or Cmd+Shift+M)
    3. Select a mobile device (e.g., iPhone 12 Pro)
    4. Inspect interactive elements to verify touch target sizing
    """)
    
    # Inject touch target CSS
    inject_touch_target_css()
    
    st.markdown("---")
    
    # Demo 1: Quick Tips Callout
    st.header("1. Quick Tips Callout")
    st.markdown("**Interactive element:** Dismiss button (X)")
    st.markdown("**Expected:** 44x44px touch target on mobile, 8px spacing from edges")
    
    tips = [
        "This is tip number one",
        "This is tip number two",
        "This is tip number three"
    ]
    quick_tips_callout(tips, dismissible=True)
    
    st.markdown("---")
    
    # Demo 2: Tooltip Wrapper
    st.header("2. Tooltip Wrapper")
    st.markdown("**Interactive elements:** Info icon (mobile), close button (modal)")
    st.markdown("**Expected:** 44x44px touch targets on mobile, 8px spacing")
    
    tooltip_wrapper(
        content="Hover or tap for help",
        tooltip_text="This is helpful information about the content. On mobile, tap the info icon to see this message.",
        icon="info-circle",
        position="top"
    )
    
    st.markdown("---")
    
    # Demo 3: Hero Section with Quick Tips
    st.header("3. Hero Section")
    st.markdown("**Interactive element:** Quick tips dismiss button")
    st.markdown("**Expected:** 44x44px touch target on mobile")
    
    hero_section(
        year=2023,
        primary_metric=0.125,
        previous_metric=0.118,
        context_summary="Food insecurity remains a significant challenge across the nation.",
        show_quick_tips=True
    )
    
    st.markdown("---")
    
    # Demo 4: Multiple Interactive Elements
    st.header("4. Multiple Adjacent Interactive Elements")
    st.markdown("**Expected:** 8px spacing between adjacent touch targets on mobile")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        tooltip_wrapper(
            content="Element 1",
            tooltip_text="First tooltip",
            icon="info-circle"
        )
    
    with col2:
        tooltip_wrapper(
            content="Element 2",
            tooltip_text="Second tooltip",
            icon="question-circle"
        )
    
    with col3:
        tooltip_wrapper(
            content="Element 3",
            tooltip_text="Third tooltip",
            icon="exclamation-circle"
        )
    
    st.markdown("---")
    
    # Demo 5: Collapsible Section (Streamlit native)
    st.header("5. Collapsible Section")
    st.markdown("**Interactive element:** Expander header (Streamlit native)")
    st.markdown("**Expected:** Streamlit handles touch targets automatically")
    
    def sample_content():
        st.write("This is collapsible content.")
        st.write("Streamlit's native expander component handles touch targets.")
    
    collapsible_section(
        title="Sample Collapsible Section",
        content_func=sample_content,
        icon="chart-bar",
        default_expanded=True,
        key="demo_collapsible"
    )
    
    st.markdown("---")
    
    # Verification Instructions
    st.header("Verification Instructions")
    st.markdown("""
    ### How to Verify Touch Target Sizing:
    
    1. **Open DevTools:**
       - Chrome/Edge: F12 or Ctrl+Shift+I (Cmd+Option+I on Mac)
       - Firefox: F12 or Ctrl+Shift+I (Cmd+Option+I on Mac)
    
    2. **Enable Device Toolbar:**
       - Chrome/Edge: Ctrl+Shift+M (Cmd+Shift+M on Mac)
       - Firefox: Ctrl+Shift+M (Cmd+Option+M on Mac)
    
    3. **Select Mobile Device:**
       - Choose "iPhone 12 Pro" or "Pixel 5" from the device dropdown
       - Or set custom dimensions: 375x667 (iPhone SE)
    
    4. **Inspect Elements:**
       - Right-click on interactive elements (buttons, icons)
       - Select "Inspect" or "Inspect Element"
       - Check the Computed styles panel for:
         - `min-width: 44px`
         - `min-height: 44px`
         - `margin-left: 8px` (for adjacent elements)
    
    5. **Verify Media Query:**
       - In DevTools, look for `@media (max-width: 767px)` rules
       - Verify touch target styles are applied only on mobile
    
    ### Expected Results:
    
    - ✅ All buttons and interactive icons have 44x44px minimum size on mobile
    - ✅ Adjacent interactive elements have 8px spacing on mobile
    - ✅ Touch target styles only apply on viewports < 768px
    - ✅ Desktop viewports (>768px) use default sizing
    """)


if __name__ == "__main__":
    main()
