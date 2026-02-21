"""
AI Data Analyst - Redesigned with sample question cards, chat window, status bar.
"""

import os
import io
import contextlib
import traceback
import streamlit as st
import pandas as pd
import numpy as np
from utils.theme import inject_tailwind, COLORS
from utils.data_loader import load_data
from utils.llm import _get_api_key, _get_groq_key

st.set_page_config(page_title="AI Data Analyst", page_icon="🤖", layout="wide")
inject_tailwind()

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

.ai-page-header { margin-bottom: 1.5rem; }
.ai-page-icon {
    display: inline-flex; align-items: center; justify-content: center;
    width: 44px; height: 44px; border-radius: 10px;
    background: linear-gradient(135deg, #4F46E5, #7C3AED);
    margin-bottom: 0.75rem;
    font-size: 1.3rem;
}
.ai-page-title { font-size: 1.75rem; font-weight: 700; color: #1e293b; font-family: 'Inter', sans-serif; }
.ai-page-sub   { color: #64748b; font-size: 0.95rem; margin-top: 0.1rem; }

.filter-section {
    background: white; border: 1px solid #e2e8f0; border-radius: 12px;
    padding: 1rem 1.25rem; margin-bottom: 1.75rem;
    display: flex; align-items: center; gap: 0.75rem;
}
.filter-label { color: #64748b; font-size: 0.85rem; font-weight: 500; }

.sample-section-title {
    font-size: 1rem; font-weight: 600; color: #1e293b;
    margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;
}

/* Question cards */
.q-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 1.1rem 1.1rem 1.1rem 1.1rem;
    cursor: pointer;
    transition: box-shadow 0.18s, transform 0.15s;
    position: relative;
    overflow: hidden;
    height: 100%;
    min-height: 110px;
}
.q-card:hover { box-shadow: 0 4px 18px rgba(0,0,0,0.10); transform: translateY(-2px); }
.q-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 4px;
}
.card-blue::before  { background: #4F46E5; }
.card-green::before { background: #16a34a; }
.card-orange::before{ background: #ea580c; }
.card-violet::before{ background: #7c3aed; }
.card-teal::before  { background: #0891b2; }
.card-rose::before  { background: #e11d48; }

.q-card-icon {
    width: 36px; height: 36px; border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; margin-bottom: 0.6rem;
}
.icon-blue   { background: #4F46E5; }
.icon-green  { background: #16a34a; }
.icon-orange { background: #ea580c; }
.icon-violet { background: #7c3aed; }
.icon-teal   { background: #0891b2; }
.icon-rose   { background: #e11d48; }

.q-card-title { font-weight: 600; color: #1e293b; font-size: 0.9rem; margin-bottom: 0.3rem; }
.q-card-desc  { color: #64748b; font-size: 0.8rem; line-height: 1.4; }

/* Status bar */
.ai-status-bar {
    background: white; border: 1px solid #e2e8f0;
    border-radius: 12px 12px 0 0;
    padding: 0.65rem 1.1rem;
    display: flex; align-items: center; gap: 0.5rem;
    border-bottom: none;
    margin-top: 1.5rem;
}
.status-dot {
    width: 9px; height: 9px; border-radius: 50%; background: #22c55e;
    display: inline-block; animation: pulse-dot 2s infinite;
}
@keyframes pulse-dot {
    0%, 100% { opacity: 1; } 50% { opacity: 0.4; }
}
.status-label { font-weight: 600; font-size: 0.85rem; color: #1e293b; }
.status-sub   { font-size: 0.8rem; color: #94a3b8; margin-left: 0.2rem; }

/* Chat window */
.chat-window {
    background: white;
    border: 1px solid #e2e8f0; border-top: none;
    border-radius: 0 0 0 0;
    min-height: 380px; padding: 1.25rem;
}
.empty-state {
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    padding: 4rem 1rem; color: #94a3b8; text-align: center;
}
.empty-icon {
    width: 60px; height: 60px; border-radius: 50%;
    background: #f1f5f9; display: flex; align-items: center;
    justify-content: center; font-size: 1.6rem; margin-bottom: 1rem;
}
.empty-title { font-size: 1rem; font-weight: 600; color: #475569; margin-bottom: 0.3rem; }
.empty-sub   { font-size: 0.85rem; color: #94a3b8; }

/* Chat messages */
.msg-user {
    background: linear-gradient(135deg, #4F46E5, #7C3AED);
    color: white; border-radius: 16px 16px 4px 16px;
    padding: 0.75rem 1rem; margin: 0.5rem 0;
    max-width: 80%; margin-left: auto;
    font-size: 0.9rem; font-family: 'Inter', sans-serif;
}
.msg-bot {
    background: #f8fafc; border: 1px solid #e2e8f0;
    border-radius: 4px 16px 16px 16px;
    padding: 0.9rem 1.1rem; margin: 0.5rem 0;
    max-width: 90%; font-size: 0.88rem;
    font-family: 'Inter', sans-serif; color: #1e293b;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)

# ── Load data ────────────────────────────────────────────────────────────────
df = load_data()
gemini_key = _get_api_key()
groq_key   = _get_groq_key()

# ── Session State ────────────────────────────────────────────────────────────
if "ai_messages"    not in st.session_state: st.session_state.ai_messages    = []
if "pending_prompt" not in st.session_state: st.session_state.pending_prompt = None

# ── Schema ───────────────────────────────────────────────────────────────────
SCHEMA = """
DataFrame `df` — U.S. Food Insecurity (Feeding America, 2009–2023), ~40,000 rows.
Key columns:
- year (Int64): 2009-2023. 2023 has 3,142 rows. Filter: df[df['year'] == 2023]
- state (str): 2-letter e.g. 'TX'
- state_name (str)
- county (str)
- overall_food_insecurity_rate (float): fraction e.g. 0.15 = 15%
- child_food_insecurity_rate (float): fraction
- poverty_rate (float): fraction
- unemployment_rate (float): fraction
- median_income (float): USD
- cost_per_meal (float): USD
- snap_rate (float): fraction
- population (Int64)
- no_of_food_insecure_persons_overall (Int64)
- no_of_food_insecure_children (Int64)
- weighted_annual_food_budget_shortfall (float): USD
- fi_category (category): 'Low','Moderate','High','Very High'
- urban_rural (category): 'Rural','Non-metro','Metro'
"""

# ── LLM helpers ──────────────────────────────────────────────────────────────
def _llm_code(question: str) -> str:
    system = (
        "You are a Python data scientist. Return ONLY executable Python code, no explanations, no markdown fences. "
        "The last statement must assign the answer to `result`. pandas (pd) and numpy (np) are already imported. "
        f"DataFrame schema:\n{SCHEMA}"
    )
    if gemini_key:
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=gemini_key)
            resp = client.models.generate_content(
                model="gemini-2.5-flash", contents=question,
                config=types.GenerateContentConfig(system_instruction=system, temperature=0.0)
            )
            return resp.text.strip()
        except Exception:
            pass
    if groq_key:
        import groq as g
        c = g.Groq(api_key=groq_key)
        r = c.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"system","content":system},{"role":"user","content":question}],
            temperature=0.0,
        )
        return r.choices[0].message.content.strip()
    raise RuntimeError("No API key.")

def _llm_explain(question: str, code: str, output: str) -> str:
    system = (
        "You are a senior food security policy analyst. "
        "Given a question, the Python code executed, and its raw output, write a concise professional "
        "summary in markdown. Lead with the key number. Use bullet points for context. Be precise."
    )
    msg = f"Question: {question}\nCode:\n```python\n{code}\n```\nOutput:\n{output}"
    if gemini_key:
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=gemini_key)
            resp = client.models.generate_content(
                model="gemini-2.5-flash", contents=msg,
                config=types.GenerateContentConfig(system_instruction=system, temperature=0.3)
            )
            return resp.text.strip()
        except Exception:
            pass
    if groq_key:
        import groq as g
        c = g.Groq(api_key=groq_key)
        r = c.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"system","content":system},{"role":"user","content":msg}],
            temperature=0.3,
        )
        return r.choices[0].message.content.strip()
    return output

def _strip(code: str) -> str:
    lines = code.splitlines()
    if lines and lines[0].startswith("```"): lines = lines[1:]
    if lines and lines[-1].strip() == "```": lines = lines[:-1]
    return "\n".join(lines).strip()

def _exec(code: str):
    code = _strip(code)
    ns = {"df": df, "pd": pd, "np": np}
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            exec(code, ns)  # noqa: S102
        result = ns.get("result", None)
        captured = buf.getvalue().strip()
        return (str(result) if result is not None else captured), None
    except Exception:
        return "", traceback.format_exc()

# ── Question card definitions ────────────────────────────────────────────────
QUESTIONS = [
    {
        "title": "National Overview",
        "desc": "What was the national food insecurity rate and total affected population in 2023?",
        "icon": "🏛️", "card_class": "card-blue", "icon_class": "icon-blue",
    },
    {
        "title": "Worst Affected States",
        "desc": "Which 5 states had the highest child food insecurity rate in 2023?",
        "icon": "👧", "card_class": "card-green", "icon_class": "icon-green",
    },
    {
        "title": "Cost Analysis",
        "desc": "What is the median cost per meal for the top 5 counties with the highest poverty rate in 2023?",
        "icon": "🍽️", "card_class": "card-orange", "icon_class": "icon-orange",
    },
    {
        "title": "Budget Shortfall",
        "desc": "Which 5 states had the largest annual food budget shortfall in 2023?",
        "icon": "💸", "card_class": "card-violet", "icon_class": "icon-violet",
    },
    {
        "title": "SNAP Participation",
        "desc": "What is the correlation between SNAP participation rate and food insecurity rate across all counties in 2023?",
        "icon": "📋", "card_class": "card-teal", "icon_class": "icon-teal",
    },
    {
        "title": "Rural vs Urban",
        "desc": "Compare average food insecurity rates between Rural, Non-metro, and Metro counties in 2023.",
        "icon": "🗺️", "card_class": "card-rose", "icon_class": "icon-rose",
    },
]

# ── PAGE HEADER ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="ai-page-header">
    <div class="ai-page-icon">🤖</div>
    <div class="ai-page-title">AI Data Analyst</div>
    <div class="ai-page-sub">Get intelligent, code-verified insights about U.S. food insecurity data</div>
</div>
""", unsafe_allow_html=True)

# ── FILTER ROW ────────────────────────────────────────────────────────────────
years = sorted(df["year"].dropna().unique().tolist(), reverse=True)
states = ["All States"] + sorted(df["state_name"].dropna().unique().tolist())

f_col1, f_col2, f_col3 = st.columns([1, 2, 1])
with f_col1:
    selected_year = st.selectbox("📅 Filter by Year", years, index=0, label_visibility="visible")
with f_col2:
    selected_state = st.selectbox("📍 Filter by State", states, index=0, label_visibility="visible")
with f_col3:
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.ai_messages = []
        st.session_state.pending_prompt = None
        st.rerun()

# ── SAMPLE QUESTIONS ──────────────────────────────────────────────────────────
st.markdown("""
<div class="sample-section-title">
    <span>❓</span> Sample Questions
</div>
""", unsafe_allow_html=True)

card_cols = st.columns(3)
for i, q in enumerate(QUESTIONS):
    with card_cols[i % 3]:
        st.markdown(f"""
        <div class="q-card {q['card_class']}">
            <div class="q-card-icon {q['icon_class']}">{q['icon']}</div>
            <div class="q-card-title">{q['title']}</div>
            <div class="q-card-desc">{q['desc']}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ask →", key=f"qbtn_{i}", use_container_width=True):
            st.session_state.pending_prompt = q["desc"]
            st.rerun()

# ── CHAT WINDOW ───────────────────────────────────────────────────────────────
# Status bar
model_tag = "Gemini 2.5 Flash" if gemini_key else "Groq Llama-3.3-70b"
st.markdown(f"""
<div class="ai-status-bar">
    <span class="status-dot"></span>
    <span class="status-label">AI Assistant</span>
    <span class="status-sub">Ready to help · {model_tag}</span>
</div>
""", unsafe_allow_html=True)

chat_container = st.container(border=False)

with chat_container:
    if not st.session_state.ai_messages:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">💬</div>
            <div class="empty-title">Start a conversation</div>
            <div class="empty-sub">Select a sample question above or type your own question below.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Show context separator on first message
        filter_label = f"Year: {selected_year}" + (f" · {selected_state}" if selected_state != "All States" else "")
        st.markdown(
            f'<div style="text-align:center;color:#94a3b8;font-size:0.78rem;margin:0.5rem 0 1rem;">'
            f'<span style="background:#f1f5f9;padding:0.25rem 0.9rem;border-radius:99px;">Started Conversation · {filter_label}</span>'
            f'</div>',
            unsafe_allow_html=True
        )
        for msg in st.session_state.ai_messages:
            if msg["role"] == "user":
                with st.chat_message("user"):
                    st.markdown(msg["content"])
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(msg["content"])
                    if msg.get("code"):
                        with st.expander("🔍 View executed code & raw output"):
                            st.code(msg["code"], language="python")
                            if msg.get("raw_output"):
                                st.caption(f"Raw output: {msg['raw_output']}")

# ── INPUT BAR ─────────────────────────────────────────────────────────────────
st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

inp_col, btn_col = st.columns([8, 1])
with inp_col:
    # Pre-fill from card click
    default_val = st.session_state.pending_prompt or ""
    user_input = st.text_input(
        "Ask a question about the data...",
        value=default_val,
        placeholder="Ask a question about the data...",
        label_visibility="collapsed",
        key="chat_input_box"
    )

with btn_col:
    send_clicked = st.button("⬆️ Send", type="primary", use_container_width=True)

# ── EXECUTION ─────────────────────────────────────────────────────────────────
prompt_to_run = None
if send_clicked and user_input.strip():
    prompt_to_run = user_input.strip()
elif st.session_state.pending_prompt and not send_clicked:
    # Auto-run when a card is clicked
    prompt_to_run = st.session_state.pending_prompt
    st.session_state.pending_prompt = None

if prompt_to_run:
    # Enrich prompt with active filter context
    filter_ctx = f"Focus on year={selected_year}"
    if selected_state != "All States":
        filter_ctx += f" and state_name='{selected_state}'"
    full_prompt = f"{prompt_to_run} ({filter_ctx})"

    st.session_state.ai_messages.append({"role": "user", "content": prompt_to_run})
    st.session_state.pending_prompt = None

    with st.spinner("Generating code and executing against live data..."):
        try:
            code = _llm_code(full_prompt)
            raw_output, error = _exec(code)

            if error:
                retry = f"{full_prompt}\n\nPrevious attempt failed:\n{error}\nPlease fix."
                code = _llm_code(retry)
                raw_output, error = _exec(code)

            if error:
                final = f"⚠️ Execution failed:\n```\n{error}\n```"
                raw_output = ""
            else:
                final = _llm_explain(prompt_to_run, code, raw_output)

            st.session_state.ai_messages.append({
                "role": "assistant",
                "content": final,
                "code": code,
                "raw_output": raw_output,
            })

        except Exception as e:
            st.session_state.ai_messages.append({
                "role": "assistant",
                "content": f"⚠️ Error: {e}",
                "code": None,
                "raw_output": None,
            })

    st.rerun()
