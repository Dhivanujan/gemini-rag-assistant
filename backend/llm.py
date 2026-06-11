# backend/llm.py

from google import genai

try:
    from backend.config import GEMINI_API_KEY
except ModuleNotFoundError:
    from config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)


import time
from google.genai import errors

def generate_response(question, context):
    prompt = f"""
You are a helpful AI assistant.

Use ONLY the provided context to answer.

Context:
{context}

Question:
{question}

Answer:
"""

    models = ["gemini-2.5-flash", "gemini-2.5-flash-lite"]
    
    last_error = None
    for model in models:
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )
                return response.text
            except errors.APIError as e:
                last_error = e
                # Retry on rate limit (429) or temporary server overload (503)
                if e.code in [429, 503] and attempt < 2:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                break
            except Exception as e:
                last_error = e
                break

    raise RuntimeError(f"All models failed to generate response. Last error: {last_error}")