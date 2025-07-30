from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os

from pydantic import BaseModel # 导入BaseModel

# 确保导入路径正确
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from ..config.database import get_db
    from ..schemas import Token, User
    from ..auth.security import (create_access_token, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES, 
                                get_current_user, REMEMBER_ME_TOKEN_EXPIRE_DAYS)
    from ..models.user import User as DBUser
    from ..common.crud import authenticate_user # 导入authenticate_user
except ImportError:
    # 尝试使用绝对导入
    from backend.config.database import get_db
    from backend.schemas import Token, User
    from backend.auth.security import (create_access_token, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES, 
                                    get_current_user, REMEMBER_ME_TOKEN_EXPIRE_DAYS)
    from backend.models.user import User as DBUser
    from backend.common.crud import authenticate_user # 导入authenticate_user

import logging
from datetime import timedelta

logger = logging.getLogger(__name__)

router = APIRouter()

# 新增一个用于登录请求的Pydantic模型
class LoginForm(BaseModel):
    username: str
    password: str
    remember_me: bool = False # 新增remember_me字段，默认False

@router.post("/token", response_model=Token)
async def login_for_access_token(
    username: str = Form(...),
    password: str = Form(...),
    remember_me: bool = Form(False),
    db: Session = Depends(get_db)
):
    logger.info(f"尝试为用户 '{username}' 获取access token")
    user = authenticate_user(db, username, password)
    if not user:
        logger.warning(f"用户 '{username}' 认证失败")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码不正确",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 确保用户角色被加载
    _ = user.roles

    # 根据remember_me设置过期时间
    access_token_expires = None
    if remember_me:
        access_token_expires = timedelta(days=REMEMBER_ME_TOKEN_EXPIRE_DAYS)
    else:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(
        data={"sub": user.username, "id": user.id, "roles": [role.name for role in user.roles]},
        expires_delta=access_token_expires,
        remember_me=remember_me # 传递remember_me状态
    )
    logger.info(f"用户 '{username}' access token创建成功")
    
    # 确保用户角色被正确序列化
    user_dict = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "roles": [{"id": role.id, "name": role.name, "description": role.description} for role in user.roles],
        "permissions": []  # 添加空的权限列表以匹配前端期望
    }
    
    logger.info(f"返回用户信息: {user_dict}")
    return {"access_token": access_token, "token_type": "bearer", "user": user_dict}

@router.get("/user-permissions")
async def get_user_permissions(
    username: str,
    db: Session = Depends(get_db)
):
    """获取用户权限列表"""
    logger.info(f"获取用户权限: username={username}")
    # 从数据库中获取用户权限
    try:
        from ..common.crud import get_user_by_username
    except ImportError:
        from backend.common.crud import get_user_by_username
        
    user = get_user_by_username(db, username)
    if not user:
        logger.warning(f"用户不存在: username={username}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    
    # 获取用户所有角色的权限列表
    permissions = set()
    for role in user.roles:
        for perm in role.permissions:
            permissions.add(perm.name)
            
    return list(permissions)

@router.get("/me", response_model=User)
async def read_users_me(current_user: DBUser = Depends(get_current_user)):
    logger.info(f"获取当前用户信息: {current_user.username}")
    return current_user

# 辅助路由，用于测试当前用户及其权限
@router.get("/test_current_user_from_db", response_model=User)
async def get_current_user_from_db(current_user: DBUser = Depends(get_current_user)):
    logger.info(f"测试路由：获取当前用户（从数据库加载完整信息）: {current_user.username}")
    # 确保roles和permissions关系被加载
    _ = current_user.roles
    _ = current_user.permissions
    return current_user