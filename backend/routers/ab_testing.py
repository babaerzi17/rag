from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from ..database import get_db
from ..auth.security import get_current_user
from ..models.user import User
from ..models.ab_testing import ABTest, ABTestSession, ABTestInteraction, TestStatus
from ..schemas.ab_testing import (
    ABTestCreate, ABTestUpdate, ABTestResponse, ABTestSummary,
    ABTestSessionResponse, ABTestInteractionResponse,
    TestQueryRequest, TestQueryResponse, UserFeedbackRequest,
    TestQuestionCreate, TestQuestionResponse, QuestionEvaluationCreate,
    ABTestMetricResponse, TestStatistics, TestConfigTemplate
)
from ..services.ab_test_service import ABTestService
from ..services.rag_service import RAGService
from ..services.llm_service import LLMService

router = APIRouter()

def get_ab_test_service(db: Session = Depends(get_db)) -> ABTestService:
    """获取AB测试服务实例"""
    rag_service = RAGService()
    llm_service = LLMService()
    return ABTestService(rag_service, llm_service)

# AB测试管理
@router.post("/tests", response_model=ABTestResponse, status_code=status.HTTP_201_CREATED)
async def create_ab_test(
    test_data: ABTestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ab_test_service: ABTestService = Depends(get_ab_test_service)
):
    """创建AB测试"""
    test = ab_test_service.create_test(test_data.dict(), current_user.id)
    db.add(test)
    db.commit()
    db.refresh(test)
    return test

@router.get("/tests", response_model=List[ABTestResponse])
async def list_ab_tests(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[TestStatus] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取AB测试列表"""
    query = db.query(ABTest).filter(ABTest.created_by == current_user.id)
    
    if status_filter:
        query = query.filter(ABTest.status == status_filter)
    
    tests = query.offset(skip).limit(limit).all()
    return tests

@router.get("/tests/{test_id}", response_model=ABTestResponse)
async def get_ab_test(
    test_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取AB测试详情"""
    test = db.query(ABTest).filter(
        ABTest.id == test_id,
        ABTest.created_by == current_user.id
    ).first()
    
    if not test:
        raise HTTPException(status_code=404, detail="测试不存在")
    
    return test

@router.put("/tests/{test_id}", response_model=ABTestResponse)
async def update_ab_test(
    test_id: int,
    test_update: ABTestUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新AB测试"""
    test = db.query(ABTest).filter(
        ABTest.id == test_id,
        ABTest.created_by == current_user.id
    ).first()
    
    if not test:
        raise HTTPException(status_code=404, detail="测试不存在")
    
    update_data = test_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(test, field, value)
    
    db.commit()
    db.refresh(test)
    return test

@router.delete("/tests/{test_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ab_test(
    test_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除AB测试"""
    test = db.query(ABTest).filter(
        ABTest.id == test_id,
        ABTest.created_by == current_user.id
    ).first()
    
    if not test:
        raise HTTPException(status_code=404, detail="测试不存在")
    
    db.delete(test)
    db.commit()

@router.post("/tests/{test_id}/start", response_model=ABTestResponse)
async def start_ab_test(
    test_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """启动AB测试"""
    test = db.query(ABTest).filter(
        ABTest.id == test_id,
        ABTest.created_by == current_user.id
    ).first()
    
    if not test:
        raise HTTPException(status_code=404, detail="测试不存在")
    
    if test.status != TestStatus.DRAFT:
        raise HTTPException(status_code=400, detail="只能启动草稿状态的测试")
    
    test.status = TestStatus.ACTIVE
    test.started_at = datetime.now()
    db.commit()
    db.refresh(test)
    return test

@router.post("/tests/{test_id}/pause", response_model=ABTestResponse)
async def pause_ab_test(
    test_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """暂停AB测试"""
    test = db.query(ABTest).filter(
        ABTest.id == test_id,
        ABTest.created_by == current_user.id
    ).first()
    
    if not test:
        raise HTTPException(status_code=404, detail="测试不存在")
    
    if test.status != TestStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="只能暂停进行中的测试")
    
    test.status = TestStatus.PAUSED
    db.commit()
    db.refresh(test)
    return test

@router.post("/tests/{test_id}/complete", response_model=ABTestResponse)
async def complete_ab_test(
    test_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """完成AB测试"""
    test = db.query(ABTest).filter(
        ABTest.id == test_id,
        ABTest.created_by == current_user.id
    ).first()
    
    if not test:
        raise HTTPException(status_code=404, detail="测试不存在")
    
    if test.status not in [TestStatus.ACTIVE, TestStatus.PAUSED]:
        raise HTTPException(status_code=400, detail="只能完成进行中或暂停的测试")
    
    test.status = TestStatus.COMPLETED
    test.ended_at = datetime.now()
    db.commit()
    db.refresh(test)
    return test

# 测试会话管理
@router.post("/tests/{test_id}/sessions", response_model=ABTestSessionResponse)
async def start_test_session(
    test_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ab_test_service: ABTestService = Depends(get_ab_test_service)
):
    """开始测试会话"""
    test = db.query(ABTest).filter(
        ABTest.id == test_id,
        ABTest.status == TestStatus.ACTIVE
    ).first()
    
    if not test:
        raise HTTPException(status_code=404, detail="测试不存在或未激活")
    
    # 生成会话ID
    session_id = str(uuid.uuid4())
    
    # 创建测试会话
    test_session = ab_test_service.start_test_session(test, current_user.id, session_id)
    db.add(test_session)
    db.commit()
    db.refresh(test_session)
    return test_session

@router.post("/tests/{test_id}/query", response_model=TestQueryResponse)
async def process_test_query(
    test_id: int,
    query_request: TestQueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ab_test_service: ABTestService = Depends(get_ab_test_service)
):
    """处理测试查询"""
    # 获取或创建测试会话
    test_session = None
    if query_request.session_id:
        test_session = db.query(ABTestSession).filter(
            ABTestSession.session_id == query_request.session_id,
            ABTestSession.user_id == current_user.id
        ).first()
    
    if not test_session:
        # 创建新的测试会话
        test = db.query(ABTest).filter(
            ABTest.id == test_id,
            ABTest.status == TestStatus.ACTIVE
        ).first()
        
        if not test:
            raise HTTPException(status_code=404, detail="测试不存在或未激活")
        
        session_id = str(uuid.uuid4())
        test_session = ab_test_service.start_test_session(test, current_user.id, session_id)
        db.add(test_session)
        db.commit()
        db.refresh(test_session)
    
    # 处理查询
    result = await ab_test_service.process_test_query(
        test_session, 
        query_request.query, 
        query_request.kb_id
    )
    
    # 保存交互记录
    interaction = result["interaction"]
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    
    # 更新会话统计
    test_session.total_queries += 1
    if "失败" not in result["response"]["answer"]:
        test_session.successful_queries += 1
    else:
        test_session.failed_queries += 1
    db.commit()
    
    return TestQueryResponse(
        answer=result["response"]["answer"],
        sources=result["response"].get("sources", []),
        response_time_ms=result["response_time_ms"],
        model_used=result["response"].get("model", ""),
        tokens_used=result["response"].get("usage", {}).get("total_tokens", 0),
        interaction_id=interaction.id
    )

@router.post("/interactions/{interaction_id}/feedback")
async def submit_user_feedback(
    interaction_id: int,
    feedback: UserFeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """提交用户反馈"""
    interaction = db.query(ABTestInteraction).filter(
        ABTestInteraction.id == interaction_id
    ).first()
    
    if not interaction:
        raise HTTPException(status_code=404, detail="交互记录不存在")
    
    # 验证用户权限
    if interaction.test_session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限操作此交互记录")
    
    interaction.user_rating = feedback.rating
    interaction.user_feedback = feedback.feedback
    db.commit()
    
    return {"message": "反馈提交成功"}

# 测试问题管理
@router.post("/tests/{test_id}/questions", response_model=List[TestQuestionResponse])
async def create_test_questions(
    test_id: int,
    questions_data: List[TestQuestionCreate],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建测试问题"""
    test = db.query(ABTest).filter(
        ABTest.id == test_id,
        ABTest.created_by == current_user.id
    ).first()
    
    if not test:
        raise HTTPException(status_code=404, detail="测试不存在")
    
    questions = []
    for q_data in questions_data:
        question = TestQuestion(
            test_id=test_id,
            question=q_data.question,
            category=q_data.category,
            difficulty=q_data.difficulty,
            expected_answer=q_data.expected_answer,
            key_points=q_data.key_points,
            scoring_criteria=q_data.scoring_criteria
        )
        questions.append(question)
    
    db.add_all(questions)
    db.commit()
    
    for question in questions:
        db.refresh(question)
    
    return questions

@router.get("/tests/{test_id}/questions", response_model=List[TestQuestionResponse])
async def get_test_questions(
    test_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取测试问题列表"""
    test = db.query(ABTest).filter(
        ABTest.id == test_id,
        ABTest.created_by == current_user.id
    ).first()
    
    if not test:
        raise HTTPException(status_code=404, detail="测试不存在")
    
    questions = db.query(TestQuestion).filter(TestQuestion.test_id == test_id).all()
    return questions

# 测试分析
@router.get("/tests/{test_id}/summary", response_model=ABTestSummary)
async def get_test_summary(
    test_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ab_test_service: ABTestService = Depends(get_ab_test_service)
):
    """获取测试摘要"""
    test = db.query(ABTest).filter(
        ABTest.id == test_id,
        ABTest.created_by == current_user.id
    ).first()
    
    if not test:
        raise HTTPException(status_code=404, detail="测试不存在")
    
    return ab_test_service.get_test_summary(test)

@router.post("/tests/{test_id}/calculate-metrics", response_model=List[ABTestMetricResponse])
async def calculate_test_metrics(
    test_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ab_test_service: ABTestService = Depends(get_ab_test_service)
):
    """计算测试指标"""
    test = db.query(ABTest).filter(
        ABTest.id == test_id,
        ABTest.created_by == current_user.id
    ).first()
    
    if not test:
        raise HTTPException(status_code=404, detail="测试不存在")
    
    metrics = ab_test_service.calculate_metrics(test)
    
    # 保存指标到数据库
    for metric in metrics:
        db.add(metric)
    db.commit()
    
    for metric in metrics:
        db.refresh(metric)
    
    return metrics

@router.get("/tests/{test_id}/metrics", response_model=List[ABTestMetricResponse])
async def get_test_metrics(
    test_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取测试指标"""
    test = db.query(ABTest).filter(
        ABTest.id == test_id,
        ABTest.created_by == current_user.id
    ).first()
    
    if not test:
        raise HTTPException(status_code=404, detail="测试不存在")
    
    metrics = db.query(ABTestMetric).filter(ABTestMetric.test_id == test_id).all()
    return metrics

# 测试配置模板
@router.get("/config-templates", response_model=List[TestConfigTemplate])
async def get_config_templates():
    """获取测试配置模板"""
    templates = [
        {
            "name": "模型对比测试",
            "description": "对比不同LLM模型的性能",
            "test_type": "model_comparison",
            "group_a_config": {
                "provider": "deepseek",
                "model": "deepseek-chat",
                "temperature": 0.7,
                "max_tokens": 1000
            },
            "group_b_config": {
                "provider": "openai",
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 1000
            }
        },
        {
            "name": "检索方法对比",
            "description": "对比不同检索方法的准确性",
            "test_type": "retrieval_method",
            "group_a_config": {
                "retrieval_method": "vector",
                "top_k": 5
            },
            "group_b_config": {
                "retrieval_method": "hybrid",
                "top_k": 5
            }
        },
        {
            "name": "分块大小对比",
            "description": "对比不同文档分块大小的效果",
            "test_type": "chunk_size",
            "group_a_config": {
                "chunk_size": 512
            },
            "group_b_config": {
                "chunk_size": 1024
            }
        }
    ]
    return templates 