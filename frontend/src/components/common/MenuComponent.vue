<template>
  <el-aside :width="isCollapse ? '64px' : '200px'" class="menu-aside">
    <el-menu
      :default-active="activeMenu"
      :collapse="isCollapse"
      class="el-menu-vertical-demo"
      @open="handleOpen"
      @close="handleClose"
    >
      <!-- 菜单头部，用于控制折叠 -->
      <el-menu-item index="toggle-collapse" @click="isCollapse = !isCollapse" class="menu-header">
        <el-icon><Fold /></el-icon>
        <template #title>
          <span v-show="!isCollapse">菜单</span>
        </template>
      </el-menu-item>
      <el-divider v-show="!isCollapse"></el-divider>

      <!-- 动态菜单项 -->
      <template v-for="item in filteredMenuItems" :key="item.path">
        <!-- 有子菜单的项 -->
        <el-sub-menu v-if="item.children" :index="item.path">
          <template #title>
            <el-icon v-if="item.icon">
              <component :is="item.icon" />
            </el-icon>
            <span>{{ item.title }}</span>
          </template>
          <el-menu-item
            v-for="child in getFilteredChildren(item.children)"
            :key="child.path"
            :index="child.path"
            @click="handleMenuItemClick(child)" // 添加点击事件处理
          >
            <span class="ml-4">{{ child.title }}</span>
          </el-menu-item>
        </el-sub-menu>

        <!-- 没有子菜单的项 -->
        <el-menu-item v-else :index="item.path" @click="handleMenuItemClick(item)"> // 添加点击事件处理
          <el-icon v-if="item.icon">
            <component :is="item.icon" />
          </el-icon>
          <span>{{ item.title }}</span>
        </el-menu-item>
      </template>
    </el-menu>
  </el-aside>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRoute, useRouter } from 'vue-router' // 导入 useRouter
import { ElMessage } from 'element-plus' // 导入ElMessage
// 导入Element Plus图标
import {
  Fold,
  Expand,
  ViewDashboard,
  Tickets,
  Document,
  ChatDotRound,
  MostlyCloudy, // 假设这是一个脑的图标
  Setting,
  User,
  Van, // 假设这是一个角色的图标
  Unlock // 假设这是一个权限的图标
} from '@element-plus/icons-vue'

// Props
interface Props {
  modelValue?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: true
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

// State
const isCollapse = ref(false) // 更改 rail 为 isCollapse
const authStore = useAuthStore()
const route = useRoute()

// New: 获取router实例
const router = useRouter()

// Computed
const activeMenu = computed(() => route.path) // 根据当前路由路径高亮菜单

// 处理菜单打开和关闭，这里可以放置您的逻辑
const handleOpen = (key: string, keyPath: string[]) => {
  console.log(key, keyPath)
}
const handleClose = (key: string, keyPath: string[]) => {
  console.log(key, keyPath)
}

// New: 处理菜单项点击事件
const handleMenuItemClick = (item: any) => {
  if (item.permission && !authStore.hasPermission(item.permission)) {
    ElMessage.warning('您没有权限访问此功能。')
    return
  }
  router.push(item.path) // 有权限则进行路由跳转
}

// 菜单项配置
const menuItems = [
  {
    path: '/admin/dashboard',
    title: '仪表板',
    icon: 'ViewDashboard',
    permission: 'dashboard.read'
  },
  {
    path: '/admin/knowledge',
    title: '知识库管理',
    icon: 'Tickets',
    permission: 'knowledge.library.read'
  },
  {
    path: '/admin/documents',
    title: '文档管理',
    icon: 'Document',
    permission: 'document.read'
  },
  {
    path: '/admin/chat',
    title: '智能问答',
    icon: 'ChatDotRound',
    permission: 'chat.use'
  },
  {
    path: '/admin/models',
    title: '模型管理',
    icon: 'MostlyCloudy',
    permission: 'model.manage'
  },
  {
    path: '/admin/rbac',
    title: '权限管理',
    icon: 'Setting',
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
    icon: 'Setting',
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
</script>

<style scoped>
.menu-aside {
  transition: width 0.3s ease;
}

.el-menu-vertical-demo:not(.el-menu--collapse) {
  width: 200px;
  min-height: 400px;
}

.el-menu-vertical-demo {
  height: 100%; /* 填充整个侧边栏高度 */
}

.menu-header {
  height: 56px; /* Element Plus 菜单项的默认高度 */
  display: flex;
  align-items: center;
  justify-content: center; /* 居中显示图标和文本 */
}

.menu-header span {
  margin-left: 10px; /* 菜单文本与图标的间距 */
}

.el-menu-item.is-active {
  background-color: #ecf5ff; /* Element Plus 默认的激活背景色 */
  color: #409eff; /* Element Plus 默认的激活文本颜色 */
}

/* 调整子菜单项的左边距 */
.el-menu--inline .el-menu-item {
  padding-left: 32px !important; /* 根据需要调整 */
}

.el-divider {
  margin: 0;
}
</style>