<template>
  <div v-if="show" class="history-dialog-overlay" @click.self="closeDialog">
    <div class="history-dialog-container">
      <!-- 搜索框 -->
      <div class="search-input-wrapper">
        <input 
          type="text" 
          placeholder="搜索历史记录..." 
          v-model="searchQuery"
          class="search-input"
        />
        <span class="search-icon">🔍</span>
      </div>

      <!-- 描述性文字 -->
      <p class="dialog-description-text">在这里，您可以搜索和选择历史对话记录。</p>

      <!-- 历史记录列表 -->
      <div class="history-list-wrapper">
        <div 
          v-for="item in displayedHistory" 
          :key="item.id" 
          class="history-item-entry"
          @click="selectHistory(item)"
        >
          <div class="history-item-title">
            <i class="item-icon mdi mdi-history"></i>{{ item.title }}
          </div>
          <div class="history-item-body">
            {{ item.truncatedContent }}
          </div>
        </div>
        <div v-if="filteredHistory.length === 0" class="no-history-message">
          暂无历史记录或未找到相关内容。
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

const props = defineProps<{
  show: boolean;
  historyData: { id: number; title: string; content: string }[];
}>();

const emit = defineEmits(['update:show', 'select-history']);

const searchQuery = ref('');

// 文本截断辅助函数
const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) {
    return text;
  }
  return text.substring(0, maxLength) + '...';
};

// 过滤历史记录
const filteredHistory = computed(() => {
  if (!searchQuery.value) {
    return props.historyData;
  }
  const lowerCaseQuery = searchQuery.value.toLowerCase();
  return props.historyData.filter(item => 
    item.title.toLowerCase().includes(lowerCaseQuery) || 
    item.content.toLowerCase().includes(lowerCaseQuery)
  );
});

// 显示的历史记录，包含截断后的正文
const displayedHistory = computed(() => {
  return filteredHistory.value.map(item => ({
    ...item,
    truncatedContent: truncateText(item.content, 500) // 限制500字
  }));
});

// 关闭对话框
const closeDialog = () => {
  emit('update:show', false);
  searchQuery.value = ''; // 清空搜索框
};

// 选中历史记录
const selectHistory = (item: { id: number; title: string; content: string }) => {
  emit('select-history', item);
  closeDialog();
};

// 监听对话框显示状态，如果隐藏则清空搜索
watch(() => props.show, (newVal) => {
  if (!newVal) {
    searchQuery.value = '';
  }
});

</script>

<style scoped>
.history-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.4); /* 半透明背景 */
  display: flex;
  justify-content: flex-end; /* 对话框靠右显示 */
  align-items: flex-start; /* 对话框靠顶部显示 */
  z-index: 1000; /* 确保在最上层 */
}

.history-dialog-container {
  background-color: #ffffff;
  width: 500px; /* 对话框宽度从350px调整为500px */
  height: 100vh;
  box-shadow: -4px 0 10px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  padding: 20px;
  box-sizing: border-box;
  animation: slideInRight 0.3s ease-out;
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
  }
  to {
    transform: translateX(0);
  }
}

.search-input-wrapper {
  position: relative;
  margin-bottom: 10px; /* 调整margin-bottom为10px，为描述性文字留出空间 */
}

/* 新增描述性文字样式 */
.dialog-description-text {
  font-size: 12px;
  color: #666;
  margin-bottom: 15px; /* 描述性文字下方间距 */
  padding: 0 5px; /* 稍微内缩 */
}

.search-input {
  width: 100%;
  padding: 10px 10px 10px 35px; /* 左侧留出图标位置 */
  border: 1px solid #e9ecef;
  border-radius: 0; /* 移除圆角，从5px调整为0 */
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s ease;
}

.search-input:focus {
  border-color: #007bff;
}

.search-icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: #999;
  font-size: 16px;
}

.history-list-wrapper {
  flex: 1; /* 占据剩余空间 */
  overflow-y: auto; /* 内容溢出时滚动 */
  padding-right: 5px; /* 防止滚动条遮挡内容 */
}

/* 类似百度搜索历史的效果 */
.history-item-entry {
  background-color: #f8f9fa;
  border-left: 4px solid #007bff; /* 左侧蓝色边框 */
  padding: 10px 15px;
  margin-bottom: 10px;
  border-radius: 0;
  cursor: pointer;
  transition: background-color 0.2s ease, box-shadow 0.2s ease;
  font-size: 14px; /* 标题的字体大小 */
  color: #333;
  line-height: 1.4;
  word-break: break-word;
}

.history-item-entry:hover {
  background-color: #e6f7ff;
  box-shadow: 0 2px 5px rgba(0, 123, 255, 0.1);
}

/* 调整标题样式 */
.history-item-title {
  font-weight: 600;
  margin-bottom: 5px; /* 标题和正文之间的间距 */
  display: -webkit-box; /* 确保文本不溢出，多行显示 */
  -webkit-line-clamp: 1; /* 标题最多显示1行 */
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 正文样式 */
.history-item-body {
  font-size: 12px; /* 正文字体大小12px */
  color: #666;
  line-height: 1.4;
}

.no-history-message {
  text-align: center;
  color: #999;
  font-size: 14px;
  margin-top: 20px;
}

.item-icon {
  margin-right: 8px;
  font-size: 16px;
  color: #666; /* 确保图标颜色与文本协调 */
}
</style> 