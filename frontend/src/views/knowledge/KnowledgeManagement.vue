<template>
  <div class="knowledge-management">
    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索知识库名称"
          :prefix-icon="Search"
          @keyup.enter="handleSearch"
          clearable
          style="width: 300px"
        />
        <el-button :icon="Search" @click="handleSearch" size="small" style="margin-left: 10px">
          搜索
        </el-button>
      </div>
      <div class="actions">
        <el-button type="primary" :icon="Plus" @click="showCreateDialog" size="small">
          新增知识库
        </el-button>
        <el-button :icon="Refresh" @click="refreshKnowledgeBases" size="small">
          刷新
        </el-button>
      </div>
    </div>

    <!-- 知识库表格 -->
    <el-card shadow="never">
      <el-table
        :data="knowledgeBaseList"
        v-loading="loading"
        stripe
        style="width: 100%"
        max-height="calc(100vh - 310px)"
        @sort-change="handleSortChange"
      >
        <el-table-column label="序号" width="80">
          <template #default="scope">
            {{ pagination.pageSize * (pagination.page - 1) + scope.$index + 1 }}
          </template>
        </el-table-column>
        
        <el-table-column prop="name" label="知识库名称" min-width="150" sortable />
        
        <el-table-column prop="type" label="类型" width="120" />
        
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="文档数" width="100" align="center">
          <template #default="{ row }">
            <el-badge :value="row.stats?.documentCount || 0" :max="99" />
          </template>
        </el-table-column>
        
        <el-table-column label="所有者" width="120">
          <template #default="{ row }">
            <div class="owner-cell">
              <el-avatar :size="24">{{ row.owner?.name?.charAt(0) || 'U' }}</el-avatar>
              <span>{{ row.owner?.name }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="更新时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.updatedAt) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              :icon="Edit"
              @click="showEditDialog(row)"
            >
              编辑
            </el-button>
            <el-button
              type="warning"
              size="small"
              :icon="CopyDocument"
              @click="confirmDuplicate(row)"
            >
              复制
            </el-button>
            <el-button
              type="danger"
              size="small"
              :icon="Delete"
              @click="confirmDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          background
          layout="prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 新增/编辑知识库对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? '新增知识库' : '编辑知识库'"
      width="500px"
      @close="resetForm"
    >
      <el-form
        ref="kbFormRef"
        :model="kbForm"
        :rules="kbFormRules"
        label-width="100px"
      >
        <el-form-item label="知识库名称" prop="name">
          <el-input v-model="kbForm.name" placeholder="请输入知识库名称" />
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="kbForm.description"
            type="textarea"
            rows="3"
            placeholder="请输入知识库描述"
          />
        </el-form-item>
        
        <el-form-item label="类型" prop="type">
          <el-select v-model="kbForm.type" placeholder="请选择知识库类型" style="width: 100%">
            <el-option
              v-for="item in typeOptions"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item v-if="dialogMode === 'edit'" label="状态" prop="status">
          <el-select v-model="kbForm.status" placeholder="请选择状态" style="width: 100%">
            <el-option label="活跃" value="active" />
            <el-option label="维护中" value="maintenance" />
            <el-option label="已禁用" value="disabled" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="颜色" prop="color">
          <div class="color-selector">
            <div
              v-for="color in colorOptions"
              :key="color.value"
              class="color-item"
              :class="{ active: kbForm.color === color.value }"
              :style="{ backgroundColor: color.value }"
              @click="kbForm.color = color.value"
            >
              <el-icon v-if="kbForm.color === color.value"><Check /></el-icon>
            </div>
          </div>
        </el-form-item>
        
        <el-form-item label="公开知识库" prop="isPublic">
          <el-switch v-model="kbForm.isPublic" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="submitting">
            {{ dialogMode === 'create' ? '创建' : '更新' }}
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 复制知识库对话框 -->
    <el-dialog
      v-model="duplicateDialogVisible"
      title="复制知识库"
      width="400px"
    >
      <el-form ref="duplicateFormRef" :model="duplicateForm" :rules="duplicateRules">
        <el-form-item label="知识库名称" prop="name">
          <el-input v-model="duplicateForm.name" placeholder="请输入新知识库名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="duplicateDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitDuplicate" :loading="submitting">
            复制
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import {
  ElMessage,
  ElMessageBox,
  type FormInstance,
  type FormRules
} from 'element-plus'
import {
  Search,
  Plus,
  Refresh,
  Edit,
  Delete,
  Check,
  CopyDocument
} from '@element-plus/icons-vue'
import { knowledgeApi, type KnowledgeBase } from '@/api/knowledge'

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const knowledgeBaseList = ref<KnowledgeBase[]>([])
const searchQuery = ref('')
const dialogVisible = ref(false)
const duplicateDialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const currentKB = ref<KnowledgeBase | null>(null)

// 表单引用
const kbFormRef = ref<FormInstance>()
const duplicateFormRef = ref<FormInstance>()

// 分页数据
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 知识库表单数据
const kbForm = reactive({
  name: '',
  description: '',
  type: '技术',
  status: 'active',
  color: '#1976D2',
  isPublic: false
})

// 复制表单数据
const duplicateForm = reactive({
  name: ''
})

// 表单验证规则
const kbFormRules: FormRules = {
  name: [
    { required: true, message: '请输入知识库名称', trigger: 'blur' },
    { min: 2, max: 50, message: '名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  description: [
    { max: 500, message: '描述最多 500 个字符', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择知识库类型', trigger: 'change' }
  ]
}

const duplicateRules: FormRules = {
  name: [
    { required: true, message: '请输入知识库名称', trigger: 'blur' },
    { min: 2, max: 50, message: '名称长度在 2 到 50 个字符', trigger: 'blur' }
  ]
}

// 类型选项
const typeOptions = ['技术', '产品', '培训', '法律', '其他']

// 颜色选项
const colorOptions = [
  { name: '蓝色', value: '#1976D2' },
  { name: '绿色', value: '#388E3C' },
  { name: '橙色', value: '#F57C00' },
  { name: '紫色', value: '#7B1FA2' },
  { name: '红色', value: '#D32F2F' },
  { name: '青色', value: '#0097A7' }
]

// 方法
const fetchKnowledgeBases = async () => {
  try {
    loading.value = true
    const response = await knowledgeApi.getKnowledgeBases({
      page: pagination.page,
      pageSize: pagination.pageSize,
      search: searchQuery.value
    })
    
    // 后端返回的是直接数组，不是分页对象
    const dataArray = Array.isArray(response) ? response : response.items || []
    
    // 为每个知识库添加缺失字段
    knowledgeBaseList.value = dataArray.map(kb => ({
      ...kb,
      owner: {
        id: kb.created_by?.toString() || '1',
        name: '管理员',
        avatar: ''
      },
      stats: {
        documentCount: 0 // 临时值
      },
      // 确保字段名一致
      updatedAt: kb.updated_at,
      createdAt: kb.created_at,
      isPublic: kb.is_public
    }))
    
    pagination.total = dataArray.length // 暂时用数组长度
    console.log('KnowledgeManagement - Fetched data:', dataArray)
    console.log('KnowledgeManagement - Processed list:', knowledgeBaseList.value)
  } catch (error: any) {
    console.error('KnowledgeManagement - Fetch error:', error)
    ElMessage.error('获取知识库列表失败：' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchKnowledgeBases()
}

const handleSortChange = () => {
  fetchKnowledgeBases()
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  pagination.page = 1
  fetchKnowledgeBases()
}

const handleCurrentChange = (val: number) => {
  pagination.page = val
  fetchKnowledgeBases()
}

const refreshKnowledgeBases = () => {
  fetchKnowledgeBases()
}

const showCreateDialog = () => {
  dialogMode.value = 'create'
  resetForm()
  dialogVisible.value = true
}

const showEditDialog = (kb: KnowledgeBase) => {
  dialogMode.value = 'edit'
  currentKB.value = kb
  
  // 填充表单数据
  kbForm.name = kb.name
  kbForm.description = kb.description || ''
  kbForm.type = kb.type || '技术'
  kbForm.status = kb.status
  kbForm.color = kb.color || '#1976D2'
  kbForm.isPublic = kb.isPublic
  
  dialogVisible.value = true
}

const resetForm = () => {
  kbForm.name = ''
  kbForm.description = ''
  kbForm.type = '技术'
  kbForm.status = 'active'
  kbForm.color = '#1976D2'
  kbForm.isPublic = false
  currentKB.value = null
  kbFormRef.value?.resetFields()
}

const submitForm = async () => {
  if (!kbFormRef.value) return
  
  try {
    await kbFormRef.value.validate()
    submitting.value = true
    
    if (dialogMode.value === 'create') {
      const kbData = {
        name: kbForm.name,
        description: kbForm.description,
        type: kbForm.type,
        color: kbForm.color,
        isPublic: kbForm.isPublic
      }
      await knowledgeApi.createKnowledgeBase(kbData)
      ElMessage.success('知识库创建成功')
    } else if (dialogMode.value === 'edit' && currentKB.value) {
      const kbData = {
        name: kbForm.name,
        description: kbForm.description,
        type: kbForm.type,
        status: kbForm.status,
        color: kbForm.color,
        isPublic: kbForm.isPublic
      }
      await knowledgeApi.updateKnowledgeBase(currentKB.value.id.toString(), kbData)
      ElMessage.success('知识库更新成功')
    }
    
    dialogVisible.value = false
    fetchKnowledgeBases()
  } catch (error: any) {
    ElMessage.error(dialogMode.value === 'create' ? '创建知识库失败' : '更新知识库失败')
    console.error(error)
  } finally {
    submitting.value = false
  }
}

const confirmDelete = (kb: KnowledgeBase) => {
  ElMessageBox.confirm(
    `确定要删除知识库"${kb.name}"吗？此操作不可撤销。`,
    '删除确认',
    {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      submitting.value = true
      await knowledgeApi.deleteKnowledgeBase(kb.id.toString())
      ElMessage.success('知识库删除成功')
      fetchKnowledgeBases()
    } catch (error: any) {
      ElMessage.error('删除知识库失败：' + (error.message || '未知错误'))
    } finally {
      submitting.value = false
    }
  }).catch(() => {
    // 用户取消删除
  })
}

const confirmDuplicate = (kb: KnowledgeBase) => {
  currentKB.value = kb
  duplicateForm.name = `${kb.name} (副本)`
  duplicateDialogVisible.value = true
}

const submitDuplicate = async () => {
  if (!duplicateFormRef.value || !currentKB.value) return
  
  try {
    await duplicateFormRef.value.validate()
    submitting.value = true
    
    await knowledgeApi.duplicateKnowledgeBase(currentKB.value.id.toString(), duplicateForm.name)
    ElMessage.success('知识库复制成功')
    duplicateDialogVisible.value = false
    fetchKnowledgeBases()
  } catch (error: any) {
    ElMessage.error('复制知识库失败：' + (error.message || '未知错误'))
  } finally {
    submitting.value = false
  }
}

// 获取状态类型
const getStatusType = (status: string) => {
  const types = {
    'active': 'success',
    'maintenance': 'warning',
    'disabled': 'danger'
  }
  return types[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const texts = {
    'active': '活跃',
    'maintenance': '维护中',
    'disabled': '已禁用'
  }
  return texts[status] || status
}

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

// 初始化
onMounted(() => {
  fetchKnowledgeBases()
})
</script>

<style scoped>
.knowledge-management {
  padding: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.actions {
  display: flex;
  gap: 10px;
}

.owner-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.color-selector {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.color-item {
  width: 32px;
  height: 32px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.color-item.active {
  border: 2px solid #ffffff;
  box-shadow: 0 0 0 2px #409EFF;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.mr-1 {
  margin-right: 4px;
}
</style> 