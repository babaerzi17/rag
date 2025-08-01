import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app' // 导入 appStore

// 导入布局组件
const MainLayout = () => import('@/components/common/MainLayout.vue')
const AuthLayout = () => import('@/components/common/AuthLayout.vue')

// 导入页面组件
const MainHome = () => import('@/views/MainHome.vue')
const Login = () => import('@/views/auth/Login.vue')
const KnowledgeManagement = () => import('@/views/knowledge/KnowledgeManagement.vue')
const DocumentManagement = () => import('@/views/document/DocumentManagement.vue')
const ChatInterface = () => import('@/views/chat/ChatInterface.vue')
const ModelManagement = () => import('@/views/model/ModelManagement.vue')
const UserManagement = () => import('@/views/rbac/UserManagement.vue')
const RoleManagement = () => import('@/views/rbac/RoleManagement.vue')
const PermissionManagement = () => import('@/views/rbac/PermissionManagement.vue')
const Settings = () => import('@/views/settings/Settings.vue')
const Unauthorized = () => import('@/views/Unauthorized.vue')

// 定义所有菜单路由
const menuRoutes = [
  { path: '/knowledge', name: 'Knowledge', component: () => import('@/views/knowledge/KnowledgeManagement.vue'), meta: { permission: 'menu:knowledge' } },
  { path: '/document', name: 'Document', component: () => import('@/views/document/DocumentManagement.vue'), meta: { permission: 'menu:document' } },
  { path: '/chat', name: 'Chat', component: () => import('@/views/chat/ChatInterface.vue'), meta: { permission: 'menu:chat' } },
  { path: '/model', name: 'Model', component: () => import('@/views/model/ModelManagement.vue'), meta: { permission: 'menu:model' } },
  { path: '/settings', name: 'Settings', component: () => import('@/views/settings/Settings.vue'), meta: { permission: 'menu:settings' } },
  // 添加更多基于init.sql的菜单
];

const routes: RouteRecordRaw[] = [
  {
    path: '/auth',
    component: AuthLayout,
    children: [
      {
        path: 'login',
        name: 'Login',
        component: Login,
        meta: { title: '登录' }
      },
    ]
  },
  {
    path: '/',
    name: 'MainHome', // 将SimpleHome改为MainHome
    component: MainHome,
    meta: { 
      title: 'AI知识库管理系统'
    }
  },
  {
    path: '/admin',
    component: MainLayout,
    redirect: '/', // 将/admin的重定向改为根路径，即MainHome
    meta: { requiresAuth: true },
    children: [
      // 已删除 Dashboard 页面，移除其路由定义
      // {
      //   path: 'dashboard',
      //   name: 'Dashboard',
      //   component: Dashboard,
      //   meta: { 
      //     title: '仪表板',
      //     icon: 'mdi-view-dashboard',
      //     requiresAuth: true 
      //   }
      // },
      {
        path: 'knowledge',
        name: 'Knowledge',
        component: KnowledgeManagement,
        meta: { 
          title: '知识库管理',
          icon: 'mdi-book-multiple',
          requiresAuth: true,
          permission: 'knowledge.library.read'
        }
      },
      {
        path: 'documents',
        name: 'Documents',
        component: DocumentManagement,
        meta: { 
          title: '文档管理',
          icon: 'mdi-file-document-multiple',
          requiresAuth: true,
          permission: 'document.read'
        }
      },
      {
        path: 'chat',
        name: 'Chat',
        component: ChatInterface,
        meta: { 
          title: '智能问答',
          icon: 'mdi-chat',
          requiresAuth: true,
          permission: 'chat.use'
        }
      },
      {
        path: 'models',
        name: 'Models',
        component: ModelManagement,
        meta: { 
          title: '模型管理',
          icon: 'mdi-brain',
          requiresAuth: true,
          permission: 'model.manage'
        }
      },
      {
        path: 'rbac',
        meta: { 
          title: '权限管理',
          icon: 'mdi-security',
          requiresAuth: true,
          permission: 'rbac.read'
        },
        children: [
          {
            path: 'users',
            name: 'Users',
            component: UserManagement,
            meta: { 
              title: '用户管理',
              requiresAuth: true,
              permission: 'rbac.user.read'
            }
          },
          {
            path: 'roles',
            name: 'Roles',
            component: RoleManagement,
            meta: { 
              title: '角色管理',
              requiresAuth: true,
              permission: 'rbac.role.read'
            }
          },
          {
            path: 'permissions',
            name: 'Permissions', 
            component: PermissionManagement,
            meta: { 
              title: '权限管理',
              requiresAuth: true,
              permission: 'rbac.permission.read'
            }
          }
        ]
      },
      {
        path: 'settings',
        name: 'Settings',
        component: Settings,
        meta: { 
          title: '系统设置',
          icon: 'mdi-cog',
          requiresAuth: true 
        }
      }
    ]
  },
  {
    path: '/login',
    redirect: '/auth/login'
  },
  {
    path: '/unauthorized',
    name: 'Unauthorized',
    component: Unauthorized,
    meta: { requiresAuth: true, title: '访问受限' }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    redirect: (to) => {
      // 如果用户已登录，重定向到主页，否则重定向到登录页
      const authStore = useAuthStore()
      return authStore.isAuthenticated ? '/' : '/auth/login'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  const token = localStorage.getItem('token'); // 直接从localStorage获取token
  const requiresAuth = to.meta.requiresAuth;
  const requiredPermission = to.meta.permission as string | undefined;

  // 1. 初始化认证状态 (仅在应用启动时或token存在但store未初始化时)
  // 确保authStore.isAuthenticated是最新状态，如果token存在但authStore.user尚未加载，则尝试加载
  if (token && (!authStore.isAuthenticated || !authStore.user)) { // 增加对authStore.user的检查
    try {
      await authStore.initAuth(); // 确保加载用户信息和权限
    } catch (error) {
      console.error('Failed to initialize auth state:', error);
      // 如果初始化失败（如token失效），则清除本地存储并重定向到登录页
      authStore.logout();
      next('/auth/login');
      return;
    }
  }

  // 2. 处理根路径访问 (未认证则强制跳转登录)
  if (to.path === '/' && !authStore.isAuthenticated) {
    next('/auth/login');
    return;
  }

  // 3. 已登录用户访问登录/注册页面的重定向
  if (authStore.isAuthenticated && to.path.startsWith('/auth/')) {
    next('/'); // 重定向到根路径（MainHome）
    return;
  }

  // 4. 核心认证检查：需要登录的页面
  if (requiresAuth && !authStore.isAuthenticated) {
    // 如果页面需要认证但用户未登录，则保存目标路径并重定向到登录页
    localStorage.setItem('redirectAfterLogin', to.fullPath);
    next('/auth/login');
    return;
  }

  // 5. 权限检查 (仅当用户已认证且页面有特定权限要求时)
  // 注意：这一步只在用户isAuthenticated为true时才进行，否则在第4步已被处理
  if (authStore.isAuthenticated && requiredPermission && !authStore.hasPermission(requiredPermission)) {
    console.warn(`Access denied: missing permission "${requiredPermission}" for route ${to.fullPath}`);
    const appStore = useAppStore(); // 获取 appStore 实例
    appStore.openDialog('访问受限', '抱歉，您没有权限访问此功能。请联系管理员。'); // 调用 openDialog
    next(false); // 阻止路由跳转
    return;
  }

  // 6. 设置页面标题 (无论是否重定向，只要是最终目标页就设置)
  if (to.meta.title) {
    document.title = `${to.meta.title} - AI知识库管理系统`;
  }

  // 7. 放行
  next();
});

// 登录后重定向处理
router.afterEach((to) => {
  // 清除重定向标记（成功导航后）
  if (to.path !== '/auth/login') {
    localStorage.removeItem('redirectAfterLogin')
  }
})

// 动态添加路由（登录后）
export function addDynamicRoutes() { // 导出函数
  const authStore = useAuthStore();
  menuRoutes.forEach(route => {
    // 检查路由是否已经添加，避免重复添加导致警告
    if (!router.hasRoute(route.name) && authStore.hasPermission(route.meta.permission as string)) {
      router.addRoute('admin', route); // 添加到admin路由下
    }
  });
}

export default router