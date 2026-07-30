from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from nanoid import generate
from app.core.security import hash_password, verify_password
from app.models.api_key import ApiKey, ApiKeyStatus
from app.models.user import User


def generate_api_key(phone: str) -> str:
    return f"sk-{phone}-{generate(size=16)}"


def mask_key(full_key: str) -> str:
    parts = full_key.split("-")
    if len(parts) == 3:
        phone = parts[1]
        suffix = parts[2]
        masked_phone = phone[:3] + "****" + phone[-4:]
        short_suffix = suffix[:4] + "..."
        return f"sk-{masked_phone}-{short_suffix}"
    return full_key


async def get_api_keys(db: AsyncSession, user: User) -> list[ApiKey]:
    result = await db.execute(
        select(ApiKey).where(ApiKey.user_id == user.id).order_by(ApiKey.created_at.desc())
    )
    return list(result.scalars().all())


async def create_api_key(db: AsyncSession, user: User) -> tuple[ApiKey, str]:
    full_key = generate_api_key(user.phone)
    key_prefix = mask_key(full_key)
    key_hash = hash_password(full_key)
    api_key = ApiKey(user_id=user.id, key_prefix=key_prefix, key_hash=key_hash)
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)
    return api_key, full_key


async def revoke_api_key(db: AsyncSession, key_id: str, user: User) -> bool:
    result = await db.execute(
        select(ApiKey).where(ApiKey.id == key_id, ApiKey.user_id == user.id)
    )
    key = result.scalar_one_or_none()
    if not key:
        return False
    key.status = ApiKeyStatus.revoked
    await db.commit()
    return True


async def verify_api_key(db: AsyncSession, api_key_string: str) -> User | None:
    result = await db.execute(select(ApiKey).where(ApiKey.status == ApiKeyStatus.active))
    all_keys = result.scalars().all()
    for key in all_keys:
        if verify_password(api_key_string, key.key_hash):
            result = await db.execute(select(User).where(User.id == key.user_id))
            return result.scalar_one_or_none()
    return None
