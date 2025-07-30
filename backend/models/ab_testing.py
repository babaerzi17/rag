from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base
import enum

class TestType(str, enum.Enum):
    RAG_VS_BASELINE = "rag_vs_baseline"  # RAG vs 基线模型
    MODEL_COMPARISON = "model_comparison"  # 不同模型对比
    RETRIEVAL_METHOD = "retrieval_method"  # 不同检索方法
    CHUNK_SIZE = "chunk_size"  # 不同分块大小
    CONTEXT_WINDOW = "context_window"  # 不同上下文窗口

class TestStatus(str, enum.Enum):
    DRAFT = "draft"  # 草稿
    ACTIVE = "active"  # 进行中
    PAUSED = "paused"  # 暂停
    COMPLETED = "completed"  # 已完成
    ANALYZED = "analyzed"  # 已分析

class ABTest(Base):
    __tablename__ = "ab_tests"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    test_type = Column(Enum(TestType), nullable=False)
    status = Column(Enum(TestStatus), default=TestStatus.DRAFT)
    
    # 测试配置
    config = Column(JSON)  # 存储测试参数配置
    
    # 分组配置
    group_a_config = Column(JSON)  # A组配置
    group_b_config = Column(JSON)  # B组配置
    
    # 测试参数
    traffic_split = Column(Float, default=0.5)  # 流量分配比例
    sample_size = Column(Integer)  # 样本大小
    duration_days = Column(Integer)  # 测试持续天数
    
    # 创建者
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    started_at = Column(DateTime(timezone=True))
    ended_at = Column(DateTime(timezone=True))
    
    # 关系
    creator = relationship("User", back_populates="ab_tests")
    test_sessions = relationship("ABTestSession", back_populates="ab_test", cascade="all, delete-orphan")
    metrics = relationship("ABTestMetric", back_populates="ab_test", cascade="all, delete-orphan")

class ABTestSession(Base):
    __tablename__ = "ab_test_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("ab_tests.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(255), nullable=False)  # 用户会话ID
    
    # 分组信息
    group = Column(String(10), nullable=False)  # 'A' 或 'B'
    group_config = Column(JSON)  # 该用户使用的配置
    
    # 会话信息
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True))
    duration_seconds = Column(Integer)  # 会话持续时间
    
    # 会话统计
    total_queries = Column(Integer, default=0)  # 总查询数
    successful_queries = Column(Integer, default=0)  # 成功查询数
    failed_queries = Column(Integer, default=0)  # 失败查询数
    
    # 关系
    ab_test = relationship("ABTest", back_populates="test_sessions")
    user = relationship("User", back_populates="ab_test_sessions")
    interactions = relationship("ABTestInteraction", back_populates="test_session", cascade="all, delete-orphan")

class ABTestInteraction(Base):
    __tablename__ = "ab_test_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("ab_test_sessions.id"), nullable=False)
    
    # 交互信息
    query = Column(Text, nullable=False)  # 用户查询
    response = Column(Text)  # 系统响应
    response_time_ms = Column(Integer)  # 响应时间（毫秒）
    
    # 检索信息
    retrieved_chunks = Column(JSON)  # 检索到的文档块
    retrieval_time_ms = Column(Integer)  # 检索时间
    chunk_count = Column(Integer)  # 检索到的块数量
    
    # 生成信息
    generation_time_ms = Column(Integer)  # 生成时间
    model_used = Column(String(100))  # 使用的模型
    tokens_used = Column(Integer)  # 使用的token数
    
    # 质量评估
    relevance_score = Column(Float)  # 相关性评分
    accuracy_score = Column(Float)  # 准确性评分
    helpfulness_score = Column(Float)  # 有用性评分
    
    # 用户反馈
    user_rating = Column(Integer)  # 用户评分 (1-5)
    user_feedback = Column(Text)  # 用户反馈
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    test_session = relationship("ABTestSession", back_populates="interactions")

class ABTestMetric(Base):
    __tablename__ = "ab_test_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("ab_tests.id"), nullable=False)
    
    # 指标信息
    metric_name = Column(String(100), nullable=False)  # 指标名称
    metric_type = Column(String(50), nullable=False)  # 指标类型
    
    # 分组数据
    group_a_value = Column(Float)  # A组值
    group_b_value = Column(Float)  # B组值
    difference = Column(Float)  # 差异
    improvement_percentage = Column(Float)  # 改进百分比
    
    # 统计信息
    confidence_level = Column(Float)  # 置信水平
    p_value = Column(Float)  # P值
    is_significant = Column(Boolean)  # 是否显著
    
    # 计算时间
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    ab_test = relationship("ABTest", back_populates="metrics")

class TestQuestion(Base):
    __tablename__ = "test_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("ab_tests.id"), nullable=False)
    
    # 问题信息
    question = Column(Text, nullable=False)  # 测试问题
    category = Column(String(100))  # 问题类别
    difficulty = Column(String(20))  # 难度级别
    
    # 标准答案
    expected_answer = Column(Text)  # 期望答案
    key_points = Column(JSON)  # 关键点
    
    # 评分标准
    scoring_criteria = Column(JSON)  # 评分标准
    
    # 关系
    ab_test = relationship("ABTest")
    evaluations = relationship("QuestionEvaluation", back_populates="question", cascade="all, delete-orphan")

class QuestionEvaluation(Base):
    __tablename__ = "question_evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("test_questions.id"), nullable=False)
    interaction_id = Column(Integer, ForeignKey("ab_test_interactions.id"), nullable=False)
    
    # 评估信息
    evaluator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 评分维度
    relevance_score = Column(Float)  # 相关性 (0-10)
    accuracy_score = Column(Float)  # 准确性 (0-10)
    completeness_score = Column(Float)  # 完整性 (0-10)
    clarity_score = Column(Float)  # 清晰度 (0-10)
    helpfulness_score = Column(Float)  # 有用性 (0-10)
    
    # 总体评分
    overall_score = Column(Float)  # 总体评分 (0-10)
    
    # 详细评价
    strengths = Column(Text)  # 优点
    weaknesses = Column(Text)  # 缺点
    suggestions = Column(Text)  # 建议
    
    # 评估时间
    evaluated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    question = relationship("TestQuestion", back_populates="evaluations")
    interaction = relationship("ABTestInteraction")
    evaluator = relationship("User") 