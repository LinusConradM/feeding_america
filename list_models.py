import os
from google import genai
from dotenv import load_dotenv

load_dotenv(override=True)
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

try:
    models = client.models.list()
    for m in models:
        print(f"Name: {m.name}, Display: {m.display_name}")
except Exception as e:
    print(f"Error: {e}")
