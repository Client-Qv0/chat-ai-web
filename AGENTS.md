# AGENTS.md — AI Chat Platform

## 项目概述

局域网内部署的 AI 对话平台，支持流式对话、API 接口调用、用户鉴权及后台管理。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + TypeScript + Tailwind CSS + Element Plus |
| 后端 | Python + FastAPI + SQLAlchemy 2.0 (Async) |
| 数据库 | PostgreSQL 15+ |
| 部署 | Docker Compose + Nginx |
| 模型 | Qwen3.5-0.8b (Ollama) |
| 依赖 | markdown-it, highlight.js, pinia, vue-router, axios, python-jose, passlib, nanoid, httpx |

## 项目结构

```
chat–ai–web/
├── frontend/                     # Vue 3 SPA
│   ├── nginx.conf                # Nginx 配置（生产）
│   ├── Dockerfile                # 前端容器
│   ├── .env / .env.development   # 环境变量（VITE_API_BASE_URL）
│   └── src/
│       ├── api/                  # Axios 请求封装
│       │   ├── client.ts         #   实例 + 拦截器（JWT 自动附加、401 跳转）
│       │   ├── auth.ts           #   认证接口
│       │   ├── chat.ts           #   对话接口
│       │   ├── api-keys.ts       #   API Key 管理
│       │   └── token-usage.ts    #   Token 用量统计
│       ├── components/           # 公共组件
│       │   ├── GlobalUserWidget.vue  # 左下角用户悬浮卡片
│       │   └── ChatStreamRenderer.vue # 对话 Markdown 渲染
│       ├── router/index.ts       # 路由表 + 守卫（auth / admin）
│       ├── stores/auth.ts        # Pinia 认证状态
│       ├── types/index.ts        # TypeScript 类型定义
│       └── views/                # 页面组件
│           ├── Home.vue          #   首页（/）
│           ├── Login.vue         #   登录（/login）
│           ├── Register.vue      #   注册（/register）
│           ├── Recovery.vue      #   找回密码（/recovery）
│           ├── Forbidden.vue     #   403（/403）
│           ├── chat/             #   对话模块（/chat）
│           │   ├── ChatLayout.vue
│           │   ├── EmptyChat.vue
│           │   └── ChatWindow.vue
│           ├── api/              #   API 服务模块（/api）
│           │   ├── ApiLayout.vue
│           │   ├── ApiDocs.vue
│           │   ├── TokenUsage.vue
│           │   └── ApiKeyManage.vue
│           ├── user/             #   用户中心（/user/:phone）
│           │   └── UserProfile.vue
│           └── admin/            #   后台管理（/admin）
│               └── AdminLayout.vue
├── backend/                      # FastAPI 后端
│   ├── .env                      # Docker 环境变量
│   ├── Dockerfile                # 后端容器
│   ├── requirements.txt          # Python 依赖
│   ├── alembic.ini               # Alembic 配置
│   ├── alembic/                  # 数据库迁移
│   └── app/
│       ├── main.py               # FastAPI 入口（lifespan、CORS、路由挂载）
│       ├── core/
│       │   ├── config.py         # Pydantic Settings（环境变量）
│       │   └── security.py       # 密码哈希 + JWT 签发/验证
│       ├── db/
│       │   ├── base.py           # ORM 基类 + TimestampMixin
│       │   └── session.py        # 异步数据库会话
│       ├── models/               # SQLAlchemy ORM 模型
│       │   ├── user.py           #   User（用户表）
│       │   ├── conversation.py   #   Conversation（对话表）
│       │   ├── message.py        #   Message（消息表）
│       │   ├── api_key.py        #   ApiKey（API 密钥表）
│       │   └── token_usage.py    #   TokenUsageLog（Token 消耗日志）
│       ├── schemas/              # Pydantic 请求/响应模型
│       │   ├── auth.py           #   认证相关
│       │   ├── chat.py           #   对话相关
│       │   ├── api_key.py        #   API Key 相关
│       │   └── token_usage.py    #   Token 统计相关
│       ├── services/             # 业务逻辑
│       │   ├── auth_service.py   #   用户注册/登录/密码修改
│       │   ├── chat_service.py   #   对话/消息 CRUD + route_id 生成
│       │   ├── llm_service.py    #   Ollama 流式调用
│       │   └── api_key_service.py # API Key 生成/撤销/校验
│       └── api/
│           ├── v1/               # 内部 API（JWT 鉴权）
│           │   ├── auth.py       #   /auth/register, /login, /me, /me/profile, /me/password
│           │   ├── chat.py       #   /chat/conversations, /.../{route_id}/messages
│           │   ├── api_keys.py   #   /api-keys/
│           │   ├── token_usage.py #  /token-usage/summary, /daily
│           │   └── dependencies.py # get_current_user, require_admin
│           └── v1_openai/        # 对外 LLM API（API Key 鉴权）
│               └── chat.py       #   /v1/chat/completions
├── docker-compose.yml            # Docker 编排（db + backend + frontend）
├── PRD.md                        # 产品需求文档
├── SPEC.md                       # 技术规格说明
└── docs/                         # 其他文档
```

## 常用命令

### 前端

```bash
cd frontend
npm install          # 安装依赖
npm run dev          # 开发服务器 (localhost:5173)
npm run build        # 生产构建（vue-tsc + vite）
```

### 后端

```bash
cd backend
pip install -r requirements.txt                           # 安装依赖
uvicorn app.main:app --reload --port 8000                 # 开发服务器
alembic revision --autogenerate -m "description"          # 生成迁移
alembic upgrade head                                      # 执行迁移
```

### Docker

```bash
docker compose up -d --build   # 启动所有服务
docker compose down            # 停止
```

### 数据库（PostgreSQL 本地开发）

创建数据库后，启动后端时按以下顺序：
1. 确保 PostgreSQL 运行中
2. `cd backend && uvicorn app.main:app --reload --port 8000`
3. 首次启动自动通过 `lifespan` 事件创建表（`Base.metadata.create_all`）

如需迁移管理：
```bash
cd backend
alembic revision --autogenerate -m "init"
alembic upgrade head
```

## 开发环境

- 后端 API 基地址（开发）：`http://localhost:8000`（前端通过 `.env.development` 指向）
- 前端开发服务器：`http://localhost:5173`
- PostgreSQL：`localhost:5432`（数据库 `ai_platform`，用户 `ai_user`，密码 `ai_password`）
- Ollama：`http://127.0.0.1:11434`
- 前端路径别名：`@/` → `src/`（配置在 `tsconfig.app.json` 和 `vite.config.ts`）

## 环境变量

### 后端 (`backend/app/core/config.py`)

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DATABASE_URL` | `postgresql+asyncpg://...@localhost:5432/ai_platform` | 数据库连接 |
| `LLM_API_URL` | `http://127.0.0.1:11434` | Ollama 地址 |
| `LLM_MODEL` | `qwen3.5:0.8b` | 模型名称 |
| `SECRET_KEY` | `change-me-...` | JWT 签名密钥（生产环境必须修改） |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `10080` | JWT 过期时间（7天） |
| `ALLOWED_ORIGINS` | `["http://localhost:5173"]` | CORS 白名单 |

### 前端 (.env / .env.development)

| 变量 | 开发值 | 生产值 |
|------|--------|--------|
| `VITE_API_BASE_URL` | `http://localhost:8000/api/v1` | `/api/v1` |

## Python 环境

- 版本：3.13.12
- 绝对路径：`C:\Users\ASUS\AppData\Local\Programs\Python\Python313\python.exe`
- Shell 中不使用 `python` 关键字，使用绝对路径或 `py` 命令

## API 约定

- 内部接口前缀：`/api/v1/`，JWT 鉴权（`Authorization: Bearer <token>`）
- 对外 LLM API：`/v1/chat/completions`，API Key 鉴权（`Authorization: Bearer <sk-...>`）
- SSE 流式接口（`/chat/conversations/{route_id}/messages` 和 `/v1/chat/completions?stream=true`）
- Nginx 配置中 SSE 接口已关闭缓冲（`proxy_buffering off; proxy_cache off;`）
- API Key 格式：`sk-{phone}-{nanoid(16)}`，数据库存 Bcrypt 哈希
- 对话路由 ID 格式：`{phone}-{nanoid(12)}`

## Git 仓库

- Remote：`https://github.com/Client-Qv0/chat-ai-web`
- 分支：`master`

## 代码规范

- 不自动 commit/push，每步骤完成后询问
- 不添加代码注释（除非明确要求）
- 保持现有代码风格
- commit message 使用简洁英文
