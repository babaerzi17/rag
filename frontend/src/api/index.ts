import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from 'axios'
import { useAuthStore } from '@/stores/auth'

// API基础配置
// 动态获取当前访问的主机名，确保API请求发送到同一主机
const currentHost = window.location.hostname
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || `http://${currentHost}:8000/api`

// 创建axios实例
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    
    // 添加认证token
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    
    // 添加请求ID用于追踪
    config.headers['X-Request-ID'] = generateRequestId()
    
    console.log('API Request:', {
      method: config.method?.toUpperCase(),
      url: config.url,
      data: config.data,
    })
    
    return config
  },
  (error) => {
    console.error('Request Error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    console.log('API Response:', {
      status: response.status,
      url: response.config.url,
      data: response.data,
    })
    
    return response
  },
  async (error) => {
    const authStore = useAuthStore()
    
    console.error('Response Error:', {
      status: error.response?.status,
      url: error.config?.url,
      message: error.message,
      data: error.response?.data,
    })
    
    // 处理认证错误 (401 Unauthorized)
    if (error.response?.status === 401) {
      console.log('401 Unauthorized: Logging out user and redirecting to login.')
      authStore.logout()
      window.location.href = '/auth/login'
    }
    
    // 处理其他HTTP错误
    const errorMessage = getErrorMessage(error)
    throw new ApiError(
      errorMessage,
      error.response?.status || 0,
      error.response?.data
    )
  }
)

// 生成请求ID
function generateRequestId(): string {
  return Math.random().toString(36).substring(2, 15) + 
         Math.random().toString(36).substring(2, 15)
}

// 获取错误消息
function getErrorMessage(error: any): string {
  // 优先从FastAPI的detail字段获取
  if (error.response?.data?.detail) {
    return error.response.data.detail
  }

  if (error.response?.data?.message) {
    return error.response.data.message
  }
  
  if (error.response?.data?.error) {
    return error.response.data.error
  }
  
  if (error.message) {
    return error.message
  }
  
  return '网络请求失败，请稍后重试'
}

// 自定义API错误类
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: any
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

// API响应类型
export interface ApiResponse<T = any> {
  success: boolean
  data: T
  message?: string
  code?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}

// 通用API方法
export const api = {
  // GET请求
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await apiClient.get<ApiResponse<T>>(url, config)
    return response.data.data
  },

  // POST请求
  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await apiClient.post<ApiResponse<T>>(url, data, config)
    return response.data.data
  },

  // PUT请求
  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await apiClient.put<ApiResponse<T>>(url, data, config)
    return response.data.data
  },

  // PATCH请求
  async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await apiClient.patch<ApiResponse<T>>(url, data, config)
    return response.data.data
  },

  // DELETE请求
  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await apiClient.delete<ApiResponse<T>>(url, config)
    return response.data.data
  },

  // 文件上传
  async upload<T = any>(
    url: string,
    file: File | FormData,
    config?: AxiosRequestConfig & {
      onUploadProgress?: (progressEvent: any) => void
    }
  ): Promise<T> {
    const formData = file instanceof FormData ? file : new FormData()
    if (file instanceof File) {
      formData.append('file', file)
    }

    const response = await apiClient.post<ApiResponse<T>>(url, formData, {
      ...config,
      headers: {
        ...config?.headers,
        'Content-Type': 'multipart/form-data',
      },
    })
    
    return response.data.data
  },

  // 文件下载
  async download(
    url: string,
    filename?: string,
    config?: AxiosRequestConfig
  ): Promise<void> {
    const response = await apiClient.get(url, {
      ...config,
      responseType: 'blob',
    })

    const blob = new Blob([response.data])
    const downloadUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = filename || 'download'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(downloadUrl)
  },

  // 分页请求
  async paginate<T = any>(
    url: string,
    params?: {
      page?: number
      pageSize?: number
      search?: string
      sort?: string
      filter?: Record<string, any>
    },
    config?: AxiosRequestConfig
  ): Promise<PaginatedResponse<T>> {
    const response = await apiClient.get<ApiResponse<PaginatedResponse<T>>>(url, {
      ...config,
      params: {
        page: 1,
        pageSize: 20,
        ...params,
      },
    })
    
    return response.data.data
  },
}

export default apiClient