import { api } from './index'
import type { PaginatedResponse, User, UserCreate, UserUpdate } from '@/types'

export const userApi = {
  /**
   * 获取用户列表
   * @param page 页码
   * @param pageSize 每页数量
   * @param search 搜索关键词 (用户名或邮箱)
   */
  async getUsers(page: number = 1, pageSize: number = 10, search: string = ''): Promise<PaginatedResponse<User>> {
    const response = await api.get<PaginatedResponse<User>>('/users/', {
      params: { page, page_size: pageSize, search }
    })
    return response
  },

  /**
   * 根据ID获取用户详情
   * @param userId 用户ID
   */
  async getUserById(userId: number): Promise<User> {
    const response = await api.get<User>(`/users/${userId}`)
    return response
  },

  /**
   * 创建新用户
   * @param userData 用户创建数据
   */
  async createUser(userData: UserCreate): Promise<User> {
    const response = await api.post<User>('/users/', userData)
    return response
  },

  /**
   * 更新用户
   * @param userId 用户ID
   * @param userData 用户更新数据
   */
  async updateUser(userId: number, userData: UserUpdate): Promise<User> {
    const response = await api.put<User>(`/users/${userId}`, userData)
    return response
  },

  /**
   * 删除用户
   * @param userId 用户ID
   */
  async deleteUser(userId: number): Promise<void> {
    await api.delete<void>(`/users/${userId}`)
  },

  /**
   * 更新用户角色
   * @param userId 用户ID
   * @param roleNames 角色名称列表
   */
  async updateUserRoles(userId: number, roleNames: string[]): Promise<User> {
    const response = await api.put<User>(`/users/${userId}/roles`, { roles: roleNames })
    return response
  },

  /**
   * 重置用户密码
   * @param userId 用户ID
   * @param newPassword 新密码
   */
  async resetUserPassword(userId: number, newPassword: string): Promise<void> {
    await api.post<void>(`/users/${userId}/reset-password`, { new_password: newPassword })
  }
} 