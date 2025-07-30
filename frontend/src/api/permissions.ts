import { api } from './index'
import type { PaginatedResponse, Permission, PermissionCreate } from '@/types'

export const permissionApi = {
  /**
   * 获取权限列表
   * @param page 页码
   * @param pageSize 每页数量
   * @param search 搜索关键词 (权限名称)
   */
  async getPermissions(page: number = 1, pageSize: number = 10, search: string = ''): Promise<PaginatedResponse<Permission>> {
    const response = await api.get<PaginatedResponse<Permission>>('/permissions/', {
      params: { page, page_size: pageSize, search }
    })
    return response
  },

  /**
   * 根据ID获取权限详情
   * @param permissionId 权限ID
   */
  async getPermissionById(permissionId: number): Promise<Permission> {
    const response = await api.get<Permission>(`/permissions/${permissionId}`)
    return response
  },

  /**
   * 创建新权限
   * @param permissionData 权限创建数据
   */
  async createPermission(permissionData: PermissionCreate): Promise<Permission> {
    const response = await api.post<Permission>('/permissions/', permissionData)
    return response
  },

  /**
   * 更新权限
   * @param permissionId 权限ID
   * @param permissionData 权限更新数据
   */
  async updatePermission(permissionId: number, permissionData: PermissionCreate): Promise<Permission> {
    const response = await api.put<Permission>(`/permissions/${permissionId}`, permissionData)
    return response
  },

  /**
   * 删除权限
   * @param permissionId 权限ID
   */
  async deletePermission(permissionId: number): Promise<void> {
    await api.delete<void>(`/permissions/${permissionId}`)
  }
} 