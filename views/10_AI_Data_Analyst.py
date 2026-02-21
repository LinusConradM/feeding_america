"""
AI Data Analyst - Custom code generation + local exec() loop.
Guarantees code is always executed against the real dataframe.
"""

import os
import io
import contextlib
import traceback
import streamlit as st
import pandas as pd
import numpy as np
from utils.theme import inject_tailwind, page_header
from utils.components import info_banner
from utils.data_loader import load_data
from utils.llm import _get_api_key, _get_groq_key

st.set_page_config(page_title="AI Data Analyst", page_icon="🤖", layout="wide")
inject_tailwind()

page_header("AI Data Analyst", "Ask complex questions in plain English. The AI writes Python code, runs it live against the dataset, then explains the results.", "robot")

# ── Session State ────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Load data ────────────────────────────────────────────────────────────────
df = load_data()

# ── API key helpers ──────────────────────────────────────────────────────────
gemini_key = _get_api_key()
groq_key = _get_groq_key()

if not gemini_key and not groq_key:
    info_banner("⚠️ A valid GEMINI_API_KEY or GROQ_API_KEY is required.", "warning")
    st.stop()

# ── Schema description injected into every prompt ────────────────────────────
SCHEMA = """
The DataFrame `df` contains U.S. Food Insecurity data (Feeding America, 2009–2023).
Shape: ~40,000 rows × 20+ columns.
VERIFIED FACTS:
- `year` (Int64): Values 2009–2023. 2023 has exactly 3,142 rows. Filter: df[df['year'] == 2023]
- `state` (str): 2-letter abbreviation e.g. 'TX'
- `state_name` (str): Full state name
- `county` (str): County name
- `overall_food_insecurity_rate` (float): fraction (e.g. 0.15 = 15%)
- `child_food_insecurity_rate` (float): fraction
- `poverty_rate` (float): fraction
- `unemployment_rate` (float): fraction
- `median_income` (float): USD
- `cost_per_meal` (float): USD per meal
- `snap_rate` (float): SNAP participation rate (fraction)
- `population` (Int64)
- `no_of_food_insecure_persons_overall` (Int64)
- `no_of_food_insecure_children` (Int64)
- `weighted_annual_food_budget_shortfall` (float): USD
- `fi_category` (category): 'Low','Moderate','High','Very High'
- `urban_rural` (category): 'Rural','Non-metro','Metro'
"""

# ── LLM caller: returns code string ─────────────────────────────────────────
def _call_llm_for_code(question: str) -> str:
    """Ask the LLM to return ONLY executable pandas code, nothing else."""
    system = (
        "You are a Python data scientist. "
        "Given a question about a DataFrame `df`, return ONLY executable Python code. "
        "NO explanation, NO markdown fences, NO comments. Just raw Python. "
        "The last line must assign the answer to a variable called `result`. "
        "Import nothing — pandas (pd), numpy (np) are already imported. "
        f"\n\nDataFrame schema:\n{SCHEMA}"
    )
    user_msg = f"Question: {question}"

    # Try Gemini
    if gemini_key:
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=gemini_key)
            resp = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_msg,
                config=types.GenerateContentConfig(
                    system_instruction=system,
                    temperature=0.0,
                )
            )
            return resp.text.strip()
        except Exception:
            pass

    # Groq fallback
    if groq_key:
        import groq as groq_sdk
        client = groq_sdk.Groq(api_key=groq_key)
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.0,
        )
        return resp.choices[0].message.content.strip()

    raise RuntimeError("No valid API key available.")


def _call_llm_for_explanation(question: str, code: str, output: str) -> str:
    """Ask the LLM to explain the code result in natural language."""
    system = (
        "You are a senior policy analyst. "
        "Given a user question, the Python code that was executed, and its output, "
        "write a concise, professional markdown summary of the findings. "
        "Start directly with key findings. Use bullet points. Be precise with numbers."
    )
    user_msg = (
        f"Question: {question}\n\n"
        f"Code executed:\n```python\n{code}\n```\n\n"
        f"Output:\n{output}"
    )

    if gemini_key:
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=gemini_key)
            resp = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_msg,
                config=types.GenerateContentConfig(system_instruction=system, temperature=0.3)
            )
            return resp.text.strip()
        except Exception:
            pass

    if groq_key:
        import groq as groq_sdk
        client = groq_sdk.Groq(api_key=groq_key)
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.3,
        )
        return resp.choices[0].message.content.strip()

    return output  # worst case, return raw output


def _strip_fences(code: str) -> str:
    """Strip markdown code fences if LLM includes them anyway."""
    lines = code.splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()


def _exec_code(code: str) -> tuple[str, str | None]:
    """
    Execute code in a local namespace with df, pd, np available.
    Returns (stdout_output, error_string_or_None).
    """
    code = _strip_fences(code)
    local_ns = {"df": df, "pd": pd, "np": np}
    stdout_capture = io.StringIO()
    try:
        with contextlib.redirect_stdout(stdout_capture):
            exec(code, local_ns)  # noqa: S102
        # Prefer `result` variable, else captured stdout
        result = local_ns.get("result", None)
        captured = stdout_capture.getvalue().strip()
        output = str(result) if result is not None else captured
        return output, None
    except Exception:
        return "", traceback.format_exc()


# ── UI ───────────────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown('<div class="bg-gray-50 border border-gray-200 rounded-xl p-6 min-h-[500px]">', unsafe_allow_html=True)

    # Render chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])
            if msg.get("code"):
                with st.expander("🔍 Show AI-Generated Code & Raw Output"):
                    st.code(msg["code"], language="python")
                    if msg.get("raw_output"):
                        st.text(f"Output: {msg['raw_output']}")

    # Chat input
    if prompt := st.chat_input("E.g., Which 5 counties in Texas saw the highest spike in child food insecurity between 2019 and 2021?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🤖"):
            placeholder = st.empty()
            placeholder.markdown(f'<i class="fas fa-circle-notch fa-spin text-blue-500 mr-2"></i> Generating pandas code against {len(df):,} rows...', unsafe_allow_html=True)

            try:
                # Step 1: LLM generates code
                placeholder.markdown('<i class="fas fa-circle-notch fa-spin text-blue-500 mr-2"></i> Step 1/3 — Generating code...', unsafe_allow_html=True)
                code = _call_llm_for_code(prompt)
                code = _strip_fences(code)

                # Step 2: Execute code locally
                placeholder.markdown('<i class="fas fa-circle-notch fa-spin text-blue-500 mr-2"></i> Step 2/3 — Executing code locally...', unsafe_allow_html=True)
                raw_output, error = _exec_code(code)

                if error:
                    # Try once more with the error context
                    retry_prompt = f"{prompt}\n\nPrevious code failed with:\n{error}\nPlease fix the code."
                    code = _call_llm_for_code(retry_prompt)
                    code = _strip_fences(code)
                    raw_output, error = _exec_code(code)

                if error:
                    final_answer = f"⚠️ Code execution failed:\n```\n{error}\n```"
                else:
                    # Step 3: LLM explains result
                    placeholder.markdown('<i class="fas fa-circle-notch fa-spin text-blue-500 mr-2"></i> Step 3/3 — Interpreting results...', unsafe_allow_html=True)
                    final_answer = _call_llm_for_explanation(prompt, code, raw_output)

                placeholder.markdown(final_answer)

                with st.expander("🔍 Show AI-Generated Code & Raw Output"):
                    st.code(code, language="python")
                    st.text(f"Raw output: {raw_output}")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": final_answer,
                    "code": code,
                    "raw_output": raw_output,
                })

            except Exception as e:
                placeholder.error(f"Agent Error: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown(
        """
        <div class="bg-blue-50 rounded-xl p-5 border border-blue-100 shadow-sm">
            <h3 class="text-blue-800 font-bold text-sm mb-3">
                <i class="fas fa-lightbulb text-yellow-500 mr-2"></i>How this works
            </h3>
            <p class="text-sm text-blue-900 leading-relaxed mb-4">
                This is a <b>verified code execution engine</b>. Unlike LLM chatbots, it never guesses.
            </p>
            <ol class="text-sm text-blue-900 space-y-2 list-decimal list-inside">
                <li class="bg-white p-2 rounded border border-blue-200">AI writes Python pandas code</li>
                <li class="bg-white p-2 rounded border border-blue-200">Code runs <b>locally</b> against the real dataset</li>
                <li class="bg-white p-2 rounded border border-blue-200">AI explains the actual output</li>
            </ol>
            <h4 class="text-xs font-bold text-blue-800 uppercase tracking-wider mb-2 mt-4">Example Questions</h4>
            <ul class="text-sm text-blue-900 space-y-3">
                <li class="bg-white p-2 rounded border border-blue-200 shadow-sm font-medium">Which state had the largest <b>decrease</b> in child food insecurity between 2012 and 2022?</li>
                <li class="bg-white p-2 rounded border border-blue-200 shadow-sm font-medium">What is the median cost per meal for the 5 counties with highest poverty in 2023?</li>
                <li class="bg-white p-2 rounded border border-blue-200 shadow-sm font-medium">List top 5 Rural counties with lowest unemployment but highest SNAP participation.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True
    )
