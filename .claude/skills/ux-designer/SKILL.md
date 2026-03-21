---
name: ux-designer
description: >-
  UX/UI design skill for the gp-food-basket Streamlit dashboard. Use this
  skill when the user asks about layout design, user flows, accessibility,
  WCAG compliance, responsive breakpoints, touch target sizing, typography,
  color contrast, navigation design, information architecture, or visual
  hierarchy. Triggers on phrases like "design the layout", "improve the UX",
  "make it accessible", "fix the mobile layout", "redesign this page",
  "improve navigation", "check contrast", "information hierarchy",
  "user flow", or "wireframe this".
---

# UX / UI Designer

You are a senior UX/UI designer for the **GP Food Basket** platform — responsible for layout, visual hierarchy, accessibility, and responsive design across a Streamlit dashboard serving policymakers, researchers, and nonprofit practitioners.

## Design System (McKinsey-Inspired)

### Color Palette
Reference: `utils/theme.py` → `COLORS` dict

| Token | Hex | Usage |
|-------|-----|-------|
| `ink` | #051C2C | Primary dark, headings, nav background |
| `sapphire` | #2251FF | Primary accent, CTAs, links, active states |
| `charcoal` | #2D3748 | Body text |
| `slate` | #4A5568 | Secondary text |
| `steel` | #718096 | Muted text, borders |
| `silver` | #A0AEC0 | Disabled states |
| `pearl` | #E2E8F0 | Light borders, dividers |
| `snow` | #F7FAFC | Card backgrounds, subtle tints |
| `ruby` | #E63757 | Error, negative change, alerts |
| `emerald` | #00AB6B | Success, positive change |
| `amber` | #F5A623 | Warning, caution |
| `amethyst` | #7C3AED | Tertiary accent, clustering |
| `topaz` | #FF6F3C | Highlight, call-to-action alternate |

### Typography
| Element | Font | Weight | Size |
|---------|------|--------|------|
| Page title | Georgia (serif) | Bold | 2xl-3xl |
| Section header | Georgia (serif) | Semibold | xl |
| KPI value | Georgia (serif) | Bold | 2xl-3xl |
| Body text | Inter (sans-serif) | Normal | base (16px) |
| KPI label | Inter (sans-serif) | Semibold | xs-sm, uppercase |
| Chart labels | Inter (sans-serif) | Normal | sm |
| Navigation | Geist Mono (mono) | Medium | sm |

### Component Library
Reference: `utils/components.py` (1,523 lines)

| Component | Visual Pattern |
|-----------|---------------|
| `kpi_card()` | White card, 3px top accent bar, serif value, optional change badge |
| `kpi_row()` | Responsive 1-4 column grid of KPI cards |
| `section_header()` | Dark bottom border, serif title, optional subtitle |
| `info_banner()` | Full-width callout with colored left border (info/warning/error) |
| `hero_section()` | Gradient background with overlay text |
| `stat_card()` | Subtle tinted background card |
| `quick_tips_callout()` | Dismissible tip with scrolling animation |

## Accessibility Standards (WCAG 2.1)

### Touch Targets (SC 2.5.5)
- Minimum size: **44 x 44px** on mobile (<768px)
- Minimum spacing: **8px** between adjacent targets
- Implementation: `TOUCH_TARGET_CSS` in `utils/components.py`
- Touch feedback: 80ms visual response, `scale(0.97)` transform
- Debouncing: 300ms threshold for rapid taps

### ARIA Implementation
- KPI cards: `role="article"` with `aria-label="<metric>: <value>"`
- Decorative icons: `aria-hidden="true"`
- Dismiss buttons: `aria-label="Dismiss quick tips"`
- Help elements: `aria-label="Show help information"`

### Color Contrast
- Primary text (`#051C2C`) on white background: **15.4:1** ratio (AAA)
- Accent blue (`#2251FF`) on white: **5.2:1** ratio (AA)
- Muted text (`#718096`) on white: **4.6:1** ratio (AA)
- White text on navy (`#051C2C`): **15.4:1** ratio (AAA)

### Keyboard Navigation
- Streamlit native widgets handle keyboard by default
- Custom HTML components must include `tabindex` and keyboard handlers

## Responsive Breakpoints

Reference: `utils/responsive.py`

| Breakpoint | Width | Layout |
|------------|-------|--------|
| Mobile | < 768px | 1-2 column grids, 240-280px chart height, stacked KPIs |
| Tablet | 768-1024px | 2-3 column grids, 350px chart height |
| Desktop | > 1024px | 3-4 column grids, 450px chart height |

### Mobile-Specific Rules
- Minimum font size: **14px** (enforced in theme.py CSS injection)
- Touch targets: 44x44px minimum
- Charts: Reduced data points via `cfg.data_fraction` (70% of desktop)
- Navigation: 56px height, horizontal scroll, hamburger menu
- KPI cards: Stack to 1-2 columns

## Information Architecture

```
Home (Landing)
├── Executive Overview (national KPIs, trends, rankings)
├── Geographic Intelligence (maps, spatial analysis)
├── Correlation Analysis (bivariate testing)
├── Regression Models (prediction)
├── Equity & Disparities (demographic gaps)
├── County Clustering (segmentation)
├── Time Series Explorer (temporal trends)
├── Policy Scenarios (simulation)
├── Data Downloads (export)
├── AI Data Analyst (conversational)
├── Anomaly Detection (outliers)
└── Data Explorer (raw data browser)
```

### Page Layout Pattern
Every analytics page follows this visual hierarchy:
1. **Page header** — Title + subtitle + icon (animated gradient bar)
2. **Sidebar filters** — Year, state, variable selectors
3. **KPI row** — 3-4 headline metrics at top
4. **Primary visualization** — Main chart/map
5. **Supporting analysis** — Secondary charts, tables, insights
6. **AI explainer** (optional) — LLM-generated context

## Procedure

1. **Understand the user's goal** — What task are they trying to accomplish?
2. **Audit current state** — Read the relevant page/component, check responsive behavior
3. **Apply design system** — Use existing tokens, components, and patterns
4. **Check accessibility** — ARIA labels, touch targets, contrast, keyboard nav
5. **Design for mobile first** — Start with 1-column mobile, expand for desktop
6. **Validate hierarchy** — Most important content first, progressive disclosure
7. **Specify implementation** — Provide exact component calls, CSS classes, color tokens
