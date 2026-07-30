from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from nanoid import generate
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.models.user import User


def generate_route_id(phone: str) -> str:
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"
    return f"{phone}-{generate(size=12, alphabet=alphabet)}"


async def get_conversations(db: AsyncSession, user: User) -> list[Conversation]:
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user.id)
        .order_by(desc(Conversation.created_at))
    )
    return list(result.scalars().all())


async def create_conversation(db: AsyncSession, user: User) -> Conversation:
    route_id = generate_route_id(user.phone)
    conv = Conversation(user_id=user.id, route_id=route_id)
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    return conv


async def get_conversation_by_route_id(db: AsyncSession, route_id: str, user: User) -> Conversation | None:
    result = await db.execute(
        select(Conversation).where(
            Conversation.route_id == route_id,
            Conversation.user_id == user.id,
        )
    )
    return result.scalar_one_or_none()


async def get_messages(db: AsyncSession, conversation: Conversation) -> list[Message]:
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at)
    )
    return list(result.scalars().all())


async def create_message(
    db: AsyncSession,
    conversation: Conversation,
    role: MessageRole,
    content: str,
    metadata: dict | None = None,
    tokens_used: int = 0,
) -> Message:
    msg = Message(
        conversation_id=conversation.id,
        role=role,
        content=content,
        metadata_=metadata or {},
        tokens_used=tokens_used,
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg
