"""
Demo script for tooltip_wrapper component.

This script demonstrates the tooltip_wrapper component functionality:
- Desktop: CSS-only hover tooltip (200ms delay)
- Mobile: Tap icon to show tooltip in modal/popover
- Touch target: 44x44px minimum
- Dismissible on outside click
- Supports positioning (top, bottom, left, right)

Run with: streamlit run demo_tooltip_wrapper.py
"""

import streamlit as st
from utils.components import tooltip_wrapper, section_header

# Page config
st.set_page_config(
    page_title="Tooltip Wrapper Demo",
    page_icon="💡",
    layout="wide"
)

# Title
st.title("Tooltip Wrapper Component Demo")
st.markdown("---")

# Introduction
st.markdown("""
This demo showcases the `tooltip_wrapper` component with different configurations.

**Desktop behavior**: Hover over the content to see the tooltip (200ms delay)  
**Mobile behavior**: Tap the info icon to open a modal with the tooltip text
""")

st.markdown("---")

# Demo 1: Basic tooltip with default parameters
section_header("Basic Tooltip (Default)", icon="info-circle")
st.markdown("Hover over or tap the content below:")
tooltip_wrapper(
    content="National Food Insecurity Rate",
    tooltip_text="The percentage of households that lack consistent access to adequate food due to insufficient resources."
)

st.markdown("<br>", unsafe_allow_html=True)

# Demo 2: Different positions
section_header("Position Variations", icon="arrows-alt")
st.markdown("Tooltips can be positioned in different directions:")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("**Top Position**")
    tooltip_wrapper(
        content="Hover me (top)",
        tooltip_text="This tooltip appears above the content",
        position="top"
    )

with col2:
    st.markdown("**Bottom Position**")
    tooltip_wrapper(
        content="Hover me (bottom)",
        tooltip_text="This tooltip appears below the content",
        position="bottom"
    )

with col3:
    st.markdown("**Left Position**")
    tooltip_wrapper(
        content="Hover me (left)",
        tooltip_text="This tooltip appears to the left of the content",
        position="left"
    )

with col4:
    st.markdown("**Right Position**")
    tooltip_wrapper(
        content="Hover me (right)",
        tooltip_text="This tooltip appears to the right of the content",
        position="right"
    )

st.markdown("<br>", unsafe_allow_html=True)

# Demo 3: Different icons
section_header("Custom Icons", icon="icons")
st.markdown("Different icons can be used for the mobile tap target:")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Info Circle**")
    tooltip_wrapper(
        content="Info icon",
        tooltip_text="This uses the default info-circle icon",
        icon="info-circle"
    )

with col2:
    st.markdown("**Question Circle**")
    tooltip_wrapper(
        content="Question icon",
        tooltip_text="This uses a question-circle icon for help",
        icon="question-circle"
    )

with col3:
    st.markdown("**Lightbulb**")
    tooltip_wrapper(
        content="Tip icon",
        tooltip_text="This uses a lightbulb icon for tips and suggestions",
        icon="lightbulb"
    )

st.markdown("<br>", unsafe_allow_html=True)

# Demo 4: Real-world use cases
section_header("Real-World Examples", icon="chart-line")
st.markdown("Examples of how tooltips would be used in the Executive Overview dashboard:")

# KPI Card example
st.markdown("**KPI Card with Tooltip**")
st.markdown(
    """
    <div style="background: white; border-left: 4px solid #2251FF; border-radius: 0.5rem; 
                padding: 1.25rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 1rem;">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div>
                <div style="font-size: 0.75rem; font-weight: 600; color: #6B7F95; 
                            text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
                    National FI Rate
                </div>
                <div style="font-family: Georgia, serif; font-size: 2rem; font-weight: 700; 
                            color: #1E293B; line-height: 1.2;">
                    12.3%
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

tooltip_wrapper(
    content="What does this metric mean?",
    tooltip_text="The National Food Insecurity Rate represents the percentage of U.S. households that experienced food insecurity at some point during the year. Food insecurity means lacking consistent access to enough food for an active, healthy life.",
    icon="question-circle",
    position="top"
)

st.markdown("<br>", unsafe_allow_html=True)

# Chart example
st.markdown("**Chart with Tooltip**")
st.markdown(
    """
    <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 0.5rem; 
                padding: 1rem; margin-bottom: 1rem;">
        <div style="font-weight: 600; color: #1E293B; margin-bottom: 0.5rem;">
            📊 National Trend Over Time
        </div>
        <div style="color: #64748B; font-size: 0.875rem;">
            [Chart would appear here]
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

tooltip_wrapper(
    content="How do I interpret this chart?",
    tooltip_text="This line chart shows the national food insecurity rate from 2009 to 2023. Hover over data points to see exact values. An upward trend indicates increasing food insecurity, while a downward trend shows improvement.",
    icon="info-circle",
    position="top"
)

st.markdown("---")

# Technical details
with st.expander("📋 Technical Implementation Details"):
    st.markdown("""
    ### Desktop Implementation
    - **CSS-only hover**: Uses `:hover` pseudo-class with `opacity` and `visibility` transitions
    - **200ms delay**: Implemented via `transition-delay: 200ms` to prevent accidental triggers
    - **Positioning**: Absolute positioning with transform for precise placement
    - **Arrow**: CSS triangle using border trick
    
    ### Mobile Implementation
    - **Touch target**: 44x44px minimum size (WCAG 2.1 AA compliance)
    - **Modal/popover**: Fixed position overlay with backdrop
    - **Dismissible**: Click outside or press Escape to close
    - **Visual feedback**: Active state with scale transform (100ms)
    
    ### Accessibility
    - **ARIA labels**: All interactive elements have proper labels
    - **Keyboard support**: Escape key closes modal
    - **Focus management**: Modal prevents body scroll when open
    - **Screen reader friendly**: Semantic HTML structure
    
    ### Requirements Validated
    - ✅ Requirement 6.3: Desktop hover tooltip with 200ms delay
    - ✅ Requirement 6.4: Mobile tap interaction
    - ✅ Requirement 6.5: Dismissible on outside click
    - ✅ Requirement 10.1: 44x44px touch target for mobile
    """)

st.markdown("---")
st.markdown("*Demo created for task 2.10 of the executive-overview-redesign spec*")
