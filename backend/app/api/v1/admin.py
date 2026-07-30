from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.v1.dependencies import get_current_user, require_admin
from app.models.user import User, UserRole
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.admin import (
    AdminStats, AdminUserResponse, UpdateUserRoleRequest,
    AdminConversationResponse,
)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats", response_model=AdminStats)
async def get_stats(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    user_count = (await db.execute(select(func.count(User.id)))).scalar() or 0
    conv_count = (await db.execute(select(func.count(Conversation.id)))).scalar() or 0
    msg_count = (await db.execute(select(func.count(Message.id)))).scalar() or 0
    token_result = await db.execute(select(func.coalesce(func.sum(Message.tokens_used), 0)))
    total_tokens = token_result.scalar() or 0

    return AdminStats(
        total_users=user_count,
        total_conversations=conv_count,
        total_messages=msg_count,
        total_tokens=total_tokens,
    )


@router.get("/users", response_model=list[AdminUserResponse])
async def list_users(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return list(result.scalars().all())


@router.put("/users/{user_id}/role", response_model=AdminUserResponse)
async def update_user_role(
    user_id: str,
    data: UpdateUserRoleRequest,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    if data.role not in ("user", "admin"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.role = UserRole(data.role)
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/conversations", response_model=list[AdminConversationResponse])
async def list_conversations(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Conversation, User.username, User.phone)
        .join(User, Conversation.user_id == User.id)
        .order_by(Conversation.created_at.desc())
    )
    rows = result.all()
    return [
        AdminConversationResponse(
            id=str(row[0].id),
            route_id=row[0].route_id,
            title=row[0].title,
            username=row[1],
            phone=row[2],
            created_at=row[0].created_at,
        )
        for row in rows
    ]


@router.get("/conversations/{conv_id}/messages")
async def get_conversation_messages(
    conv_id: str,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    conv_result = await db.execute(select(Conversation).where(Conversation.id == conv_id))
    conv = conv_result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conv.id)
        .order_by(Message.created_at)
    )
    messages = result.scalars().all()
    return [
        {
            "id": str(m.id),
            "role": m.role.value,
            "content": m.content,
            "tokens_used": m.tokens_used,
            "created_at": m.created_at.isoformat(),
        }
        for m in messages
    ]
