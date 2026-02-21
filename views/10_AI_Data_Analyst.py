"""
Agentic AI Data Analyst - Natural language dataframe querying
"""

import os
import streamlit as st
import pandas as pd
import numpy as np
import io
import time
from utils.theme import inject_tailwind, page_header, COLORS
from utils.components import section_header, info_banner
from utils.data_loader import load_data
from utils.llm import _get_api_key
from langchain_experimental.agents import create_pandas_dataframe_agent

st.set_page_config(page_title="AI Data Analyst", page_icon="🤖", layout="wide")
inject_tailwind()

page_header("AI Data Analyst", "Ask complex questions in plain english. The AI will write and execute data analysis code to find the answer.", "robot")

# App State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    st.session_state.agent = None

api_key = _get_api_key()

if not api_key:
    info_banner("⚠️ A valid GEMINI_API_KEY is required to use the Agentic LLM features.", "warning")
    st.stop()

df = load_data()

# Initialize Langchain Pandas Agent (Gemini → Groq fallback)
try:
    if st.session_state.agent is None:
        gemini_key = api_key
        groq_key = os.environ.get("GROQ_API_KEY") or (
            st.secrets.get("GROQ_API_KEY") if hasattr(st, "secrets") else None
        )

        llm = None
        active_model = ""

        # Attempt 1: Gemini
        if gemini_key:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                test_llm = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash",
                    google_api_key=gemini_key,
                    temperature=0.0
                )
                # Quick validation ping
                test_llm.invoke("ping")
                llm = test_llm
                active_model = "gemini-2.5-flash"
            except Exception:
                llm = None  # Fall through to Groq

        # Attempt 2: Groq fallback
        if llm is None and groq_key:
            from langchain_groq import ChatGroq
            llm = ChatGroq(
                model="llama-3.3-70b-versatile",
                api_key=groq_key,
                temperature=0.0
            )
            active_model = "llama-3.3-70b-versatile (Groq)"

        if llm is None:
            st.error("⚠️ No valid AI API key found. Please set GEMINI_API_KEY or GROQ_API_KEY.")
            st.stop()

        st.session_state.active_model = active_model
        st.session_state.agent = create_pandas_dataframe_agent(
            llm,
            df,
            verbose=False,
            allow_dangerous_code=True,
            agent_type="tool-calling",
            return_intermediate_steps=True,
            prefix=(
                "You are a Senior Data Scientist analyzing the Feeding America U.S. Food Insecurity dataset. "
                "The dataset is loaded as a pandas DataFrame named `df` with 40,000+ rows.\n\n"
                "STRICT RULES:\n"
                "1. You MUST ALWAYS use the python_repl_ast tool to write and execute pandas code BEFORE providing any answer.\n"
                "2. NEVER assume data does not exist without running `df['year'].unique()` or equivalent to verify.\n"
                "3. NEVER return a final answer without first verifying via code execution.\n"
                "4. The `year` column is of dtype `Int64` (nullable integer). Filter it like: `df[df['year'] == 2023]`.\n\n"
                "VERIFIED SCHEMA:\n"
                "- `year` (Int64): 2009–2023. ALL 15 years have data. 2023 has 3,142 rows.\n"
                "- `state` (str): 2-letter abbreviation (e.g. 'TX')\n"
                "- `state_name` (str): Full state name\n"
                "- `county` (str): County name\n"
                "- `overall_food_insecurity_rate` (float): % of total pop food insecure\n"
                "- `child_food_insecurity_rate` (float): % of children food insecure\n"
                "- `poverty_rate` (float): % in poverty\n"
                "- `unemployment_rate` (float): % unemployed\n"
                "- `median_income` (float): Median household income in USD\n"
                "- `cost_per_meal` (float): Local cost per meal in USD\n"
                "- `snap_rate` (float): SNAP participation rate\n"
                "- `population` (Int64): County population\n"
                "- `no_of_food_insecure_persons_overall` (Int64): Raw count\n"
                "- `no_of_food_insecure_children` (Int64): Raw count\n"
                "- `weighted_annual_food_budget_shortfall` (float): Annual budget shortfall in USD\n"
                "- `fi_category` (category): 'Low', 'Moderate', 'High', 'Very High'\n"
                "- `urban_rural` (category): 'Rural', 'Non-metro', 'Metro'\n\n"
                "When formatting your final answer use markdown with bold headers and bullet points."
            )
        )
except Exception as e:
    st.error(f"Failed to initialize AI Agent: {e}")
    st.stop()

col1, col2 = st.columns([3, 1])

with col1:
    st.markdown('<div class="bg-gray-50 border border-gray-200 rounded-xl p-6 min-h-[500px]">', unsafe_allow_html=True)
    
    # Render chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])
            if "code" in msg:
                with st.expander("Show AI-Generated Code"):
                    st.code(msg["code"], language="python")

    # Chat input
    if prompt := st.chat_input("E.g., Which 5 counties in Texas saw the highest spike in child food insecurity between 2019 and 2021?"):
        # Append user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant", avatar="🤖"):
            placeholder = st.empty()
            placeholder.markdown(f'<i class="fas fa-circle-notch fa-spin text-blue-500 mr-2"></i> Analyzing {len(df):,} rows of data...', unsafe_allow_html=True)
            
            try:
                # Send message to model
                response = st.session_state.agent.invoke({"input": prompt})
                
                # Extract code snippets if tool was used
                executed_code = ""
                intermediate_steps = response.get("intermediate_steps", [])
                for action, observation in intermediate_steps:
                    # action.tool_input handles the python code string generated by the agent
                    code_val = action.tool_input
                    if isinstance(code_val, dict) and 'query' in code_val:
                        code_val = code_val['query']
                    executed_code += f"# Code Executed by AI:\n{code_val}\n\n"
                    executed_code += f"# Result:\n{observation}\n\n"

                final_answer = response.get("output", "")
                placeholder.markdown(final_answer)
                
                if executed_code:
                    with st.expander("Show AI-Generated Code"):
                        st.code(executed_code, language="python")
                
                # Save assistant response
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": final_answer,
                    "code": executed_code if executed_code else None
                })
                
            except Exception as e:
                placeholder.error(f"Agent Execution Error: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown(
        """
        <div class="bg-blue-50 rounded-xl p-5 border border-blue-100 shadow-sm">
            <h3 class="text-blue-800 font-bold text-sm mb-3">
                <i class="fas fa-lightbulb text-yellow-500 mr-2"></i>How this works
            </h3>
            <p class="text-sm text-blue-900 leading-relaxed mb-4">
                This isn't a standard chatbot. It is an <b>Agentic Code Execution Engine</b> powered by Gemini 2.5 Flash.
            </p>
            <p class="text-sm text-blue-900 leading-relaxed mb-4">
                When you ask a question, the AI won't guess the answer or regurgitate its training data. Instead, it will <b>write custom Python Pandas code</b>, securely execute that code against the live <code>Dataframe</code> backing this dashboard, and synthesize the mathematical outputs into a precise answer.
            </p>
            <h4 class="text-xs font-bold text-blue-800 uppercase tracking-wider mb-2 mt-4">Example Questions</h4>
            <ul class="text-sm text-blue-900 space-y-3">
                <li class="bg-white p-2 rounded border border-blue-200 shadow-sm font-medium">Which state had the largest <b>decrease</b> in child food insecurity between 2012 and 2022?</li>
                <li class="bg-white p-2 rounded border border-blue-200 shadow-sm font-medium">What is the average poverty rate and cost per meal for the 10 counties with the highest overall food insecurity in 2023?</li>
                <li class="bg-white p-2 rounded border border-blue-200 shadow-sm font-medium">List the top 5 'Rural' counties with the lowest unemployment rate but highest SNAP participation.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True
    )
