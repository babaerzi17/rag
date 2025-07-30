<template>
  <div class="model-management">
    <h1 class="el-text-h4 el-text-primary el-font-bold mb-4">模型管理</h1>
    <p class="el-text-body-1 el-text-medium-emphasis">管理AI模型配置和参数设置</p>
    
    <el-card class="mt-6" shadow="never">
      <div class="el-card-content text-center py-12">
        <el-icon :size="80" color="var(--el-color-primary)" class="mb-4">
          <MostlyCloudy /> <!-- 假设使用MostlyCloudy，或者您可以根据实际需求选择更合适的图标 -->
        </el-icon>
        <h3 class="el-text-h6 mb-2">模型管理功能开发中</h3>
        <p class="el-text-body-2 el-text-medium-emphasis">
          即将支持多种AI模型的配置和管理
        </p>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { MostlyCloudy } from '@element-plus/icons-vue' // 导入 Element Plus 云图标 (或者其他合适的图标)

// 模型管理页面
</script>

<style scoped>
/* 辅助类以匹配 Element Plus 的默认样式或您自定义的全局样式 */
.el-text-h4 {
  font-size: 2rem;
  line-height: 1.2;
}

.el-font-bold {
  font-weight: bold;
}

.el-text-primary {
  color: var(--el-color-primary);
}

.mb-4 {
  margin-bottom: 1rem;
}

.el-text-body-1 {
  font-size: 1rem;
  line-height: 1.5;
}

.el-text-medium-emphasis {
  color: var(--el-text-color-secondary);
}

.mt-6 {
  margin-top: 1.5rem;
}

.el-card-content {
  padding: 32px 0; /* py-12, assuming 1 unit = 4px */
}

.text-center {
  text-align: center;
}

.mb-4 {
  margin-bottom: 1rem;
}

.el-text-h6 {
  font-size: 1.25rem;
  line-height: 1.2;
}

.mb-2 {
  margin-bottom: 0.5rem;
}

.el-text-body-2 {
  font-size: 0.875rem;
  line-height: 1.5;
}
</style>