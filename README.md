# RAG 项目概述

这是一个RAG（Retrieval-Augmented Generation）项目，旨在结合检索和生成技术，提供更强大、更准确的信息问答能力。项目包含前端和后端两部分，前端负责用户界面交互，后端负责数据处理、模型调用和业务逻辑。

## 后端 SQL 打印功能

### 用途

为了帮助您更好地调试和理解后端数据库操作，我们增加了SQL语句的打印功能。当您在开发或测试过程中遇到数据相关的问题时，可以直接查看后端执行的SQL语句，从而快速定位问题。

### 实现方式

我们将通过修改后端数据库会话的创建过程，注入一个“拦截器”来捕获并打印所有执行的SQL语句。这样，每次数据库执行查询、插入、更新或删除操作时，相应的SQL语句都会被记录下来。

### 使用方法

您可以通过设置 `SQLALCHEMY_ECHO` 环境变量来开启或关闭 SQL 语句的打印。在您的项目根目录下的 `.env` 文件中，添加或修改以下行：

```
SQLALCHEMY_ECHO=True  # 设置为 True 会打印所有SQL语句
# SQLALCHEMY_ECHO=False # 设置为 False 则不会打印SQL语句 (默认)
```

请注意，修改 `.env` 文件后，您可能需要重启后端服务才能使更改生效。

## 项目快速启动

为了方便您快速启动前端和后端服务，我们提供了两个批处理（.bat）文件。在运行之前，请确保您已安装 Node.js 和 Python，并且 Python 已经配置好环境变量。

### 后端服务设置（首次运行必读）

由于后端服务依赖于 Python 虚拟环境和相关库，首次启动前您可能需要手动确保虚拟环境已正确设置。

1.  **进入后端目录：** 在命令行中进入 `backend` 目录。
    ```bash
    cd backend
    ```
2.  **创建并激活虚拟环境（如果 `venv` 目录不存在）：**
    ```bash
    python -m venv venv
    # 激活虚拟环境
    venv\Scripts\activate.bat
    ```
3.  **安装后端依赖：**
    ```bash
    pip install -r requirements.txt
    ```

完成上述步骤后，`start_backend.bat` 脚本将能够自动检测并使用已设置的虚拟环境和依赖。

### 启动前端服务

在项目根目录双击运行 `start_frontend.bat` 文件，或者在命令行中执行：

```bash
start_frontend.bat
```

此脚本会自动导航到 `frontend` 目录，检查并安装 Node.js 依赖（如果尚未安装），然后启动前端开发服务器。

### 启动后端服务

在项目根目录双击运行 `start_backend.bat` 文件，或者在命令行中执行：

```bash
start_backend.bat
```

此脚本会自动导航到 `backend` 目录，检查、创建并激活 Python 虚拟环境，安装后端依赖（如果尚未安装），然后启动 Uvicorn 服务器。

