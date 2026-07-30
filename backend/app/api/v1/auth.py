from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.auth import (
    RegisterRequest, LoginRequest, LoginResponse, TokenResponse,
    UserInfo, UpdateProfileRequest, ChangePasswordRequest,
)
from app.services.auth_service import create_user, authenticate_user, change_user_password, get_user_by_phone
from app.core.security import create_access_token
from app.api.v1.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await get_user_by_phone(db, data.phone)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Phone already registered")
    user = await create_user(db, data)
    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token)


@router.post("/login", response_model=LoginResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, data.phone, data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.id)})
    return LoginResponse(
        access_token=token,
        user_info=UserInfo(
            id=str(user.id), username=user.username, phone=user.phone,
            role=user.role.value, avatar_url=user.avatar_url,
            created_at=user.created_at.isoformat(),
        ),
    )


@router.get("/me", response_model=UserInfo)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserInfo(
        id=str(current_user.id), username=current_user.username,
        phone=current_user.phone, role=current_user.role.value,
        avatar_url=current_user.avatar_url,
        created_at=current_user.created_at.isoformat(),
    )


@router.put("/me/profile", response_model=UserInfo)
async def update_profile(
    data: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if data.username is not None:
        current_user.username = data.username
    await db.commit()
    await db.refresh(current_user)
    return UserInfo(
        id=str(current_user.id), username=current_user.username,
        phone=current_user.phone, role=current_user.role.value,
        avatar_url=current_user.avatar_url,
        created_at=current_user.created_at.isoformat(),
    )


@router.put("/me/password")
async def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    success = await change_user_password(db, current_user, data.old_password, data.new_password)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Old password is incorrect")
    return {"message": "Password changed successfully"}
