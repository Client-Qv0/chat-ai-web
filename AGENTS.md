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

## 项目结构

```
chat–ai–web/
├── frontend/          # Vue 3 SPA
│   └── src/
│       ├── api/       # Axios API 封装
│       ├── components/ # 公共组件
│       ├── router/    # Vue Router
│       ├── stores/    # Pinia stores
│       ├── types/     # TypeScript 类型定义
│       └── views/     # 页面组件
├── backend/           # FastAPI 后端
│   └── app/
│       ├── api/v1/    # 内部 API 路由
│       ├── core/      # 配置、安全工具
│       ├── db/        # 数据库会话
│       ├── models/    # SQLAlchemy ORM 模型
│       ├── schemas/   # Pydantic 请求/响应模型
│       └── services/  # 业务逻辑
├── docker-compose.yml
└── docs/              # 文档
```

## 常用命令

### 前端

```bash
cd frontend
npm install          # 安装依赖
npm run dev          # 开发服务器 (localhost:5173)
npm run build        # 生产构建
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

## 开发环境

- 后端 API 基地址（开发）：`http://localhost:8000`
- 前端开发服务器：`http://localhost:5173`
- PostgreSQL：`localhost:5432`（数据库 `ai_platform`，用户 `ai_user`）
- Ollama：`http://127.0.0.1:11434`

## Python 环境

- 版本：3.13.12
- 绝对路径：`C:\Users\ASUS\AppData\Local\Programs\Python\Python313\python.exe`
- Shell 中不使用 `python` 关键字，使用绝对路径或 `py` 命令

## API 约定

- 内部接口前缀：`/api/v1/`
- 对外 LLM API：`/v1/chat/completions`（OpenAI 兼容格式）
- 鉴权：JWT (`Authorization: Bearer <token>`) 用于内部 API，API Key 用于对外 API
- SSE 流式接口不缓冲

## Git 仓库

- Remote：`https://github.com/Client-Qv0/chat-ai-web`

## 代码规范

- 不自动 commit/push，每步骤完成后询问
- 不添加代码注释（除非明确要求）
- 保持现有代码风格
- commit message 使用简洁英文
