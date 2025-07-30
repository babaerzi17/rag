# 导入所有模型以确保它们被正确注册
from .base import Base
from .associations import user_roles, role_permissions
from .user import User
from .role import Role  
from .permission import Permission

__all__ = ["Base", "User", "Role", "Permission", "user_roles", "role_permissions"] 