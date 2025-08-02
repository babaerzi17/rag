from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum
from .base import Base

class KnowledgeBaseStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"  
    MAINTENANCE = "maintenance"

class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    type = Column(String(50))
    status = Column(String(20), nullable=False, default="active")
    color = Column(String(20))
    is_public = Column(Boolean, default=False)
    embedding_model = Column(String(100))
    vector_store = Column(String(100), default="chroma")
    kb_metadata = Column("metadata", JSON)  # Map to 'metadata' column in DB
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    
    # Relationships
    documents = relationship("Document", back_populates="knowledge_base")
    document_chunks = relationship("DocumentChunk", back_populates="knowledge_base")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)  # Changed from 'name' to 'title' per init.sql
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50))
    file_size = Column(BigInteger)
    status = Column(String(20), nullable=False, default="processing")
    page_count = Column(Integer)
    chunk_count = Column(Integer, default=0)
    doc_metadata = Column("doc_metadata", JSON)  # Map to 'doc_metadata' column in DB
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    
    # Relationships
    knowledge_base = relationship("KnowledgeBase", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    page_number = Column(Integer)
    vector_id = Column(String(255))  # Changed from 'embedding_id' to 'vector_id' per init.sql
    chunk_metadata = Column("metadata", JSON)  # Map to 'metadata' column in DB
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="chunks")
    knowledge_base = relationship("KnowledgeBase", back_populates="document_chunks") 
