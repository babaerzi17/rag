import api from './index'

// 文档相关类型定义
export interface Document {
  id: number
  title: string
  description?: string
  file_path: string
  file_type: string
  file_size: number
  status: 'processing' | 'completed' | 'failed'
  kb_id: number
  knowledge_base_name: string
  tags: string[]
  version: number
  created_at: string
  updated_at: string
}

export interface DocumentCreate {
  title: string
  description?: string
  kb_id: number
  tags?: string[]
}

export interface DocumentUpdate {
  title?: string
  description?: string
  tags?: string[]
}

export interface DocumentVersion {
  id: number
  version: number
  file_path: string
  file_size: number
  change_log?: string
  created_at: string
}

// 文档管理API
export const documentApi = {
  // 获取文档列表
  getDocuments: (params?: {
    page?: number
    page_size?: number
    kb_id?: number
    file_type?: string
    status?: string
    search?: string
  }): Promise<{
    items: Document[]
    total: number
    page: number
    page_size: number
  }> => {
    return api.get('/documents', { params })
  },

  // 获取文档详情
  getDocument: (id: number): Promise<Document> => {
    return api.get(`/documents/${id}`)
  },

  // 创建文档
  createDocument: (data: DocumentCreate): Promise<Document> => {
    return api.post('/documents', data)
  },

  // 更新文档
  updateDocument: (id: number, data: DocumentUpdate): Promise<Document> => {
    return api.put(`/documents/${id}`, data)
  },

  // 删除文档
  deleteDocument: (id: number): Promise<void> => {
    return api.delete(`/documents/${id}`)
  },

  // 上传文档
  uploadDocuments: (data: {
    kb_id: number
    title: string
    description?: string
    tags?: string[]
    files: File[]
  }): Promise<Document[]> => {
    const formData = new FormData()
    formData.append('kb_id', data.kb_id.toString())
    formData.append('title', data.title)
    if (data.description) {
      formData.append('description', data.description)
    }
    if (data.tags) {
      formData.append('tags', data.tags.join(','))
    }
    
    data.files.forEach((file, index) => {
      formData.append(`files`, file)
    })
    
    return api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 获取文档预览URL
  getDocumentPreview: (id: number): Promise<{ preview_url: string }> => {
    return api.get(`/documents/${id}/preview`)
  },

  // 获取文档下载URL
  getDocumentDownload: (id: number): Promise<{ download_url: string }> => {
    return api.get(`/documents/${id}/download`)
  },

  // 获取文档版本历史
  getDocumentVersions: (id: number): Promise<DocumentVersion[]> => {
    return api.get(`/documents/${id}/versions`)
  },

  // 恢复文档版本
  restoreVersion: (docId: number, versionId: number): Promise<void> => {
    return api.post(`/documents/${docId}/versions/${versionId}/restore`)
  },

  // 批量删除文档
  batchDeleteDocuments: (ids: number[]): Promise<void> => {
    return api.post('/documents/batch-delete', { ids })
  },

  // 批量移动文档
  batchMoveDocuments: (ids: number[], kbId: number): Promise<void> => {
    return api.post('/documents/batch-move', { ids, kb_id: kbId })
  },

  // 获取文档统计信息
  getDocumentStats: (): Promise<{
    total_documents: number
    total_size: number
    by_type: Record<string, number>
    by_status: Record<string, number>
  }> => {
    return api.get('/documents/stats')
  }
} 