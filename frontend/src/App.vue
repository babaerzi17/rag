<template>
  <div>
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
// import { useTheme } from 'vuetify' // 移除 Vuetify 导入
import { useAuthStore } from '@/stores/auth'

// const theme = useTheme() // 移除 Vuetify useTheme
const authStore = useAuthStore()

onMounted(async () => {
  try {
    // 初始化认证状态
    await authStore.initAuth()
    console.log('App initialized successfully')
  } catch (error) {
    console.error('App initialization failed:', error)
  }
})
</script>

<style>
/* 全局样式 */
html,
body {
  margin: 0;
  padding: 0;
  overflow-x: hidden; /* 强制隐藏水平滚动条 */
}

html {
  overflow-y: auto !important;
}

.v-application { /* 移除 Vuetify 特有样式 */
  font-family: 'Roboto', 'Noto Sans SC', sans-serif !important;
}

/* 自定义滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* LaTeX数学公式样式调整 */
.katex {
  font-size: 1.1em;
}

.katex-display {
  margin: 1em 0;
  text-align: center;
}

/* 代码高亮样式调整 */
.hljs {
  background: #f8f8f8 !important;
  border-radius: 4px;
  padding: 12px;
}

/* 响应式布局辅助类 */
.fill-height {
  height: 100vh;
}

.overflow-y-auto {
  overflow-y: auto;
}

.text-truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>