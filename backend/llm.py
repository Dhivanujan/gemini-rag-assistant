# backend/llm.py

import time
from google import genai
from google.genai import errors

try:
    from backend.config import GEMINI_API_KEY
except ModuleNotFoundError:
    from config import GEMINI_API_KEY


client = genai.Client(api_key=GEMINI_API_KEY)


def generate_response(question, context, short_term_memory, long_term_memory=""):
    """
    Generate an AI response using:
    - short_term_memory: recent chat messages
    - long_term_memory: semantically retrieved facts from past conversations
    - context: retrieved RAG knowledge base context
    - question: current user question
    """

    # Format history blocks: check if memory ends with the current question to avoid duplication
    # since the user message is saved before loading memory in the new request flow.
    short_term_stripped = short_term_memory.strip() if short_term_memory else ""
    user_q_format = f"User: {question}"
    
    if short_term_stripped.endswith(user_q_format) or short_term_stripped.endswith(question.strip()):
        short_term_block = short_term_stripped
    else:
        if short_term_stripped:
            short_term_block = f"{short_term_stripped}\n{user_q_format}"
        else:
            short_term_block = user_q_format

    long_term_block = long_term_memory.strip() if long_term_memory else "No relevant long-term memories retrieved."

    prompt = f"""
You are a helpful AI assistant.

Use the knowledge base context when it contains relevant information.
Use the long-term retrieved memories and short-term conversation history to maintain context and remember user facts.

Knowledge Base Context:
{context}

Long-Term Retrieved Memories:
{long_term_block}

Short-Term Conversation History:
{short_term_block}
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