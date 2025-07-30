<template>
  <div class="knowledge-library">
    <!-- 页面标题栏 -->
    <div class="d-flex align-center justify-space-between mb-6">
      <div>
        <h1 class="text-h4 font-weight-bold text-primary mb-2">
          知识库管理
        </h1>
        <p class="text-body-1 text-medium-emphasis">
          管理和组织您的知识库，支持文档分类和智能检索
        </p>
      </div>
      <v-btn
        color="primary"
        variant="elevated"
        prepend-icon="mdi-plus"
        @click="showCreateDialog = true"
      >
        创建知识库
      </v-btn>
    </div>

    <!-- 搜索和过滤栏 -->
    <v-card class="mb-6" variant="outlined">
      <v-card-text>
        <v-row align="center">
          <v-col cols="12" md="4">
            <v-text-field
              v-model="searchQuery"
              placeholder="搜索知识库..."
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              density="compact"
              hide-details
              clearable
            />
          </v-col>
          <v-col cols="12" md="2">
            <v-select
              v-model="statusFilter"
              :items="statusOptions"
              label="状态筛选"
              variant="outlined"
              density="compact"
              hide-details
            />
          </v-col>
          <v-col cols="12" md="2">
            <v-select
              v-model="typeFilter"
              :items="typeOptions"
              label="类型筛选"
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
          <v-col cols="12" md="2">
            <div class="d-flex gap-2">
              <v-btn-toggle
                v-model="viewMode"
                mandatory
                variant="outlined"
                density="compact"
              >
                <v-btn value="grid" icon="mdi-view-grid" />
                <v-btn value="list" icon="mdi-view-list" />
              </v-btn-toggle>
            </div>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- 知识库网格视图 -->
    <div v-if="viewMode === 'grid'">
      <v-row>
        <v-col
          v-for="kb in filteredKnowledgeBases"
          :key="kb.id"
          cols="12" 
          sm="6" 
          md="4" 
          lg="3"
        >
          <v-card
            class="knowledge-card fill-height"
            variant="outlined"
            hover
            @click="viewKnowledgeBase(kb)"
          >
            <div class="knowledge-card-header" :style="{ backgroundColor: kb.color }">
              <v-icon size="48" color="white" class="ma-4">
                {{ getKnowledgeBaseIcon(kb.type) }}
              </v-icon>
              <v-menu location="bottom end">
                <template v-slot:activator="{ props }">
                  <v-btn
                    v-bind="props"
                    icon="mdi-dots-vertical"
                    variant="text"
                    color="white"
                    size="small"
                    class="card-menu-btn"
                    @click.stop
                  />
                </template>
                <v-list density="compact">
                  <v-list-item @click="editKnowledgeBase(kb)">
                    <template v-slot:prepend>
                      <v-icon>mdi-pencil</v-icon>
                    </template>
                    <v-list-item-title>编辑</v-list-item-title>
                  </v-list-item>
                  <v-list-item @click="duplicateKnowledgeBase(kb)">
                    <template v-slot:prepend>
                      <v-icon>mdi-content-copy</v-icon>
                    </template>
                    <v-list-item-title>复制</v-list-item-title>
                  </v-list-item>
                  <v-list-item @click="exportKnowledgeBase(kb)">
                    <template v-slot:prepend>
                      <v-icon>mdi-export</v-icon>
                    </template>
                    <v-list-item-title>导出</v-list-item-title>
                  </v-list-item>
                  <v-divider />
                  <v-list-item @click="deleteKnowledgeBase(kb)" class="text-error">
                    <template v-slot:prepend>
                      <v-icon color="error">mdi-delete</v-icon>
                    </template>
                    <v-list-item-title>删除</v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-menu>
            </div>

            <v-card-text class="pb-2">
              <h3 class="text-h6 font-weight-bold mb-2 text-truncate">
                {{ kb.name }}
              </h3>
              <p class="text-body-2 text-medium-emphasis mb-3 line-clamp-2">
                {{ kb.description }}
              </p>
              
              <div class="d-flex align-center mb-2">
                <v-chip
                  :color="getStatusColor(kb.status)"
                  size="small"
                  variant="tonal"
                >
                  {{ kb.status }}
                </v-chip>
                <v-spacer />
                <span class="text-caption text-medium-emphasis">
                  {{ kb.documents }} 个文档
                </span>
              </div>
            </v-card-text>

            <v-card-actions class="pt-0">
              <div class="d-flex align-center w-100">
                <v-avatar size="24" class="mr-2">
                  <v-img :src="kb.owner.avatar" :alt="kb.owner.name">
                    <template v-slot:placeholder>
                      <v-icon>mdi-account</v-icon>
                    </template>
                  </v-img>
                </v-avatar>
                <span class="text-caption text-medium-emphasis flex-grow-1 text-truncate">
                  {{ kb.owner.name }}
                </span>
                <span class="text-caption text-medium-emphasis">
                  {{ formatDate(kb.updatedAt) }}
                </span>
              </div>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </div>

    <!-- 知识库列表视图 -->
    <div v-else>
      <v-card variant="outlined">
        <v-data-table
          :headers="tableHeaders"
          :items="filteredKnowledgeBases"
          :search="searchQuery"
          item-key="id"
          class="knowledge-table"
        >
          <template v-slot:item.name="{ item }">
            <div class="d-flex align-center">
              <v-avatar
                :color="item.color"
                size="32"
                class="mr-3"
              >
                <v-icon color="white" size="16">
                  {{ getKnowledgeBaseIcon(item.type) }}
                </v-icon>
              </v-avatar>
              <div>
                <div class="font-weight-bold">{{ item.name }}</div>
                <div class="text-caption text-medium-emphasis">
                  {{ item.description }}
                </div>
              </div>
            </div>
          </template>

          <template v-slot:item.status="{ item }">
            <v-chip
              :color="getStatusColor(item.status)"
              size="small"
              variant="tonal"
            >
              {{ item.status }}
            </v-chip>
          </template>

          <template v-slot:item.owner="{ item }">
            <div class="d-flex align-center">
              <v-avatar size="24" class="mr-2">
                <v-img :src="item.owner.avatar" :alt="item.owner.name">
                  <template v-slot:placeholder>
                    <v-icon size="12">mdi-account</v-icon>
                  </template>
                </v-img>
              </v-avatar>
              {{ item.owner.name }}
            </div>
          </template>

          <template v-slot:item.updatedAt="{ item }">
            {{ formatDate(item.updatedAt) }}
          </template>

          <template v-slot:item.actions="{ item }">
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
                <v-list-item @click="viewKnowledgeBase(item)">
                  <template v-slot:prepend>
                    <v-icon>mdi-eye</v-icon>
                  </template>
                  <v-list-item-title>查看</v-list-item-title>
                </v-list-item>
                <v-list-item @click="editKnowledgeBase(item)">
                  <template v-slot:prepend>
                    <v-icon>mdi-pencil</v-icon>
                  </template>
                  <v-list-item-title>编辑</v-list-item-title>
                </v-list-item>
                <v-list-item @click="duplicateKnowledgeBase(item)">
                  <template v-slot:prepend>
                    <v-icon>mdi-content-copy</v-icon>
                  </template>
                  <v-list-item-title>复制</v-list-item-title>
                </v-list-item>
                <v-divider />
                <v-list-item @click="deleteKnowledgeBase(item)" class="text-error">
                  <template v-slot:prepend>
                    <v-icon color="error">mdi-delete</v-icon>
                  </template>
                  <v-list-item-title>删除</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </template>
        </v-data-table>
      </v-card>
    </div>

    <!-- 创建知识库对话框 -->
    <v-dialog v-model="showCreateDialog" max-width="600">
      <v-card>
        <v-card-title class="text-h5">创建知识库</v-card-title>
        
        <v-card-text>
          <v-form ref="createFormRef" v-model="createFormValid">
            <v-text-field
              v-model="createForm.name"
              label="知识库名称"
              :rules="nameRules"
              variant="outlined"
              class="mb-4"
            />
            
            <v-textarea
              v-model="createForm.description"
              label="描述"
              rows="3"
              variant="outlined"
              class="mb-4"
            />
            
            <v-select
              v-model="createForm.type"
              :items="typeOptions"
              label="知识库类型"
              variant="outlined"
              class="mb-4"
            />
            
            <div class="mb-4">
              <v-label class="mb-2">选择颜色</v-label>
              <div class="d-flex gap-2 flex-wrap">
                <v-btn
                  v-for="color in colorOptions"
                  :key="color.value"
                  :color="color.value"
                  variant="elevated"
                  size="small"
                  class="color-btn"
                  @click="createForm.color = color.value"
                >
                  <v-icon v-if="createForm.color === color.value">
                    mdi-check
                  </v-icon>
                </v-btn>
              </div>
            </div>
            
            <v-switch
              v-model="createForm.isPublic"
              label="公开知识库"
              color="primary"
              hide-details
            />
          </v-form>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showCreateDialog = false">取消</v-btn>
          <v-btn
            color="primary"
            @click="createKnowledgeBase"
            :disabled="!createFormValid"
          >
            创建
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 删除确认对话框 -->
    <v-dialog v-model="showDeleteDialog" max-width="400">
      <v-card>
        <v-card-title class="text-h6">确认删除</v-card-title>
        <v-card-text>
          确定要删除知识库 "{{ selectedKB?.name }}" 吗？此操作不可撤销。
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
import { useRouter } from 'vue-router'

const router = useRouter()

// 响应式数据
const searchQuery = ref('')
const statusFilter = ref('全部')
const typeFilter = ref('全部')
const sortBy = ref('更新时间')
const viewMode = ref('grid')
const showCreateDialog = ref(false)
const showDeleteDialog = ref(false)
const createFormRef = ref()
const createFormValid = ref(false)
const selectedKB = ref(null)

// 筛选选项
const statusOptions = ['全部', '活跃', '维护中', '已禁用']
const typeOptions = ['全部', '技术文档', '产品手册', '培训资料', '法律文件', '其他']
const sortOptions = ['更新时间', '创建时间', '名称', '文档数量']

// 颜色选项
const colorOptions = [
  { name: '蓝色', value: '#1976D2' },
  { name: '绿色', value: '#388E3C' },
  { name: '橙色', value: '#F57C00' },
  { name: '紫色', value: '#7B1FA2' },
  { name: '红色', value: '#D32F2F' },
  { name: '青色', value: '#0097A7' }
]

// 创建表单
const createForm = reactive({
  name: '',
  description: '',
  type: '技术文档',
  color: '#1976D2',
  isPublic: false
})

// 表单验证规则
const nameRules = [
  (v: string) => !!v || '请输入知识库名称',
  (v: string) => v.length >= 2 || '名称至少2个字符'
]

// 表格标题
const tableHeaders = [
  { title: '名称', key: 'name', sortable: true },
  { title: '类型', key: 'type', sortable: true },
  { title: '状态', key: 'status', sortable: true },
  { title: '文档数', key: 'documents', sortable: true },
  { title: '所有者', key: 'owner', sortable: false },
  { title: '更新时间', key: 'updatedAt', sortable: true },
  { title: '操作', key: 'actions', sortable: false }
]

// 模拟知识库数据
const knowledgeBases = ref([
  {
    id: 1,
    name: 'AI技术文档',
    description: '人工智能相关技术文档和研究资料',
    type: '技术文档',
    status: '活跃',
    documents: 156,
    color: '#1976D2',
    isPublic: true,
    owner: { name: 'Alice', avatar: '' },
    createdAt: new Date('2024-01-15'),
    updatedAt: new Date('2024-01-20')
  },
  {
    id: 2,
    name: '产品使用手册',
    description: '产品功能介绍和使用指南',
    type: '产品手册',
    status: '活跃',
    documents: 89,
    color: '#388E3C',
    isPublic: true,
    owner: { name: 'Bob', avatar: '' },
    createdAt: new Date('2024-01-10'),
    updatedAt: new Date('2024-01-18')
  },
  {
    id: 3,
    name: '内部培训资料',
    description: '员工培训和技能提升相关材料',
    type: '培训资料',
    status: '维护中',
    documents: 234,
    color: '#F57C00',
    isPublic: false,
    owner: { name: 'Charlie', avatar: '' },
    createdAt: new Date('2024-01-05'),
    updatedAt: new Date('2024-01-16')
  },
  {
    id: 4,
    name: '法律合规文档',
    description: '法律法规和合规要求相关文档',
    type: '法律文件',
    status: '活跃',
    documents: 67,
    color: '#7B1FA2',
    isPublic: false,
    owner: { name: 'Diana', avatar: '' },
    createdAt: new Date('2024-01-08'),
    updatedAt: new Date('2024-01-19')
  }
])

// 过滤后的知识库
const filteredKnowledgeBases = computed(() => {
  let filtered = knowledgeBases.value

  // 状态筛选
  if (statusFilter.value !== '全部') {
    filtered = filtered.filter(kb => kb.status === statusFilter.value)
  }

  // 类型筛选
  if (typeFilter.value !== '全部') {
    filtered = filtered.filter(kb => kb.type === typeFilter.value)
  }

  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(kb => 
      kb.name.toLowerCase().includes(query) ||
      kb.description.toLowerCase().includes(query)
    )
  }

  // 排序
  filtered.sort((a, b) => {
    switch (sortBy.value) {
      case '名称':
        return a.name.localeCompare(b.name)
      case '创建时间':
        return b.createdAt.getTime() - a.createdAt.getTime()
      case '文档数量':
        return b.documents - a.documents
      default: // 更新时间
        return b.updatedAt.getTime() - a.updatedAt.getTime()
    }
  })

  return filtered
})

// 获取知识库图标
function getKnowledgeBaseIcon(type: string) {
  const icons = {
    '技术文档': 'mdi-code-tags',
    '产品手册': 'mdi-book-open-variant',
    '培训资料': 'mdi-school',
    '法律文件': 'mdi-gavel',
    '其他': 'mdi-folder'
  }
  return icons[type] || 'mdi-folder'
}

// 获取状态颜色
function getStatusColor(status: string) {
  const colors = {
    '活跃': 'success',
    '维护中': 'warning',
    '已禁用': 'error'
  }
  return colors[status] || 'default'
}

// 格式化日期
function formatDate(date: Date) {
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

// 查看知识库
function viewKnowledgeBase(kb: any) {
  router.push(`/knowledge/${kb.id}`)
}

// 编辑知识库
function editKnowledgeBase(kb: any) {
  // 实现编辑逻辑
  console.log('编辑知识库:', kb.name)
}

// 复制知识库
function duplicateKnowledgeBase(kb: any) {
  // 实现复制逻辑
  console.log('复制知识库:', kb.name)
}

// 导出知识库
function exportKnowledgeBase(kb: any) {
  // 实现导出逻辑
  console.log('导出知识库:', kb.name)
}

// 删除知识库
function deleteKnowledgeBase(kb: any) {
  selectedKB.value = kb
  showDeleteDialog.value = true
}

// 确认删除
function confirmDelete() {
  if (selectedKB.value) {
    const index = knowledgeBases.value.findIndex(kb => kb.id === selectedKB.value.id)
    if (index > -1) {
      knowledgeBases.value.splice(index, 1)
    }
    showDeleteDialog.value = false
    selectedKB.value = null
  }
}

// 创建知识库
async function createKnowledgeBase() {
  if (!createFormValid.value) return

  const newKB = {
    id: Date.now(),
    name: createForm.name,
    description: createForm.description,
    type: createForm.type,
    status: '活跃',
    documents: 0,
    color: createForm.color,
    isPublic: createForm.isPublic,
    owner: { name: '当前用户', avatar: '' },
    createdAt: new Date(),
    updatedAt: new Date()
  }

  knowledgeBases.value.unshift(newKB)
  showCreateDialog.value = false
  
  // 重置表单
  Object.assign(createForm, {
    name: '',
    description: '',
    type: '技术文档',
    color: '#1976D2',
    isPublic: false
  })
}
</script>

<style scoped>
.knowledge-library {
  max-width: 1400px;
  margin: 0 auto;
}

.knowledge-card {
  position: relative;
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
  cursor: pointer;
}

.knowledge-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
}

.knowledge-card-header {
  position: relative;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-menu-btn {
  position: absolute;
  top: 8px;
  right: 8px;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.color-btn {
  min-width: 40px !important;
  height: 40px !important;
}

.knowledge-table :deep(.v-data-table-header) {
  background-color: rgb(var(--v-theme-surface-variant));
}

/* 响应式调整 */
@media (max-width: 960px) {
  .knowledge-library {
    padding: 0 8px;
  }
  
  .knowledge-card-header {
    height: 80px;
  }
}
</style>