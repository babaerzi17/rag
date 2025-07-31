# This file makes the schemas directory a proper Python package
# Re-export all schemas from both the main schemas.py file and knowledge schemas

# Import knowledge schemas from this package
from .knowledge import *

# Define all user/auth related schemas directly here to avoid import issues
from pydantic import BaseModel
from typing import List, Optional, Generic, TypeVar

T = TypeVar('T')

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str
    full_name: Optional[str] = None

class PermissionBase(BaseModel):
    name: str
    menu_name: str
    description: Optional[str] = None
    menu_path: Optional[str] = None
    menu_icon: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: Optional[int] = 0

class PermissionCreate(PermissionBase):
    pass

class Permission(PermissionBase):
    id: int

    class Config:
        from_attributes = True

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class Role(RoleBase):
    id: int
    permissions: List['Permission'] = [] # 添加权限列表，使其成为完整角色模型

    class Config:
        from_attributes = True

# 新增角色权限更新Schema
class RolePermissionUpdate(BaseModel):
    permissions: List[str]  # 权限name列表

class User(UserBase):
    id: int
    is_active: bool
    full_name: Optional[str] = None
    roles: List[Role] = [] # 添加角色列表

    class Config:
        from_attributes = True

# 新增UserUpdate Schema
class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

# 新增UserPasswordReset Schema
class UserPasswordReset(BaseModel):
    new_password: str

# 新增UserRoleUpdate Schema，用于更新用户角色
class UserRoleUpdate(BaseModel):
    roles: List[str]

class Token(BaseModel):
    access_token: str
    token_type: str
    user: Optional[User] = None

# 新增 PaginatedResponse Schema
class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    pageSize: int
    totalPages: int

# 新增通用API响应Schema
class ApiResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    message: Optional[str] = None
    code: Optional[str] = None

# 在所有相关模型定义完成后调用 update_forward_refs()，以确保前向引用被正确解析
Role.update_forward_refs()
User.update_forward_refs()

# Re-export all schemas
__all__ = [
    'UserBase', 'UserCreate', 'PermissionBase', 'PermissionCreate', 'Permission',
    'RoleBase', 'RoleCreate', 'RoleUpdate', 'Role', 'RolePermissionUpdate',
    'User', 'UserUpdate', 'UserPasswordReset', 'UserRoleUpdate', 'Token',
    'PaginatedResponse', 'ApiResponse',
    # Knowledge schemas
    'KnowledgeBaseStatus', 'DocumentStatus', 'KnowledgeBaseBase', 'KnowledgeBaseCreate',
    'KnowledgeBaseUpdate', 'KnowledgeBaseResponse', 'DocumentBase', 'DocumentCreate',
    'DocumentUpdate', 'DocumentResponse', 'DocumentChunkBase', 'DocumentChunkCreate',
    'DocumentChunkResponse'
] 