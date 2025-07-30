from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ..config.database import get_db
from ..schemas import User, UserCreate, UserUpdate, UserPasswordReset, PaginatedResponse, ApiResponse, UserRoleUpdate # 导入PaginatedResponse和ApiResponse, UserRoleUpdate
from ..common import crud
from ..auth.security import get_current_user # 导入get_current_user
from ..models.user import User as DBUser # 导入数据库User模型

import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# 权限检查辅助函数
def check_admin_permission(current_user: DBUser = Depends(get_current_user)):
    if "admin" not in [role.name for role in current_user.roles]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您没有管理员权限")
    return current_user

@router.get("/", response_model=ApiResponse[PaginatedResponse[User]]) # 修改返回模型为ApiResponse封装PaginatedResponse
async def get_all_users(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(check_admin_permission), # 添加管理员权限检查
    page: int = 1,
    page_size: int = 10,
    search: Optional[str] = None
):
    """获取用户列表"""
    skip = (page - 1) * page_size
    users, total = crud.get_users(db, skip=skip, limit=page_size, search=search)
    paginated_response = PaginatedResponse(items=users, total=total, page=page, pageSize=page_size, totalPages=(total + page_size - 1) // page_size)
    return ApiResponse(success=True, data=paginated_response, message="用户列表获取成功") # 封装在ApiResponse中

@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(check_admin_permission) # 添加管理员权限检查
):
    """获取单个用户"""
    db_user = crud.get_user_by_id(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    return db_user

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(check_admin_permission) # 添加管理员权限检查
):
    """创建新用户"""
    logger.info(f"尝试创建新用户: username={user.username}, email={user.email}, full_name={user.full_name}")
    try:
        db_user = crud.get_user_by_username(db, username=user.username)
        if db_user: # 检查用户名是否已存在
            logger.warning(f"创建用户失败: 用户名 '{user.username}' 已存在")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")

        db_user = crud.get_user_by_email(db, email=user.email)
        if db_user: # 检查邮箱是否已存在
            logger.warning(f"创建用户失败: 邮箱 '{user.email}' 已存在")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱已存在")
        
        db_user = crud.create_user(db=db, user=user)
        logger.info(f"用户 '{user.username}' 创建成功")
        return db_user
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"创建用户时发生意外错误: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="创建用户失败")

@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(check_admin_permission) # 添加管理员权限检查
):
    """更新用户"""
    db_user = crud.update_user(db, user_id, user_update)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    return db_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(check_admin_permission) # 添加管理员权限检查
):
    """删除用户"""
    db_user = crud.get_user_by_id(db, user_id) # 获取要删除的用户对象
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    
    if db_user.username == "admin": # 新增：禁止删除admin账户
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="系统管理员账户不允许删除")

    result = crud.delete_user(db, user_id)
    if result is None: # 如果用户不存在，crud.delete_user会返回None
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    return # 204 No Content 不需要返回体

@router.put("/{user_id}/roles", response_model=User)
async def update_user_roles(
    user_id: int,
    user_role_update: UserRoleUpdate, # 修改为接收UserRoleUpdate Schema
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(check_admin_permission) # 添加管理员权限检查
):
    """更新用户角色"""
    db_user = crud.update_user_roles(db, user_id, user_role_update.roles) # 传递roles列表
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    # 检查所有角色名称是否存在
    for role_name in user_role_update.roles: # 遍历user_role_update.roles
        if not crud.get_role_by_name(db, role_name):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"角色 '{role_name}' 不存在")
    return db_user

@router.post("/{user_id}/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_user_password(
    user_id: int,
    password_reset: UserPasswordReset,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(check_admin_permission) # 添加管理员权限检查
):
    """重置用户密码"""
    result = crud.reset_user_password(db, user_id, password_reset.new_password)
    if result is None: # 如果用户不存在，crud.reset_user_password会返回None
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    return # 204 No Content 不需要返回体