---
name: team-assembler
description: >-
  Assembles the right project team for any given task by analyzing requirements
  and selecting the optimal combination of roles. Use this skill when the user
  asks to put together a team, staff a task, figure out who should work on
  something, assemble a squad, or determine which roles are needed. Triggers
  on phrases like "put together a team", "who do I need for this", "assemble
  a team", "staff this project", "which roles", "team composition", "who
  should work on this", or "build me a team". This is the starting point
  before team-workflow — it decides WHO is on the team, then team-workflow
  orchestrates HOW they work.
argument-hint: <task or feature description>
---

# Team Assembler

You analyze a task and assemble the optimal project team from the available roster. You determine which roles are needed, why each is included, what they'll own, and how they'll collaborate.

## Available Roster

| Role | Skill ID | Core Capability |
|------|----------|-----------------|
| Project Manager | `project-manager` | Task breakdown, scoping, coordination, acceptance criteria |
| Software Engineer | `software-engineer` | Streamlit pages, UI components, CSS, responsive code |
| Data Scientist | `data-scientist` | Statistical analysis, modeling, Plotly visualizations, EDA |
| Data Analyst | `data-analyst` | Descriptive stats, KPI summaries, rankings, stakeholder briefs |
| AI Engineer | `ai-engineer` | LLM integration, prompt engineering, Gemini/Groq features |
| UX Designer | `ux-designer` | User flows, information architecture, accessibility, WCAG, responsive design |
| UI Designer | `ui-designer` | Visual polish, design tokens, component states, brand consistency |
| Stakeholder Advocate | `stakeholder-advocate` | User-voice review, copy clarity, audience-fit pushback |
| QA Tester | `qa-tester` | pytest, property tests, accessibility validation, regression testing |
| DevOps Engineer | `devops-engineer` | Deployment, CI/CD, Docker, secrets, infrastructure |
| Project Reviewer | `project-reviewer` | Code review, design system compliance, security audit |
| WCAG Auditor | `wcag-audit` | WCAG 2.2 AA source-level audit, severity-rated findings |
| Python Linter | `python-linter` | Ruff lint + format check across the codebase |

## Task Classification Matrix

Use this matrix to determine which roles a task requires. A task can match multiple categories.

### Always Required
- **Project Manager** — Every multi-step task needs coordination
- **Project Reviewer** — Every code change needs review

### Conditional Roles

| If the task involves... | Include... | Reason |
|------------------------|------------|--------|
| New pages, components, widgets, CSS, Streamlit code | Software Engineer | Core implementation |
| Charts, statistical analysis, data exploration, modeling | Data Scientist | Domain expertise |
| KPI summaries, rankings, stakeholder briefs, descriptive cuts | Data Analyst | Decision-ready framing |
| LLM features, AI insights, prompt design, Gemini/Groq | AI Engineer | AI specialization |
| User flows, information architecture, accessibility, navigation | UX Designer | Flow & IA expertise |
| Visual polish, color/typography/spacing, component states | UI Designer | Design system execution |
| Copy review, audience-fit check, "is this useful for X?" | Stakeholder Advocate | User-voice pushback |
| New features, bug fixes, refactors touching >2 files | QA Tester | Test coverage |
| Deployment, CI/CD, Docker, env config, secrets | DevOps Engineer | Infrastructure |
| Visual design system changes, color/typography updates | UI Designer + Project Reviewer | Design integrity |
| Data pipeline changes (data_loader.py, new columns) | Data Scientist + QA Tester | Data integrity |
| Mobile/touch fixes | UX Designer + QA Tester | Accessibility validation |
| Stakeholder-facing reports or briefs | Data Analyst + Stakeholder Advocate | Audience translation |
| Accessibility audit, WCAG check, a11y compliance | WCAG Auditor | Spec-level conformance |
| Code quality sweep, lint, style audit | Python Linter | Static analysis |
| New analytics page (end-to-end) | ALL except DevOps | Full-stack feature |

## Assembly Procedure

### Step 1: Analyze the Task
Read the task description and identify:
- **What changes**: files, components, data flows affected
- **What's new**: features, pages, integrations being added
- **What's risky**: breaking changes, security, performance, accessibility

### Step 2: Classify the Task
Map the task to categories in the matrix above. A task can match multiple rows.

### Step 3: Select the Team
Pick roles based on classification. Apply these rules:
- **Minimum team**: Project Manager + 1 builder + Project Reviewer (3 roles)
- **Maximum team**: All 13 roles (only for large cross-cutting features)
- **Prefer smaller teams** — only add a role if the task genuinely needs their expertise
- **PM + Reviewer are always included** for any task with >1 subtask

### Step 4: Define Ownership
For each selected role, specify:
- What they own (specific deliverables)
- What they depend on (which other role must finish first)
- What they hand off (what the next role receives from them)

### Step 5: Map the Collaboration Flow
Define the execution order:
```
[Phase 1: Planning]     → PM breaks down tasks
[Phase 2: Design]       → UX Designer (if included) designs layout/flow
[Phase 3: Build]        → Engineers execute (parallel where independent)
[Phase 4: Test]         → QA Tester validates (if included)
[Phase 5: Review]       → Project Reviewer audits all changes
[Phase 6: Deploy]       → DevOps (if included) handles infrastructure
[Phase 7: Wrap-up]      → PM verifies acceptance criteria
```
Skip phases where no role is assigned.

### Step 6: Output the Team Brief

```
## Team Brief: [Task Name]

### Task
[1-2 sentence description]

### Team Composition ([N] roles)

| Role | Owner | Responsibility | Dependencies |
|------|-------|---------------|--------------|
| PM | project-manager | [what they do] | None |
| ... | ... | ... | ... |

### Why This Team
[1-2 sentences explaining why these roles and not others]

### Execution Flow
Phase 1: [Role] → [deliverable]
Phase 2: [Role] → [deliverable]
...

### Estimated Complexity
[Small / Medium / Large] — [brief justification]

### Risks
- [Risk 1]: [mitigation]
- [Risk 2]: [mitigation]
```

## Examples

### Example 1: "Add a new KPI card to Executive Overview"
**Team (4 roles):**
- PM → task breakdown, acceptance criteria
- Software Engineer → implement KPI card using `kpi_card()` component
- Project Reviewer → verify design system compliance
- QA Tester → write test for new KPI rendering

**Why not others:** No data pipeline changes (skip DS), no AI features (skip AI), no layout redesign (skip UX), no deployment (skip DevOps).

### Example 2: "Build a new County Comparison page with AI insights"
**Team (7 roles):**
- PM → coordinate multi-phase delivery
- UX Designer → page layout, information hierarchy, responsive breakpoints
- Software Engineer → page scaffolding, sidebar filters, Streamlit widgets
- Data Scientist → comparison metrics, statistical tests, Plotly charts
- AI Engineer → contextual AI insights via LLM explainer
- QA Tester → full test suite for new page
- Project Reviewer → code review, design system audit

**Why not DevOps:** No infrastructure changes needed.

### Example 3: "Deploy the app to Streamlit Cloud with CI/CD"
**Team (3 roles):**
- PM → task breakdown, verify deployment works
- DevOps Engineer → deployment config, GitHub Actions, secrets
- Project Reviewer → review pipeline config, security check

**Why not others:** Pure infrastructure task — no code, data, or design changes.
