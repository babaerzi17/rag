"""
Knowledge base related Pydantic models
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
    """Knowledge base base model"""
    name: str = Field(..., description="Knowledge base name")
    description: Optional[str] = Field(None, description="Knowledge base description")
    type: str = Field("general", description="Knowledge base type")
    color: Optional[str] = Field(None, description="Color identifier")
    is_public: bool = Field(False, description="Whether it's public")
    settings: Optional[Dict[str, Any]] = Field(None, description="Knowledge base settings")
    tags: Optional[List[str]] = Field(None, description="Tags")

class KnowledgeBaseCreate(KnowledgeBaseBase):
    """Request model for creating a knowledge base"""
    pass

class KnowledgeBaseUpdate(KnowledgeBaseBase):
    """Request model for updating a knowledge base"""
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    is_public: Optional[bool] = None

class KnowledgeBaseResponse(KnowledgeBaseBase):
    """Knowledge base response model"""
    id: int
    status: str = Field("active", description="Knowledge base status")
    created_by: int = Field(..., description="Creator ID")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: Optional[datetime] = Field(None, description="Update time")

    class Config:
        orm_mode = True

class DocumentBase(BaseModel):
    """Document base model"""
    name: str = Field(..., description="Document name")
    kb_id: int = Field(..., description="Knowledge base ID")

class DocumentCreate(DocumentBase):
    """Request model for creating a document"""
    file_path: str = Field(..., description="File path")
    file_type: str = Field(..., description="File type")
    file_size: int = Field(..., description="File size (bytes)")

class DocumentUpdate(BaseModel):
    """Request model for updating a document"""
    name: Optional[str] = None
    status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class DocumentResponse(DocumentBase):
    """Document response model"""
    id: int
    file_type: str = Field(..., description="File type")
    file_size: int = Field(..., description="File size (bytes)")
    status: str = Field(..., description="Processing status")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata")
    created_by: int = Field(..., description="Creator ID")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: Optional[datetime] = Field(None, description="Update time")

    class Config:
        orm_mode = True

class DocumentChunkBase(BaseModel):
    """Document chunk base model"""
    doc_id: int = Field(..., description="Document ID")
    content: str = Field(..., description="Chunk content")
    chunk_index: int = Field(..., description="Chunk index")

class DocumentChunkCreate(DocumentChunkBase):
    """Request model for creating a document chunk"""
    embedding_id: str = Field(..., description="Vector ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata")

class DocumentChunkResponse(DocumentChunkBase):
    """Document chunk response model"""
    id: int
    embedding_id: str = Field(..., description="Vector ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: Optional[datetime] = Field(None, description="Update time")

    class Config:
        orm_mode = True 