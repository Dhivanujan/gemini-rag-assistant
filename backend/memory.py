# backend/memory.py

from datetime import datetime
import os
import pickle
import threading
import faiss
import numpy as np

try:
    from backend.database import messages_collection
except ModuleNotFoundError:
    from database import messages_collection

memory_lock = threading.Lock()


def get_memory_paths(session_id: str):
    """
    Generate absolute paths for the session-isolated memory store.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    vectorstore_dir = os.path.join(base_dir, "vectorstore")
    os.makedirs(vectorstore_dir, exist_ok=True)
    
    # Sanitize session_id to prevent path traversal
    clean_id = "".join([c for c in session_id if c.isalnum() or c in ("-", "_")])
    if not clean_id:
        clean_id = "default"
        
    index_path = os.path.join(vectorstore_dir, f"memory_{clean_id}.index")
    chunks_path = os.path.join(vectorstore_dir, f"memory_{clean_id}_chunks.pkl")
    return index_path, chunks_path


def init_memory_store(index_path: str, chunks_path: str):
    """
    Initialize empty FAISS index and chunks file if not present.
    """
    if not os.path.exists(index_path) or not os.path.exists(chunks_path):
        dimension = 384
        index = faiss.IndexFlatL2(dimension)
        faiss.write_index(index, index_path)
        with open(chunks_path, "wb") as f:
            pickle.dump([], f)


def load_memory_store(session_id: str):
    """
    Load the session-specific memory index and chunks list.
    """
    index_path, chunks_path = get_memory_paths(session_id)
    with memory_lock:
        init_memory_store(index_path, chunks_path)
        index = faiss.read_index(index_path)
        with open(chunks_path, "rb") as f:
            chunks = pickle.load(f)
        return index, chunks


def save_memory_store(session_id: str, index, chunks):
    """
    Save the session-specific memory index and chunks list to disk.
    """
    index_path, chunks_path = get_memory_paths(session_id)
    with memory_lock:
        faiss.write_index(index, index_path)
        with open(chunks_path, "wb") as f:
            pickle.dump(chunks, f)


def add_to_long_term_memory(session_id: str, content: str):
    """
    Embed content and add it to the session-specific FAISS index.
    """
    try:
        from backend.rag import get_embedding
    except ModuleNotFoundError:
        from rag import get_embedding

    try:
        emb = get_embedding(content)
        emb_expanded = np.array([emb], dtype=np.float32)
        
        index, chunks = load_memory_store(session_id)
        index.add(emb_expanded)
        chunks.append(content)
        save_memory_store(session_id, index, chunks)
    except Exception as e:
        print(f"Error adding to long-term memory: {e}")


def search_long_term_memory(session_id: str, question: str, k: int = 3):
    """
    Retrieve semantically relevant memories from the session's FAISS index.
    """
    if not question:
        return []
        
    index, chunks = load_memory_store(session_id)
    if index.ntotal == 0:
        return []
        
    try:
        from backend.rag import get_embedding
    except ModuleNotFoundError:
        from rag import get_embedding

    try:
        query_emb = get_embedding(question)
        query_emb_expanded = np.array([query_emb], dtype=np.float32)
        
        k = min(k, len(chunks))
        distances, indices = index.search(query_emb_expanded, k)
        
        results = []
        for idx in indices[0]:
            if idx != -1 and idx < len(chunks):
                results.append(chunks[idx])
        return results
    except Exception as e:
        print(f"Error searching long-term memory: {e}")
        return []


def clear_long_term_memory(session_id: str):
    """
    Delete session-specific FAISS storage files.
    """
    index_path, chunks_path = get_memory_paths(session_id)
    with memory_lock:
        if os.path.exists(index_path):
            try:
                os.remove(index_path)
            except Exception:
                pass
        if os.path.exists(chunks_path):
            try:
                os.remove(chunks_path)
            except Exception:
                pass


def add_message(session_id: str, role: str, content: str):
    """
    Save message to short-term storage (MongoDB).
    """
    messages_collection.insert_one({
        "session_id": session_id,
        "role": role,
        "content": content,
        "timestamp": datetime.utcnow()
    })


def get_recent_messages(session_id: str, limit: int = 15):
    """
    Retrieve recent messages from MongoDB (short-term memory).
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
    Clear both short-term MongoDB history and long-term FAISS index.
    """
    # Clear Short-Term (MongoDB)
    messages_collection.delete_many({"session_id": session_id})
    # Clear Long-Term (FAISS files)
    clear_long_term_memory(session_id)


def build_chat_history(session_id: str, limit_recent: int = 15):
    """
    Build short-term dialogue context string from MongoDB messages.
    """
    messages = get_recent_messages(session_id, limit_recent)
    
    history = ""
    for msg in messages:
        role_label = "User" if msg["role"] == "user" else "Assistant"
        history += f"{role_label}: {msg['content']}\n"
        
    return history
