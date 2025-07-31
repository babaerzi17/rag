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
    type: Optional[str] = Field(None, description="Knowledge base type")
    color: Optional[str] = Field(None, description="Color identifier")
    is_public: bool = Field(False, description="Whether it's public")
    embedding_model: Optional[str] = Field(None, description="Embedding model used")
    vector_store: Optional[str] = Field(None, description="Vector store used")
    kb_metadata: Optional[Dict[str, Any]] = Field(None, description="Knowledge base metadata")
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
    created_by: Optional[int] = Field(None, description="Creator ID")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: Optional[datetime] = Field(None, description="Update time")

    class Config:
        from_attributes = True

class DocumentBase(BaseModel):
    """Document base model"""
    title: str = Field(..., description="Document title")  # Changed from 'name' to 'title' per init.sql
    knowledge_base_id: int = Field(..., description="Knowledge base ID")  # Changed from 'kb_id'

class DocumentCreate(DocumentBase):
    """Request model for creating a document"""
    file_path: str = Field(..., description="File path")
    file_type: Optional[str] = Field(None, description="File type")
    file_size: Optional[int] = Field(None, description="File size (bytes)")

class DocumentUpdate(BaseModel):
    """Request model for updating a document"""
    title: Optional[str] = None  # Changed from 'name' to 'title'
    status: Optional[str] = None
    doc_metadata: Optional[Dict[str, Any]] = Field(None, description="Document metadata")  # Keep as 'doc_metadata' per init.sql

class DocumentResponse(DocumentBase):
    """Document response model"""
    id: int
    file_type: Optional[str] = Field(None, description="File type")
    file_size: Optional[int] = Field(None, description="File size (bytes)")
    status: str = Field(..., description="Processing status")
    page_count: Optional[int] = Field(None, description="Page count")
    chunk_count: int = Field(0, description="Chunk count")
    doc_metadata: Optional[Dict[str, Any]] = Field(None, description="Document metadata")  # Keep as 'doc_metadata' per init.sql
    created_by: Optional[int] = Field(None, description="Creator ID")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: Optional[datetime] = Field(None, description="Update time")

    class Config:
        from_attributes = True

class DocumentChunkBase(BaseModel):
    """Document chunk base model"""
    document_id: int = Field(..., description="Document ID")
    knowledge_base_id: int = Field(..., description="Knowledge base ID")
    chunk_index: int = Field(..., description="Chunk index")
    chunk_text: str = Field(..., description="Chunk content")
    page_number: Optional[int] = Field(None, description="Page number")

class DocumentChunkCreate(DocumentChunkBase):
    """Request model for creating a document chunk"""
    vector_id: Optional[str] = Field(None, description="Vector ID")  # Changed from 'embedding_id' to 'vector_id' per init.sql
    chunk_metadata: Optional[Dict[str, Any]] = Field(None, description="Chunk metadata")

class DocumentChunkResponse(DocumentChunkBase):
    """Document chunk response model"""
    id: int
    vector_id: Optional[str] = Field(None, description="Vector ID")  # Changed from 'embedding_id' to 'vector_id' per init.sql
    chunk_metadata: Optional[Dict[str, Any]] = Field(None, description="Chunk metadata")
    created_at: datetime = Field(..., description="Creation time")

    class Config:
        from_attributes = True 