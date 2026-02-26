# Implementation Plan: Executive Overview Redesign

## Overview

This implementation plan transforms the Executive Overview dashboard (views/1_Executive_Overview.py) into a story-driven, mobile-responsive experience with enhanced visual hierarchy and interactive features. The implementation follows a component-first approach, building reusable UI components in utils/components.py, enhancing data models in utils/responsive.py, then reorganizing the main dashboard file.

The plan prioritizes incremental validation through checkpoints and includes property-based testing with Hypothesis to verify the 75 correctness properties defined in the design document.

## Implementation Strategy

1. Build foundation: Data models and responsive utilities
2. Create new interactive components with accessibility built-in
3. Enhance existing components for responsive behavior
4. Reorganize main dashboard with new content flow
5. Implement performance optimizations for mobile
6. Add comprehensive error handling
7. Validate with property-based and unit tests

## Tasks

### 1. Foundation: Data Models and Responsive Utilities

- [x] 1.1 Enhance ViewportProfile data model in utils/responsive.py
  - Add breakpoint_name property ("mobile", "tablet", "desktop")
  - Add chart_height property with viewport-specific heights
  - Add kpi_columns property for responsive grid layout
  - _Requirements: 8.1, 8.2, 8.3, 9.1, 9.2, 9.3, 11.2, 11.3, 11.4_

- [x] 1.2 Write property test for ViewportProfile
  - **Property 25, 28, 37: Chart height ranges by viewport**
  - **Validates: Requirements 8.3, 9.3, 11.2, 11.3, 11.4**

- [x] 1.3 Create ChartConfig data model in utils/responsive.py
  - Implement ChartConfig dataclass with height, margin, font_size, marker_size, line_width, show_legend, data_point_reduction
  - Implement for_viewport() class method to generate viewport-specific configs
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 12.1_

- [x] 1.4 Write property test for ChartConfig
  - **Property 36, 38: Chart responsive width and mobile data reduction**
  - **Validates: Requirements 11.1, 12.1**

- [x] 1.5 Create StateSummary data model in utils/responsive.py
  - Implement StateSummary dataclass with state_code, state_name, fi_rate, rank, total_states, food_insecure_persons, cost_per_meal, poverty_rate
  - Implement to_display_dict() method for formatted output
  - _Requirements: 4.4_

### 2. New Interactive Components

- [x] 2.1 Implement hero_section component in utils/components.py
  - Create hero_section() function with year, primary_metric, previous_metric, context_summary, show_quick_tips parameters
  - Display year with badge styling
  - Display primary metric with large typography (3rem desktop, 2.5rem mobile)
  - Generate contextual summary with year-over-year comparison
  - Apply gradient background styling
  - _Requirements: 1.2, 15.2, 15.3, 15.4_

- [x] 2.2 Write property test for hero_section
  - **Property 2, 51: Hero section content completeness and typography**
  - **Validates: Requirements 1.2, 15.2, 15.3, 15.4_

- [x] 2.3 Write unit tests for hero_section
  - Test rendering with valid data
  - Test handling of None previous_metric
  - Test typography scaling across viewports
  - _Requirements: 1.2, 15.3_

- [x] 2.4 Implement quick_tips_callout component in utils/components.py
  - Create quick_tips_callout() function with tips list and dismissible flag
  - Style as info banner with lightbulb icon
  - Add dismiss button with localStorage persistence via st.components.v1.html
  - Check localStorage on load to determine visibility
  - _Requirements: 7.2, 7.4, 7.5_

- [x] 2.5 Write property test for quick_tips_callout
  - **Property 23, 24, 52: Quick tips content range and dismissal persistence**
  - **Validates: Requirements 7.2, 7.4, 7.5**

- [x] 2.6 Implement state_lookup_component in utils/components.py
  - Create state_lookup_component() function with year_data, state_names, on_state_select parameters
  - Use st.selectbox with alphabetically sorted state list
  - Implement format_func for display names
  - Return selected state code
  - _Requirements: 4.2, 4.5_

- [x] 2.7 Write property test for state_lookup_component
  - **Property 10, 13: State lookup completeness and keyboard accessibility**
  - **Validates: Requirements 4.2, 4.5**

- [x] 2.8 Implement collapsible_section wrapper in utils/components.py
  - Create collapsible_section() function wrapping st.expander
  - Add title, content_func, icon, default_expanded, key parameters
  - Persist state in st.session_state
  - Apply custom CSS for chevron icon animation
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 2.9 Write property test for collapsible_section
  - **Property 14, 15, 16, 17: Collapsible section implementation and behavior**
  - **Validates: Requirements 5.1, 5.2, 5.3, 5.4**

- [x] 2.10 Implement tooltip_wrapper component in utils/components.py
  - Create tooltip_wrapper() function with content, tooltip_text, icon, position parameters
  - Implement CSS-only hover tooltip for desktop (200ms delay)
  - Use st.popover for mobile tap interaction
  - Ensure 44x44px touch target for mobile
  - _Requirements: 6.3, 6.4, 6.5, 10.1_

- [x] 2.11 Write property test for tooltip_wrapper
  - **Property 20, 21, 22, 31: Tooltip timing, interaction, and touch target sizing**
  - **Validates: Requirements 6.3, 6.4, 6.5, 10.1**

### 3. Checkpoint - Verify Component Foundation

- [x] 3.1 Ensure all new component tests pass
  - Run pytest on utils/components.py tests
  - Verify all property tests pass with 100 iterations
  - Ask the user if questions arise

### 4. Enhanced Existing Components

- [x] 4.1 Enhance kpi_card component in utils/components.py
  - Add tooltip_text parameter to existing kpi_card() function
  - Integrate tooltip_wrapper for contextual help
  - Ensure ARIA labels for accessibility
  - _Requirements: 6.1, 16.4_

- [x] 4.2 Write property test for kpi_card tooltips
  - **Property 18: KPI card tooltip presence**
  - **Validates: Requirements 6.1**

- [x] 4.3 Create kpi_row_grouped component in utils/components.py
  - Implement kpi_row_grouped() function with row_groups and viewport_profile parameters
  - Add row group headers ("Core Food Insecurity Metrics", "Economic Drivers")
  - Adjust grid columns based on viewport (4 cols desktop, 2 cols tablet, 1 col mobile)
  - Maintain row groupings in mobile stacking
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 4.4 Write property test for kpi_row_grouped
  - **Property 3, 4, 5: KPI card row grouping and responsive layout**
  - **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**

- [x] 4.5 Create geographic_section component in utils/components.py
  - Implement geographic_section() function with year_data, selected_year, viewport_profile parameters
  - Desktop: 3-column layout with 60/20/20 split (map | regional | urban/rural)
  - Tablet: 2-row layout (map + regional in row 1, urban/rural in row 2)
  - Mobile: Vertical stack (map → regional → urban/rural)
  - Apply consistent color scales across all three visualizations
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 14.1_

- [x] 4.6 Write property test for geographic_section
  - **Property 6, 7, 8, 9: Geographic section completeness, layout, and color consistency**
  - **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 14.1**

- [x] 4.7 Enhance section_header component in utils/components.py
  - Add subtitle parameter to existing section_header() function
  - Ensure consistent spacing (24px top, 16px bottom)
  - Ensure minimum 18px font size across breakpoints
  - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_

- [x] 4.8 Write property test for section_header
  - **Property 43, 44, 45, 46: Section header completeness, subtitle, spacing, typography**
  - **Validates: Requirements 13.1, 13.2, 13.3, 13.4, 13.5**

### 5. Main Dashboard Reorganization

- [x] 5.1 Reorganize views/1_Executive_Overview.py with new section order
  - Implement section ordering: Hero_Section, National Trend, Geographic_Section, State Rankings, Statistical Details
  - Maintain narrative flow from national to state-level scope
  - _Requirements: 1.1, 1.3_

- [x] 5.2 Write property test for section ordering
  - **Property 1: Section ordering**
  - **Validates: Requirements 1.1, 1.3**

- [x] 5.3 Implement Hero Section in views/1_Executive_Overview.py
  - Calculate national FI rate for selected year
  - Calculate previous year's FI rate for comparison
  - Generate contextual summary sentence
  - Render hero_section component
  - Conditionally render quick_tips_callout based on localStorage
  - Integrate existing llm_explainer_ui component
  - _Requirements: 1.2, 7.5, 15.1, 15.2, 15.3, 15.4, 15.5, 20.1, 20.2_

- [x] 5.4 Write unit tests for Hero Section integration
  - Test metric calculations
  - Test contextual summary generation
  - Test LLM explainer integration
  - _Requirements: 1.2, 15.4, 20.2_

- [x] 5.5 Reorganize KPI Cards section in views/1_Executive_Overview.py
  - Define two row groups: Core FI Metrics and Economic Drivers
  - Row 1: National FI Rate, Food Insecure Persons, Child FI Rate, Cost Per Meal
  - Row 2: Poverty Rate, Median Income, Unemployment, Budget Shortfall
  - Add tooltip text for each metric
  - Render using kpi_row_grouped component
  - _Requirements: 2.1, 2.2, 2.3, 6.1_

- [x] 5.6 Write property test for KPI Cards layout
  - **Property 3, 4, 5: KPI row grouping and responsive behavior**
  - **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**

- [x] 5.7 Enhance National Trend Chart section in views/1_Executive_Overview.py
  - Apply ChartConfig.for_viewport() for responsive sizing
  - Add tooltip with AI-generated insights on hover
  - Reduce data points by 30% for mobile viewports
  - _Requirements: 6.2, 11.1, 11.2, 11.3, 11.4, 12.1, 20.3_

- [x] 5.8 Write property test for chart responsive sizing
  - **Property 36, 37, 38: Chart responsive width, height ranges, data reduction**
  - **Validates: Requirements 11.1, 11.2, 11.3, 11.4, 12.1**

- [x] 5.9 Implement Geographic Section in views/1_Executive_Overview.py
  - Consolidate state map, regional comparison, urban/rural comparison
  - Render using geographic_section component
  - Apply consistent color scales (teal/amber/rose)
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 14.1_

- [x] 5.10 Implement State Lookup feature in views/1_Executive_Overview.py
  - Render state_lookup_component
  - On state selection, highlight state on map using Plotly selectedpoints
  - Display StateSummary card with state metrics
  - Scroll to map section using st.experimental_set_query_params
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 5.11 Write property test for state lookup interaction
  - **Property 11, 12: State selection map highlighting and summary display**
  - **Validates: Requirements 4.3, 4.4**

- [x] 5.12 Implement State Rankings as collapsible section in views/1_Executive_Overview.py
  - Wrap State Rankings in collapsible_section component
  - Desktop: 2-column layout (top 10 | bottom 10)
  - Tablet: 2-column layout
  - Mobile: 1-column layout (top 10 above bottom 10)
  - Default to expanded state
  - _Requirements: 5.1, 8.4, 9.4_

- [x] 5.13 Write property test for State Rankings layout
  - **Property 26, 29: Desktop and mobile State Rankings layout**
  - **Validates: Requirements 8.4, 9.4**

- [x] 5.14 Implement Statistical Details as collapsible section in views/1_Executive_Overview.py
  - Create Statistical Details section with key statistics cards
  - Wrap in collapsible_section component
  - Default to expanded state
  - _Requirements: 5.1_

### 6. Checkpoint - Verify Dashboard Reorganization

- [x] 6.1 Ensure dashboard renders correctly across viewports
  - Test on desktop (>1024px), tablet (768-1024px), mobile (<768px)
  - Verify section ordering and content flow
  - Verify all interactive features work
  - Ask the user if questions arise

### 7. Responsive Design and Performance

- [x] 7.1 Implement mobile typography adjustments in utils/theme.py
  - Ensure body text >= 14px on mobile
  - Scale heading sizes appropriately
  - _Requirements: 9.5_

- [x] 7.2 Write property test for mobile typography
  - **Property 30: Mobile typography minimum**
  - **Validates: Requirements 9.5**

- [x] 7.3 Implement touch target sizing for mobile in utils/components.py
  - Ensure all interactive elements have 44x44px minimum touch targets on mobile
  - Add 8px spacing between adjacent touch targets
  - _Requirements: 10.1, 10.2_

- [x] 7.4 Write property test for touch target sizing
  - **Property 31, 32: Mobile touch target sizing and spacing**
  - **Validates: Requirements 10.1, 10.2**

- [x] 7.5 Implement touch interaction feedback in utils/components.py
  - Add visual feedback (color change or scale animation) within 100ms
  - Implement debouncing for rapid taps (300ms threshold)
  - _Requirements: 10.3, 10.5_

- [x] 7.6 Write property test for touch interaction feedback
  - **Property 33, 35: Touch feedback timing and rapid tap debouncing**
  - **Validates: Requirements 10.3, 10.5**

- [x] 7.7 Enable pinch-to-zoom for map on mobile
  - Configure Plotly map with dragmode='zoom' for mobile
  - Test pinch-to-zoom gestures
  - _Requirements: 10.4_

- [x] 7.8 Write property test for map pinch-zoom
  - **Property 34: Map pinch-zoom support**
  - **Validates: Requirements 10.4**

- [ ] 7.9 Implement lazy loading for below-fold content on mobile
  - Identify visualizations below the fold
  - Implement lazy loading using st.empty() placeholders
  - Render on scroll into view
  - _Requirements: 12.2_

- [ ] 7.10 Write property test for mobile lazy loading
  - **Property 39: Mobile lazy loading**
  - **Validates: Requirements 12.2**

- [ ] 7.11 Optimize JavaScript loading for performance
  - Add defer/async attributes to non-critical JavaScript
  - Measure First Contentful Paint timing
  - _Requirements: 12.3, 12.4_

- [ ] 7.12 Write property test for performance metrics
  - **Property 40, 41: First Contentful Paint and deferred JavaScript**
  - **Validates: Requirements 12.3, 12.4**

- [ ] 7.13 Optimize images for mobile
  - Compress images to reduce file size by 40%
  - Serve appropriately sized images based on viewport
  - _Requirements: 12.5_

- [ ] 7.14 Write property test for mobile image optimization
  - **Property 42: Mobile image optimization**
  - **Validates: Requirements 12.5**

### 8. Accessibility Implementation

- [ ] 8.1 Add alt text and ARIA labels to all icons and images
  - Audit all img elements for alt attributes
  - Add aria-label to icon-only buttons
  - _Requirements: 16.1_

- [ ] 8.2 Write property test for alt text and ARIA labels
  - **Property 53, 56: Icon/image alt text and ARIA labels for unlabeled controls**
  - **Validates: Requirements 16.1, 16.4**

- [ ] 8.3 Implement keyboard navigation for all interactive elements
  - Ensure all interactive elements are focusable via Tab
  - Add visible focus indicators
  - Test tab order follows logical flow
  - _Requirements: 16.2_

- [ ] 8.4 Write property test for keyboard navigation
  - **Property 54: Keyboard navigation support**
  - **Validates: Requirements 16.2**

- [ ] 8.5 Implement semantic HTML heading hierarchy
  - Use h1 for page title, h2 for major sections, h3 for subsections
  - Ensure no heading levels are skipped
  - _Requirements: 16.3_

- [ ] 8.6 Write property test for heading hierarchy
  - **Property 55: Semantic heading hierarchy**
  - **Validates: Requirements 16.3**

- [ ] 8.7 Add labels to all form controls
  - Ensure all dropdowns, buttons, inputs have associated labels
  - Use aria-labelledby where visual labels are not present
  - _Requirements: 16.5_

- [ ] 8.8 Write property test for form control labels
  - **Property 57: Form control label association**
  - **Validates: Requirements 16.5**

- [ ] 8.9 Add text alternatives for data visualizations
  - Provide aria-describedby descriptions for charts
  - Offer data table alternatives in expanders
  - _Requirements: 16.6_

- [ ] 8.10 Write property test for visualization text alternatives
  - **Property 58: Visualization text alternatives**
  - **Validates: Requirements 16.6**

- [ ] 8.11 Verify color contrast ratios meet WCAG AA standards
  - Test all text/background pairs for 4.5:1 contrast ratio
  - Use color-blind friendly palettes for multi-category visualizations
  - Add non-color visual cues (labels, patterns) for critical distinctions
  - _Requirements: 14.3, 14.4, 14.5_

- [ ] 8.12 Write property test for color accessibility
  - **Property 48, 49, 50: Color contrast, color-blind palettes, redundant encoding**
  - **Validates: Requirements 14.3, 14.4, 14.5**

### 9. Checkpoint - Verify Accessibility and Performance

- [ ] 9.1 Run accessibility audit with axe-core
  - Fix any WCAG AA violations
  - Test with screen reader (NVDA or JAWS)
  - Verify keyboard navigation flow
  - Ask the user if questions arise

### 10. Error Handling and Data Validation

- [ ] 10.1 Implement data loading error handling
  - Wrap data loading in try-except
  - Display user-friendly error banner
  - Provide retry button
  - Log detailed error to console
  - _Requirements: 18.1_

- [ ] 10.2 Write unit test for data loading errors
  - Test error banner display
  - Test retry functionality
  - _Requirements: 18.1_

- [ ] 10.3 Implement missing data graceful degradation
  - Display "N/A" in KPI cards for missing metrics
  - Show warning for unavailable year data
  - Suggest alternative years
  - _Requirements: 18.2_

- [ ] 10.4 Write property test for missing data handling
  - **Property 64: Missing data graceful degradation**
  - **Validates: Requirements 18.2**

- [ ] 10.5 Implement visualization rendering error handling
  - Catch Plotly rendering exceptions
  - Display fallback message with retry option
  - Offer data table alternative
  - _Requirements: 18.3_

- [ ] 10.6 Write unit test for visualization errors
  - Test fallback message display
  - Test data table alternative
  - _Requirements: 18.3_

- [ ] 10.7 Implement year validation before filtering
  - Validate selected year exists in dataset
  - Default to most recent year if invalid
  - _Requirements: 18.5_

- [ ] 10.8 Write property test for year validation
  - **Property 66: Year validation before filtering**
  - **Validates: Requirements 18.5**

- [ ] 10.9 Implement error console logging
  - Log all errors with timestamp, type, message, stack trace
  - Include user context (year, viewport, browser)
  - _Requirements: 18.4_

- [ ] 10.10 Write property test for error logging
  - **Property 65: Error console logging**
  - **Validates: Requirements 18.4**

- [ ] 10.11 Implement LLM API error handling
  - Catch API exceptions gracefully
  - Display "AI insights temporarily unavailable" message
  - Do not block dashboard rendering
  - _Requirements: 20.2, 20.3_

- [ ] 10.12 Write unit test for LLM API errors
  - Test graceful degradation
  - Test dashboard continues rendering
  - _Requirements: 20.2, 20.3_

- [ ] 10.13 Implement state lookup selection error handling
  - Validate state code exists in dataset
  - Display warning if state has no data
  - Clear selection and reset to default view
  - _Requirements: 4.3, 4.4_

- [ ] 10.14 Write unit test for state lookup errors
  - Test invalid state code handling
  - Test missing state data warning
  - _Requirements: 4.3, 4.4_

- [ ] 10.15 Implement session storage error handling
  - Wrap localStorage operations in try-except
  - Fall back to session_state for persistence
  - Log warning about storage unavailability
  - _Requirements: 17.1, 17.2_

- [ ] 10.16 Write unit test for session storage errors
  - Test localStorage fallback
  - Test session_state persistence
  - _Requirements: 17.1, 17.2_

### 11. Year Selection and State Persistence

- [ ] 11.1 Implement year selection storage in sessionStorage
  - Store selected year on change
  - Restore year from sessionStorage on load
  - Default to most recent year for new sessions
  - _Requirements: 17.1, 17.2, 17.3_

- [ ] 11.2 Write property test for year selection persistence
  - **Property 59, 60, 61: Year selection storage, restoration, default**
  - **Validates: Requirements 17.1, 17.2, 17.3**

- [ ] 11.3 Implement year change update timing
  - Update all visualizations within 500ms of year change
  - Display loading indicator during update
  - _Requirements: 17.4, 17.5_

- [ ] 11.4 Write property test for year change timing
  - **Property 62, 63: Year change update timing and loading indicator**
  - **Validates: Requirements 17.4, 17.5**

### 12. Print-Friendly Layout

- [ ] 12.1 Implement print-specific CSS styles
  - Create print media query styles
  - Expand all collapsible sections for print
  - Hide interactive elements (buttons, dropdowns)
  - Ensure content fits within standard page margins
  - Add footer with year and timestamp
  - _Requirements: 19.1, 19.2, 19.3, 19.4, 19.5_

- [ ] 12.2 Write property test for print mode
  - **Property 67, 68, 69, 70, 71: Print CSS, section expansion, element removal, margins, footer**
  - **Validates: Requirements 19.1, 19.2, 19.3, 19.4, 19.5**

### 13. LLM Integration and Insights

- [ ] 13.1 Enhance LLM explainer with year-specific context
  - Pass selected year's national metrics to LLM
  - Generate contextual insights for Hero Section
  - _Requirements: 20.1, 20.2_

- [ ] 13.2 Write property test for LLM input context
  - **Property 72: LLM explainer input context**
  - **Validates: Requirements 20.2**

- [ ] 13.3 Implement hover insights for National Trend chart
  - Add hover event handler to chart
  - Display AI-generated insights about trend pattern
  - _Requirements: 20.3_

- [ ] 13.4 Write property test for chart hover insights
  - **Property 73: National trend hover insights**
  - **Validates: Requirements 20.3**

- [ ] 13.5 Implement LLM output length constraint
  - Truncate LLM output to 150 words maximum
  - Add "Read more" link if truncated
  - _Requirements: 20.4_

- [ ] 13.6 Write property test for LLM output length
  - **Property 74: LLM output length constraint**
  - **Validates: Requirements 20.4**

- [ ] 13.7 Add transparency indicator for LLM content
  - Display "AI-generated" badge or label
  - Add icon to identify AI content
  - _Requirements: 20.5_

- [ ] 13.8 Write property test for LLM transparency
  - **Property 75: LLM content transparency indicator**
  - **Validates: Requirements 20.5**

### 14. Color Scheme and Visual Consistency

- [ ] 14.1 Implement consistent color scales for geographic visualizations
  - Define color scale: teal (low) → amber (medium) → rose (high)
  - Apply to state map, regional comparison, urban/rural comparison
  - _Requirements: 3.4, 14.1_

- [ ] 14.2 Write property test for color scale consistency
  - **Property 8: Geographic color scale consistency**
  - **Validates: Requirements 3.4, 14.1**

- [ ] 14.3 Implement KPI card gradient consistency
  - Define gradient colors for Core FI Metrics row
  - Define gradient colors for Economic Drivers row
  - Apply consistently within row groups
  - _Requirements: 14.2_

- [ ] 14.4 Write property test for KPI gradient consistency
  - **Property 47: KPI card gradient consistency**
  - **Validates: Requirements 14.2**

### 15. Final Integration and Testing

- [x] 15.1 Run complete property-based test suite
  - Execute all 75 property tests with 100 iterations each
  - Fix any failing properties
  - Document any edge cases discovered

- [ ] 15.2 Run complete unit test suite
  - Execute all unit tests for components and integration
  - Achieve minimum 80% code coverage
  - Fix any failing tests

- [ ] 15.3 Perform manual testing across devices
  - Test on desktop (Chrome, Firefox, Safari)
  - Test on tablet (iPad, Android tablet)
  - Test on mobile (iPhone, Android phone)
  - Verify responsive breakpoints transition smoothly
  - Test touch interactions feel natural

- [ ] 15.4 Perform accessibility audit
  - Run axe-core automated accessibility tests
  - Test with screen reader (NVDA or JAWS)
  - Verify keyboard navigation follows logical tab order
  - Test color contrast with accessibility tools

- [ ] 15.5 Performance testing and optimization
  - Measure First Contentful Paint on 3G network
  - Verify lazy loading works on mobile
  - Test dashboard render time with full dataset
  - Optimize any performance bottlenecks

- [ ] 15.6 Final checkpoint - Ensure all tests pass
  - Verify all property tests pass
  - Verify all unit tests pass
  - Verify accessibility audit passes
  - Verify performance benchmarks met
  - Ask the user if questions arise

## Notes

- Tasks marked with `*` are optional testing tasks and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties with Hypothesis
- Unit tests validate specific examples and edge cases with pytest
- Checkpoints ensure incremental validation at logical breaks
- All code examples use Python with Streamlit framework
- Testing uses Hypothesis for property-based tests and pytest for unit tests
- Accessibility compliance targets WCAG 2.1 AA standards
- Performance targets: <2s First Contentful Paint on 3G, <500ms year change updates
