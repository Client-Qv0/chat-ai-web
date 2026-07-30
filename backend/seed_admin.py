import asyncio
import bcrypt
from app.db.session import async_session
from app.models.user import User, UserRole


async def seed_admin():
    async with async_session() as db:
        from sqlalchemy import select
        existing = await db.execute(select(User).where(User.phone == "19977883322"))
        if existing.scalar_one_or_none():
            print("Admin user already exists, skipping.")
            return

        pwd_hash = bcrypt.hashpw(b"2026", bcrypt.gensalt()).decode()
        user = User(
            username="li",
            phone="19977883322",
            password_hash=pwd_hash,
            role=UserRole.admin,
        )
        db.add(user)
        await db.commit()
        print(f"Admin created: username=li, phone=19977883322, role=admin")


if __name__ == "__main__":
    asyncio.run(seed_admin())
