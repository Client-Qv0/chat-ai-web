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

| 依赖 | 版本 | 检查命令 |
|------|------|----------|
| Node.js | 20+ | `node -v` |
| Python | 3.12+ | `py --version` |
| PostgreSQL | 15+ | `psql --version` |
| Ollama | 最新 | `ollama --version` |

### 1. 安装 Ollama 并拉取模型

**macOS / Linux：**

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows：** 从 [ollama.com](https://ollama.com/download) 下载安装包。

启动 Ollama 并拉取模型：

```bash
ollama serve          # 启动服务（Windows 上安装后自动运行）
ollama pull qwen3.5:0.8b
```

验证：

```bash
ollama run qwen3.5:0.8b "Hello"
```

### 2. 安装并配置 PostgreSQL

**macOS：**

```bash
brew install postgresql@15
brew services start postgresql@15
```

**Ubuntu：**

```bash
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**Windows：** 从 [postgresql.org](https://www.postgresql.org/download/windows/) 下载安装。

创建数据库和用户：

```bash
# macOS (Homebrew)
psql -U $USER postgres -c "CREATE USER ai_user WITH PASSWORD 'ai_password';"
psql -U $USER postgres -c "CREATE DATABASE ai_platform OWNER ai_user;"

# Ubuntu
sudo -u postgres psql -c "CREATE USER ai_user WITH PASSWORD 'ai_password';"
sudo -u postgres psql -c "CREATE DATABASE ai_platform OWNER ai_user;"

# Windows (PowerShell, 以安装时设置的管理员用户为准)
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -c "CREATE USER ai_user WITH PASSWORD 'ai_password';"
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -c "CREATE DATABASE ai_platform OWNER ai_user;"
```

### 3. 配置后端环境变量

```bash
cd backend
```

创建 `backend/.env`（如不存在）：

```env
DATABASE_URL=postgresql+asyncpg://ai_user:ai_password@localhost:5432/ai_platform
LLM_API_URL=http://127.0.0.1:11434
LLM_MODEL=qwen3.5:0.8b
SECRET_KEY=请替换为随机字符串
ACCESS_TOKEN_EXPIRE_MINUTES=10080
ALLOWED_ORIGINS=["http://localhost:5173"]
```

> 生产环境务必修改 `SECRET_KEY`，可用 `python -c "import secrets; print(secrets.token_hex(32))"` 生成。

### 4. 启动后端

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

首次启动自动建表。验证：

```bash
curl http://localhost:8000/health
# 返回 {"status":"ok"}
```

API 文档：http://localhost:8000/docs

### 5. 启动前端

```bash
cd frontend
npm install
npm run dev
```

访问：http://localhost:5173

### 6. 首次使用

1. 打开 http://localhost:5173，点击「在线对话」
2. 跳转到登录页 — 点击「注册」创建账号
3. 登录后即可开始对话

### Docker 部署

如果你不想手动安装 PostgreSQL，可以用 Docker 托管数据库：

```bash
# 仅启动数据库
docker compose up -d db

# 启动全部服务（前端 + 后端 + 数据库）
docker compose up -d --build
```

Docker 启动后后端会自动连接 `db` 容器中的 PostgreSQL，无需手动创建数据库。访问：http://localhost

### 常见问题

**`uvicorn` 启动报数据库连接错误：**
PostgreSQL 服务未运行。检查：`pg_isready` 或 `systemctl status postgresql`。

**对话无响应：**
确保 Ollama 在运行且有模型：`ollama list`。如果模型名不匹配，修改 `backend/.env` 中的 `LLM_MODEL`。

**前端 401 错误：**
Token 已过期，清除浏览器 LocalStorage 后重新登录。

**Windows 上 pip 不是命令：**
使用绝对路径 `C:\Users\<用户名>\AppData\Local\Programs\Python\Python313\python.exe -m pip install -r requirements.txt`，或使用 `py -m pip install -r requirements.txt`。

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
