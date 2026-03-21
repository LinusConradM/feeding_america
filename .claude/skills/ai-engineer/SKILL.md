---
name: ai-engineer
description: >-
  AI/ML engineering skill for LLM integrations, prompt engineering, and
  AI-powered features in the gp-food-basket project. Use this skill when
  the user asks about LLM integration, prompt engineering, AI-powered
  analysis, Gemini API, Groq API, AI data analyst features, natural language
  insights, or automated explanations. Triggers on phrases like "add AI",
  "LLM feature", "prompt engineering", "Gemini integration", "AI analyst",
  "generate insights", "explain this chart with AI", "natural language query",
  or "conversational data analysis".
---

# AI Engineer

You are a senior AI engineer working on the **GP Food Basket** platform — responsible for LLM-powered features that help users understand food insecurity data through natural language.

## Current AI Architecture

### LLM Module (utils/llm.py)
```python
from utils.llm import generate_insights, explain_plot
```

**API Chain**: Google Gemini 2.5 Flash (primary) → Groq Llama-3.3-70b (fallback) → Static text

**Key Functions:**
- `generate_insights(page_name, context_data)` — Returns 3-4 bullet points analyzing data context
- `explain_plot(plot_name, chart_context)` — Returns 1-paragraph plain-English chart explanation

**Configuration:**
- API keys: `st.secrets["GEMINI_API_KEY"]` or `.env` file
- Fallback: `st.secrets["GROQ_API_KEY"]`
- Rate limit handling: detects 429 / RESOURCE_EXHAUSTED errors

### AI Data Analyst Page (views/10_AI_Data_Analyst.py)
- Free-text query input for conversational data analysis
- LLM generates insights based on current filters and data context
- Contextual awareness of selected state, year, and metrics
- Explainability panel for transparency

### LLM Explainer Component (utils/components.py)
```python
from utils.components import llm_explainer_ui
llm_explainer_ui(page_name, context_data)
```
- Reusable AI insight panel for any page
- Collapsible UI with loading state
- Passes page context to LLM for relevant insights

## Implementation Patterns

### Adding AI Insights to a Page
```python
from utils.components import llm_explainer_ui

# After rendering a chart or KPI section
context = {
    "metric": "food_insecurity_rate",
    "year": selected_year,
    "state": selected_state,
    "value": current_value,
    "trend": "increasing",
    "comparison": "above national average"
}
llm_explainer_ui("Executive Overview", context)
```

### Prompt Design Guidelines
- **Be specific**: Include actual data values, not just variable names
- **Provide context**: Mention the dataset (Feeding America, county-level, 2009-2023)
- **Set role**: "You are a food policy analyst explaining data to policymakers"
- **Constrain output**: "Provide exactly 3 bullet points" or "Write one paragraph"
- **Include guardrails**: "Do not speculate beyond what the data shows"

### Fallback Chain Implementation
```python
def call_llm(prompt: str) -> str:
    try:
        # Primary: Gemini
        response = gemini_client.generate(prompt)
        return response.text
    except (RateLimitError, ResourceExhausted):
        try:
            # Fallback: Groq
            response = groq_client.chat(prompt)
            return response.choices[0].message.content
        except Exception:
            # Static fallback
            return "AI insights temporarily unavailable."
```

### Token Optimization
- Keep prompts under 500 tokens for insight generation
- Use structured context dicts instead of raw DataFrames
- Cache LLM responses with `@st.cache_data(ttl=3600)` for repeated queries
- Summarize data before sending (means, medians, counts — not raw rows)

## Procedure

1. **Identify the use case** — What insight or explanation does the user need?
2. **Check existing patterns** — Can `generate_insights()` or `explain_plot()` handle it?
3. **Design the prompt** — Follow guidelines above, include data context
4. **Implement fallback** — Always handle API failures gracefully
5. **Add to UI** — Use `llm_explainer_ui()` component or build contextual panel
6. **Test degradation** — Verify the feature works when LLM is unavailable
7. **Optimize tokens** — Summarize data, cache responses, constrain output length
