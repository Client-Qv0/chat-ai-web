import json
import httpx
from app.core.config import settings


async def stream_qwen_response(
    messages: list[dict],
    enable_thinking: bool = False,
) -> str:
    system_prompt = "You are a helpful AI assistant."
    if enable_thinking:
        system_prompt = "Please think step-by-step before answering. " + system_prompt

    payload = {
        "model": settings.LLM_MODEL,
        "messages": [{"role": "system", "content": system_prompt}] + messages,
        "stream": True,
        "options": {"temperature": 0.7},
    }

    async with httpx.AsyncClient(timeout=300.0) as client:
        async with client.stream("POST", f"{settings.LLM_API_URL}/api/chat", json=payload) as response:
            async for line in response.aiter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        content = data.get("message", {}).get("content", "")
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue
