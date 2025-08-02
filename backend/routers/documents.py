from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
import os
import shutil
import sys
from datetime import datetime
import json

# Ensure import paths are correct
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from ..database import get_db
    from ..models.knowledge import KnowledgeBase, Document, DocumentChunk, DocumentStatus
    from ..models.user import User
    from ..auth.security import get_current_user
    from ..schemas.knowledge import DocumentResponse, DocumentCreate, DocumentUpdate
    from ..services.document_service import DocumentService
    from ..logger import get_logger
except ImportError:
    from backend.database import get_db
    from backend.models.knowledge import KnowledgeBase, Document, DocumentChunk, DocumentStatus
    from backend.models.user import User
    from backend.auth.security import get_current_user
    from backend.schemas.knowledge import DocumentResponse, DocumentCreate, DocumentUpdate
    from backend.services.document_service import DocumentService
    from backend.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

# 依赖函数：获取文档服务
def get_document_service_dep(db: Session = Depends(get_db)) -> DocumentService:
    return DocumentService(db)

@router.get("/", response_model=List[DocumentResponse])
async def get_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    kb_id: Optional[int] = Query(None),
    file_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    document_service: DocumentService = Depends(get_document_service_dep),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取文档列表，支持分页和筛选"""
    logger.info(f"获取文档列表: user_id={current_user.id}, page={page}, page_size={page_size}")
    
    # 构建查询
    query = db.query(Document).join(KnowledgeBase, Document.knowledge_base_id == KnowledgeBase.id)
    
    # 只显示用户的文档
    query = query.filter(KnowledgeBase.created_by == current_user.id)
    
    # 按知识库筛选
    if kb_id:
        query = query.filter(Document.knowledge_base_id == kb_id)
    
    # 按文件类型筛选
    if file_type:
        query = query.filter(Document.file_type == file_type)
    
    # 按状态筛选
    if status:
        query = query.filter(Document.status == status)
    
    # 搜索
    if search:
        query = query.filter(Document.title.contains(search))
    
    # 分页
    skip = (page - 1) * page_size
    documents = query.offset(skip).limit(page_size).all()
    
    return [DocumentResponse.from_orm(doc) for doc in documents]

@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: int,
    document_service: DocumentService = Depends(get_document_service_dep),
    current_user: User = Depends(get_current_user)
):
    """获取文档详情"""
    logger.info(f"获取文档详情: doc_id={doc_id}, user_id={current_user.id}")
    
    document = document_service.get_by_id(doc_id, current_user.id)
    if not document:
        logger.warning(f"文档不存在: doc_id={doc_id}")
        raise HTTPException(status_code=404, detail="文档不存在")
    
    return document

@router.post("/", response_model=DocumentResponse)
async def create_document(
    kb_id: int = Form(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    file: UploadFile = File(...),
    document_service: DocumentService = Depends(get_document_service_dep),
    current_user: User = Depends(get_current_user)
):
    """创建文档（上传单个文件）"""
    logger.info(f"创建文档: kb_id={kb_id}, user_id={current_user.id}, file_name={file.filename}")
    
    # 验证知识库存在
    db = next(get_db())
    kb = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == kb_id,
        KnowledgeBase.created_by == current_user.id
    ).first()
    
    if not kb:
        logger.warning(f"知识库不存在: kb_id={kb_id}")
        raise HTTPException(status_code=404, detail="知识库不存在")
    
    # 上传文档
    document = await document_service.upload(kb_id, current_user.id, file)
    if not document:
        logger.warning(f"文件上传失败: file_name={file.filename}")
        raise HTTPException(status_code=400, detail="文件上传失败或文件类型不支持")
    
    # 更新标题和描述
    if title != file.filename:
        document_service.update_metadata(document.id, {"title": title})
    
    if description:
        document_service.update_metadata(document.id, {"description": description})
    
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        document_service.update_metadata(document.id, {"tags": tag_list})
    
    return document

@router.put("/{doc_id}", response_model=DocumentResponse)
async def update_document(
    doc_id: int,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    document_service: DocumentService = Depends(get_document_service_dep),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新文档信息"""
    logger.info(f"更新文档: doc_id={doc_id}, user_id={current_user.id}")
    
    # 验证文档存在且属于用户
    document = (
        db.query(Document)
        .join(KnowledgeBase, Document.knowledge_base_id == KnowledgeBase.id)
        .filter(Document.id == doc_id, KnowledgeBase.created_by == current_user.id)
        .first()
    )
    
    if not document:
        logger.warning(f"文档不存在: doc_id={doc_id}")
        raise HTTPException(status_code=404, detail="文档不存在")
    
    # 更新字段
    update_data = {}
    if title is not None:
        document.title = title
        update_data["title"] = title
    
    if description is not None:
        update_data["description"] = description
    
    if tags is not None:
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        update_data["tags"] = tag_list
    
    # 更新元数据
    if update_data:
        current_metadata = document.doc_metadata or {}
        current_metadata.update(update_data)
        document.doc_metadata = current_metadata
    
    db.commit()
    db.refresh(document)
    
    return DocumentResponse.from_orm(document)

@router.delete("/{doc_id}")
async def delete_document(
    doc_id: int,
    document_service: DocumentService = Depends(get_document_service_dep),
    current_user: User = Depends(get_current_user)
):
    """删除文档"""
    logger.info(f"删除文档: doc_id={doc_id}, user_id={current_user.id}")
    
    success = document_service.delete(doc_id, current_user.id)
    if not success:
        logger.warning(f"文档删除失败: doc_id={doc_id}")
        raise HTTPException(status_code=404, detail="文档不存在或删除失败")
    
    return {"message": "文档删除成功"}

@router.post("/batch-upload", response_model=List[DocumentResponse])
async def batch_upload_documents(
    kb_id: int = Form(...),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    files: List[UploadFile] = File(...),
    document_service: DocumentService = Depends(get_document_service_dep),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """批量上传文档"""
    logger.info(f"批量上传文档: kb_id={kb_id}, user_id={current_user.id}, file_count={len(files)}")
    
    # 验证知识库存在
    kb = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == kb_id,
        KnowledgeBase.created_by == current_user.id
    ).first()
    
    if not kb:
        logger.warning(f"知识库不存在: kb_id={kb_id}")
        raise HTTPException(status_code=404, detail="知识库不存在")
    
    uploaded_documents = []
    failed_files = []
    
    for file in files:
        try:
            document = await document_service.upload(kb_id, current_user.id, file)
            if document:
                # 添加元数据
                metadata = {}
                if description:
                    metadata["description"] = description
                if tags:
                    tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
                    metadata["tags"] = tag_list
                
                if metadata:
                    document_service.update_metadata(document.id, metadata)
                
                uploaded_documents.append(document)
            else:
                failed_files.append(file.filename)
        except Exception as e:
            logger.error(f"文件上传失败: {file.filename}, error={str(e)}")
            failed_files.append(file.filename)
    
    if failed_files:
        logger.warning(f"部分文件上传失败: {failed_files}")
        # 可以选择抛出异常或返回部分成功的结果
    
    return uploaded_documents

@router.post("/import-from-directory")
async def import_from_directory(
    kb_id: int = Form(...),
    directory_path: str = Form(...),
    recursive: bool = Form(False),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    document_service: DocumentService = Depends(get_document_service_dep),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """从指定目录导入文档"""
    logger.info(f"从目录导入文档: kb_id={kb_id}, directory={directory_path}, user_id={current_user.id}")
    
    # 验证知识库存在
    kb = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == kb_id,
        KnowledgeBase.created_by == current_user.id
    ).first()
    
    if not kb:
        logger.warning(f"知识库不存在: kb_id={kb_id}")
        raise HTTPException(status_code=404, detail="知识库不存在")
    
    # 检查目录是否存在
    if not os.path.exists(directory_path):
        logger.warning(f"目录不存在: {directory_path}")
        raise HTTPException(status_code=404, detail="目录不存在")
    
    # 支持的文件扩展名
    allowed_extensions = {'.txt', '.pdf', '.doc', '.docx', '.md', '.ppt', '.pptx', '.xls', '.xlsx'}
    
    imported_files = []
    failed_files = []
    
    # 遍历目录
    if recursive:
        for root, dirs, files in os.walk(directory_path):
            for filename in files:
                file_path = os.path.join(root, filename)
                ext = os.path.splitext(filename)[1].lower()
                
                if ext in allowed_extensions:
                    try:
                        success = await import_single_file(
                            file_path, kb_id, current_user.id, 
                            document_service, description, tags
                        )
                        if success:
                            imported_files.append(filename)
                        else:
                            failed_files.append(filename)
                    except Exception as e:
                        logger.error(f"导入文件失败: {filename}, error={str(e)}")
                        failed_files.append(filename)
    else:
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            if os.path.isfile(file_path):
                ext = os.path.splitext(filename)[1].lower()
                
                if ext in allowed_extensions:
                    try:
                        success = await import_single_file(
                            file_path, kb_id, current_user.id, 
                            document_service, description, tags
                        )
                        if success:
                            imported_files.append(filename)
                        else:
                            failed_files.append(filename)
                    except Exception as e:
                        logger.error(f"导入文件失败: {filename}, error={str(e)}")
                        failed_files.append(filename)
    
    return {
        "message": f"导入完成，成功: {len(imported_files)}, 失败: {len(failed_files)}",
        "imported_files": imported_files,
        "failed_files": failed_files
    }

async def import_single_file(
    file_path: str, 
    kb_id: int, 
    user_id: int, 
    document_service: DocumentService,
    description: Optional[str] = None,
    tags: Optional[str] = None
) -> bool:
    """导入单个文件"""
    try:
        # 读取文件内容
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        filename = os.path.basename(file_path)
        
        # 创建临时UploadFile对象
        class TempUploadFile:
            def __init__(self, filename: str, content: bytes):
                self.filename = filename
                self.content = content
                self.size = len(content)
            
            async def read(self):
                return self.content
        
        temp_file = TempUploadFile(filename, file_content)
        
        # 上传文档
        document = await document_service.upload(kb_id, user_id, temp_file)
        
        if document:
            # 添加元数据
            metadata = {}
            if description:
                metadata["description"] = description
            if tags:
                tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
                metadata["tags"] = tag_list
            
            if metadata:
                document_service.update_metadata(document.id, metadata)
            
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"导入文件失败: {file_path}, error={str(e)}")
        return False

@router.delete("/batch")
async def batch_delete_documents(
    doc_ids: List[int],
    document_service: DocumentService = Depends(get_document_service_dep),
    current_user: User = Depends(get_current_user)
):
    """批量删除文档"""
    logger.info(f"批量删除文档: doc_ids={doc_ids}, user_id={current_user.id}")
    
    deleted_count = 0
    failed_count = 0
    
    for doc_id in doc_ids:
        try:
            success = document_service.delete(doc_id, current_user.id)
            if success:
                deleted_count += 1
            else:
                failed_count += 1
        except Exception as e:
            logger.error(f"删除文档失败: doc_id={doc_id}, error={str(e)}")
            failed_count += 1
    
    return {
        "message": f"批量删除完成，成功: {deleted_count}, 失败: {failed_count}",
        "deleted_count": deleted_count,
        "failed_count": failed_count
    }

@router.get("/stats")
async def get_document_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取文档统计信息"""
    logger.info(f"获取文档统计: user_id={current_user.id}")
    
    # 总文档数
    total_documents = (
        db.query(Document)
        .join(KnowledgeBase, Document.knowledge_base_id == KnowledgeBase.id)
        .filter(KnowledgeBase.created_by == current_user.id)
        .count()
    )
    
    # 按状态统计
    status_stats = {}
    for status in ['processing', 'completed', 'failed', 'pending']:
        count = (
            db.query(Document)
            .join(KnowledgeBase, Document.knowledge_base_id == KnowledgeBase.id)
            .filter(
                KnowledgeBase.created_by == current_user.id,
                Document.status == status
            )
            .count()
        )
        status_stats[status] = count
    
    # 按类型统计
    type_stats = {}
    types = db.query(Document.file_type).join(
        KnowledgeBase, Document.knowledge_base_id == KnowledgeBase.id
    ).filter(KnowledgeBase.created_by == current_user.id).distinct().all()
    
    for (file_type,) in types:
        if file_type:
            count = (
                db.query(Document)
                .join(KnowledgeBase, Document.knowledge_base_id == KnowledgeBase.id)
                .filter(
                    KnowledgeBase.created_by == current_user.id,
                    Document.file_type == file_type
                )
                .count()
            )
            type_stats[file_type] = count
    
    # 总文件大小
    total_size = (
        db.query(func.sum(Document.file_size))
        .join(KnowledgeBase, Document.knowledge_base_id == KnowledgeBase.id)
        .filter(KnowledgeBase.created_by == current_user.id)
        .scalar()
    ) or 0
    
    return {
        "total_documents": total_documents,
        "total_size": total_size,
        "by_status": status_stats,
        "by_type": type_stats
    } 