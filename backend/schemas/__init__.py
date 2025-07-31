# This file makes the schemas directory a proper Python package
# Re-export all schemas from the main schemas.py file
from backend.schemas.knowledge import *
# Import all schemas from the main schemas.py file
import sys
import os

# Add the parent directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import all schemas from the main schemas.py file
from backend.schemas import (
    UserBase, UserCreate, PermissionBase, PermissionCreate, Permission,
    RoleBase, RoleCreate, RoleUpdate, Role, RolePermissionUpdate,
    User, UserUpdate, UserPasswordReset, UserRoleUpdate, Token,
    PaginatedResponse, ApiResponse
)

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