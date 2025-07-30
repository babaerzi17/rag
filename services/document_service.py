"""
文档服务模块，负责文档的上传、处理和管理
"""

import os
import uuid
from fastapi import UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import shutil
from datetime import datetime

try:
    from models.knowledge import Document, DocumentStatus, KnowledgeBase
    from logger import get_logger
except ImportError:
    try:
        from backend.models.knowledge import Document, DocumentStatus, KnowledgeBase
        from backend.logger import get_logger
    except ImportError:
        print("无法导入所需模块，请检查项目结构")

class DocumentService:
    """
    文档服务类，负责文档的上传、处理和管理
    """
    
    def __init__(self, db: Session):
        """
        初始化文档服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
        self.logger = get_logger(__name__)
        self.upload_dir = os.path.join(os.getcwd(), "uploads")
        # 确保上传目录存在
        os.makedirs(self.upload_dir, exist_ok=True)
    
    async def upload(self, kb_id: int, user_id: int, file: UploadFile) -> Optional[Document]:
        """
        上传文档到知识库
        
        Args:
            kb_id: 知识库ID
            user_id: 用户ID
            file: 上传的文件
            
        Returns:
            文档对象，如果知识库不存在或文件类型不支持则返回None
        """
        # 检查知识库是否存在
        kb = self.db.query(KnowledgeBase).filter(
            KnowledgeBase.id == kb_id,
            KnowledgeBase.created_by == user_id
        ).first()
        if not kb:
            self.logger.warning(f"知识库不存在: kb_id={kb_id}")
            return None
        
        # 检查文件类型
        filename = file.filename
        file_ext = os.path.splitext(filename)[1].lower()
        
        # 支持的文件类型
        supported_extensions = ['.txt', '.pdf', '.doc', '.docx', '.md', '.csv', '.json']
        if file_ext not in supported_extensions:
            self.logger.warning(f"不支持的文件类型: {file_ext}")
            return None
        
        # 生成唯一文件名
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(self.upload_dir, unique_filename)
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 创建文档记录
        doc = Document(
            kb_id=kb_id,
            name=filename,
            file_path=file_path,
            file_type=file_ext[1:],  # 去掉点号
            file_size=os.path.getsize(file_path),
            status=DocumentStatus.PENDING,
            created_by=user_id
        )
        
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        self.logger.info(f"文档上传成功: kb_id={kb_id}, doc_id={doc.id}, file_name={filename}")
        
        return doc
    
    def get_all_by_kb(self, kb_id: int, user_id: int, skip: int = 0, limit: int = 100) -> List[Document]:
        """
        获取知识库的所有文档
        
        Args:
            kb_id: 知识库ID
            user_id: 用户ID
            skip: 跳过的记录数
            limit: 返回的最大记录数
            
        Returns:
            文档列表
        """
        self.logger.info(f"获取知识库文档: kb_id={kb_id}, user_id={user_id}, skip={skip}, limit={limit}")
        return self.db.query(Document).join(KnowledgeBase).filter(
            Document.kb_id == kb_id,
            KnowledgeBase.created_by == user_id
        ).offset(skip).limit(limit).all()
    
    def get_by_id(self, doc_id: int, user_id: int) -> Optional[Document]:
        """
        根据ID获取文档
        
        Args:
            doc_id: 文档ID
            user_id: 用户ID
            
        Returns:
            文档对象，如果不存在则返回None
        """
        self.logger.info(f"获取文档: doc_id={doc_id}, user_id={user_id}")
        return self.db.query(Document).join(KnowledgeBase).filter(
            Document.id == doc_id,
            KnowledgeBase.created_by == user_id
        ).first()
    
    def update_status(self, doc_id: int, status: DocumentStatus, metadata: Dict[str, Any] = None) -> Optional[Document]:
        """
        更新文档状态
        
        Args:
            doc_id: 文档ID
            status: 新状态
            metadata: 元数据
            
        Returns:
            更新后的文档对象，如果不存在则返回None
        """
        self.logger.info(f"更新文档状态: doc_id={doc_id}, status={status}")
        doc = self.db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            self.logger.warning(f"文档不存在: doc_id={doc_id}")
            return None
        
        doc.status = status
        if metadata:
            # 如果存在metadata，则更新
            current_metadata = doc.metadata or {}
            current_metadata.update(metadata)
            doc.metadata = current_metadata
        
        doc.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(doc)
        self.logger.info(f"文档状态更新成功: doc_id={doc_id}, status={status}")
        return doc
    
    def delete(self, doc_id: int, user_id: int) -> bool:
        """
        删除文档
        
        Args:
            doc_id: 文档ID
            user_id: 用户ID
            
        Returns:
            是否成功删除
        """
        self.logger.info(f"删除文档: doc_id={doc_id}, user_id={user_id}")
        doc = self.get_by_id(doc_id, user_id)
        if not doc:
            self.logger.warning(f"文档不存在: doc_id={doc_id}")
            return False
        
        # 删除文件
        try:
            if os.path.exists(doc.file_path):
                os.remove(doc.file_path)
        except Exception as e:
            self.logger.error(f"删除文件失败: path={doc.file_path}, error={str(e)}")
        
        # 删除数据库记录
        self.db.delete(doc)
        self.db.commit()
        self.logger.info(f"文档删除成功: doc_id={doc_id}")
        return True 