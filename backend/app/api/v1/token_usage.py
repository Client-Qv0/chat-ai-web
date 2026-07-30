from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.v1.dependencies import get_current_user
from app.models.user import User
from app.models.token_usage import TokenUsageLog
from app.schemas.token_usage import TokenUsageSummary, DailyUsage

router = APIRouter(prefix="/token-usage", tags=["token-usage"])


@router.get("/summary", response_model=TokenUsageSummary)
async def get_summary(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    total_result = await db.execute(
        select(func.coalesce(func.sum(TokenUsageLog.prompt_tokens + TokenUsageLog.completion_tokens), 0))
        .where(TokenUsageLog.user_id == current_user.id)
    )
    total_tokens = total_result.scalar() or 0

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_result = await db.execute(
        select(func.coalesce(func.sum(TokenUsageLog.prompt_tokens + TokenUsageLog.completion_tokens), 0))
        .where(TokenUsageLog.user_id == current_user.id, TokenUsageLog.created_at >= today_start)
    )
    today_tokens = today_result.scalar() or 0

    return TokenUsageSummary(total_tokens=total_tokens, today_tokens=today_tokens)


@router.get("/daily", response_model=list[DailyUsage])
async def get_daily_usage(
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    since = datetime.utcnow() - timedelta(days=days)
    result = await db.execute(
        select(
            func.date(TokenUsageLog.created_at).label("date"),
            func.coalesce(func.sum(TokenUsageLog.prompt_tokens), 0).label("prompt_tokens"),
            func.coalesce(func.sum(TokenUsageLog.completion_tokens), 0).label("completion_tokens"),
        )
        .where(TokenUsageLog.user_id == current_user.id, TokenUsageLog.created_at >= since)
        .group_by(func.date(TokenUsageLog.created_at))
        .order_by(func.date(TokenUsageLog.created_at))
    )
    rows = result.all()
    return [
        DailyUsage(
            date=row.date,
            prompt_tokens=row.prompt_tokens,
            completion_tokens=row.completion_tokens,
            total_tokens=row.prompt_tokens + row.completion_tokens,
        )
        for row in rows
    ]
