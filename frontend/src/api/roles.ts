import { api } from './index'
import type { PaginatedResponse, Role, RoleCreate, RoleUpdate } from '@/types'

export const roleApi = {
  /**
   * 获取角色列表
   * @param page 页码
   * @param pageSize 每页数量
   * @param search 搜索关键词 (角色名称或描述)
   */
  async getRoles(page: number = 1, pageSize: number = 10, search: string = ''): Promise<PaginatedResponse<Role>> {
    const response = await api.get<PaginatedResponse<Role>>('/roles/', {
      params: { page, page_size: pageSize, search }
    })
    return response
  },

  /**
   * 根据ID获取角色详情
   * @param roleId 角色ID
   */
  async getRoleById(roleId: number): Promise<Role> {
    const response = await api.get<Role>(`/roles/${roleId}`)
    return response
  },

  /**
   * 创建新角色
   * @param roleData 角色创建数据
   */
  async createRole(roleData: RoleCreate): Promise<Role> {
    const response = await api.post<Role>('/roles/', roleData)
    return response
  },

  /**
   * 更新角色
   * @param roleId 角色ID
   * @param roleData 角色更新数据
   */
  async updateRole(roleId: number, roleData: RoleUpdate): Promise<Role> {
    const response = await api.put<Role>(`/roles/${roleId}`, roleData)
    return response
  },

  /**
   * 删除角色
   * @param roleId 角色ID
   */
  async deleteRole(roleId: number): Promise<void> {
    await api.delete<void>(`/roles/${roleId}`)
  },

  /**
   * 更新角色权限
   * @param roleId 角色ID
   * @param permissions 权限名称列表
   */
  async updateRolePermissions(roleId: number, permissions: string[]): Promise<Role> {
    const response = await api.put<Role>(`/roles/${roleId}/permissions`, { permissions })
    return response
  },

  /**
   * 获取角色下的用户列表
   * @param roleId 角色ID
   */
  async getRoleUsers(roleId: number): Promise<string[]> {
    const response = await api.get<string[]>(`/roles/${roleId}/users`)
    return response
  }
} 