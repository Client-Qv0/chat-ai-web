from pydantic import BaseModel
from datetime import datetime


class ApiKeyResponse(BaseModel):
    id: str
    key_prefix: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ApiKeyGenerated(ApiKeyResponse):
    full_key: str
