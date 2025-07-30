from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ..config.database import get_db
from ..schemas import Permission, PermissionCreate, PaginatedResponse, ApiResponse
from ..common import crud
from ..auth.security import get_current_user
from ..models.user import User as DBUser

import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# 权限检查辅助函数
def check_admin_permission(current_user: DBUser = Depends(get_current_user)):
    if "admin" not in [role.name for role in current_user.roles]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您没有管理员权限")
    return current_user

@router.get("/", response_model=ApiResponse[PaginatedResponse[Permission]])
async def get_all_permissions(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(check_admin_permission),
    page: int = 1,
    page_size: int = 10,
    search: Optional[str] = None
):
    """获取权限列表"""
    skip = (page - 1) * page_size
    permissions, total = crud.get_permissions(db, skip=skip, limit=page_size, search=search)
    paginated_response = PaginatedResponse(items=permissions, total=total, page=page, pageSize=page_size, totalPages=(total + page_size - 1) // page_size)
    return ApiResponse(success=True, data=paginated_response, message="权限列表获取成功")

@router.get("/{permission_id}", response_model=Permission)
async def get_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(check_admin_permission)
):
    """获取单个权限"""
    db_permission = crud.get_permission_by_id(db, permission_id=permission_id)
    if db_permission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="权限不存在")
    return db_permission

@router.post("/", response_model=Permission, status_code=status.HTTP_201_CREATED)
async def create_permission(
    permission: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(check_admin_permission)
):
    """创建新权限"""
    logger.info(f"尝试创建新权限: name={permission.name}")
    try:
        db_permission = crud.get_permission_by_name(db, name=permission.name)
        if db_permission:
            logger.warning(f"创建权限失败: 权限名称 '{permission.name}' 已存在")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="权限名称已存在")
        
        db_permission = crud.create_permission(db=db, permission=permission)
        logger.info(f"权限 '{permission.name}' 创建成功")
        return db_permission
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"创建权限时发生意外错误: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="创建权限失败")

@router.put("/{permission_id}", response_model=Permission)
async def update_permission(
    permission_id: int,
    permission_update: PermissionCreate,  # 复用PermissionCreate，因为只有name字段
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(check_admin_permission)
):
    """更新权限"""
    db_permission = crud.update_permission(db, permission_id, permission_update)
    if db_permission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="权限不存在")
    return db_permission

@router.delete("/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(check_admin_permission)
):
    """删除权限"""
    result = crud.delete_permission(db, permission_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="权限不存在")
    return