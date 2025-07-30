<template>
  <div class="chat-interface fill-height d-flex flex-column">
    <v-container fluid class="fill-height pa-0">
      <v-row no-gutters class="fill-height">
        <!-- 左侧边栏 - 会话历史 -->
        <v-col
          cols="3"
          class="chat-sidebar d-none d-md-flex flex-column"
          :class="{ 'sidebar-collapsed': sidebarCollapsed }"
        >
          <div class="sidebar-header pa-4">
            <div class="d-flex align-center justify-space-between mb-4">
              <h3 class="text-h6 font-weight-bold">
                对话历史
              </h3>
              <v-btn
                icon="mdi-plus"
                variant="outlined"
                size="small"
                @click="createNewChat"
              />
            </div>
            
            <v-text-field
              v-model="sessionSearch"
              placeholder="搜索对话..."
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              density="compact"
              hide-details
              clearable
            />
          </div>

          <div class="sidebar-content flex-grow-1 overflow-y-auto">
            <v-list density="compact" nav>
              <v-list-item
                v-for="session in filteredSessions"
                :key="session.id"
                :active="currentSessionId === session.id"
                @click="switchSession(session.id)"
                class="session-item"
              >
                <template v-slot:prepend>
                  <v-icon size="16">
                    mdi-chat-outline
                  </v-icon>
                </template>
                
                <v-list-item-title class="text-truncate">
                  {{ session.title }}
                </v-list-item-title>
                
                <v-list-item-subtitle class="text-truncate">
                  {{ formatDate(session.updatedAt) }}
                </v-list-item-subtitle>

                <template v-slot:append>
                  <v-menu>
                    <template v-slot:activator="{ props }">
                      <v-btn
                        v-bind="props"
                        icon="mdi-dots-vertical"
                        variant="text"
                        size="x-small"
                        @click.stop
                      />
                    </template>
                    <v-list density="compact">
                      <v-list-item @click="renameSession(session)">
                        <template v-slot:prepend>
                          <v-icon size="16">mdi-pencil</v-icon>
                        </template>
                        <v-list-item-title>重命名</v-list-item-title>
                      </v-list-item>
                      <v-list-item @click="exportSession(session)">
                        <template v-slot:prepend>
                          <v-icon size="16">mdi-export</v-icon>
                        </template>
                        <v-list-item-title>导出</v-list-item-title>
                      </v-list-item>
                      <v-divider />
                      <v-list-item @click="deleteSession(session)" class="text-error">
                        <template v-slot:prepend>
                          <v-icon size="16" color="error">mdi-delete</v-icon>
                        </template>
                        <v-list-item-title>删除</v-list-item-title>
                      </v-list-item>
                    </v-list>
                  </v-menu>
                </template>
              </v-list-item>
            </v-list>
          </div>
        </v-col>

        <!-- 主要聊天区域 -->
        <v-col 
          :cols="sidebarCollapsed ? 12 : 9"
          class="chat-main d-flex flex-column"
        >
          <!-- 聊天头部 -->
          <div class="chat-header pa-4 border-b">
            <div class="d-flex align-center justify-space-between">
              <div class="d-flex align-center">
                <v-btn
                  icon="mdi-menu"
                  variant="text"
                  size="small"
                  class="mr-2 d-md-none"
                  @click="sidebarCollapsed = !sidebarCollapsed"
                />
                <div>
                  <h2 class="text-h6 font-weight-bold">
                    {{ currentSession?.title || '新对话' }}
                  </h2>
                  <p class="text-caption text-medium-emphasis">
                    {{ messages.length }} 条消息
                  </p>
                </div>
              </div>
              
              <div class="d-flex align-center gap-2">
                <!-- 知识库选择 -->
                <v-select
                  v-model="selectedKnowledgeBase"
                  :items="knowledgeBaseOptions"
                  item-title="name"
                  item-value="id"
                  label="知识库"
                  variant="outlined"
                  density="compact"
                  style="min-width: 200px;"
                  hide-details
                />
                
                <!-- 模型选择 -->
                <v-select
                  v-model="selectedModel"
                  :items="modelOptions"
                  item-title="name"
                  item-value="id"
                  label="AI模型"
                  variant="outlined"
                  density="compact"
                  style="min-width: 150px;"
                  hide-details
                />
                
                <!-- 设置按钮 -->
                <v-btn
                  icon="mdi-cog"
                  variant="outlined"
                  size="small"
                  @click="showSettings = true"
                />
              </div>
            </div>
          </div>

          <!-- 消息区域 -->
          <div 
            ref="messagesContainer"
            class="messages-container flex-grow-1 overflow-y-auto pa-4"
          >
            <!-- 欢迎界面 -->
            <div v-if="messages.length === 0" class="welcome-screen text-center">
              <v-icon size="80" color="primary" class="mb-4">
                mdi-robot-outline
              </v-icon>
              <h2 class="text-h5 font-weight-bold mb-4">
                欢迎使用智能问答助手
              </h2>
              <p class="text-body-1 text-medium-emphasis mb-6">
                我可以帮您查找和理解文档内容，支持自然语言问答
              </p>
              
              <!-- 快速问题建议 -->
              <div class="quick-questions">
                <h3 class="text-h6 mb-4">试试这些问题：</h3>
                <v-row justify="center">
                  <v-col
                    v-for="suggestion in quickSuggestions"
                    :key="suggestion"
                    cols="12"
                    sm="6"
                    md="4"
                  >
                    <v-card
                      variant="outlined"
                      hover
                      class="suggestion-card"
                      @click="askQuestion(suggestion)"
                    >
                      <v-card-text class="text-center">
                        <v-icon class="mb-2" color="primary">
                          mdi-help-circle-outline
                        </v-icon>
                        <p class="text-body-2">{{ suggestion }}</p>
                      </v-card-text>
                    </v-card>
                  </v-col>
                </v-row>
              </div>
            </div>

            <!-- 消息列表 -->
            <div v-else class="messages-list">
              <div
                v-for="message in messages"
                :key="message.id"
                class="message-wrapper mb-4"
                :class="message.role === 'user' ? 'user-message' : 'assistant-message'"
              >
                <div class="d-flex align-start gap-3">
                  <!-- 头像 -->
                  <v-avatar
                    :color="message.role === 'user' ? 'primary' : 'success'"
                    size="40"
                    class="message-avatar"
                  >
                    <v-icon color="white">
                      {{ message.role === 'user' ? 'mdi-account' : 'mdi-robot' }}
                    </v-icon>
                  </v-avatar>

                  <!-- 消息内容 -->
                  <div class="message-content flex-grow-1">
                    <div class="d-flex align-center justify-space-between mb-2">
                      <span class="text-subtitle-2 font-weight-bold">
                        {{ message.role === 'user' ? '您' : 'AI助手' }}
                      </span>
                      <span class="text-caption text-medium-emphasis">
                        {{ formatTime(message.timestamp) }}
                      </span>
                    </div>

                    <!-- 消息气泡 -->
                    <div
                      class="message-bubble pa-3 rounded"
                      :class="message.role === 'user' ? 'user-bubble' : 'assistant-bubble'"
                    >
                      <!-- 文本消息 -->
                      <div v-if="message.type === 'text'" class="message-text">
                        <div v-html="formatMessage(message.content)"></div>
                      </div>

                      <!-- 思考中动画 -->
                      <div v-else-if="message.type === 'thinking'" class="thinking-animation">
                        <div class="d-flex align-center">
                          <v-progress-circular
                            indeterminate
                            size="16"
                            width="2"
                            color="primary"
                            class="mr-2"
                          />
                          <span class="text-body-2">正在思考...</span>
                        </div>
                      </div>

                      <!-- 引用的文档片段 -->
                      <div v-if="message.sources && message.sources.length > 0" class="sources mt-3">
                        <v-divider class="mb-2" />
                        <div class="text-caption text-medium-emphasis mb-2">
                          <v-icon size="14" class="mr-1">mdi-book-open-variant</v-icon>
                          参考来源:
                        </div>
                        <div class="sources-list">
                          <v-chip
                            v-for="source in message.sources"
                            :key="source.id"
                            size="small"
                            variant="tonal"
                            class="mr-1 mb-1"
                            @click="viewSource(source)"
                          >
                            <v-icon start size="12">mdi-file-document</v-icon>
                            {{ source.title }}
                          </v-chip>
                        </div>
                      </div>
                    </div>

                    <!-- 消息操作 -->
                    <div class="message-actions mt-2">
                      <v-btn
                        variant="text"
                        size="x-small"
                        @click="copyMessage(message)"
                      >
                        <v-icon size="14">mdi-content-copy</v-icon>
                      </v-btn>
                      <v-btn
                        v-if="message.role === 'assistant'"
                        variant="text"
                        size="x-small"
                        @click="regenerateResponse(message)"
                      >
                        <v-icon size="14">mdi-refresh</v-icon>
                      </v-btn>
                      <v-btn
                        variant="text"
                        size="x-small"
                        @click="shareMessage(message)"
                      >
                        <v-icon size="14">mdi-share</v-icon>
                      </v-btn>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 输入区域 -->
          <div class="input-area pa-4 border-t">
            <v-form @submit.prevent="sendMessage">
              <div class="d-flex align-end gap-3">
                <v-textarea
                  v-model="currentMessage"
                  placeholder="输入您的问题..."
                  variant="outlined"
                  rows="1"
                  auto-grow
                  max-rows="4"
                  hide-details
                  class="flex-grow-1"
                  @keydown.enter.exact.prevent="sendMessage"
                  @keydown.enter.shift.exact="addNewLine"
                  :disabled="isLoading"
                />
                
                <div class="d-flex flex-column gap-2">
                  <v-btn
                    icon="mdi-attachment" 
                    variant="outlined"
                    size="small"
                    @click="attachFile"
                    :disabled="isLoading"
                  />
                  <v-btn
                    icon="mdi-send"
                    color="primary"
                    :disabled="!currentMessage.trim() || isLoading"
                    :loading="isLoading"
                    @click="sendMessage"
                  />
                </div>
              </div>
              
              <!-- 输入提示 -->
              <div class="text-caption text-medium-emphasis mt-2">
                按 Enter 发送，Shift + Enter 换行
              </div>
            </v-form>
          </div>
        </v-col>
      </v-row>
    </v-container>

    <!-- 设置对话框 -->
    <v-dialog v-model="showSettings" max-width="500">
      <v-card>
        <v-card-title>聊天设置</v-card-title>
        <v-card-text>
          <v-form>
            <v-slider
              v-model="chatSettings.temperature"
              label="创造性"
              min="0"
              max="1"
              step="0.1"
              thumb-label
              class="mb-4"
            />
            <v-slider
              v-model="chatSettings.maxTokens"
              label="最大回复长度"
              min="100"
              max="2000"
              step="100"
              thumb-label
              class="mb-4"
            />
            <v-switch
              v-model="chatSettings.enableSources"
              label="显示参考来源"
              hide-details
              class="mb-4"
            />
            <v-switch
              v-model="chatSettings.streamResponse"
              label="流式回复"
              hide-details
            />
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showSettings = false">关闭</v-btn>
          <v-btn color="primary" @click="saveSettings">保存</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, nextTick, onMounted } from 'vue'

// 响应式数据
const sidebarCollapsed = ref(false)
const sessionSearch = ref('')
const currentSessionId = ref(1)
const currentMessage = ref('')
const isLoading = ref(false)
const messagesContainer = ref()
const showSettings = ref(false)
const selectedKnowledgeBase = ref('all')
const selectedModel = ref('gpt-4')

// 知识库选项
const knowledgeBaseOptions = [
  { id: 'all', name: '全部知识库' },
  { id: 1, name: 'AI技术文档' },
  { id: 2, name: '产品使用手册' },
  { id: 3, name: '内部培训资料' },
  { id: 4, name: '法律合规文档' }
]

// 模型选项
const modelOptions = [
  { id: 'gpt-4', name: 'GPT-4' },
  { id: 'gpt-3.5', name: 'GPT-3.5' },
  { id: 'claude', name: 'Claude' },
  { id: 'llama', name: 'LLaMA' }
]

// 聊天设置
const chatSettings = reactive({
  temperature: 0.7,
  maxTokens: 1000,
  enableSources: true,
  streamResponse: true
})

// 快速问题建议
const quickSuggestions = [
  '什么是RAG技术？',
  '如何提高文档检索精度？',
  '系统支持哪些文件格式？',
  '如何创建新的知识库？',
  '权限管理如何配置？',
  '模型参数如何调优？'
]

// 会话历史
const sessions = ref([
  {
    id: 1,
    title: 'RAG技术讨论',
    updatedAt: new Date('2024-01-20T14:30:00'),
    messageCount: 12
  },
  {
    id: 2,
    title: '文档处理问题',
    updatedAt: new Date('2024-01-20T10:15:00'),
    messageCount: 8
  },
  {
    id: 3,
    title: '权限配置咨询',
    updatedAt: new Date('2024-01-19T16:45:00'),
    messageCount: 5
  }
])

// 消息列表
const messages = ref([
  {
    id: 1,
    role: 'user',
    type: 'text',
    content: '什么是RAG技术？',
    timestamp: new Date('2024-01-20T14:25:00')
  },
  {
    id: 2,
    role: 'assistant',
    type: 'text',
    content: 'RAG（Retrieval-Augmented Generation）是一种结合检索和生成的AI技术。它通过从外部知识库中检索相关信息，然后将这些信息作为上下文输入到大语言模型中，从而生成更准确、更有针对性的回答。\n\nRAG技术的主要优势包括：\n1. **知识更新**：可以使用最新的外部信息\n2. **减少幻觉**：基于真实文档内容回答\n3. **计算效率**：无需重新训练模型\n4. **可解释性**：可以追踪信息来源',
    timestamp: new Date('2024-01-20T14:25:30'),
    sources: [
      { id: 1, title: 'RAG技术白皮书.pdf', excerpt: '关于RAG技术的定义和应用' },
      { id: 2, title: 'AI技术指南.docx', excerpt: '检索增强生成的技术细节' }
    ]
  }
])

// 过滤后的会话
const filteredSessions = computed(() => {
  if (!sessionSearch.value) {
    return sessions.value
  }
  return sessions.value.filter(session =>
    session.title.toLowerCase().includes(sessionSearch.value.toLowerCase())
  )
})

// 当前会话
const currentSession = computed(() => {
  return sessions.value.find(s => s.id === currentSessionId.value)
})

// 格式化日期
function formatDate(date: Date) {
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  } else if (days === 1) {
    return '昨天'
  } else if (days < 7) {
    return `${days}天前`
  } else {
    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
  }
}

// 格式化时间
function formatTime(date: Date) {
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

// 格式化消息内容（支持Markdown）
function formatMessage(content: string) {
  // 简单的Markdown支持
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
}

// 创建新对话
function createNewChat() {
  const newSession = {
    id: Date.now(),
    title: '新对话',
    updatedAt: new Date(),
    messageCount: 0
  }
  sessions.value.unshift(newSession)
  switchSession(newSession.id)
}

// 切换会话
function switchSession(sessionId: number) {
  currentSessionId.value = sessionId
  // 这里应该加载对应会话的消息
  console.log('切换到会话:', sessionId)
}

// 重命名会话
function renameSession(session: any) {
  const newTitle = prompt('请输入新的会话名称:', session.title)
  if (newTitle && newTitle.trim()) {
    session.title = newTitle.trim()
  }
}

// 导出会话
function exportSession(session: any) {
  console.log('导出会话:', session.title)
}

// 删除会话
function deleteSession(session: any) {
  if (confirm(`确定要删除会话"${session.title}"吗？`)) {
    const index = sessions.value.findIndex(s => s.id === session.id)
    if (index > -1) {
      sessions.value.splice(index, 1)
      if (currentSessionId.value === session.id && sessions.value.length > 0) {
        currentSessionId.value = sessions.value[0].id
      }
    }
  }
}

// 发送消息
async function sendMessage() {
  if (!currentMessage.value.trim() || isLoading.value) return

  const userMessage = {
    id: Date.now(),
    role: 'user',
    type: 'text',
    content: currentMessage.value.trim(),
    timestamp: new Date()
  }

  messages.value.push(userMessage)
  const question = currentMessage.value.trim()
  currentMessage.value = ''

  // 显示思考动画
  const thinkingMessage = {
    id: Date.now() + 1,
    role: 'assistant',
    type: 'thinking',
    content: '',
    timestamp: new Date()
  }
  messages.value.push(thinkingMessage)

  isLoading.value = true
  await scrollToBottom()

  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 2000))

    // 移除思考动画
    const thinkingIndex = messages.value.findIndex(m => m.id === thinkingMessage.id)
    if (thinkingIndex > -1) {
      messages.value.splice(thinkingIndex, 1)
    }

    // 添加AI回复
    const aiResponse = {
      id: Date.now() + 2,
      role: 'assistant',
      type: 'text',
      content: `这是对"${question}"的回答。在实际应用中，这里会是AI模型基于知识库内容生成的专业回答。`,
      timestamp: new Date(),
      sources: chatSettings.enableSources ? [
        { id: 1, title: '相关文档.pdf', excerpt: '相关内容片段' }
      ] : []
    }

    messages.value.push(aiResponse)
    await scrollToBottom()

    // 更新会话标题（如果是第一条消息）
    if (messages.value.filter(m => m.role === 'user').length === 1) {
      const session = sessions.value.find(s => s.id === currentSessionId.value)
      if (session) {
        session.title = question.substring(0, 20) + (question.length > 20 ? '...' : '')
      }
    }

  } catch (error) {
    console.error('发送消息失败:', error)
  } finally {
    isLoading.value = false
  }
}

// 快速提问
function askQuestion(question: string) {
  currentMessage.value = question
  sendMessage()
}

// 添加换行
function addNewLine() {
  currentMessage.value += '\n'
}

// 附加文件
function attachFile() {
  console.log('附加文件功能')
}

// 滚动到底部
async function scrollToBottom() {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 复制消息
function copyMessage(message: any) {
  navigator.clipboard.writeText(message.content)
  console.log('消息已复制')
}

// 重新生成回复
function regenerateResponse(message: any) {
  console.log('重新生成回复:', message.id)
}

// 分享消息
function shareMessage(message: any) {
  console.log('分享消息:', message.id)
}

// 查看来源
function viewSource(source: any) {
  console.log('查看来源:', source.title)
}

// 保存设置
function saveSettings() {
  console.log('保存聊天设置:', chatSettings)
  showSettings.value = false
}

// 组件挂载后滚动到底部
onMounted(() => {
  scrollToBottom()
})
</script>

<style scoped>
.chat-interface {
  height: 100vh;
  background-color: rgb(var(--v-theme-background));
}

.chat-sidebar {
  background-color: rgb(var(--v-theme-surface));
  border-right: 1px solid rgb(var(--v-theme-outline-variant));
  max-width: 300px;
  min-width: 250px;
}

.sidebar-collapsed {
  display: none !important;
}

.sidebar-header {
  border-bottom: 1px solid rgb(var(--v-theme-outline-variant));
}

.sidebar-content {
  max-height: calc(100vh - 200px);
}

.session-item {
  margin: 4px 8px;
  border-radius: 8px;
}

.chat-main {
  background-color: rgb(var(--v-theme-background));
}

.chat-header {
  background-color: rgb(var(--v-theme-surface));
  border-bottom: 1px solid rgb(var(--v-theme-outline-variant));
}

.messages-container {
  max-height: 60vh;
  background: linear-gradient(to bottom, transparent, rgba(var(--v-theme-surface-variant), 0.1));
}

.welcome-screen {
  padding: 60px 20px;
}

.suggestion-card {
  cursor: pointer;
  transition: transform 0.2s ease;
}

.suggestion-card:hover {
  transform: translateY(-2px);
}

.message-wrapper {
  max-width: 100%;
}

.user-message {
  align-self: flex-end;
}

.assistant-message {
  align-self: flex-start;
}

.message-bubble {
  max-width: 80%;
  word-wrap: break-word;
}

.user-bubble {
  background-color: rgb(var(--v-theme-primary));
  color: white;
  margin-left: auto;
}

.assistant-bubble {
  background-color: rgb(var(--v-theme-surface-variant));
  color: rgb(var(--v-theme-on-surface));
}

.message-text :deep(code) {
  background-color: rgba(var(--v-theme-on-surface), 0.1);
  padding: 2px 4px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
}

.sources-list {
  max-height: 100px;
  overflow-y: auto;
}

.message-actions {
  opacity: 0;
  transition: opacity 0.2s ease;
}

.message-wrapper:hover .message-actions {
  opacity: 1;
}

.input-area {
  background-color: rgb(var(--v-theme-surface));
  border-top: 1px solid rgb(var(--v-theme-outline-variant));
}

.border-b {
  border-bottom: 1px solid rgb(var(--v-theme-outline-variant));
}

.border-t {
  border-top: 1px solid rgb(var(--v-theme-outline-variant));
}

.thinking-animation {
  padding: 8px 0;
}

/* 响应式调整 */
@media (max-width: 960px) {
  .chat-sidebar {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    z-index: 1000;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }
  
  .chat-sidebar.show {
    transform: translateX(0);
  }
  
  .message-bubble {
    max-width: 90%;
  }
}
</style>