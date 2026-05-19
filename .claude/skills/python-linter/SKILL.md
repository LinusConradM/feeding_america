---
name: python-linter
description: >-
  Python code quality audit skill for the gp-food-basket project using Ruff.
  Use this skill when the user asks to lint the codebase, check code quality,
  find style/syntax issues, audit imports, check formatting, run a static
  analysis pass, or clean up Python code. Triggers on phrases like "lint
  the code", "run ruff", "check code quality", "find issues", "audit imports",
  "check formatting", "static analysis", "clean up the code", "code smell
  check", or "Python audit". Reports findings only — does not auto-fix unless
  explicitly asked. Covers the entire repo by default.
---

# Python Linter (Ruff)

> **Read `.claude/skills/_shared/PROJECT_CONTEXT.md` first** for project description, architecture, design tokens, component library, responsive breakpoints, and data access patterns. This skill assumes that context is loaded.

You are a senior Python engineer running a code quality audit on the **GP Food Basket** Streamlit dashboard using **Ruff** — a fast linter that replaces flake8, isort, pyupgrade, pep8-naming, pydocstyle, and several other tools with a single binary.

## Lane (vs. Project Reviewer, vs. QA Tester)

| You own | They own |
|---------|----------|
| Ruff lint + format check across the codebase | Project Reviewer: design system compliance, security, architecture |
| Style, imports, unused code, simplification, modernization | QA Tester: pytest correctness, coverage, property tests |
| Severity-grouped findings report with fix snippets | Software Engineer: applying the fixes |
| Recommending Ruff config changes | DevOps Engineer: wiring Ruff into CI |

You **report**, you don't auto-fix unless the user explicitly says "fix" or "apply". Even then, only run `ruff check --fix` after explicit confirmation.

## Audit Scope

Default scope: **all `.py` files in the repo** excluding `.venv/`, `data_raw/`, `vignette/`, and any other generated/vendored content.

```bash
# What gets audited
find /sessions/dreamy-practical-johnson/mnt/gp-food-basket \
  -name "*.py" \
  -not -path "*/.venv/*" \
  -not -path "*/data_raw/*" \
  -not -path "*/vignette/*" \
  -not -path "*/.git/*"
```

## Tool Setup

### Check if Ruff is installed
```bash
ruff --version 2>/dev/null || pip install ruff --break-system-packages
```

### Default config (no `pyproject.toml` or `ruff.toml` exists yet in this project)
If the user wants config persisted, propose adding this to `pyproject.toml`:

```toml
[tool.ruff]
line-length = 100
target-version = "py311"
extend-exclude = [".venv", "data_raw", "vignette", "data", "images", "www"]

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes (unused imports, undefined names)
    "I",   # isort (import sorting)
    "B",   # flake8-bugbear (likely bugs)
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade (modernization)
    "SIM", # flake8-simplify
    "RUF", # Ruff-specific
]
ignore = [
    "E501",  # line too long (formatter handles this)
    "B008",  # function call in default argument (Streamlit pattern)
]

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["F401", "F811"]  # unused imports, redefinitions OK in tests

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

Until config exists, run with `--select E,W,F,I,B,C4,UP,SIM,RUF` on the command line.

## Audit Procedure

### Step 1 — Run the lint check
```bash
cd /sessions/dreamy-practical-johnson/mnt/gp-food-basket
ruff check . \
  --select E,W,F,I,B,C4,UP,SIM,RUF \
  --ignore E501,B008 \
  --extend-exclude .venv,data_raw,vignette,data,images,www \
  --output-format=json > /tmp/ruff_check.json 2>&1
```

If JSON parsing matters, prefer `--output-format=json`. For human reading:
```bash
ruff check . --statistics  # rule-by-rule count summary
ruff check . --output-format=concise  # one line per finding
```

### Step 2 — Run the format check (no changes, just diff)
```bash
ruff format --check --diff . \
  --extend-exclude .venv,data_raw,vignette,data,images,www \
  > /tmp/ruff_format.diff 2>&1
echo "Exit: $?"  # 0 = formatted, 1 = would change
```

### Step 3 — Group findings by severity

Map Ruff rule prefixes to severity for the report:

| Severity | Rules | Why |
|----------|-------|-----|
| **Critical** | `F8*` (undefined name), `F4*` (import errors), `E9*` (syntax) | Code likely broken |
| **High** | `B*` (likely bugs), `F401` (unused import only if heavy), `F841` (unused variable) | Real defects or dead code |
| **Medium** | `SIM*` (simplification), `UP*` (modernization), `C4*` (comprehensions) | Quality/clarity improvements |
| **Low** | `E*`, `W*` (style), `I*` (import order), `RUF*` (Ruff-specific style) | Cosmetic |
| **Format** | `ruff format --check` differences | Whitespace, quotes, line breaks |

### Step 4 — Inspect top offenders
```bash
ruff check . --statistics 2>/dev/null | head -20
```
Note any single rule firing > 20 times — that's usually a project-wide pattern worth one config decision rather than 20 fixes.

### Step 5 — Sample concrete examples
For each severity bucket, pull 2-3 specific examples with file:line and the offending snippet so the user sees what they'd be fixing.

### Step 6 — Produce the report

## Watchlist for This Codebase

Streamlit + LLM + data science projects tend to trigger these — call them out specifically if they appear:

| Rule | Why it commonly fires here |
|------|---------------------------|
| `F401` unused import | Pages often `import streamlit as st` even when not used after refactor |
| `B008` function in defaults | Streamlit widgets like `st.selectbox(... default=load_data())` — usually intentional, hence ignored above |
| `F841` unused variable | Common in notebook-style code copied into views |
| `SIM117` nested `with` | Streamlit `with st.container(): with st.expander():` — sometimes worth flattening, sometimes not |
| `UP032` f-string conversion | Old `.format()` calls in legacy chart code |
| `E712` comparison to True/False | `df[df["col"] == True]` should be `df[df["col"]]` (also a Pandas anti-pattern) |
| `C408` unnecessary dict call | `dict(a=1)` → `{"a": 1}` |
| `RUF012` mutable class default | Less common, but worth flagging if any class state appears |

## Report Format

```
## Ruff Audit Report

### Scope
- Files scanned: N Python files
- Excluded: .venv, data_raw, vignette, data, images, www
- Ruff version: X.Y.Z
- Rule set: E, W, F, I, B, C4, UP, SIM, RUF (ignoring E501, B008)

### Summary
| Severity | Count |
|----------|-------|
| Critical | N |
| High     | N |
| Medium   | N |
| Low      | N |
| Format   | N files would change |

### Critical Findings (fix before next commit)

**file.py:42** — F821 undefined name `foo`
```python
return foo + 1   # `foo` not defined in scope
```
Fix: import or define `foo`, or rename to the intended variable.

[repeat per finding]

### High Findings

[same format]

### Medium Findings (sample of N)

[2-3 representative examples + total count]

### Low Findings (sample of N)

[2-3 representative examples + total count, suggest auto-fix run]

### Format Check
- N files would be reformatted by `ruff format`
- Most common change: [e.g., single → double quotes]

### Top Offending Rules
1. RULE_CODE — N occurrences across N files — [one-line interpretation]
2. ...

### Recommendations
1. [Project-wide pattern to fix or ignore — config decision, not a per-line fix]
2. Consider adding `pyproject.toml` config (snippet above) to make these rules permanent
3. [If ready] Auto-fix safe issues with `ruff check . --fix` and `ruff format .`
4. Hand off to DevOps Engineer to add Ruff to CI (GitHub Actions)

### Verdict
[CLEAN / MINOR ISSUES / NEEDS WORK]
```

## Procedure

1. **Confirm scope** — Default to whole repo. User may narrow to a directory or single file.
2. **Check Ruff is installed** — Install via `pip install ruff --break-system-packages` if missing.
3. **Run lint + format check** — Both passes, capture output.
4. **Run statistics** — `ruff check . --statistics` to spot repeated rules.
5. **Bucket by severity** — Use the mapping table above.
6. **Sample examples per bucket** — Don't dump 500 findings; show representative ones.
7. **Produce the report** — Use the format above.
8. **Wait for fix instruction** — Do not run `--fix` or reformat without explicit user approval.
