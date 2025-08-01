# 导入所有模型以确保它们被正确注册
from .base import Base
from .associations import user_roles, role_permissions
from .user import User
from .role import Role  
from .permission import Permission
from .knowledge import KnowledgeBase, Document, DocumentChunk
from .chat import ChatSession, ChatMessage
from .model_config import ModelConfig
# 暂时注释掉AB测试相关模型以避免循环依赖问题
# from .system import SystemLog, SystemBackup, SystemMetric, PerformanceMetric, ModelUsageMetric, SystemConfig, ServiceHealth, SystemAlert
# from .ab_testing import ABTest, ABTestSession, ABTestInteraction, ABTestMetric, TestQuestion, QuestionEvaluation

__all__ = [
    "Base", 
    "User", 
    "Role", 
    "Permission", 
    "user_roles", 
    "role_permissions",
    "KnowledgeBase",
    "Document",
    "DocumentChunk",
    "ChatSession",
    "ChatMessage",
    "ModelConfig",
    # 暂时注释掉AB测试相关模型
    # "SystemLog",
    # "SystemBackup",
    # "SystemMetric",
    # "PerformanceMetric",
    # "ModelUsageMetric",
    # "SystemConfig",
    # "ServiceHealth",
    # "SystemAlert",
    # "ABTest",
    # "ABTestSession",
    # "ABTestInteraction",
    # "ABTestMetric",
    # "TestQuestion",
    # "QuestionEvaluation",
] 