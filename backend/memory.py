# backend/memory.py

from datetime import datetime
import numpy as np

try:
    from backend.database import messages_collection
except ModuleNotFoundError:
    from database import messages_collection


def cosine_similarity(v1, v2):
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
    return float(dot_product / (norm_v1 * norm_v2))


def add_message(session_id: str, role: str, content: str):
    """
    Save a chat message to MongoDB for the specified session_id,
    generating and storing its embedding for semantic retrieval.
    """
    try:
        from backend.rag import get_embedding
    except ModuleNotFoundError:
        from rag import get_embedding

    try:
        embedding = get_embedding(content).tolist()
    except Exception:
        embedding = None

    messages_collection.insert_one({
        "session_id": session_id,
        "role": role,
        "content": content,
        "embedding": embedding,
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


def build_chat_history(session_id: str, question: str = None, limit_recent: int = 4, limit_relevant: int = 3):
    """
    Build a chat history context by combining the immediate recent messages
    and the most semantically relevant historical messages.
    """
    # 1. Fetch all messages for the session sorted chronologically
    cursor = messages_collection.find({"session_id": session_id}).sort("timestamp", 1)
    all_messages = list(cursor)
    
    if not all_messages:
        return ""
        
    # 2. Split into recent and older
    if len(all_messages) <= limit_recent:
        recent_messages = all_messages
        older_messages = []
    else:
        recent_messages = all_messages[-limit_recent:]
        older_messages = all_messages[:-limit_recent]
        
    # 3. Retrieve relevant older messages using vector similarity
    relevant_memories = []
    if older_messages and question:
        try:
            from backend.rag import get_embedding
        except ModuleNotFoundError:
            from rag import get_embedding
            
        try:
            query_emb = get_embedding(question)
            
            scored_messages = []
            for msg in older_messages:
                msg_emb_list = msg.get("embedding")
                if not msg_emb_list:
                    try:
                        # Fallback generation for legacy messages
                        msg_emb = get_embedding(msg["content"])
                        messages_collection.update_one(
                            {"_id": msg["_id"]},
                            {"$set": {"embedding": msg_emb.tolist()}}
                        )
                    except Exception:
                        continue
                else:
                    msg_emb = np.array(msg_emb_list, dtype=np.float32)
                    
                sim = cosine_similarity(query_emb, msg_emb)
                scored_messages.append((sim, msg))
                
            # Sort by similarity descending
            scored_messages.sort(key=lambda x: x[0], reverse=True)
            # Take top `limit_relevant`
            top_scored = scored_messages[:limit_relevant]
            
            # Sort selected memories chronologically so they make sense in the conversation flow
            relevant_memories = [item[1] for item in top_scored]
            relevant_memories.sort(key=lambda x: x.get("timestamp") or datetime.min)
        except Exception:
            # Fallback if embedding fails
            pass

    # 4. Format prompt section
    history_str = ""
    if relevant_memories:
        history_str += "Relevant Past Context:\n"
        for msg in relevant_memories:
            role_label = "User" if msg["role"] == "user" else "Assistant"
            history_str += f"[{role_label}]: {msg['content']}\n"
        history_str += "\n"
        
    history_str += "Recent Conversation:\n"
    for msg in recent_messages:
        role_label = "User" if msg["role"] == "user" else "Assistant"
        history_str += f"{role_label}: {msg['content']}\n"
        
    return history_str
