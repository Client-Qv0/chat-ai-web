from sqlalchemy import Column, String, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin
import enum


class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    username = Column(String(50), nullable=False)
    phone = Column(String(11), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole), default=UserRole.user, nullable=False)
    avatar_url = Column(String(255), default="")

    conversations = relationship("Conversation", back_populates="user")
    api_keys = relationship("ApiKey", back_populates="user")
