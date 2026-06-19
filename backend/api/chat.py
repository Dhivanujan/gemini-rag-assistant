# backend/api/chat.py

import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from backend.database.models import ChatRequest, ChatResponse, HistoryResponse, MessageHistoryItem
from backend.services.llm_service import generate_response, generate_response_stream
from backend.services.rag_service import get_context, get_knowledge_base_index
from backend.services.memory_service import (
    add_message,
    add_to_long_term_memory,
    build_chat_history,
    search_long_term_memory,
    get_recent_messages,
    clear_memory
)

router = APIRouter()


@router.post("/chat")
def chat(request: ChatRequest):
    try:
        # 1. Save User Message to Short-Term (MongoDB) and Long-Term (FAISS)
        add_message(request.session_id, "user", request.message)
        add_to_long_term_memory(request.session_id, f"User: {request.message}")

        # 2. Load Short-Term Session History from MongoDB (last 15 messages)
        short_term_memory = build_chat_history(request.session_id, limit_recent=15)

        # 3. Perform Long-Term Memory Vector Search in FAISS
        relevant_memories = search_long_term_memory(request.session_id, request.message, k=3)
        long_term_context = "\n".join(relevant_memories)

        # 4. Perform Knowledge RAG Search in FAISS
        knowledge_index, knowledge_chunks = get_knowledge_base_index()
        knowledge_context = get_context(
            request.message,
            knowledge_index,
            knowledge_chunks
        )

        if request.stream:
            def event_generator():
                try:
                    # 1. Yield metadata event (RAG context & session_id)
                    yield f"data: {json.dumps({'type': 'context', 'context': knowledge_context, 'session_id': request.session_id})}\n\n"

                    # 2. Yield LLM chunks and accumulate response
                    full_response = ""
                    for chunk in generate_response_stream(
                        request.message,
                        knowledge_context,
                        short_term_memory,
                        long_term_context
                    ):
                        full_response += chunk
                        yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"

                    # 3. Save Assistant response to Short-Term & Long-Term
                    add_message(request.session_id, "assistant", full_response)
                    add_to_long_term_memory(request.session_id, f"Assistant: {full_response}")

                    # 4. Yield done event
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                except Exception as e:
                    yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

            return StreamingResponse(event_generator(), media_type="text/event-stream")

        else:
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

            return ChatResponse(
                question=request.message,
                context=knowledge_context,
                answer=answer,
                session_id=request.session_id
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{session_id}", response_model=HistoryResponse)
def get_history(session_id: str):
    try:
        raw_messages = get_recent_messages(session_id, limit=50)
        formatted = []
        for msg in raw_messages:
            formatted.append(MessageHistoryItem(
                role=msg["role"],
                content=msg["content"],
                timestamp=msg.get("timestamp").isoformat() if msg.get("timestamp") else None
            ))
        return HistoryResponse(history=formatted)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/history/{session_id}")
def delete_history(session_id: str):
    try:
        clear_memory(session_id)
        return {
            "status": "success",
            "message": f"Chat history and long-term memory for session '{session_id}' have been cleared."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
