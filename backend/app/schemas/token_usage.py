from pydantic import BaseModel
from datetime import date


class TokenUsageSummary(BaseModel):
    total_tokens: int
    today_tokens: int


class DailyUsage(BaseModel):
    date: date
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
