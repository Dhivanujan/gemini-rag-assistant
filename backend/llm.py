# backend/llm.py

import time
from google import genai
from google.genai import errors

try:
    from backend.config import GEMINI_API_KEY
except ModuleNotFoundError:
    from config import GEMINI_API_KEY


client = genai.Client(api_key=GEMINI_API_KEY)


def generate_response(question, context, memory):
    """
    Generate an AI response using:
    - memory: previous conversation history
    - context: retrieved RAG knowledge base context
    - question: current user question
    """

    # Format history block: check if memory ends with the current question to avoid duplication
    # since the user message is saved before loading memory in the new request flow.
    mem_stripped = memory.strip() if memory else ""
    user_q_format = f"User: {question}"
    
    if mem_stripped.endswith(user_q_format) or mem_stripped.endswith(question.strip()):
        history_block = mem_stripped
    else:
        if mem_stripped:
            history_block = f"{mem_stripped}\n{user_q_format}"
        else:
            history_block = user_q_format

    prompt = f"""
You are a helpful AI assistant.

Use the knowledge base context when it contains relevant information.
If the answer is not in the knowledge base, use the conversation history and your general reasoning.

Knowledge Base Context:
{context}

Conversation History:
{history_block}
Assistant:
"""


    models = [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite"
    ]

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

                # Retry on temporary failures
                if getattr(e, "code", None) in [429, 503] and attempt < 2:
                    time.sleep(1.5 * (attempt + 1))
                    continue

                break

            except Exception as e:
                last_error = e
                break

    raise RuntimeError(
        f"All models failed to generate response. Last error: {last_error}"
    )