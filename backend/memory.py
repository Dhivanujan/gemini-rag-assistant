# backend/memory.py

from datetime import datetime
try:
    from backend.database import messages_collection
except ModuleNotFoundError:
    from database import messages_collection


def add_message(session_id: str, role: str, content: str):
    """
    Save a chat message to MongoDB for the specified session_id.
    """
    messages_collection.insert_one({
        "session_id": session_id,
        "role": role,
        "content": content,
        "timestamp": datetime.utcnow()
    })


def get_recent_messages(session_id: str, limit: int = 10):
    """
    Retrieve recent messages for a specific session, sorted chronologically.
    """
    cursor = messages_collection.find(
        {"session_id": session_id}
    ).sort("timestamp", 1)
    
    messages = list(cursor)
    if len(messages) > limit:
        messages = messages[-limit:]
        
    return messages


def clear_memory(session_id: str):
    """
    Clear all messages for the specified session_id.
    """
    messages_collection.delete_many({"session_id": session_id})


def build_chat_history(session_id: str, limit: int = 10):
    """
    Construct a chat history string for context building in the LLM prompt.
    """
    messages = get_recent_messages(session_id, limit)
    
    history = ""
    for msg in messages:
        role_label = "User" if msg["role"] == "user" else "Assistant"
        history += f"{role_label}: {msg['content']}\n"
        
    return history
