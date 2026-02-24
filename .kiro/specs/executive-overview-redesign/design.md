# Design Document: Executive Overview Redesign

## Overview

This design document specifies the technical approach for redesigning the Executive Overview dashboard (views/1_Executive_Overview.py) to deliver a story-driven, mobile-responsive user experience with enhanced visual hierarchy and interactive features.

### Design Goals

1. **Story-Driven Flow**: Transform linear data presentation into a narrative journey from national overview to state-level details
2. **Visual Hierarchy**: Group related metrics logically to improve comprehension and reduce cognitive load
3. **Responsive Design**: Deliver optimized experiences across desktop (>1024px), tablet (768-1024px), and mobile (<768px) viewports
4. **Interactive Features**: Enable quick state lookup, collapsible sections, and contextual help without page navigation
5. **Performance**: Optimize mobile rendering through lazy loading and adaptive data reduction
6. **Accessibility**: Ensure WCAG 2.1 AA compliance with keyboard navigation, ARIA labels, and semantic HTML

### Key Design Decisions

**Component-Based Architecture**: Leverage existing utils/components.py patterns (kpi_card, section_header) and extend with new interactive components (state_lookup, collapsible_section, tooltip_wrapper).

**CSS-First Responsive Strategy**: Use existing micro-Tailwind system from utils/theme.py with viewport-aware rendering via utils/responsive.py rather than JavaScript-heavy solutions.

**Progressive Enhancement**: Desktop layout serves as baseline; mobile adaptations reduce complexity rather than add features.

**Streamlit Native Components**: Prefer Streamlit's built-in components (st.expander for collapsible sections, st.selectbox for state lookup) over custom HTML/JS to maintain consistency and reduce maintenance burden.

## Architecture

### High-Level Structure

```
Executive Overview Dashboard
├── Hero Section (new)
│   ├── Year Display
│   ├── Primary Metric (National FI Rate)
│   ├── Contextual Summary
│   ├── Quick Tips Callout (dismissible)
│   └── LLM Explainer
├── KPI Cards (reorganized)
│   ├── Row 1: Core FI Metrics (4 cards)
│   └── Row 2: Economic Drivers (4 cards)
├── National Trend Chart (existing, enhanced)
├── Geographic Section (consolidated, new)
│   ├── State Map (60% width on desktop)
│   ├── Regional Comparison (20% width)
│   └── Urban/Rural Comparison (20% width)
├── State Lookup (new interactive component)
├── State Rankings (collapsible)
│   ├── Top 10 States
│   └── Bottom 10 States
└── Statistical Details (collapsible, new)
    └── Key Statistics Cards
```

### Responsive Layout Strategy

**Desktop (>1024px)**:
- Multi-column layouts for Geographic Section (60/20/20 split)
- KPI cards in 4-column grid
- State Rankings in 2-column layout (top 10 | bottom 10)
- Chart heights: 400-500px

**Tablet (768-1024px)**:
- Geographic Section stacks to 2-column (map + regional, then urban/rural below)
- KPI cards in 2-column grid maintaining row groupings
- State Rankings in 2-column layout
- Chart heights: 300-400px

**Mobile (<768px)**:
- All sections stack vertically
- KPI cards in 1-column maintaining row groupings
- State Rankings in 1-column (top 10, then bottom 10)
- Chart heights: 240-300px
- Reduced data points in charts (30% reduction)
- Lazy loading for below-fold content

### Data Flow

```
User selects year (sidebar)
    ↓
Filter dataset by year
    ↓
Calculate metrics (national, state, regional)
    ↓
Detect viewport (utils/responsive.py)
    ↓
Render components with viewport-specific configs
    ↓
Apply lazy loading for mobile below-fold content
```

## Components and Interfaces

### New Components

#### 1. Hero Section Component

**Purpose**: Provide immediate high-level context with primary metric and narrative summary.

**Interface**:
```python
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
```

**Implementation Details**:
- Large typography for primary metric (3rem on desktop, 2.5rem on mobile)
- Year displayed prominently with badge styling
- Context summary uses natural language comparison ("up 0.5% from 2022")
- Quick tips stored in session state with dismissal preference in localStorage
- Gradient background (subtle) to differentiate from content sections

#### 2. State Lookup Component

**Purpose**: Enable quick navigation to specific state data without scrolling.

**Interface**:
```python
def state_lookup_component(
    year_data: pd.DataFrame,
    state_names: dict[str, str],
    on_state_select: callable
) -> str | None:
    """
    Render state lookup dropdown with search and keyboard navigation.
    
    Args:
        year_data: Filtered dataset for selected year
        state_names: Mapping of state codes to full names
        on_state_select: Callback function when state is selected
        
    Returns:
        Selected state code or None
    """
```

**Implementation Details**:
- Uses st.selectbox with format_func for display names
- Alphabetically sorted state list
- On selection, triggers:
  1. Map highlight (via Plotly selectedpoints)
  2. Summary card display with state metrics
  3. Scroll to map section (via st.experimental_set_query_params anchor)
- Keyboard accessible with type-ahead search (native to st.selectbox)

#### 3. Collapsible Section Wrapper

**Purpose**: Allow users to expand/collapse less critical sections.

**Interface**:
```python
def collapsible_section(
    title: str,
    content_func: callable,
    icon: str = "",
    default_expanded: bool = True,
    key: str = ""
) -> None:
    """
    Render collapsible section using st.expander.
    
    Args:
        title: Section header text
        content_func: Function that renders section content
        icon: FontAwesome icon name
        default_expanded: Initial state
        key: Unique key for session state persistence
    """
```

**Implementation Details**:
- Wraps st.expander with custom styling
- Persists state in st.session_state during session
- Custom CSS for chevron icon animation
- Maintains accessibility with proper ARIA attributes (handled by Streamlit)

#### 4. Tooltip Wrapper Component

**Purpose**: Provide contextual help for metrics and visualizations.

**Interface**:
```python
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
```

**Implementation Details**:
- Desktop: CSS-only hover tooltip (200ms delay)
- Mobile: Tap icon to show tooltip in modal/popover
- Touch target: 44x44px minimum
- Dismissible on outside click
- Uses st.popover for mobile implementation

#### 5. Quick Tips Callout

**Purpose**: Guide first-time users on dashboard navigation.

**Interface**:
```python
def quick_tips_callout(tips: list[str], dismissible: bool = True) -> None:
    """
    Render quick tips callout with dismissal option.
    
    Args:
        tips: List of 3-5 actionable tips
        dismissible: Whether user can dismiss the callout
    """
```

**Implementation Details**:
- Styled info banner with lightbulb icon
- 3-5 bullet points with actionable tips
- Dismiss button stores preference in localStorage via st.components.v1.html
- Checks localStorage on load to determine visibility
- Positioned in Hero Section

### Modified Components

#### KPI Row Component Enhancement

**Current**: Single row of 8 cards with no grouping

**Enhanced**:
```python
def kpi_row_grouped(
    row_groups: list[dict],
    viewport_profile: dict
) -> None:
    """
    Render KPI cards in logical row groupings with responsive layout.
    
    Args:
        row_groups: List of row configs, each containing:
            - title: Row group title
            - cards: List of card configs
        viewport_profile: Viewport detection result from get_viewport_profile()
    """
```

**Changes**:
- Add row group headers ("Core Food Insecurity Metrics", "Economic Drivers")
- Maintain row groupings in mobile stacking
- Adjust grid columns based on viewport (4 cols desktop, 2 cols tablet, 1 col mobile)

#### Geographic Section Layout

**Current**: Three separate sections (map, regional, urban/rural) scattered in layout

**Enhanced**:
```python
def geographic_section(
    year_data: pd.DataFrame,
    selected_year: int,
    viewport_profile: dict
) -> None:
    """
    Render consolidated geographic visualizations with responsive layout.
    
    Args:
        year_data: Filtered dataset for selected year
        selected_year: Year for display
        viewport_profile: Viewport detection result
    """
```

**Layout**:
- Desktop: 3-column layout with 60/20/20 split (map | regional | urban/rural)
- Tablet: 2-row layout (map + regional in row 1, urban/rural in row 2)
- Mobile: Vertical stack (map → regional → urban/rural)
- Consistent color scales across all three visualizations

### Existing Components (Reused)

- `kpi_card()`: Individual KPI card rendering
- `section_header()`: Section dividers with icons
- `stat_card()`: Statistical summary cards
- `llm_explainer_ui()`: AI-generated insights
- `info_banner()`: Alert/notification banners

## Data Models

### Viewport Profile

```python
@dataclass
class ViewportProfile:
    width: int | None
    is_mobile: bool
    is_portrait: bool
    breakpoint_name: str  # "mobile", "tablet", "desktop"
    
    @property
    def chart_height(self) -> int:
        """Return appropriate chart height for viewport."""
        if self.is_portrait:
            return 240
        elif self.is_mobile:
            return 280
        elif self.breakpoint_name == "tablet":
            return 350
        else:
            return 450
    
    @property
    def kpi_columns(self) -> int:
        """Return number of KPI card columns for viewport."""
        if self.is_mobile:
            return 1
        elif self.breakpoint_name == "tablet":
            return 2
        else:
            return 4
```

### State Summary Card Data

```python
@dataclass
class StateSummary:
    state_code: str
    state_name: str
    fi_rate: float
    rank: int  # 1-51 ranking
    total_states: int  # Always 51 (50 states + DC)
    food_insecure_persons: int
    cost_per_meal: float
    poverty_rate: float
    
    def to_display_dict(self) -> dict:
        """Convert to display-ready dictionary."""
        return {
            "State": self.state_name,
            "FI Rate": f"{self.fi_rate:.1%}",
            "Rank": f"{self.rank} of {self.total_states}",
            "Food Insecure": f"{self.food_insecure_persons:,}",
            "Cost/Meal": f"${self.cost_per_meal:.2f}",
            "Poverty": f"{self.poverty_rate:.1%}"
        }
```

### Quick Tips Configuration

```python
QUICK_TIPS = [
    "Use the State Lookup dropdown to quickly find specific state data",
    "Hover over charts to see AI-generated insights about trends",
    "Collapse sections you don't need to focus on key metrics",
    "Compare regional patterns in the Geographic Section",
    "Check year-over-year changes in the KPI cards"
]
```

### Chart Configuration by Viewport

```python
@dataclass
class ChartConfig:
    height: int
    margin: dict[str, int]
    font_size: int
    marker_size: int
    line_width: int
    show_legend: bool
    data_point_reduction: float  # 0.0-1.0, percentage to keep
    
    @classmethod
    def for_viewport(cls, viewport: ViewportProfile) -> "ChartConfig":
        """Generate chart config for viewport."""
        if viewport.is_mobile:
            return cls(
                height=240 if viewport.is_portrait else 280,
                margin={"l": 40, "r": 12, "t": 32, "b": 40},
                font_size=11,
                marker_size=5,
                line_width=2,
                show_legend=False,
                data_point_reduction=0.7  # Keep 70% of points
            )
        elif viewport.breakpoint_name == "tablet":
            return cls(
                height=350,
                margin={"l": 48, "r": 16, "t": 40, "b": 44},
                font_size=12,
                marker_size=6,
                line_width=2.5,
                show_legend=True,
                data_point_reduction=1.0
            )
        else:  # desktop
            return cls(
                height=450,
                margin={"l": 56, "r": 24, "t": 64, "b": 48},
                font_size=13,
                marker_size=8,
                line_width=3,
                show_legend=True,
                data_point_reduction=1.0
            )
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After analyzing all acceptance criteria, the following redundancies were identified and consolidated:

- **1.1 and 1.3**: Both specify section ordering (national → regional → state → statistical). Consolidated into Property 1.
- **9.3 and 11.2**: Both specify mobile chart heights (240-300px). Consolidated into Property 18.
- **2.4 and 8.2**: Both specify desktop KPI layout (4 columns). Consolidated into Property 3.

### Property 1: Section Ordering

*For any* rendered dashboard, sections SHALL appear in the following order: Hero_Section, National Trend, Geographic_Section, State Rankings, Statistical Details, maintaining a narrative flow from national to state-level scope.

**Validates: Requirements 1.1, 1.3**

### Property 2: Hero Section Content Completeness

*For any* selected year with available data, the Hero_Section SHALL display the year, national FI rate as primary metric, and a contextual summary sentence.

**Validates: Requirements 1.2, 15.2, 15.3, 15.4**

### Property 3: KPI Card Row Grouping

*For any* rendered dashboard, KPI_Cards SHALL be organized into exactly two rows: Row 1 containing [National FI Rate, Food Insecure Persons, Child FI Rate, Cost Per Meal] and Row 2 containing [Poverty Rate, Median Income, Unemployment, Budget Shortfall].

**Validates: Requirements 2.1, 2.2, 2.3**

### Property 4: Desktop KPI Layout

*For any* viewport width > 1024px, each KPI row SHALL display 4 cards in horizontal layout.

**Validates: Requirements 2.4, 8.2**

### Property 5: Mobile KPI Layout Preservation

*For any* viewport width < 768px, KPI_Cards SHALL stack vertically while maintaining row groupings (Row 1 cards appear before Row 2 cards).

**Validates: Requirements 2.5, 9.2**

### Property 6: Geographic Section Component Completeness

*For any* rendered dashboard, the Geographic_Section SHALL contain exactly three visualizations: state map, regional comparison, and urban/rural comparison.

**Validates: Requirements 3.1**

### Property 7: Desktop Geographic Layout

*For any* viewport width > 1024px, the Geographic_Section SHALL display visualizations in multi-column layout with the state map allocated >= 60% of horizontal space.

**Validates: Requirements 3.2, 3.3, 8.1**

### Property 8: Geographic Color Scale Consistency

*For any* rendered Geographic_Section, all three visualizations SHALL use the same color scale configuration (teal for low, amber for medium, rose for high FI rates).

**Validates: Requirements 3.4, 14.1**

### Property 9: Mobile Geographic Stacking Order

*For any* viewport width < 768px, Geographic_Section visualizations SHALL stack vertically in order: state map, regional comparison, urban/rural comparison.

**Validates: Requirements 3.5, 9.1**

### Property 10: State Lookup Completeness

*For any* rendered dashboard, the State_Lookup dropdown SHALL contain exactly 51 options (50 states + DC) in alphabetical order by state name.

**Validates: Requirements 4.2**

### Property 11: State Selection Map Highlighting

*For any* state selected from State_Lookup, the dashboard SHALL highlight that state on the map visualization.

**Validates: Requirements 4.3**

### Property 12: State Selection Summary Display

*For any* state selected from State_Lookup, the dashboard SHALL display a summary card containing the state's FI rate, rank, and key metrics (food insecure persons, cost per meal, poverty rate).

**Validates: Requirements 4.4**

### Property 13: State Lookup Keyboard Accessibility

*For any* rendered State_Lookup component, it SHALL support keyboard navigation (Tab, Arrow keys, Enter) and have proper ARIA attributes.

**Validates: Requirements 4.5**

### Property 14: Collapsible Section Implementation

*For any* rendered dashboard, Statistical Details and State Rankings sections SHALL be implemented as collapsible components with expand/collapse functionality.

**Validates: Requirements 5.1**

### Property 15: Collapsible Section Toggle Behavior

*For any* collapsible section, clicking the header SHALL toggle the section between expanded and collapsed states.

**Validates: Requirements 5.2**

### Property 16: Collapsible Section Visual Indicator

*For any* collapsible section, a chevron icon SHALL be displayed that reflects the current state (pointing down when expanded, pointing right when collapsed).

**Validates: Requirements 5.3**

### Property 17: Collapsible Section Session Persistence

*For any* collapsible section state change, the new state SHALL persist in session storage and be maintained during the user session across interactions.

**Validates: Requirements 5.4**

### Property 18: KPI Card Tooltip Presence

*For any* KPI_Card, there SHALL exist an associated tooltip component explaining the metric definition.

**Validates: Requirements 6.1**

### Property 19: Chart Tooltip Presence

*For any* chart visualization, there SHALL exist an associated tooltip or hover explanation describing how to interpret the data.

**Validates: Requirements 6.2**

### Property 20: Desktop Tooltip Timing

*For any* KPI_Card hover event on viewport width > 768px, the associated tooltip SHALL display within 200 milliseconds.

**Validates: Requirements 6.3**

### Property 21: Mobile Tooltip Interaction

*For any* tooltip info icon tap on viewport width < 768px, the associated tooltip SHALL display.

**Validates: Requirements 6.4**

### Property 22: Tooltip Dismissal

*For any* visible tooltip, clicking or tapping outside the tooltip area SHALL dismiss it.

**Validates: Requirements 6.5**

### Property 23: Quick Tips Content Range

*For any* rendered Quick_Tips component, it SHALL contain between 3 and 5 actionable tips.

**Validates: Requirements 7.2**

### Property 24: Quick Tips Dismissal Persistence

*For any* Quick_Tips dismissal action, the dismissal preference SHALL be stored in localStorage and the component SHALL not display on subsequent page loads.

**Validates: Requirements 7.4, 7.5**

### Property 25: Desktop Chart Height Range

*For any* viewport width > 1024px, primary chart visualizations SHALL have heights between 400-500 pixels.

**Validates: Requirements 8.3, 11.4**

### Property 26: Desktop State Rankings Layout

*For any* viewport width > 1024px, State Rankings SHALL display in two-column layout with top 10 states and bottom 10 states side by side.

**Validates: Requirements 8.4**

### Property 27: Mobile Vertical Stacking

*For any* viewport width < 768px, all major sections SHALL stack vertically in a single column.

**Validates: Requirements 9.1**

### Property 28: Mobile Chart Height Range

*For any* viewport width < 768px, chart visualizations SHALL have heights between 240-300 pixels.

**Validates: Requirements 9.3, 11.2**

### Property 29: Mobile State Rankings Layout

*For any* viewport width < 768px, State Rankings SHALL display in single-column layout with top 10 states above bottom 10 states.

**Validates: Requirements 9.4**

### Property 30: Mobile Typography Minimum

*For any* viewport width < 768px, body text SHALL have font size >= 14px to maintain readability.

**Validates: Requirements 9.5**

### Property 31: Mobile Touch Target Sizing

*For any* interactive element on viewport width < 768px, the touch target SHALL have minimum dimensions of 44x44 pixels.

**Validates: Requirements 10.1**

### Property 32: Mobile Touch Target Spacing

*For any* pair of adjacent interactive elements on viewport width < 768px, there SHALL be >= 8 pixels of spacing between them.

**Validates: Requirements 10.2**

### Property 33: Touch Interaction Feedback Timing

*For any* touch interaction on an interactive element, visual feedback (color change or scale animation) SHALL appear within 100 milliseconds.

**Validates: Requirements 10.3**

### Property 34: Map Pinch-Zoom Support

*For any* map visualization on viewport width < 768px, pinch-to-zoom gestures SHALL be enabled.

**Validates: Requirements 10.4**

### Property 35: Rapid Tap Debouncing

*For any* interactive element, rapid successive taps within 300 milliseconds SHALL be debounced to register as a single interaction.

**Validates: Requirements 10.5**

### Property 36: Chart Responsive Width

*For any* chart visualization at any breakpoint, the chart width SHALL be 100% of its container width.

**Validates: Requirements 11.1**

### Property 37: Tablet Chart Height Range

*For any* viewport width between 768-1024 pixels, chart visualizations SHALL have heights between 300-400 pixels.

**Validates: Requirements 11.3**

### Property 38: Mobile Data Point Reduction

*For any* line chart on viewport width < 768px, the number of rendered data points SHALL be reduced by at least 30% compared to desktop rendering.

**Validates: Requirements 12.1**

### Property 39: Mobile Lazy Loading

*For any* visualization positioned below the fold on viewport width < 768px, it SHALL be lazy-loaded (not rendered until scrolled into view).

**Validates: Requirements 12.2**

### Property 40: First Contentful Paint Performance

*For any* dashboard load on a 3G network connection, First Contentful Paint SHALL occur within 2 seconds.

**Validates: Requirements 12.3**

### Property 41: Deferred Non-Critical JavaScript

*For any* non-critical JavaScript resource, it SHALL have defer or async attributes to avoid blocking initial render.

**Validates: Requirements 12.4**

### Property 42: Mobile Image Optimization

*For any* image on viewport width < 768px, the file size SHALL be <= 60% of the desktop version file size.

**Validates: Requirements 12.5**

### Property 43: Section Header Completeness

*For any* major content section, there SHALL be a section header containing a title and icon.

**Validates: Requirements 13.1, 13.2**

### Property 44: Section Header Subtitle Presence

*For any* section header, there SHALL be a descriptive subtitle explaining the content purpose.

**Validates: Requirements 13.3**

### Property 45: Section Header Spacing

*For any* section header, it SHALL have margin-top >= 24px and margin-bottom >= 16px.

**Validates: Requirements 13.4**

### Property 46: Section Header Typography Minimum

*For any* section header at any breakpoint, the header text SHALL have font size >= 18px.

**Validates: Requirements 13.5**

### Property 47: KPI Card Gradient Consistency

*For any* KPI row group, all cards within that group SHALL use consistent gradient colors matching their thematic grouping.

**Validates: Requirements 14.2**

### Property 48: Color Contrast Accessibility

*For any* text/background color pair, the contrast ratio SHALL be >= 4.5:1 to meet WCAG AA standards.

**Validates: Requirements 14.3**

### Property 49: Color-Blind Friendly Palettes

*For any* multi-category visualization, the color palette SHALL be from an approved color-blind safe palette set.

**Validates: Requirements 14.4**

### Property 50: Redundant Visual Encoding

*For any* critical data distinction, there SHALL be both color encoding and non-color visual cues (labels, patterns, or shapes).

**Validates: Requirements 14.5**

### Property 51: Hero Section Primary Metric Typography

*For any* Hero_Section, the national FI rate SHALL be displayed with font-size >= 2.5rem and font-weight >= 700.

**Validates: Requirements 15.3**

### Property 52: Quick Tips Conditional Display

*For any* dashboard load where localStorage does not contain a Quick_Tips dismissal flag, the Quick_Tips component SHALL be displayed in the Hero_Section.

**Validates: Requirements 15.5**

### Property 53: Icon and Image Alt Text

*For any* icon or image element, it SHALL have either an alt attribute or aria-label attribute with descriptive text.

**Validates: Requirements 16.1**

### Property 54: Keyboard Navigation Support

*For any* interactive element, it SHALL be keyboard accessible (focusable via Tab) and have visible focus indicators.

**Validates: Requirements 16.2**

### Property 55: Semantic Heading Hierarchy

*For any* rendered dashboard, HTML headings SHALL follow proper hierarchical order (h1 → h2 → h3) without skipping levels.

**Validates: Requirements 16.3**

### Property 56: ARIA Labels for Unlabeled Controls

*For any* interactive component without visible text labels, it SHALL have aria-label or aria-labelledby attributes.

**Validates: Requirements 16.4**

### Property 57: Form Control Label Association

*For any* form control (dropdown, button, input), it SHALL have an associated label element or aria-labelledby attribute.

**Validates: Requirements 16.5**

### Property 58: Visualization Text Alternatives

*For any* data visualization, there SHALL be an accessible alternative (data table or detailed aria-describedby description).

**Validates: Requirements 16.6**

### Property 59: Year Selection Storage

*For any* year selection change, the selected year SHALL be stored in sessionStorage.

**Validates: Requirements 17.1**

### Property 60: Year Selection Session Restoration

*For any* dashboard load within an existing browser session, if sessionStorage contains a year value, that year SHALL be restored as the selected year.

**Validates: Requirements 17.2**

### Property 61: Default Year Selection

*For any* dashboard load in a new browser session (no sessionStorage year), the selected year SHALL default to the maximum year in the dataset.

**Validates: Requirements 17.3**

### Property 62: Year Change Update Timing

*For any* year selection change, all visualizations and metrics SHALL update within 500 milliseconds.

**Validates: Requirements 17.4**

### Property 63: Year Change Loading Indicator

*For any* year selection change, a loading indicator SHALL be visible during the data filtering and visualization update process.

**Validates: Requirements 17.5**

### Property 64: Missing Data Graceful Degradation

*For any* KPI metric that cannot be calculated due to missing data, the KPI_Card SHALL display "N/A" instead of an error or empty value.

**Validates: Requirements 18.2**

### Property 65: Error Console Logging

*For any* error that occurs during dashboard operation, an error message SHALL be logged to the browser console.

**Validates: Requirements 18.4**

### Property 66: Year Validation Before Filtering

*For any* year selection, the dashboard SHALL validate that the year exists in the dataset before attempting to filter data.

**Validates: Requirements 18.5**

### Property 67: Print Mode CSS Application

*For any* print initiation, print-specific CSS styles SHALL be applied to the dashboard.

**Validates: Requirements 19.1**

### Property 68: Print Mode Section Expansion

*For any* print initiation, all collapsible sections SHALL be expanded to show complete content.

**Validates: Requirements 19.2**

### Property 69: Print Mode Interactive Element Removal

*For any* print initiation, interactive elements (buttons, dropdowns) SHALL be hidden or removed from the printed output.

**Validates: Requirements 19.3**

### Property 70: Print Mode Page Margins

*For any* print initiation, all content SHALL fit within standard page margins (1 inch on all sides).

**Validates: Requirements 19.4**

### Property 71: Print Mode Footer Information

*For any* print initiation, the page footer SHALL include the selected year and generation timestamp.

**Validates: Requirements 19.5**

### Property 72: LLM Explainer Input Context

*For any* LLM_Explainer invocation, it SHALL receive the selected year's national metrics as input context.

**Validates: Requirements 20.2**

### Property 73: National Trend Hover Insights

*For any* hover event on the National Trend chart, AI-generated insights about the trend pattern SHALL be displayed.

**Validates: Requirements 20.3**

### Property 74: LLM Output Length Constraint

*For any* LLM_Explainer output, the text SHALL be <= 150 words.

**Validates: Requirements 20.4**

### Property 75: LLM Content Transparency Indicator

*For any* LLM-generated content display, there SHALL be a visual indicator or label identifying it as AI-generated.

**Validates: Requirements 20.5**


## Error Handling

### Error Categories and Strategies

#### 1. Data Loading Errors

**Scenario**: Dataset fails to load or is corrupted

**Handling**:
- Display user-friendly error banner at top of dashboard
- Log detailed error to console for debugging
- Provide retry button to attempt reload
- Show empty state placeholders for visualizations

**Implementation**:
```python
try:
    data = load_data()
except Exception as e:
    st.error("Unable to load food insecurity data. Please refresh the page.")
    logging.error(f"Data loading failed: {e}")
    if st.button("Retry"):
        st.rerun()
    st.stop()
```

#### 2. Missing Data for Selected Year

**Scenario**: User selects a year with no data in dataset

**Handling**:
- Validate year exists before filtering
- Display warning banner explaining data unavailability
- Suggest alternative years with available data
- Maintain previous valid selection

**Implementation**:
```python
available_years = data["year"].unique()
if selected_year not in available_years:
    st.warning(f"Data for {selected_year} is not available. Showing {max(available_years)} instead.")
    selected_year = max(available_years)
```

#### 3. Metric Calculation Failures

**Scenario**: Metric cannot be calculated due to missing columns or null values

**Handling**:
- Display "N/A" in KPI cards instead of error
- Log warning to console with metric name
- Continue rendering other metrics
- Provide tooltip explaining why data is unavailable

**Implementation**:
```python
def safe_metric(data, column, aggregation="mean"):
    try:
        if column not in data.columns:
            logging.warning(f"Column {column} not found in dataset")
            return None
        result = getattr(data[column], aggregation)()
        return result if pd.notna(result) else None
    except Exception as e:
        logging.error(f"Metric calculation failed for {column}: {e}")
        return None

value = safe_metric(year_data, "overall_food_insecurity_rate")
display_value = f"{value:.1%}" if value is not None else "N/A"
```

#### 4. Visualization Rendering Failures

**Scenario**: Plotly chart fails to render due to data issues or library errors

**Handling**:
- Catch rendering exceptions
- Display fallback message with chart title
- Provide retry button
- Log error details to console
- Show data table as alternative

**Implementation**:
```python
try:
    fig = create_chart(data)
    st.plotly_chart(fig)
except Exception as e:
    st.error(f"Unable to render visualization. [Retry](#)")
    logging.error(f"Chart rendering failed: {e}")
    with st.expander("View data table instead"):
        st.dataframe(data)
```

#### 5. Viewport Detection Failures

**Scenario**: JavaScript viewport detection fails or returns invalid values

**Handling**:
- Default to desktop layout if viewport width is None
- Validate viewport width is positive integer
- Log warning if detection fails
- Provide manual breakpoint override in sidebar (dev mode)

**Implementation**:
```python
viewport = get_viewport_profile()
if viewport["width"] is None:
    logging.warning("Viewport detection failed, defaulting to desktop layout")
    viewport = {"width": 1920, "is_mobile": False, "is_portrait": False}
```

#### 6. LLM API Failures

**Scenario**: LLM explainer API call fails or times out

**Handling**:
- Catch API exceptions gracefully
- Display message explaining AI insights are temporarily unavailable
- Do not block dashboard rendering
- Provide fallback to static insights if available

**Implementation**:
```python
try:
    insights = generate_insights(page_name, context_dict)
    st.info(insights, icon="💡")
except Exception as e:
    st.warning("AI insights temporarily unavailable. Please try again later.")
    logging.error(f"LLM API failed: {e}")
```

#### 7. State Lookup Selection Errors

**Scenario**: Selected state code not found in dataset

**Handling**:
- Validate state code exists in dataset
- Display warning if state has no data
- Clear selection and reset to default view
- Log warning with state code

**Implementation**:
```python
selected_state = st.selectbox("State Lookup", state_options)
if selected_state:
    state_data = year_data[year_data["state"] == selected_state]
    if state_data.empty:
        st.warning(f"No data available for {STATE_NAMES[selected_state]}")
        selected_state = None
```

#### 8. Session Storage Failures

**Scenario**: Browser blocks localStorage/sessionStorage access

**Handling**:
- Wrap storage operations in try-except
- Fall back to session_state for persistence
- Log warning about storage unavailability
- Continue with default values

**Implementation**:
```python
def store_preference(key, value):
    try:
        # Attempt localStorage via JavaScript
        st.components.v1.html(f"<script>localStorage.setItem('{key}', '{value}')</script>")
    except Exception as e:
        # Fallback to session_state
        st.session_state[key] = value
        logging.warning(f"localStorage unavailable, using session_state: {e}")
```

### Error Logging Strategy

All errors SHALL be logged with the following information:
- Timestamp
- Error type/category
- Error message
- Stack trace (for exceptions)
- User context (selected year, viewport, browser info)

**Implementation**:
```python
import logging
import traceback

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def log_error(error, context=None):
    logging.error(f"Error: {error}")
    logging.error(f"Context: {context}")
    logging.error(f"Traceback: {traceback.format_exc()}")
```

## Testing Strategy

### Dual Testing Approach

This feature requires both unit testing and property-based testing to ensure comprehensive coverage:

- **Unit tests**: Verify specific examples, edge cases, error conditions, and integration points
- **Property tests**: Verify universal properties across all inputs through randomization

Together, these approaches provide comprehensive coverage where unit tests catch concrete bugs and property tests verify general correctness.

### Property-Based Testing

**Library**: Hypothesis (Python)

**Configuration**:
- Minimum 100 iterations per property test
- Each test tagged with reference to design document property
- Tag format: `# Feature: executive-overview-redesign, Property {number}: {property_text}`

**Example Property Test**:
```python
from hypothesis import given, strategies as st
import hypothesis

@given(
    year=st.integers(min_value=2009, max_value=2023),
    viewport_width=st.integers(min_value=320, max_value=2560)
)
@hypothesis.settings(max_examples=100)
def test_section_ordering_property(year, viewport_width):
    """
    Feature: executive-overview-redesign, Property 1: Section Ordering
    
    For any rendered dashboard, sections SHALL appear in the following order:
    Hero_Section, National Trend, Geographic_Section, State Rankings, Statistical Details
    """
    # Render dashboard with given year and viewport
    rendered_html = render_dashboard(year, viewport_width)
    
    # Extract section positions
    sections = extract_section_order(rendered_html)
    
    # Assert correct ordering
    expected_order = [
        "Hero_Section",
        "National Trend",
        "Geographic_Section",
        "State Rankings",
        "Statistical Details"
    ]
    assert sections == expected_order
```

**Property Test Coverage**:

Each of the 75 correctness properties SHALL be implemented as a property-based test. Key property tests include:

1. **Layout Properties** (Properties 1, 3-7, 9, 26-29): Test responsive layout behavior across viewport ranges
2. **Component Presence** (Properties 2, 6, 10, 14, 18-19, 43): Test required components exist
3. **Interaction Properties** (Properties 11-12, 15, 21-22, 24, 33, 35): Test user interactions produce expected results
4. **Accessibility Properties** (Properties 13, 31-32, 48, 53-58): Test WCAG compliance
5. **Performance Properties** (Properties 20, 33, 38-42, 62): Test timing and optimization constraints
6. **Data Handling Properties** (Properties 59-66): Test data persistence and error handling

**Generator Strategies**:

```python
# Viewport width generator covering all breakpoints
viewport_widths = st.one_of(
    st.integers(min_value=320, max_value=767),   # mobile
    st.integers(min_value=768, max_value=1024),  # tablet
    st.integers(min_value=1025, max_value=2560)  # desktop
)

# Year generator covering dataset range
years = st.integers(min_value=2009, max_value=2023)

# State code generator
state_codes = st.sampled_from([
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL",
    "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME",
    "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH",
    "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI",
    "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
])

# KPI metric generator
kpi_metrics = st.floats(min_value=0.0, max_value=1.0, allow_nan=False)

# Color contrast ratio generator
contrast_ratios = st.floats(min_value=1.0, max_value=21.0)
```

### Unit Testing

**Framework**: pytest

**Coverage Areas**:

#### 1. Component Rendering Tests

Test individual component functions with specific inputs:

```python
def test_hero_section_renders_with_valid_data():
    """Test hero section renders correctly with valid year and metrics."""
    result = hero_section(
        year=2023,
        primary_metric=0.123,
        previous_metric=0.118,
        context_summary="up 0.5% from 2022",
        show_quick_tips=True
    )
    assert "2023" in result
    assert "12.3%" in result
    assert "up 0.5% from 2022" in result

def test_hero_section_handles_missing_previous_year():
    """Test hero section handles None for previous_metric gracefully."""
    result = hero_section(
        year=2009,
        primary_metric=0.145,
        previous_metric=None,
        context_summary="first year in dataset",
        show_quick_tips=True
    )
    assert "2009" in result
    assert "14.5%" in result
    assert "N/A" not in result  # Should handle gracefully without showing N/A
```

#### 2. Data Calculation Tests

Test metric calculation functions with edge cases:

```python
def test_safe_pct_change_with_valid_values():
    """Test percentage change calculation with valid inputs."""
    result = safe_pct_change(0.123, 0.118)
    assert result == "+4.2%"

def test_safe_pct_change_with_zero_previous():
    """Test percentage change handles zero previous value."""
    result = safe_pct_change(0.123, 0)
    assert result == ""

def test_safe_pct_change_with_none_previous():
    """Test percentage change handles None previous value."""
    result = safe_pct_change(0.123, None)
    assert result == ""

def test_safe_pct_change_with_nan_current():
    """Test percentage change handles NaN current value."""
    result = safe_pct_change(np.nan, 0.118)
    assert result == ""
```

#### 3. Viewport Detection Tests

Test responsive behavior at breakpoint boundaries:

```python
def test_viewport_profile_mobile():
    """Test viewport profile correctly identifies mobile."""
    profile = ViewportProfile(width=767, is_mobile=True, is_portrait=True)
    assert profile.breakpoint_name == "mobile"
    assert profile.chart_height == 240
    assert profile.kpi_columns == 1

def test_viewport_profile_tablet():
    """Test viewport profile correctly identifies tablet."""
    profile = ViewportProfile(width=900, is_mobile=False, is_portrait=False)
    assert profile.breakpoint_name == "tablet"
    assert profile.chart_height == 350
    assert profile.kpi_columns == 2

def test_viewport_profile_desktop():
    """Test viewport profile correctly identifies desktop."""
    profile = ViewportProfile(width=1920, is_mobile=False, is_portrait=False)
    assert profile.breakpoint_name == "desktop"
    assert profile.chart_height == 450
    assert profile.kpi_columns == 4
```

#### 4. Error Handling Tests

Test error scenarios and graceful degradation:

```python
def test_missing_data_shows_na():
    """Test KPI card shows N/A for missing data."""
    value = safe_metric(empty_dataframe, "nonexistent_column")
    assert value is None
    display_value = f"{value:.1%}" if value is not None else "N/A"
    assert display_value == "N/A"

def test_invalid_year_selection():
    """Test invalid year selection shows warning."""
    with pytest.warns(UserWarning):
        result = validate_year_selection(1999, available_years=[2009, 2010, 2011])
    assert result == 2011  # Should default to max available year

def test_state_lookup_with_missing_state():
    """Test state lookup handles missing state gracefully."""
    result = get_state_summary("XX", year_data)
    assert result is None
```

#### 5. Integration Tests

Test component interactions and data flow:

```python
def test_year_selection_updates_all_metrics():
    """Test changing year updates all KPI cards and charts."""
    initial_state = render_dashboard(year=2022)
    updated_state = render_dashboard(year=2023)
    
    # Verify metrics changed
    assert initial_state["fi_rate"] != updated_state["fi_rate"]
    assert initial_state["chart_data"] != updated_state["chart_data"]

def test_state_lookup_highlights_map():
    """Test state selection highlights correct state on map."""
    result = handle_state_selection("CA", year_data)
    assert result["map_highlight"] == "CA"
    assert result["summary_card"]["state_name"] == "California"

def test_collapsible_section_persistence():
    """Test collapsible section state persists across interactions."""
    # Collapse section
    session_state = {"rankings_expanded": False}
    
    # Perform other action (e.g., change year)
    session_state["selected_year"] = 2023
    
    # Verify section state persisted
    assert session_state["rankings_expanded"] == False
```

#### 6. Accessibility Tests

Test WCAG compliance with specific examples:

```python
def test_all_images_have_alt_text():
    """Test all images have alt text or aria-label."""
    rendered_html = render_dashboard(year=2023, viewport_width=1920)
    soup = BeautifulSoup(rendered_html, 'html.parser')
    
    images = soup.find_all('img')
    for img in images:
        assert img.get('alt') or img.get('aria-label'), f"Image missing alt text: {img}"

def test_heading_hierarchy():
    """Test headings follow proper hierarchy."""
    rendered_html = render_dashboard(year=2023, viewport_width=1920)
    soup = BeautifulSoup(rendered_html, 'html.parser')
    
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
    levels = [int(h.name[1]) for h in headings]
    
    # Check no level skipping
    for i in range(len(levels) - 1):
        assert levels[i+1] - levels[i] <= 1, f"Heading hierarchy skip: {levels}"

def test_color_contrast_ratios():
    """Test text/background pairs meet 4.5:1 contrast ratio."""
    color_pairs = [
        ("#051C2C", "#FFFFFF"),  # dark on white
        ("#2251FF", "#FFFFFF"),  # blue on white
        ("#6B7F95", "#FFFFFF"),  # steel on white
    ]
    
    for fg, bg in color_pairs:
        ratio = calculate_contrast_ratio(fg, bg)
        assert ratio >= 4.5, f"Insufficient contrast: {fg} on {bg} = {ratio}"
```

### Test Execution

**Local Development**:
```bash
# Run all tests
pytest tests/

# Run only unit tests
pytest tests/unit/

# Run only property tests
pytest tests/property/

# Run with coverage
pytest --cov=views --cov-report=html

# Run specific property test
pytest tests/property/test_layout_properties.py::test_section_ordering_property -v
```

**CI/CD Integration**:
- Run full test suite on every pull request
- Require 80% code coverage minimum
- Run property tests with 100 iterations in CI
- Run accessibility tests with axe-core
- Performance tests on staging environment

### Test Data

**Fixtures**:
```python
@pytest.fixture
def sample_year_data():
    """Provide sample dataset for testing."""
    return pd.DataFrame({
        "year": [2023] * 51,
        "state": ["AL", "AK", ...],  # All 50 states + DC
        "overall_food_insecurity_rate": np.random.uniform(0.08, 0.18, 51),
        "child_food_insecurity_rate": np.random.uniform(0.10, 0.25, 51),
        "cost_per_meal": np.random.uniform(2.5, 4.5, 51),
        # ... other columns
    })

@pytest.fixture
def empty_data():
    """Provide empty dataset for error testing."""
    return pd.DataFrame()

@pytest.fixture
def missing_columns_data():
    """Provide dataset with missing columns for error testing."""
    return pd.DataFrame({
        "year": [2023],
        "state": ["CA"]
        # Missing all metric columns
    })
```

### Performance Testing

**Load Testing**:
- Test dashboard render time with full dataset (3000+ rows)
- Test chart rendering with maximum data points
- Test mobile lazy loading effectiveness

**Benchmarks**:
```python
def test_dashboard_render_performance(benchmark):
    """Test dashboard renders within acceptable time."""
    result = benchmark(render_dashboard, year=2023, viewport_width=1920)
    assert benchmark.stats.mean < 2.0  # Should render in < 2 seconds

def test_chart_render_performance(benchmark):
    """Test chart renders within acceptable time."""
    result = benchmark(create_trend_chart, trend_data)
    assert benchmark.stats.mean < 0.5  # Should render in < 500ms
```

### Manual Testing Checklist

In addition to automated tests, manual testing SHALL verify:

- [ ] Visual appearance matches design mockups
- [ ] Responsive breakpoints transition smoothly
- [ ] Touch interactions feel natural on mobile devices
- [ ] Tooltips appear in correct positions
- [ ] Print layout fits on standard paper
- [ ] Screen reader announces content correctly
- [ ] Keyboard navigation follows logical tab order
- [ ] LLM insights are contextually relevant
- [ ] Color schemes are visually appealing
- [ ] Loading states provide adequate feedback

