"""
依赖注入模块，用于管理服务实例和数据库会话
"""

from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Callable, Type, TypeVar, Any
import logging

# 使用绝对导入
try:
    from backend.config.database import get_db
    from backend.services.knowledge_service import KnowledgeService
    from backend.services.document_service import DocumentService
except ImportError as e:
    print(f"导入服务类失败: {e}")
    raise

# 创建一个日志记录器
logger = logging.getLogger(__name__)

# 创建一个泛型类型变量，用于服务类型
T = TypeVar('T')

def get_service(service_class: Type[T]) -> Callable[[Session], T]:
    """
    创建一个依赖函数，用于获取指定服务类的实例
    
    Args:
        service_class: 服务类
        
    Returns:
        依赖函数，接受数据库会话作为参数，返回服务实例
    """
    def _get_service(db: Session = Depends(get_db)) -> T:
        return service_class(db)
    return _get_service

# 知识库服务
get_knowledge_service = get_service(KnowledgeService)

# 文档服务
get_document_service = get_service(DocumentService) 
