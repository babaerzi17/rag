"""
知识库相关的Pydantic模型
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class KnowledgeBaseStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"

class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class KnowledgeBaseBase(BaseModel):
    """知识库基础模型"""
    name: str = Field(..., description="知识库名称")
    description: Optional[str] = Field(None, description="知识库描述")
    type: str = Field("general", description="知识库类型")
    color: Optional[str] = Field(None, description="颜色标识")
    is_public: bool = Field(False, description="是否公开")
    settings: Optional[Dict[str, Any]] = Field(None, description="知识库设置")
    tags: Optional[List[str]] = Field(None, description="标签")

class KnowledgeBaseCreate(KnowledgeBaseBase):
    """创建知识库的请求模型"""
    pass

class KnowledgeBaseUpdate(KnowledgeBaseBase):
    """更新知识库的请求模型"""
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    is_public: Optional[bool] = None

class KnowledgeBaseResponse(KnowledgeBaseBase):
    """知识库响应模型"""
    id: int
    status: str = Field("active", description="知识库状态")
    created_by: int = Field(..., description="创建者ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        orm_mode = True

class DocumentBase(BaseModel):
    """文档基础模型"""
    name: str = Field(..., description="文档名称")
    kb_id: int = Field(..., description="所属知识库ID")

class DocumentCreate(DocumentBase):
    """创建文档的请求模型"""
    file_path: str = Field(..., description="文件路径")
    file_type: str = Field(..., description="文件类型")
    file_size: int = Field(..., description="文件大小(字节)")

class DocumentUpdate(BaseModel):
    """更新文档的请求模型"""
    name: Optional[str] = None
    status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class DocumentResponse(DocumentBase):
    """文档响应模型"""
    id: int
    file_type: str = Field(..., description="文件类型")
    file_size: int = Field(..., description="文件大小(字节)")
    status: str = Field(..., description="处理状态")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    created_by: int = Field(..., description="创建者ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        orm_mode = True

class DocumentChunkBase(BaseModel):
    """文档块基础模型"""
    doc_id: int = Field(..., description="所属文档ID")
    content: str = Field(..., description="块内容")
    chunk_index: int = Field(..., description="块索引")

class DocumentChunkCreate(DocumentChunkBase):
    """创建文档块的请求模型"""
    embedding_id: str = Field(..., description="向量ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")

class DocumentChunkResponse(DocumentChunkBase):
    """文档块响应模型"""
    id: int
    embedding_id: str = Field(..., description="向量ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        orm_mode = True 