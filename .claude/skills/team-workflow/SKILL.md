---
name: team-workflow
description: >-
  Orchestrates a full team workflow across all available roles: Project Manager,
  Software Engineer, Data Scientist, AI Engineer, UX Designer, QA Tester,
  DevOps Engineer, and Project Reviewer. Run the `team-assembler` skill first to pick
  the right team, then `team-workflow` to execute. This skill coordinates
  planning, design, implementation, testing, review, and deployment in a
  structured pipeline. Use when the user wants a complete end-to-end workflow
  with task breakdown, role-based execution, and quality review.
argument-hint: <task description>
---

# Team Workflow Orchestrator

You coordinate a professional software team to deliver changes to the **GP Food Basket** platform. You manage the full lifecycle: plan → build → review → deliver.

## Team Roles

| Role | Skill | Handles |
|------|-------|---------|
| Project Manager | `project-manager` | Task breakdown, scoping, acceptance criteria, progress |
| UX Designer | `ux-designer` | User flows, information architecture, accessibility, responsive design |
| UI Designer | `ui-designer` | Visual polish, design tokens, component states, chart styling |
| Software Engineer | `software-engineer` | UI, components, pages, Streamlit code, CSS, responsive |
| Data Scientist | `data-scientist` | Modeling, statistical tests, clustering, anomaly detection |
| Data Analyst | `data-analyst` | KPI summaries, rankings, stakeholder briefs, descriptive cuts |
| AI Engineer | `ai-engineer` | LLM features, prompts, Gemini/Groq, AI insights |
| Stakeholder Advocate | `stakeholder-advocate` | User-voice review, copy clarity, audience-fit pushback |
| QA Tester | `qa-tester` | pytest, property tests, accessibility validation |
| WCAG Auditor | `wcag-audit` | WCAG 2.2 AA source-level audit when UI ships |
| Python Linter | `python-linter` | Ruff lint + format check across the codebase |
| Project Reviewer | `project-reviewer` | Code review, quality, security, design system compliance |
| DevOps Engineer | `devops-engineer` | Deployment, CI/CD, Docker, secrets, infrastructure |

## Workflow Pipeline

Execute these phases in order for every task:

### Phase 1: Planning (Project Manager)

1. Read the task description provided by the user
2. Read relevant existing files to understand current state
3. Break the task into concrete subtasks using **TodoWrite**
4. For each subtask, assign:
   - **Role**: Which team member handles it
   - **Acceptance criteria**: What "done" looks like
   - **Dependencies**: What must finish first
5. Identify risks and flag them to the user
6. Present the plan and get user confirmation before proceeding

### Phase 2: Design (UX Designer — if on team)

If the task involves layout, new pages, or visual changes:

1. Audit the current UI state of affected pages
2. Define visual hierarchy, component placement, and responsive breakpoints
3. Specify exact components (`kpi_card()`, `section_header()`, etc.), color tokens, and layout grid
4. Verify WCAG 2.1 compliance: touch targets (44x44px), contrast ratios, ARIA labels
5. Hand off design spec to engineers

Skip this phase if UX Designer is not on the team.

### Phase 3: Execution (Engineers)

Execute subtasks in dependency order. For each subtask:

1. Mark the task as `in_progress` in TodoWrite
2. Read all relevant files before making changes
3. Implement following the assigned role's conventions:
   - **Software Engineer**: Follow page template, reuse components, use COLORS/PLOTLY_LAYOUT
   - **Data Scientist**: Use load_data(), follow statistical patterns, Plotly conventions
   - **AI Engineer**: Follow fallback chain, use llm_explainer_ui(), optimize tokens
4. Mark the task as `completed` when done

**Parallelism**: Launch independent subtasks in parallel using the Agent tool when they don't depend on each other.

### Phase 4: Testing (QA Tester — if on team)

If QA Tester is on the team:

1. Write tests for new/changed functionality following `tests/` patterns
2. Use pytest with `unittest.mock` for Streamlit mocking
3. Add property-based tests (Hypothesis) for invariants
4. Validate accessibility (ARIA labels, touch targets)
5. Run `pytest tests/ -v` and report results
6. If tests fail: fix issues before proceeding to review

Skip this phase if QA Tester is not on the team.

### Phase 5: Review (Project Reviewer)

After all implementation and testing subtasks complete:

1. Run `git diff` to see all changes
2. Read each changed file in full
3. Check against the review checklist:
   - Correctness
   - McKinsey design system compliance
   - Responsive design
   - Data pipeline integrity
   - Security (OWASP)
   - Performance
   - Component reuse
4. Produce a structured review report
5. If critical issues found: fix them before proceeding
6. If warnings found: note them in the report

### Phase 5b: Audit (WCAG Auditor / Python Linter — if on team)

If WCAG Auditor is on the team:
1. Run the WCAG 2.2 AA audit procedure on changed views/components
2. Produce findings report grouped by severity
3. Critical findings block deploy until fixed

If Python Linter is on the team:
1. Run `ruff check` and `ruff format --check` against scope
2. Report findings by severity bucket
3. Wait for explicit fix instruction before applying `--fix`

Skip this phase if neither is on the team.

### Phase 6: Deploy (DevOps Engineer — if on team)

If DevOps Engineer is on the team:

1. Create/update deployment configuration as needed
2. Set up CI/CD pipeline if requested
3. Configure secrets management
4. Verify deployment works

Skip this phase if DevOps Engineer is not on the team.

### Phase 7: Wrap-up (Project Manager)

1. Verify all acceptance criteria are met
2. Update TodoWrite — mark all tasks completed
3. Produce a **Delivery Summary**:

```
## Delivery Summary

### Task
[Original request]

### Changes Made
- [File]: [What changed]
- [File]: [What changed]

### Review Result
[APPROVED / APPROVED WITH NOTES]

### Key Decisions
- [Any non-obvious choices made during implementation]

### Notes
- [Anything the user should know]
```

## Execution Rules

1. **Always plan before coding** — Never start implementation without a task breakdown
2. **Read before writing** — Always read existing files before modifying them
3. **One task at a time** — Only one TodoWrite item should be `in_progress`
4. **Fix review issues immediately** — Don't deliver code with critical findings
5. **Keep the user informed** — Report progress at each phase transition
6. **Don't over-engineer** — Implement exactly what was requested, nothing more
7. **Reuse existing components** — Check utils/ before writing custom code

## Example Invocation

User: `/team-workflow Add a budget shortfall trend chart to the Executive Overview page`

Phase 1 output:
```
Task breakdown:
1. [PM] Scope and break down task
2. [UX] Define chart placement and responsive layout spec
3. [DS] Analyze budget_shortfall data availability and trends
4. [SWE] Add trend chart section with section_header
5. [SWE] Create Plotly line chart with PLOTLY_LAYOUT
6. [SWE] Make chart responsive with ChartConfig
7. [QA] Write test for new chart rendering
8. [REVIEW] Review all changes
9. [PM] Verify and summarize
```

Then execute phases 2-7 sequentially, skipping phases where no role is assigned.
