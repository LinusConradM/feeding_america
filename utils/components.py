"""
Reusable UI components — McKinsey-grade design.
White cards, left accent bars, Georgia serif numbers, high-contrast.

Touch Target Sizing (Requirements 10.1, 10.2):
- All interactive elements have minimum 44x44px touch targets on mobile (<768px)
- Minimum 8px spacing between adjacent touch targets on mobile
- Touch target CSS is automatically injected via inject_touch_target_css()
- Components with custom HTML (quick_tips, tooltip_wrapper) have built-in touch target sizing
- Streamlit native components (st.button, st.selectbox, st.expander) handle touch targets automatically

Touch Interaction Feedback (Requirements 10.3, 10.5):
- Visual feedback (color change + scale animation) within 100ms for all interactive elements
- Debouncing prevents rapid successive taps within 300ms threshold
- Automatic application to buttons, links, and custom interactive elements
- CSS transitions: 80ms for sub-100ms feedback requirement
- JavaScript debouncing with MutationObserver for dynamic content
- Helper functions: add_touch_feedback() and ensure_touch_target()
"""

import streamlit as st


# ── Touch Target Sizing Utilities ───────────────────────────────────────────
# Requirements 10.1, 10.2, 10.3, 10.5: Touch-friendly interactions for mobile
# - Minimum 44x44px touch targets on mobile (<768px)
# - Minimum 8px spacing between adjacent touch targets
# - Visual feedback within 100ms (color change or scale animation)
# - Debouncing for rapid taps (300ms threshold)

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
    
    .touch-target-stack > .touch-target:last-child,
    .touch-target-stack > button:last-child,
    .touch-target-stack > a:last-child {
        margin-bottom: 0 !important;
    }
}

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

/* Disabled state - no feedback */
.touch-feedback:disabled,
button:disabled,
a:disabled,
[role="button"]:disabled,
[onclick]:disabled,
.touch-target:disabled {
    pointer-events: none;
    opacity: 0.5;
}
</style>

<script>
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
    
    // Apply on load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', applyDebouncing);
    } else {
        applyDebouncing();
    }
    
    // Re-apply when new elements are added (for dynamic content)
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
</script>
"""


def inject_touch_target_css():
    """Inject touch target sizing CSS into the page."""
    st.markdown(TOUCH_TARGET_CSS, unsafe_allow_html=True)


def ensure_touch_target(element_html: str, add_spacing: bool = False) -> str:
    """
    Wrap an interactive element to ensure proper touch target sizing on mobile.
    
    Args:
        element_html: HTML string of the interactive element
        add_spacing: Whether to add spacing class for adjacent elements
        
    Returns:
        HTML string with touch target classes applied
        
    Requirements: 10.1, 10.2
    """
    spacing_class = " touch-target-spacing" if add_spacing else ""
    return f'<div class="touch-target{spacing_class}">{element_html}</div>'


def add_touch_feedback(element_html: str, debounce: bool = True) -> str:
    """
    Add touch interaction feedback to an interactive element.
    
    Adds:
    - Visual feedback (color change and scale animation) within 100ms
    - Optional debouncing for rapid taps (300ms threshold)
    
    Args:
        element_html: HTML string of the interactive element
        debounce: Whether to apply debouncing (default: True)
        
    Returns:
        HTML string with touch feedback classes applied
        
    Requirements: 10.3, 10.5
    """
    feedback_class = "touch-feedback"
    if debounce:
        feedback_class += " touch-debounce"
    
    # Add class to the element
    if 'class="' in element_html:
        element_html = element_html.replace('class="', f'class="{feedback_class} ')
    else:
        # Find the first tag and add class
        import re
        element_html = re.sub(r'(<[a-zA-Z]+)', rf'\1 class="{feedback_class}"', element_html, count=1)
    
    return element_html


# ── KPI Card ─────────────────────────────────────────────────────────────────
_ACCENT_MAP = {
    "sapphire": "accent-blue",
    "blue": "accent-blue",
    "ruby": "accent-red",
    "coral": "accent-red",
    "emerald": "accent-green",
    "teal": "accent-green",
    "amber": "accent-amber",
    "amethyst": "accent-purple",
    "plum": "accent-purple",
    "navy": "accent-dark",
    "dark": "accent-dark",
}


def kpi_card(
    title: str,
    value: str,
    change: str = "",
    icon: str = "chart-line",
    gradient: str = "sapphire",   # kept param name for backwards compat
    tooltip_text: str = None,
):
    """
    Render a McKinsey-style KPI card — white bg, left accent bar, serif value.
    
    Args:
        title: Card title/label
        value: Main metric value to display
        change: Optional change indicator (e.g., "+2.3%")
        icon: FontAwesome icon name
        gradient: Color gradient theme
        tooltip_text: Optional contextual help text for tooltip
    """
    accent = _ACCENT_MAP.get(gradient, "accent-blue")

    change_html = ""
    if change:
        is_up = change.startswith("+") or change.startswith("↑")
        cls = "up" if is_up else "down"
        arrow = "&#9650;" if is_up else "&#9660;"
        change_html = f'<div class="kpi-change {cls}">{arrow} {change}</div>'

    card_html = f"""
        <div class="kpi-card {accent}" role="article" aria-label="{title}: {value}">
            <div class="kpi-label">
                <i class="fas fa-{icon}" style="margin-right:.35rem;opacity:.5" aria-hidden="true"></i>{title}
            </div>
            <div class="kpi-value">{value}</div>
            {change_html}
        </div>
        """
    
    # If tooltip_text is provided, wrap the card with tooltip_wrapper
    if tooltip_text:
        tooltip_wrapper(
            content=card_html,
            tooltip_text=tooltip_text,
            icon="info-circle",
            position="top"
        )
    else:
        st.markdown(card_html, unsafe_allow_html=True)


def kpi_row(cards: list[dict]):
    """Render a row of KPI cards using responsive micro-tailwind classes."""
    cols = min(4, len(cards)) # Cap at 4 since micro-tailwind only goes up to grid-cols-4
    cards_html = f'<div class="grid grid-cols-{cols} gap-6 mb-6">'
    
    for card in cards:
        title = card.get("title", "")
        value = card.get("value", "")
        change = card.get("change", "")
        icon = card.get("icon", "chart-line")
        accent = _ACCENT_MAP.get(card.get("gradient", "blue"), "accent-blue")
        
        change_html = ""
        if change:
            is_up = change.startswith("+") or change.startswith("↑")
            cls = "up" if is_up else "down"
            arrow = "&#9650;" if is_up else "&#9660;"
            change_html = f'<div class="kpi-change {cls}">{arrow} {change}</div>'
            
        cards_html += f"""
            <div class="kpi-card {accent}">
                <div class="kpi-label">
                    <i class="fas fa-{icon}" style="margin-right:.25rem;opacity:.5"></i>{title}
                </div>
                <div class="kpi-value">{value}</div>
                {change_html}
            </div>
        """
        
    cards_html += '</div>'
    
    if hasattr(st, "html"):
        st.html(cards_html)
    else:
        st.markdown(cards_html, unsafe_allow_html=True)


def kpi_row_grouped(
    row_groups: list[dict],
    viewport_profile
) -> None:
    """
    Render KPI cards in logical row groupings with responsive layout.

    Args:
        row_groups: List of row configs, each containing:
            - title: Row group title
            - cards: List of card configs (same format as kpi_row)
        viewport_profile: Viewport detection result from get_viewport_profile()
    """
    # Get number of columns based on viewport
    columns = viewport_profile.kpi_columns

    # Render each row group
    for row_group in row_groups:
        title = row_group.get("title", "")
        cards = row_group.get("cards", [])

        # Render row group header
        if title:
            st.markdown(
                f"""
                <div style="margin-top:1.5rem;margin-bottom:0.75rem">
                    <h3 style="font-size:0.95rem;font-weight:600;
                               letter-spacing:0.05em;text-transform:uppercase;
                               color:#64748B;margin:0">{title}</h3>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Build grid HTML for cards
        cards_html = f'<div class="grid grid-cols-{columns} gap-6 mb-6">'

        for card in cards:
            card_title = card.get("title", "")
            value = card.get("value", "")
            change = card.get("change", "")
            icon = card.get("icon", "chart-line")
            accent = _ACCENT_MAP.get(card.get("gradient", "blue"), "accent-blue")

            change_html = ""
            if change:
                is_up = change.startswith("+") or change.startswith("↑")
                cls = "up" if is_up else "down"
                arrow = "&#9650;" if is_up else "&#9660;"
                change_html = f'<div class="kpi-change {cls}">{arrow} {change}</div>'

            cards_html += f"""
                <div class="kpi-card {accent}">
                    <div class="kpi-label">
                        <i class="fas fa-{icon}" style="margin-right:.25rem;opacity:.5"></i>{card_title}
                    </div>
                    <div class="kpi-value">{value}</div>
                    {change_html}
                </div>
            """

        cards_html += '</div>'

        # Render the grid
        if hasattr(st, "html"):
            st.html(cards_html)
        else:
            st.markdown(cards_html, unsafe_allow_html=True)



# ── Stat Card ────────────────────────────────────────────────────────────────
_STAT_COLORS = {
    "blue":   ("#EFF6FF", "#1D4ED8", "#DBEAFE"),
    "green":  ("#ECFDF5", "#047857", "#D1FAE5"),
    "red":    ("#FEF2F2", "#B91C1C", "#FECACA"),
    "purple": ("#FAF5FF", "#7E22CE", "#F3E8FF"),
    "amber":  ("#FFFBEB", "#92400E", "#FDE68A"),
    "gray":   ("#F9FAFB", "#374151", "#E5E7EB"),
}


def stat_card(label: str, value: str, description: str = "", color: str = "blue"):
    """Clean stat card with subtle background tint."""
    bg, val_color, brd = _STAT_COLORS.get(color, _STAT_COLORS["blue"])
    desc_html = (
        f'<div style="color:#6B7F95;font-size:.78rem;margin-top:.25rem">{description}</div>'
        if description else ""
    )
    st.markdown(
        f"""
        <div style="background:{bg};border:1px solid {brd};border-radius:.75rem;padding:1.15rem 1.25rem">
            <div style="font-size:.7rem;font-weight:600;letter-spacing:.05em;
                        text-transform:uppercase;color:#6B7F95;margin-bottom:.25rem">{label}</div>
            <div style="font-family:'Inter',sans-serif;font-size:1.35rem;font-weight:700;
                        color:{val_color};line-height:1.25">{value}</div>
            {desc_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Section Header ───────────────────────────────────────────────────────────
def section_header(title: str, subtitle: str = "", icon: str = ""):
    """McKinsey-style section divider — bold line, serif heading."""
    ico = (
        f'<i class="fas fa-{icon}" style="color:#2251FF;margin-right:.5rem;font-size:.85em"></i>'
        if icon else ""
    )
    sub = f'<p>{subtitle}</p>' if subtitle else ""
    st.markdown(
        f"""
        <div class="section-hdr">
            <h2>{ico}{title}</h2>
            {sub}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Info Banner ──────────────────────────────────────────────────────────────
_BANNER = {
    "info":    ("#EFF6FF", "#1E40AF", "#2251FF", "fa-info-circle"),
    "warning": ("#FFFBEB", "#92400E", "#F59E0B", "fa-exclamation-triangle"),
    "success": ("#ECFDF5", "#065F46", "#00B894", "fa-check-circle"),
    "error":   ("#FEF2F2", "#991B1B", "#D63031", "fa-times-circle"),
}


def info_banner(text: str, type: str = "info"):
    """Styled alert banner."""
    bg, txt, accent, fa = _BANNER.get(type, _BANNER["info"])
    st.markdown(
        f"""
        <div style="background:{bg};border-left:4px solid {accent};
                    border-radius:.5rem;padding:.85rem 1rem;
                    display:flex;align-items:flex-start;gap:.65rem;margin-bottom:1rem">
            <i class="fas {fa}" style="color:{accent};margin-top:.15rem"></i>
            <span style="color:{txt};font-size:.875rem;line-height:1.45">{text}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Metric Badge ─────────────────────────────────────────────────────────────
def metric_badge(label: str, value: str, color: str = "blue"):
    """Inline pill badge."""
    _map = {
        "blue":   ("bg-blue-100", "text-blue-800"),
        "green":  ("bg-emerald-100", "text-emerald-800"),
        "red":    ("bg-red-100", "text-red-800"),
        "purple": ("bg-purple-100", "text-purple-800"),
    }
    bg_cls, txt_cls = _map.get(color, _map["blue"])
    return (
        f'<span class="{bg_cls} {txt_cls}" '
        f'style="font-size:.75rem;font-weight:600;padding:.2rem .65rem;border-radius:9999px">'
        f'{label}: {value}</span>'
    )


# ── Empty State ──────────────────────────────────────────────────────────────
def empty_state(message: str, icon: str = "chart-bar"):
    """Placeholder for empty content areas."""
    st.markdown(
        f"""
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                    padding:4rem 1rem;color:#A3B1BF">
            <i class="fas fa-{icon}" style="font-size:2.5rem;margin-bottom:1rem;opacity:.4"></i>
            <p style="font-size:1rem;font-weight:500;margin:0">{message}</p>
            <p style="font-size:.8rem;margin-top:.35rem">Adjust filters or parameters to see results</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Quick Tips Callout ───────────────────────────────────────────────────────
def quick_tips_callout(tips: list[str], dismissible: bool = True) -> None:
    """
    Render quick tips callout with dismissal option.
    
    Args:
        tips: List of 3-5 actionable tips
        dismissible: Whether user can dismiss the callout
    """
    # HTML component with localStorage check and dismiss functionality
    localStorage_key = "quick_tips_dismissed"
    
    # Generate tips HTML
    tips_items = "\n".join([f"<li>{tip}</li>" for tip in tips])
    
    # Create HTML with localStorage integration
    html_content = f"""
    <div id="quick-tips-container">
        <style>
            #quick-tips-banner {{
                background: #FFFBEB;
                border-left: 4px solid #F59E0B;
                border-radius: 0.5rem;
                padding: 1rem 1.25rem;
                margin-bottom: 1.5rem;
                position: relative;
                display: none;
            }}
            #quick-tips-banner.visible {{
                display: block;
            }}
            .quick-tips-content {{
                display: flex;
                align-items: flex-start;
                gap: 0.75rem;
            }}
            .quick-tips-icon {{
                color: #F59E0B;
                margin-top: 0.15rem;
                font-size: 1.1rem;
            }}
            .quick-tips-body {{
                flex: 1;
            }}
            .quick-tips-title {{
                color: #92400E;
                font-weight: 700;
                font-size: 0.9rem;
                margin-bottom: 0.5rem;
            }}
            .quick-tips-list {{
                color: #92400E;
                font-size: 0.85rem;
                line-height: 1.6;
                margin: 0;
                padding-left: 1.25rem;
            }}
            .quick-tips-dismiss {{
                position: absolute;
                top: 0.75rem;
                right: 0.75rem;
                background: transparent;
                border: none;
                color: #92400E;
                cursor: pointer;
                font-size: 1.2rem;
                padding: 0.25rem 0.5rem;
                opacity: 0.6;
                transition: opacity 80ms ease, background-color 80ms ease, transform 80ms ease;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 0.25rem;
            }}
            .quick-tips-dismiss:hover {{
                opacity: 1;
            }}
            
            /* Touch feedback - Requirements 10.3, 10.5 */
            .quick-tips-dismiss:active {{
                transform: scale(0.95);
                background-color: rgba(146, 64, 14, 0.1);
                opacity: 1;
            }}
            
            /* Touch target sizing for mobile (Requirements 10.1, 10.2) */
            @media (max-width: 767px) {{
                .quick-tips-dismiss {{
                    min-width: 44px;
                    min-height: 44px;
                    /* Ensure 8px spacing from content edges */
                    top: 8px;
                    right: 8px;
                }}
            }}
        </style>
        
        <div id="quick-tips-banner">
            <div class="quick-tips-content">
                <i class="fas fa-lightbulb quick-tips-icon"></i>
                <div class="quick-tips-body">
                    <div class="quick-tips-title">Quick Tips</div>
                    <ul class="quick-tips-list">
                        {tips_items}
                    </ul>
                </div>
            </div>
            {"<button class='quick-tips-dismiss' onclick='dismissQuickTips()' aria-label='Dismiss quick tips'>✕</button>" if dismissible else ""}
        </div>
        
        <script>
            // Check localStorage on load
            (function() {{
                var dismissed = localStorage.getItem('{localStorage_key}');
                var banner = document.getElementById('quick-tips-banner');
                
                if (!dismissed || dismissed !== 'true') {{
                    banner.classList.add('visible');
                }}
            }})();
            
            // Dismiss function
            function dismissQuickTips() {{
                localStorage.setItem('{localStorage_key}', 'true');
                var banner = document.getElementById('quick-tips-banner');
                banner.style.display = 'none';
            }}
        </script>
    </div>
    """
    
    # Render using st.components.v1.html for localStorage support
    st.components.v1.html(html_content, height=200)


# ── Hero Section ─────────────────────────────────────────────────────────────
def hero_section(
    year: int,
    primary_metric: float,
    previous_metric: float | None,
    context_summary: str,
    show_quick_tips: bool = True
) -> None:
    """
    Render hero section with year, primary metric, and contextual summary.
    
    Args:
        year: Selected year for display
        primary_metric: National FI rate for selected year
        previous_metric: Previous year's FI rate for comparison
        context_summary: One-sentence contextual summary
        show_quick_tips: Whether to display quick tips callout
    """
    # Generate year-over-year comparison text
    comparison_text = ""
    if previous_metric is not None:
        change = primary_metric - previous_metric
        direction = "up" if change > 0 else "down"
        comparison_text = f"{direction} {abs(change):.1%} from {year - 1}"
    
    # Responsive typography: 3rem desktop, 2.5rem mobile
    hero_html = f"""
    <div style="background:linear-gradient(135deg, #051C2C 0%, #0D1452 50%, #1A237E 100%);
                border-radius:1rem;padding:2.5rem 2rem;margin-bottom:2rem;
                box-shadow:0 10px 25px -5px rgba(5,28,44,0.3);position:relative;overflow:hidden">
        
        <!-- Year badge -->
        <div style="display:inline-block;background:rgba(255,255,255,0.15);
                    border:1px solid rgba(255,255,255,0.25);border-radius:9999px;
                    padding:0.4rem 1rem;margin-bottom:1rem;backdrop-filter:blur(10px)">
            <span style="color:#FFFFFF;font-size:0.85rem;font-weight:700;
                         letter-spacing:0.05em;text-transform:uppercase">
                <i class="fas fa-calendar-alt" style="margin-right:0.4rem;opacity:0.8"></i>
                {year}
            </span>
        </div>
        
        <!-- Primary metric with responsive typography -->
        <div style="margin-bottom:0.75rem">
            <div class="text-5xl font-bold font-serif" 
                 style="color:#FFFFFF;line-height:1.15;letter-spacing:-0.02em;
                        text-shadow:0 2px 10px rgba(0,0,0,0.3)">
                {primary_metric:.1%}
            </div>
            <div style="color:rgba(255,255,255,0.7);font-size:0.95rem;
                        margin-top:0.5rem;font-weight:500">
                National Food Insecurity Rate
            </div>
        </div>
        
        <!-- Context summary -->
        <div style="color:rgba(255,255,255,0.85);font-size:1rem;
                    margin-top:1rem;line-height:1.5;max-width:600px">
            {context_summary}
            {f' <span style="color:#74B9FF;font-weight:600">({comparison_text})</span>' if comparison_text else ''}
        </div>
    </div>
    """
    
    if hasattr(st, "html"):
        st.html(hero_html)
    else:
        st.markdown(hero_html, unsafe_allow_html=True)
    
    # Quick tips callout (if enabled)
    if show_quick_tips:
        tips = [
            "Use the State Lookup dropdown to quickly find specific state data",
            "Hover over charts to see AI-generated insights about trends",
            "Collapse sections you don't need to focus on key metrics",
            "Compare regional patterns in the Geographic Section",
            "Check year-over-year changes in the KPI cards"
        ]
        quick_tips_callout(tips, dismissible=True)


# ── State Lookup Component ──────────────────────────────────────────────────
def state_lookup_component(
    year_data,
    state_names: dict[str, str],
    on_state_select: callable
) -> str | None:
    """
    Render state lookup dropdown with search and keyboard navigation.
    
    Args:
        year_data: Filtered dataset for selected year (pandas DataFrame)
        state_names: Mapping of state codes to full names
        on_state_select: Callback function when state is selected
        
    Returns:
        Selected state code or None
    """
    # Get available states from the year_data
    if hasattr(year_data, 'empty') and not year_data.empty:
        available_states = sorted(year_data['state'].unique().tolist())
    else:
        # Fallback to all states if data is empty
        available_states = sorted(state_names.keys())
    
    # Sort states alphabetically by full name
    sorted_states = sorted(available_states, key=lambda code: state_names.get(code, code))
    
    # Add a default "Select a state..." option at the beginning
    options = [None] + sorted_states
    
    # Format function to display full state names
    def format_state(state_code):
        if state_code is None:
            return "Select a state..."
        return state_names.get(state_code, state_code)
    
    # Render selectbox with keyboard navigation support (native to st.selectbox)
    selected_state = st.selectbox(
        "State Lookup",
        options=options,
        format_func=format_state,
        key="state_lookup_selectbox",
        help="Search for a specific state to view detailed metrics"
    )
    
    # Call the callback function if a state is selected
    if selected_state is not None:
        on_state_select(selected_state)
    
    return selected_state


# ── LLM Explainer UI ──────────────────────────────────────────────────────────

def llm_explainer_ui(page_name: str, context_dict: dict):
    """
    Renders an expandable LLM insight generator using the Gemini API.
    """
    st.markdown("<div class='h-4'></div>", unsafe_allow_html=True)
    with st.expander("✨ Generate Insights"):
        st.markdown(
            """<p style="font-size:0.85rem;color:#64748b;margin-bottom:1rem;">
            Click below to generate insights from the data on this page</p>""",
            unsafe_allow_html=True
        )
        if st.button("Generate Insights", key=f"btn_llm_{page_name.replace(' ', '_')}", type="primary"):
            with st.spinner("Analyzing data with Google Gemini..."):
                try:
                    from utils.llm import generate_insights
                    response = generate_insights(page_name, context_dict)
                    st.info(response, icon="💡")
                except Exception as e:
                    st.error(f"⚠️ Unable to load AI dependencies: {e}", icon="🚨")

# ── Collapsible Section Wrapper ─────────────────────────────────────────────
def collapsible_section(
    title: str,
    content_func: callable,
    icon: str = "",
    default_expanded: bool = True,
    key: str = ""
) -> None:
    """
    Render collapsible section using st.expander with custom styling.

    Args:
        title: Section header text
        content_func: Function that renders section content
        icon: FontAwesome icon name
        default_expanded: Initial state
        key: Unique key for session state persistence
    """
    # Generate unique session state key
    session_key = f"collapsible_{key}" if key else f"collapsible_{title.replace(' ', '_').lower()}"

    # Initialize session state if not exists
    if session_key not in st.session_state:
        st.session_state[session_key] = default_expanded

    # Custom CSS for chevron animation and styling
    st.markdown(
        """
        <style>
        /* Collapsible section custom styling */
        .streamlit-expanderHeader {
            font-size: 1.125rem;
            font-weight: 600;
            color: #1E293B;
            padding: 0.75rem 1rem;
            border-radius: 0.5rem;
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            transition: all 0.2s ease;
        }

        .streamlit-expanderHeader:hover {
            background: #F1F5F9;
            border-color: #CBD5E1;
        }

        /* Chevron icon animation */
        .streamlit-expanderHeader svg {
            transition: transform 0.3s ease;
        }

        details[open] > summary .streamlit-expanderHeader svg {
            transform: rotate(90deg);
        }

        /* Expander content styling */
        .streamlit-expanderContent {
            padding: 1rem;
            border: 1px solid #E2E8F0;
            border-top: none;
            border-radius: 0 0 0.5rem 0.5rem;
            background: #FFFFFF;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Render icon and title separately if icon is provided
    if icon:
        st.markdown(
            f'<div style="margin-bottom: 0.5rem;"><i class="fas fa-{icon}" style="color:#2251FF;margin-right:0.5rem;"></i><span style="font-size:1.125rem;font-weight:600;color:#1E293B;">{title}</span></div>',
            unsafe_allow_html=True
        )
        # Use empty title for expander to avoid duplication
        with st.expander("", expanded=st.session_state[session_key]):
            content_func()
    else:
        # No icon, use title directly
        with st.expander(title, expanded=st.session_state[session_key]):
            content_func()



# ── Tooltip Wrapper ─────────────────────────────────────────────────────────
def tooltip_wrapper(
    content: str,
    tooltip_text: str,
    icon: str = "info-circle",
    position: str = "top"
) -> None:
    """
    Wrap content with tooltip on hover (desktop) or tap (mobile).
    
    Args:
        content: Main content to display
        tooltip_text: Help text to show in tooltip
        icon: Icon to display for mobile tap target
        position: Tooltip position (top, bottom, left, right)
    """
    # Generate unique ID for this tooltip instance
    import hashlib
    tooltip_id = hashlib.md5(f"{content}{tooltip_text}".encode()).hexdigest()[:8]
    
    # Position-specific CSS classes
    position_styles = {
        "top": "bottom: 100%; left: 50%; transform: translateX(-50%) translateY(-8px);",
        "bottom": "top: 100%; left: 50%; transform: translateX(-50%) translateY(8px);",
        "left": "right: 100%; top: 50%; transform: translateX(-8px) translateY(-50%);",
        "right": "left: 100%; top: 50%; transform: translateX(8px) translateY(-50%);"
    }
    
    tooltip_position_style = position_styles.get(position, position_styles["top"])
    
    # Arrow position styles
    arrow_styles = {
        "top": "top: 100%; left: 50%; transform: translateX(-50%); border-color: #1E293B transparent transparent transparent;",
        "bottom": "bottom: 100%; left: 50%; transform: translateX(-50%); border-color: transparent transparent #1E293B transparent;",
        "left": "left: 100%; top: 50%; transform: translateY(-50%); border-color: transparent transparent transparent #1E293B;",
        "right": "right: 100%; top: 50%; transform: translateY(-50%); border-color: transparent #1E293B transparent transparent;"
    }
    
    arrow_position_style = arrow_styles.get(position, arrow_styles["top"])
    
    html_content = f"""
    <div id="tooltip-wrapper-{tooltip_id}" class="tooltip-wrapper-container">
        <style>
            /* Tooltip wrapper container */
            .tooltip-wrapper-container {{
                display: inline-block;
                position: relative;
            }}
            
            /* Content wrapper */
            .tooltip-content-wrapper {{
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
            }}
            
            /* Desktop: CSS-only hover tooltip */
            .tooltip-hover {{
                position: absolute;
                background: #1E293B;
                color: #FFFFFF;
                padding: 0.5rem 0.75rem;
                border-radius: 0.375rem;
                font-size: 0.875rem;
                line-height: 1.4;
                white-space: normal;
                max-width: 250px;
                z-index: 1000;
                pointer-events: none;
                opacity: 0;
                visibility: hidden;
                transition: opacity 0.2s ease, visibility 0.2s ease;
                transition-delay: 200ms;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                {tooltip_position_style}
            }}
            
            /* Tooltip arrow */
            .tooltip-hover::after {{
                content: '';
                position: absolute;
                width: 0;
                height: 0;
                border-style: solid;
                border-width: 6px;
                {arrow_position_style}
            }}
            
            /* Show tooltip on hover (desktop only) */
            @media (min-width: 768px) {{
                .tooltip-wrapper-container:hover .tooltip-hover {{
                    opacity: 1;
                    visibility: visible;
                }}
            }}
            
            /* Mobile: Info icon with tap interaction */
            .tooltip-icon-mobile {{
                display: none;
                align-items: center;
                justify-content: center;
                background: transparent;
                border: none;
                color: #2251FF;
                cursor: pointer;
                font-size: 1.1rem;
                padding: 0.5rem;
                border-radius: 0.375rem;
                transition: background 80ms ease, transform 80ms ease;
            }}
            
            .tooltip-icon-mobile:hover {{
                background: #EFF6FF;
            }}
            
            /* Touch feedback - Requirements 10.3, 10.5 */
            .tooltip-icon-mobile:active {{
                transform: scale(0.95);
                background: #DBEAFE;
            }}
            
            /* Show icon on mobile, hide desktop tooltip */
            /* Requirements 10.1, 10.2: Touch target sizing and spacing */
            @media (max-width: 767px) {{
                .tooltip-icon-mobile {{
                    display: inline-flex;
                    min-width: 44px;
                    min-height: 44px;
                }}
                
                .tooltip-hover {{
                    display: none;
                }}
                
                /* Ensure 8px spacing between tooltip icon and adjacent elements */
                .tooltip-content-wrapper {{
                    gap: 8px;
                }}
            }}
            
            /* Mobile popover modal */
            .tooltip-modal {{
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                z-index: 9999;
                align-items: center;
                justify-content: center;
                padding: 1rem;
            }}
            
            .tooltip-modal.active {{
                display: flex;
            }}
            
            .tooltip-modal-content {{
                background: #FFFFFF;
                border-radius: 0.75rem;
                padding: 1.25rem;
                max-width: 400px;
                width: 100%;
                box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
                position: relative;
                animation: slideUp 0.2s ease;
            }}
            
            @keyframes slideUp {{
                from {{
                    opacity: 0;
                    transform: translateY(20px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
            
            .tooltip-modal-header {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 0.75rem;
                padding-bottom: 0.75rem;
                border-bottom: 1px solid #E2E8F0;
            }}
            
            .tooltip-modal-title {{
                font-weight: 600;
                color: #1E293B;
                font-size: 1rem;
            }}
            
            .tooltip-modal-close {{
                display: flex;
                align-items: center;
                justify-content: center;
                background: transparent;
                border: none;
                color: #64748B;
                cursor: pointer;
                font-size: 1.5rem;
                padding: 0.5rem;
                border-radius: 0.375rem;
                transition: background 80ms ease, color 80ms ease, transform 80ms ease;
            }}
            
            .tooltip-modal-close:hover {{
                background: #F1F5F9;
                color: #1E293B;
            }}
            
            /* Touch feedback - Requirements 10.3, 10.5 */
            .tooltip-modal-close:active {{
                transform: scale(0.95);
                background: #E2E8F0;
            }}
            
            /* Touch target sizing for mobile (Requirements 10.1, 10.2) */
            @media (max-width: 767px) {{
                .tooltip-modal-close {{
                    min-width: 44px;
                    min-height: 44px;
                }}
            }}
            
            .tooltip-modal-body {{
                color: #475569;
                font-size: 0.9rem;
                line-height: 1.6;
            }}
        </style>
        
        <div class="tooltip-content-wrapper">
            <span>{content}</span>
            
            <!-- Desktop: Hover tooltip -->
            <div class="tooltip-hover">
                {tooltip_text}
            </div>
            
            <!-- Mobile: Tap icon -->
            <button 
                class="tooltip-icon-mobile" 
                onclick="openTooltipModal_{tooltip_id}()"
                aria-label="Show help information"
                type="button">
                <i class="fas fa-{icon}"></i>
            </button>
        </div>
        
        <!-- Mobile: Modal popover -->
        <div id="tooltip-modal-{tooltip_id}" class="tooltip-modal" onclick="closeTooltipModal_{tooltip_id}(event)">
            <div class="tooltip-modal-content" onclick="event.stopPropagation()">
                <div class="tooltip-modal-header">
                    <div class="tooltip-modal-title">Information</div>
                    <button 
                        class="tooltip-modal-close" 
                        onclick="closeTooltipModal_{tooltip_id}(event)"
                        aria-label="Close"
                        type="button">
                        ✕
                    </button>
                </div>
                <div class="tooltip-modal-body">
                    {tooltip_text}
                </div>
            </div>
        </div>
        
        <script>
            function openTooltipModal_{tooltip_id}() {{
                const modal = document.getElementById('tooltip-modal-{tooltip_id}');
                if (modal) {{
                    modal.classList.add('active');
                    // Prevent body scroll when modal is open
                    document.body.style.overflow = 'hidden';
                }}
            }}
            
            function closeTooltipModal_{tooltip_id}(event) {{
                if (event) {{
                    event.stopPropagation();
                }}
                const modal = document.getElementById('tooltip-modal-{tooltip_id}');
                if (modal) {{
                    modal.classList.remove('active');
                    // Restore body scroll
                    document.body.style.overflow = '';
                }}
            }}
            
            // Close modal on Escape key
            document.addEventListener('keydown', function(event) {{
                if (event.key === 'Escape') {{
                    closeTooltipModal_{tooltip_id}(event);
                }}
            }});
        </script>
    </div>
    """
    
    # Render using st.html if available, otherwise st.markdown
    if hasattr(st, "html"):
        st.html(html_content)
    else:
        st.markdown(html_content, unsafe_allow_html=True)



# ── Geographic Section ─────────────────────────────────────────────────────
def geographic_section(
    year_data,
    selected_year: int,
    viewport_profile: dict,
    selected_state: str | None = None
) -> None:
    """
    Render consolidated geographic visualizations with responsive layout.
    
    Consolidates three geographic visualizations:
    - State-level choropleth map
    - Regional comparison bar chart
    - Urban/Rural comparison bar chart
    
    Layout adapts based on viewport:
    - Desktop (>1024px): 3-column layout with 60/20/20 split (map | regional | urban/rural)
    - Tablet (768-1024px): 2-row layout (map + regional in row 1, urban/rural in row 2)
    - Mobile (<768px): Vertical stack (map → regional → urban/rural)
    
    All three visualizations use consistent color scales:
    - Teal (low) → Amber (medium) → Rose (high)
    
    Args:
        year_data: Filtered dataset for selected year
        selected_year: Year for display
        viewport_profile: Viewport detection result from get_viewport_profile()
        selected_state: Optional state code to highlight on the map
    
    Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 14.1
    """
    import plotly.express as px
    import plotly.graph_objects as go
    from utils.theme import COLORS, PLOTLY_LAYOUT
    from utils.data_loader import STATE_NAMES
    
    # Determine viewport characteristics
    is_mobile = viewport_profile.is_mobile
    is_portrait = viewport_profile.is_portrait
    breakpoint = viewport_profile.breakpoint_name
    
    # Consistent color scale for all geographic visualizations
    color_scale = [COLORS["teal"], COLORS["amber"], COLORS["rose"]]
    
    # Helper function to merge layout with responsive overrides
    def layout_responsive(**kwargs):
        """Merge base Plotly layout with responsive overrides safely."""
        layout = dict(PLOTLY_LAYOUT)
        margin = kwargs.pop("margin", None)
        layout.update(kwargs)
        if margin:
            layout["margin"] = margin
        return layout
    
    # ============================================================================
    # 1. STATE-LEVEL MAP
    # ============================================================================
    state_map = (year_data.groupby("state", observed=True)["overall_food_insecurity_rate"]
                 .mean().reset_index())
    state_map.columns = ["State", "FI Rate"]
    state_map["State Name"] = state_map["State"].map(STATE_NAMES)
    
    fig_map = px.choropleth(
        state_map, 
        locations="State", 
        locationmode="USA-states",
        color="FI Rate", 
        color_continuous_scale=color_scale,
        scope="usa", 
        hover_name="State Name",
        labels={"FI Rate": "Food Insecurity Rate"},
    )
    
    # Highlight selected state if provided
    if selected_state:
        # Add a border/outline to the selected state
        selected_state_data = state_map[state_map["State"] == selected_state]
        if not selected_state_data.empty:
            fig_map.add_trace(go.Choropleth(
                locations=[selected_state],
                locationmode="USA-states",
                z=[selected_state_data["FI Rate"].iloc[0]],
                colorscale=[[0, "rgba(255, 0, 0, 0)"], [1, "rgba(255, 0, 0, 0)"]],
                showscale=False,
                hoverinfo="skip",
                marker=dict(
                    line=dict(color="red", width=3)
                ),
            ))
    
    # Responsive map height
    if is_portrait:
        map_height = 300
    elif is_mobile:
        map_height = 360
    elif breakpoint == "tablet":
        map_height = 420
    else:  # desktop
        map_height = 500
    
    # Configure pinch-to-zoom for mobile devices (Requirement 10.4)
    layout_config = {
        "title": "",
        "height": map_height,
        "geo": dict(bgcolor="rgba(0,0,0,0)", lakecolor="rgba(0,0,0,0)"),
        "coloraxis_colorbar": dict(tickformat=".0%", title="FI Rate"),
    }
    
    # Enable pinch-to-zoom on mobile viewports
    if is_mobile:
        layout_config["dragmode"] = "zoom"
    
    fig_map.update_layout(**layout_responsive(**layout_config))
    
    # ============================================================================
    # 2. REGIONAL COMPARISON
    # ============================================================================
    regional_fig = None
    if "census_region" in year_data.columns:
        regional = (year_data.groupby("census_region", observed=True)["overall_food_insecurity_rate"]
                    .mean().reset_index()
                    .sort_values("overall_food_insecurity_rate", ascending=True))
        regional.columns = ["Region", "FI Rate"]
        regional = regional.dropna(subset=["Region"])
        
        # Responsive regional chart height
        if is_portrait:
            reg_height = 240
        elif is_mobile:
            reg_height = 280
        elif breakpoint == "tablet":
            reg_height = 300
        else:  # desktop
            reg_height = 300
        
        reg_margin = dict(l=64, r=12, t=32, b=40) if is_mobile else None
        reg_dtick = 0.02 if is_mobile else None
        
        regional_fig = px.bar(
            regional, 
            x="FI Rate", 
            y="Region", 
            orientation="h",
            color="FI Rate",
            color_continuous_scale=color_scale,
        )
        regional_fig.update_layout(
            **layout_responsive(
                title="",
                height=reg_height,
                showlegend=False,
                coloraxis_showscale=False,
                xaxis_tickformat=".0%",
                margin=reg_margin,
            ),
        )
        regional_fig.update_xaxes(dtick=reg_dtick)
        regional_fig.update_traces(
            hovertemplate="<b>%{y}</b><br>FI Rate: %{x:.1%}<extra></extra>",
        )
    
    # ============================================================================
    # 3. URBAN/RURAL COMPARISON
    # ============================================================================
    urban_fig = None
    if "urban_rural" in year_data.columns:
        urban = (year_data.groupby("urban_rural", observed=True)["overall_food_insecurity_rate"]
                 .mean().reset_index())
        urban.columns = ["Category", "FI Rate"]
        urban = urban.dropna()
        
        # Responsive urban/rural chart height
        if is_portrait:
            urban_height = 260
        elif is_mobile:
            urban_height = 300
        elif breakpoint == "tablet":
            urban_height = 320
        else:  # desktop
            urban_height = 350
        
        urban_fig = px.bar(
            urban, 
            x="Category", 
            y="FI Rate",
            color="Category",
            color_discrete_sequence=[COLORS["teal"], COLORS["amber"], COLORS["blue"]],
        )
        urban_fig.update_layout(
            **layout_responsive(
                title="",
                height=urban_height,
                showlegend=False,
                yaxis_tickformat=".0%",
                yaxis_title="Avg FI Rate",
                margin=dict(l=40, r=10, t=32, b=40) if is_mobile else None,
            ),
        )
        urban_fig.update_traces(
            hovertemplate="<b>%{x}</b><br>FI Rate: %{y:.1%}<extra></extra>",
        )
    
    # ============================================================================
    # RESPONSIVE LAYOUT RENDERING
    # ============================================================================
    
    # Configure Plotly chart config for mobile pinch-to-zoom (Requirement 10.4)
    plotly_config = {
        'displayModeBar': True if is_mobile else 'hover',
        'scrollZoom': True if is_mobile else False,
        'doubleClick': 'reset',
    }
    
    if is_mobile:
        # Mobile: Vertical stack (map → regional → urban/rural)
        st.markdown(
            '<h3 style="font-size: 1rem; font-weight: 600; color: #4B5563; '
            'margin-bottom: 1rem; margin-top: 1.5rem;">State-Level Map</h3>',
            unsafe_allow_html=True
        )
        st.plotly_chart(fig_map, use_container_width=True, config=plotly_config)
        
        if regional_fig:
            st.markdown(
                '<h3 style="font-size: 1rem; font-weight: 600; color: #4B5563; '
                'margin-bottom: 1rem; margin-top: 1.5rem;">Regional Comparison</h3>',
                unsafe_allow_html=True
            )
            st.plotly_chart(regional_fig, use_container_width=True)
        
        if urban_fig:
            st.markdown(
                '<h3 style="font-size: 1rem; font-weight: 600; color: #4B5563; '
                'margin-bottom: 1rem; margin-top: 1.5rem;">Urban vs Rural</h3>',
                unsafe_allow_html=True
            )
            st.plotly_chart(urban_fig, use_container_width=True)
    
    elif breakpoint == "tablet":
        # Tablet: 2-row layout (map + regional in row 1, urban/rural in row 2)
        st.markdown(
            '<h3 style="font-size: 1rem; font-weight: 600; color: #4B5563; '
            'margin-bottom: 1rem; margin-top: 1.5rem;">State-Level Map</h3>',
            unsafe_allow_html=True
        )
        st.plotly_chart(fig_map, use_container_width=True, config=plotly_config)
        
        if regional_fig:
            st.markdown(
                '<h3 style="font-size: 1rem; font-weight: 600; color: #4B5563; '
                'margin-bottom: 1rem; margin-top: 1.5rem;">Regional Comparison</h3>',
                unsafe_allow_html=True
            )
            st.plotly_chart(regional_fig, use_container_width=True)
        
        if urban_fig:
            st.markdown(
                '<h3 style="font-size: 1rem; font-weight: 600; color: #4B5563; '
                'margin-bottom: 1rem; margin-top: 1.5rem;">Urban vs Rural</h3>',
                unsafe_allow_html=True
            )
            st.plotly_chart(urban_fig, use_container_width=True)
    
    else:
        # Desktop: 3-column layout with 60/20/20 split
        # Map takes full width first
        st.markdown(
            '<h3 style="font-size: 1rem; font-weight: 600; color: #4B5563; '
            'margin-bottom: 1rem; margin-top: 1.5rem;">State-Level Map</h3>',
            unsafe_allow_html=True
        )
        st.plotly_chart(fig_map, use_container_width=True, config=plotly_config)
        
        # Regional and Urban/Rural side by side
        if regional_fig or urban_fig:
            col_reg, col_urban = st.columns(2)
            
            if regional_fig:
                with col_reg:
                    st.markdown(
                        '<h3 style="font-size: 1rem; font-weight: 600; color: #4B5563; '
                        'margin-bottom: 1rem;">Regional Comparison</h3>',
                        unsafe_allow_html=True
                    )
                    st.plotly_chart(regional_fig, use_container_width=True)
            
            if urban_fig:
                with col_urban:
                    st.markdown(
                        '<h3 style="font-size: 1rem; font-weight: 600; color: #4B5563; '
                        'margin-bottom: 1rem;">Urban vs Rural</h3>',
                        unsafe_allow_html=True
                    )
                    st.plotly_chart(urban_fig, use_container_width=True)
