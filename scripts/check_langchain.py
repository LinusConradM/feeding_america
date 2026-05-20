import os
import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.agents import create_pandas_dataframe_agent
from utils.llm import _get_api_key
app_df = pd.DataFrame({"state": ["AL", "TX", "CA"], "poverty_rate": [0.15, 0.12, 0.11], "population": [500, 3000, 4000]})

try:
    api_key = _get_api_key()
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key, temperature=0.0)
    agent = create_pandas_dataframe_agent(llm, app_df, verbose=False, allow_dangerous_code=True, return_intermediate_steps=True)
    res = agent.invoke({"input": "What is the average poverty rate?"})
    print("OUTPUT:", res["output"])
    print("INTERMEDIATE:", res["intermediate_steps"])
except Exception as e:
    print("ERR:", e)
