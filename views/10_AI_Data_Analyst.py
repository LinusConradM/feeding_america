"""
Agentic AI Data Analyst - Natural language dataframe querying
"""

import streamlit as st
import pandas as pd
import numpy as np
import io
import time
from utils.theme import inject_tailwind, page_header, COLORS
from utils.components import section_header, info_banner
from utils.data_loader import load_data
from utils.llm import _get_api_key
from google import genai
from google.genai import types

st.set_page_config(page_title="AI Data Analyst", page_icon="🤖", layout="wide")
inject_tailwind()

page_header("AI Data Analyst", "Ask complex questions in plain english. The AI will write and execute data analysis code to find the answer.", "robot")

# App State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "client" not in st.session_state:
    st.session_state.client = None
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None

api_key = _get_api_key()

if not api_key:
    info_banner("⚠️ A valid GEMINI_API_KEY is required to use the Agentic LLM features.", "warning")
    st.stop()

# Initialize Gemini Client with experimental Code Execution tool
try:
    if st.session_state.client is None:
        st.session_state.client = genai.Client(api_key=api_key)
        
    if st.session_state.chat_session is None:
        st.session_state.chat_session = st.session_state.client.chats.create(
            model='gemini-2.5-flash',
            config=types.GenerateContentConfig(
                tools=[{'code_execution': {}}],
                temperature=0.0,
                system_instruction=(
                    "You are a Senior Data Scientist analyzing a U.S. Food Insecurity dataset. "
                    "The dataset is loaded in the python environment as a pandas DataFrame named `df`. "
                    "You MUST use python code execution to analytically answer the user's question by querying `df`. "
                    "\n\nHere are the columns in `df` along with their types:\n"
                    "- `year` (Int64): Year of the observation (2009-2023)\n"
                    "- `state` (object): 2-letter state abbreviation (e.g. 'TX')\n"
                    "- `state_name` (object): Full state name\n"
                    "- `county` (object): County name\n"
                    "- `overall_food_insecurity_rate` (float64): % of total pop food insecure\n"
                    "- `child_food_insecurity_rate` (float64): % of children food insecure\n"
                    "- `poverty_rate` (float64): % in poverty\n"
                    "- `unemployment_rate` (float64): % unemployed\n"
                    "- `median_income` (float64): Median household income in dollars\n"
                    "- `cost_per_meal` (float64): Local cost per meal in dollars\n"
                    "- `snap_rate` (float64): SNAP participation rate\n"
                    "- `population` (Int64): County population\n"
                    "- `no_of_food_insecure_persons_overall` (Int64): Raw count\n"
                    "- `no_of_food_insecure_children` (Int64): Raw count\n"
                    "- `weighted_annual_food_budget_shortfall` (float64): Total budget shortfall in dollars\n"
                    "- `fi_category` (category): 'Low', 'Moderate', 'High', 'Very High'\n"
                    "- `urban_rural` (category): 'Rural', 'Non-metro', 'Metro'\n"
                    "\nAlways return formatted data in standard professional markdown. Never guess the answer without writing and executing the code first."
                )
            )
        )
except Exception as e:
    st.error(f"Failed to initialize AI Client: {e}")
    st.stop()

# The global DF needs to be accessible to the code execution sandbox
import builtins
df = load_data()
builtins.df = df # Gross hack for standard python `exec()` sandbox. The Gemini API tool manages its own state but we specify the prompt schema.
# Note: Google's GenAI SDK handles the backend sandbox autonomously using its own secure environment. 
# It does NOT execute code on the user's physical machine or rely on `builtins.df`. It operates on the schema provided.

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
                response = st.session_state.chat_session.send_message(prompt)
                
                # Extract code snippets if tool was used
                executed_code = ""
                for part in response.parts:
                    if part.executable_code:
                        executed_code += f"# Code Executed by AI:\n{part.executable_code.code}\n\n"
                    if part.code_execution_result:
                        executed_code += f"# Result:\n{part.code_execution_result.output}\n"

                placeholder.markdown(response.text)
                
                if executed_code:
                    with st.expander("Show AI-Generated Code"):
                        st.code(executed_code, language="python")
                
                # Save assistant response
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response.text,
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
