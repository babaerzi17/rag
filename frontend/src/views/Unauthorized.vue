<template>
  <div class="unauthorized-container">
    <el-row justify="center" align="middle">
      <el-col :span="24" :md="12" class="text-center">
        <el-card shadow="never" class="unauthorized-card">
          <el-icon :size="100" color="var(--el-color-warning)">
            <Lock />
          </el-icon>
          
          <h1 class="unauthorized-title">
            访问受限
          </h1>
          
          <p class="unauthorized-description">
            抱歉，您没有权限访问此页面。请联系管理员或返回首页。
          </p>
          
          <div class="unauthorized-actions">
            <el-button
              type="primary"
              :icon="HomeFilled"
              @click="goHome"
            >
              返回首页
            </el-button>
            
            <el-button
              type="primary"
              plain
              :icon="ArrowLeft"
              @click="goBack"
            >
              返回上页
            </el-button>
          </div>
          
          <el-divider class="unauthorized-divider"></el-divider>
          
          <div class="unauthorized-user-info">
            当前用户：{{ authStore.user?.full_name || authStore.user?.username }}
            <br>
            角色：{{ userRoles.join(', ') || '无' }}
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  Lock, // 导入锁图标
  HomeFilled, // 导入主页图标
  ArrowLeft // 导入返回图标
} from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

// 用户角色
const userRoles = computed(() => authStore.userRoles)

// 返回首页
const goHome = () => {
  if (authStore.isAuthenticated) {
    router.push('/admin/dashboard')
  } else {
    router.push('/')
  }
}

// 返回上页
const goBack = () => {
  router.go(-1)
}
</script>

<style scoped>
.unauthorized-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
}

.unauthorized-card {
  padding: 32px; /* pa-8 roughly */
  text-align: center;
}

.unauthorized-title {
  font-size: 2.25rem; /* text-h4 */
  margin-bottom: 16px; /* mb-4 */
  color: var(--el-color-warning); /* text-warning */
}

.unauthorized-description {
  font-size: 1rem; /* text-body-1 */
  margin-bottom: 24px; /* mb-6 */
  color: var(--el-text-color-secondary); /* text-medium-emphasis */
}

.unauthorized-actions {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 16px; /* gap-4 */
}

@media (min-width: 600px) { /* equivalent to sm breakpoint */
  .unauthorized-actions {
    flex-direction: row;
  }
}

.unauthorized-divider {
  margin: 24px 0; /* my-6 */
}

.unauthorized-user-info {
  font-size: 0.75rem; /* text-caption */
  color: var(--el-text-color-secondary); /* text-medium-emphasis */
}
</style>