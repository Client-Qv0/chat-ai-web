from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.v1.dependencies import get_current_user
from app.models.user import User
from app.schemas.api_key import ApiKeyResponse, ApiKeyGenerated
from app.services.api_key_service import get_api_keys, create_api_key, revoke_api_key

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


@router.get("/", response_model=list[ApiKeyResponse])
async def list_keys(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_api_keys(db, current_user)


@router.post("/generate", response_model=ApiKeyGenerated, status_code=status.HTTP_201_CREATED)
async def generate_key(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    key_obj, full_key = await create_api_key(db, current_user)
    return ApiKeyGenerated(
        id=str(key_obj.id),
        key_prefix=key_obj.key_prefix,
        status=key_obj.status.value,
        created_at=key_obj.created_at,
        full_key=full_key,
    )


@router.delete("/{key_id}")
async def delete_key(key_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    ok = await revoke_api_key(db, key_id, current_user)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Key not found")
    return {"message": "Key revoked"}
