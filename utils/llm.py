import os
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

def _get_groq_key():
    try:
        import streamlit as st
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except Exception:
        pass
    return os.environ.get("GROQ_API_KEY")

def generate_insights(page_name: str, context_data: dict) -> str:
    """
    Generate insights using Gemini Pro with a Groq fallback.
    """
    gemini_key = _get_api_key()
    groq_key = _get_groq_key()

    prompt = f"""
You are an expert data analyst and public policy advisor analyzing a dashboard regarding Food Insecurity in the United States.

The user is currently viewing the "{page_name}" tab.
Here is the raw context data currently visible on their screen:
{context_data}

Please provide 3-4 bullet points of high-level insights interpreting this data. 
Focus on what the numbers *mean*, identify any alarming or interesting trends, and maintain a highly professional, McKinsey-grade consulting tone.
Keep the response concise and directly addressing the provided data parameters. Do not include markdown headers like "## Insights", just start directly with the bullet points.
"""

    # --- Attempt 1: Gemini ---
    if gemini_key:
        try:
            from google import genai
            client = genai.Client(api_key=gemini_key)
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            return response.text
        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                return "⏳ **API Rate Limit Reached.** Please wait ~10 seconds and try again."
            # Any other error (key expired, etc.) → fall through to Groq
            pass

    # --- Attempt 2: Groq Fallback ---
    if groq_key:
        try:
            import groq as groq_sdk
            client = groq_sdk.Groq(api_key=groq_key)
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            return f"*[Powered by Groq Llama-3.3-70b Fallback]*\n\n{response.choices[0].message.content}"
        except Exception as e:
            return f"⚠️ Both Gemini and Groq failed: {e}"

    return "⚠️ No valid API key found. Please set GEMINI_API_KEY or GROQ_API_KEY."
