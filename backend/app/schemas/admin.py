from pydantic import BaseModel
from datetime import datetime


class AdminStats(BaseModel):
    total_users: int
    total_conversations: int
    total_messages: int
    total_tokens: int


class AdminUserResponse(BaseModel):
    id: str
    username: str
    phone: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class UpdateUserRoleRequest(BaseModel):
    role: str


class AdminConversationResponse(BaseModel):
    id: str
    route_id: str
    title: str
    username: str
    phone: str
    created_at: datetime

    class Config:
        from_attributes = True
