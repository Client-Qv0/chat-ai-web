from sqlalchemy import Column, String, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin
import enum


class ApiKeyStatus(str, enum.Enum):
    active = "active"
    revoked = "revoked"


class ApiKey(Base, TimestampMixin):
    __tablename__ = "api_keys"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    key_prefix = Column(String(20), nullable=False)
    key_hash = Column(String(255), nullable=False)
    status = Column(SAEnum(ApiKeyStatus), default=ApiKeyStatus.active, nullable=False)

    user = relationship("User", back_populates="api_keys")
