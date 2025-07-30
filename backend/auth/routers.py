import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from common import crud # 导入 crud 模块
from models.role import Role # 导入 Role 模型
from models.permission import Permission # 导入 Permission 模型
from schemas import Token, User # 导入 Token 和 User Schema
from config.database import get_db
from auth.security import create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES # 导入安全相关的函数和常量

router = APIRouter()

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "user": user}

@router.get("/user-permissions", response_model=list[str])
async def get_user_permissions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    permissions = set()
    # 假设 User 模型有 roles 属性，Role 模型有 permissions 属性
    # 并且 permission 对象有 name 属性
    if current_user and current_user.roles:
        for role in current_user.roles:
            if role.permissions:
                for perm in role.permissions:
                    if perm.name.startswith('menu:'):
                        permissions.add(perm.name)
    return list(permissions)

@router.post("/assign-role-permission")
async def assign_role_permission(role_name: str, permission_name: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 简单的权限检查，确保只有管理员可以分配权限
    if "admin" not in [role.name for role in current_user.roles]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    role = db.query(Role).filter(Role.name == role_name).first()
    permission = db.query(Permission).filter(Permission.name == permission_name).first()

    if not role or not permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role or Permission not found")

    # 检查是否已存在此关联
    if permission in role.permissions:
        return {"message": f"Permission {permission_name} already assigned to role {role_name}"}

    role.permissions.append(permission)
    db.add(role)
    db.commit()
    db.refresh(role)
    return {"message": f"Permission {permission_name} assigned to role {role_name}"} 