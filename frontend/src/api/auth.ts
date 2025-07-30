import { api } from './index'
import axios from 'axios'

// 认证相关接口类型
export interface LoginRequest {
  username: string
  password: string
  remember_me?: boolean // 新增remember_me字段
}

export interface LoginResponse {
  access_token: string // 与后端保持一致
  token_type: string
  user: User
}

export interface User {
  id: number // 修改为number，与后端保持一致
  username: string
  email: string
  avatar?: string
  roles: Array<{id: number; name: string; description?: string}>
  permissions?: string[]
  profile?: UserProfile
}

export interface UserProfile {
  firstName?: string
  lastName?: string
  phone?: string
  department?: string
  title?: string
  bio?: string
  preferences?: UserPreferences
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'auto'
  language: string
  timezone: string
  notifications: NotificationSettings
}

export interface NotificationSettings {
  email: boolean
  push: boolean
  desktop: boolean
  sound: boolean
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
  confirmPassword: string
  firstName?: string
  lastName?: string
}

export interface RefreshTokenRequest {
  refreshToken: string
}

export interface ResetPasswordRequest {
  email: string
}

export interface ChangePasswordRequest {
  currentPassword: string
  newPassword: string
  confirmPassword: string
}

export interface UpdateProfileRequest {
  firstName?: string
  lastName?: string
  email?: string
  phone?: string
  department?: string
  title?: string
  bio?: string
  avatar?: string
}

// 认证API服务
export const authApi = {
  // 用户登录
  async login(username: string, password: string, rememberMe: boolean = false): Promise<LoginResponse> {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    if (rememberMe) {
      formData.append('remember_me', 'true');
    }

    // 直接使用axios发送请求，避免API拦截器的包装
    // 动态获取当前访问的主机名，确保API请求发送到同一主机
    const currentHost = window.location.hostname;
    const apiUrl = `http://${currentHost}:8000/api/auth/token`;
    console.log('Login API URL:', apiUrl); // 添加调试日志
    const response = await axios.post<LoginResponse>(apiUrl, formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    console.log('Login response:', response.data); // 添加调试日志
    return response.data; // 直接返回响应数据
  },

  // 用户注册
  async register(userData: RegisterRequest): Promise<User> {
    return api.post('/auth/register', userData)
  },

  // 刷新Token
  async refreshToken(refreshToken: string): Promise<LoginResponse> {
    return api.post('/auth/refresh', { refreshToken })
  },

  // 用户登出
  async logout(): Promise<void> {
    return api.post('/auth/logout')
  },

  // 获取当前用户信息
  async getCurrentUser(): Promise<User> {
    return api.get('/auth/me')
  },

  // 更新用户资料
  async updateProfile(data: UpdateProfileRequest): Promise<User> {
    return api.put('/auth/profile', data)
  },

  // 修改密码
  async changePassword(data: ChangePasswordRequest): Promise<void> {
    return api.post('/auth/change-password', data)
  },

  // 重置密码请求
  async requestPasswordReset(email: string): Promise<void> {
    return api.post('/auth/reset-password', { email })
  },

  // 确认重置密码
  async confirmPasswordReset(token: string, newPassword: string): Promise<void> {
    return api.post('/auth/reset-password/confirm', { token, newPassword })
  },

  // 验证邮箱
  async verifyEmail(token: string): Promise<void> {
    return api.post('/auth/verify-email', { token })
  },

  // 重新发送验证邮件
  async resendVerificationEmail(): Promise<void> {
    return api.post('/auth/resend-verification')
  },

  // 上传头像
  async uploadAvatar(file: File): Promise<{ avatarUrl: string }> {
    return api.upload('/auth/avatar', file)
  },

  // 删除头像
  async deleteAvatar(): Promise<void> {
    return api.delete('/auth/avatar')
  },

  // 获取用户权限
  async getUserPermissions(): Promise<string[]> {
    return api.get('/auth/permissions')
  },

  // 检查权限
  async checkPermission(permission: string): Promise<boolean> {
    const result = await api.get(`/auth/check-permission/${permission}`)
    return result.hasPermission
  },

  // 获取用户角色
  async getUserRoles(): Promise<string[]> {
    return api.get('/auth/roles')
  },

  // 更新用户偏好设置
  async updatePreferences(preferences: Partial<UserPreferences>): Promise<UserPreferences> {
    return api.put('/auth/preferences', preferences)
  },

  // 获取用户偏好设置
  async getPreferences(): Promise<UserPreferences> {
    return api.get('/auth/preferences')
  },

  // 启用/禁用双因素认证
  async toggleTwoFactorAuth(enabled: boolean): Promise<{ secret?: string; qrCode?: string }> {
    return api.post('/auth/2fa/toggle', { enabled })
  },

  // 验证双因素认证代码
  async verifyTwoFactorAuth(code: string): Promise<void> {
    return api.post('/auth/2fa/verify', { code })
  },

  // 获取登录历史
  async getLoginHistory(page = 1, pageSize = 20): Promise<{
    items: Array<{
      id: string
      ip: string
      userAgent: string
      location?: string
      timestamp: string
      success: boolean
    }>
    total: number
    page: number
    pageSize: number
  }> {
    return api.paginate('/auth/login-history', { page, pageSize })
  },

  // 登出所有设备
  async logoutAllDevices(): Promise<void> {
    return api.post('/auth/logout-all')
  },

  // 获取活跃会话
  async getActiveSessions(): Promise<Array<{
    id: string
    ip: string
    userAgent: string
    location?: string
    current: boolean
    lastActivity: string
  }>> {
    return api.get('/auth/sessions')
  },

  // 终止特定会话
  async terminateSession(sessionId: string): Promise<void> {
    return api.delete(`/auth/sessions/${sessionId}`)
  },
}

export default authApi