import os
from google import genai
from dotenv import load_dotenv

load_dotenv(override=True)
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

try:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents="Hello! Tell me a fun fact about apples."
    )
    print("SUCCESS! Output:")
    print(response.text)
except Exception as e:
    print(f"Error: {e}")
