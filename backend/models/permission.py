from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from .base import Base

class Permission(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)  # 权限标识，如 menu:user_management
    menu_name = Column(String(255), nullable=False)  # 菜单名称，如 "用户管理"
    description = Column(Text, nullable=True)  # 权限描述
    menu_path = Column(String(255), nullable=True)  # 菜单路径，如 "/rbac/users"
    menu_icon = Column(String(100), nullable=True)  # 菜单图标
    parent_id = Column(Integer, nullable=True)  # 父菜单ID，支持菜单层级
    sort_order = Column(Integer, default=0)  # 排序
    roles = relationship("Role", secondary="role_permissions", back_populates="permissions") 