<template>
  <div class="document-management">
    <!-- 页面标题栏 -->
    <div class="d-flex align-center justify-space-between mb-6">
      <div>
        <h1 class="text-h4 font-weight-bold text-primary mb-2">
          文档管理
        </h1>
        <p class="text-body-1 text-medium-emphasis">
          上传、管理和处理文档，支持PDF、Word、Excel等多种格式
        </p>
      </div>
      <v-btn
        color="primary"
        variant="elevated"
        prepend-icon="mdi-upload"
        @click="showUploadDialog = true"
      >
        上传文档
      </v-btn>
    </div>

    <!-- 统计卡片 -->
    <v-row class="mb-6">
      <v-col
        v-for="stat in documentStats"
        :key="stat.title"
        cols="12"
        sm="6"
        md="3"
      >
        <v-card variant="outlined" class="stat-card">
          <v-card-text>
            <div class="d-flex align-center">
              <div class="flex-grow-1">
                <div class="text-caption text-medium-emphasis mb-1">
                  {{ stat.title }}
                </div>
                <div class="text-h5 font-weight-bold text-primary">
                  {{ stat.value }}
                </div>
                <div class="text-caption" :class="`text-${stat.trend === 'up' ? 'success' : 'error'}`">
                  <v-icon size="12" class="mr-1">
                    {{ stat.trend === 'up' ? 'mdi-trending-up' : 'mdi-trending-down' }}
                  </v-icon>
                  {{ stat.change }}
                </div>
              </div>
              <v-avatar
                :color="stat.color"
                size="48"
                class="stat-icon"
              >
                <v-icon color="white" size="24">
                  {{ stat.icon }}
                </v-icon>
              </v-avatar>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 搜索和过滤栏 -->
    <v-card class="mb-6" variant="outlined">
      <v-card-text>
        <v-row align="center">
          <v-col cols="12" md="3">
            <v-text-field
              v-model="searchQuery"
              placeholder="搜索文档..."
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              density="compact"
              hide-details
              clearable
              @keyup.enter="searchDocuments"
            />
          </v-col>
          <v-col cols="12" md="2">
            <v-select
              v-model="knowledgeBaseFilter"
              :items="knowledgeBaseOptions"
              label="知识库"
              variant="outlined"
              density="compact"
              hide-details
            />
          </v-col>
          <v-col cols="12" md="2">
            <v-select
              v-model="statusFilter"
              :items="statusOptions"
              label="处理状态"
              variant="outlined"
              density="compact"
              hide-details
            />
          </v-col>
          <v-col cols="12" md="2">
            <v-select
              v-model="typeFilter"
              :items="typeOptions"
              label="文档类型"
              variant="outlined"
              density="compact"
              hide-details
            />
          </v-col>
          <v-col cols="12" md="2">
            <v-select
              v-model="sortBy"
              :items="sortOptions"
              label="排序方式"
              variant="outlined"
              density="compact"
              hide-details
            />
          </v-col>
          <v-col cols="12" md="1">
            <div class="d-flex gap-2">
              <v-btn
                variant="outlined"
                icon="mdi-refresh"
                @click="refreshDocuments"
                :loading="loading"
                title="刷新"
              />
              <v-btn
                variant="outlined"
                icon="mdi-filter-remove"
                @click="resetFilters"
                title="重置筛选"
              />
            </div>
          </v-col>
        </v-row>
        
        <!-- 高级筛选选项 -->
        <v-expand-transition>
          <div v-if="showAdvancedFilters" class="mt-4">
            <v-divider class="mb-4" />
            <v-row>
              <v-col cols="12" md="3">
                <v-menu
                  ref="dateMenu"
                  v-model="dateMenuOpen"
                  :close-on-content-click="false"
                  transition="scale-transition"
                  offset-y
                >
                  <template v-slot:activator="{ props }">
                    <v-text-field
                      v-model="dateRangeText"
                      label="上传日期范围"
                      prepend-inner-icon="mdi-calendar"
                      readonly
                      v-bind="props"
                      variant="outlined"
                      density="compact"
                      hide-details
                    />
                  </template>
                  <v-date-picker
                    v-model="dateRange"
                    range
                    @update:model-value="dateMenuOpen = false"
                  />
                </v-menu>
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field
                  v-model="sizeFilter.min"
                  label="最小文件大小 (KB)"
                  type="number"
                  variant="outlined"
                  density="compact"
                  hide-details
                />
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field
                  v-model="sizeFilter.max"
                  label="最大文件大小 (KB)"
                  type="number"
                  variant="outlined"
                  density="compact"
                  hide-details
                />
              </v-col>
              <v-col cols="12" md="3">
                <v-autocomplete
                  v-model="tagFilter"
                  :items="availableTags"
                  label="标签"
                  multiple
                  chips
                  variant="outlined"
                  density="compact"
                  hide-details
                />
              </v-col>
            </v-row>
          </div>
        </v-expand-transition>
        
        <div class="d-flex justify-end mt-2">
          <v-btn
            variant="text"
            size="small"
            @click="showAdvancedFilters = !showAdvancedFilters"
          >
            {{ showAdvancedFilters ? '收起高级筛选' : '显示高级筛选' }}
            <v-icon right>
              {{ showAdvancedFilters ? 'mdi-chevron-up' : 'mdi-chevron-down' }}
            </v-icon>
          </v-btn>
        </div>
      </v-card-text>
    </v-card>

    <!-- 文档列表 -->
    <v-card variant="outlined">
      <v-data-table
        :headers="tableHeaders"
        :items="filteredDocuments"
        :search="searchQuery"
        :loading="loading"
        item-key="id"
        class="document-table"
      >
        <!-- 文档名称列 -->
        <template v-slot:item.name="{ item }">
          <div class="d-flex align-center">
            <v-icon
              :color="getFileTypeColor(item.type)"
              class="mr-3"
              size="32"
            >
              {{ getFileTypeIcon(item.type) }}
            </v-icon>
            <div>
              <div class="font-weight-bold">{{ item.name }}</div>
              <div class="text-caption text-medium-emphasis">
                {{ formatFileSize(item.size) }}
              </div>
            </div>
          </div>
        </template>

        <!-- 知识库列 -->
        <template v-slot:item.knowledgeBase="{ item }">
          <v-chip
            :color="item.knowledgeBase.color"
            size="small"
            variant="tonal"
          >
            {{ item.knowledgeBase.name }}
          </v-chip>
        </template>

        <!-- 状态列 -->
        <template v-slot:item.status="{ item }">
          <div class="d-flex align-center">
            <v-chip
              :color="getStatusColor(item.status)"
              size="small"
              variant="tonal"
              class="mr-2"
            >
              <v-icon size="small" start>
                {{ getStatusIcon(item.status) }}
              </v-icon>
              {{ item.status }}
            </v-chip>
            <v-progress-circular
              v-if="item.status === '处理中'"
              :model-value="item.progress"
              size="20"
              width="2"
              :color="getStatusColor(item.status)"
            />
          </div>
        </template>

        <!-- 上传者列 -->
        <template v-slot:item.uploader="{ item }">
          <div class="d-flex align-center">
            <v-avatar size="24" class="mr-2">
              <v-img :src="item.uploader.avatar" :alt="item.uploader.name">
                <template v-slot:placeholder>
                  <v-icon size="12">mdi-account</v-icon>
                </template>
              </v-img>
            </v-avatar>
            {{ item.uploader.name }}
          </div>
        </template>

        <!-- 上传时间列 -->
        <template v-slot:item.uploadedAt="{ item }">
          {{ formatDate(item.uploadedAt) }}
        </template>

        <!-- 操作列 -->
        <template v-slot:item.actions="{ item }">
          <div class="d-flex align-center">
            <v-btn
              icon="mdi-eye"
              variant="text"
              size="small"
              @click="previewDocument(item)"
              :disabled="!canPreview(item)"
            />
            <v-btn
              icon="mdi-download"
              variant="text"
              size="small"
              @click="downloadDocument(item)"
            />
            <v-menu>
              <template v-slot:activator="{ props }">
                <v-btn
                  v-bind="props"
                  icon="mdi-dots-vertical"
                  variant="text"
                  size="small"
                />
              </template>
              <v-list density="compact">
                <v-list-item @click="editDocument(item)">
                  <template v-slot:prepend>
                    <v-icon>mdi-pencil</v-icon>
                  </template>
                  <v-list-item-title>编辑信息</v-list-item-title>
                </v-list-item>
                <v-list-item @click="reprocessDocument(item)">
                  <template v-slot:prepend>
                    <v-icon>mdi-refresh</v-icon>
                  </template>
                  <v-list-item-title>重新处理</v-list-item-title>
                </v-list-item>
                <v-list-item @click="moveDocument(item)">
                  <template v-slot:prepend>
                    <v-icon>mdi-folder-move</v-icon>
                  </template>
                  <v-list-item-title>移动到...</v-list-item-title>
                </v-list-item>
                <v-divider />
                <v-list-item @click="deleteDocument(item)" class="text-error">
                  <template v-slot:prepend>
                    <v-icon color="error">mdi-delete</v-icon>
                  </template>
                  <v-list-item-title>删除</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </div>
        </template>
      </v-data-table>
    </v-card>

    <!-- 上传文档对话框 -->
    <v-dialog v-model="showUploadDialog" max-width="600" persistent>
      <v-card>
        <v-card-title class="text-h5 d-flex align-center">
          <v-icon class="mr-2">mdi-upload</v-icon>
          上传文档
        </v-card-title>
        
        <v-card-text>
          <v-form ref="uploadFormRef" v-model="uploadFormValid">
            <!-- 知识库选择 -->
            <v-select
              v-model="uploadForm.knowledgeBaseId"
              :items="knowledgeBaseOptions"
              item-title="text"
              item-value="value"
              label="选择知识库"
              :rules="requiredRules"
              variant="outlined"
              class="mb-4"
            />

            <!-- 文件上传区域 -->
            <div class="upload-area mb-4" @drop="handleDrop" @dragover.prevent @dragenter.prevent>
              <v-file-input
                v-model="uploadForm.files"
                accept=".pdf,.doc,.docx,.txt,.md,.ppt,.pptx,.xls,.xlsx"
                label="选择文件"
                multiple
                variant="outlined"
                prepend-icon="mdi-paperclip"
                show-size
                @change="handleFileChange"
              />
              
              <div class="text-center mt-4">
                <v-icon size="64" color="primary" class="mb-2">
                  mdi-cloud-upload-outline
                </v-icon>
                <p class="text-body-1">
                  拖拽文件到此处或点击选择文件
                </p>
                <p class="text-caption text-medium-emphasis">
                  支持 PDF, DOC, DOCX, TXT, MD, PPT, PPTX, XLS, XLSX 格式
                </p>
              </div>
            </div>

            <!-- 处理选项 -->
            <v-expansion-panels variant="accordion" class="mb-4">
              <v-expansion-panel title="处理选项">
                <v-expansion-panel-text>
                  <v-checkbox
                    v-model="uploadForm.enableOCR"
                    label="启用OCR文字识别"
                    hide-details
                    class="mb-2"
                  />
                  <v-checkbox
                    v-model="uploadForm.autoChunk"
                    label="自动分块处理"
                    hide-details
                    class="mb-2"
                  />
                  <v-checkbox
                    v-model="uploadForm.extractKeywords"
                    label="提取关键词"
                    hide-details
                  />
                </v-expansion-panel-text>
              </v-expansion-panel>
            </v-expansion-panels>

            <!-- 上传进度 -->
            <div v-if="uploading" class="mb-4">
              <div class="d-flex align-center justify-space-between mb-2">
                <span class="text-body-2">上传进度</span>
                <span class="text-body-2">{{ uploadProgress }}%</span>
              </div>
              <v-progress-linear
                :model-value="uploadProgress"
                color="primary"
                height="8"
                rounded
              />
            </div>
          </v-form>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer />
          <v-btn @click="cancelUpload">取消</v-btn>
          <v-btn
            color="primary"
            @click="startUpload"
            :disabled="!uploadFormValid || uploading"
            :loading="uploading"
          >
            开始上传
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 文档预览对话框 -->
    <v-dialog v-model="showPreviewDialog" max-width="900" height="600">
      <v-card class="fill-height">
        <v-card-title class="d-flex align-center">
          <v-icon class="mr-2">mdi-eye</v-icon>
          文档预览: {{ selectedDocument?.name }}
          <v-spacer />
          <v-btn
            icon="mdi-close"
            variant="text"
            @click="showPreviewDialog = false"
          />
        </v-card-title>
        
        <v-card-text class="pa-0 fill-height">
          <div class="preview-container fill-height d-flex align-center justify-center">
            <div class="text-center">
              <v-icon size="64" color="primary" class="mb-4">
                mdi-file-document-outline
              </v-icon>
              <p class="text-h6 mb-2">文档预览功能开发中</p>
              <p class="text-body-2 text-medium-emphasis">
                将支持PDF、Word、图片等格式的在线预览
              </p>
            </div>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- 删除确认对话框 -->
    <v-dialog v-model="showDeleteDialog" max-width="400">
      <v-card>
        <v-card-title class="text-h6">确认删除</v-card-title>
        <v-card-text>
          确定要删除文档 "{{ selectedDocument?.name }}" 吗？此操作不可撤销。
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showDeleteDialog = false">取消</v-btn>
          <v-btn color="error" @click="confirmDelete">删除</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'

// 响应式数据
const loading = ref(false)
const searchQuery = ref('')
const knowledgeBaseFilter = ref('全部')
const statusFilter = ref('全部')
const typeFilter = ref('全部')
const sortBy = ref('上传时间')
const showUploadDialog = ref(false)
const showPreviewDialog = ref(false)
const showDeleteDialog = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadFormRef = ref()
const uploadFormValid = ref(false)
const selectedDocument = ref(null)
const showAdvancedFilters = ref(false)
const dateMenuOpen = ref(false)
const dateRange = ref([])
const sizeFilter = reactive({
  min: null,
  max: null
})
const tagFilter = ref([])
const availableTags = ['重要', '草稿', '已审核', '机密', '公开']

// 统计数据
const documentStats = [
  {
    title: '总文档数',
    value: '1,234',
    change: '+56 本月',
    trend: 'up',
    color: 'primary',
    icon: 'mdi-file-document-multiple'
  },
  {
    title: '处理成功',
    value: '1,156',
    change: '93.7%',
    trend: 'up',
    color: 'success',
    icon: 'mdi-check-circle'
  },
  {
    title: '处理中',
    value: '45',
    change: '+12 今日',
    trend: 'up',
    color: 'warning',
    icon: 'mdi-clock-outline'
  },
  {
    title: '处理失败',
    value: '33',
    change: '-5 本周',
    trend: 'down',
    color: 'error',
    icon: 'mdi-alert-circle'
  }
]

// 筛选选项
const knowledgeBaseOptions = [
  { text: '全部知识库', value: '全部' },
  { text: 'AI技术文档', value: 1 },
  { text: '产品使用手册', value: 2 },
  { text: '内部培训资料', value: 3 },
  { text: '法律合规文档', value: 4 }
]

const statusOptions = ['全部', '处理成功', '处理中', '处理失败', '等待处理']
const typeOptions = ['全部', 'PDF', 'Word', 'Excel', 'PowerPoint', 'Text', 'Markdown']
const sortOptions = ['上传时间', '文件名', '文件大小', '处理状态']

// 表格标题
const tableHeaders = [
  { title: '文档名称', key: 'name', sortable: true },
  { title: '知识库', key: 'knowledgeBase', sortable: true },
  { title: '类型', key: 'type', sortable: true },
  { title: '状态', key: 'status', sortable: true },
  { title: '上传者', key: 'uploader', sortable: false },
  { title: '上传时间', key: 'uploadedAt', sortable: true },
  { title: '操作', key: 'actions', sortable: false }
]

// 上传表单
const uploadForm = reactive({
  knowledgeBaseId: null,
  files: [],
  enableOCR: true,
  autoChunk: true,
  extractKeywords: true
})

// 验证规则
const requiredRules = [
  (v: any) => !!v || '此字段为必填项'
]

// 模拟文档数据
const documents = ref([
  {
    id: 1,
    name: 'AI技术白皮书.pdf',
    type: 'PDF',
    size: 2048576,
    status: '处理成功',
    progress: 100,
    knowledgeBase: { name: 'AI技术文档', color: 'primary' },
    uploader: { name: 'Alice', avatar: '' },
    uploadedAt: new Date('2024-01-20T10:30:00'),
    chunks: 45,
    tags: ['重要', '已审核'],
    metadata: {
      keywords: ['人工智能', '机器学习', '深度学习', '神经网络'],
      pageCount: 32,
      author: 'AI研究团队'
    }
  },
  {
    id: 2,
    name: '产品需求文档.docx',
    type: 'Word',
    size: 1536000,
    status: '处理中',
    progress: 75,
    knowledgeBase: { name: '产品使用手册', color: 'success' },
    uploader: { name: 'Bob', avatar: '' },
    uploadedAt: new Date('2024-01-20T14:15:00'),
    chunks: 0,
    tags: ['草稿'],
    metadata: {
      keywords: ['产品', '需求', '功能', '规格'],
      pageCount: 18,
      author: '产品团队'
    }
  },
  {
    id: 3,
    name: '数据分析报告.xlsx',
    type: 'Excel',
    size: 3072000,
    status: '处理失败',
    progress: 0,
    knowledgeBase: { name: '内部培训资料', color: 'warning' },
    uploader: { name: 'Charlie', avatar: '' },
    uploadedAt: new Date('2024-01-20T09:45:00'),
    chunks: 0,
    tags: ['机密'],
    metadata: {
      keywords: ['数据', '分析', '报表', '统计'],
      error: '文件格式不支持'
    }
  },
  {
    id: 4,
    name: '法律条款说明.pdf',
    type: 'PDF',
    size: 1024000,
    status: '等待处理',
    progress: 0,
    knowledgeBase: { name: '法律合规文档', color: 'info' },
    uploader: { name: 'Diana', avatar: '' },
    uploadedAt: new Date('2024-01-20T16:20:00'),
    chunks: 0,
    tags: ['公开', '重要'],
    metadata: {
      keywords: ['法律', '条款', '合规', '规定']
    }
  },
  {
    id: 5,
    name: '用户操作手册.pdf',
    type: 'PDF',
    size: 1845000,
    status: '处理成功',
    progress: 100,
    knowledgeBase: { name: '产品使用手册', color: 'success' },
    uploader: { name: 'Eva', avatar: '' },
    uploadedAt: new Date('2024-01-19T11:20:00'),
    chunks: 28,
    tags: ['公开', '已审核'],
    metadata: {
      keywords: ['用户', '操作', '指南', '教程'],
      pageCount: 24,
      author: '技术文档团队'
    }
  },
  {
    id: 6,
    name: '研发计划书.docx',
    type: 'Word',
    size: 1245000,
    status: '处理成功',
    progress: 100,
    knowledgeBase: { name: 'AI技术文档', color: 'primary' },
    uploader: { name: 'Frank', avatar: '' },
    uploadedAt: new Date('2024-01-18T09:30:00'),
    chunks: 20,
    tags: ['机密', '重要'],
    metadata: {
      keywords: ['研发', '计划', '项目', '时间线'],
      pageCount: 15,
      author: '研发团队'
    }
  }
])

// 过滤后的文档
const filteredDocuments = computed(() => {
  let filtered = documents.value

  // 知识库筛选
  if (knowledgeBaseFilter.value !== '全部') {
    filtered = filtered.filter(doc => doc.knowledgeBase.name === knowledgeBaseFilter.value)
  }

  // 状态筛选
  if (statusFilter.value !== '全部') {
    filtered = filtered.filter(doc => doc.status === statusFilter.value)
  }

  // 类型筛选
  if (typeFilter.value !== '全部') {
    filtered = filtered.filter(doc => doc.type === typeFilter.value)
  }
  
  // 搜索查询
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(doc => 
      doc.name.toLowerCase().includes(query) || 
      (doc.metadata?.keywords?.some(kw => kw.toLowerCase().includes(query)))
    )
  }
  
  // 高级筛选 - 日期范围
  if (dateRange.value && dateRange.value.length === 2) {
    const startDate = new Date(dateRange.value[0])
    const endDate = new Date(dateRange.value[1])
    endDate.setHours(23, 59, 59, 999) // 设置为当天结束时间
    
    filtered = filtered.filter(doc => {
      const docDate = new Date(doc.uploadedAt)
      return docDate >= startDate && docDate <= endDate
    })
  }
  
  // 高级筛选 - 文件大小
  if (sizeFilter.min !== null && sizeFilter.min !== '') {
    const minBytes = Number(sizeFilter.min) * 1024 // KB转字节
    filtered = filtered.filter(doc => doc.size >= minBytes)
  }
  
  if (sizeFilter.max !== null && sizeFilter.max !== '') {
    const maxBytes = Number(sizeFilter.max) * 1024 // KB转字节
    filtered = filtered.filter(doc => doc.size <= maxBytes)
  }
  
  // 高级筛选 - 标签
  if (tagFilter.value && tagFilter.value.length > 0) {
    filtered = filtered.filter(doc => {
      // 假设文档有tags属性
      const docTags = doc.tags || []
      return tagFilter.value.some(tag => docTags.includes(tag))
    })
  }

  return filtered
})

// 获取文件类型图标
function getFileTypeIcon(type: string) {
  const icons = {
    'PDF': 'mdi-file-pdf-box',
    'Word': 'mdi-file-word-box',
    'Excel': 'mdi-file-excel-box',
    'PowerPoint': 'mdi-file-powerpoint-box',
    'Text': 'mdi-file-document-outline',
    'Markdown': 'mdi-language-markdown-outline'
  }
  return icons[type] || 'mdi-file-outline'
}

// 获取文件类型颜色
function getFileTypeColor(type: string) {
  const colors = {
    'PDF': 'error',
    'Word': 'primary',
    'Excel': 'success',
    'PowerPoint': 'warning',
    'Text': 'info',
    'Markdown': 'secondary'
  }
  return colors[type] || 'default'
}

// 获取状态颜色
function getStatusColor(status: string) {
  const colors = {
    '处理成功': 'success',
    '处理中': 'warning',
    '处理失败': 'error',
    '等待处理': 'info'
  }
  return colors[status] || 'default'
}

// 获取状态图标
function getStatusIcon(status: string) {
  const icons = {
    '处理成功': 'mdi-check-circle',
    '处理中': 'mdi-clock-outline',
    '处理失败': 'mdi-alert-circle',
    '等待处理': 'mdi-timer-sand'
  }
  return icons[status] || 'mdi-help-circle'
}

// 格式化文件大小
function formatFileSize(bytes: number) {
  const units = ['B', 'KB', 'MB', 'GB']
  let size = bytes
  let unitIndex = 0
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  
  return `${size.toFixed(1)} ${units[unitIndex]}`
}

// 格式化日期
function formatDate(date: Date) {
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 检查是否可预览
function canPreview(document: any) {
  return ['PDF', 'Text', 'Markdown'].includes(document.type) && document.status === '处理成功'
}

// 计算日期范围文本
const dateRangeText = computed(() => {
  if (!dateRange.value || dateRange.value.length !== 2) return ''
  return `${dateRange.value[0]} ~ ${dateRange.value[1]}`
})

// 刷新文档列表
function refreshDocuments() {
  loading.value = true
  setTimeout(() => {
    loading.value = false
  }, 1000)
}

// 搜索文档
function searchDocuments() {
  loading.value = true
  // 这里可以调用API进行搜索
  setTimeout(() => {
    loading.value = false
  }, 800)
}

// 重置筛选条件
function resetFilters() {
  searchQuery.value = ''
  knowledgeBaseFilter.value = '全部'
  statusFilter.value = '全部'
  typeFilter.value = '全部'
  sortBy.value = '上传时间'
  dateRange.value = []
  sizeFilter.min = null
  sizeFilter.max = null
  tagFilter.value = []
  
  // 刷新文档列表
  refreshDocuments()
}

// 预览文档
function previewDocument(document: any) {
  selectedDocument.value = document
  showPreviewDialog.value = true
}

// 下载文档
function downloadDocument(document: any) {
  console.log('下载文档:', document.name)
}

// 编辑文档信息
function editDocument(document: any) {
  console.log('编辑文档:', document.name)
}

// 重新处理文档
function reprocessDocument(document: any) {
  console.log('重新处理文档:', document.name)
}

// 移动文档
function moveDocument(document: any) {
  console.log('移动文档:', document.name)
}

// 删除文档
function deleteDocument(document: any) {
  selectedDocument.value = document
  showDeleteDialog.value = true
}

// 确认删除
function confirmDelete() {
  if (selectedDocument.value) {
    const index = documents.value.findIndex(doc => doc.id === selectedDocument.value.id)
    if (index > -1) {
      documents.value.splice(index, 1)
    }
    showDeleteDialog.value = false
    selectedDocument.value = null
  }
}

// 处理文件拖拽
function handleDrop(event: DragEvent) {
  event.preventDefault()
  const files = Array.from(event.dataTransfer?.files || [])
  uploadForm.files = files
}

// 处理文件选择
function handleFileChange(files: File[]) {
  uploadForm.files = files
}

// 开始上传
async function startUpload() {
  if (!uploadFormValid.value) return

  uploading.value = true
  uploadProgress.value = 0

  // 模拟上传进度
  const interval = setInterval(() => {
    uploadProgress.value += Math.random() * 10
    if (uploadProgress.value >= 100) {
      uploadProgress.value = 100
      clearInterval(interval)
      setTimeout(() => {
        uploading.value = false
        showUploadDialog.value = false
        // 重置表单
        Object.assign(uploadForm, {
          knowledgeBaseId: null,
          files: [],
          enableOCR: true,
          autoChunk: true,
          extractKeywords: true
        })
        uploadProgress.value = 0
      }, 500)
    }
  }, 200)
}

// 取消上传
function cancelUpload() {
  showUploadDialog.value = false
  uploading.value = false
  uploadProgress.value = 0
  Object.assign(uploadForm, {
    knowledgeBaseId: null,
    files: [],
    enableOCR: true,
    autoChunk: true,
    extractKeywords: true
  })
}
</script>

<style scoped>
.document-management {
  max-width: 1400px;
  margin: 0 auto;
}

.stat-card {
  transition: transform 0.2s ease-in-out;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-icon {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.upload-area {
  border: 2px dashed rgb(var(--v-theme-primary));
  border-radius: 8px;
  padding: 24px;
  background-color: rgba(var(--v-theme-primary), 0.05);
  transition: all 0.2s ease;
}

.upload-area:hover {
  background-color: rgba(var(--v-theme-primary), 0.1);
}

.preview-container {
  background-color: rgb(var(--v-theme-surface-variant));
}

.document-table :deep(.v-data-table-header) {
  background-color: rgb(var(--v-theme-surface-variant));
}

/* 响应式调整 */
@media (max-width: 960px) {
  .document-management {
    padding: 0 8px;
  }
}
</style>