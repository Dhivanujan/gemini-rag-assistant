# backend/main.py

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.chat import router as chat_router
from backend.services.rag_service import get_knowledge_base_index

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load or build Knowledge Base FAISS index at startup
    print("Initializing knowledge base FAISS index...")
    get_knowledge_base_index()
    yield
    print("Shutting down...")

app = FastAPI(title="AI RAG Chatbot", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(chat_router)