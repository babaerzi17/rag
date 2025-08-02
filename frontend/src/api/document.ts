import api from './index'

// 文档相关类型定义
export interface Document {
  id: number
  title: string
  description?: string
  file_path: string
  file_type: string
  file_size: number
  status: 'processing' | 'completed' | 'failed' | 'pending'
  knowledge_base_id: number
  knowledge_base?: {
    id: number
    name: string
    color?: string
  }
  tags?: string[]
  page_count?: number
  chunk_count?: number
  doc_metadata?: any
  created_at: string
  updated_at: string
  created_by: number
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

export interface DocumentStats {
  total_documents: number
  total_size: number
  by_status: Record<string, number>
  by_type: Record<string, number>
}

export interface BatchUploadRequest {
  kb_id: number
  description?: string
  tags?: string
  files: File[]
}

export interface ImportFromDirectoryRequest {
  kb_id: number
  directory_path: string
  recursive?: boolean
  description?: string
  tags?: string
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
  }): Promise<Document[]> => {
    return api.get('/documents', { params })
  },

  // 获取文档详情
  getDocument: (id: number): Promise<Document> => {
    return api.get(`/documents/${id}`)
  },

  // 创建文档（单个文件上传）
  createDocument: (data: {
    kb_id: number
    title: string
    description?: string
    tags?: string
    file: File
  }): Promise<Document> => {
    const formData = new FormData()
    formData.append('kb_id', data.kb_id.toString())
    formData.append('title', data.title)
    if (data.description) {
      formData.append('description', data.description)
    }
    if (data.tags) {
      formData.append('tags', data.tags)
    }
    formData.append('file', data.file)
    
    return api.post('/documents', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 更新文档
  updateDocument: (id: number, data: DocumentUpdate): Promise<Document> => {
    const formData = new FormData()
    if (data.title !== undefined) {
      formData.append('title', data.title)
    }
    if (data.description !== undefined) {
      formData.append('description', data.description)
    }
    if (data.tags !== undefined) {
      formData.append('tags', Array.isArray(data.tags) ? data.tags.join(',') : data.tags)
    }
    
    return api.put(`/documents/${id}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 删除文档
  deleteDocument: (id: number): Promise<void> => {
    return api.delete(`/documents/${id}`)
  },

  // 批量上传文档
  batchUploadDocuments: (data: BatchUploadRequest): Promise<Document[]> => {
    const formData = new FormData()
    formData.append('kb_id', data.kb_id.toString())
    
    if (data.description) {
      formData.append('description', data.description)
    }
    if (data.tags) {
      formData.append('tags', data.tags)
    }
    
    data.files.forEach((file) => {
      formData.append('files', file)
    })
    
    return api.post('/documents/batch-upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 从目录导入文档
  importFromDirectory: (data: ImportFromDirectoryRequest): Promise<{
    message: string
    imported_files: string[]
    failed_files: string[]
  }> => {
    const formData = new FormData()
    formData.append('kb_id', data.kb_id.toString())
    formData.append('directory_path', data.directory_path)
    formData.append('recursive', data.recursive ? 'true' : 'false')
    
    if (data.description) {
      formData.append('description', data.description)
    }
    if (data.tags) {
      formData.append('tags', data.tags)
    }
    
    return api.post('/documents/import-from-directory', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 批量删除文档
  batchDeleteDocuments: (ids: number[]): Promise<{
    message: string
    deleted_count: number
    failed_count: number
  }> => {
    return api.delete('/documents/batch', { data: ids })
  },

  // 获取文档统计信息
  getDocumentStats: (): Promise<DocumentStats> => {
    return api.get('/documents/stats')
  },

  // 获取文档预览URL（保留原有功能）
  getDocumentPreview: (id: number): Promise<{ preview_url: string }> => {
    return api.get(`/documents/${id}/preview`)
  },

  // 获取文档下载URL（保留原有功能）
  getDocumentDownload: (id: number): Promise<{ download_url: string }> => {
    return api.get(`/documents/${id}/download`)
  },

  // 批量创建文档
  batchCreateDocuments: (kb_id: number, documents: Array<{
    file_id: number
    title: string
    description?: string
    tags?: string
  }>): Promise<Document[]> => {
    return api.post('/documents/batch-create', {
      kb_id,
      documents
    })
  }
} 