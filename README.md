# Chat AI Web

局域网内部署的 AI 对话平台，基于本地大语言模型（Qwen 系列），支持流式对话、API 接口调用、用户鉴权及后台管理。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + TypeScript + Tailwind CSS + Element Plus |
| 后端 | Python + FastAPI + SQLAlchemy 2.0 (Async) + PostgreSQL |
| 部署 | Docker Compose + Nginx |
| 模型 | Qwen3.5-0.8b (Ollama) |

## 快速开始

### 环境要求

- Node.js 20+
- Python 3.12+
- PostgreSQL 15+
- Ollama（本地模型服务）

### 1. 准备模型

```bash
# 确保 Ollama 已安装并运行
ollama pull qwen3.5:0.8b
```

### 2. 准备数据库

```bash
# 创建数据库
psql -U postgres -c "CREATE USER ai_user WITH PASSWORD 'ai_password';"
psql -U postgres -c "CREATE DATABASE ai_platform OWNER ai_user;"
```

### 3. 启动后端

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

首次启动自动创建表。API 文档：http://localhost:8000/docs

### 4. 启动前端

```bash
cd frontend
npm install
npm run dev
```

访问：http://localhost:5173

### Docker 部署

```bash
docker compose up -d --build
```

访问：http://localhost

## 功能模块

| 模块 | 路径 | 说明 |
|------|------|------|
| 首页 | `/` | 对话 & API 入口 |
| 在线对话 | `/chat` | 流式对话、多轮历史、Markdown 渲染 |
| API 服务 | `/api` | 调用文档、Token 用量、API Key 管理 |
| 用户中心 | `/user/:phone` | 修改资料、修改密码 |
| 认证 | `/login` `/register` `/recovery` | JWT 鉴权 |
| 后台管理 | `/admin` | 管理员入口（开发中） |

## API 接口

### 内部 API (`/api/v1`)

需要 JWT 鉴权，通过网页登录获取。

### 对外 LLM API (`/v1`)

OpenAI 兼容格式，通过 API Key 鉴权。Key 格式：`sk-{phone}-{random}`。

```bash
curl -X POST http://localhost/v1/chat/completions \
  -H "Authorization: Bearer sk-138****8000-xxxx" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hello"}],"stream":true}'
```

## 项目结构

```
chat–ai–web/
├── frontend/          # Vue 3 SPA
├── backend/           # FastAPI 后端
├── docker-compose.yml # Docker 编排
├── PRD.md             # 产品需求文档
├── SPEC.md            # 技术规格说明
├── AGENTS.md          # AI Agent 开发指南
└── README.md
```

## License

MIT
