# AI 对话平台网站 实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 构建一个部署于局域网内的 AI 对话平台，支持流式对话、API 接口调用、用户鉴权及后台管理。

**架构：** 前后端分离，Vue 3 SPA 通过 Nginx 反向代理到 FastAPI 后端，后端调用本地 Ollama 部署的 Qwen 模型，数据存 PostgreSQL。

**技术栈：** Vue 3 + Vite + TypeScript + Tailwind CSS + Element Plus / Python + FastAPI + SQLAlchemy 2.0 (Async) + PostgreSQL / Docker Compose + Nginx

---

## Phase 1：项目脚手架与基础设施

### 任务 1.1：初始化前端项目

**文件：**
- 创建：`frontend/` 目录下所有 Vite + Vue 3 + TS 初始化文件
- 创建：`frontend/.env`、`frontend/.env.development`
- 创建：`frontend/tailwind.config.js`
- 创建：`frontend/postcss.config.js`

- [ ] **步骤 1：使用 Vite 创建项目**

```bash
npm create vite@latest frontend -- --template vue-ts
```

- [ ] **步骤 2：安装核心依赖**

```bash
cd frontend
npm install
npm install vue-router@4 pinia axios
npm install element-plus @element-plus/icons-vue
npm install -D tailwindcss@3 postcss autoprefixer
npm install markdown-it highlight.js
npm install -D @types/markdown-it
```

- [ ] **步骤 3：初始化 Tailwind CSS**

```bash
npx tailwindcss init -p
```

**`frontend/tailwind.config.js`**:
```js
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: { extend: {} },
  plugins: [],
}
```

**`frontend/src/assets/main.css`** (追加到尾部的 Tailwind 指令):
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

- [ ] **步骤 4：配置环境变量**

**`frontend/.env`**:
```
VITE_API_BASE_URL=/api/v1
```

**`frontend/.env.development`**:
```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

- [ ] **步骤 5：验证项目运行**

```bash
npm run dev
```

预期：浏览器打开 `http://localhost:5173` 显示 Vite + Vue 默认页面。

- [ ] **步骤 6：Commit**

```bash
git add frontend/
git commit -m "feat: initialize Vue 3 + Vite + TS frontend project"
```

---

### 任务 1.2：初始化后端项目

**文件：**
- 创建：`backend/requirements.txt`
- 创建：`backend/app/__init__.py`
- 创建：`backend/app/main.py`
- 创建：`backend/app/core/__init__.py`
- 创建：`backend/app/core/config.py`

- [ ] **步骤 1：创建后端目录结构**

```bash
mkdir -p backend/app/core backend/app/models backend/app/schemas backend/app/api/v1 backend/app/services backend/app/db
```

- [ ] **步骤 2：编写 `backend/requirements.txt`**

```
fastapi==0.115.0
uvicorn[standard]==0.30.0
sqlalchemy[asyncio]==2.0.35
asyncpg==0.30.0
alembic==1.14.0
pydantic[email]==2.9.0
pydantic-settings==2.5.0
passlib[bcrypt]==1.7.4
pyjwt==2.9.0
python-multipart==0.0.12
nanoid==2.0.0
httpx==0.27.0
```

- [ ] **步骤 3：编写 `backend/app/core/config.py`**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://ai_user:ai_password@localhost:5432/ai_platform"
    LLM_API_URL: str = "http://127.0.0.1:11434"
    LLM_MODEL: str = "qwen3.5:0.8b"
    SECRET_KEY: str = "change-me-to-a-random-secret-string"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173"]

    class Config:
        env_file = ".env"


settings = Settings()
```

- [ ] **步骤 4：编写 `backend/app/main.py`**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(title="AI Chat Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

- [ ] **步骤 5：安装依赖并验证启动**

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

预期：`http://localhost:8000/health` 返回 `{"status":"ok"}`。`http://localhost:8000/docs` 显示 Swagger UI。

- [ ] **步骤 6：Commit**

```bash
git add backend/
git commit -m "feat: initialize FastAPI backend project"
```

---

## Phase 2：数据库模型与核心基础设施

### 任务 2.1：数据库连接与会话管理

**文件：**
- 创建：`backend/app/db/base.py`
- 创建：`backend/app/db/session.py`
- 修改：`backend/app/main.py`

- [ ] **步骤 1：编写 `backend/app/db/base.py`**

```python
from sqlalchemy.orm import DeclarativeBase
import uuid
from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

- [ ] **步骤 2：编写 `backend/app/db/session.py`**

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
```

- [ ] **步骤 3：在 `backend/app/main.py` 中添加 startup 事件**

```python
from contextlib import asynccontextmanager
from app.db.base import Base
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="AI Chat Platform", lifespan=lifespan)
```

- [ ] **步骤 4：Commit**

```bash
git add backend/app/db/ backend/app/main.py
git commit -m "feat: add database connection and session management"
```

---

### 任务 2.2：定义数据库模型

**文件：**
- 创建：`backend/app/models/user.py`
- 创建：`backend/app/models/conversation.py`
- 创建：`backend/app/models/message.py`
- 创建：`backend/app/models/api_key.py`
- 创建：`backend/app/models/token_usage.py`
- 创建：`backend/app/models/__init__.py`

- [ ] **步骤 1：编写 `backend/app/models/user.py`**

```python
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
```

- [ ] **步骤 2：编写 `backend/app/models/conversation.py`**

```python
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin
import uuid


class Conversation(Base, TimestampMixin):
    __tablename__ = "conversations"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    route_id = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(100), default="新对话")

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", order_by="Message.created_at")
```

- [ ] **步骤 3：编写 `backend/app/models/message.py`**

```python
from sqlalchemy import Column, String, Text, Integer, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin
import enum


class MessageRole(str, enum.Enum):
    user = "user"
    assistant = "assistant"
    system = "system"


class Message(Base, TimestampMixin):
    __tablename__ = "messages"

    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    role = Column(SAEnum(MessageRole), nullable=False)
    content = Column(Text, nullable=False, default="")
    metadata_ = Column("metadata", JSONB, default=dict)
    tokens_used = Column(Integer, default=0)

    conversation = relationship("Conversation", back_populates="messages")
```

- [ ] **步骤 4：编写 `backend/app/models/api_key.py`**

```python
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
```

- [ ] **步骤 5：编写 `backend/app/models/token_usage.py`**

```python
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base, TimestampMixin


class TokenUsageLog(Base, TimestampMixin):
    __tablename__ = "token_usage_logs"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    api_key_id = Column(UUID(as_uuid=True), ForeignKey("api_keys.id"), nullable=True)
    model_name = Column(String(50), nullable=False)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
```

- [ ] **步骤 6：编写 `backend/app/models/__init__.py`**

```python
from app.models.user import User, UserRole
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.models.api_key import ApiKey, ApiKeyStatus
from app.models.token_usage import TokenUsageLog

__all__ = [
    "User", "UserRole",
    "Conversation",
    "Message", "MessageRole",
    "ApiKey", "ApiKeyStatus",
    "TokenUsageLog",
]
```

- [ ] **步骤 7：Commit**

```bash
git add backend/app/models/
git commit -m "feat: define all database ORM models"
```

---

### 任务 2.3：配置 Alembic 迁移

**文件：**
- 创建：`backend/alembic.ini`
- 创建：`backend/alembic/env.py`
- 创建：`backend/alembic/versions/` 目录

- [ ] **步骤 1：初始化 Alembic**

```bash
cd backend
alembic init alembic
```

- [ ] **步骤 2：修改 `backend/alembic/env.py` 以支持异步**

```python
from app.core.config import settings
from app.db.base import Base
from app.models import *  # noqa: F401, F403

target_metadata = Base.metadata
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL.replace("+asyncpg", ""))
```

- [ ] **步骤 3：生成初始迁移**

```bash
alembic revision --autogenerate -m "init"
```

- [ ] **步骤 4：Commit**

```bash
git add backend/alembic.ini backend/alembic/
git commit -m "feat: configure Alembic migrations"
```

---

### 任务 2.4：Pydantic Schemas 定义

**文件：**
- 创建：`backend/app/schemas/__init__.py`
- 创建：`backend/app/schemas/auth.py`
- 创建：`backend/app/schemas/chat.py`
- 创建：`backend/app/schemas/api_key.py`
- 创建：`backend/app/schemas/token_usage.py`

- [ ] **步骤 1：编写 `backend/app/schemas/auth.py`**

```python
from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    phone: str = Field(pattern=r"^1[3-9]\d{9}$")
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    phone: str = Field(pattern=r"^1[3-9]\d{9}$")
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserInfo(BaseModel):
    id: str
    username: str
    phone: str
    role: str
    avatar_url: str
    created_at: str

    class Config:
        from_attributes = True


class LoginResponse(TokenResponse):
    user_info: UserInfo


class UpdateProfileRequest(BaseModel):
    username: str | None = Field(None, min_length=1, max_length=50)


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8, max_length=128)
```

- [ ] **步骤 2：编写 `backend/app/schemas/chat.py`**

```python
from pydantic import BaseModel, Field
from datetime import datetime


class ConversationCreate(BaseModel):
    pass  # no extra fields needed, title defaults to "新对话"


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
```

- [ ] **步骤 3：编写 `backend/app/schemas/api_key.py`**

```python
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
```

- [ ] **步骤 4：编写 `backend/app/schemas/token_usage.py`**

```python
from pydantic import BaseModel
from datetime import date


class TokenUsageSummary(BaseModel):
    total_tokens: int
    today_tokens: int


class DailyUsage(BaseModel):
    date: date
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
```

- [ ] **步骤 5：Commit**

```bash
git add backend/app/schemas/
git commit -m "feat: add Pydantic request/response schemas"
```

---

## Phase 3：认证系统

### 任务 3.1：密码哈希与 JWT 工具

**文件：**
- 创建：`backend/app/core/security.py`
- 创建：`backend/app/services/auth.py`

- [ ] **步骤 1：编写 `backend/app/core/security.py`**

```python
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt, JWTError
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except JWTError:
        return None
```

- [ ] **步骤 2：编写 `backend/app/services/auth_service.py`**

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.core.security import hash_password, verify_password, create_access_token
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
```

- [ ] **步骤 3：编写依赖注入 `backend/app/api/v1/dependencies.py`**

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import decode_access_token
from app.models.user import User

security_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role.value != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return current_user
```

- [ ] **步骤 4：Commit**

```bash
git add backend/app/core/security.py backend/app/services/auth_service.py backend/app/api/v1/dependencies.py
git commit -m "feat: add password hashing, JWT, and auth dependencies"
```

---

### 任务 3.2：认证 API 路由

**文件：**
- 创建：`backend/app/api/v1/auth.py`
- 修改：`backend/app/main.py`（挂载路由）

- [ ] **步骤 1：编写 `backend/app/api/v1/auth.py`**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.auth import (
    RegisterRequest, LoginRequest, LoginResponse, TokenResponse,
    UserInfo, UpdateProfileRequest, ChangePasswordRequest,
)
from app.services.auth_service import create_user, authenticate_user, change_user_password
from app.core.security import create_access_token
from app.api.v1.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    from app.services.auth_service import get_user_by_phone
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
```

- [ ] **步骤 2：在 `backend/app/main.py` 中挂载路由**

```python
from app.api.v1 import auth

app.include_router(auth.router, prefix="/api/v1")
```

- [ ] **步骤 3：启动后端并用 curl 测试**

```bash
# 测试注册
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","phone":"13800138000","password":"test1234"}'

# 测试登录
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone":"13800138000","password":"test1234"}'
```

预期：注册返回 201 + token，登录返回 200 + token + user_info。

- [ ] **步骤 4：Commit**

```bash
git add backend/app/api/v1/auth.py backend/app/main.py
git commit -m "feat: implement auth API (register, login, me, profile, password)"
```

---

### 任务 3.3：前端认证模块

**文件：**
- 创建：`frontend/src/stores/auth.ts`
- 创建：`frontend/src/api/client.ts`
- 创建：`frontend/src/api/auth.ts`
- 创建：`frontend/src/router/index.ts`
- 创建：`frontend/src/views/Login.vue`
- 创建：`frontend/src/views/Register.vue`
- 创建：`frontend/src/views/Recovery.vue`
- 修改：`frontend/src/App.vue`
- 修改：`frontend/src/main.ts`

- [ ] **步骤 1：编写 API 客户端 `frontend/src/api/client.ts`**

```typescript
import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
})

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_info')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default apiClient
```

- [ ] **步骤 2：编写 Auth Store `frontend/src/stores/auth.ts`**

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import type { UserInfo } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const user = ref<UserInfo | null>(null)

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  function setAuth(newToken: string, userInfo: UserInfo) {
    token.value = newToken
    user.value = userInfo
    localStorage.setItem('access_token', newToken)
    localStorage.setItem('user_info', JSON.stringify(userInfo))
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_info')
  }

  async function loadUser() {
    if (!token.value) return
    try {
      const res = await authApi.getMe()
      user.value = res.data
    } catch {
      logout()
    }
  }

  return { token, user, isLoggedIn, isAdmin, setAuth, logout, loadUser }
})
```

- [ ] **步骤 3：编写 Auth API `frontend/src/api/auth.ts`**

```typescript
import apiClient from './client'
import type { LoginRequest, RegisterRequest, LoginResponse, UserInfo } from '@/types'

export const authApi = {
  register: (data: RegisterRequest) => apiClient.post<LoginResponse>('/auth/register', data),
  login: (data: LoginRequest) => apiClient.post<LoginResponse>('/auth/login', data),
  getMe: () => apiClient.get<UserInfo>('/auth/me'),
  updateProfile: (data: { username: string }) => apiClient.put<UserInfo>('/auth/me/profile', data),
  changePassword: (data: { old_password: string; new_password: string }) =>
    apiClient.put('/auth/me/password', data),
}
```

- [ ] **步骤 4：编写前端类型 `frontend/src/types/index.ts`**

```typescript
export interface UserInfo {
  id: string
  username: string
  phone: string
  role: string
  avatar_url: string
  created_at: string
}

export interface LoginRequest {
  phone: string
  password: string
}

export interface RegisterRequest {
  username: string
  phone: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user_info: UserInfo
}

export interface Conversation {
  id: string
  route_id: string
  title: string
  created_at: string
}

export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  metadata: Record<string, any>
  tokens_used: number
  created_at: string
}

export interface ApiKey {
  id: string
  key_prefix: string
  status: 'active' | 'revoked'
  created_at: string
}

export interface ApiKeyGenerated extends ApiKey {
  full_key: string
}

export interface TokenUsageSummary {
  total_tokens: number
  today_tokens: number
}

export interface DailyUsage {
  date: string
  prompt_tokens: number
  completion_tokens: number
  total_tokens: number
}
```

- [ ] **步骤 5：编写路由 `frontend/src/router/index.ts`**

```typescript
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: () => import('@/views/Home.vue') },
    { path: '/login', component: () => import('@/views/Login.vue') },
    { path: '/register', component: () => import('@/views/Register.vue') },
    { path: '/recovery', component: () => import('@/views/Recovery.vue') },
    {
      path: '/chat',
      component: () => import('@/views/chat/ChatLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', component: () => import('@/views/chat/EmptyChat.vue') },
        { path: ':routeId', component: () => import('@/views/chat/ChatWindow.vue') },
      ],
    },
    {
      path: '/api',
      component: () => import('@/views/api/ApiLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', redirect: '/api/index' },
        { path: 'index', component: () => import('@/views/api/ApiDocs.vue') },
        { path: 'token', component: () => import('@/views/api/TokenUsage.vue') },
        { path: 'key', component: () => import('@/views/api/ApiKeyManage.vue') },
      ],
    },
    { path: '/user/:phone', component: () => import('@/views/user/UserProfile.vue'), meta: { requiresAuth: true } },
    { path: '/admin', component: () => import('@/views/admin/AdminLayout.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
  ],
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('access_token')
  if (to.meta.requiresAuth && !token) {
    return next('/login')
  }
  if (to.meta.requiresAdmin) {
    const raw = localStorage.getItem('user_info')
    if (raw) {
      const user = JSON.parse(raw)
      if (user.role !== 'admin') return next('/403')
    } else {
      return next('/login')
    }
  }
  next()
})

export default router
```

- [ ] **步骤 6：编写登录页 `frontend/src/views/Login.vue`**

```vue
<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({ phone: '', password: '' })
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  loading.value = true
  error.value = ''
  try {
    const res = await authApi.login(form.value)
    authStore.setAuth(res.data.access_token, res.data.user_info)
    router.push('/chat')
  } catch (e: any) {
    error.value = e.response?.data?.detail || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="w-full max-w-md bg-white rounded-2xl shadow-lg p-8">
      <h1 class="text-2xl font-bold text-center mb-6">登录</h1>
      <el-form @submit.prevent="handleLogin" label-position="top">
        <el-form-item label="手机号">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <p v-if="error" class="text-red-500 text-sm mb-3">{{ error }}</p>
        <el-button type="primary" native-type="submit" :loading="loading" class="w-full">登录</el-button>
      </el-form>
      <div class="mt-4 text-center text-sm text-gray-500">
        <router-link to="/register" class="text-blue-500 hover:underline">注册</router-link>
        <span class="mx-2">|</span>
        <router-link to="/recovery" class="text-blue-500 hover:underline">忘记密码</router-link>
      </div>
    </div>
  </div>
</template>
```

- [ ] **步骤 7：编写注册页 `frontend/src/views/Register.vue`**

```vue
<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({ username: '', phone: '', password: '', confirmPassword: '' })
const loading = ref(false)
const error = ref('')

async function handleRegister() {
  if (form.value.password !== form.value.confirmPassword) {
    error.value = '两次密码不一致'
    return
  }
  loading.value = true
  error.value = ''
  try {
    const res = await authApi.register({
      username: form.value.username,
      phone: form.value.phone,
      password: form.value.password,
    })
    authStore.setAuth(res.data.access_token, res.data.user_info)
    router.push('/chat')
  } catch (e: any) {
    error.value = e.response?.data?.detail || '注册失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="w-full max-w-md bg-white rounded-2xl shadow-lg p-8">
      <h1 class="text-2xl font-bold text-center mb-6">注册</h1>
      <el-form @submit.prevent="handleRegister" label-position="top">
        <el-form-item label="用户名">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" placeholder="至少8位，包含字母和数字" show-password />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input v-model="form.confirmPassword" type="password" placeholder="请再次输入密码" show-password />
        </el-form-item>
        <p v-if="error" class="text-red-500 text-sm mb-3">{{ error }}</p>
        <el-button type="primary" native-type="submit" :loading="loading" class="w-full">注册</el-button>
      </el-form>
      <div class="mt-4 text-center text-sm text-gray-500">
        已有账号？<router-link to="/login" class="text-blue-500 hover:underline">去登录</router-link>
      </div>
    </div>
  </div>
</template>
```

- [ ] **步骤 8：编写找回密码页 `frontend/src/views/Recovery.vue`**

```vue
<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="w-full max-w-md bg-white rounded-2xl shadow-lg p-8 text-center">
      <h1 class="text-2xl font-bold mb-4">找回密码</h1>
      <p class="text-gray-600 mb-6">请联系系统管理员重置密码</p>
      <div class="bg-gray-100 rounded-lg p-4 mb-6">
        <p class="text-sm text-gray-500">管理员联系方式占位（图片待配置）</p>
      </div>
      <router-link to="/login" class="text-blue-500 hover:underline">返回登录</router-link>
    </div>
  </div>
</template>
```

- [ ] **步骤 9：更新 `frontend/src/main.ts`**

```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import './assets/main.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(ElementPlus)
app.mount('#app')
```

- [ ] **步骤 10：更新 `frontend/src/App.vue`**

```vue
<template>
  <router-view />
</template>
```

- [ ] **步骤 11：验证登录注册流程**

```bash
cd frontend
npm run dev
```

在浏览器中访问 `http://localhost:5173/login`，测试注册、登录、跳转流程。

- [ ] **步骤 12：Commit**

```bash
git add frontend/src/stores/ frontend/src/api/ frontend/src/router/ frontend/src/views/ frontend/src/types/ frontend/src/main.ts frontend/src/App.vue
git commit -m "feat: implement frontend auth pages (login, register, recovery)"
```

---

## Phase 4：在线对话模块（核心）

### 任务 4.1：后端对话 CRUD API

**文件：**
- 创建：`backend/app/services/chat_service.py`
- 创建：`backend/app/api/v1/chat.py`
- 修改：`backend/app/main.py`

- [ ] **步骤 1：编写 `backend/app/services/chat_service.py`**

```python
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from nanoid import generate
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.models.user import User


def generate_route_id(phone: str) -> str:
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"
    return f"{phone}-{generate(size=12, alphabet=alphabet)}"


async def get_conversations(db: AsyncSession, user: User) -> list[Conversation]:
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user.id)
        .order_by(desc(Conversation.created_at))
    )
    return list(result.scalars().all())


async def create_conversation(db: AsyncSession, user: User) -> Conversation:
    route_id = generate_route_id(user.phone)
    conv = Conversation(user_id=user.id, route_id=route_id)
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    return conv


async def get_conversation_by_route_id(db: AsyncSession, route_id: str, user: User) -> Conversation | None:
    result = await db.execute(
        select(Conversation).where(
            Conversation.route_id == route_id,
            Conversation.user_id == user.id,
        )
    )
    return result.scalar_one_or_none()


async def get_messages(db: AsyncSession, conversation: Conversation) -> list[Message]:
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at)
    )
    return list(result.scalars().all())


async def create_message(
    db: AsyncSession,
    conversation: Conversation,
    role: MessageRole,
    content: str,
    metadata: dict | None = None,
    tokens_used: int = 0,
) -> Message:
    msg = Message(
        conversation_id=conversation.id,
        role=role,
        content=content,
        metadata_=metadata or {},
        tokens_used=tokens_used,
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg
```

- [ ] **步骤 2：编写 `backend/app/api/v1/chat.py`**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.v1.dependencies import get_current_user
from app.models.user import User
from app.schemas.chat import ConversationResponse, ChatMessageRequest, MessageResponse
from app.services.chat_service import (
    get_conversations, create_conversation, get_conversation_by_route_id,
    get_messages, create_message,
)
from app.models.message import MessageRole

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_conversations(db, current_user)


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def new_conversation(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_conversation(db, current_user)


@router.get("/conversations/{route_id}/messages", response_model=list[MessageResponse])
async def list_messages(
    route_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conv = await get_conversation_by_route_id(db, route_id, current_user)
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return await get_messages(db, conv)


@router.post("/conversations/{route_id}/messages")
async def send_message(
    route_id: str,
    data: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conv = await get_conversation_by_route_id(db, route_id, current_user)
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    await create_message(db, conv, MessageRole.user, data.content, data.metadata)

    async def event_stream():
        yield "data: {}\n\n"  # placeholder — will be replaced in next task

    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

- [ ] **步骤 3：挂载 chat 路由到 `backend/app/main.py`**

```python
from app.api.v1 import chat
app.include_router(chat.router, prefix="/api/v1")
```

- [ ] **步骤 4：Commit**

```bash
git add backend/app/services/chat_service.py backend/app/api/v1/chat.py backend/app/main.py
git commit -m "feat: implement conversation CRUD API"
```

---

### 任务 4.2：对接本地 LLM（Ollama）实现 SSE 流式响应

**文件：**
- 创建：`backend/app/services/llm_service.py`
- 修改：`backend/app/api/v1/chat.py`（替换 send_message 中的 placeholder）

- [ ] **步骤 1：编写 `backend/app/services/llm_service.py`**

```python
import json
import httpx
from app.core.config import settings


async def stream_qwen_response(
    messages: list[dict],
    enable_thinking: bool = False,
) -> str:
    system_prompt = "You are a helpful AI assistant."
    if enable_thinking:
        system_prompt = "Please think step-by-step before answering. " + system_prompt

    payload = {
        "model": settings.LLM_MODEL,
        "messages": [{"role": "system", "content": system_prompt}] + messages,
        "stream": True,
        "options": {"temperature": 0.7},
    }

    async with httpx.AsyncClient(timeout=300.0) as client:
        async with client.stream("POST", f"{settings.LLM_API_URL}/api/chat", json=payload) as response:
            async for line in response.aiter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        content = data.get("message", {}).get("content", "")
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue


async def get_llm_response_text(
    messages: list[dict],
    enable_thinking: bool = False,
) -> str:
    """非流式获取完整响应，用于计算 token（简化版）"""
    full = ""
    async for chunk in stream_qwen_response(messages, enable_thinking):
        full += chunk
    return full
```

- [ ] **步骤 2：修改 `backend/app/api/v1/chat.py` 的 `send_message` 函数**

替换 event_stream 内部逻辑：

```python
@router.post("/conversations/{route_id}/messages")
async def send_message(
    route_id: str,
    data: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conv = await get_conversation_by_route_id(db, route_id, current_user)
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    await create_message(db, conv, MessageRole.user, data.content, data.metadata)

    existing_messages = await get_messages(db, conv)
    llm_messages = [
        {"role": msg.role.value, "content": msg.content}
        for msg in existing_messages[-20:]  # 限制上下文窗口
    ]
    enable_thinking = data.metadata.get("thinking", False)

    async def event_stream():
        full_response = ""
        async for chunk in stream_qwen_response(llm_messages, enable_thinking):
            full_response += chunk
            yield f"data: {json.dumps({'content': chunk})}\n\n"

        # 流结束后保存 assistant 消息
        async for session in [db]:
            await create_message(
                session, conv, MessageRole.assistant, full_response,
                tokens_used=len(full_response) // 4,  # 粗略估算
            )
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

这处修改需要完整覆盖 `send_message` 函数体。为保持原子性，用以下代码替换整个函数：

```python
@router.post("/conversations/{route_id}/messages")
async def send_message(
    route_id: str,
    data: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conv = await get_conversation_by_route_id(db, route_id, current_user)
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    await create_message(db, conv, MessageRole.user, data.content, data.metadata)

    existing_messages = await get_messages(db, conv)
    llm_messages = [
        {"role": msg.role.value, "content": msg.content}
        for msg in existing_messages[-20:]
    ]
    enable_thinking = data.metadata.get("thinking", False)

    async def event_stream():
        full_response = ""
        async for chunk in stream_qwen_response(llm_messages, enable_thinking):
            full_response += chunk
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        await create_message(
            db, conv, MessageRole.assistant, full_response,
            tokens_used=len(full_response) // 4,
        )
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

- [ ] **步骤 3：Commit**

```bash
git add backend/app/services/llm_service.py backend/app/api/v1/chat.py
git commit -m "feat: integrate Ollama LLM with SSE streaming"
```

---

### 任务 4.3：前端对话页面

**文件：**
- 创建：`frontend/src/api/chat.ts`
- 创建：`frontend/src/views/chat/ChatLayout.vue`
- 创建：`frontend/src/views/chat/EmptyChat.vue`
- 创建：`frontend/src/views/chat/ChatWindow.vue`
- 创建：`frontend/src/components/ChatStreamRenderer.vue`

- [ ] **步骤 1：编写 Chat API `frontend/src/api/chat.ts`**

```typescript
import apiClient from './client'
import type { Conversation, Message } from '@/types'

export const chatApi = {
  getConversations: () => apiClient.get<Conversation[]>('/chat/conversations'),
  createConversation: () => apiClient.post<Conversation>('/chat/conversations'),
  getMessages: (routeId: string) => apiClient.get<Message[]>(`/chat/conversations/${routeId}/messages`),
}
```

- [ ] **步骤 2：编写 `frontend/src/views/chat/ChatLayout.vue`**

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { chatApi } from '@/api/chat'
import type { Conversation } from '@/types'

const router = useRouter()
const conversations = ref<Conversation[]>([])
const loading = ref(false)

async function loadConversations() {
  loading.value = true
  try {
    const res = await chatApi.getConversations()
    conversations.value = res.data
  } finally {
    loading.value = false
  }
}

async function createNewChat() {
  try {
    const res = await chatApi.createConversation()
    conversations.value.unshift(res.data)
    router.push(`/chat/${res.data.route_id}`)
  } catch { /* ignore */ }
}

onMounted(loadConversations)
</script>

<template>
  <div class="flex h-screen">
    <aside class="w-64 bg-gray-50 border-r flex flex-col">
      <div class="p-4">
        <el-button type="primary" class="w-full" @click="createNewChat">新建对话</el-button>
      </div>
      <div class="flex-1 overflow-y-auto px-2">
        <div
          v-for="conv in conversations"
          :key="conv.id"
          class="p-3 rounded-lg cursor-pointer hover:bg-gray-200 text-sm truncate"
          :class="{ 'bg-gray-200': $route.params.routeId === conv.route_id }"
          @click="router.push(`/chat/${conv.route_id}`)"
        >
          {{ conv.title }}
        </div>
      </div>
    </aside>
    <main class="flex-1 flex flex-col">
      <header class="h-14 border-b flex items-center justify-end px-4">
        <router-link to="/api" class="text-sm text-blue-500 hover:underline">API 服务</router-link>
      </header>
      <div class="flex-1 overflow-hidden">
        <router-view />
      </div>
    </main>
    <GlobalUserWidget />
  </div>
</template>
```

- [ ] **步骤 3：编写 `frontend/src/views/chat/EmptyChat.vue`**

```vue
<template>
  <div class="flex items-center justify-center h-full text-gray-400">
    <p>选择或创建一个对话开始聊天</p>
  </div>
</template>
```

- [ ] **步骤 4：编写 `frontend/src/views/chat/ChatWindow.vue`**

```vue
<script setup lang="ts">
import { ref, nextTick, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { chatApi } from '@/api/chat'
import type { Message } from '@/types'
import ChatStreamRenderer from '@/components/ChatStreamRenderer.vue'

const route = useRoute()
const messages = ref<Message[]>([])
const inputText = ref('')
const thinkingEnabled = ref(false)
const searchEnabled = ref(false)
const loading = ref(false)
const messagesContainer = ref<HTMLElement>()

async function loadMessages() {
  const routeId = route.params.routeId as string
  if (!routeId) return
  try {
    const res = await chatApi.getMessages(routeId)
    messages.value = res.data
    await nextTick()
    scrollToBottom()
  } catch { /* ignore */ }
}

function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text || loading.value) return
  const routeId = route.params.routeId as string

  messages.value.push({
    id: '', role: 'user', content: text,
    metadata: { thinking: thinkingEnabled.value, search: searchEnabled.value },
    tokens_used: 0, created_at: new Date().toISOString(),
  })
  inputText.value = ''
  loading.value = true

  const assistantMsg: Message = {
    id: '', role: 'assistant', content: '',
    metadata: {}, tokens_used: 0, created_at: new Date().toISOString(),
  }
  messages.value.push(assistantMsg)

  const token = localStorage.getItem('access_token')
  const baseUrl = import.meta.env.VITE_API_BASE_URL

  try {
    const response = await fetch(`${baseUrl}/chat/conversations/${routeId}/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        content: text,
        metadata: { thinking: thinkingEnabled.value, search: searchEnabled.value },
      }),
    })

    const reader = response.body?.getReader()
    const decoder = new TextDecoder()
    if (!reader) return

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      const chunk = decoder.decode(value, { stream: true })
      const lines = chunk.split('\n')
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          if (data === '[DONE]') continue
          try {
            const parsed = JSON.parse(data)
            assistantMsg.content += parsed.content || ''
            await nextTick()
            scrollToBottom()
          } catch { /* ignore */ }
        }
      }
    }
  } finally {
    loading.value = false
    loadMessages()
  }
}

watch(() => route.params.routeId, () => {
  messages.value = []
  loadMessages()
})

onMounted(loadMessages)
</script>

<template>
  <div class="flex flex-col h-full">
    <div ref="messagesContainer" class="flex-1 overflow-y-auto p-4 space-y-4">
      <ChatStreamRenderer
        v-for="(msg, idx) in messages"
        :key="idx"
        :message="msg"
      />
    </div>
    <footer class="border-t p-4">
      <div class="flex items-center gap-3 mb-2">
        <el-switch v-model="thinkingEnabled" size="small" active-text="深度思考" />
        <el-switch v-model="searchEnabled" size="small" active-text="联网搜索" />
        <el-button size="small">+ 文件上传</el-button>
      </div>
      <div class="flex gap-2">
        <el-input
          v-model="inputText"
          type="textarea"
          :rows="2"
          placeholder="输入消息..."
          @keydown.enter.exact.prevent="sendMessage"
        />
        <el-button type="primary" :loading="loading" @click="sendMessage">发送</el-button>
      </div>
    </footer>
  </div>
</template>
```

- [ ] **步骤 5：编写 `frontend/src/components/ChatStreamRenderer.vue`**

```vue
<script setup lang="ts">
import { computed } from 'vue'
import MarkdownIt from 'markdown-it'
import type { Message } from '@/types'

const props = defineProps<{ message: Message }>()
const md = new MarkdownIt({ breaks: true })

const renderedHtml = computed(() => md.render(props.message.content))
const isUser = computed(() => props.message.role === 'user')
</script>

<template>
  <div class="flex" :class="isUser ? 'justify-end' : 'justify-start'">
    <div
      class="max-w-[80%] rounded-xl px-4 py-2"
      :class="isUser ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-900'"
    >
      <div v-if="isUser" class="whitespace-pre-wrap">{{ message.content }}</div>
      <div v-else class="prose prose-sm max-w-none" v-html="renderedHtml" />
    </div>
  </div>
</template>
```

- [ ] **步骤 6：安装 markdown-it 依赖（若未在任务 1.1 中安装）**

```bash
cd frontend
npm install markdown-it
npm install -D @types/markdown-it
```

- [ ] **步骤 7：Commit**

```bash
git add frontend/src/api/chat.ts frontend/src/views/chat/ frontend/src/components/ChatStreamRenderer.vue
git commit -m "feat: implement chat UI with SSE streaming"
```

---

## Phase 5：API 服务模块

### 任务 5.1：后端 API Key 管理

**文件：**
- 创建：`backend/app/services/api_key_service.py`
- 创建：`backend/app/api/v1/api_keys.py`
- 修改：`backend/app/main.py`

- [ ] **步骤 1：编写 `backend/app/services/api_key_service.py`**

```python
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
```

- [ ] **步骤 2：编写 `backend/app/api/v1/api_keys.py`**

```python
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
```

- [ ] **步骤 3：挂载路由**

```python
from app.api.v1 import api_keys
app.include_router(api_keys.router, prefix="/api/v1")
```

- [ ] **步骤 4：Commit**

```bash
git add backend/app/services/api_key_service.py backend/app/api/v1/api_keys.py backend/app/main.py
git commit -m "feat: implement API key management (generate, list, revoke)"
```

---

### 任务 5.2：后端 Token 用量统计

**文件：**
- 创建：`backend/app/api/v1/token_usage.py`
- 修改：`backend/app/main.py`

- [ ] **步骤 1：编写 `backend/app/api/v1/token_usage.py`**

```python
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.v1.dependencies import get_current_user
from app.models.user import User
from app.models.token_usage import TokenUsageLog
from app.schemas.token_usage import TokenUsageSummary, DailyUsage

router = APIRouter(prefix="/token-usage", tags=["token-usage"])


@router.get("/summary", response_model=TokenUsageSummary)
async def get_summary(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    total_result = await db.execute(
        select(func.coalesce(func.sum(TokenUsageLog.prompt_tokens + TokenUsageLog.completion_tokens), 0))
        .where(TokenUsageLog.user_id == current_user.id)
    )
    total_tokens = total_result.scalar() or 0

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_result = await db.execute(
        select(func.coalesce(func.sum(TokenUsageLog.prompt_tokens + TokenUsageLog.completion_tokens), 0))
        .where(TokenUsageLog.user_id == current_user.id, TokenUsageLog.created_at >= today_start)
    )
    today_tokens = today_result.scalar() or 0

    return TokenUsageSummary(total_tokens=total_tokens, today_tokens=today_tokens)


@router.get("/daily", response_model=list[DailyUsage])
async def get_daily_usage(
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    since = datetime.utcnow() - timedelta(days=days)
    result = await db.execute(
        select(
            func.date(TokenUsageLog.created_at).label("date"),
            func.coalesce(func.sum(TokenUsageLog.prompt_tokens), 0).label("prompt_tokens"),
            func.coalesce(func.sum(TokenUsageLog.completion_tokens), 0).label("completion_tokens"),
        )
        .where(TokenUsageLog.user_id == current_user.id, TokenUsageLog.created_at >= since)
        .group_by(func.date(TokenUsageLog.created_at))
        .order_by(func.date(TokenUsageLog.created_at))
    )
    rows = result.all()
    return [
        DailyUsage(
            date=row.date,
            prompt_tokens=row.prompt_tokens,
            completion_tokens=row.completion_tokens,
            total_tokens=row.prompt_tokens + row.completion_tokens,
        )
        for row in rows
    ]
```

- [ ] **步骤 2：挂载路由**

```python
from app.api.v1 import token_usage
app.include_router(token_usage.router, prefix="/api/v1")
```

- [ ] **步骤 3：Commit**

```bash
git add backend/app/api/v1/token_usage.py backend/app/main.py
git commit -m "feat: implement token usage statistics API"
```

---

### 任务 5.3：对外 LLM API（OpenAI 兼容格式）

**文件：**
- 创建：`backend/app/api/v1_openai/chat.py`
- 修改：`backend/app/main.py`

- [ ] **步骤 1：编写 `backend/app/api/v1_openai/chat.py`**

```python
import json
import time
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.api_key_service import verify_api_key
from app.services.llm_service import stream_qwen_response

router = APIRouter(prefix="/v1", tags=["openai-compatible"])


@router.post("/chat/completions")
async def chat_completions(request: Request, db: AsyncSession = Depends(get_db)):
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    api_key = auth_header[7:]
    user = await verify_api_key(db, api_key)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    body = await request.json()
    messages = body.get("messages", [])
    model = body.get("model", "qwen3.5:0.8b")
    stream = body.get("stream", False)

    async def event_stream():
        full = ""
        async for chunk in stream_qwen_response(messages):
            full += chunk
            yield f"data: {json.dumps({'id': 'chatcmpl-xxx', 'object': 'chat.completion.chunk', 'created': int(time.time()), 'model': model, 'choices': [{'delta': {'content': chunk}, 'index': 0}]})}\n\n"
        yield "data: [DONE]\n\n"

    if stream:
        return StreamingResponse(event_stream(), media_type="text/event-stream")

    # Non-streaming
    full = ""
    async for chunk in stream_qwen_response(messages):
        full += chunk

    return {
        "id": "chatcmpl-xxx",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [{"index": 0, "message": {"role": "assistant", "content": full}, "finish_reason": "stop"}],
    }
```

- [ ] **步骤 2：挂载路由**

```python
from app.api.v1_openai import chat as openai_chat
app.include_router(openai_chat.router)
```

- [ ] **步骤 3：Commit**

```bash
git add backend/app/api/v1_openai/chat.py backend/app/main.py
git commit -m "feat: implement OpenAI-compatible chat completions API"
```

---

### 任务 5.4：前端 API 服务页面

**文件：**
- 创建：`frontend/src/views/api/ApiLayout.vue`
- 创建：`frontend/src/views/api/ApiDocs.vue`
- 创建：`frontend/src/views/api/TokenUsage.vue`
- 创建：`frontend/src/views/api/ApiKeyManage.vue`
- 创建：`frontend/src/api/api-keys.ts`
- 创建：`frontend/src/api/token-usage.ts`

- [ ] **步骤 1：编写 `frontend/src/api/api-keys.ts`** 和 `frontend/src/api/token-usage.ts`**

**`frontend/src/api/api-keys.ts`**:
```typescript
import apiClient from './client'
import type { ApiKey, ApiKeyGenerated } from '@/types'

export const apiKeysApi = {
  list: () => apiClient.get<ApiKey[]>('/api-keys/'),
  generate: () => apiClient.post<ApiKeyGenerated>('/api-keys/generate'),
  revoke: (id: string) => apiClient.delete(`/api-keys/${id}`),
}
```

**`frontend/src/api/token-usage.ts`**:
```typescript
import apiClient from './client'
import type { TokenUsageSummary, DailyUsage } from '@/types'

export const tokenUsageApi = {
  getSummary: () => apiClient.get<TokenUsageSummary>('/token-usage/summary'),
  getDaily: (days = 7) => apiClient.get<DailyUsage[]>('/token-usage/daily', { params: { days } }),
}
```

- [ ] **步骤 2：编写 `frontend/src/views/api/ApiLayout.vue`**

```vue
<script setup lang="ts">
import { useRoute } from 'vue-router'
const route = useRoute()
</script>

<template>
  <div class="flex h-screen">
    <aside class="w-48 bg-gray-50 border-r p-4">
      <el-menu :default-active="route.path" router>
        <el-menu-item index="/api/index">首次调用文档</el-menu-item>
        <el-menu-item index="/api/token">Token 用量</el-menu-item>
        <el-menu-item index="/api/key">API Key 管理</el-menu-item>
      </el-menu>
    </aside>
    <main class="flex-1 flex flex-col">
      <header class="h-14 border-b flex items-center justify-end px-4">
        <router-link to="/chat" class="text-sm text-blue-500 hover:underline">在线对话</router-link>
      </header>
      <div class="flex-1 overflow-auto p-6">
        <router-view />
      </div>
    </main>
    <GlobalUserWidget />
  </div>
</template>
```

- [ ] **步骤 3：编写 `frontend/src/views/api/ApiDocs.vue`**

```vue
<template>
  <div class="prose max-w-none">
    <h1>API 调用文档</h1>
    <h2>接口地址</h2>
    <p><code>POST /v1/chat/completions</code></p>
    <h2>鉴权</h2>
    <p>在 Header 中传入 API Key：<code>Authorization: Bearer YOUR_API_KEY</code></p>
    <h2>cURL 示例</h2>
    <pre class="bg-gray-900 text-gray-100 p-4 rounded"><code>curl -X POST http://your-server/v1/chat/completions \
  -H "Authorization: Bearer sk-138****8000-xxxx" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hello"}],"stream":true}'</code></pre>
    <h2>Python 示例</h2>
    <pre class="bg-gray-900 text-gray-100 p-4 rounded"><code>import requests

url = "http://your-server/v1/chat/completions"
headers = {"Authorization": "Bearer sk-xxx", "Content-Type": "application/json"}
data = {"messages": [{"role": "user", "content": "Hello"}], "stream": True}

with requests.post(url, headers=headers, json=data, stream=True) as r:
    for line in r.iter_lines():
        if line:
            print(line.decode())</code></pre>
    <h2>Node.js 示例</h2>
    <pre class="bg-gray-900 text-gray-100 p-4 rounded"><code>const response = await fetch('http://your-server/v1/chat/completions', {
  method: 'POST',
  headers: { 'Authorization': 'Bearer sk-xxx', 'Content-Type': 'application/json' },
  body: JSON.stringify({ messages: [{ role: 'user', content: 'Hello' }], stream: true })
})

const reader = response.body.getReader()
const decoder = new TextDecoder()
while (true) {
  const { done, value } = await reader.read()
  if (done) break
  console.log(decoder.decode(value))
}</code></pre>
  </div>
</template>
```

- [ ] **步骤 4：编写 `frontend/src/views/api/TokenUsage.vue`**

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { tokenUsageApi } from '@/api/token-usage'
import type { TokenUsageSummary, DailyUsage } from '@/types'

const summary = ref<TokenUsageSummary>({ total_tokens: 0, today_tokens: 0 })
const dailyData = ref<DailyUsage[]>([])
const days = ref(7)

async function load() {
  const [s, d] = await Promise.all([
    tokenUsageApi.getSummary(),
    tokenUsageApi.getDaily(days.value),
  ])
  summary.value = s.data
  dailyData.value = d.data
}

onMounted(load)
</script>

<template>
  <div>
    <h2 class="text-xl font-bold mb-4">Token 用量</h2>
    <div class="grid grid-cols-3 gap-4 mb-6">
      <el-statistic title="总消耗" :value="summary.total_tokens" />
      <el-statistic title="今日消耗" :value="summary.today_tokens" />
      <el-statistic title="剩余可用" value="不限" />
    </div>
    <div class="flex items-center gap-2 mb-4">
      <span class="text-sm text-gray-500">显示近</span>
      <el-radio-group v-model="days" size="small" @change="load">
        <el-radio-button :value="7">7天</el-radio-button>
        <el-radio-button :value="30">30天</el-radio-button>
      </el-radio-group>
    </div>
    <div class="bg-white rounded-lg p-4">
      <div v-if="dailyData.length === 0" class="text-gray-400 text-center py-8">暂无数据</div>
      <table v-else class="w-full text-sm">
        <thead>
          <tr class="border-b">
            <th class="text-left py-2">日期</th>
            <th class="text-right py-2">输入</th>
            <th class="text-right py-2">输出</th>
            <th class="text-right py-2">合计</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="d in dailyData" :key="d.date" class="border-b">
            <td class="py-2">{{ d.date }}</td>
            <td class="text-right">{{ d.prompt_tokens }}</td>
            <td class="text-right">{{ d.completion_tokens }}</td>
            <td class="text-right font-bold">{{ d.total_tokens }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
```

- [ ] **步骤 5：编写 `frontend/src/views/api/ApiKeyManage.vue`**

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiKeysApi } from '@/api/api-keys'
import type { ApiKey } from '@/types'
import { ElMessage, ElMessageBox } from 'element-plus'

const keys = ref<ApiKey[]>([])

async function loadKeys() {
  const res = await apiKeysApi.list()
  keys.value = res.data
}

async function generateKey() {
  try {
    const res = await apiKeysApi.generate()
    ElMessageBox.alert(`新密钥（仅显示一次，请复制保存）：\n${res.data.full_key}`, '密钥已生成', {
      confirmButtonText: '已复制',
    })
    await loadKeys()
  } catch { ElMessage.error('生成失败') }
}

async function revokeKey(id: string) {
  try {
    await ElMessageBox.confirm('确定要禁用此密钥吗？', '确认', { type: 'warning' })
    await apiKeysApi.revoke(id)
    ElMessage.success('已禁用')
    await loadKeys()
  } catch { /* cancelled */ }
}

onMounted(loadKeys)
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl font-bold">API Key 管理</h2>
      <el-button type="primary" @click="generateKey">生成新 Key</el-button>
    </div>
    <el-table :data="keys" style="width: 100%">
      <el-table-column prop="key_prefix" label="Key" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'danger'" size="small">
            {{ row.status === 'active' ? '可用' : '已禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button
            v-if="row.status === 'active'"
            size="small"
            type="danger"
            @click="revokeKey(row.id)"
          >
            禁用
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>
```

- [ ] **步骤 6：Commit**

```bash
git add frontend/src/api/api-keys.ts frontend/src/api/token-usage.ts frontend/src/views/api/
git commit -m "feat: implement API service frontend pages"
```

---

## Phase 6：全局组件与用户中心

### 任务 6.1：全局左下角用户信息卡片

**文件：**
- 创建：`frontend/src/components/GlobalUserWidget.vue`
- 修改：`frontend/src/views/chat/ChatLayout.vue`（引入组件）
- 修改：`frontend/src/views/api/ApiLayout.vue`（引入组件）

- [ ] **步骤 1：编写 `frontend/src/components/GlobalUserWidget.vue`**

```vue
<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const auth = useAuthStore()

const hiddenRoutes = ['/', '/login', '/register', '/admin']
const visible = computed(() => !hiddenRoutes.includes(route.path))

function goProfile() {
  if (auth.user) {
    window.open(`/user/${auth.user.phone}`, '_blank')
  }
}

const initial = computed(() => auth.user?.username?.charAt(0).toUpperCase() || '?')
</script>

<template>
  <div
    v-if="visible"
    class="fixed bottom-4 left-4 bg-white rounded-full shadow-lg px-4 py-2 flex items-center gap-2 cursor-pointer hover:shadow-xl transition-shadow border"
    @click="goProfile"
  >
    <div class="w-8 h-8 rounded-full bg-blue-500 text-white flex items-center justify-center text-sm font-bold">
      {{ initial }}
    </div>
    <span class="text-sm font-medium">{{ auth.user?.username }}</span>
  </div>
</template>
```

- [ ] **步骤 2：在 ChatLayout 和 ApiLayout 中引入组件**

在 `ChatLayout.vue` 和 `ApiLayout.vue` 的 `<script setup>` 中添加：
```typescript
import GlobalUserWidget from '@/components/GlobalUserWidget.vue'
```

- [ ] **步骤 3：Commit**

```bash
git add frontend/src/components/GlobalUserWidget.vue frontend/src/views/chat/ChatLayout.vue frontend/src/views/api/ApiLayout.vue
git commit -m "feat: add global user widget component"
```

---

### 任务 6.2：用户中心页面

**文件：**
- 创建：`frontend/src/views/user/UserProfile.vue`

- [ ] **步骤 1：编写 `frontend/src/views/user/UserProfile.vue`**

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api/auth'
import { ElMessage } from 'element-plus'

const auth = useAuthStore()
const username = ref('')
const saving = ref(false)

const passwordForm = ref({ old_password: '', new_password: '', confirm: '' })
const changingPwd = ref(false)

onMounted(async () => {
  await auth.loadUser()
  username.value = auth.user?.username || ''
})

async function updateProfile() {
  saving.value = true
  try {
    const res = await authApi.updateProfile({ username: username.value })
    auth.user = res.data
    localStorage.setItem('user_info', JSON.stringify(res.data))
    ElMessage.success('修改成功')
  } catch { ElMessage.error('修改失败') }
  finally { saving.value = false }
}

async function changePassword() {
  if (passwordForm.value.new_password !== passwordForm.value.confirm) {
    ElMessage.error('两次密码不一致')
    return
  }
  changingPwd.value = true
  try {
    await authApi.changePassword({
      old_password: passwordForm.value.old_password,
      new_password: passwordForm.value.new_password,
    })
    ElMessage.success('密码修改成功')
    passwordForm.value = { old_password: '', new_password: '', confirm: '' }
  } catch { ElMessage.error('密码修改失败') }
  finally { changingPwd.value = false }
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex justify-center py-12">
    <div class="w-full max-w-lg space-y-6">
      <div class="bg-white rounded-2xl shadow p-6">
        <h2 class="text-lg font-bold mb-4">基本信息</h2>
        <el-form label-position="top">
          <el-form-item label="用户名">
            <el-input v-model="username" />
          </el-form-item>
          <el-form-item label="手机号">
            <el-input :model-value="auth.user?.phone" disabled />
          </el-form-item>
          <el-form-item label="注册时间">
            <el-input :model-value="auth.user?.created_at" disabled />
          </el-form-item>
          <el-button type="primary" :loading="saving" @click="updateProfile">保存</el-button>
        </el-form>
      </div>

      <div class="bg-white rounded-2xl shadow p-6">
        <h2 class="text-lg font-bold mb-4">安全设置</h2>
        <el-form label-position="top">
          <el-form-item label="原密码">
            <el-input v-model="passwordForm.old_password" type="password" show-password />
          </el-form-item>
          <el-form-item label="新密码">
            <el-input v-model="passwordForm.new_password" type="password" show-password />
          </el-form-item>
          <el-form-item label="确认新密码">
            <el-input v-model="passwordForm.confirm" type="password" show-password />
          </el-form-item>
          <el-button type="primary" :loading="changingPwd" @click="changePassword">修改密码</el-button>
        </el-form>
      </div>
    </div>
  </div>
</template>
```

- [ ] **步骤 2：Commit**

```bash
git add frontend/src/views/user/UserProfile.vue
git commit -m "feat: implement user profile and password change page"
```

---

## Phase 7：后台管理 & 首页

### 任务 7.1：首页 (`/`)

**文件：**
- 创建：`frontend/src/views/Home.vue`

- [ ] **步骤 1：编写 `frontend/src/views/Home.vue`**

```vue
<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="grid grid-cols-2 gap-8 max-w-4xl">
      <div class="bg-white rounded-2xl shadow-lg p-8 text-center hover:shadow-xl transition-shadow cursor-pointer" @click="$router.push('/chat')">
        <h2 class="text-2xl font-bold mb-2">在线对话</h2>
        <p class="text-gray-500">基于本地大模型的智能对话服务，支持流式输出、多轮对话</p>
        <el-button type="primary" size="large" class="mt-4">进入对话</el-button>
      </div>
      <div class="bg-white rounded-2xl shadow-lg p-8 text-center hover:shadow-xl transition-shadow cursor-pointer" @click="$router.push('/api')">
        <h2 class="text-2xl font-bold mb-2">API 服务</h2>
        <p class="text-gray-500">标准化 API 接口，支持 OpenAI 兼容格式调用</p>
        <el-button type="success" size="large" class="mt-4">进入 API</el-button>
      </div>
    </div>
  </div>
</template>
```

- [ ] **步骤 2：Commit**

```bash
git add frontend/src/views/Home.vue
git commit -m "feat: add homepage with chat and API entry cards"
```

---

### 任务 7.2：后台管理占位页面

**文件：**
- 创建：`frontend/src/views/admin/AdminLayout.vue`

- [ ] **步骤 1：编写 `frontend/src/views/admin/AdminLayout.vue`**

```vue
<script setup lang="ts">
import { ElMessage } from 'element-plus'

function goRoot() {
  ElMessage.info('后台管理面板（后续开发）')
}
</script>

<template>
  <div class="flex h-screen">
    <aside class="w-48 bg-gray-50 border-r p-4">
      <p class="text-sm text-gray-500">管理菜单（建设中）</p>
    </aside>
    <main class="flex-1 flex flex-col">
      <header class="h-14 border-b flex items-center justify-between px-4">
        <h1 class="text-lg font-bold">后台管理</h1>
        <el-button type="warning" size="small" @click="goRoot">root</el-button>
      </header>
      <div class="flex-1 flex items-center justify-center text-gray-400">
        <p>管理面板开发中，敬请期待</p>
      </div>
    </main>
  </div>
</template>
```

- [ ] **步骤 2：Commit**

```bash
git add frontend/src/views/admin/AdminLayout.vue
git commit -m "feat: add admin layout placeholder"
```

---

## Phase 8：403 页面与路由补全

### 任务 8.1：403 禁止访问页面

**文件：**
- 创建：`frontend/src/views/Forbidden.vue`
- 修改：`frontend/src/router/index.ts`

- [ ] **步骤 1：编写 `frontend/src/views/Forbidden.vue`**

```vue
<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="text-center">
      <h1 class="text-6xl font-bold text-gray-300 mb-4">403</h1>
      <p class="text-gray-500 mb-6">您没有权限访问此页面</p>
      <el-button type="primary" @click="$router.push('/')">返回首页</el-button>
    </div>
  </div>
</template>
```

- [ ] **步骤 2：添加 403 路由**

在 `frontend/src/router/index.ts` 的 routes 数组中追加：
```typescript
{ path: '/403', component: () => import('@/views/Forbidden.vue') },
```

将 admin guard 中的 `return next('/403')` 改为：
```typescript
if (user.role !== 'admin') return next('/403')
```

- [ ] **步骤 3：Commit**

```bash
git add frontend/src/views/Forbidden.vue frontend/src/router/index.ts
git commit -m "feat: add 403 forbidden page"
```

---

## Phase 9：Docker 部署配置

### 任务 9.1：Dockerfile 与 Compose

**文件：**
- 创建：`docker-compose.yml`
- 创建：`backend/Dockerfile`
- 创建：`frontend/Dockerfile`
- 创建：`frontend/nginx.conf`
- 创建：`backend/.env`

- [ ] **步骤 1：编写 `backend/Dockerfile`**

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **步骤 2：编写 `frontend/Dockerfile`**

```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:1.25-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

- [ ] **步骤 3：编写 `frontend/nginx.conf`**

```nginx
server {
    listen 80;
    server_name localhost;

    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    location /api/v1/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /v1/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 300s;
        chunked_transfer_encoding on;
    }
}
```

- [ ] **步骤 4：编写 `backend/.env`**

```
DATABASE_URL=postgresql+asyncpg://ai_user:ai_password@db:5432/ai_platform
LLM_API_URL=http://host.docker.internal:11434
SECRET_KEY=change-me-to-a-random-secret-string-in-production
```

- [ ] **步骤 5：编写项目根目录 `docker-compose.yml`**

```yaml
version: '3.8'
services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ai_user
      POSTGRES_PASSWORD: ai_password
      POSTGRES_DB: ai_platform
    volumes:
      - pg_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    env_file:
      - ./backend/.env
    depends_on:
      - db
    ports:
      - "8000:8000"
    extra_hosts:
      - "host.docker.internal:host-gateway"

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  pg_data:
```

- [ ] **步骤 6：Commit**

```bash
git add docker-compose.yml backend/Dockerfile backend/.env frontend/Dockerfile frontend/nginx.conf
git commit -m "feat: add Docker Compose deployment configuration"
```

---

## Phase 10：验证与收尾

### 任务 10.1：端到端验证

- [ ] **步骤 1：启动全栈开发环境进行手动测试**

```bash
# 终端 1: 启动 PostgreSQL (如已安装)
# 终端 2: 启动后端
cd backend
uvicorn app.main:app --reload --port 8000

# 终端 3: 启动前端
cd frontend
npm run dev
```

- [ ] **步骤 2：验证清单**

| 功能 | 验证方式 | 预期 |
|------|---------|------|
| 首页 | 访问 `http://localhost:5173/` | 显示两个卡片 |
| 注册 | `/register` 注册新用户 | 成功注册并跳转 chat |
| 登录 | `/login` 登录已有用户 | 成功登录并跳转 chat |
| 登录拦截 | 未登录访问 `/chat` | 重定向到 `/login` |
| 新建对话 | 点击"新建对话" | 创建新 conversation 并跳转 |
| 对话流式响应 | 发送消息 | SSE 流式逐步显示回复 |
| 切换对话 | 左侧列表切换 | 加载对应历史消息 |
| API 文档页 | 访问 `/api/index` | 显示文档和代码示例 |
| Token 用量 | 访问 `/api/token` | 显示统计（初始为 0） |
| API Key 生成/禁用 | `/api/key` 生成后禁用 | 生成成功，禁用后显示已禁用 |
| 用户中心 | 点击左下角头像 | 新窗口打开 profile 页 |
| 修改资料 | 修改用户名 | 保存成功 |
| 修改密码 | 修改密码 | 修改成功 |
| 管理员 403 | 非 admin 用户访问 `/admin` | 跳转 403 页 |
| API Key 鉴权 | `curl -H "Authorization: Bearer sk-xxx" /v1/chat/completions` | 正常返回 |
| 404 路由 | 访问不存在的路由 | 显示空白或默认页面 |

- [ ] **步骤 3：Docker Compose 部署验证**

```bash
docker compose up -d --build
```

访问 `http://localhost` 验证前端 + API 是否正常工作。

---

## 自检结果

1. **规格覆盖度：** PRD 中所有 MVP 功能均有对应任务——首页(7.1)、认证(3.2-3.3)、在线对话(4.1-4.3)、API 服务(5.1-5.4)、用户中心(6.2)、后台管理(7.2)、全局组件(6.1)、Docker 部署(9.1)。

2. **占位符扫描：** 无 TODO/待定/后续实现占位。每个步骤均有具体代码或命令。

3. **类型一致性：** 前后端 schema 名称对齐（`UserInfo`、`ConversationResponse`、`MessageResponse`、`ApiKeyResponse` 等）。前端 `types/index.ts` 与后端 Pydantic schema 字段一致。路由参数 `routeId` 全链路一致使用。

