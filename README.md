# 项目名称：知识中心 RAG 应用程序

## 项目概述

这是一个知识中心应用程序，结合了 RAG (Retrieval-Augmented Generation) 技术，旨在提供一个智能问答和知识管理平台。该项目包含一个基于 FastAPI 的后端和一个基于 Vue.js 的前端。

## 功能模块

- **用户认证与授权**：安全的登录、注册和权限管理。
- **知识库管理**：上传、存储和管理各类文档（PDF, DOCX, Markdown 等）。
- **文档分块与索引**：自动将文档分块并创建向量索引，以便 RAG 模型检索。
- **智能问答**：用户可以通过自然语言提问，系统将从知识库中检索相关信息并生成回答。
- **A/B 测试**：支持对不同模型或策略进行 A/B 测试。
- **模型管理**：管理和配置不同的 LLM 模型。

## 技术栈

### 后端 (Python/FastAPI)

- **FastAPI**：现代、快速（高性能）的 Web 框架，用于构建 API。
- **SQLAlchemy**：Python SQL 工具包和 ORM，用于数据库交互。
- **PostgreSQL**：关系型数据库（你可以根据配置更改为其他数据库）。
- **ChromaDB**：开源嵌入数据库，用于存储和检索向量。
- **Sentence-Transformers**：用于生成文本嵌入。
- **LangChain**：用于构建基于 LLM 的应用程序的框架。
- **Passlib, python-jose**：用于身份验证和安全。
- **Pydantic**：用于数据验证和设置管理。

### 前端 (Vue.js/Vite)

- **Vue.js 3**：渐进式 JavaScript 框架，用于构建用户界面。
- **Vite**：下一代前端工具，提供快速开发体验。
- **Element Plus**：Vue 3 的组件库，用于构建美观的用户界面。
- **Pinia**：Vue 的状态管理库。
- **Vue Router**：Vue 的官方路由。
- **Axios**：基于 Promise 的 HTTP 客户端。
- **Socket.IO Client**：用于实时通信。

## 安装与运行

### 前提条件

在开始之前，请确保你的系统已安装以下软件：

- **Python 3.8+**
- **Node.js (LTS 版本)** 和 **npm (或 yarn, pnpm)**
- **Git**
- **PostgreSQL** 数据库（或其他你配置的数据库）

### 步骤 1: 克隆仓库

```bash
git clone <仓库地址>
cd rag
```

### 步骤 2: 后端设置

1.  **创建并激活虚拟环境**：
    ```bash
    cd backend
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

2.  **安装 Python 依赖**：
    ```bash
    pip install -r requirements.txt --trusted-host mirrors.huaweicloud.com
    ```

3.  **配置数据库**：
    - 确保你的 PostgreSQL 数据库正在运行。
    - 根据 `backend/config/database.py` 或相关配置文件，设置数据库连接信息（例如，环境变量 `DATABASE_URL`）。

4.  **运行数据库迁移 (Alembic)**：
    ```bash
    alembic upgrade head
    ```

5.  **启动后端服务**：
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    # 如果你的主入口文件不是 main.py，请相应调整
    ```

### 步骤 3: 前端设置

1.  **进入前端目录**：
    ```bash
    cd ../frontend
    ```

2.  **安装 Node.js 依赖**：
    ```bash
    npm install
    ```

3.  **启动前端开发服务器**：
    ```bash
    npm run dev
    ```

    前端应用通常会在 `http://localhost:5173` (或类似端口) 启动。

## 项目结构

```
rag/
├── backend/               # 后端 FastAPI 应用
│   ├── auth/              # 认证和安全模块
│   ├── common/            # 通用工具和 CRUD 操作
│   ├── config/            # 配置，如数据库连接
│   ├── models/            # 数据库模型定义
│   ├── routers/           # API 路由定义
│   ├── schemas/           # Pydantic 数据模型
│   ├── services/          # 业务逻辑服务
│   ├── tests/             # 后端测试
│   ├── utils/             # 工具函数
│   ├── venv/              # Python 虚拟环境
│   └── main.py            # 后端主入口文件
├── frontend/              # 前端 Vue.js 应用
│   ├── src/               # 源代码
│   │   ├── api/           # API 请求封装
│   │   ├── components/    # 可复用组件
│   │   ├── router/        # Vue Router 配置
│   │   ├── stores/        # Pinia 状态管理
│   │   ├── types/         # TypeScript 类型定义
│   │   ├── utils/         # 前端工具函数
│   │   └── views/         # 页面组件
│   └── package.json       # 前端依赖配置
├── README.md              # 项目说明文档
└── ...                    # 其他配置文件或脚本
```

## 贡献

欢迎贡献！请查阅 `CONTRIBUTING.md` (如果存在) 获取更多信息。

## 许可证

本项目采用 [MIT 许可证](LICENSE) (或你选择的其他许可证)。

