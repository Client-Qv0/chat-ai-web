from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.core.security import hash_password, verify_password
from app.schemas.auth import RegisterRequest


async def create_user(db: AsyncSession, data: RegisterRequest) -> User:
    user = User(
        username=data.username,
        phone=data.phone,
        password_hash=hash_password(data.password),
        role=UserRole.user,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_by_phone(db: AsyncSession, phone: str) -> User | None:
    result = await db.execute(select(User).where(User.phone == phone))
    return result.scalar_one_or_none()


async def authenticate_user(db: AsyncSession, phone: str, password: str) -> User | None:
    user = await get_user_by_phone(db, phone)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


async def change_user_password(db: AsyncSession, user: User, old_password: str, new_password: str) -> bool:
    if not verify_password(old_password, user.password_hash):
        return False
    user.password_hash = hash_password(new_password)
    await db.commit()
    return True
