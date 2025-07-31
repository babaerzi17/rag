from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import os
import shutil
import sys
from datetime import datetime

# Ensure import paths are correct
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from ..database import get_db
    from ..models.knowledge import KnowledgeBase, Document, DocumentChunk, KnowledgeBaseStatus, DocumentStatus
    from ..models.user import User
    from ..auth.security import get_current_user
    from ..schemas import knowledge as schemas
    from ..services.knowledge_service import KnowledgeService
    from ..services.document_service import DocumentService
    from ..logger import get_logger
except ImportError:
    # 尝试绝对导入
    from backend.database import get_db
    from backend.models.knowledge import KnowledgeBase, Document, DocumentChunk, KnowledgeBaseStatus, DocumentStatus
    from backend.models.user import User
    from backend.auth.security import get_current_user
    from backend.schemas import knowledge as schemas
    from backend.services.knowledge_service import KnowledgeService
    from backend.services.document_service import DocumentService
    from backend.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

# 依赖函数：获取知识库服务
def get_knowledge_service_dep(db: Session = Depends(get_db)) -> KnowledgeService:
    return KnowledgeService(db)

# 依赖函数：获取文档服务
def get_document_service_dep(db: Session = Depends(get_db)) -> DocumentService:
    return DocumentService(db)

@router.get("/", response_model=List[schemas.KnowledgeBaseResponse])
async def get_knowledge_bases(
    skip: int = 0,
    limit: int = 100,
    search: str = "",
    page: int = 1,
    pageSize: int = 10,
    knowledge_service: KnowledgeService = Depends(get_knowledge_service_dep),
    current_user: User = Depends(get_current_user)
):
    """获取知识库列表"""
    # 处理分页参数
    if page > 0 and pageSize > 0:
        skip = (page - 1) * pageSize
        limit = pageSize
        
    logger.info(f"获取知识库列表: user_id={current_user.id}, skip={skip}, limit={limit}, search={search}")
    return knowledge_service.get_all(current_user.id, skip, limit)

@router.post("/", response_model=schemas.KnowledgeBaseResponse)
async def create_knowledge_base(
    knowledge_base: schemas.KnowledgeBaseCreate,
    knowledge_service: KnowledgeService = Depends(get_knowledge_service_dep),
    current_user: User = Depends(get_current_user)
):
    """创建知识库"""
    logger.info(f"创建知识库: user_id={current_user.id}, data={knowledge_base}")
    return knowledge_service.create(current_user.id, knowledge_base.dict())

@router.get("/{kb_id}", response_model=schemas.KnowledgeBaseResponse)
async def get_knowledge_base(
    kb_id: int,
    knowledge_service: KnowledgeService = Depends(get_knowledge_service_dep),
    current_user: User = Depends(get_current_user)
):
    """获取知识库详情"""
    logger.info(f"获取知识库详情: kb_id={kb_id}, user_id={current_user.id}")
    kb = knowledge_service.get_by_id(kb_id, current_user.id)
    if not kb:
        logger.warning(f"知识库不存在: kb_id={kb_id}")
        raise HTTPException(status_code=404, detail="知识库不存在")
    return kb

@router.put("/{kb_id}", response_model=schemas.KnowledgeBaseResponse)
async def update_knowledge_base(
    kb_id: int,
    knowledge_base: schemas.KnowledgeBaseUpdate,
    knowledge_service: KnowledgeService = Depends(get_knowledge_service_dep),
    current_user: User = Depends(get_current_user)
):
    """更新知识库"""
    logger.info(f"更新知识库: kb_id={kb_id}, user_id={current_user.id}, data={knowledge_base}")
    kb = knowledge_service.update(kb_id, current_user.id, knowledge_base.dict(exclude_unset=True))
    if not kb:
        logger.warning(f"知识库不存在: kb_id={kb_id}")
        raise HTTPException(status_code=404, detail="知识库不存在")
    return kb

@router.delete("/{kb_id}")
async def delete_knowledge_base(
    kb_id: int,
    knowledge_service: KnowledgeService = Depends(get_knowledge_service_dep),
    current_user: User = Depends(get_current_user)
):
    """删除知识库"""
    logger.info(f"删除知识库: kb_id={kb_id}, user_id={current_user.id}")
    success = knowledge_service.delete(kb_id, current_user.id)
    if not success:
        logger.warning(f"知识库不存在: kb_id={kb_id}")
        raise HTTPException(status_code=404, detail="知识库不存在")
    return {"message": "知识库删除成功"}

@router.post("/{kb_id}/documents", response_model=schemas.DocumentResponse)
async def upload_document(
    kb_id: int,
    file: UploadFile = File(...),
    document_service: DocumentService = Depends(get_document_service_dep),
    current_user: User = Depends(get_current_user)
):
    """上传文档到知识库"""
    logger.info(f"上传文档: kb_id={kb_id}, user_id={current_user.id}, file_name={file.filename}")
    doc = await document_service.upload(kb_id, current_user.id, file)
    if not doc:
        logger.warning(f"知识库不存在或文件类型不支持: kb_id={kb_id}, file_name={file.filename}")
        raise HTTPException(status_code=404, detail="知识库不存在或文件类型不支持")
    
    # 异步处理文档
    try:
        # 仅在需要时导入和使用RAGService
        try:
            from ..services.rag_service import RAGService
        except ImportError:
            from backend.services.rag_service import RAGService
            
        rag_service = RAGService()
        
        # 处理文档（提取文本、分块、向量化）
        chunk_data = rag_service.process_document(doc.file_path, doc.id, kb_id)
        
        # 保存块到数据库
        db = next(get_db())  # 获取数据库会话
        for chunk_info in chunk_data:
            chunk = DocumentChunk(
                doc_id=doc.id,
                content=chunk_info["content"],
                chunk_index=chunk_info["chunk_index"],
                embedding_id=chunk_info["embedding_id"],
                chunk_metadata=chunk_info["metadata"]
            )
            db.add(chunk)
        
        # 更新文档状态
        document_service.update_status(
            doc.id, 
            DocumentStatus.COMPLETED,
            {"chunk_count": len(chunk_data)}
        )
        
    except Exception as e:
        logger.error(f"文档处理失败: doc_id={doc.id}, error={str(e)}", exc_info=True)
        # 处理失败
        document_service.update_status(
            doc.id,
            DocumentStatus.FAILED,
            {"error": str(e)}
        )
        raise HTTPException(status_code=500, detail=f"文档处理失败: {str(e)}")
    
    return doc

@router.get("/{kb_id}/documents", response_model=List[schemas.DocumentResponse])
async def get_documents(
    kb_id: int,
    skip: int = 0,
    limit: int = 100,
    document_service: DocumentService = Depends(get_document_service_dep),
    current_user: User = Depends(get_current_user)
):
    """获取知识库的文档列表"""
    logger.info(f"获取知识库文档列表: kb_id={kb_id}, user_id={current_user.id}, skip={skip}, limit={limit}")
    documents = document_service.get_all_by_kb(kb_id, current_user.id, skip, limit)
    if not documents and skip == 0:
        # 如果是第一页且没有文档，检查知识库是否存在
        kb_service = KnowledgeService(next(get_db()))
        kb = kb_service.get_by_id(kb_id, current_user.id)
        if not kb:
            logger.warning(f"知识库不存在: kb_id={kb_id}")
            raise HTTPException(status_code=404, detail="知识库不存在")
    
    return documents

@router.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: int,
    document_service: DocumentService = Depends(get_document_service_dep),
    current_user: User = Depends(get_current_user)
):
    """删除文档"""
    logger.info(f"删除文档: doc_id={doc_id}, user_id={current_user.id}")
    
    # 获取文档信息（用于后续删除向量数据）
    doc = document_service.get_by_id(doc_id, current_user.id)
    if not doc:
        logger.warning(f"文档不存在: doc_id={doc_id}")
        raise HTTPException(status_code=404, detail="文档不存在")
    
    # 删除向量数据库中的块
    try:
        # 仅在需要时导入和使用RAGService
        try:
            from ..services.rag_service import RAGService
        except ImportError:
            from backend.services.rag_service import RAGService
            
        rag_service = RAGService()
        rag_service.delete_document_chunks(doc_id)
    except Exception as e:
        logger.error(f"删除向量数据失败: doc_id={doc_id}, error={str(e)}")
        # 继续删除文档，即使向量数据删除失败
    
    # 删除文档
    success = document_service.delete(doc_id, current_user.id)
    if not success:
        logger.warning(f"文档删除失败: doc_id={doc_id}")
        raise HTTPException(status_code=500, detail="文档删除失败")
    
    return {"message": "文档删除成功"}

@router.get("/stats")
async def get_knowledge_base_stats(
    knowledge_service: KnowledgeService = Depends(get_knowledge_service_dep),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取知识库统计信息"""
    logger.info(f"获取知识库统计信息: user_id={current_user.id}")
    
    # 数据库统计
    kb_count = db.query(KnowledgeBase).filter(
        KnowledgeBase.created_by == current_user.id
    ).count()
    
    doc_count = db.query(Document).join(KnowledgeBase).filter(
        KnowledgeBase.created_by == current_user.id
    ).count()
    
    chunk_count = db.query(DocumentChunk).join(Document).join(KnowledgeBase).filter(
        KnowledgeBase.created_by == current_user.id
    ).count()
    
    # 向量数据库统计
    try:
        # 仅在需要时导入和使用RAGService
        try:
            from ..services.rag_service import RAGService
        except ImportError:
            from backend.services.rag_service import RAGService
            
        rag_service = RAGService()
        vector_stats = rag_service.get_collection_stats()
    except Exception as e:
        logger.error(f"获取向量数据库统计失败: error={str(e)}")
        vector_stats = {"error": str(e)}
    
    return {
        "knowledge_bases": kb_count,
        "documents": doc_count,
        "chunks": chunk_count,
        "vector_database": vector_stats
    } 