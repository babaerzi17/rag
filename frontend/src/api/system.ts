import api from './index'

// 系统监控相关类型定义
export interface SystemMetrics {
  cpu_usage: number
  memory_usage: number
  disk_usage: number
  network_io: {
    bytes_sent: number
    bytes_recv: number
  }
  uptime: number
  active_connections: number
}

export interface ServiceStatus {
  name: string
  status: 'healthy' | 'warning' | 'error'
  response_time: number
  last_check: string
  details?: string
}

export interface SystemStats {
  total_users: number
  total_knowledge_bases: number
  total_documents: number
  total_chunks: number
  total_queries: number
  active_sessions: number
  system_uptime: number
}

export interface PerformanceMetrics {
  api_response_time: {
    avg: number
    p95: number
    p99: number
  }
  error_rate: number
  request_count: number
  success_rate: number
}

export interface ModelMetrics {
  model_name: string
  total_calls: number
  success_calls: number
  failed_calls: number
  avg_response_time: number
  total_tokens: number
  cost: number
  last_used: string
}

export interface LogEntry {
  id: number
  timestamp: string
  level: 'debug' | 'info' | 'warning' | 'error'
  module: string
  message: string
  user?: string
  ip?: string
  details?: Record<string, any>
}

export interface LogFilters {
  level?: string
  module?: string
  date_range?: [string, string]
  user?: string
  search?: string
  page?: number
  page_size?: number
}

export interface LogListResponse {
  logs: LogEntry[]
  total: number
  page: number
  page_size: number
}

export interface BackupInfo {
  id: number
  filename: string
  size: number
  type: 'full' | 'incremental'
  status: 'completed' | 'in_progress' | 'failed'
  created_at: string
  completed_at?: string
  error_message?: string
}

export interface BackupCreate {
  type: 'full' | 'incremental'
  description?: string
}

// 系统管理API
export const systemApi = {
  // 获取系统指标
  getSystemMetrics: (): Promise<SystemMetrics> => {
    return api.get('/system/metrics')
  },

  // 获取服务状态
  getServiceStatus: (): Promise<ServiceStatus[]> => {
    return api.get('/system/services/status')
  },

  // 获取系统统计
  getSystemStats: (): Promise<SystemStats> => {
    return api.get('/system/stats')
  },

  // 获取性能指标
  getPerformanceMetrics: (params?: {
    time_range?: string
    service?: string
  }): Promise<PerformanceMetrics> => {
    return api.get('/system/performance', { params })
  },

  // 获取模型使用统计
  getModelMetrics: (params?: {
    time_range?: string
    model_name?: string
  }): Promise<ModelMetrics[]> => {
    return api.get('/system/models/metrics', { params })
  },

  // 获取日志列表
  getLogs: (params?: LogFilters): Promise<LogListResponse> => {
    return api.get('/system/logs', { params })
  },

  // 导出日志
  exportLogs: (params?: LogFilters): Promise<Blob> => {
    return api.get('/system/logs/export', { 
      params,
      responseType: 'blob'
    })
  },

  // 清理日志
  clearLogs: (params?: {
    before_date?: string
    level?: string
  }): Promise<void> => {
    return api.post('/system/logs/clear', params)
  },

  // 获取备份列表
  getBackups: (): Promise<BackupInfo[]> => {
    return api.get('/system/backups')
  },

  // 创建备份
  createBackup: (data: BackupCreate): Promise<BackupInfo> => {
    return api.post('/system/backups', data)
  },

  // 下载备份
  downloadBackup: (id: number): Promise<Blob> => {
    return api.get(`/system/backups/${id}/download`, {
      responseType: 'blob'
    })
  },

  // 删除备份
  deleteBackup: (id: number): Promise<void> => {
    return api.delete(`/system/backups/${id}`)
  },

  // 恢复备份
  restoreBackup: (id: number): Promise<void> => {
    return api.post(`/system/backups/${id}/restore`)
  },

  // 获取系统配置
  getSystemConfig: (): Promise<Record<string, any>> => {
    return api.get('/system/config')
  },

  // 更新系统配置
  updateSystemConfig: (config: Record<string, any>): Promise<void> => {
    return api.put('/system/config', config)
  },

  // 获取系统健康检查
  getHealthCheck: (): Promise<{
    status: 'healthy' | 'unhealthy'
    checks: Array<{
      name: string
      status: 'healthy' | 'unhealthy'
      response_time: number
      details?: string
    }>
  }> => {
    return api.get('/system/health')
  },

  // 重启服务
  restartService: (serviceName: string): Promise<void> => {
    return api.post(`/system/services/${serviceName}/restart`)
  },

  // 获取实时监控数据
  getRealtimeMetrics: (): Promise<{
    timestamp: string
    metrics: SystemMetrics
    performance: PerformanceMetrics
  }> => {
    return api.get('/system/realtime')
  }
} 