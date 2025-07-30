"""
知识库服务模块，负责知识库的CRUD操作
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.knowledge import KnowledgeBase
from ..logger import get_logger

class KnowledgeService:
    """
    知识库服务类，负责知识库的CRUD操作
    """
    
    def __init__(self, db: Session):
        """
        初始化知识库服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
        self.logger = get_logger(__name__)
    
    def get_all(self, user_id: int, skip: int = 0, limit: int = 100) -> List[KnowledgeBase]:
        """
        获取用户的所有知识库
        
        Args:
            user_id: 用户ID
            skip: 跳过的记录数
            limit: 返回的最大记录数
            
        Returns:
            知识库列表
        """
        self.logger.info(f"获取用户 {user_id} 的知识库列表: skip={skip}, limit={limit}")
        return self.db.query(KnowledgeBase).filter(
            KnowledgeBase.created_by == user_id
        ).offset(skip).limit(limit).all()
    
    def get_by_id(self, kb_id: int, user_id: int) -> Optional[KnowledgeBase]:
        """
        根据ID获取知识库
        
        Args:
            kb_id: 知识库ID
            user_id: 用户ID，用于权限验证
            
        Returns:
            知识库对象，如果不存在则返回None
        """
        self.logger.info(f"获取知识库: id={kb_id}, user_id={user_id}")
        return self.db.query(KnowledgeBase).filter(
            KnowledgeBase.id == kb_id,
            KnowledgeBase.created_by == user_id
        ).first()
    
    def create(self, user_id: int, data: dict) -> KnowledgeBase:
        """
        创建知识库
        
        Args:
            user_id: 用户ID
            data: 知识库数据
            
        Returns:
            新创建的知识库对象
        """
        self.logger.info(f"创建知识库: user_id={user_id}, data={data}")
        kb = KnowledgeBase(**data, created_by=user_id)
        self.db.add(kb)
        self.db.commit()
        self.db.refresh(kb)
        self.logger.info(f"知识库创建成功: id={kb.id}")
        return kb
    
    def update(self, kb_id: int, user_id: int, data: dict) -> Optional[KnowledgeBase]:
        """
        更新知识库
        
        Args:
            kb_id: 知识库ID
            user_id: 用户ID，用于权限验证
            data: 更新的数据
            
        Returns:
            更新后的知识库对象，如果知识库不存在则返回None
        """
        self.logger.info(f"更新知识库: id={kb_id}, user_id={user_id}, data={data}")
        kb = self.get_by_id(kb_id, user_id)
        if not kb:
            self.logger.warning(f"知识库不存在: id={kb_id}")
            return None
        
        # 更新字段
        for key, value in data.items():
            if hasattr(kb, key):
                setattr(kb, key, value)
        
        self.db.commit()
        self.db.refresh(kb)
        self.logger.info(f"知识库更新成功: id={kb.id}")
        return kb
    
    def delete(self, kb_id: int, user_id: int) -> bool:
        """
        删除知识库
        
        Args:
            kb_id: 知识库ID
            user_id: 用户ID，用于权限验证
            
        Returns:
            是否成功删除
        """
        self.logger.info(f"删除知识库: id={kb_id}, user_id={user_id}")
        kb = self.get_by_id(kb_id, user_id)
        if not kb:
            self.logger.warning(f"知识库不存在: id={kb_id}")
            return False
        
        self.db.delete(kb)
        self.db.commit()
        self.logger.info(f"知识库删除成功: id={kb_id}")
        return True 