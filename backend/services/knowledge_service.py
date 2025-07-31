from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging

# Import models
from ..models.knowledge import KnowledgeBase, KnowledgeBaseStatus
from ..schemas.knowledge import KnowledgeBaseCreate, KnowledgeBaseUpdate, KnowledgeBaseResponse

logger = logging.getLogger(__name__)

class KnowledgeService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, user_id: int, skip: int = 0, limit: int = 100) -> List[KnowledgeBaseResponse]:
        """获取用户的知识库列表"""
        knowledge_bases = (
            self.db.query(KnowledgeBase)
            .filter(KnowledgeBase.created_by == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        logger.info(f"从数据库查询到的知识库数量: {len(knowledge_bases)}")
        if knowledge_bases:
            logger.info(f"第一个知识库对象: {knowledge_bases[0].__dict__}")
        
        response_data = [KnowledgeBaseResponse.from_orm(kb) for kb in knowledge_bases]
        logger.info(f"序列化后的知识库数量: {len(response_data)}")
        if response_data:
            logger.info(f"第一个序列化后的知识库数据: {response_data[0].dict()}")
        return response_data
    
    def get_by_id(self, kb_id: int, user_id: int) -> Optional[KnowledgeBaseResponse]:
        """根据ID获取知识库"""
        kb = (
            self.db.query(KnowledgeBase)
            .filter(KnowledgeBase.id == kb_id, KnowledgeBase.created_by == user_id)
            .first()
        )
        return KnowledgeBaseResponse.from_orm(kb) if kb else None
    
    def create(self, user_id: int, knowledge_base_data: Dict[str, Any]) -> KnowledgeBaseResponse:
        """创建知识库"""
        kb = KnowledgeBase(
            **knowledge_base_data,
            created_by=user_id,
            status=KnowledgeBaseStatus.ACTIVE
        )
        self.db.add(kb)
        self.db.commit()
        self.db.refresh(kb)
        return KnowledgeBaseResponse.from_orm(kb)
    
    def update(self, kb_id: int, user_id: int, update_data: Dict[str, Any]) -> Optional[KnowledgeBaseResponse]:
        """更新知识库"""
        kb = (
            self.db.query(KnowledgeBase)
            .filter(KnowledgeBase.id == kb_id, KnowledgeBase.created_by == user_id)
            .first()
        )
        if not kb:
            return None
            
        for key, value in update_data.items():
            if hasattr(kb, key):
                setattr(kb, key, value)
        
        self.db.commit()
        self.db.refresh(kb)
        return KnowledgeBaseResponse.from_orm(kb)
    
    def delete(self, kb_id: int, user_id: int) -> bool:
        """删除知识库"""
        kb = (
            self.db.query(KnowledgeBase)
            .filter(KnowledgeBase.id == kb_id, KnowledgeBase.created_by == user_id)
            .first()
        )
        if not kb:
            return False
            
        self.db.delete(kb)
        self.db.commit()
        return True 