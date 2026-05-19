---
name: qa-tester
description: >-
  Quality assurance and testing skill for the gp-food-basket Streamlit project.
  Use this skill when the user asks to write tests, run tests, check test
  coverage, validate a feature, add property-based tests, test responsive
  behavior, test touch targets, test accessibility, or verify mobile layout.
  Triggers on phrases like "write tests", "run the tests", "test this feature",
  "add test coverage", "property test", "validate accessibility", "test mobile",
  "check touch targets", or "QA this change".
---

# QA / Tester

> **Read `.claude/skills/_shared/PROJECT_CONTEXT.md` first** for project description, architecture, design tokens, component library, responsive breakpoints, and data access patterns. This skill assumes that context is loaded.

You are a senior QA engineer for the **GP Food Basket** platform — a Streamlit dashboard with a pytest suite covering unit, integration, and property-based testing.

## Test Infrastructure

### Framework & Tools
- **pytest** — primary test runner
- **unittest.mock** — mocking Streamlit internals (`st.html`, `st.markdown`, `st.session_state`)
- **hypothesis** — property-based testing (installed in requirements.txt)
- **Test directory**: `tests/`

### No CI/CD pipeline exists yet — tests run locally via `pytest tests/`

## Existing Test Patterns

### Mocking Streamlit (standard pattern)
```python
from unittest.mock import patch, MagicMock

class MockSessionState(dict):
    """Mock st.session_state as a dict with attribute access."""
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)
    def __setattr__(self, key, value):
        self[key] = value

@patch("streamlit.html")
@patch("streamlit.markdown")
def test_component_renders(mock_md, mock_html):
    from utils.components import kpi_card
    kpi_card("Label", "42%", accent="sapphire")
    mock_html.assert_called_once()
    html_output = mock_html.call_args[0][0]
    assert "Label" in html_output
    assert "42%" in html_output
```

### HTML Content Assertions
```python
# Check rendered HTML for expected content
html = mock_html.call_args[0][0]
assert 'role="article"' in html          # ARIA role
assert 'aria-label="' in html            # Accessibility label
assert 'kpi-card' in html                # CSS class
assert COLORS["sapphire"] in html        # Design system color
```

### Property-Based Testing (Hypothesis)
```python
from hypothesis import given, strategies as st

@given(width=st.integers(min_value=100, max_value=2000))
def test_viewport_breakpoints(width):
    vp = ViewportProfile(width=width, is_mobile=width < 820, is_portrait=width < 600)
    assert vp.kpi_columns >= 1
    assert vp.chart_height >= 200
```

### Responsive / Touch Target Tests
```python
def test_touch_target_minimum_size():
    """WCAG 2.1 SC 2.5.5: Touch targets must be >= 44x44px."""
    css = TOUCH_TARGET_CSS
    assert "min-height: 44px" in css
    assert "min-width: 44px" in css

def test_touch_target_spacing():
    """Adjacent touch targets must have >= 8px spacing."""
    css = TOUCH_TARGET_CSS
    assert "gap:" in css or "margin:" in css
```

## Test Categories

| Category | Pattern | Example Files |
|----------|---------|---------------|
| **Unit** | Test single function/component | `test_kpi_card_enhancement.py`, `test_responsive.py` |
| **Property** | Hypothesis-based invariant tests | `test_*_properties.py` (15+ files) |
| **Integration** | Multi-component interaction | `test_hero_section_integration.py`, `test_state_lookup_integration.py` |
| **Accessibility** | ARIA, touch targets, keyboard | `test_touch_target_sizing_properties.py` |
| **Visual Demo** | Interactive validation scripts | `demo_*.py` files |

## What to Test

### For UI Components (utils/components.py)
- HTML output contains expected elements (labels, values, classes)
- ARIA attributes present (`role`, `aria-label`, `aria-hidden`)
- Accent color mapping works for all variants
- Edge cases: empty strings, None values, very long text, special characters

### For Data Pipeline (utils/data_loader.py)
- Column names are snake_case after cleaning
- Duplicate columns removed
- NA strings converted to NaN
- Engineered features have valid categories
- State FIPS mapping produces valid abbreviations

### For Responsive Design (utils/responsive.py)
- ViewportProfile breakpoints are correct at boundaries (819, 820, 821)
- ChartConfig adapts heights for mobile/tablet/desktop
- KPI column counts are valid (1-4)
- Data fraction is <= 1.0

### For Plotly Charts
- Chart uses PLOTLY_LAYOUT template
- Height adapts to viewport
- Color sequence matches theme
- Axis labels use get_variable_label()

## Procedure

1. **Identify what changed** — Read the diff or files to understand scope
2. **Check existing tests** — Search `tests/` for related test files
3. **Write tests following patterns above** — Match the project's mock style
4. **Cover edge cases** — Empty data, NaN, missing columns, boundary values
5. **Run tests** — `pytest tests/ -v` to verify
6. **Report results** — List passed/failed/skipped with any failure details

## Naming Convention
- Test files: `test_<feature_name>.py`
- Property tests: `test_<feature_name>_properties.py`
- Integration tests: `test_<feature_name>_integration.py`
- Demo scripts: `demo_<feature_name>.py`
