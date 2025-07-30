<template>
  <v-app>
    <!-- 应用栏 -->
    <v-app-bar elevation="1" density="compact">
      <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
      
      <v-toolbar-title class="text-h6">
        AI知识库管理系统
      </v-toolbar-title>
      
      <v-spacer></v-spacer>
      
      <!-- 用户菜单 -->
      <v-menu>
        <template v-slot:activator="{ props }">
          <v-btn 
            v-bind="props" 
            variant="text" 
            prepend-icon="mdi-account-circle"
          >
            {{ authStore.user?.full_name || authStore.user?.username }}
          </v-btn>
        </template>
        
        <v-list>
          <v-list-item 
            prepend-icon="mdi-account-circle"
            title="个人信息"
            @click="handleProfile"
          ></v-list-item>
          
          <v-list-item 
            prepend-icon="mdi-cog"
            title="设置"
            @click="handleSettings"
          ></v-list-item>
          
          <v-divider></v-divider>
          
          <v-list-item 
            prepend-icon="mdi-logout"
            title="退出登录"
            @click="handleLogout"
          ></v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>

    <!-- 侧边导航栏 -->
    <v-navigation-drawer v-model="drawer" temporary>
      <v-list>
        <!-- 菜单头部 -->
        <v-list-item class="pa-4">
          <v-list-item-title class="text-h6">
            导航菜单
          </v-list-item-title>
        </v-list-item>
        
        <v-divider></v-divider>
        
        <!-- 动态菜单项 -->
        <template v-for="item in filteredMenuItems" :key="item.path">
          <!-- 有子菜单的项 -->
          <v-list-group v-if="item.children" :value="item.path">
            <template v-slot:activator="{ props }">
              <v-list-item
                v-bind="props"
                :prepend-icon="item.icon"
                :title="item.title"
              ></v-list-item>
            </template>
            
            <v-list-item
              v-for="child in getFilteredChildren(item.children)"
              :key="child.path"
              :to="child.path"
              :title="child.title"
              class="ml-4"
            ></v-list-item>
          </v-list-group>
          
          <!-- 没有子菜单的项 -->
          <v-list-item
            v-else
            :to="item.path"
            :prepend-icon="item.icon"
            :title="item.title"
          ></v-list-item>
        </template>
      </v-list>
    </v-navigation-drawer>

    <!-- 主内容区域 -->
    <v-main>
      <v-container fluid>
        <router-view />
      </v-container>
    </v-main>

    <!-- 全局权限提示对话框 -->
    <v-dialog v-model="appStore.showDialog" max-width="300">
      <v-card>
        <v-card-title class="text-h5">{{ appStore.dialogTitle }}</v-card-title>
        <v-card-text>{{ appStore.dialogMessage }}</v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="appStore.closeDialog">确定</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

  </v-app>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app' // 导入 appStore

const router = useRouter()
const authStore = useAuthStore()
const appStore = useAppStore() // 获取 appStore 实例

const drawer = ref(false)

// 菜单项配置
const menuItems = [
  {
    path: '/admin/dashboard',
    title: '仪表板',
    icon: 'mdi-view-dashboard',
    permission: 'dashboard.read'
  },
  {
    path: '/admin/knowledge',
    title: '知识库管理',
    icon: 'mdi-book-multiple',
    permission: 'knowledge.library.read'
  },
  {
    path: '/admin/documents',
    title: '文档管理',
    icon: 'mdi-file-document-multiple',
    permission: 'document.read'
  },
  {
    path: '/admin/chat',
    title: '智能问答',
    icon: 'mdi-chat',
    permission: 'chat.use'
  },
  {
    path: '/admin/models',
    title: '模型管理',
    icon: 'mdi-brain',
    permission: 'model.manage'
  },
  {
    path: '/admin/rbac',
    title: '权限管理',
    icon: 'mdi-security',
    permission: 'rbac.read',
    children: [
      {
        path: '/admin/rbac/users',
        title: '用户管理',
        permission: 'rbac.user.read'
      },
      {
        path: '/admin/rbac/roles',
        title: '角色管理',
        permission: 'rbac.role.read'
      },
      {
        path: '/admin/rbac/permissions',
        title: '权限管理',
        permission: 'rbac.permission.read'
      }
    ]
  },
  {
    path: '/admin/settings',
    title: '系统设置',
    icon: 'mdi-cog',
    permission: 'settings.read'
  }
]

// 根据权限过滤菜单项
const filteredMenuItems = computed(() => {
  return menuItems.filter(item => {
    if (!item.permission) return true
    return authStore.hasPermission(item.permission)
  })
})

// 过滤子菜单项
const getFilteredChildren = (children: any[]) => {
  return children.filter(child => {
    if (!child.permission) return true
    return authStore.hasPermission(child.permission)
  })
}

// 处理个人信息
const handleProfile = () => {
  // TODO: 实现个人信息页面
  console.log('跳转到个人信息页面')
}

// 处理设置
const handleSettings = () => {
  router.push('/admin/settings')
}

// 处理退出登录
const handleLogout = async () => {
  try {
    authStore.logout()
    router.push('/auth/login')
  } catch (error) {
    console.error('Logout failed:', error)
  }
}

// 组件挂载时初始化
onMounted(async () => {
  // 确保认证状态已初始化
  if (!authStore.isAuthenticated && localStorage.getItem('token')) {
    await authStore.initAuth()
  }
})
</script>

<style scoped>
.v-app-bar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.v-navigation-drawer {
  border-right: 1px solid rgba(0, 0, 0, 0.12);
}

.v-list-item {
  border-radius: 8px;
  margin: 2px 8px;
}

.v-list-item:hover {
  background-color: rgba(0, 0, 0, 0.04);
}

.v-list-item--active {
  background-color: rgba(102, 126, 234, 0.1);
  color: #667eea;
}
</style>