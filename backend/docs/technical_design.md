# RAG后端技术方案

## 1. 概述

本文档旨在为RAG（Retrieval-Augmented Generation）系统的后端部分提供一套清晰、可扩展且易于维护的技术方案。方案的核心思想是**分层架构**和**模块化设计**，确保系统的高内聚、低耦合。

## 2. 系统架构

后端系统将采用经典的三层架构：**表现层（Routers）**、**服务层（Services）**和**数据访问层（Models/Database）**。

```mermaid
graph TD
    A[客户端] --> B{表现层 (Routers)};
    B --> C{服务层 (Services)};
    C --> D[数据访问层 (Models)];
    C --> E[外部API (OpenAI/Ollama)];
    D --> F[数据库 (PostgreSQL)];
    E --> C;

    subgraph "后端应用"
        B; C; D;
    end
```

-   **表现层 (Routers)**: 负责处理HTTP请求，验证输入数据，并调用相应的服务。此层不应包含任何业务逻辑。
-   **服务层 (Services)**: 包含核心的业务逻辑。每个服务类都遵循单一职责原则，负责处理一项特定的功能（如知识库管理、文档处理等）。
-   **数据访问层 (Models)**: 使用SQLAlchemy ORM定义数据模型，并与数据库进行交互。

## 3. 服务模块化设计

为了实现高内聚和低耦合，我们将根据功能将服务层拆分为多个独立的服务类。

### 3.1 服务划分

-   `KnowledgeService`: 负责知识库的CRUD操作。
-   `DocumentService`: 负责文档的上传、元数据管理和状态追踪。
-   `ParsingService`: 负责调用外部API（如OpenAI, Ollama）或本地库解析文档内容。
-   `ChunkingService`: 负责将解析后的文本进行分块，支持多种分块策略。
-   `VectorizationService`: 负责将文本块转换为向量并存入向量数据库。
-   `SearchService`: 负责根据用户查询在向量数据库中进行检索。

### 3.2 示例：`KnowledgeService`

```python
# backend/services/knowledge_service.py
from sqlalchemy.orm import Session
from ..models.knowledge import KnowledgeBase
from ..schemas.knowledge import KnowledgeBaseCreate

class KnowledgeService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, user_id: int, skip: int = 0, limit: int = 100) -> list[KnowledgeBase]:
        """获取用户的所有知识库"""
        return self.db.query(KnowledgeBase).filter(
            KnowledgeBase.created_by == user_id
        ).offset(skip).limit(limit).all()

    def create(self, user_id: int, kb_create: KnowledgeBaseCreate) -> KnowledgeBase:
        """创建一个新的知识库"""
        db_kb = KnowledgeBase(**kb_create.dict(), created_by=user_id)
        self.db.add(db_kb)
        self.db.commit()
        self.db.refresh(db_kb)
        return db_kb
    
    # ... 其他CRUD方法 ...
```

## 4. 依赖注入（Dependency Injection）

我们将全面采用FastAPI的依赖注入系统来管理服务实例和数据库会话，从而实现控制反转（IoC）。

### 4.1 创建依赖项

在`backend/dependencies.py`中统一管理所有服务的依赖注入函数。

```python
# backend/dependencies.py
from fastapi import Depends
from sqlalchemy.orm import Session
from .database import get_db
from .services.knowledge_service import KnowledgeService
# ... import其他服务 ...

def get_knowledge_service(db: Session = Depends(get_db)) -> KnowledgeService:
    return KnowledgeService(db)

# ... 其他服务的getter函数 ...
```

### 4.2 在路由中使用

在路由函数中，通过`Depends`关键字注入所需的服务。

```python
# backend/routers/knowledge.py
from fastapi import APIRouter, Depends
from ..dependencies import get_knowledge_service

router = APIRouter()

@router.post("/")
def create_knowledge_base(
    # ... 其他参数 ...
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    # ... 调用服务 ...
    return knowledge_service.create(...)
```

这种方式使得服务之间的依赖关系清晰明了，并且极大地提高了代码的可测试性。

## 5. 日志与监控

健壮的日志系统是调试和监控的关键。

### 5.1 日志配置

我们将创建一个集中的日志配置文件`backend/logger.py`，支持多目标输出（控制台和文件）。

-   **日志轮转**: 按天生成新的日志文件，便于归档和查询。
-   **日志级别**: 在不同环境中（开发/生产）可配置不同的日志级别。
-   **结构化日志**: 日志格式包含时间戳、日志级别、模块名和消息内容。

```python
# backend/logger.py
import logging
from logging.handlers import TimedRotatingFileHandler

# ... (详细配置) ...

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
```

### 5.2 在服务中使用

在每个服务类的构造函数中初始化一个logger实例。

```python
# backend/services/document_service.py
from ..logger import get_logger

class DocumentService:
    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger(__name__)

    def process_upload(self, ...):
        self.logger.info(f"开始处理文档上传: {file_name}")
        try:
            # ... 业务逻辑 ...
            self.logger.info(f"文档处理成功: {file_name}")
        except Exception as e:
            self.logger.error(f"处理文档失败: {file_name}", exc_info=True)
            raise
```

## 6. 错误处理与重试机制

### 6.1 全局错误处理中间件

通过FastAPI中间件捕获所有未处理的异常，返回统一格式的JSON错误响应。

-   **捕获特定异常**: 如`RequestValidationError`用于处理请求体验证失败，`SQLAlchemyError`用于数据库错误。
-   **记录关键错误**: 所有500级别的内部错误都将被详细记录到日志中。

### 6.2 外部API调用重试

对于所有外部API调用（如OpenAI, Ollama），我们将实现一个通用的重试装饰器，以处理暂时的网络故障或API不稳定。

-   **指数退避**: 每次重试的间隔时间将指数级增长，避免对下游服务造成冲击。
-   **可配置**: 可灵活配置重试次数、延迟时间和需要重试的异常类型。

```python
# backend/utils/retry.py
import time
import functools

def retry(max_tries=3, delay_seconds=1, exceptions=(Exception,)):
    # ... (装饰器实现) ...
```

```python
# 在服务中使用
from ..utils.retry import retry

class ParsingService:
    @retry(max_tries=3, exceptions=(ConnectionError,))
    def parse_with_openai(self, text: str):
        # ... 调用OpenAI API ...
```

## 7. 总结

本技术方案旨在构建一个健壮、可扩展、易于维护的后端系统。通过分层架构、服务模块化、依赖注入、全面的日志和错误处理机制，我们可以确保项目在未来的开发迭代中保持高质量和高效率。 