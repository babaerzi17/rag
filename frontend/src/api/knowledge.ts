import apiClient from './index'
import type { PaginatedResponse } from '@/types'

// 知识库相关接口类型
export interface KnowledgeBase {
  id: number // 后端返回数字类型
  name: string
  description: string
  type?: string // 标记为可选
  status: 'active' | 'inactive' | 'maintenance'
  color?: string // 标记为可选
  is_public: boolean // 匹配后端字段名 is_public
  embedding_model?: string // 添加后端返回的字段
  vector_store?: string // 添加后端返回的字段
  kb_metadata?: Record<string, any> // 修改为kb_metadata以匹配后端
  created_by?: number // 添加后端返回的字段
  created_at: string // 匹配后端字段名
  updated_at: string // 匹配后端字段名
  tags?: string[]
  
  // 前端需要但后端不返回的字段 - 在组件中处理
  owner?: {
    id: string
    name?: string
    avatar?: string
  }
}

export interface KnowledgeBaseSettings {
  chunkSize: number
  chunkOverlap: number
  enableOCR: boolean
  enableAutoTag: boolean
  allowedFileTypes: string[]
  maxFileSize: number
  vectorModel: string
  embeddingDimensions: number
  indexType: string
  retrievalStrategy: string
}

export interface KnowledgeBaseStats {
  documentCount: number
  chunkCount: number
  totalSize: number
  lastIndexed?: string
  queryCount: number
  avgResponseTime: number
}

export interface CreateKnowledgeBaseRequest {
  name: string
  description: string
  type: string
  color?: string
  isPublic?: boolean
  settings?: Partial<KnowledgeBaseSettings>
  tags?: string[]
}

export interface UpdateKnowledgeBaseRequest {
  name?: string
  description?: string
  type?: string
  color?: string
  isPublic?: boolean
  settings?: Partial<KnowledgeBaseSettings>
  tags?: string[]
}

export interface KnowledgeBaseSearchParams {
  page?: number
  pageSize?: number
  search?: string
  type?: string
  status?: string
  isPublic?: boolean
  ownerId?: string
  tags?: string[]
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
}

// 知识库API服务
export const knowledgeApi = {
  // 获取知识库列表
  async getKnowledgeBases(params?: KnowledgeBaseSearchParams): Promise<KnowledgeBase[]> {
    // 后端直接返回数组，不是包装的ApiResponse格式
    const response = await apiClient.get<KnowledgeBase[]>('/knowledge-bases/', { params })
    return response.data
  },

  // 获取知识库详情
  async getKnowledgeBase(id: string): Promise<KnowledgeBase> {
    return apiClient.get(`/knowledge-bases/${id}`)
  },

  // 创建知识库
  async createKnowledgeBase(data: CreateKnowledgeBaseRequest): Promise<KnowledgeBase> {
    return apiClient.post('/knowledge-bases', data)
  },

  // 更新知识库
  async updateKnowledgeBase(id: string, data: UpdateKnowledgeBaseRequest): Promise<KnowledgeBase> {
    return apiClient.put(`/knowledge-bases/${id}`, data)
  },

  // 删除知识库
  async deleteKnowledgeBase(id: string): Promise<void> {
    return apiClient.delete(`/knowledge-bases/${id}`)
  },

  // 复制知识库
  async duplicateKnowledgeBase(id: string, name: string): Promise<KnowledgeBase> {
    return apiClient.post(`/knowledge-bases/${id}/duplicate`, { name })
  },

  // 导出知识库
  async exportKnowledgeBase(id: string, format: 'json' | 'csv' | 'xml' = 'json'): Promise<void> {
    return apiClient.download(`/knowledge-bases/${id}/export?format=${format}`, `knowledge-base-${id}.${format}`)
  },

  // 导入知识库
  async importKnowledgeBase(file: File, name: string): Promise<KnowledgeBase> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('name', name)
    return apiClient.upload('/knowledge-bases/import', formData)
  },

  // 获取知识库统计信息
  async getKnowledgeBaseStats(id: string): Promise<KnowledgeBaseStats> {
    return apiClient.get(`/knowledge-bases/${id}/stats`)
  },

  // 重建知识库索引
  async rebuildIndex(id: string): Promise<{ taskId: string }> {
    return apiClient.post(`/knowledge-bases/${id}/rebuild-index`)
  },

  // 获取索引状态
  async getIndexStatus(id: string): Promise<{
    status: 'idle' | 'indexing' | 'completed' | 'failed'
    progress: number
    message?: string
    startedAt?: string
    completedAt?: string
  }> {
    return apiClient.get(`/knowledge-bases/${id}/index-status`)
  },

  // 清空知识库
  async clearKnowledgeBase(id: string): Promise<void> {
    return apiClient.post(`/knowledge-bases/${id}/clear`)
  },

  // 获取知识库类型选项
  async getKnowledgeBaseTypes(): Promise<Array<{
    value: string
    label: string
    description: string
    icon: string
  }>> {
    return apiClient.get('/knowledge-bases/types')
  },

  // 获取向量模型选项
  async getVectorModels(): Promise<Array<{
    id: string
    name: string
    description: string
    dimensions: number
    languages: string[]
    performance: {
      accuracy: number
      speed: number
      memoryUsage: number
    }
  }>> {
    return apiClient.get('/knowledge-bases/vector-models')
  },

  // 测试知识库查询
  async testQuery(id: string, query: string, options?: {
    topK?: number
    minScore?: number
    includeMetadata?: boolean
  }): Promise<{
    results: Array<{
      content: string
      score: number
      metadata?: Record<string, any>
      source?: {
        documentId: string
        documentName: string
        chunkIndex: number
      }
    }>
    queryTime: number
    totalResults: number
  }> {
    return apiClient.post(`/knowledge-bases/${id}/test-query`, { query, ...options })
  },

  // 获取知识库权限
  async getKnowledgeBasePermissions(id: string): Promise<{
    canRead: boolean
    canWrite: boolean
    canDelete: boolean
    canShare: boolean
    canManage: boolean
  }> {
    return apiClient.get(`/knowledge-bases/${id}/permissions`)
  },

  // 分享知识库
  async shareKnowledgeBase(id: string, users: Array<{
    userId: string
    permission: 'read' | 'write' | 'manage'
  }>): Promise<void> {
    return apiClient.post(`/knowledge-bases/${id}/share`, { users })
  },

  // 获取知识库分享信息
  async getKnowledgeBaseSharing(id: string): Promise<{
    isPublic: boolean
    publicLink?: string
    sharedUsers: Array<{
      userId: string
      userName: string
      userAvatar?: string
      permission: string
      sharedAt: string
    }>
  }> {
    return apiClient.get(`/knowledge-bases/${id}/sharing`)
  },

  // 更新分享权限
  async updateSharingPermission(id: string, userId: string, permission: string): Promise<void> {
    return apiClient.put(`/knowledge-bases/${id}/sharing/${userId}`, { permission })
  },

  // 移除分享
  async removeSharing(id: string, userId: string): Promise<void> {
    return apiClient.delete(`/knowledge-bases/${id}/sharing/${userId}`)
  },

  // 生成公开链接
  async generatePublicLink(id: string, expiresAt?: string): Promise<{ publicLink: string }> {
    return apiClient.post(`/knowledge-bases/${id}/public-link`, { expiresAt })
  },

  // 撤销公开链接
  async revokePublicLink(id: string): Promise<void> {
    return apiClient.delete(`/knowledge-bases/${id}/public-link`)
  },

  // 获取知识库活动日志
  async getKnowledgeBaseActivity(id: string, params?: {
    page?: number
    pageSize?: number
    actionType?: string
    userId?: string
    startDate?: string
    endDate?: string
  }): Promise<PaginatedResponse<{
    id: string
    action: string
    description: string
    user: {
      id: string
      name: string
      avatar?: string
    }
    metadata?: Record<string, any>
    timestamp: string
  }>> {
    return apiClient.paginate(`/knowledge-bases/${id}/activity`, params)
  },

  // 获取知识库备份列表
  async getKnowledgeBaseBackups(id: string): Promise<Array<{
    id: string
    name: string
    size: number
    type: 'manual' | 'automatic'
    status: 'completed' | 'failed' | 'in_progress'
    createdAt: string
    createdBy?: {
      id: string
      name: string
    }
  }>> {
    return apiClient.get(`/knowledge-bases/${id}/backups`)
  },

  // 创建知识库备份
  async createKnowledgeBaseBackup(id: string, name?: string): Promise<{ backupId: string }> {
    return apiClient.post(`/knowledge-bases/${id}/backups`, { name })
  },

  // 恢复知识库备份
  async restoreKnowledgeBaseBackup(id: string, backupId: string): Promise<{ taskId: string }> {
    return apiClient.post(`/knowledge-bases/${id}/backups/${backupId}/restore`)
  },

  // 删除知识库备份
  async deleteKnowledgeBaseBackup(id: string, backupId: string): Promise<void> {
    return apiClient.delete(`/knowledge-bases/${id}/backups/${backupId}`)
  },

  // 下载知识库备份
  async downloadKnowledgeBaseBackup(id: string, backupId: string): Promise<void> {
    return apiClient.download(`/knowledge-bases/${id}/backups/${backupId}/download`, `kb-backup-${backupId}.zip`)
  },
}

export default knowledgeApi