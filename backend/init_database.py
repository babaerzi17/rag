#!/usr/bin/env python3
"""
数据库初始化脚本
创建所有表结构和初始数据
"""

import os
import sys
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config.database import DATABASE_URL
from backend.models.base import Base
from backend.models.user import User
from backend.models.role import Role
from backend.models.permission import Permission
from backend.models.associations import user_roles, role_permissions
from backend.models.knowledge import KnowledgeBase, Document, DocumentChunk, ChatSession, ChatMessage, ModelConfig
from backend.models.ab_testing import ABTest, ABTestSession, ABTestInteraction, ABTestMetric, TestQuestion, QuestionEvaluation
from backend.models.system import SystemLog, SystemBackup, SystemMetric, PerformanceMetric, ModelUsageMetric, SystemConfig, ServiceHealth, SystemAlert
from backend.utils.init_password import get_password_hash

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseInitializer:
    def __init__(self, database_url: str = None):
        self.database_url = database_url or DATABASE_URL
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def create_tables(self):
        """创建所有表"""
        try:
            logger.info("开始创建数据库表...")
            Base.metadata.create_all(bind=self.engine)
            logger.info("数据库表创建完成")
            return True
        except Exception as e:
            logger.error(f"创建表失败: {e}")
            return False
    
    def drop_tables(self):
        """删除所有表"""
        try:
            logger.info("开始删除数据库表...")
            Base.metadata.drop_all(bind=self.engine)
            logger.info("数据库表删除完成")
            return True
        except Exception as e:
            logger.error(f"删除表失败: {e}")
            return False
    
    def init_permissions(self):
        """初始化权限数据"""
        try:
            session = self.SessionLocal()
            
            # 检查是否已有权限数据
            if session.query(Permission).count() > 0:
                logger.info("权限数据已存在，跳过初始化")
                session.close()
                return True
            
            # 定义权限
            permissions = [
                # 用户管理权限
                {"name": "user.view", "description": "查看用户", "category": "用户管理"},
                {"name": "user.create", "description": "创建用户", "category": "用户管理"},
                {"name": "user.edit", "description": "编辑用户", "category": "用户管理"},
                {"name": "user.delete", "description": "删除用户", "category": "用户管理"},
                
                # 角色管理权限
                {"name": "role.view", "description": "查看角色", "category": "角色管理"},
                {"name": "role.create", "description": "创建角色", "category": "角色管理"},
                {"name": "role.edit", "description": "编辑角色", "category": "角色管理"},
                {"name": "role.delete", "description": "删除角色", "category": "角色管理"},
                
                # 权限管理权限
                {"name": "permission.view", "description": "查看权限", "category": "权限管理"},
                {"name": "permission.create", "description": "创建权限", "category": "权限管理"},
                {"name": "permission.edit", "description": "编辑权限", "category": "权限管理"},
                {"name": "permission.delete", "description": "删除权限", "category": "权限管理"},
                
                # 知识库管理权限
                {"name": "knowledge.view", "description": "查看知识库", "category": "知识库管理"},
                {"name": "knowledge.create", "description": "创建知识库", "category": "知识库管理"},
                {"name": "knowledge.edit", "description": "编辑知识库", "category": "知识库管理"},
                {"name": "knowledge.delete", "description": "删除知识库", "category": "知识库管理"},
                {"name": "knowledge.upload", "description": "上传文档", "category": "知识库管理"},
                
                # 文档管理权限
                {"name": "document.view", "description": "查看文档", "category": "文档管理"},
                {"name": "document.create", "description": "创建文档", "category": "文档管理"},
                {"name": "document.edit", "description": "编辑文档", "category": "文档管理"},
                {"name": "document.delete", "description": "删除文档", "category": "文档管理"},
                
                # 聊天权限
                {"name": "chat.view", "description": "查看聊天", "category": "聊天管理"},
                {"name": "chat.create", "description": "创建聊天", "category": "聊天管理"},
                {"name": "chat.edit", "description": "编辑聊天", "category": "聊天管理"},
                {"name": "chat.delete", "description": "删除聊天", "category": "聊天管理"},
                
                # 模型管理权限
                {"name": "model.view", "description": "查看模型", "category": "模型管理"},
                {"name": "model.create", "description": "创建模型", "category": "模型管理"},
                {"name": "model.edit", "description": "编辑模型", "category": "模型管理"},
                {"name": "model.delete", "description": "删除模型", "category": "模型管理"},
                {"name": "model.test", "description": "测试模型", "category": "模型管理"},
                
                # AB测试权限
                {"name": "ab-testing.view", "description": "查看AB测试", "category": "AB测试管理"},
                {"name": "ab-testing.create", "description": "创建AB测试", "category": "AB测试管理"},
                {"name": "ab-testing.edit", "description": "编辑AB测试", "category": "AB测试管理"},
                {"name": "ab-testing.delete", "description": "删除AB测试", "category": "AB测试管理"},
                {"name": "ab-testing.manage", "description": "管理AB测试", "category": "AB测试管理"},
                
                # 系统管理权限
                {"name": "system.view", "description": "查看系统", "category": "系统管理"},
                {"name": "system.config", "description": "配置系统", "category": "系统管理"},
                {"name": "system.backup", "description": "备份系统", "category": "系统管理"},
                {"name": "system.restore", "description": "恢复系统", "category": "系统管理"},
                {"name": "system.log", "description": "查看日志", "category": "系统管理"},
                {"name": "system.monitor", "description": "系统监控", "category": "系统管理"},
            ]
            
            # 创建权限
            for perm_data in permissions:
                permission = Permission(**perm_data)
                session.add(permission)
            
            session.commit()
            logger.info(f"权限初始化完成，共创建 {len(permissions)} 个权限")
            session.close()
            return True
            
        except Exception as e:
            logger.error(f"权限初始化失败: {e}")
            session.rollback()
            session.close()
            return False
    
    def init_roles(self):
        """初始化角色数据"""
        try:
            session = self.SessionLocal()
            
            # 检查是否已有角色数据
            if session.query(Role).count() > 0:
                logger.info("角色数据已存在，跳过初始化")
                session.close()
                return True
            
            # 获取所有权限
            permissions = session.query(Permission).all()
            permission_map = {perm.name: perm for perm in permissions}
            
            # 定义角色
            roles = [
                {
                    "name": "超级管理员",
                    "description": "拥有所有权限的超级管理员",
                    "permissions": list(permission_map.keys())  # 所有权限
                },
                {
                    "name": "系统管理员",
                    "description": "系统管理权限",
                    "permissions": [
                        "system.view", "system.config", "system.backup", 
                        "system.restore", "system.log", "system.monitor",
                        "user.view", "user.create", "user.edit", "user.delete",
                        "role.view", "role.create", "role.edit", "role.delete",
                        "permission.view", "permission.create", "permission.edit", "permission.delete"
                    ]
                },
                {
                    "name": "知识库管理员",
                    "description": "知识库和文档管理权限",
                    "permissions": [
                        "knowledge.view", "knowledge.create", "knowledge.edit", 
                        "knowledge.delete", "knowledge.upload",
                        "document.view", "document.create", "document.edit", "document.delete",
                        "model.view", "model.create", "model.edit", "model.delete", "model.test"
                    ]
                },
                {
                    "name": "普通用户",
                    "description": "基础使用权限",
                    "permissions": [
                        "knowledge.view", "document.view", "chat.view", 
                        "chat.create", "chat.edit", "chat.delete"
                    ]
                },
                {
                    "name": "AB测试员",
                    "description": "AB测试管理权限",
                    "permissions": [
                        "ab-testing.view", "ab-testing.create", "ab-testing.edit", 
                        "ab-testing.delete", "ab-testing.manage"
                    ]
                }
            ]
            
            # 创建角色
            for role_data in roles:
                role = Role(
                    name=role_data["name"],
                    description=role_data["description"]
                )
                session.add(role)
                session.flush()  # 获取角色ID
                
                # 分配权限
                for perm_name in role_data["permissions"]:
                    if perm_name in permission_map:
                        role.permissions.append(permission_map[perm_name])
            
            session.commit()
            logger.info(f"角色初始化完成，共创建 {len(roles)} 个角色")
            session.close()
            return True
            
        except Exception as e:
            logger.error(f"角色初始化失败: {e}")
            session.rollback()
            session.close()
            return False
    
    def init_users(self):
        """初始化用户数据"""
        try:
            session = self.SessionLocal()
            
            # 检查是否已有用户数据
            if session.query(User).count() > 0:
                logger.info("用户数据已存在，跳过初始化")
                session.close()
                return True
            
            # 获取角色
            admin_role = session.query(Role).filter(Role.name == "超级管理员").first()
            if not admin_role:
                logger.error("未找到超级管理员角色")
                session.close()
                return False
            
            # 创建默认管理员用户
            admin_user = User(
                username="admin",
                email="admin@example.com",
                full_name="系统管理员",
                is_active=True,
                is_admin=True
            )
            admin_user.hashed_password = get_password_hash("admin123")
            admin_user.roles.append(admin_role)
            
            session.add(admin_user)
            
            # 创建测试用户
            test_users = [
                {
                    "username": "user1",
                    "email": "user1@example.com",
                    "full_name": "测试用户1",
                    "role_name": "普通用户"
                },
                {
                    "username": "manager",
                    "email": "manager@example.com", 
                    "full_name": "知识库管理员",
                    "role_name": "知识库管理员"
                },
                {
                    "username": "tester",
                    "email": "tester@example.com",
                    "full_name": "AB测试员",
                    "role_name": "AB测试员"
                }
            ]
            
            for user_data in test_users:
                role = session.query(Role).filter(Role.name == user_data["role_name"]).first()
                if role:
                    user = User(
                        username=user_data["username"],
                        email=user_data["email"],
                        full_name=user_data["full_name"],
                        is_active=True,
                        is_admin=False
                    )
                    user.hashed_password = get_password_hash("password123")
                    user.roles.append(role)
                    session.add(user)
            
            session.commit()
            logger.info("用户初始化完成")
            session.close()
            return True
            
        except Exception as e:
            logger.error(f"用户初始化失败: {e}")
            session.rollback()
            session.close()
            return False
    
    def init_model_configs(self):
        """初始化模型配置"""
        try:
            session = self.SessionLocal()
            
            # 检查是否已有模型配置
            if session.query(ModelConfig).count() > 0:
                logger.info("模型配置已存在，跳过初始化")
                session.close()
                return True
            
            # 默认模型配置
            model_configs = [
                {
                    "name": "DeepSeek Chat",
                    "provider": "deepseek",
                    "model_name": "deepseek-chat",
                    "api_key": "",
                    "base_url": "https://api.deepseek.com",
                    "is_default": True,
                    "config": {
                        "temperature": 0.7,
                        "max_tokens": 4000,
                        "top_p": 0.9
                    }
                },
                {
                    "name": "OpenAI GPT-4",
                    "provider": "openai",
                    "model_name": "gpt-4",
                    "api_key": "",
                    "base_url": "https://api.openai.com/v1",
                    "is_default": False,
                    "config": {
                        "temperature": 0.7,
                        "max_tokens": 4000,
                        "top_p": 0.9
                    }
                },
                {
                    "name": "Claude 3",
                    "provider": "anthropic",
                    "model_name": "claude-3-sonnet-20240229",
                    "api_key": "",
                    "base_url": "https://api.anthropic.com",
                    "is_default": False,
                    "config": {
                        "temperature": 0.7,
                        "max_tokens": 4000,
                        "top_p": 0.9
                    }
                }
            ]
            
            for config_data in model_configs:
                model_config = ModelConfig(**config_data)
                session.add(model_config)
            
            session.commit()
            logger.info(f"模型配置初始化完成，共创建 {len(model_configs)} 个配置")
            session.close()
            return True
            
        except Exception as e:
            logger.error(f"模型配置初始化失败: {e}")
            session.rollback()
            session.close()
            return False
    
    def init_system_configs(self):
        """初始化系统配置"""
        try:
            session = self.SessionLocal()
            
            # 检查是否已有系统配置
            if session.query(SystemConfig).count() > 0:
                logger.info("系统配置已存在，跳过初始化")
                session.close()
                return True
            
            # 默认系统配置
            system_configs = [
                {
                    "config_key": "app_name",
                    "config_value": "AI知识库管理系统",
                    "config_type": "string",
                    "description": "应用名称"
                },
                {
                    "config_key": "version",
                    "config_value": "1.0.0",
                    "config_type": "string",
                    "description": "应用版本"
                },
                {
                    "config_key": "debug",
                    "config_value": "false",
                    "config_type": "bool",
                    "description": "调试模式"
                },
                {
                    "config_key": "log_level",
                    "config_value": "INFO",
                    "config_type": "string",
                    "description": "日志级别"
                },
                {
                    "config_key": "max_file_size",
                    "config_value": "104857600",
                    "config_type": "int",
                    "description": "最大文件大小（字节）"
                },
                {
                    "config_key": "allowed_file_types",
                    "config_value": '["pdf", "docx", "txt", "md"]',
                    "config_type": "json",
                    "description": "允许的文件类型"
                },
                {
                    "config_key": "backup_retention_days",
                    "config_value": "30",
                    "config_type": "int",
                    "description": "备份保留天数"
                },
                {
                    "config_key": "chunk_size",
                    "config_value": "1000",
                    "config_type": "int",
                    "description": "文档分块大小"
                },
                {
                    "config_key": "chunk_overlap",
                    "config_value": "200",
                    "config_type": "int",
                    "description": "文档分块重叠大小"
                }
            ]
            
            for config_data in system_configs:
                system_config = SystemConfig(**config_data)
                session.add(system_config)
            
            session.commit()
            logger.info(f"系统配置初始化完成，共创建 {len(system_configs)} 个配置")
            session.close()
            return True
            
        except Exception as e:
            logger.error(f"系统配置初始化失败: {e}")
            session.rollback()
            session.close()
            return False
    
    def init_all(self):
        """初始化所有数据"""
        logger.info("开始数据库初始化...")
        
        # 创建表
        if not self.create_tables():
            return False
        
        # 初始化数据
        if not self.init_permissions():
            return False
        
        if not self.init_roles():
            return False
        
        if not self.init_users():
            return False
        
        if not self.init_model_configs():
            return False
        
        if not self.init_system_configs():
            return False
        
        logger.info("数据库初始化完成！")
        logger.info("默认管理员账户: admin / admin123")
        return True

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="数据库初始化工具")
    parser.add_argument("--drop", action="store_true", help="删除所有表后重新创建")
    parser.add_argument("--database-url", help="数据库连接URL")
    parser.add_argument("--init-only", action="store_true", help="仅初始化数据，不创建表")
    
    args = parser.parse_args()
    
    initializer = DatabaseInitializer(args.database_url)
    
    if args.drop:
        logger.info("删除所有表...")
        initializer.drop_tables()
    
    if args.init_only:
        # 仅初始化数据
        success = (
            initializer.init_permissions() and
            initializer.init_roles() and
            initializer.init_users() and
            initializer.init_model_configs() and
            initializer.init_system_configs()
        )
    else:
        # 完整初始化
        success = initializer.init_all()
    
    if success:
        logger.info("数据库初始化成功！")
        sys.exit(0)
    else:
        logger.error("数据库初始化失败！")
        sys.exit(1)

if __name__ == "__main__":
    main() 