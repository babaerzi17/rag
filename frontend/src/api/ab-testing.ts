import api from './index'

// AB测试相关类型定义
export interface ABTest {
  id: number
  name: string
  description?: string
  test_type: 'rag_vs_baseline' | 'model_comparison' | 'retrieval_method' | 'chunk_size' | 'context_window'
  status: 'draft' | 'active' | 'paused' | 'completed' | 'analyzed'
  traffic_split: number
  sample_size?: number
  duration_days?: number
  group_a_config: Record<string, any>
  group_b_config: Record<string, any>
  config?: Record<string, any>
  created_by: number
  created_at: string
  updated_at?: string
  started_at?: string
  ended_at?: string
}

export interface ABTestCreate {
  name: string
  description?: string
  test_type: 'rag_vs_baseline' | 'model_comparison' | 'retrieval_method' | 'chunk_size' | 'context_window'
  traffic_split: number
  sample_size?: number
  duration_days?: number
  group_a_config: Record<string, any>
  group_b_config: Record<string, any>
  config?: Record<string, any>
}

export interface ABTestUpdate {
  name?: string
  description?: string
  status?: 'draft' | 'active' | 'paused' | 'completed' | 'analyzed'
  group_a_config?: Record<string, any>
  group_b_config?: Record<string, any>
  config?: Record<string, any>
}

export interface ABTestSummary {
  test_id: number
  test_name: string
  status: string
  total_sessions: number
  group_a_sessions: number
  group_b_sessions: number
  total_interactions: number
  successful_interactions: number
  success_rate: number
  avg_response_time_ms: number
  avg_user_rating: number
  created_at: string
  started_at?: string
  ended_at?: string
}

export interface ABTestSession {
  id: number
  test_id: number
  user_id: number
  session_id: string
  group: string
  group_config: Record<string, any>
  start_time: string
  end_time?: string
  duration_seconds?: number
  total_queries: number
  successful_queries: number
  failed_queries: number
}

export interface ABTestInteraction {
  id: number
  session_id: number
  query: string
  response?: string
  response_time_ms?: number
  retrieved_chunks?: any[]
  retrieval_time_ms?: number
  chunk_count?: number
  model_used?: string
  tokens_used?: number
  relevance_score?: number
  accuracy_score?: number
  helpfulness_score?: number
  user_rating?: number
  user_feedback?: string
  created_at: string
}

export interface ABTestMetric {
  id: number
  test_id: number
  metric_name: string
  metric_type: string
  group_a_value?: number
  group_b_value?: number
  difference?: number
  improvement_percentage?: number
  confidence_level?: number
  p_value?: number
  is_significant?: boolean
  calculated_at: string
}

export interface TestQuestion {
  id: number
  test_id: number
  question: string
  category?: string
  difficulty?: string
  expected_answer?: string
  key_points?: string[]
  scoring_criteria?: Record<string, any>
}

export interface TestQuestionCreate {
  test_id: number
  question: string
  category?: string
  difficulty?: string
  expected_answer?: string
  key_points?: string[]
  scoring_criteria?: Record<string, any>
}

export interface TestQueryRequest {
  query: string
  kb_id?: number
  session_id?: string
}

export interface TestQueryResponse {
  answer: string
  sources: any[]
  response_time_ms: number
  model_used: string
  tokens_used: number
  interaction_id: number
}

export interface UserFeedbackRequest {
  interaction_id: number
  rating: number
  feedback?: string
}

export interface TestConfigTemplate {
  name: string
  description: string
  test_type: string
  group_a_config: Record<string, any>
  group_b_config: Record<string, any>
  config?: Record<string, any>
}

// AB测试管理API
export const abTestingApi = {
  // 创建AB测试
  createTest: (data: ABTestCreate): Promise<ABTest> => {
    return api.post('/ab-testing/tests', data)
  },

  // 获取AB测试列表
  getTests: (params?: {
    skip?: number
    limit?: number
    status_filter?: string
  }): Promise<ABTest[]> => {
    return api.get('/ab-testing/tests', { params })
  },

  // 获取AB测试详情
  getTest: (testId: number): Promise<ABTest> => {
    return api.get(`/ab-testing/tests/${testId}`)
  },

  // 更新AB测试
  updateTest: (testId: number, data: ABTestUpdate): Promise<ABTest> => {
    return api.put(`/ab-testing/tests/${testId}`, data)
  },

  // 删除AB测试
  deleteTest: (testId: number): Promise<void> => {
    return api.delete(`/ab-testing/tests/${testId}`)
  },

  // 启动AB测试
  startTest: (testId: number): Promise<ABTest> => {
    return api.post(`/ab-testing/tests/${testId}/start`)
  },

  // 暂停AB测试
  pauseTest: (testId: number): Promise<ABTest> => {
    return api.post(`/ab-testing/tests/${testId}/pause`)
  },

  // 完成AB测试
  completeTest: (testId: number): Promise<ABTest> => {
    return api.post(`/ab-testing/tests/${testId}/complete`)
  },

  // 获取测试摘要
  getTestSummary: (testId: number): Promise<ABTestSummary> => {
    return api.get(`/ab-testing/tests/${testId}/summary`)
  },

  // 计算测试指标
  calculateMetrics: (testId: number): Promise<ABTestMetric[]> => {
    return api.post(`/ab-testing/tests/${testId}/calculate-metrics`)
  },

  // 获取测试指标
  getTestMetrics: (testId: number): Promise<ABTestMetric[]> => {
    return api.get(`/ab-testing/tests/${testId}/metrics`)
  },

  // 获取配置模板
  getConfigTemplates: (): Promise<TestConfigTemplate[]> => {
    return api.get('/ab-testing/config-templates')
  }
}

// 测试会话API
export const testSessionApi = {
  // 开始测试会话
  startSession: (testId: number): Promise<ABTestSession> => {
    return api.post(`/ab-testing/tests/${testId}/sessions`)
  },

  // 处理测试查询
  processQuery: (testId: number, data: TestQueryRequest): Promise<TestQueryResponse> => {
    return api.post(`/ab-testing/tests/${testId}/query`, data)
  },

  // 提交用户反馈
  submitFeedback: (interactionId: number, data: UserFeedbackRequest): Promise<void> => {
    return api.post(`/ab-testing/interactions/${interactionId}/feedback`, data)
  }
}

// 测试问题API
export const testQuestionApi = {
  // 创建测试问题
  createQuestions: (testId: number, questions: TestQuestionCreate[]): Promise<TestQuestion[]> => {
    return api.post(`/ab-testing/tests/${testId}/questions`, questions)
  },

  // 获取测试问题列表
  getQuestions: (testId: number): Promise<TestQuestion[]> => {
    return api.get(`/ab-testing/tests/${testId}/questions`)
  }
}

// 测试评估API
export const testEvaluationApi = {
  // 评估回答质量
  evaluateResponse: (data: {
    question_id: number
    interaction_id: number
    evaluator_id: number
    relevance_score?: number
    accuracy_score?: number
    completeness_score?: number
    clarity_score?: number
    helpfulness_score?: number
    overall_score?: number
    strengths?: string
    weaknesses?: string
    suggestions?: string
  }): Promise<any> => {
    return api.post('/ab-testing/evaluations', data)
  }
} 