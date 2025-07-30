import random
import hashlib
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
from scipy import stats
import logging

from ..models.ab_testing import (
    ABTest, ABTestSession, ABTestInteraction, ABTestMetric,
    TestQuestion, QuestionEvaluation, TestStatus, TestType
)
from ..services.rag_service import RAGService
from ..services.llm_service import LLMService, RAGChatService

logger = logging.getLogger(__name__)

class ABTestService:
    def __init__(self, rag_service: RAGService, llm_service: LLMService):
        """初始化AB测试服务"""
        self.rag_service = rag_service
        self.llm_service = llm_service
        self.rag_chat_service = RAGChatService(rag_service, llm_service)
    
    def create_test(self, test_data: Dict[str, Any], user_id: int) -> ABTest:
        """创建AB测试"""
        test = ABTest(
            name=test_data["name"],
            description=test_data.get("description", ""),
            test_type=test_data["test_type"],
            config=test_data.get("config", {}),
            group_a_config=test_data["group_a_config"],
            group_b_config=test_data["group_b_config"],
            traffic_split=test_data.get("traffic_split", 0.5),
            sample_size=test_data.get("sample_size"),
            duration_days=test_data.get("duration_days"),
            created_by=user_id
        )
        return test
    
    def assign_user_to_group(self, test: ABTest, user_id: int) -> str:
        """为用户分配测试组"""
        # 使用用户ID和测试ID生成一致的哈希值
        hash_input = f"{user_id}_{test.id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        
        # 根据流量分配比例决定分组
        if hash_value % 100 < test.traffic_split * 100:
            return "A"
        else:
            return "B"
    
    def get_group_config(self, test: ABTest, group: str) -> Dict[str, Any]:
        """获取分组配置"""
        if group == "A":
            return test.group_a_config
        elif group == "B":
            return test.group_b_config
        else:
            raise ValueError(f"无效的分组: {group}")
    
    def start_test_session(self, test: ABTest, user_id: int, session_id: str) -> ABTestSession:
        """开始测试会话"""
        # 分配用户到测试组
        group = self.assign_user_to_group(test, user_id)
        group_config = self.get_group_config(test, group)
        
        # 创建测试会话
        test_session = ABTestSession(
            test_id=test.id,
            user_id=user_id,
            session_id=session_id,
            group=group,
            group_config=group_config,
            start_time=datetime.now()
        )
        
        return test_session
    
    async def process_test_query(
        self,
        test_session: ABTestSession,
        query: str,
        kb_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """处理测试查询"""
        start_time = time.time()
        
        try:
            # 根据测试配置处理查询
            group_config = test_session.group_config
            
            # 应用测试配置
            if test_session.ab_test.test_type == TestType.MODEL_COMPARISON:
                # 模型对比测试
                provider = group_config.get("provider", "deepseek")
                model = group_config.get("model", "deepseek-chat")
                temperature = group_config.get("temperature", 0.7)
                max_tokens = group_config.get("max_tokens", 1000)
                
                response = await self.rag_chat_service.chat(
                    query=query,
                    kb_id=kb_id,
                    provider=provider,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
            elif test_session.ab_test.test_type == TestType.RETRIEVAL_METHOD:
                # 检索方法对比测试
                retrieval_method = group_config.get("retrieval_method", "vector")
                top_k = group_config.get("top_k", 5)
                
                if retrieval_method == "vector":
                    search_results = self.rag_service.search(query, kb_id, top_k)
                elif retrieval_method == "hybrid":
                    # 混合检索
                    vector_results = self.rag_service.search(query, kb_id, top_k)
                    # 这里可以添加关键词检索逻辑
                    search_results = vector_results
                else:
                    search_results = self.rag_service.search(query, kb_id, top_k)
                
                # 使用默认配置生成回答
                response = await self.rag_chat_service.chat(
                    query=query,
                    kb_id=kb_id,
                    top_k=top_k
                )
                
            elif test_session.ab_test.test_type == TestType.CHUNK_SIZE:
                # 分块大小对比测试
                chunk_size = group_config.get("chunk_size", 512)
                # 这里需要重新处理文档分块，暂时使用默认配置
                response = await self.rag_chat_service.chat(
                    query=query,
                    kb_id=kb_id
                )
                
            else:
                # 默认RAG处理
                response = await self.rag_chat_service.chat(
                    query=query,
                    kb_id=kb_id
                )
            
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            # 创建交互记录
            interaction = ABTestInteraction(
                session_id=test_session.id,
                query=query,
                response=response["answer"],
                response_time_ms=response_time_ms,
                retrieved_chunks=response.get("sources", []),
                chunk_count=len(response.get("sources", [])),
                model_used=response.get("model", ""),
                tokens_used=response.get("usage", {}).get("total_tokens", 0)
            )
            
            return {
                "interaction": interaction,
                "response": response,
                "response_time_ms": response_time_ms
            }
            
        except Exception as e:
            logger.error(f"处理测试查询失败: {e}")
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            # 创建失败记录
            interaction = ABTestInteraction(
                session_id=test_session.id,
                query=query,
                response=f"处理失败: {str(e)}",
                response_time_ms=response_time_ms
            )
            
            return {
                "interaction": interaction,
                "response": {"answer": f"处理失败: {str(e)}", "sources": []},
                "response_time_ms": response_time_ms
            }
    
    def calculate_metrics(self, test: ABTest) -> List[ABTestMetric]:
        """计算测试指标"""
        metrics = []
        
        # 获取A组和B组的数据
        group_a_sessions = [s for s in test.test_sessions if s.group == "A"]
        group_b_sessions = [s for s in test.test_sessions if s.group == "B"]
        
        # 1. 响应时间指标
        a_response_times = []
        b_response_times = []
        
        for session in group_a_sessions:
            for interaction in session.interactions:
                if interaction.response_time_ms:
                    a_response_times.append(interaction.response_time_ms)
        
        for session in group_b_sessions:
            for interaction in session.interactions:
                if interaction.response_time_ms:
                    b_response_times.append(interaction.response_time_ms)
        
        if a_response_times and b_response_times:
            metric = self._calculate_statistical_metric(
                test, "response_time_ms", "performance",
                a_response_times, b_response_times,
                "平均响应时间 (ms)"
            )
            metrics.append(metric)
        
        # 2. 成功率指标
        a_success_count = sum(1 for s in group_a_sessions for i in s.interactions if "失败" not in i.response)
        a_total_count = sum(len(s.interactions) for s in group_a_sessions)
        b_success_count = sum(1 for s in group_b_sessions for i in s.interactions if "失败" not in i.response)
        b_total_count = sum(len(s.interactions) for s in group_b_sessions)
        
        if a_total_count > 0 and b_total_count > 0:
            a_success_rate = a_success_count / a_total_count
            b_success_rate = b_success_count / b_total_count
            
            metric = ABTestMetric(
                test_id=test.id,
                metric_name="success_rate",
                metric_type="quality",
                group_a_value=a_success_rate,
                group_b_value=b_success_rate,
                difference=b_success_rate - a_success_rate,
                improvement_percentage=((b_success_rate - a_success_rate) / a_success_rate * 100) if a_success_rate > 0 else 0
            )
            metrics.append(metric)
        
        # 3. 用户评分指标
        a_ratings = [i.user_rating for s in group_a_sessions for i in s.interactions if i.user_rating]
        b_ratings = [i.user_rating for s in group_b_sessions for i in s.interactions if i.user_rating]
        
        if a_ratings and b_ratings:
            metric = self._calculate_statistical_metric(
                test, "user_rating", "quality",
                a_ratings, b_ratings,
                "用户评分"
            )
            metrics.append(metric)
        
        # 4. Token使用量指标
        a_tokens = [i.tokens_used for s in group_a_sessions for i in s.interactions if i.tokens_used]
        b_tokens = [i.tokens_used for s in group_b_sessions for i in s.interactions if i.tokens_used]
        
        if a_tokens and b_tokens:
            metric = self._calculate_statistical_metric(
                test, "tokens_used", "cost",
                a_tokens, b_tokens,
                "Token使用量"
            )
            metrics.append(metric)
        
        return metrics
    
    def _calculate_statistical_metric(
        self,
        test: ABTest,
        metric_name: str,
        metric_type: str,
        group_a_data: List[float],
        group_b_data: List[float],
        display_name: str
    ) -> ABTestMetric:
        """计算统计指标"""
        a_mean = np.mean(group_a_data)
        b_mean = np.mean(group_b_data)
        difference = b_mean - a_mean
        improvement_percentage = (difference / a_mean * 100) if a_mean != 0 else 0
        
        # 执行t检验
        t_stat, p_value = stats.ttest_ind(group_a_data, group_b_data)
        confidence_level = 1 - p_value
        is_significant = p_value < 0.05
        
        return ABTestMetric(
            test_id=test.id,
            metric_name=metric_name,
            metric_type=metric_type,
            group_a_value=a_mean,
            group_b_value=b_mean,
            difference=difference,
            improvement_percentage=improvement_percentage,
            confidence_level=confidence_level,
            p_value=p_value,
            is_significant=is_significant
        )
    
    def get_test_summary(self, test: ABTest) -> Dict[str, Any]:
        """获取测试摘要"""
        total_sessions = len(test.test_sessions)
        group_a_sessions = len([s for s in test.test_sessions if s.group == "A"])
        group_b_sessions = len([s for s in test.test_sessions if s.group == "B"])
        
        total_interactions = sum(len(s.interactions) for s in test.test_sessions)
        successful_interactions = sum(
            1 for s in test.test_sessions 
            for i in s.interactions 
            if "失败" not in i.response
        )
        
        avg_response_time = np.mean([
            i.response_time_ms for s in test.test_sessions 
            for i in s.interactions 
            if i.response_time_ms
        ]) if total_interactions > 0 else 0
        
        avg_user_rating = np.mean([
            i.user_rating for s in test.test_sessions 
            for i in s.interactions 
            if i.user_rating
        ]) if any(i.user_rating for s in test.test_sessions for i in s.interactions) else 0
        
        return {
            "test_id": test.id,
            "test_name": test.name,
            "status": test.status,
            "total_sessions": total_sessions,
            "group_a_sessions": group_a_sessions,
            "group_b_sessions": group_b_sessions,
            "total_interactions": total_interactions,
            "successful_interactions": successful_interactions,
            "success_rate": successful_interactions / total_interactions if total_interactions > 0 else 0,
            "avg_response_time_ms": avg_response_time,
            "avg_user_rating": avg_user_rating,
            "created_at": test.created_at,
            "started_at": test.started_at,
            "ended_at": test.ended_at
        }
    
    def create_test_questions(self, test_id: int, questions_data: List[Dict[str, Any]]) -> List[TestQuestion]:
        """创建测试问题"""
        questions = []
        for q_data in questions_data:
            question = TestQuestion(
                test_id=test_id,
                question=q_data["question"],
                category=q_data.get("category", "general"),
                difficulty=q_data.get("difficulty", "medium"),
                expected_answer=q_data.get("expected_answer", ""),
                key_points=q_data.get("key_points", []),
                scoring_criteria=q_data.get("scoring_criteria", {})
            )
            questions.append(question)
        return questions
    
    def evaluate_response(
        self,
        question: TestQuestion,
        interaction: ABTestInteraction,
        evaluator_id: int,
        evaluation_data: Dict[str, Any]
    ) -> QuestionEvaluation:
        """评估回答质量"""
        evaluation = QuestionEvaluation(
            question_id=question.id,
            interaction_id=interaction.id,
            evaluator_id=evaluator_id,
            relevance_score=evaluation_data.get("relevance_score", 0),
            accuracy_score=evaluation_data.get("accuracy_score", 0),
            completeness_score=evaluation_data.get("completeness_score", 0),
            clarity_score=evaluation_data.get("clarity_score", 0),
            helpfulness_score=evaluation_data.get("helpfulness_score", 0),
            overall_score=evaluation_data.get("overall_score", 0),
            strengths=evaluation_data.get("strengths", ""),
            weaknesses=evaluation_data.get("weaknesses", ""),
            suggestions=evaluation_data.get("suggestions", "")
        )
        return evaluation 