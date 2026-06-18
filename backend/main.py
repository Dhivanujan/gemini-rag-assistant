# backend/main.py

from fastapi import FastAPI
from pydantic import BaseModel

try:
    from backend.rag import (
        get_context,
        get_knowledge_base
    )
    from backend.llm import generate_response
    from backend.memory import (
        add_message,
        build_chat_history,
        get_recent_messages,
        clear_memory,
        add_to_long_term_memory,
        search_long_term_memory
    )
except ModuleNotFoundError:
    from rag import (
        get_context,
        get_knowledge_base
    )
    from llm import generate_response
    from memory import (
        add_message,
        build_chat_history,
        get_recent_messages,
        clear_memory,
        add_to_long_term_memory,
        search_long_term_memory
    )

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI RAG Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load or build Knowledge Base FAISS index at startup
knowledge_index, knowledge_chunks = get_knowledge_base()


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


@app.post("/chat")
def chat(request: ChatRequest):
    # 1. Save User Message to Short-Term (MongoDB) and Long-Term (FAISS)
    add_message(request.session_id, "user", request.message)
    add_to_long_term_memory(request.session_id, f"User: {request.message}")

    # 2. Load Short-Term Session History from MongoDB (last 15 messages)
    short_term_memory = build_chat_history(request.session_id, limit_recent=15)

    # 3. Perform Long-Term Memory Vector Search in FAISS
    relevant_memories = search_long_term_memory(request.session_id, request.message, k=3)
    long_term_context = "\n".join(relevant_memories)

    # 4. Perform Knowledge RAG Search in FAISS
    knowledge_context = get_context(
        request.message,
        knowledge_index,
        knowledge_chunks
    )

    # 5. Generate Response via LLM
    answer = generate_response(
        request.message,
        knowledge_context,
        short_term_memory,
        long_term_context
    )

    # 6. Save Assistant Response to Short-Term (MongoDB) and Long-Term (FAISS)
    add_message(request.session_id, "assistant", answer)
    add_to_long_term_memory(request.session_id, f"Assistant: {answer}")

    return {
        "question": request.message,
        "context": knowledge_context,
        "answer": answer,
        "session_id": request.session_id
    }


@app.get("/history/{session_id}")
def get_history(session_id: str):
    raw_messages = get_recent_messages(session_id, limit=50)
    formatted = []
    for msg in raw_messages:
        formatted.append({
            "role": msg["role"],
            "content": msg["content"],
            "timestamp": msg.get("timestamp").isoformat() if msg.get("timestamp") else None
        })
    return {"history": formatted}


@app.delete("/history/{session_id}")
def delete_history(session_id: str):
    clear_memory(session_id)
    return {
        "status": "success",
        "message": f"Chat history and long-term memory for session '{session_id}' have been cleared."
    }