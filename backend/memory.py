# backend/memory.py

chat_history = []

def add_message(role, content):
    chat_history.append({
        "role": role,
        "content": content
    })

def get_recent_messages(limit=10):
    return chat_history[-limit:]

def clear_memory():
    chat_history.clear()

def build_chat_history():

    messages = get_recent_messages()

    history = ""

    for msg in messages:

        history += (
            f"{msg['role']}: "
            f"{msg['content']}\n"
        )

    return history

