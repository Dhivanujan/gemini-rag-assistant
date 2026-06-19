# backend/database/models.py

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    question: str
    context: str
    answer: str
    session_id: str

class MessageHistoryItem(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None

class HistoryResponse(BaseModel):
    history: List[MessageHistoryItem]
