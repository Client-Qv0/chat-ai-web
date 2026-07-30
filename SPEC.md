# AI对话平台网站 技术规格说明书 (Spec)

## 1. 系统架构设计

### 1.1 整体架构图
系统采用前后端分离架构，通过 Nginx 进行统一网关路由。

```text
[ 浏览器 (Vue3 SPA) ] 
       │
       ▼
[ Nginx (反向代理 & 静态资源托管) ]
       │
       ├─► /, /chat, /api, /login... ──► [ Vue3 静态文件 (Nginx 直接返回) ]
       │
       └─► /api/v1/*, /v1/* ───────────► [ FastAPI 后端服务 ]
                                                 │
                                                 ├─► [ PostgreSQL 数据库 ]
                                                 │
                                                 └─► [ 本地 LLM 服务 (Qwen3.5-0.8b) ]
                                                      (通过 Ollama/vLLM 等暴露本地 API)
```

### 1.2 技术栈规格
- **前端**：Vue 3.4+ (Composition API), Vite 5, TypeScript 5, Tailwind CSS 3, Element Plus, `markdown-it` (渲染), `highlight.js` (代码高亮), `EventSource` (SSE流式接收)。
- **后端**：Python 3.10+, FastAPI, SQLAlchemy 2.0 (Async), Pydantic v2, `passlib` (密码哈希), `PyJWT` (鉴权), `nanoid` (ID生成)。
- **数据库**：PostgreSQL 15+。
- **部署**：Docker 24+, Docker Compose v2, Nginx 1.24+。

---

## 2. 数据库设计 (PostgreSQL)

采用 SQLAlchemy ORM 定义，核心表结构如下：

### 2.1 用户表 (`users`)
| 字段名          | 类型         | 约束/说明                               |
| --------------- | ------------ | --------------------------------------- |
| `id`            | UUID         | 主键，默认生成                          |
| `username`      | VARCHAR(50)  | 用户名                                  |
| `phone`         | VARCHAR(11)  | **唯一索引**，+86手机号（仅存11位数字） |
| `password_hash` | VARCHAR(255) | Bcrypt/Argon2 哈希密码                  |
| `role`          | ENUM         | `user` (默认), `admin`                  |
| `avatar_url`    | VARCHAR(255) | 头像URL（默认生成首字母头像）           |
| `created_at`    | TIMESTAMP    | 注册时间                                |

### 2.2 对话表 (`conversations`)
| 字段名       | 类型         | 约束/说明                                  |
| ------------ | ------------ | ------------------------------------------ |
| `id`         | UUID         | 主键                                       |
| `user_id`    | UUID         | 外键关联 `users.id`                        |
| `route_id`   | VARCHAR(50)  | **唯一索引**，格式：`{phone}-{random_str}` |
| `title`      | VARCHAR(100) | 对话标题（默认取第一条消息摘要）           |
| `created_at` | TIMESTAMP    | 创建时间                                   |

### 2.3 消息表 (`messages`)
| 字段名            | 类型      | 约束/说明                                                    |
| ----------------- | --------- | ------------------------------------------------------------ |
| `id`              | UUID      | 主键                                                         |
| `conversation_id` | UUID      | 外键关联 `conversations.id`                                  |
| `role`            | ENUM      | `user`, `assistant`, `system`                                |
| `content`         | TEXT      | 消息文本内容                                                 |
| `metadata`        | JSONB     | 存储附加信息：`{"thinking": true, "search": false, "files": ["url1"]}` |
| `tokens_used`     | INT       | 该条消息消耗的 Token 数                                      |
| `created_at`      | TIMESTAMP | 发送时间                                                     |

### 2.4 API密钥表 (`api_keys`)
| 字段名       | 类型         | 约束/说明                                      |
| ------------ | ------------ | ---------------------------------------------- |
| `id`         | UUID         | 主键                                           |
| `user_id`    | UUID         | 外键关联 `users.id`                            |
| `key_prefix` | VARCHAR(20)  | 密钥前缀，用于展示（如 `sk-138****8000-a1b2`） |
| `key_hash`   | VARCHAR(255) | 完整密钥的哈希值（用于校验）                   |
| `status`     | ENUM         | `active`, `revoked`                            |
| `created_at` | TIMESTAMP    | 创建时间                                       |

### 2.5 Token消耗日志表 (`token_usage_logs`)
| 字段名              | 类型        | 约束/说明                  |
| ------------------- | ----------- | -------------------------- |
| `id`                | UUID        | 主键                       |
| `user_id`           | UUID        | 外键                       |
| `api_key_id`        | UUID        | 可空，若通过网页对话则为空 |
| `model_name`        | VARCHAR(50) | 调用的模型名称             |
| `prompt_tokens`     | INT         | 输入 Token                 |
| `completion_tokens` | INT         | 输出 Token                 |
| `created_at`        | TIMESTAMP   | 消耗时间                   |

---

## 3. API 接口规格 (FastAPI)

所有内部接口前缀为 `/api/v1`，需通过 Header `Authorization: Bearer <JWT>` 鉴权。
对外提供的 LLM API 兼容 OpenAI 格式，前缀为 `/v1`，通过 Header `Authorization: Bearer <API_KEY>` 鉴权。

### 3.1 认证模块 (`/api/v1/auth`)
- `POST /register`
  - **Body**: `{"username": "str", "phone": "str", "password": "str"}`
  - **逻辑**: 正则校验 `^1[3-9]\d{9}$`；检查 phone 唯一性；密码加盐哈希；入库。
- `POST /login`
  - **Body**: `{"phone": "str", "password": "str"}`
  - **返回**: `{"access_token": "str", "token_type": "bearer", "user_info": {...}}`
- `GET /me`
  - **返回**: 当前用户基本信息。

### 3.2 在线对话模块 (`/api/v1/chat`)
- `GET /conversations`
  - **返回**: 当前用户的对话列表（按时间倒序）。
- `POST /conversations`
  - **逻辑**: 生成 `route_id` = `{user.phone}-{nanoid(12, alphabet='0123456789abcdefghijklmnopqrstuvwxyz')}`。
  - **返回**: 新建的对话对象。
- `POST /conversations/{route_id}/messages` (SSE 流式接口)
  - **Body**: `{"content": "str", "metadata": {"thinking": bool, "search": bool, "files": ["url"]}}`
  - **逻辑**: 
    1. 保存 User 消息。
    2. 组装 Prompt（结合历史消息、深度思考/联网搜索的 System Prompt）。
    3. 调用本地 Qwen 模型 API，获取流式响应。
    4. 通过 `StreamingResponse` (SSE) 逐字返回给前端。
    5. 流结束后，保存 Assistant 消息，计算并记录 Token 消耗。

### 3.3 API 服务模块 (`/api/v1/api-keys`)
- `GET /`
  - **返回**: 当前用户的 API Key 列表（脱敏展示）。
- `POST /generate`
  - **逻辑**: 生成 Key = `sk-{user.phone}-{nanoid(16)}`。计算哈希存入 DB，返回完整 Key（仅展示一次）。
- `DELETE /{key_id}`
  - **逻辑**: 将状态更新为 `revoked`。

### 3.4 对外 LLM API (`/v1/chat/completions`)
- **鉴权**: 解析 `Authorization` 中的 API Key，校验哈希。
- **逻辑**: 与内部对话流式逻辑类似，但需根据 API Key 归属记录 `token_usage_logs`（关联 `api_key_id`）。

---

## 4. 前端路由与组件设计

### 4.1 路由守卫 (Router Guards)
- **Auth Guard**: 拦截 `/chat/*`, `/api/*`, `/user/*`。检查 LocalStorage 中的 Token，若失效则重定向至 `/login`。
- **Role Guard**: 拦截 `/admin/*`。检查用户 `role`，若非 `admin` 则渲染 403 页面。

### 4.2 路由表定义
```typescript
const routes = [
  { path: '/', component: Home },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/recovery', component: Recovery },
  
  // 需登录
  { 
    path: '/chat', 
    component: ChatLayout,
    children: [
      { path: '', component: EmptyChat }, // 默认空状态
      { path: ':routeId', component: ChatWindow } // routeId 为 {phone}-{random}
    ]
  },
  { 
    path: '/api', 
    component: ApiLayout,
    children: [
      { path: '', redirect: '/api/index' },
      { path: 'index', component: ApiDocs },
      { path: 'token', component: TokenUsage },
      { path: 'key', component: ApiKeyManage }
    ]
  },
  
  // 新窗口打开
  { path: '/user/:phone', component: UserProfile },
  
  // 需管理员
  { path: '/admin', component: AdminLayout, meta: { requiresAdmin: true } }
]
```

### 4.3 核心组件拆解
1. **`GlobalUserWidget` (左下角悬浮组件)**
   - **位置**: `fixed bottom-4 left-4`。
   - **逻辑**: 监听路由变化，若当前路由在 `['/', '/login', '/register', '/admin']` 中，则 `v-show="false"` 隐藏。
   - **交互**: `@click="window.open('/user/' + currentUser.phone, '_blank')"`。
2. **`ChatStreamRenderer` (对话流渲染组件)**
   - **功能**: 接收 SSE 数据流，实时拼接文本。
   - **特性**: 使用 `markdown-it` 实时渲染，集成 `highlight.js`，处理代码块复制按钮。
3. **`FileUploader` (文件上传组件)**
   - **逻辑**: 限制文件类型（pdf, txt, docx, png, jpg），限制大小（10MB）。上传后返回 OSS/本地存储 URL，存入消息的 `metadata.files` 中。

---

## 5. 核心业务逻辑说明

### 5.1 本地模型对接逻辑 (FastAPI -> LLM)
假设本地 Qwen3.5-0.8b 通过 Ollama 部署在 `http://127.0.0.1:11434`。
```python
import httpx

async def stream_qwen_response(prompt: str, enable_thinking: bool):
    # 构建 Ollama 请求体
    payload = {
        "model": "qwen3.5:0.8b",
        "prompt": prompt,
        "stream": True,
        "options": {
            "temperature": 0.7
        }
    }
    # 若开启深度思考，可调整 system prompt 或 temperature
    if enable_thinking:
        payload["system"] = "Please think step-by-step before answering..."

    async with httpx.AsyncClient() as client:
        async with client.stream("POST", "http://127.0.0.1:11434/api/generate", json=payload) as response:
            async for line in response.aiter_lines():
                if line:
                    data = json.loads(line)
                    yield data.get("response", "")
```

### 5.2 路由 ID 与 API Key 生成算法
使用 `nanoid` 保证高并发下的唯一性和安全性。
```python
from nanoid import generate

# 对话路由 ID: 电话明文 + 12位英数混合
def generate_route_id(phone: str) -> str:
    return f"{phone}-{generate(size=12, alphabet='0123456789abcdefghijklmnopqrstuvwxyz')}"

# API Key: sk- + 电话明文 + 16位英数混合
def generate_api_key(phone: str) -> str:
    return f"sk-{phone}-{generate(size=16)}"
```

### 5.3 权限与 403 拦截
- **后端**: 使用 FastAPI 的 `Depends` 注入权限校验。
  ```python
  def require_admin(current_user: User = Depends(get_current_user)):
      if current_user.role != "admin":
          raise HTTPException(status_code=403, detail="Forbidden")
      return current_user
  ```
- **前端**: 在 `/admin` 路由的 `beforeEnter` 钩子中校验，或直接由后端返回 403 时前端渲染统一的 403 错误页。

---

## 6. 部署与运维规格

### 6.1 Docker Compose 编排 (`docker-compose.yml`)
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

  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql+asyncpg://ai_user:ai_password@db:5432/ai_platform
      - LLM_API_URL=http://host.docker.internal:11434 # 指向宿主机的本地模型
    depends_on:
      - db
    ports:
      - "8000:8000"

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  pg_data:
```

### 6.2 Nginx 核心配置 (`nginx.conf`)
重点处理 SSE 流式接口的代理配置，防止 Nginx 缓冲导致流式输出卡顿。

```nginx
server {
    listen 80;
    server_name localhost;

    # 前端静态资源
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html; # Vue Router History 模式
    }

    # 内部 API 接口
    location /api/v1/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 对外 LLM API 及 SSE 流式接口 (关键配置)
    location /v1/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        
        # SSE 防缓冲配置
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 300s; # 防止长连接超时断开
        chunked_transfer_encoding on;
    }
}
```

### 6.3 本地模型环境要求
- 确保 Ubuntu 宿主机已安装并运行 Ollama 或 vLLM。
- 若使用 Docker 部署后端，需确保后端容器能访问宿主机的模型服务（如使用 `host.docker.internal` 或 `--network host` 模式）。
- 模型需提前拉取：`ollama pull qwen2.5:0.5b` (注：目前官方最新为 qwen2.5，若确为 qwen3.5 请替换对应模型名)。