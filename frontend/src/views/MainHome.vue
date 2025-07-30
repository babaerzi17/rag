<template>
  <div class="main-home">
    <!-- 左侧面板 -->
    <div class="left-panel">
      <!-- AI知识库标题 -->
      <div class="knowledge-title" >
        <h2>高精度AI智能知识库系统</h2>
      </div>
      
      <!-- Tab 切换 -->
      <div class="tab-buttons">
        <button 
          class="tab-button"
          :class="{ active: activeTab === 'conversation' }"
          @click="activeTab = 'conversation'"
        >
          聊天
        </button>
        <button 
          class="tab-button"
          :class="{ active: activeTab === 'functions' }"
          @click="activeTab = 'functions'"
        >
          功能
        </button>
      </div>
      
      <!-- Tab 内容 -->
      <div class="tab-content">
        <!-- 对话 Tab -->
        <div v-if="activeTab === 'conversation'" class="tab-panel">
          <div class="drawer-container">
            <!-- 对话分类抽屉 -->
            <div class="drawer-item">
              <div 
                class="drawer-header"
                @click="toggleDrawer('conversations')"
              >
                <div class="drawer-title">
                  <span>对话</span>
                </div>
                <span 
                  class="drawer-arrow"
                  :class="{ 'drawer-arrow-expanded': drawerStates.conversations }"
                >
                </span>
              </div>
              <div 
                class="drawer-content"
                :class="{ 'drawer-content-expanded': drawerStates.conversations }"
              >
                <div class="drawer-body">
                  <div 
                    class="conversation-item"
                    :class="{ 'active-conversation-item': selectedConversationId === 1 }"
                    @click="selectConversation(1)"
                  >
                    <span class="item-icon">💬</span><span>RAG技术讨论文档处理问题</span>
                  </div>
                  <div 
                    class="conversation-item"
                    :class="{ 'active-conversation-item': selectedConversationId === 2 }"
                    @click="selectConversation(2)"
                  >
                    <span class="item-icon">💬</span><span>知识库管理和优化策略</span>
                  </div>
                  <div 
                    class="conversation-item"
                    :class="{ 'active-conversation-item': selectedConversationId === 3 }"
                    @click="selectConversation(3)"
                  >
                    <span class="item-icon">💬</span><span>模型参数调优实践经验</span>
                  </div>
                  <div 
                    class="conversation-item"
                    :class="{ 'active-conversation-item': selectedConversationId === 4 }"
                    @click="selectConversation(4)"
                  >
                    <span class="item-icon">💬</span><span>文档解析和向量化处理</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 历史记录抽屉 -->
            <div class="drawer-item">
              <div 
                class="drawer-header"
                @click="toggleDrawer('history')"
              >
                <div class="drawer-title">
                  <span>历史记录</span>
                </div>
                <span 
                  class="drawer-arrow"
                  :class="{ 'drawer-arrow-expanded': drawerStates.history }"
                >
                  
                </span>
              </div>
              <div 
                class="drawer-content"
                :class="{ 'drawer-content-expanded': drawerStates.history }"
              >
                <div class="drawer-body">
                  <div 
                    class="conversation-item"
                    :class="{ 'active-conversation-item': selectedConversationId === 101 }"
                    @click="selectConversation(101)"
                  >
                    <i class="item-icon mdi mdi-history"></i><span>历史对话：项目A会议纪要</span>
                  </div>
                  <div 
                    class="conversation-item"
                    :class="{ 'active-conversation-item': selectedConversationId === 102 }"
                    @click="selectConversation(102)"
                  >
                    <i class="item-icon mdi mdi-history"></i><span>历史对话：技术方案讨论</span>
                  </div>
                  <div 
                    class="conversation-item"
                    :class="{ 'active-conversation-item': selectedConversationId === 103 }"
                    @click="selectConversation(103)"
                  >
                    <i class="item-icon mdi mdi-history"></i><span>历史对话：用户反馈分析</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 功能 Tab -->
        <div v-if="activeTab === 'functions'" class="tab-panel">
          <div class="drawer-container">
            <!-- 知识库管理抽屉 -->
            <div class="drawer-item">
              <div 
                class="drawer-header"
                @click="toggleDrawer('knowledge')"
              >
                <div class="drawer-title">
                  <span>知识库管理</span>
                </div>
                <span 
                  class="drawer-arrow"
                  :class="{ 'drawer-arrow-expanded': drawerStates.knowledge }"
                >
                  
                </span>
              </div>
              <div 
                class="drawer-content"
                :class="{ 'drawer-content-expanded': drawerStates.knowledge }"
              >
                <div class="drawer-body">
                  <div class="function-item" :class="{ 'active-function-item': currentFunction === 'documents' }" @click="handleFunctionClick('documents')">
                    <span class="item-icon">📄</span><span>文档管理</span>
                  </div>
                  <div class="function-item" :class="{ 'active-function-item': currentFunction === 'parse' }" @click="handleFunctionClick('parse')">
                    <span class="item-icon">📄</span><span>文档解析</span>
                  </div>
                  <div class="function-item" :class="{ 'active-function-item': currentFunction === 'chunks' }" @click="handleFunctionClick('chunks')">
                    <span class="item-icon">📄</span><span>Chunk管理</span>
                  </div>
                  <div class="function-item" :class="{ 'active-function-item': currentFunction === 'kb-management' }" @click="handleFunctionClick('kb-management')">
                    <span class="item-icon">📚</span><span>知识库管理</span>
                  </div>
                  <div class="function-item" :class="{ 'active-function-item': currentFunction === 'kb-settings' }" @click="handleFunctionClick('kb-settings')">
                    <span class="item-icon">⚙️</span><span>知识库设置</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 模型管理抽屉 -->
            <div class="drawer-item">
              <div 
                class="drawer-header"
                @click="toggleDrawer('models')"
              >
                <div class="drawer-title">
                  <span>模型管理</span>
                </div>
                <span 
                  class="drawer-arrow"
                  :class="{ 'drawer-arrow-expanded': drawerStates.models }"
                >
                  
                </span>
              </div>
              <div 
                class="drawer-content"
                :class="{ 'drawer-content-expanded': drawerStates.models }"
              >
                <div class="drawer-body">
                  <div class="function-item" :class="{ 'active-function-item': currentFunction === 'model-config' }" @click="handleFunctionClick('model-config')">
                    <span class="item-icon">🧠</span><span>模型配置</span>
                  </div>
                  <div class="function-item" :class="{ 'active-function-item': currentFunction === 'param-tuning' }" @click="handleFunctionClick('param-tuning')">
                    <span class="item-icon">🧠</span><span>参数调优</span>
                  </div>
                  <div class="function-item" :class="{ 'active-function-item': currentFunction === 'performance' }" @click="handleFunctionClick('performance')">
                    <span class="item-icon">🧠</span><span>性能监控</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 系统工具抽屉 -->
            <div class="drawer-item">
              <div 
                class="drawer-header"
                @click="toggleDrawer('tools')"
              >
                <div class="drawer-title">
                  <span>系统工具</span>
                </div>
                <span 
                  class="drawer-arrow"
                  :class="{ 'drawer-arrow-expanded': drawerStates.tools }"
                >
                  
                </span>
              </div>
              <div 
                class="drawer-content"
                :class="{ 'drawer-content-expanded': drawerStates.tools }"
              >
                <div class="drawer-body">
                  <div class="function-item" :class="{ 'active-function-item': currentFunction === 'import' }" @click="handleFunctionClick('import')">
                    <span class="item-icon">⚙️</span><span>数据导入</span>
                  </div>
                  <div class="function-item" :class="{ 'active-function-item': currentFunction === 'export' }" @click="handleFunctionClick('export')">
                    <span class="item-icon">⚙️</span><span>数据导出</span>
                  </div>
                  <div class="function-item" :class="{ 'active-function-item': currentFunction === 'logs' }" @click="handleFunctionClick('logs')">
                    <span class="item-icon">⚙️</span><span>系统日志</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 权限设置抽屉 -->
            <div class="drawer-item">
              <div 
                class="drawer-header"
                @click="toggleDrawer('rbac')"
              >
                <div class="drawer-title">
                  <span>权限设置</span>
                </div>
                <span 
                  class="drawer-arrow"
                  :class="{ 'drawer-arrow-expanded': drawerStates.rbac }"
                >
                  
                </span>
              </div>
              <div 
                class="drawer-content"
                :class="{ 'drawer-content-expanded': drawerStates.rbac }"
              >
                <div class="drawer-body">
                  <div v-if="(console.log('Checking menu:rbac_user:', authStore.hasPermission('menu:rbac_user')), authStore.hasPermission('menu:rbac_user'))" class="function-item" :class="{ 'active-function-item': currentFunction === 'rbac_user' }" @click="handleFunctionClick('rbac_user')">
                    <span class="item-icon">👥</span><span>用户管理</span>
                  </div>
                  <div v-if="(console.log('Checking menu:rbac_role:', authStore.hasPermission('menu:rbac_role')), authStore.hasPermission('menu:rbac_role'))" class="function-item" :class="{ 'active-function-item': currentFunction === 'rbac_role' }" @click="handleFunctionClick('rbac_role')">
                    <span class="item-icon">🔑</span><span>角色管理</span>
                  </div>
                  <div v-if="(console.log('Checking menu:rbac_perm:', authStore.hasPermission('menu:rbac_perm')), authStore.hasPermission('menu:rbac_perm'))" class="function-item" :class="{ 'active-function-item': currentFunction === 'rbac_perm' }" @click="handleFunctionClick('rbac_perm')">
                    <span class="item-icon">⚙️</span><span>权限管理</span>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>
      <!-- 底部退出登录按钮 -->
      <div class="logout-bottom-fixed">
        <span class="logout-btn" @click="logout">退出登录</span>
      </div>
    </div>
    
    <!-- 右侧区域 -->
    <div class="right-panel">
      <!-- 内容区域 -->
      <div class="content-area">
        <!-- 聊天界面 -->
        <div v-if="currentView === 'chat'" class="chat-area">
          <!-- 聊天内容区域 -->
          <div class="chat-content">
            <!-- 欢迎界面 -->
            <div v-if="messages.length === 0" class="welcome-content">
              <div class="welcome-header">
                <div class="robot-icon">🤖</div>
                <h1>ChatGPT 中文版</h1>
                <p>我可以帮您写代码、读文件、写作各种创意内容，请把您的任务交给我吧～</p>
              </div>
              
              <!-- 快捷提示词 -->
              <div class="quick-prompts">
                <div class="prompt-row">
                  <div class="prompt-item">
                    <div class="prompt-icon">♻️</div>
                    <span>减少塑料垃圾...</span>
                  </div>
                  <div class="prompt-item">
                    <div class="prompt-icon">❤️</div>
                    <span>情感分析...</span>
                  </div>
                  <div class="prompt-item">
                    <div class="prompt-icon">🏃</div>
                    <span>100米短跑...</span>
                  </div>
                  <div class="prompt-item">
                    <div class="prompt-icon">⚛️</div>
                    <span>量子力学</span>
                  </div>
                </div>
                <div class="prompt-row">
                  <div class="prompt-item">
                    <div class="prompt-icon">🚭</div>
                    <span>吸烟相关...</span>
                  </div>
                  <div class="prompt-item">
                    <div class="prompt-icon">🎬</div>
                    <span>《肖申克的...</span>
                  </div>
                  <div class="prompt-item">
                    <div class="prompt-icon">👨‍🍳</div>
                    <span>如何学做菜</span>
                  </div>
                  <div class="prompt-item">
                    <div class="prompt-icon">🧠</div>
                    <span>心理学家</span>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 消息列表 -->
            <div v-else class="messages-list">
              <div
                v-for="message in messages"
                :key="message.id"
                class="message-item"
                :class="{ 'user-message': message.role === 'user' }"
              >
                <!-- Avatar -->
                <div class="message-avatar">
                  <span v-if="message.role === 'user'">👤</span>
                  <span v-else>🤖</span>
                </div>

                <!-- Message Bubble Wrapper -->
                <div class="message-bubble-wrapper">
                  <div class="message-text-new">{{ message.content }}</div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 输入框区域（固定在底部） -->
          <!-- <div class="input-area">
            <div class="input-container">
              <span class="input-icon-plus">+</span>
              <input
                v-model="currentMessage"
                placeholder="向 ChatGPT 中文版发消息，或使用 @ 搜索应用"
                class="message-input"
                @keydown.enter="sendMessage"
              />
              <div class="input-actions-new">
                <button class="send-square-button" @click="sendMessage">➤</button>
              </div>
            </div>
          </div> -->
        </div>

        <!-- 功能界面 -->
        <div v-else-if="currentView === 'function'" class="function-area">
          <div class="function-content">
            <div class="function-header">
              <h2>{{ getFunctionTitle(currentFunction) }}</h2>
            </div>
            
            <div class="function-body">
              <!-- 文档管理 -->
              <div v-if="currentFunction === 'documents'" class="function-panel">
                <div class="panel-section">
                  <h3>文档管理</h3>
                  <p>这里是文档管理功能界面。您可以上传、编辑、删除和组织您的文档。</p>
                  <div class="action-buttons">
                    <button class="action-btn primary">上传文档</button>
                    <button class="action-btn">创建文档</button>
                    <button class="action-btn">批量操作</button>
                  </div>
                </div>
              </div>

              <!-- 文档解析 -->
              <div v-else-if="currentFunction === 'parse'" class="function-panel">
                <div class="panel-section">
                  <h3>文档解析</h3>
                  <p>这里是文档解析功能界面。您可以解析各种格式的文档，提取文本内容。</p>
                  <div class="action-buttons">
                    <button class="action-btn primary">开始解析</button>
                    <button class="action-btn">解析历史</button>
                    <button class="action-btn">解析设置</button>
                  </div>
                </div>
              </div>

              <!-- Chunk管理 -->
              <div v-else-if="currentFunction === 'chunks'" class="function-panel">
                <div class="panel-section">
                  <h3>Chunk管理</h3>
                  <p>这里是Chunk管理功能界面。您可以管理文档的分块处理和向量化。</p>
                  <div class="action-buttons">
                    <button class="action-btn primary">创建Chunk</button>
                    <button class="action-btn">Chunk列表</button>
                    <button class="action-btn">优化设置</button>
                  </div>
                </div>
              </div>

              <!-- 模型配置 -->
              <div v-else-if="currentFunction === 'model-config'" class="function-panel">
                <div class="panel-section">
                  <h3>模型配置</h3>
                  <p>这里是模型配置功能界面。您可以配置和管理AI模型参数。</p>
                  <div class="action-buttons">
                    <button class="action-btn primary">配置模型</button>
                    <button class="action-btn">模型列表</button>
                    <button class="action-btn">性能测试</button>
                  </div>
                </div>
              </div>

              <!-- 知识库管理 -->
              <div v-else-if="currentFunction === 'kb-management'" class="function-panel">
                <KnowledgeManagement />
              </div>

              <!-- 用户管理 -->
              <div v-else-if="currentFunction === 'rbac_user'" class="function-panel">
                <UserManagement />
              </div>

              <!-- 角色管理 -->
              <div v-else-if="currentFunction === 'rbac_role'" class="function-panel">
                <RoleManagement />
              </div>

              <!-- 权限管理 -->
              <div v-else-if="currentFunction === 'rbac_perm'" class="function-panel">
                <PermissionManagement />
              </div>

              <!-- 其他功能的通用界面 -->
              <div v-else class="function-panel">
                <div class="panel-section">
                  <h3>{{ getFunctionTitle(currentFunction) }}</h3>
                  <p>{{ getFunctionTitle(currentFunction) }}功能正在开发中，敬请期待。</p>
                  <div class="action-buttons">
                    <button class="action-btn primary">开始使用</button>
                    <button class="action-btn">查看文档</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入框区域（固定在底部，现在在content-area之外） -->
      <div v-if="currentView === 'chat'" class="input-area">
        <div class="input-container">
          <button @click="createNewChatSession" class="input-icon-plus" title="创建新的对话">
            +
          </button>
          
          <!-- Element Plus 文件上传组件 -->
          <el-upload
            class="upload-demo"
            :action="'#'" 
            :multiple="true"
            :show-file-list="false"
            :accept="'image/*'"
            :http-request="dummyUploadRequest"
            :on-change="handleUploadChange"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
          >
            <button class="input-image-upload-button" title="选择文件">
              <i class="mdi mdi-image"></i>
            </button>
          </el-upload>

          <textarea
            v-model="currentMessage"
            placeholder="向 ChatGPT 中文版发消息，或使用 @ 搜索应用"
            class="message-input"
            @keydown.enter="sendMessage"
          ></textarea>
          <div class="input-actions-new">
            <button class="history-icon-button" @click="toggleHistoryDialog">
              <i class="history-icon mdi mdi-history"></i>
            </button>
            <button class="send-square-button" @click="sendMessage">➤</button>
          </div>
        </div>
      </div>

    </div>
  </div>

  <!-- 历史记录对话框 -->
  <HistoryDialog 
    :show="showHistoryDialog"
    :history-data="historyChatData"
    @update:show="showHistoryDialog = $event"
    @select-history="onSelectHistory"
  />

</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import HistoryDialog from '@/components/chat/HistoryDialog.vue' // 导入历史记录对话框组件
import { ElMessage } from 'element-plus' // 导入 Element Plus 的消息提示组件

// 导入RBAC管理组件
import UserManagement from '@/views/rbac/UserManagement.vue'
import RoleManagement from '@/views/rbac/RoleManagement.vue'
import PermissionManagement from '@/views/rbac/PermissionManagement.vue'

// 导入知识库管理组件
import KnowledgeManagement from '@/views/knowledge/KnowledgeManagement.vue'

const authStore = useAuthStore()
const router = useRouter()

// 响应式数据
const activeTab = ref('functions') // 默认显示功能tab
const currentMessage = ref('')
const messages = ref([])
const selectedModel = ref('gpt-4o-mini')
const currentView = ref('chat') // 当前右侧显示的视图：chat | function
const currentFunction = ref('') // 当前显示的功能
const selectedConversationId = ref<number | null>(null) // 新增：选中的对话ID
const showHistoryDialog = ref(false) // 控制历史记录对话框显示隐藏

// 抽屉状态管理
const drawerStates = ref({
  conversations: true,  // 对话抽屉默认展开
  knowledge: true,      // 知识库管理抽屉默认展开
  models: false,        // 模型管理抽屉默认收起
  tools: false,         // 系统工具抽屉默认收起
  history: true,        // 历史记录抽屉默认展开
  rbac: false           // 新增：权限设置抽屉默认收起
})

// 模型选项
const modelOptions = [
  { id: 'gpt-4o-mini', name: 'GPT-4o mini' },
  { id: 'gpt-4', name: 'GPT-4' },
  { id: 'gpt-3.5', name: 'GPT-3.5' },
  { id: 'claude', name: 'Claude' }
]

// 方法
function toggleDrawer(drawerName: string) {
  drawerStates.value[drawerName] = !drawerStates.value[drawerName];
  console.log(`Drawer ${drawerName} toggled. New state: ${drawerStates.value[drawerName]}`);
}

function selectConversation(id: number) {
  console.log('选择对话:', id)
  // 切换回聊天界面
  currentView.value = 'chat'
  selectedConversationId.value = id; // 设置选中对话ID
  currentFunction.value = ''; // 清空功能选中状态
  // 这里可以加载对应的对话消息
  // 模拟加载对话，清空当前消息并添加一些新消息
  messages.value = []
  messages.value.push({ id: Date.now(), role: 'assistant', content: '您好！欢迎回来。这是一个新的对话。' , timestamp: new Date()})
}

function handleFunctionClick(functionType: string) {
  console.log('点击功能:', functionType);
  currentView.value = 'function'; // 默认切换到功能界面
  currentFunction.value = functionType; // 默认设置当前功能
  selectedConversationId.value = null; // 清空对话选中状态

  // 根据功能类型进行路由跳转或显示不同内容
  switch (functionType) {
    case 'rbac_user':
      // 检查权限
      if (!authStore.hasPermission('menu:rbac_user')) {
        ElMessage.warning('您没有权限访问用户管理。');
        return;
      }
      // 移除 router.push，通过 currentFunction 渲染组件
      // router.push('/admin/rbac/users');
      break;
    case 'rbac_role':
      // 检查权限
      if (!authStore.hasPermission('menu:rbac_role')) {
        ElMessage.warning('您没有权限访问角色管理。');
        return;
      }
      // 移除 router.push，通过 currentFunction 渲染组件
      // router.push('/admin/rbac/roles');
      break;
    case 'rbac_perm':
      // 检查权限
      if (!authStore.hasPermission('menu:rbac_perm')) {
        ElMessage.warning('您没有权限访问权限管理。');
        return;
      }
      // 移除 router.push，通过 currentFunction 渲染组件
      // router.push('/admin/rbac/permissions');
      break;
    default:
      // 对于其他功能，继续在当前视图内切换显示
      break;
  }
}

// 新建对话会话
function createNewChatSession() {
  console.log('创建新对话会话')
  messages.value = [] // 清空当前消息列表
  currentMessage.value = '' // 清空输入框
  selectedConversationId.value = null // 清空选中对话ID
  currentView.value = 'chat' // 确保在聊天视图
  // 可以在这里添加一条欢迎消息，或者根据需要加载默认对话内容
  messages.value.push({ id: Date.now(), role: 'assistant', content: '您好！很高兴为您服务，请开始您的新对话吧！' , timestamp: new Date()})
}

// 模拟历史记录数据
const historyChatData = ref([
  { id: 201, title: '关于RAG技术应用的讨论', content: '讨论了RAG在问答系统中的优势和挑战，以及不同向量数据库的对比。' },
  { id: 202, title: '模型微调与参数优化指南', content: '详细记录了GPT-3模型在特定任务上的微调步骤和常见参数调优的经验。' },
  { id: 203, title: '知识库数据导入导出方案', content: '探讨了如何高效地从各种数据源导入和导出数据到知识库，包括数据清洗和格式转换。' },
  { id: 204, title: 'AI伦理与数据隐私最佳实践', content: '回顾了AI应用中涉及的伦理问题，特别是数据隐私保护的法律法规和技术实现方案。' },
  { id: 205, title: '系统日志分析与故障排查', content: '记录了系统日志的常见分析方法，以及如何根据日志快速定位和解决故障。' },
])

// 切换历史记录对话框显示状态
function toggleHistoryDialog() {
  showHistoryDialog.value = !showHistoryDialog.value
  console.log('历史记录对话框状态:', showHistoryDialog.value)
}

// 选中历史记录处理
function onSelectHistory(item: { id: number; title: string; content: string }) {
  console.log('选中历史记录:', item.title)
  // 模拟加载历史对话内容
  messages.value = [
    { id: Date.now() + 1, role: 'assistant', content: `加载历史对话：${item.title}` , timestamp: new Date()},
    { id: Date.now() + 2, role: 'assistant', content: item.content , timestamp: new Date()}
  ]
  currentView.value = 'chat' // 确保切换到聊天视图
  selectedConversationId.value = item.id // 设置选中对话ID
  currentFunction.value = null // 清空功能选中状态
  showHistoryDialog.value = false // 关闭对话框
}

// 获取功能标题
function getFunctionTitle(functionType: string) {
  const functionTitles = {
    'documents': '文档管理',
    'parse': '文档解析',
    'chunks': 'Chunk管理',
    'kb-management': '知识库管理',
    'kb-settings': '知识库设置',
    'model-config': '模型配置',
    'param-tuning': '参数调优',
    'performance': '性能监控',
    'import': '数据导入',
    'export': '数据导出',
    'logs': '系统日志',
    'rbac_user': '用户管理',
    'rbac_role': '角色管理',
    'rbac_perm': '权限管理'
  }
  return functionTitles[functionType] || '未知功能'
}

function logout() {
  authStore.logout()
  router.push('/auth/login')
}

function sendMessage() {
  if (!currentMessage.value.trim()) return

  const userMessage = {
    id: Date.now(),
    role: 'user',
    content: currentMessage.value.trim(),
    timestamp: new Date()
  }

  messages.value.push(userMessage)
  currentMessage.value = ''

  // 模拟AI回复
  setTimeout(() => {
    const aiMessage = {
      id: Date.now() + 1,
      role: 'assistant',
      content: '这是一个模拟的AI回复。',
      timestamp: new Date()
    }
    messages.value.push(aiMessage)
  }, 1000)
}

function formatTime(date: Date) {
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

// Element Plus 文件上传相关方法
const dummyUploadRequest = (options: any) => {
  // 这是一个占位函数，防止 Element Plus 自动上传
  // 实际上传逻辑将在 handleUploadChange 中处理
  console.log('dummyUploadRequest triggered, file:', options.file.name);
  options.onSuccess(); // 模拟成功
};

const handleUploadChange = (file: any, fileList: any[]) => {
  // 在这里可以获取到选择的文件并进行处理
  console.log('文件选择或状态变化:', file.name, fileList);
  // 如果是图片识别，可以在这里读取文件内容并发送给后端API
  // 或者将 fileList 存储到 selectedFiles ref 中，待用户点击发送时再统一处理
  selectedFiles.value = fileList.map((item: any) => item.raw);
};

const handleUploadSuccess = (response: any, uploadFile: any) => {
  console.log('文件上传成功:', response, uploadFile.name);
  ElMessage.success(`图片 ${uploadFile.name} 上传成功！`);
  // 清空已选择文件，如果需要
  // selectedFiles.value = [];
};

const handleUploadError = (error: Error, uploadFile: any) => {
  console.error('文件上传失败:', error, uploadFile.name);
  ElMessage.error(`图片 ${uploadFile.name} 上传失败！`);
};

// 保留 selectedFiles ref，用于存储待处理的文件
const selectedFiles = ref<File[]>([]);
</script>

<style scoped>
.main-home {
  display: flex;
  height: 100vh;
  max-height: 100vh;
  overflow: hidden;
  background-color: #ffffff;
  font-size: 12px;
}

/* 左侧面板 */
.left-panel {
  width: 280px;
  min-width: 280px;
  background-color: #f8f9fa; /* 调整为更柔和的背景色 */
  border-right: 1px solid #e9ecef;
  display: flex;
  flex-direction: column;
  max-height: 100vh; /* 限制最大高度 */
  overflow: hidden; /* 防止内容溢出 */
}

.knowledge-title {
  padding: 8px 16px; /* 统一调整为8px 16px */
  border-bottom: 1px solid #e9ecef;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f8f9fa; /* 保持原有背景色作为fallback */
  background-image: linear-gradient(90deg, rgba(173, 216, 230, 0) 0%, rgba(173, 216, 230, 0.4) 30%, rgba(173, 216, 230, 0.6) 50%, rgba(173, 216, 230, 0.4) 70%, rgba(173, 216, 230, 0) 100%); /* 发淡蓝色光束效果 */
  background-size: 400% 100%;
  animation: shimmerEffect 1.5s linear infinite alternate; /* 动画时长调整为1.5秒，并添加alternate */
}

.knowledge-title h2 {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  margin: 0;
  z-index: 1;
  position: relative;
  line-height: 16px; /* 确保文本垂直居中 */
}

/* 定义发光效果动画 */
@keyframes shimmerEffect {
  0% {
    background-position: 0% 0; /* 光束从左边开始 */
  }
  100% {
    background-position: 100% 0; /* 光束移动到右边 */
  }
}

/* Tab按钮样式 */
.tab-buttons {
  display: flex;
  border-bottom: 1px solid #e9ecef;
  background-color: #ffffff; /* Tab 按钮区域背景色 */
}

.tab-button {
  flex: 1;
  padding: 12px 16px; /* 恢复垂直内边距到12px */
  border: none;
  background: transparent;
  font-size: 14px;
  font-weight: 500;
  color: #666;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s ease;
}

.tab-button:hover {
  background: #f0f2f5; /* 调整hover背景色 */
  color: #333;
}

.tab-button.active {
  color: #1976d2;
  border-bottom-color: #1976d2;
  background: #ffffff; /* Active Tab背景色 */
  font-weight: 600;
}

.tab-content {
  /* flex: 1; */ /* 移除这里的flex，改为固定高度 */
  overflow-y: auto; /* 在这里添加滚动条 */
  display: flex; /* 让 tab-panel 能够填充空间 */
  flex-direction: column; /* 让 tab-panel 能够填充空间 */
  height: calc(100vh - 50px - 47px - 21px); /* 计算高度：总高 - 标题 - tab按钮 - 退出登录 */
  max-height: calc(100vh - 50px - 47px - 21px); /* 确保不超过视口高度 */
}

/* 对话内容 */
.conversation-content {
  padding: 16px;
}

.category-header {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 12px;
}

.conversation-item {
  padding: 12px;
  background: white;
  border-radius: 6px;
  font-size: 12px;
  color: #666;
  line-height: 1.4;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.conversation-item:hover {
  background: #f0f0f0;
}

/* 抽屉组件样式 */
.tab-panel {
  height: 100%; /* Important for scroll */
  padding-bottom: 20px; /* Adjust as needed */
  box-sizing: border-box;
}

.drawer-container {
  display: flex;
  flex-direction: column;
}

.drawer-item {
  border-bottom: 1px solid #e4e7ed;
  background: #fdfdfd; /* 调整抽屉项背景色 */
}

.drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px; /* 恢复垂直内边距到14px */
  background: #f5f7fa; /* 调整抽屉头部背景色 */
  cursor: pointer;
  transition: all 0.3s ease;
  border-bottom: 1px solid #e4e7ed;
}

.drawer-header:hover {
  background: #e9ecef; /* 调整抽屉头部hover背景色 */
}

.drawer-title {
  display: flex;
  align-items: center;
  font-size: 14px; /* 确认使用px单位 */
  font-weight: bold; /* 加粗字体 */
  color: #303133;
}

.drawer-arrow {
  color: #c0c4cc;
  transition: transform 0.3s ease;
  font-size: 12px;
  font-family: monospace;
}

.drawer-arrow-expanded {
  transform: rotate(90deg);
}

.drawer-content {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease;
  background: #ffffff; /* 调整抽屉内容背景色 */
}

.drawer-content-expanded {
  max-height: 1000px; /* 增加max-height到一个足够大的值，使其能适应内容高度并保持动画 */
}

.drawer-body {
  padding: 0;
}

.function-item,
.conversation-item {
  display: flex;
  align-items: center;
  padding: 12px 16px 12px 32px; /* 恢复垂直内边距到12px，左边距到32px */
  font-size: 13px;
  color: #606266;
  cursor: pointer;
  transition: all 0.2s ease;
  border-bottom: 1px solid #f0f2f5;
}

.item-icon {
  margin-right: 8px; /* 图标与文本的间距 */
  font-size: 18px; /* 稍微增大图标大小，从16px调整到18px */
  color: #666; /* 确保图标颜色与文本协调 */
  display: inline-block; /* 新增：确保图标作为块级元素显示 */
  vertical-align: middle; /* 新增：垂直居中对齐 */
}

.function-item:hover,
.conversation-item:hover {
  background: #e6f7ff; /* 调整列表项hover背景色 */
  color: #1890ff; /* 调整列表项hover文字颜色 */
}

.function-item:last-child,
.conversation-item:last-child {
  border-bottom: none;
}

.active-function-item {
  background-color: rgba(0, 123, 255, 0.1);
  color: #007bff; /* 选中时文字颜色更亮 */
}

.active-conversation-item {
  background-color: rgba(0, 123, 255, 0.1);
  color: #007bff; /* 选中时文字颜色更亮 */
}

/* 右侧面板 */
.right-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.top-bar {
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  background: white;
  border-bottom: 1px solid #e9ecef;
}

/* 新增右侧内容头部样式 */
/* .right-content-header {
  padding: 16px 20px;
  border-bottom: 1px solid #e9ecef;
  background-color: #ffffff;
  flex-shrink: 0;
}

.right-content-header h2 {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
}

.right-content-header p {
  font-size: 13px;
  color: #666;
  line-height: 1.5;
  margin: 0;
} */

.model-selection {
  display: flex;
  align-items: center;
  height: 100%;
}

.model-selection :deep(.v-field) {
  background: white;
  border-radius: 6px;
}

.model-selection :deep(.v-field__outline) {
  --v-field-border-opacity: 0.3;
}

.model-selection :deep(.v-field__overlay) {
  background: transparent;
}

.model-selection :deep(.v-field__input) {
  font-size: 13px;
  min-height: 32px;
  padding: 6px 12px;
}

.model-selection :deep(.v-field__append-inner) {
  padding-top: 6px;
}

.model-selection :deep(.v-input__control) {
  min-height: 32px;
}

.spacer {
  flex: 1;
}

/* .action-buttons { */
/*   display: flex; */
/*   align-items: center; */
/*   gap: 20px; */
/*   height: 100%; */
/* } */

.logout-btn {
  font-size: 13px;
  color: #666;
  cursor: pointer;
  transition: color 0.2s ease;
  padding: 8px 12px;
  border-radius: 4px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center; /* 居中按钮文本 */
  width: 100%; /* 让按钮宽度填充容器 */
}

.logout-btn:hover {
  color: #333;
  background: #f8f9fa;
}

.logout-bottom-fixed {
  padding: 8px 16px;
  border-top: 1px solid #e9ecef;
  background-color: #f8f9fa;
  flex-shrink: 0; /* 防止被压缩 */
  height: 21px; /* 固定高度 */
  display: flex;
  align-items: center;
}

/* 内容区域 */
.content-area {
  flex: 1; /* 确保内容区域占据剩余空间 */
  display: flex;
  flex-direction: column;
  background: white;
  min-height: 0; /* 新增：确保在flex容器中可以缩小 */
  max-height: 100vh; /* 限制最大高度 */
  overflow: hidden; /* 防止内容溢出 */
}

/* 聊天区域 */
.chat-area {
  flex: 1; /* 重新启用flex，让它占据content-area的剩余空间 */
  display: flex;
  flex-direction: column;
  background: white;
  min-height: 0; /* 确保在flex容器中可以缩小 */
  max-height: 100vh; /* 限制最大高度 */
  overflow: hidden; /* 防止内容溢出 */
  /* height: calc(100vh - 164px); */ /* 移除固定高度 */
}

/* 功能区域 */
.function-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
}

.function-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  /* padding: 20px; */ /* 移除此处的padding */
}

.function-header {
  /* padding-bottom: 20px; */
  border-bottom: 1px solid #e9ecef;
  /* margin-bottom: 20px; */
  padding: 8px 16px 6px 16px; /* 调整垂直内边距以微调对齐 */
  height: 30px; /* 固定高度为30px */
  display: flex; /* 启用flex布局 */
  align-items: center; /* 垂直居中 */
}

.function-header h2 {
  font-size: 16px; /* 调整字体大小为16px */
  font-weight: 600;
  color: #333;
  margin: 0;
  line-height: 16px; /* 确保文本垂直居中 */
}

.function-body {
  flex: 1;
  overflow-y: auto;
}

.function-panel {
  background: white;
  border-radius: 0; /* 移除圆角，从8px调整为0 */
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.panel-section {
  margin-bottom: 20px;
}

.panel-section h3 {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0 0 12px 0;
}

.panel-section p {
  font-size: 14px;
  color: #666;
  line-height: 1.5;
  margin: 0 0 16px 0;
}

.action-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.action-btn {
  padding: 10px 20px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  color: #333;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.action-btn:hover {
  border-color: #007bff;
  color: #007bff;
}

.action-btn.primary {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.action-btn.primary:hover {
  background: #0056b3;
  border-color: #0056b3;
}

.chat-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  min-height: 0; /* 新增：确保在flex容器中可以缩小 */
}

.welcome-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  max-width: 1200px; /* 从1000px调整为1200px */
  margin: 0 auto;
}

.welcome-header {
  text-align: center;
  margin-bottom: 40px;
}

.robot-icon {
  font-size: 60px;
  color: #666;
  margin-bottom: 16px;
}

.welcome-header h1 {
  font-size: 28px;
  font-weight: 600;
  color: #333;
  margin: 16px 0;
}

.welcome-header p {
  font-size: 14px;
  color: #666;
  line-height: 1.5;
}

.quick-prompts {
  width: 100%;
  max-width: 600px;
}

.prompt-row {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  justify-content: center;
}

.prompt-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  min-width: 120px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.prompt-item:hover {
  background: #e9ecef;
  transform: translateY(-2px);
}

.prompt-icon {
  font-size: 20px;
  margin-bottom: 8px;
}

.prompt-item span {
  font-size: 11px;
  color: #666;
  text-align: center;
}

.messages-list {
  max-width: 1200px; /* 从1000px调整为1200px */
  margin: 0 auto;
}

.message-item {
  margin-bottom: 20px;
  display: flex;
  align-items: center; /* 从flex-start调整为center，使头像与消息气泡内容垂直居中 */
  gap: 8px;
}

.user-message {
  flex-direction: row-reverse; /* 用户消息方向反转，使头像在右侧 */
  margin-left: auto; /* 将整个消息项推到右侧 */
}

.message-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%; /* 圆形头像 */
  background-color: #eee; /* 头像背景色 */
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 16px;
  /* 移除所有 margin */
  flex-shrink: 0; /* 防止头像被压缩 */
}

/* .user-message .message-avatar {
  margin-left: 8px;
  margin-right: 0;
} */

/* .message-content {
  max-width: 80%;
} */

/* .user-message .message-content {
  margin-left: auto;
} */

/* .message-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
} */

/* .sender {
  font-weight: 600;
  font-size: 12px;
} */

/* .timestamp {
  font-size: 11px;
  color: #999;
} */

/* 新增消息气泡容器和内容样式 */
.message-bubble-wrapper {
  display: flex;
  flex-direction: column;
  max-width: 80%; /* 控制气泡最大宽度 */
}

.user-message .message-bubble-wrapper {
  align-items: flex-end; /* 用户消息气泡内容靠右对齐 */
}

/* .message-header-new {
  font-size: 11px;
  color: #999;
  margin-bottom: 4px;
  display: flex;
  justify-content: flex-start;
}

.user-message .message-header-new {
  justify-content: flex-end;
} */

.message-text-new {
  padding: 10px 14px;
  line-height: 1.5;
  font-size: 12px;
  /* max-width: 80%; */ /* 移除此处的max-width，由message-bubble-wrapper控制 */
}

.user-message .message-text-new {
  background: #e6f7ff;
  color: #333;
  border: 1px solid #cce7ff;
  border-radius: 0; /* 移除圆角，从12px调整为0 */
}

.message-item:not(.user-message) .message-text-new {
  background: #f0f2f5;
  color: #333;
  border-radius: 0; /* 移除圆角，从12px调整为0 */
}

/* 输入区域 */
.input-area {
  padding: 10px 20px; /* 调整外边距，顶部和底部10px，左右20px */
  background: white;
  border-top: 1px solid #e9ecef;
}

.input-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 8px; /* 调整图标之间的空隙 */
  border: 1px solid #e9ecef;
  border-radius: 5px;
  padding: 8px 12px; /* 调整内部内边距，使其更紧凑 */
  background: #f8f9fa;
}

.message-input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 14px;
  padding: 4px 0; /* 调整输入框内部文字的垂直内边距 */
  line-height: 1.5; /* 确保行高适中 */
  vertical-align: middle; /* 尝试垂直居中对齐 */
  resize: none; /* 禁用用户调整textarea大小 */
  border-left: 1px solid #e9ecef; /* 新增：左侧竖线 */
  padding-left: 12px; /* 新增：竖线和文字之间的间距 */
}

.input-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.input-icon {
  font-size: 16px;
  color: #666;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background-color 0.2s ease;
}

.input-icon:hover {
  background: #e9ecef;
}

/* .send-btn {
  background: #007bff;
  color: white;
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.2s ease;
}

.send-btn:hover {
  background: #0056b3;
}

.send-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
} */

/* 新增聊天输入区域样式 */
.input-icon-plus {
  font-size: 24px;
  color: #007bff;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0 5px; /* 调整内边距，减小空隙 */
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

/* 新增图片上传按钮样式 */
.input-image-upload-button {
  font-size: 20px;
  color: #666;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0 5px; /* 调整内边距，减小空隙 */
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.input-actions-new {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* .search-button {
  background: transparent;
  border: 1px solid #ddd;
  border-radius: 20px;
  padding: 6px 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s ease;
}

.search-button:hover {
  border-color: #007bff;
  color: #007bff;
}

.icon-globe {
  font-size: 16px;
} */

.send-square-button {
  width: 36px;
  height: 36px;
  background: #007bff;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s ease;
  color: white; /* 确保箭头颜色为白色 */
  font-size: 20px; /* 调整箭头大小 */
}

/* 新增历史记录图标按钮样式 */
.history-icon-button {
  background-color:rgb(209, 199, 181); /* 添加背景色 */
  border: none;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.2s ease;
  border-radius: 8px;
}

.history-icon-button:hover {
  background: #e9ecef;
}

.history-icon {
  font-size: 20px;
  color: #666;
}

.send-square-button:hover {
  background: #0056b3;
}

.send-square-button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* 响应式 */
@media (max-width: 768px) {
  .left-panel {
    width: 240px;
    min-width: 240px;
  }
  
  .prompt-row {
    flex-wrap: wrap;
  }
  
  .prompt-item {
    min-width: 100px;
  }
}

/* 暗色主题 */
.v-theme--dark .main-home {
  background-color: #121212;
}

.v-theme--dark .left-panel {
  background-color: #1e1e1e;
  border-color: #333;
}

.v-theme--dark .knowledge-title h2 {
  color: #ffffff;
}

.v-theme--dark .top-bar,
.v-theme--dark .chat-area {
  background: #121212;
  border-color: #333;
}

.v-theme--dark .function-group,
.v-theme--dark .conversation-item {
  background: #2d2d2d;
}

.v-theme--dark .welcome-header h1 {
  color: #ffffff;
}

.v-theme--dark .welcome-header p {
  color: #b3b3b3;
}

.v-theme--dark .prompt-item {
  background: #2d2d2d;
}

.v-theme--dark .prompt-item:hover {
  background: #3d3d3d;
}

.v-theme--dark .message-item:not(.user-message) .message-text {
  background: #2d2d2d;
  color: #ffffff;
}

.v-theme--dark .input-container {
  background: #2d2d2d;
  border-color: #333;
}

.v-theme--dark .message-input {
  color: #ffffff;
}
</style>