import { defineStore } from 'pinia';
import axios from 'axios';
import { authApi } from '@/api/auth'; // 导入authApi

interface User {
  id: number;
  username: string;
  email?: string;
  full_name?: string;
  roles: Array<{id: number; name: string; description?: string}>;
  permissions?: string[];
}

interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: JSON.parse(localStorage.getItem('user') || 'null') as User | null,
    permissions: JSON.parse(localStorage.getItem('permissions') || '[]') as string[],
    isLoading: false,
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.token,
    userRoles: (state) => state.user?.roles.map(role => role.name) || [],
    isAdmin: (state) => state.user?.roles.some(role => role.name === 'admin') || false,
  },
  
  actions: {
    // 登录
    async login(username: string, password: string, rememberMe: boolean = false) {
      this.isLoading = true;
      try {
        console.log('Attempting login for user:', username);
        const response = await authApi.login(username, password, rememberMe); // 传递rememberMe状态
        console.log('Login response received:', response);

        const { access_token, user } = response;
        
        // 保存认证信息
        this.token = access_token;
        this.user = user;
        
        // 持久化存储
        localStorage.setItem('token', access_token);
        localStorage.setItem('user', JSON.stringify(user));
        // rememberMe 状态已经在Login.vue中处理了rememberedUsername的存储
        
        // 设置axios默认header
        axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
        
        // 获取用户权限
        await this.fetchPermissions();
        
        return { success: true };
      } catch (error: any) {
        console.error('Login failed:', error);
        const message = error.response?.data?.detail || '登录失败，请检查用户名和密码';
        throw new Error(message);
      } finally {
        this.isLoading = false;
      }
    },

    // 开发环境模拟登录
    async mockLogin(credentials: { username: string; password: string }) {
      // 模拟API延迟
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // 模拟登录验证
      if (credentials.username === 'admin' && credentials.password === 'admin') {
        const mockUser: User = {
          id: 1,
          username: 'admin',
          email: 'admin@example.com',
          full_name: '系统管理员',
          roles: [
            {id: 1, name: 'admin', description: '系统管理员'},
            {id: 2, name: 'user', description: '普通用户'}
          ]
        };
        
        const mockToken = 'mock-jwt-token-' + Date.now();
        
        this.token = mockToken;
        this.user = mockUser;
        
        // 持久化存储
        localStorage.setItem('token', mockToken);
        localStorage.setItem('user', JSON.stringify(mockUser));
        
        // 模拟管理员权限
        this.permissions = [
          'dashboard.read',
          'knowledge.library.read',
          'knowledge.library.write',
          'document.read',
          'document.write',
          'chat.use',
          'model.manage',
          'rbac.read',
          'rbac.user.read',
          'rbac.user.write',
          'rbac.role.read',
          'rbac.role.write',
          'rbac.permission.read',
          'rbac.permission.write',
          'settings.read',
          'settings.write'
        ];
        
        localStorage.setItem('permissions', JSON.stringify(this.permissions));
        
        // 设置axios默认header
        axios.defaults.headers.common['Authorization'] = `Bearer ${mockToken}`;
        
        return { success: true };
      } else if (credentials.username === 'user' && credentials.password === 'user') {
        const mockUser: User = {
          id: 2,
          username: 'user',
          email: 'user@example.com',
          full_name: '普通用户',
          roles: [
            {id: 2, name: 'user', description: '普通用户'}
          ]
        };
        
        const mockToken = 'mock-jwt-token-user-' + Date.now();
        
        this.token = mockToken;
        this.user = mockUser;
        
        localStorage.setItem('token', mockToken);
        localStorage.setItem('user', JSON.stringify(mockUser));
        
        // 模拟普通用户权限
        this.permissions = [
          'dashboard.read',
          'knowledge.library.read',
          'document.read',
          'chat.use'
        ];
        
        localStorage.setItem('permissions', JSON.stringify(this.permissions));
        
        axios.defaults.headers.common['Authorization'] = `Bearer ${mockToken}`;
        
        return { success: true };
      } else {
        return { success: false, message: '用户名或密码错误' };
      }
    },

    // 获取用户权限
    async fetchPermissions() {
      if (!this.token) return;
      
      try {
        const currentHost = window.location.hostname;
        const apiUrl = `http://${currentHost}:8000/api/auth/user-permissions`;
        const response = await axios.get<string[]>(apiUrl, {
          headers: { Authorization: `Bearer ${this.token}` },
          params: { username: this.user?.username }
        });
        
        this.permissions = response.data;
        localStorage.setItem('permissions', JSON.stringify(this.permissions));
      } catch (error) {
        console.error('Fetch permissions failed:', error);
        // 权限获取失败时不清除认证信息，使用默认权限
        console.log('Using cached permissions');
      }
    },

    // 检查权限
    hasPermission(permission: string): boolean {
      return this.permissions.includes(permission);
    },

    // 检查多个权限（需要全部拥有）
    hasAllPermissions(permissions: string[]): boolean {
      return permissions.every(perm => this.hasPermission(perm));
    },

    // 检查多个权限（拥有其中任一即可）
    hasAnyPermission(permissions: string[]): boolean {
      return permissions.some(perm => this.hasPermission(perm));
    },

    // 检查角色
    hasRole(role: string): boolean {
      return this.userRoles.includes(role);
    },

    // 退出登录
    logout() {
      this.token = null;
      this.user = null;
      this.permissions = [];
      
      // 清除存储
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      localStorage.removeItem('permissions');
      localStorage.removeItem('rememberMe');
      // 注意：不删除rememberedUsername和rememberedPassword，保持"记住我"功能
      
      // 清除axios默认header
      delete axios.defaults.headers.common['Authorization'];
    },

    // 初始化认证状态（应用启动时调用）
    async initAuth() {
      const token = localStorage.getItem('token');
      if (token) {
        this.token = token;
        await this.fetchPermissions();
      }
    },

    // 刷新用户信息
    async refreshUserInfo() {
      if (!this.token) return;
      
      try {
        const currentHost = window.location.hostname;
        const apiUrl = `http://${currentHost}:8000/api/auth/me`;
        const response = await axios.get<User>(apiUrl, {
          headers: { Authorization: `Bearer ${this.token}` }
        });
        
        this.user = response.data;
        localStorage.setItem('user', JSON.stringify(response.data));
      } catch (error) {
        console.error('Refresh user info failed:', error);
        this.logout();
      }
    },

    // 获取用户信息（新增方法）
    async getUserInfo() {
      if (!this.token) return;
      
      try {
        const currentHost = window.location.hostname;
        const apiUrl = `http://${currentHost}:8000/api/auth/me`;
        const response = await axios.get<User>(apiUrl, {
          headers: { Authorization: `Bearer ${this.token}` }
        });
        
        this.user = response.data;
        localStorage.setItem('user', JSON.stringify(response.data));
        return response.data;
      } catch (error) {
        console.error('Get user info failed:', error);
        throw error;
      }
    }
  },
});