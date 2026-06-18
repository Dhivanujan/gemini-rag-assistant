# backend/main.py

from fastapi import FastAPI
from pydantic import BaseModel

try:
    from backend.rag import (
        load_documents,
        build_vector_store,
        get_context
    )
    from backend.llm import generate_response
    from backend.memory import (
        add_message,
        build_chat_history,
        get_recent_messages,
        clear_memory
    )
except ModuleNotFoundError:
    from rag import (
        load_documents,
        build_vector_store,
        get_context
    )
    from llm import generate_response
    from memory import (
        add_message,
        build_chat_history,
        get_recent_messages,
        clear_memory
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

# Build RAG at startup
chunks = load_documents()
index = build_vector_store(chunks)


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


@app.post("/chat")
def chat(request: ChatRequest):
    # 1. Retrieve or build chat history for the session
    memory = build_chat_history(request.session_id)

    # 2. Get relevant context from RAG vector store
    context = get_context(
        request.message,
        index,
        chunks
    )

    # 3. Generate response via LLM incorporating memory and context
    answer = generate_response(
        request.message,
        context,
        memory
    )

    # 4. Save message pair to MongoDB memory
    add_message(request.session_id, "user", request.message)
    add_message(request.session_id, "assistant", answer)

    return {
        "question": request.message,
        "context": context,
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
        "message": f"Chat history for session '{session_id}' has been cleared."
    }