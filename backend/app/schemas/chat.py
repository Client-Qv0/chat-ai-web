from pydantic import BaseModel, Field
from datetime import datetime


class ConversationCreate(BaseModel):
    pass


class ConversationResponse(BaseModel):
    id: str
    route_id: str
    title: str
    created_at: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    metadata_: dict = Field(alias="metadata")
    tokens_used: int
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


class ChatMessageRequest(BaseModel):
    content: str
    metadata: dict = Field(default_factory=dict)
