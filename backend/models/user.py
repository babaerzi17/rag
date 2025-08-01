from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    roles = relationship("Role", secondary="user_roles", back_populates="users")
    
    # 暂时注释掉AB测试相关的关系以避免循环依赖问题
    # ab_tests = relationship("ABTest", back_populates="creator")
    # ab_test_sessions = relationship("ABTestSession", back_populates="user")
    # evaluations = relationship("QuestionEvaluation", back_populates="evaluator") 