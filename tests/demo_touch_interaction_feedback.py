"""
Demo: Touch Interaction Feedback

This demo showcases the touch interaction feedback implementation:
- Visual feedback (color change and scale animation) within 100ms
- Debouncing for rapid taps (300ms threshold)

Requirements: 10.3, 10.5
"""

import streamlit as st
from utils.components import (
    inject_touch_target_css,
    add_touch_feedback,
    ensure_touch_target,
    quick_tips_callout,
    tooltip_wrapper,
    section_header
)

# Page config
st.set_page_config(
    page_title="Touch Interaction Feedback Demo",
    page_icon="👆",
    layout="wide"
)

# Inject touch target CSS (includes feedback styles and debouncing)
inject_touch_target_css()

# Title
st.title("👆 Touch Interaction Feedback Demo")

st.markdown("""
This demo showcases the touch interaction feedback implementation for mobile devices.

**Features:**
- ✨ Visual feedback within 100ms (color change + scale animation)
- 🚫 Debouncing for rapid taps (300ms threshold)
- 📱 Touch-friendly sizing (44x44px minimum)
- 🎯 Proper spacing between elements (8px minimum)
""")

# Section 1: Basic Touch Feedback
section_header("Basic Touch Feedback", "Tap any button to see visual feedback", "hand-pointer")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Standard Button")
    if st.button("Tap Me!", key="btn1"):
        st.success("Button tapped!")
    st.caption("Native Streamlit button with automatic touch feedback")

with col2:
    st.markdown("### Custom HTML Button")
    button_html = """
    <button class="touch-feedback" style="
        padding: 0.75rem 1.5rem;
        background: #2251FF;
        color: white;
        border: none;
        border-radius: 0.5rem;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        min-width: 44px;
        min-height: 44px;
    " onclick="alert('Custom button tapped!')">
        Custom Button
    </button>
    """
    st.markdown(button_html, unsafe_allow_html=True)
    st.caption("Custom HTML button with touch-feedback class")

with col3:
    st.markdown("### Link with Feedback")
    link_html = """
    <a href="#" class="touch-feedback" style="
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 0.75rem 1.5rem;
        background: #00B894;
        color: white;
        text-decoration: none;
        border-radius: 0.5rem;
        font-size: 1rem;
        font-weight: 600;
        min-width: 44px;
        min-height: 44px;
    " onclick="event.preventDefault(); alert('Link tapped!')">
        Tap Link
    </a>
    """
    st.markdown(link_html, unsafe_allow_html=True)
    st.caption("Link styled as button with touch feedback")

st.divider()

# Section 2: Debouncing Demo
section_header("Debouncing Demo", "Try tapping rapidly - only one action per 300ms", "stopwatch")

st.markdown("""
**Test the debouncing:**
1. Tap the button below rapidly multiple times
2. Notice that only one action is registered per 300ms
3. This prevents accidental double-taps and multiple submissions
""")

# Counter to track taps
if "tap_count" not in st.session_state:
    st.session_state.tap_count = 0

col1, col2 = st.columns([1, 2])

with col1:
    if st.button("Tap Rapidly!", key="debounce_btn", type="primary"):
        st.session_state.tap_count += 1
    
    st.metric("Tap Count", st.session_state.tap_count)
    
    if st.button("Reset Counter", key="reset_btn"):
        st.session_state.tap_count = 0
        st.rerun()

with col2:
    st.info("""
    **How debouncing works:**
    
    - Each tap is timestamped
    - If a tap occurs within 300ms of the previous tap, it's ignored
    - This prevents rapid successive taps from triggering multiple actions
    - The visual feedback still appears, but the action is debounced
    
    **Note:** Streamlit's button component has its own state management,
    so the debouncing is most effective with custom HTML buttons and links.
    """)

st.divider()

# Section 3: Component Integration
section_header("Component Integration", "Touch feedback in custom components", "puzzle-piece")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Quick Tips Callout")
    st.markdown("The dismiss button has touch feedback:")
    quick_tips_callout([
        "Tap the ✕ button to dismiss",
        "Notice the visual feedback on tap",
        "The button is 44x44px for easy tapping"
    ])

with col2:
    st.markdown("### Tooltip Wrapper")
    st.markdown("The info icon has touch feedback:")
    tooltip_wrapper(
        content="Hover or tap for help",
        tooltip_text="This tooltip has touch-friendly interaction with visual feedback on tap.",
        icon="info-circle",
        position="top"
    )

st.divider()

# Section 4: Technical Details
section_header("Technical Implementation", "How it works under the hood", "code")

with st.expander("View CSS Implementation"):
    st.code("""
/* Touch interaction feedback - Requirements 10.3, 10.5 */
/* Visual feedback within 100ms for all interactive elements */
.touch-feedback,
button,
a,
[role="button"],
[onclick],
.touch-target {
    transition: background-color 80ms ease, transform 80ms ease, opacity 80ms ease !important;
    -webkit-tap-highlight-color: rgba(34, 81, 255, 0.15);
}

/* Active state feedback - color change and scale animation */
.touch-feedback:active,
button:active,
a:active,
[role="button"]:active,
[onclick]:active,
.touch-target:active {
    transform: scale(0.97) !important;
    background-color: rgba(34, 81, 255, 0.1) !important;
    opacity: 0.9 !important;
}

/* Prevent double-tap zoom on touch elements */
.touch-feedback,
button,
a,
[role="button"],
[onclick],
.touch-target {
    touch-action: manipulation;
    -ms-touch-action: manipulation;
}
    """, language="css")

with st.expander("View JavaScript Debouncing Implementation"):
    st.code("""
// Debouncing for rapid taps - Requirement 10.5
// Prevents multiple actions within 300ms threshold
(function() {
    const DEBOUNCE_THRESHOLD = 300; // milliseconds
    const lastTapTimes = new Map();
    
    function debounceTouch(element, callback) {
        const now = Date.now();
        const elementId = element.id || element.className || 'default';
        const lastTap = lastTapTimes.get(elementId) || 0;
        
        if (now - lastTap < DEBOUNCE_THRESHOLD) {
            // Rapid tap detected - ignore
            return false;
        }
        
        // Update last tap time
        lastTapTimes.set(elementId, now);
        
        // Execute callback
        if (callback) {
            callback();
        }
        
        return true;
    }
    
    // Apply debouncing to all interactive elements
    function applyDebouncing() {
        const interactiveElements = document.querySelectorAll(
            'button, a, [role="button"], [onclick], .touch-target, .touch-feedback'
        );
        
        interactiveElements.forEach(element => {
            // Skip if already debounced
            if (element.dataset.debounced === 'true') {
                return;
            }
            
            // Store original onclick handler
            const originalOnClick = element.onclick;
            
            // Wrap onclick with debouncing
            element.onclick = function(event) {
                const allowed = debounceTouch(element, null);
                
                if (!allowed) {
                    event.preventDefault();
                    event.stopPropagation();
                    return false;
                }
                
                // Call original handler if exists
                if (originalOnClick) {
                    return originalOnClick.call(this, event);
                }
            };
            
            // Mark as debounced
            element.dataset.debounced = 'true';
        });
    }
    
    // Apply on load and re-apply for dynamic content
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', applyDebouncing);
    } else {
        applyDebouncing();
    }
    
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length > 0) {
                applyDebouncing();
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
})();
    """, language="javascript")

st.divider()

# Footer
st.markdown("""
---
**Requirements Validated:**
- ✅ **10.3**: Visual feedback (color change or scale animation) within 100ms of touch interaction
- ✅ **10.5**: Debouncing prevents accidental interactions by ignoring rapid successive taps within 300ms

**Testing:**
- Best tested on actual mobile devices or using browser DevTools mobile emulation
- Use Chrome DevTools → Toggle device toolbar → Select a mobile device
- Enable "Show touch events" in DevTools settings for visual feedback
""")
