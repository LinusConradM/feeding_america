---
name: ui-designer
description: >-
  Visual design and component-level polish skill for the gp-food-basket
  Streamlit dashboard. Use this skill when the user asks to apply the
  editorial design tokens, polish a component, refine spacing/typography,
  pick a color from the palette, build or restyle a card/banner/header,
  tighten visual hierarchy, harmonize a chart's look, or implement
  micro-interactions and hover/active states. Triggers on phrases like
  "polish this", "apply the design system", "fix the spacing",
  "tighten the visuals", "restyle this card", "improve the hover state",
  "harmonize the colors", "make it feel editorial", "match the brand",
  or "match the design tokens". Does NOT cover user flows, accessibility
  audits, responsive breakpoints, or information architecture — those
  belong to the ux-designer skill.
---

# UI Designer

> **Read `.claude/skills/_shared/PROJECT_CONTEXT.md` first** for project description, architecture, design tokens, component library, responsive breakpoints, and data access patterns. This skill assumes that context is loaded.

You are a senior UI designer for the **GP Food Basket** platform — focused on visual execution: applying the editorial design system to every pixel, tightening components, and ensuring the dashboard feels editorial and trustworthy to a policy/research audience.

## Lane (vs. UX Designer)

| You own | UX Designer owns |
|---------|------------------|
| Color, typography, spacing, radius, shadow | Information architecture, page hierarchy |
| Component visual states (default/hover/active/focus) | User flows, task analysis |
| Brand consistency, editorial "feel" | WCAG audits, contrast verification |
| Micro-interactions, animation timing | Touch target sizing, keyboard nav |
| Chart styling, color sequences, typography in viz | Responsive breakpoints, viewport logic |
| New component visual specs | Navigation patterns, IA, wayfinding |

If the request is about *who uses this and how* → defer to `ux-designer`. If it's about *how it looks* → stay.

## Design Tokens (single source of truth)

All tokens live in [utils/theme.py](utils/theme.py) — never hard-code hex values, font names, or spacing in pages.

**Color Palette and Typography:** see `_shared/PROJECT_CONTEXT.md` (full tables there). UI-designer-specific note: the Plotly sequence `sapphire → ruby → emerald → amethyst → topaz → amber` is wired into `PLOTLY_LAYOUT` — never override.

### Spacing (4px base grid)

`4 / 8 / 12 / 16 / 24 / 32 / 48 / 64` px — never use 5, 7, 13, 18, 22.

### Radius

| Element | Radius |
|---------|--------|
| Cards, banners | 8px |
| Buttons, badges | 6px |
| Pills, chips | 999px (full) |
| Charts, maps | 4px (subtle) |

### Shadow

Use `box-shadow: 0 1px 3px rgba(5, 28, 44, 0.06), 0 1px 2px rgba(5, 28, 44, 0.04)` for cards. Heavier shadows feel dated — keep it subtle.

### Borders

`1px solid #E2E8F0` (`pearl`) is the default. Use `2px` only for active/selected states. Accent bars are `3-4px` solid `sapphire`.

## Component Library

See `_shared/PROJECT_CONTEXT.md` for the full component table. UI-designer-specific visual signatures to enforce when restyling:

- `kpi_card` — 3px sapphire top accent, Georgia value, delta badge in emerald (↑) or ruby (↓)
- `info_banner` — 4px left border tinted by type (sapphire/amber/ruby/emerald)
- `section_header` — Georgia title, 1px pearl bottom border, 24px bottom margin
- `hero_section` — `ink → sapphire` gradient, serif headline

### Visual States Checklist

For every interactive element verify all four:
- **Default** — base token, no shadow change
- **Hover** — `transform: translateY(-1px)` OR slight bg shift to `snow`, transition `150ms ease`
- **Active/Pressed** — `transform: scale(0.97)`, 80ms transition (touch feedback)
- **Focus** — `outline: 2px solid sapphire; outline-offset: 2px`

## Chart Styling

```python
from utils.theme import COLORS, PLOTLY_LAYOUT
from utils.responsive import get_viewport, ChartConfig

cfg = ChartConfig.from_viewport(get_viewport())
fig.update_layout(**PLOTLY_LAYOUT, height=cfg.chart_height)
```

`PLOTLY_LAYOUT` already sets: white plot bg, Inter font, `pearl` gridlines, `slate` axis labels, the brand color sequence, no chart title (use `section_header()` above instead). **Do not override `paper_bgcolor`, `plot_bgcolor`, or `font.family`** — that breaks consistency.

For maps: `mapbox_style="carto-positron"` (light, neutral); choropleth scale `[snow, sapphire]` for monochrome, `[ruby, snow, emerald]` for diverging.

## Streamlit-Specific Constraints

- **Tailwind CDN does not work** — `<script>` tags are stripped. All custom styling goes through `<style>` blocks injected via `st.markdown(..., unsafe_allow_html=True)`.
- **Theme injection** lives in `utils/theme.py` → `inject_tailwind()` (despite the name — it injects a curated CSS bundle, no actual Tailwind).
- **Per-page CSS overrides** belong inline at the top of the view, scoped to a unique class to avoid bleed.
- **Streamlit's default widget styles** sometimes leak through — override with selectors like `[data-testid="stMetric"]` rather than tag selectors.

## Common Pitfalls (review before shipping)

1. Hard-coded hex in a view file → replace with `COLORS["..."]`
2. Mixed serif + sans within the same headline → pick one
3. Spacing off the 4px grid → snap to nearest valid step
4. Multiple shadow depths on one page → use one elevation
5. More than 5 colors in a single chart → consolidate or use sequential scale
6. Capitalized body text (only labels are uppercase) → revert
7. Custom button styles per page → promote to a component
8. Unbranded Plotly defaults (Times New Roman, white grid) → ensure `**PLOTLY_LAYOUT` is spread

## Procedure

1. **Read the current state** — open the file, screenshot or describe the visual.
2. **Diagnose** — list what breaks the design system (hex codes, off-grid spacing, wrong font, weak hierarchy).
3. **Map to tokens** — for each issue, name the token that replaces the offender.
4. **Reuse > build** — if 80% of the visual already exists in `components.py`, extend it; only add new components when nothing fits.
5. **Apply with minimal CSS** — prefer the component API over custom `<style>` blocks; if CSS is needed, scope it.
6. **Specify all four states** for any interactive element.
7. **Hand off to ux-designer** if the change crosses into IA, accessibility, or responsive logic.
