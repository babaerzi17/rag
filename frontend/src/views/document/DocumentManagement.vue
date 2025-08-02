<template>
  <div class="document-management">
    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="search-bar">
        <el-select
          v-model="knowledgeBaseFilter"
          placeholder="选择知识库"
          clearable
          style="width: 180px; margin-right: 10px"
          @change="handleSearch"
        >
          <el-option
            v-for="kb in knowledgeBaseOptions"
            :key="kb.value"
            :label="kb.label"
            :value="kb.value"
          />
        </el-select>
        <el-input
          v-model="searchQuery"
          placeholder="搜索文档名称"
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
        <el-button type="primary" :icon="Upload" @click="showUploadDialog" size="small">
          上传文档
        </el-button>
        <el-button type="success" :icon="FolderAdd" @click="showBatchImportDialog" size="small">
          批量导入
        </el-button>
        <el-button :icon="Refresh" @click="refreshDocuments" size="small">
          刷新
        </el-button>
    </div>
                </div>

    <!-- 筛选栏 -->
    <div class="filters" style="display: none;">
      <!-- Removed: knowledge base filter, now in search-bar -->
      <!-- Removed: status filter -->
      <!-- Removed: type filter -->
    </div>

    <!-- 文档表格 -->
    <el-card shadow="never">
      <el-table
        :data="documentList"
        v-loading="loading"
        stripe
        style="width: 100%"
        max-height="calc(100vh - 350px)"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column label="序号" width="80">
          <template #default="scope">
            {{ pagination.pageSize * (pagination.page - 1) + scope.$index + 1 }}
                  </template>
        </el-table-column>
        
        <el-table-column prop="title" label="文档名称" min-width="200">
          <template #default="{ row }">
            <div class="document-name">
              <el-icon class="file-icon" :style="{ color: getFileTypeColor(row.file_type) }">
                <component :is="getFileTypeIcon(row.file_type)" />
              </el-icon>
              <div class="name-info">
                <div class="title">{{ row.title }}</div>
                <div class="file-info">{{ formatFileSize(row.file_size) }} • {{ row.file_type }}</div>
            </div>
          </div>
        </template>
        </el-table-column>
        
        <el-table-column prop="knowledge_base" label="知识库" width="150">
          <template #default="{ row }">
            <el-tag
              v-if="row.knowledge_base"
              :color="row.knowledge_base.color || '#409eff'"
              effect="light"
            size="small"
          >
              {{ row.knowledge_base.name }}
            </el-tag>
        </template>
        </el-table-column>
        
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
        </template>
        </el-table-column>
        
        <el-table-column label="文档块数" width="100" align="center">
          <template #default="{ row }">
            <el-badge :value="row.chunk_count || 0" :max="99" />
                </template>
        </el-table-column>
        
        <el-table-column label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
        </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="editDocument(row)">
              编辑
            </el-button>
            <el-button type="primary" link size="small" @click="previewDocument(row)">
              预览
            </el-button>
            <el-button type="danger" link size="small" @click="deleteDocument(row)">
              删除
            </el-button>
        </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          background
          layout="prev, pager, next"
          @current-change="handleCurrentChange"
        />
      </div>

      <!-- 批量操作 -->
      <div v-if="selectedDocuments.length > 0" class="batch-actions">
        <el-alert
          :title="`已选择 ${selectedDocuments.length} 个文档`"
          type="info"
          show-icon
          :closable="false"
        >
          <template #default>
            <div style="margin-top: 10px">
              <el-button type="danger" size="small" @click="batchDeleteDocuments">
                批量删除
              </el-button>
          </div>
        </template>
        </el-alert>
      </div>
    </el-card>

    <!-- 上传文档对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="上传文档"
      width="900px"
      @close="resetUploadForm"
    >
      <el-form
        ref="uploadFormRef"
        :model="uploadForm"
        :rules="uploadFormRules"
        label-width="100px"
      >
        <el-form-item label="知识库" prop="knowledgeBaseId">
          <el-select v-model="uploadForm.knowledgeBaseId" placeholder="请选择知识库" style="width: 100%">
            <el-option
              v-for="kb in knowledgeBaseOptions"
              :key="kb.value"
              :label="kb.label"
              :value="kb.value"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="文件选择">
          <div class="upload-container">
            <el-upload
              ref="uploadRef"
              :file-list="[]"
              :auto-upload="false"
              :on-change="handleFileChange"
              :show-file-list="false"
              accept=".pdf,.doc,.docx,.txt,.md,.ppt,.pptx,.xls,.xlsx"
            >
              <el-button type="primary" :icon="Upload" size="small">选择文件</el-button>
            </el-upload>
            
            <!-- 文件夹上传按钮 -->
            <div style="text-align: center;">
              <input
                ref="folderInputRef"
                type="file"
                webkitdirectory
                multiple
                style="display: none"
                @change="handleFolderChange"
                accept=".pdf,.doc,.docx,.txt,.md,.ppt,.pptx,.xls,.xlsx"
              />
              <el-button @click="selectFolder" :icon="FolderAdd" size="small">
                选择文件夹
              </el-button>
            </div>
          </div>
        </el-form-item>
        
        <!-- 文件列表 -->
        <el-form-item label="已选文件" v-if="uploadFileList.length > 0">
          <div class="file-list-container">
            <div class="file-list-summary">
              <span>共 {{ uploadFileList.length }} 个文件，已完成 {{ successCount }} 个，失败 {{ errorCount }} 个</span>
              <div style="margin-left: auto;">
                <el-button @click="startAllUploads" :disabled="!hasWaitingFiles || uploading" size="small" type="primary">
                  开始上传所有文件
                </el-button>
                <el-button @click="clearAllFiles" size="small">清空列表</el-button>
              </div>
            </div>
            
            <el-table
              :data="paginatedFileList"
              max-height="300px"
              style="width: 100%"
              size="small"
            >
              <el-table-column prop="name" label="文件名" min-width="200">
                <template #default="{ row }">
                  <div class="file-name-cell">
                    <el-icon class="file-icon" :style="{ color: getFileTypeColor(getFileExtension(row.name)) }">
                      <component :is="getFileTypeIcon(getFileExtension(row.name))" />
                    </el-icon>
                    <span class="file-name">{{ row.name }}</span>
                  </div>
                </template>
              </el-table-column>
              
              <el-table-column prop="size" label="大小" width="100">
                <template #default="{ row }">
                  {{ formatFileSize(row.size) }}
                </template>
              </el-table-column>
              
              <el-table-column label="状态" width="120">
                <template #default="{ row }">
                  <el-tag v-if="row.status === 'pending'" type="info" size="small">待上传</el-tag>
                  <el-tag v-else-if="row.status === 'uploading'" type="warning" size="small">上传中</el-tag>
                  <el-tag v-else-if="row.status === 'success'" type="success" size="small">已完成</el-tag>
                  <el-tag v-else-if="row.status === 'error'" type="danger" size="small">上传失败</el-tag>
                </template>
              </el-table-column>
              
              <el-table-column label="进度" width="150">
                <template #default="{ row }">
                  <el-progress
                    v-if="row.status === 'uploading' || row.status === 'success'"
                    :percentage="row.progress"
                    :status="row.status === 'success' ? 'success' : undefined"
                    size="small"
                  />
                </template>
              </el-table-column>
              
              <el-table-column label="操作" width="80">
                <template #default="{ row, $index }">
                  <el-button
                    type="danger"
                    link
                    size="small"
                    @click="removeFile(getActualIndex($index))"
                    :disabled="row.status === 'uploading'"
                  >
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            
            <!-- 文件列表分页 -->
            <div class="file-list-pagination" v-if="uploadFileList.length > fileListPageSize">
              <el-pagination
                v-model:current-page="fileListCurrentPage"
                :page-size="fileListPageSize"
                :total="uploadFileList.length"
                layout="prev, pager, next"
                size="small"
                background
              />
            </div>
          </div>
        </el-form-item>
        
        <el-form-item label="描述">
          <el-input
            v-model="uploadForm.description"
            type="textarea"
            rows="3"
            placeholder="请输入文档描述（可选）"
          />
        </el-form-item>
        
        <el-form-item label="标签">
          <el-input
            v-model="uploadForm.tags"
            placeholder="请输入标签，多个标签用逗号分隔（可选）"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="submitBatchUpload" 
            :loading="submitting"
            :disabled="!canSubmit"
          >
            提交文档
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 批量导入对话框 -->
    <el-dialog
      v-model="batchImportDialogVisible"
      title="批量导入文档"
      width="600px"
      @close="resetImportForm"
    >
      <el-form
        ref="importFormRef"
        :model="importForm"
        :rules="importFormRules"
        label-width="100px"
      >
        <el-form-item label="知识库" prop="knowledgeBaseId">
          <el-select v-model="importForm.knowledgeBaseId" placeholder="请选择知识库" style="width: 100%">
            <el-option
              v-for="kb in knowledgeBaseOptions"
              :key="kb.value"
              :label="kb.label"
              :value="kb.value"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="导入目录" prop="directoryPath">
          <el-input
            v-model="importForm.directoryPath"
            placeholder="请输入要导入的目录路径，例如: ./files"
          />
          <el-alert
            title="目录路径说明"
            description="请输入相对于项目根目录的路径，例如 ./files 表示项目根目录下的 files 文件夹"
            type="info"
            show-icon
            :closable="false"
            style="margin-top: 10px"
          />
        </el-form-item>
        
        <el-form-item label="递归导入">
          <el-switch v-model="importForm.recursive" />
          <span style="margin-left: 10px; color: #909399; font-size: 12px">
            开启后将导入子目录中的文件
          </span>
        </el-form-item>
        
        <el-form-item label="描述">
          <el-input
            v-model="importForm.description"
            type="textarea"
            rows="3"
            placeholder="请输入文档描述（可选）"
          />
        </el-form-item>
        
        <el-form-item label="标签">
          <el-input
            v-model="importForm.tags"
            placeholder="请输入标签，多个标签用逗号分隔（可选）"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="batchImportDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitImport" :loading="importing">
            开始导入
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 编辑文档对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑文档"
      width="500px"
      @close="resetEditForm"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="editFormRules"
        label-width="100px"
      >
        <el-form-item label="文档名称" prop="title">
          <el-input v-model="editForm.title" placeholder="请输入文档名称" />
        </el-form-item>
        
        <el-form-item label="描述">
          <el-input
            v-model="editForm.description"
            type="textarea"
            rows="3"
            placeholder="请输入文档描述（可选）"
          />
        </el-form-item>
        
        <el-form-item label="标签">
          <el-input
            v-model="editForm.tags"
            placeholder="请输入标签，多个标签用逗号分隔（可选）"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitEdit" :loading="editing">
            保存
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import {
  ElMessage,
  ElMessageBox,
  type FormInstance,
  type FormRules,
  type UploadUserFile
} from 'element-plus'
import {
  Search,
  Upload,
  FolderAdd,
  Refresh,
  UploadFilled,
  Document,
  DocumentCopy,
  Files,
  Notebook,
  DataBoard,
  Grid
} from '@element-plus/icons-vue'
import { documentApi, type Document as DocumentType } from '@/api/document'
import { knowledgeApi, type KnowledgeBase } from '@/api/knowledge'

// 允许的文件类型
const allowedFileTypes = [
  '.pdf', '.doc', '.docx', '.txt', '.md', '.ppt', '.pptx', '.xls', '.xlsx'
]

// 响应式数据
const loading = ref(false)
const uploading = ref(false)
const importing = ref(false)
const editing = ref(false)
const documentList = ref<DocumentType[]>([])
const selectedDocuments = ref<DocumentType[]>([])
const searchQuery = ref('')
const knowledgeBaseFilter = ref('')
const statusFilter = ref('')
const typeFilter = ref('')
const dialogVisible = ref(false)
const batchImportDialogVisible = ref(false)
const editDialogVisible = ref(false)
const currentDocument = ref<DocumentType | null>(null)

// 表单引用
const uploadFormRef = ref<FormInstance>()
const importFormRef = ref<FormInstance>()
const editFormRef = ref<FormInstance>()

// 分页数据
const pagination = reactive({
  page: 1,
  pageSize: 10, // 与知识库管理保持一致，虽然不显示，但内部逻辑可以保持
  total: 0 // 不再用于显示，但可以保留以防未来需要
})

// 知识库选项
const knowledgeBaseOptions = ref<Array<{ label: string; value: number }>>([])

// 筛选选项 (These are no longer needed for display but might be used in backend logic. Keeping for now)
const statusOptions = ['processing', 'completed', 'failed', 'pending']
const typeOptions = ['.pdf', '.doc', '.docx', '.txt', '.md', '.ppt', '.pptx', '.xls', '.xlsx']

// 上传表单数据
const uploadForm = reactive({
  knowledgeBaseId: null as number | null,
  files: [] as UploadUserFile[],
  description: '',
  tags: ''
})

// 文件上传列表管理
const uploadFileList = ref<Array<{
  id?: string
  name: string
  size: number
  status: 'pending' | 'uploading' | 'success' | 'error'
  progress: number
  file: File
  fileId?: string
  error?: string
}>>([])

// 文件列表分页
const fileListCurrentPage = ref(1)
const fileListPageSize = ref(10)

// 表单引用
const folderInputRef = ref<HTMLInputElement>()
const submitting = ref(false)

// 导入表单数据
const importForm = reactive({
  knowledgeBaseId: null as number | null,
  directoryPath: './files',
  recursive: false,
  description: '',
  tags: ''
})

// 编辑表单数据
const editForm = reactive({
  title: '',
  description: '',
  tags: ''
})

// 表单验证规则
const uploadFormRules: FormRules = {
  knowledgeBaseId: [
    { required: true, message: '请选择知识库', trigger: 'change' }
  ],
  files: [
    { required: true, message: '请选择要上传的文件', trigger: 'change' }
  ]
}

const importFormRules: FormRules = {
  knowledgeBaseId: [
    { required: true, message: '请选择知识库', trigger: 'change' }
  ],
  directoryPath: [
    { required: true, message: '请输入导入目录路径', trigger: 'blur' }
  ]
}

const editFormRules: FormRules = {
  title: [
    { required: true, message: '请输入文档名称', trigger: 'blur' }
  ]
}

// 计算属性
const paginatedFileList = computed(() => {
  const start = (fileListCurrentPage.value - 1) * fileListPageSize.value
  const end = start + fileListPageSize.value
  return uploadFileList.value.slice(start, end)
})

const successCount = computed(() => 
  uploadFileList.value.filter(file => file.status === 'success').length
)

const errorCount = computed(() => 
  uploadFileList.value.filter(file => file.status === 'error').length
)

const hasWaitingFiles = computed(() => 
  uploadFileList.value.some(file => file.status === 'pending')
)

const canSubmit = computed(() => 
  uploadFileList.value.length > 0 && 
  uploadFileList.value.every(file => file.status === 'success' || file.status === 'error') &&
  uploadFileList.value.some(file => file.status === 'success') &&
  uploadForm.knowledgeBaseId
)

// 方法
const fetchDocuments = async () => {
  try {
    loading.value = true
    const params = {
      page: pagination.page,
      // page_size: pagination.pageSize, // 移除，因为不再提供每页大小选择
      search: searchQuery.value || undefined,
      kb_id: knowledgeBaseFilter.value || undefined,
      // Removed status and file_type from params as per UI change
      // status: statusFilter.value || undefined,
      // file_type: typeFilter.value || undefined
    }
    
    const response = await documentApi.getDocuments(params)
    // 确保 response 是一个数组，即使后端返回 null 或其他非数组类型
    documentList.value = Array.isArray(response) ? response : []
    // pagination.total = documentList.value.length // 暂时注释，等待后端返回total
    
    // 获取知识库信息
    await enrichDocumentsWithKnowledgeBase()
    
  } catch (error: any) {
    console.error('获取文档列表失败:', error)
    ElMessage.error('获取文档列表失败：' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const enrichDocumentsWithKnowledgeBase = async () => {
  // 为文档添加知识库信息
  for (const doc of documentList.value) {
    if (!doc.knowledge_base && doc.knowledge_base_id) {
      try {
        const kb = await knowledgeApi.getKnowledgeBase(doc.knowledge_base_id)
        doc.knowledge_base = {
          id: kb.id,
          name: kb.name,
          color: kb.color
        }
      } catch (error) {
        // 忽略错误，继续处理其他文档
      }
    }
  }
}

const fetchKnowledgeBases = async () => {
  try {
    const response = await knowledgeApi.getKnowledgeBases()
    const dataArray = Array.isArray(response) ? response : response.items || []
    
    knowledgeBaseOptions.value = dataArray.map(kb => ({
      label: kb.name,
      value: kb.id
    }))
  } catch (error: any) {
    console.error('获取知识库列表失败:', error)
    ElMessage.error('获取知识库列表失败：' + (error.message || '未知错误'))
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchDocuments()
}

// 移除 handleSizeChange 方法，因为不再支持页面大小调整
// const handleSizeChange = (val: number) => {
//   pagination.pageSize = val
//   pagination.page = 1
//   fetchDocuments()
// }

const handleCurrentChange = (val: number) => {
  pagination.page = val
  fetchDocuments()
}

const handleSelectionChange = (selection: DocumentType[]) => {
  selectedDocuments.value = selection
}

const refreshDocuments = () => {
  fetchDocuments()
}

const showUploadDialog = () => {
  dialogVisible.value = true
}

const showBatchImportDialog = () => {
  batchImportDialogVisible.value = true
}

// 新的文件处理方法
const handleFileChange = (file: UploadUserFile) => {
  if (!uploadForm.knowledgeBaseId) {
    ElMessage.warning('请先选择知识库')
    return
  }
  if (file.raw) {
    const fileExtension = getFileExtension(file.raw.name)
    if (!allowedFileTypes.includes(fileExtension)) {
      ElMessage.warning(`文件 ${file.raw.name} 的格式不被支持。支持的格式有：${allowedFileTypes.join(', ')}`)
      return
    }
    uploadFileList.value = []
    addFilesToList([file.raw])
  }
}

const handleFolderChange = (event: Event) => {
  if (!uploadForm.knowledgeBaseId) {
    ElMessage.warning('请先选择知识库')
    return
  }
  const target = event.target as HTMLInputElement
  if (target.files) {
    const files = Array.from(target.files)
    const validFiles = files.filter(file => {
      const fileExtension = getFileExtension(file.name)
      if (!allowedFileTypes.includes(fileExtension)) {
        ElMessage.warning(`文件 ${file.name} 的格式不被支持。支持的格式有：${allowedFileTypes.join(', ')}`)
        return false
      }
      return true
    })
    addFilesToList(validFiles)
  }
  target.value = ''
}

const selectFolder = () => {
  folderInputRef.value?.click()
}

const addFilesToList = (files: File[]) => {
  files.forEach(file => {
    // 检查文件是否已存在
    const exists = uploadFileList.value.some(f => f.name === file.name && f.size === file.size)
    if (!exists) {
      uploadFileList.value.push({
        id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
        name: file.name,
        size: file.size,
        status: 'pending',
        progress: 0,
        file: file
      })
    }
  })
  
  // 自动开始上传
  setTimeout(() => {
    startAllUploads()
  }, 100)
}

const removeFile = (index: number) => {
  uploadFileList.value.splice(index, 1)
}

const getActualIndex = (pageIndex: number) => {
  return (fileListCurrentPage.value - 1) * fileListPageSize.value + pageIndex
}

const clearAllFiles = () => {
  uploadFileList.value = []
  fileListCurrentPage.value = 1
}

const getFileExtension = (filename: string) => {
  return '.' + filename.split('.').pop()?.toLowerCase()
}

// 单个文件上传
const uploadSingleFile = async (fileItem: any) => {
  try {
    fileItem.status = 'uploading'
    fileItem.progress = 0
    
    const formData = new FormData()
    formData.append('file', fileItem.file)
    
    const xhr = new XMLHttpRequest()
    
    return new Promise((resolve, reject) => {
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          fileItem.progress = Math.round((e.loaded / e.total) * 100)
        }
      })
      
      xhr.addEventListener('load', () => {
        if (xhr.status === 200) {
          try {
            const response = JSON.parse(xhr.responseText)
            if (response.data && response.data.id) {
              fileItem.status = 'success'
              fileItem.progress = 100
              fileItem.fileId = response.data.id
              resolve(response.data)
            } else if (response.id) {
              fileItem.status = 'success'
              fileItem.progress = 100
              fileItem.fileId = response.id
              resolve(response)
            } else {
              fileItem.status = 'error'
              fileItem.error = '响应格式错误'
              reject(new Error('Invalid response format'))
            }
          } catch (e) {
            fileItem.status = 'error'
            fileItem.error = '响应解析失败'
            reject(e)
          }
        } else {
          fileItem.status = 'error'
          fileItem.error = `上传失败: ${xhr.status}`
          reject(new Error(`Upload failed: ${xhr.status}`))
        }
      })
      
      xhr.addEventListener('error', () => {
        fileItem.status = 'error'
        fileItem.error = '网络错误'
        reject(new Error('Network error'))
      })
      
      xhr.open('POST', '/api/documents/files/upload', true)
      
      const token = localStorage.getItem('token')
      if (token) {
        xhr.setRequestHeader('Authorization', `Bearer ${token}`)
      }
      
      xhr.send(formData)
    })
  } catch (error) {
    fileItem.status = 'error'
    fileItem.error = error instanceof Error ? error.message : '上传失败'
    throw error
  }
}

// 开始上传所有待上传文件
const startAllUploads = async () => {
  if (uploading.value) return
  
  const pendingFiles = uploadFileList.value.filter(file => file.status === 'pending')
  if (pendingFiles.length === 0) return
  
  uploading.value = true
  
  try {
    // 并发上传，但限制并发数
    const concurrency = 3
    for (let i = 0; i < pendingFiles.length; i += concurrency) {
      const batch = pendingFiles.slice(i, i + concurrency)
      await Promise.allSettled(batch.map(file => uploadSingleFile(file)))
    }
  } catch (error) {
    console.error('批量上传过程中出错:', error)
  } finally {
    uploading.value = false
  }
}

const submitUpload = async () => {
  if (!uploadFormRef.value) return
  
  const valid = await uploadFormRef.value.validate()
  if (!valid) return
  
  try {
    uploading.value = true
    
    if (uploadForm.files.length === 1) {
      // 单文件上传
      await documentApi.createDocument({
        kb_id: uploadForm.knowledgeBaseId!,
        title: uploadForm.files[0].name,
        description: uploadForm.description || undefined,
        tags: uploadForm.tags || undefined,
        file: uploadForm.files[0].raw!
      })
    } else {
      // 多文件上传
      await documentApi.batchUploadDocuments({
        kb_id: uploadForm.knowledgeBaseId!,
        description: uploadForm.description || undefined,
        tags: uploadForm.tags || undefined,
        files: uploadForm.files.map(f => f.raw!).filter(Boolean)
      })
    }
    
    ElMessage.success('文档上传成功')
    dialogVisible.value = false
    refreshDocuments()
  } catch (error: any) {
    console.error('文档上传失败:', error)
    ElMessage.error('文档上传失败：' + (error.message || '未知错误'))
  } finally {
    uploading.value = false
  }
}

const submitImport = async () => {
  if (!importFormRef.value) return
  
  const valid = await importFormRef.value.validate()
  if (!valid) return
  
  try {
    importing.value = true
    
    const result = await documentApi.importFromDirectory({
      kb_id: importForm.knowledgeBaseId!,
      directory_path: importForm.directoryPath,
      recursive: importForm.recursive,
      description: importForm.description || undefined,
      tags: importForm.tags || undefined
    })
    
    ElMessage.success(result.message)
    batchImportDialogVisible.value = false
    refreshDocuments()
  } catch (error: any) {
    console.error('批量导入失败:', error)
    ElMessage.error('批量导入失败：' + (error.message || '未知错误'))
  } finally {
    importing.value = false
  }
}

const submitBatchUpload = async () => {
  if (!uploadFormRef.value) return
  
  const valid = await uploadFormRef.value.validate()
  if (!valid) return
  
  submitting.value = true
  
  try {
    const batchData = uploadFileList.value
      .filter(f => f.status === 'success' && f.fileId)
      .map(f => ({
        file_id: f.fileId,
        title: f.name,
        description: uploadForm.description,
        tags: uploadForm.tags
      }))
    await documentApi.batchCreateDocuments(uploadForm.knowledgeBaseId, batchData)
    ElMessage.success('文档创建成功')
    dialogVisible.value = false
    resetUploadForm()
    refreshDocuments()
  } catch (error) {
    ElMessage.error('文档创建失败')
  } finally {
    submitting.value = false
  }
}

const editDocument = (document: DocumentType) => {
  currentDocument.value = document
  editForm.title = document.title
  editForm.description = document.doc_metadata?.description || ''
  editForm.tags = document.doc_metadata?.tags?.join(', ') || ''
  editDialogVisible.value = true
}

const submitEdit = async () => {
  if (!editFormRef.value || !currentDocument.value) return
  
  const valid = await editFormRef.value.validate()
  if (!valid) return
  
  try {
    editing.value = true
    
    await documentApi.updateDocument(currentDocument.value.id, {
      title: editForm.title,
      description: editForm.description || undefined,
      tags: editForm.tags || undefined
    })
    
    ElMessage.success('文档更新成功')
    editDialogVisible.value = false
    refreshDocuments()
  } catch (error: any) {
    console.error('文档更新失败:', error)
    ElMessage.error('文档更新失败：' + (error.message || '未知错误'))
  } finally {
    editing.value = false
  }
}

const deleteDocument = async (document: DocumentType) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除文档 "${document.title}" 吗？此操作不可撤销。`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await documentApi.deleteDocument(document.id)
    ElMessage.success('文档删除成功')
  refreshDocuments()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('文档删除失败:', error)
      ElMessage.error('文档删除失败：' + (error.message || '未知错误'))
    }
  }
}

const batchDeleteDocuments = async () => {
  if (selectedDocuments.value.length === 0) return
  
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedDocuments.value.length} 个文档吗？此操作不可撤销。`,
      '确认批量删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const ids = selectedDocuments.value.map(doc => doc.id)
    const result = await documentApi.batchDeleteDocuments(ids)
    
    ElMessage.success(result.message)
    selectedDocuments.value = []
    refreshDocuments()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败：' + (error.message || '未知错误'))
    }
  }
}

const previewDocument = (document: DocumentType) => {
  ElMessage.info('文档预览功能开发中')
}

const resetUploadForm = () => {
  uploadForm.knowledgeBaseId = null
  uploadForm.files = []
  uploadForm.description = ''
  uploadForm.tags = ''
  uploadFormRef.value?.resetFields()
}

const resetImportForm = () => {
  importForm.knowledgeBaseId = null
  importForm.directoryPath = './files'
  importForm.recursive = false
  importForm.description = ''
  importForm.tags = ''
  importFormRef.value?.resetFields()
}

const resetEditForm = () => {
  editForm.title = ''
  editForm.description = ''
  editForm.tags = ''
  currentDocument.value = null
  editFormRef.value?.resetFields()
}

// 工具函数
const getFileTypeIcon = (fileType: string | null | undefined) => {
  if (!fileType) return Document // 添加空值检查
  const iconMap: Record<string, any> = {
    '.pdf': Document,
    '.doc': DocumentCopy,
    '.docx': DocumentCopy,
    '.txt': Files,
    '.md': Notebook,
    '.ppt': DataBoard,
    '.pptx': DataBoard,
    '.xls': Grid,
    '.xlsx': Grid
  }
  return iconMap[fileType] || Document
}

const getFileTypeColor = (fileType: string) => {
  const colorMap: Record<string, string> = {
    '.pdf': '#f56565',
    '.doc': '#4299e1',
    '.docx': '#4299e1',
    '.txt': '#48bb78',
    '.md': '#ed8936',
    '.ppt': '#9f7aea',
    '.pptx': '#9f7aea',
    '.xls': '#38b2ac',
    '.xlsx': '#38b2ac'
  }
  return colorMap[fileType] || '#718096'
}

const getStatusType = (status: string | null | undefined) => {
  if (!status) return 'info' // 添加空值检查，默认为 info 类型
  const typeMap: Record<string, string> = {
    'completed': 'success',
    'processing': 'warning',
    'failed': 'danger',
    'pending': 'info'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    'completed': '已完成',
    'processing': '处理中',
    'failed': '失败',
    'pending': '待处理'
  }
  return textMap[status] || status
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 生命周期
onMounted(() => {
  fetchKnowledgeBases()
  fetchDocuments()
})
</script>

<style scoped>
.document-management {
  padding: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap; /* Allow items to wrap if space is limited */
}

.search-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap; /* Allow search bar items to wrap */
  gap: 10px; /* Add some space between items */
}

.actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap; /* Allow actions to wrap */
}

.filters {
  margin-bottom: 20px;
  /* display: none; */ /* Removed display: none; as the div will be empty anyway */
}

.document-name {
  display: flex;
  align-items: center;
  gap: 10px;
}

.file-icon {
  font-size: 24px;
}

.name-info {
  flex: 1;
}

.title {
  font-weight: 500;
  color: #303133;
}

.file-info {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end; /* 与知识库管理保持一致 */
}

.batch-actions {
  margin-top: 20px;
}

.upload-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>