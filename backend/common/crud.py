import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import Optional, List

from models.user import User
from models.role import Role
from models.permission import Permission
from schemas import UserCreate, RoleCreate, PermissionCreate, UserUpdate # 导入相关Schema
from auth.security import get_password_hash, verify_password # 导入密码哈希和验证函数

def get_user_by_username(db: Session, username: str):
    return db.query(User).options(joinedload(User.roles)).filter(User.username == username).first()

# 新增：根据邮箱获取用户
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

# 新增：获取用户列表 (带分页和搜索)
def get_users(db: Session, skip: int = 0, limit: int = 10, search: Optional[str] = None):
    query = db.query(User).options(joinedload(User.roles))
    if search:
        query = query.filter(User.username.ilike(f"%{search}%") | User.email.ilike(f"%{search}%"))
    users = query.offset(skip).limit(limit).all()
    total = query.count()
    return users, total

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password) # 对密码进行哈希
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password, full_name=user.full_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    # 确保roles关系被加载，以便在序列化时不会出现问题
    _ = db_user.roles
    return db_user

# 新增：更新用户
def update_user(db: Session, user_id: int, user_update: UserUpdate):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user: return None
    for key, value in user_update.dict(exclude_unset=True).items(): # 使用dict代替model_dump
        setattr(db_user, key, value)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# 新增：删除用户
def delete_user(db: Session, user_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user: return None
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}

def create_role(db: Session, role: RoleCreate):
    db_role = Role(name=role.name, description=role.description)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    # 确保permissions关系被加载
    _ = db_role.permissions
    return db_role

# 获取角色列表 (带分页和搜索)
def get_roles(db: Session, skip: int = 0, limit: int = 10, search: Optional[str] = None):
    query = db.query(Role).options(joinedload(Role.permissions)).options(joinedload(Role.users))
    if search:
        query = query.filter(Role.name.ilike(f"%{search}%") | Role.description.ilike(f"%{search}%"))
    roles = query.offset(skip).limit(limit).all()
    total = query.count()
    
    # 手动计算userCount
    for role in roles:
        role.userCount = len(role.users)

    return roles, total

# 根据ID获取角色
def get_role_by_id(db: Session, role_id: int):
    role = db.query(Role).filter(Role.id == role_id).first()
    if role:
        # 确保权限关系被加载
        _ = role.permissions
    return role

# 根据名称获取角色
def get_role_by_name(db: Session, role_name: str):
    return db.query(Role).filter(Role.name == role_name).first()

# 更新角色
def update_role(db: Session, role_id: int, role_update):
    db_role = db.query(Role).filter(Role.id == role_id).first()
    if not db_role: return None
    for key, value in role_update.dict(exclude_unset=True).items():
        setattr(db_role, key, value)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

# 删除角色
def delete_role(db: Session, role_id: int):
    db_role = db.query(Role).filter(Role.id == role_id).first()
    if not db_role: return None
    db.delete(db_role)
    db.commit()
    return {"message": "Role deleted successfully"}

# 更新角色权限
def update_role_permissions(db: Session, role_id: int, permission_names: List[str]):
    db_role = db.query(Role).filter(Role.id == role_id).first()
    if not db_role: return None
    
    new_permissions = []
    for permission_name in permission_names:
        permission = get_permission_by_name(db, permission_name)
        if permission:
            new_permissions.append(permission)
    
    db_role.permissions = new_permissions
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

# 获取角色下的用户
def get_users_by_role(db: Session, role_id: int):
    db_role = db.query(Role).filter(Role.id == role_id).first()
    if not db_role: return []
    return db_role.users

# 更新用户角色
def update_user_roles(db: Session, user_id: int, role_names: List[str]):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user: return None
    
    new_roles = []
    for role_name in role_names:
        role = get_role_by_name(db, role_name)
        if role:
            new_roles.append(role)
    
    db_user.roles = new_roles # 直接赋值更新关系
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# 新增：重置用户密码
def reset_user_password(db: Session, user_id: int, new_password: str):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user: return None
    
    db_user.hashed_password = get_password_hash(new_password) # 对新密码进行哈希
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_permission(db: Session, permission: PermissionCreate):
    db_permission = Permission(
        name=permission.name,
        menu_name=permission.menu_name,
        description=permission.description,
        menu_path=permission.menu_path,
        menu_icon=permission.menu_icon,
        parent_id=permission.parent_id,
        sort_order=permission.sort_order
    )
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission

# 新增：获取权限列表 (带分页和搜索)
def get_permissions(db: Session, skip: int = 0, limit: int = 10, search: Optional[str] = None):
    query = db.query(Permission).options(joinedload(Permission.roles))
    if search:
        query = query.filter(Permission.name.ilike(f"%{search}%") | Permission.menu_name.ilike(f"%{search}%"))
    permissions = query.offset(skip).limit(limit).all()
    total = query.count()
    return permissions, total

# 新增：根据ID获取权限
def get_permission_by_id(db: Session, permission_id: int):
    return db.query(Permission).filter(Permission.id == permission_id).first()

# 新增：根据名称获取权限
def get_permission_by_name(db: Session, name: str):
    return db.query(Permission).filter(Permission.name == name).first()

# 新增：更新权限
def update_permission(db: Session, permission_id: int, permission_update: PermissionCreate):
    db_permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not db_permission: return None
    
    # 更新所有字段
    for key, value in permission_update.dict(exclude_unset=True).items():
        setattr(db_permission, key, value)
    
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission

# 新增：删除权限
def delete_permission(db: Session, permission_id: int):
    db_permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not db_permission: return None
    db.delete(db_permission)
    db.commit()
    return {"message": "Permission deleted successfully"} 