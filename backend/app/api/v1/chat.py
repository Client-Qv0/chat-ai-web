import json
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.v1.dependencies import get_current_user
from app.models.user import User
from app.models.message import MessageRole
from app.schemas.chat import ConversationResponse, ChatMessageRequest, MessageResponse
from app.services.chat_service import (
    get_conversations, create_conversation, get_conversation_by_route_id,
    get_messages, create_message,
)
from app.services.llm_service import stream_qwen_response

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_conversations(db, current_user)


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def new_conversation(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_conversation(db, current_user)


@router.get("/conversations/{route_id}/messages", response_model=list[MessageResponse])
async def list_messages(
    route_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conv = await get_conversation_by_route_id(db, route_id, current_user)
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return await get_messages(db, conv)


@router.post("/conversations/{route_id}/messages")
async def send_message(
    route_id: str,
    data: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conv = await get_conversation_by_route_id(db, route_id, current_user)
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    await create_message(db, conv, MessageRole.user, data.content, data.metadata)

    existing_messages = await get_messages(db, conv)
    llm_messages = [
        {"role": msg.role.value, "content": msg.content}
        for msg in existing_messages[-20:]
    ]
    enable_thinking = data.metadata.get("thinking", False)

    async def event_stream():
        full_response = ""
        async for chunk in stream_qwen_response(llm_messages, enable_thinking):
            full_response += chunk
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        await create_message(
            db, conv, MessageRole.assistant, full_response,
            tokens_used=len(full_response) // 4,
        )
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
