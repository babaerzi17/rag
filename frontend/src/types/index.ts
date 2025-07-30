// 全局类型定义

// 用户类型
export interface User {
  id: number // 后端ID是Integer，这里改为number
  username: string
  email: string
  avatar?: string
  roles: string[]
  permissions: string[]
  full_name?: string // 与后端保持一致
  is_active: boolean // 新增字段
  // firstName?: string // 移除
  // lastName?: string // 移除
  phone?: string
  department?: string
  title?: string
}

// 创建用户请求类型
export interface UserCreate {
  username: string
  email: string
  password: string
  full_name?: string
}

// 更新用户请求类型
export interface UserUpdate {
  email?: string
  full_name?: string
  is_active?: boolean
  roles?: string[] // 更新角色可能需要单独接口或权限
  // 不包含密码更新，密码更新应该有单独接口
}

// 知识库类型
export interface KnowledgeBase {
  id: string
  name: string
  description: string
  type: string
  status: 'active' | 'inactive' | 'maintenance'
  color: string
  isPublic: boolean
  documents: number
  owner: {
    id: string
    name: string
    avatar?: string
  }
  createdAt: Date
  updatedAt: Date
}

// 文档类型
export interface Document {
  id: string
  name: string
  type: string
  size: number
  status: 'processing' | 'completed' | 'failed' | 'pending'
  progress: number
  knowledgeBase: KnowledgeBase
  uploader: User
  uploadedAt: Date
  chunks?: number
  keywords?: string[]
  error?: string
}

// 聊天消息类型
export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  type: 'text' | 'thinking' | 'error'
  content: string
  timestamp: Date
  sources?: Array<{
    id: string
    title: string
    excerpt: string
  }>
}

// 聊天会话类型
export interface ChatSession {
  id: string
  title: string
  updatedAt: Date
  messageCount: number
}

// API响应类型
export interface ApiResponse<T = any> {
  success: boolean
  data: T
  message?: string
  code?: string
}

// 分页响应类型
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}

// 路由元信息类型
export interface RouteMeta {
  title?: string
  icon?: string
  requiresAuth?: boolean
  permission?: string
}

// 主题类型
export type ThemeMode = 'light' | 'dark'

// 文件上传状态
export type UploadStatus = 'idle' | 'uploading' | 'success' | 'error'

// 表单验证规则类型
export type ValidationRule = (value: any) => boolean | string

// 通用选项类型
export interface SelectOption {
  text: string
  value: any
  disabled?: boolean
}

// 统计数据类型
export interface StatCard {
  title: string
  value: string | number
  change: string
  trend: 'up' | 'down'
  color: string
  icon: string
}

// 活动日志类型
export interface ActivityLog {
  id: string
  type: 'upload' | 'chat' | 'edit' | 'error'
  title: string
  description: string
  timestamp: Date
  status: string
}

// 系统状态类型
export interface SystemStatus {
  cpu: number
  memory: number
  storage: number
  status: 'healthy' | 'error'
}

// 快速操作类型
export interface QuickAction {
  title: string
  description: string
  icon: string
  color: string
  action: string
}

// 颜色选项类型
export interface ColorOption {
  name: string
  value: string
}

// 表格头部类型
export interface TableHeader {
  title: string
  key: string
  sortable?: boolean
  width?: string | number
  align?: 'start' | 'center' | 'end'
}

// 错误类型
export interface AppError {
  message: string
  code?: string
  status?: number
  details?: any
}

// 通知类型
export interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message?: string
  duration?: number
  persistent?: boolean
  actions?: Array<{
    label: string
    action: () => void
  }>
}

// 搜索参数类型
export interface SearchParams {
  query?: string
  page?: number
  pageSize?: number
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
  filters?: Record<string, any>
}

// 文件类型信息
export interface FileTypeInfo {
  extension: string
  mimeType: string
  icon: string
  color: string
  category: 'document' | 'image' | 'video' | 'audio' | 'archive' | 'other'
}

// 权限类型
export interface Permission {
  id: number
  name: string // 权限标识，如 menu:user_management
  menu_name: string // 菜单名称，如 "用户管理"
  description?: string // 权限描述
  menu_path?: string // 菜单路径，如 "/rbac/users"
  menu_icon?: string // 菜单图标
  parent_id?: number // 父菜单ID
  sort_order?: number // 排序
}

// 创建权限请求类型
export interface PermissionCreate {
  name: string
  menu_name: string
  description?: string
  menu_path?: string
  menu_icon?: string
  parent_id?: number
  sort_order?: number
}

// 角色类型
export interface Role {
  id: number // 修改为number类型，与后端保持一致
  name: string
  description?: string
  permissions: Permission[]
  userCount?: number
}

// 创建角色请求类型
export interface RoleCreate {
  name: string
  description?: string
}

// 更新角色请求类型
export interface RoleUpdate {
  name?: string
  description?: string
}

// 设置配置类型
export interface AppSettings {
  theme: ThemeMode
  language: string
  sidebarCollapsed: boolean
  autoSave: boolean
  notifications: boolean
  // 可以根据需要添加更多设置项
}

// 导出/导入类型
export interface ExportOptions {
  format: 'json' | 'csv' | 'xml' | 'pdf'
  includeMetadata: boolean
  dateRange?: {
    start: Date
    end: Date
  }
}

// 备份类型
export interface Backup {
  id: string
  name: string
  size: number
  type: 'manual' | 'automatic'
  status: 'completed' | 'failed' | 'in_progress'
  createdAt: Date
  createdBy?: User
}

// WebSocket消息类型
export interface WebSocketMessage {
  type: string
  data: any
  timestamp: Date
}

// 事件类型
export type AppEvent = 
  | { type: 'USER_LOGIN'; payload: { user: User } }
  | { type: 'USER_LOGOUT' }
  | { type: 'DOCUMENT_UPLOADED'; payload: { document: Document } }
  | { type: 'MESSAGE_SENT'; payload: { message: ChatMessage } }
  | { type: 'KNOWLEDGE_BASE_CREATED'; payload: { knowledgeBase: KnowledgeBase } }
  | { type: 'ERROR_OCCURRED'; payload: { error: AppError } }

// 全局常量类型
export interface AppConstants {
  MAX_FILE_SIZE: number
  SUPPORTED_FILE_TYPES: string[]
  DEFAULT_PAGE_SIZE: number
  API_TIMEOUT: number
  DEBOUNCE_DELAY: number
  AUTO_SAVE_INTERVAL: number
}

// 环境变量类型
export interface AppEnv {
  NODE_ENV: 'development' | 'production' | 'test'
  VITE_API_BASE_URL: string
  VITE_WS_URL: string
  VITE_APP_VERSION: string
  VITE_APP_NAME: string
}

// 本地存储键类型
export type StorageKey = 
  | 'user'
  | 'token'
  | 'refreshToken'
  | 'theme'
  | 'language'
  | 'sidebarCollapsed'
  | 'chatHistory'
  | 'preferences'
  | 'recentDocuments'
  | 'searchHistory'