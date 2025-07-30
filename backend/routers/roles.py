from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ..config.database import get_db
from ..schemas import Role, RoleCreate, RoleUpdate, RolePermissionUpdate, PaginatedResponse, ApiResponse
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

@router.get("/", response_model=ApiResponse[PaginatedResponse[Role]])
async def get_all_roles(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(check_admin_permission),
    page: int = 1,
    page_size: int = 10,
    search: Optional[str] = None
):
    """获取角色列表"""
    skip = (page - 1) * page_size
    roles, total = crud.get_roles(db, skip=skip, limit=page_size, search=search)
    paginated_response = PaginatedResponse(items=roles, total=total, page=page, pageSize=page_size, totalPages=(total + page_size - 1) // page_size)
    return ApiResponse(success=True, data=paginated_response, message="角色列表获取成功")

@router.get("/{role_id}", response_model=Role)
async def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(check_admin_permission)
):
    """获取单个角色"""
    db_role = crud.get_role_by_id(db, role_id=role_id)
    if db_role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="角色不存在")
    return db_role

@router.post("/", response_model=Role, status_code=status.HTTP_201_CREATED)
async def create_role(
    role: RoleCreate,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(check_admin_permission)
):
    """创建新角色"""
    logger.info(f"尝试创建新角色: name={role.name}")
    try:
        db_role = crud.get_role_by_name(db, name=role.name)
        if db_role:
            logger.warning(f"创建角色失败: 角色名称 '{role.name}' 已存在")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="角色名称已存在")
        
        db_role = crud.create_role(db=db, role=role)
        logger.info(f"角色 '{role.name}' 创建成功")
        return db_role
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"创建角色时发生意外错误: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="创建角色失败")

@router.put("/{role_id}", response_model=Role)
async def update_role(
    role_id: int,
    role_update: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(check_admin_permission)
):
    """更新角色"""
    # 检查是否试图修改admin角色
    db_role = crud.get_role_by_id(db, role_id)
    if db_role and db_role.name == "admin":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="系统管理员角色不允许修改")
    
    db_role = crud.update_role(db, role_id, role_update)
    if db_role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="角色不存在")
    return db_role

@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(check_admin_permission)
):
    """删除角色"""
    # 检查是否试图删除admin角色
    db_role = crud.get_role_by_id(db, role_id)
    if db_role and db_role.name == "admin":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="系统管理员角色不允许删除")
    
    result = crud.delete_role(db, role_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="角色不存在")
    return

@router.put("/{role_id}/permissions", response_model=Role)
async def update_role_permissions(
    role_id: int,
    role_permission_update: RolePermissionUpdate,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(check_admin_permission)
):
    """更新角色权限"""
    db_role = crud.update_role_permissions(db, role_id, role_permission_update.permissions)
    if db_role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="角色不存在")
    return db_role

@router.get("/{role_id}/users", response_model=List[str])
async def get_role_users(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(check_admin_permission)
):
    """获取角色下的用户列表"""
    users = crud.get_users_by_role(db, role_id)
    return [user.username for user in users]