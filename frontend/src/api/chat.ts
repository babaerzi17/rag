import request from './index'

export interface ChatSession {
  id: number
  user_id: number
  title?: string
  kb_id?: number
  model_config?: any
  created_at: string
  updated_at?: string
}

export interface ChatMessage {
  id: number
  session_id: number
  role: 'user' | 'assistant'
  content: string
  sources?: any[]
  metadata?: any
  created_at: string
}

export interface ChatSessionCreate {
  title?: string
  kb_id?: number
  model_config?: any
}

export interface ChatMessageCreate {
  content: string
  include_history?: boolean
  provider?: string
  model?: string
  temperature?: number
  max_tokens?: number
  top_k?: number
}

export interface StreamChatRequest {
  session_id: number
  message: string
  include_history?: boolean
  provider?: string
  model?: string
  temperature?: number
  max_tokens?: number
  top_k?: number
}

export interface LLMProvider {
  [key: string]: {
    models: string[]
    connection: {
      success: boolean
      error?: string
    }
  }
}

// 聊天API
export const chatApi = {
  // 获取会话列表
  getSessions(params?: { skip?: number; limit?: number }) {
    return request.get<ChatSession[]>('/api/chat/sessions', { params })
  },

  // 创建会话
  createSession(data: ChatSessionCreate) {
    return request.post<ChatSession>('/api/chat/sessions', data)
  },

  // 获取会话详情
  getSession(id: number) {
    return request.get<ChatSession>(`/api/chat/sessions/${id}`)
  },

  // 删除会话
  deleteSession(id: number) {
    return request.delete(`/api/chat/sessions/${id}`)
  },

  // 获取消息历史
  getMessages(sessionId: number, params?: { skip?: number; limit?: number }) {
    return request.get<ChatMessage[]>(`/api/chat/sessions/${sessionId}/messages`, { params })
  },

  // 发送消息
  sendMessage(sessionId: number, data: ChatMessageCreate) {
    return request.post<ChatMessage>(`/api/chat/sessions/${sessionId}/messages`, data)
  },

  // 流式聊天
  streamChat(data: StreamChatRequest) {
    return request.post('/api/chat/stream', data)
  },

  // 获取可用提供商
  getProviders() {
    return request.get<LLMProvider>('/api/chat/providers')
  },

  // 测试连接
  testConnection(provider: string) {
    return request.post('/api/chat/test-connection', { provider })
  }
} 