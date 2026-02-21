import os
from google import genai
from dotenv import load_dotenv

# Load environment variables, overriding existing ones if necessary
load_dotenv(override=True)

def _get_api_key():
    # 1. Try Streamlit Secrets (for cloud deployments)
    try:
        import streamlit as st
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
        
    # 2. Fall back to local environment variables
    return os.environ.get("GEMINI_API_KEY")

def generate_insights(page_name: str, context_data: dict) -> str:
    """
    Generate insights using the Gemini Pro model based on the page context.
    """
    api_key = _get_api_key()
    if not api_key:
        return "⚠️ Error: Valid GEMINI_API_KEY not found in .env file or environment variables."
        
    try:
        # Use the new genai SDK
        client = genai.Client(api_key=api_key)
        
        # Build prompt
        prompt = f"""
You are an expert data analyst and public policy advisor analyzing a dashboard regarding Food Insecurity in the United States.

The user is currently viewing the "{page_name}" tab.
Here is the raw context data currently visible on their screen:
{context_data}

Please provide 3-4 bullet points of high-level insights interpreting this data. 
Focus on what the numbers *mean*, identify any alarming or interesting trends, and maintain a highly professional, McKinsey-grade consulting tone.
Keep the response concise and directly addressing the provided data parameters. Do not include markdown headers like "## Insights", just start directly with the bullet points.
"""

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
        
    except Exception as e:
        err_msg = str(e)
        if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
            return "⏳ **API Rate Limit Reached.** You are generating insights too quickly for the free-tier Gemini model (Limit: 15 requests per minute). Please wait about 10 seconds and try clicking 'Generate Insights' again."
        return f"⚠️ An error occurred while generating insights: {err_msg}"
