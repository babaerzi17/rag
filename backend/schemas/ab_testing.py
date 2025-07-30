from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class TestType(str, Enum):
    RAG_VS_BASELINE = "rag_vs_baseline"
    MODEL_COMPARISON = "model_comparison"
    RETRIEVAL_METHOD = "retrieval_method"
    CHUNK_SIZE = "chunk_size"
    CONTEXT_WINDOW = "context_window"

class TestStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ANALYZED = "analyzed"

# AB测试基础模式
class ABTestBase(BaseModel):
    name: str = Field(..., description="测试名称")
    description: Optional[str] = Field(None, description="测试描述")
    test_type: TestType = Field(..., description="测试类型")
    traffic_split: float = Field(0.5, ge=0.1, le=0.9, description="流量分配比例")
    sample_size: Optional[int] = Field(None, description="样本大小")
    duration_days: Optional[int] = Field(None, description="测试持续天数")

class ABTestCreate(ABTestBase):
    group_a_config: Dict[str, Any] = Field(..., description="A组配置")
    group_b_config: Dict[str, Any] = Field(..., description="B组配置")
    config: Optional[Dict[str, Any]] = Field(None, description="通用配置")

class ABTestUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TestStatus] = None
    group_a_config: Optional[Dict[str, Any]] = None
    group_b_config: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None

class ABTestResponse(ABTestBase):
    id: int
    status: TestStatus
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    group_a_config: Dict[str, Any]
    group_b_config: Dict[str, Any]
    config: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

# 测试会话模式
class ABTestSessionBase(BaseModel):
    test_id: int
    user_id: int
    session_id: str
    group: str
    group_config: Dict[str, Any]

class ABTestSessionCreate(ABTestSessionBase):
    pass

class ABTestSessionResponse(ABTestSessionBase):
    id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    total_queries: int
    successful_queries: int
    failed_queries: int

    class Config:
        from_attributes = True

# 测试交互模式
class ABTestInteractionBase(BaseModel):
    session_id: int
    query: str
    response: Optional[str] = None
    response_time_ms: Optional[int] = None
    retrieved_chunks: Optional[List[Dict[str, Any]]] = None
    retrieval_time_ms: Optional[int] = None
    chunk_count: Optional[int] = None
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    relevance_score: Optional[float] = None
    accuracy_score: Optional[float] = None
    helpfulness_score: Optional[float] = None
    user_rating: Optional[int] = Field(None, ge=1, le=5)
    user_feedback: Optional[str] = None

class ABTestInteractionCreate(ABTestInteractionBase):
    pass

class ABTestInteractionResponse(ABTestInteractionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# 测试指标模式
class ABTestMetricBase(BaseModel):
    test_id: int
    metric_name: str
    metric_type: str
    group_a_value: Optional[float] = None
    group_b_value: Optional[float] = None
    difference: Optional[float] = None
    improvement_percentage: Optional[float] = None
    confidence_level: Optional[float] = None
    p_value: Optional[float] = None
    is_significant: Optional[bool] = None

class ABTestMetricResponse(ABTestMetricBase):
    id: int
    calculated_at: datetime

    class Config:
        from_attributes = True

# 测试问题模式
class TestQuestionBase(BaseModel):
    test_id: int
    question: str
    category: Optional[str] = None
    difficulty: Optional[str] = None
    expected_answer: Optional[str] = None
    key_points: Optional[List[str]] = None
    scoring_criteria: Optional[Dict[str, Any]] = None

class TestQuestionCreate(TestQuestionBase):
    pass

class TestQuestionResponse(TestQuestionBase):
    id: int

    class Config:
        from_attributes = True

# 问题评估模式
class QuestionEvaluationBase(BaseModel):
    question_id: int
    interaction_id: int
    evaluator_id: int
    relevance_score: Optional[float] = Field(None, ge=0, le=10)
    accuracy_score: Optional[float] = Field(None, ge=0, le=10)
    completeness_score: Optional[float] = Field(None, ge=0, le=10)
    clarity_score: Optional[float] = Field(None, ge=0, le=10)
    helpfulness_score: Optional[float] = Field(None, ge=0, le=10)
    overall_score: Optional[float] = Field(None, ge=0, le=10)
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    suggestions: Optional[str] = None

class QuestionEvaluationCreate(QuestionEvaluationBase):
    pass

class QuestionEvaluationResponse(QuestionEvaluationBase):
    id: int
    evaluated_at: datetime

    class Config:
        from_attributes = True

# 测试摘要模式
class ABTestSummary(BaseModel):
    test_id: int
    test_name: str
    status: TestStatus
    total_sessions: int
    group_a_sessions: int
    group_b_sessions: int
    total_interactions: int
    successful_interactions: int
    success_rate: float
    avg_response_time_ms: float
    avg_user_rating: float
    created_at: datetime
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None

# 测试查询模式
class TestQueryRequest(BaseModel):
    query: str
    kb_id: Optional[int] = None
    session_id: Optional[str] = None

class TestQueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    response_time_ms: int
    model_used: str
    tokens_used: int
    interaction_id: int

# 用户反馈模式
class UserFeedbackRequest(BaseModel):
    interaction_id: int
    rating: int = Field(..., ge=1, le=5, description="用户评分")
    feedback: Optional[str] = None

# 批量操作模式
class BatchTestCreate(BaseModel):
    tests: List[ABTestCreate]

class BatchQuestionCreate(BaseModel):
    test_id: int
    questions: List[TestQuestionCreate]

# 统计分析模式
class TestStatistics(BaseModel):
    test_id: int
    total_sessions: int
    total_interactions: int
    avg_session_duration: float
    avg_interactions_per_session: float
    success_rate: float
    avg_response_time: float
    avg_user_rating: float
    group_a_stats: Dict[str, Any]
    group_b_stats: Dict[str, Any]
    significant_metrics: List[ABTestMetricResponse]

# 测试配置模板
class TestConfigTemplate(BaseModel):
    name: str
    description: str
    test_type: TestType
    group_a_config: Dict[str, Any]
    group_b_config: Dict[str, Any]
    config: Optional[Dict[str, Any]] = None 