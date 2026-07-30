import json
import time
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.api_key_service import verify_api_key
from app.services.llm_service import stream_qwen_response

router = APIRouter(prefix="/v1", tags=["openai-compatible"])


@router.post("/chat/completions")
async def chat_completions(request: Request, db: AsyncSession = Depends(get_db)):
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    api_key = auth_header[7:]
    user = await verify_api_key(db, api_key)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    body = await request.json()
    messages = body.get("messages", [])
    model = body.get("model", "qwen3.5:0.8b")
    stream = body.get("stream", False)

    async def event_stream():
        full = ""
        async for chunk in stream_qwen_response(messages):
            full += chunk
            yield f"data: {json.dumps({'id': 'chatcmpl-xxx', 'object': 'chat.completion.chunk', 'created': int(time.time()), 'model': model, 'choices': [{'delta': {'content': chunk}, 'index': 0}]})}\n\n"
        yield "data: [DONE]\n\n"

    if stream:
        return StreamingResponse(event_stream(), media_type="text/event-stream")

    full = ""
    async for chunk in stream_qwen_response(messages):
        full += chunk

    return {
        "id": "chatcmpl-xxx",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [{"index": 0, "message": {"role": "assistant", "content": full}, "finish_reason": "stop"}],
    }
