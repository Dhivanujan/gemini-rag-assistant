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
except ModuleNotFoundError:
    from rag import (
        load_documents,
        build_vector_store,
        get_context
    )
    from llm import generate_response

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


@app.post("/chat")
def chat(request: ChatRequest):

    context = get_context(
        request.message,
        index,
        chunks
    )

    answer = generate_response(
        request.message,
        context
    )

    return {
        "question": request.message,
        "context": context,
        "answer": answer
    }