from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models.base import Base
from models.user import User
from models.role import Role
from models.permission import Permission
from models.knowledge import (
    KnowledgeBase, 
    Document, 
    DocumentChunk, 
    ChatSession, 
    ChatMessage, 
    ModelConfig
)
from config.database import DATABASE_URL
import os

def init_database():
    """初始化数据库"""
    # 创建引擎
    engine = create_engine(DATABASE_URL)
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    # 创建会话
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 检查是否已经初始化
        existing_permissions = db.query(Permission).count()
        if existing_permissions > 0:
            print("数据库已经初始化，跳过...")
            return
        
        # 创建权限
        permissions_data = [
            # 菜单权限
            {"name": "menu:auth"},
            {"name": "menu:knowledge"},
            {"name": "menu:document"},
            {"name": "menu:chat"},
            {"name": "menu:model"},
            {"name": "menu:settings"},
            {"name": "menu:rbac_user"},
            {"name": "menu:rbac_role"},
            {"name": "menu:rbac_perm"},
            
            # 功能权限
            {"name": "knowledge.library.read"},
            {"name": "knowledge.library.create"},
            {"name": "knowledge.library.update"},
            {"name": "knowledge.library.delete"},
            
            {"name": "document.read"},
            {"name": "document.create"},
            {"name": "document.update"},
            {"name": "document.delete"},
            
            {"name": "chat.use"},
            {"name": "chat.history.read"},
            {"name": "chat.history.delete"},
            
            {"name": "model.manage"},
            {"name": "model.config.read"},
            {"name": "model.config.create"},
            {"name": "model.config.update"},
            {"name": "model.config.delete"},
            
            {"name": "rbac.read"},
            {"name": "rbac.user.read"},
            {"name": "rbac.user.create"},
            {"name": "rbac.user.update"},
            {"name": "rbac.user.delete"},
            {"name": "rbac.role.read"},
            {"name": "rbac.role.create"},
            {"name": "rbac.role.update"},
            {"name": "rbac.role.delete"},
            {"name": "rbac.permission.read"},
            {"name": "rbac.permission.create"},
            {"name": "rbac.permission.update"},
            {"name": "rbac.permission.delete"},
            
            {"name": "settings.read"},
            {"name": "settings.update"},
        ]
        
        for perm_data in permissions_data:
            permission = Permission(**perm_data)
            db.add(permission)
        
        # 创建角色
        roles_data = [
            {"name": "admin"},
            {"name": "user"},
            {"name": "guest"}
        ]
        
        for role_data in roles_data:
            role = Role(**role_data)
            db.add(role)
        
        db.commit()
        
        # 获取角色和权限
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        user_role = db.query(Role).filter(Role.name == "user").first()
        guest_role = db.query(Role).filter(Role.name == "guest").first()
        
        all_permissions = db.query(Permission).all()
        user_permissions = db.query(Permission).filter(
            Permission.name.in_([
                "menu:knowledge", "menu:document", "menu:chat", "menu:settings",
                "knowledge.library.read", "document.read", "chat.use", "settings.read"
            ])
        ).all()
        guest_permissions = db.query(Permission).filter(
            Permission.name.in_([
                "menu:chat", "chat.use"
            ])
        ).all()
        
        # 分配权限给角色
        # Admin角色获得所有权限
        for permission in all_permissions:
            admin_role.permissions.append(permission)
        
        # User角色获得基本权限
        for permission in user_permissions:
            user_role.permissions.append(permission)
        
        # Guest角色获得有限权限
        for permission in guest_permissions:
            guest_role.permissions.append(permission)
        
        # 创建默认管理员用户
        from utils.init_password import get_password_hash
        
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("Admin.123"),
            full_name="系统管理员",
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        
        # 分配admin角色给管理员用户
        admin_user.roles.append(admin_role)
        
        # 创建默认模型配置
        default_models = [
            {
                "name": "DeepSeek Chat",
                "provider": "deepseek",
                "model_name": "deepseek-chat",
                "is_default": True,
                "config": {"temperature": 0.7, "max_tokens": 1000}
            },
            {
                "name": "OpenAI GPT-3.5",
                "provider": "openai",
                "model_name": "gpt-3.5-turbo",
                "is_default": False,
                "config": {"temperature": 0.7, "max_tokens": 1000}
            }
        ]
        
        for model_data in default_models:
            model_config = ModelConfig(**model_data)
            db.add(model_config)
        
        db.commit()
        print("数据库初始化完成！")
        print("默认管理员账户: admin / Admin.123")
        
    except Exception as e:
        db.rollback()
        print(f"数据库初始化失败: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database() 