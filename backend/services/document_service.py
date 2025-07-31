from sqlalchemy.orm import Session
from fastapi import UploadFile
from typing import List, Optional, Dict, Any
import logging
import os
import uuid
from datetime import datetime

# Import models
from ..models.knowledge import Document, DocumentStatus, KnowledgeBase
from ..schemas.knowledge import DocumentCreate, DocumentUpdate, DocumentResponse

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self, db: Session):
        self.db = db
    
    async def upload(self, kb_id: int, user_id: int, file: UploadFile) -> Optional[DocumentResponse]:
        """上传文档到知识库"""
        # 检查知识库是否存在且属于用户
        kb = (
            self.db.query(KnowledgeBase)
            .filter(KnowledgeBase.id == kb_id, KnowledgeBase.created_by == user_id)
            .first()
        )
        if not kb:
            return None
        
        # 支持的文件类型
        allowed_extensions = {'.txt', '.pdf', '.doc', '.docx', '.md'}
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in allowed_extensions:
            return None
        
        # 生成唯一文件名
        unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
        
        # 创建上传目录
        upload_dir = f"uploads/documents/{kb_id}"
        os.makedirs(upload_dir, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(upload_dir, unique_filename)
        
        try:
            contents = await file.read()
            with open(file_path, "wb") as f:
                f.write(contents)
        except Exception as e:
            logger.error(f"文件保存失败: {e}")
            return None
        
        # 创建文档记录
        doc = Document(
            knowledge_base_id=kb_id,
            title=file.filename,
            file_path=file_path,
            file_size=len(contents),
            file_type=file_extension,
            status="processing",
            created_by=user_id
        )
        
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        
        return DocumentResponse.from_orm(doc)
    
    def get_all_by_kb(self, kb_id: int, user_id: int, skip: int = 0, limit: int = 100) -> List[DocumentResponse]:
        """获取知识库的文档列表"""
        # 检查知识库权限
        kb = (
            self.db.query(KnowledgeBase)
            .filter(KnowledgeBase.id == kb_id, KnowledgeBase.created_by == user_id)
            .first()
        )
        if not kb:
            return []
        
        documents = (
            self.db.query(Document)
            .filter(Document.knowledge_base_id == kb_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        return [DocumentResponse.from_orm(doc) for doc in documents]
    
    def get_by_id(self, doc_id: int, user_id: int) -> Optional[DocumentResponse]:
        """根据ID获取文档"""
        doc = (
            self.db.query(Document)
            .join(KnowledgeBase, Document.knowledge_base_id == KnowledgeBase.id)
            .filter(Document.id == doc_id, KnowledgeBase.created_by == user_id)
            .first()
        )
        return DocumentResponse.from_orm(doc) if doc else None
    
    def update_status(self, doc_id: int, status: DocumentStatus, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """更新文档状态"""
        doc = self.db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            return False
        
        doc.status = status
        if metadata:
            doc.doc_metadata = metadata
        
        self.db.commit()
        return True
    
    def delete(self, doc_id: int, user_id: int) -> bool:
        """删除文档"""
        doc = (
            self.db.query(Document)
            .join(KnowledgeBase, Document.knowledge_base_id == KnowledgeBase.id)
            .filter(Document.id == doc_id, KnowledgeBase.created_by == user_id)
            .first()
        )
        if not doc:
            return False
        
        # 删除文件
        try:
            if os.path.exists(doc.file_path):
                os.remove(doc.file_path)
        except Exception as e:
            logger.error(f"删除文件失败: {e}")
        
        # 删除数据库记录
        self.db.delete(doc)
        self.db.commit()
        return True 