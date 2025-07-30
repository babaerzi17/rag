<template>
  <div class="permission-management">
    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索权限标识或菜单名称"
          :prefix-icon="Search"
          @input="handleSearch"
          clearable
          style="width: 300px"
        />
      </div>
      <div class="actions">
        <el-button type="primary" :icon="Plus" @click="showCreateDialog" size="small">
          新增权限
        </el-button>
        <el-button :icon="Refresh" @click="refreshPermissionList" size="small">
          刷新
        </el-button>
      </div>
    </div>

    <!-- 权限表格 -->
    <el-card shadow="never" class="permission-table-card">
      <el-table
        :data="permissionList"
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
        <el-table-column prop="name" label="权限标识" min-width="150" sortable />
        <el-table-column prop="menu_name" label="菜单名称" min-width="150" sortable />
        <el-table-column prop="menu_path" label="菜单路径" min-width="150" />
        <el-table-column prop="menu_icon" label="图标" width="80">
          <template #default="{ row }">
            <span v-if="row.menu_icon">{{ row.menu_icon }}</span>
            <span v-else class="text-placeholder">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="sort_order" label="排序" width="80" />
        <el-table-column label="关联角色" min-width="150">
          <template #default="{ row }">
            <el-tag
              v-for="role in row.roles"
              :key="role.id"
              type="info"
              size="small"
              class="mr-1"
            >
              {{ role.name }}
            </el-tag>
            <span v-if="!row.roles || row.roles.length === 0" class="text-placeholder">无</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
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

    <!-- 新增/编辑权限对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? '新增权限' : '编辑权限'"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="permissionFormRef"
        :model="permissionForm"
        :rules="permissionFormRules"
        label-width="120px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="权限标识" prop="name">
              <el-input
                v-model="permissionForm.name"
                placeholder="如: menu:user_management"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="菜单名称" prop="menu_name">
              <el-input
                v-model="permissionForm.menu_name"
                placeholder="如: 用户管理"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="菜单路径" prop="menu_path">
              <el-input
                v-model="permissionForm.menu_path"
                placeholder="如: /rbac/users"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="菜单图标" prop="menu_icon">
              <el-input
                v-model="permissionForm.menu_icon"
                placeholder="如: 👥"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="父菜单ID" prop="parent_id">
              <el-input-number
                v-model="permissionForm.parent_id"
                :min="0"
                placeholder="0表示顶级菜单"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="排序" prop="sort_order">
              <el-input-number
                v-model="permissionForm.sort_order"
                :min="0"
                placeholder="排序值，越小越靠前"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <!-- <el-form-item label="权限描述" prop="description">
          <el-input
            v-model="permissionForm.description"
            type="textarea"
            :rows="3"
            placeholder="权限功能描述"
          />
        </el-form-item> -->
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
  Delete
} from '@element-plus/icons-vue'
import type { Permission, PermissionCreate } from '@/types'
import { permissionApi } from '@/api/permissions'

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const permissionList = ref<Permission[]>([])
const searchQuery = ref('')
const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const currentPermission = ref<Permission | null>(null)

// 表单引用
const permissionFormRef = ref<FormInstance>()

// 分页数据
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 权限表单数据
const permissionForm = reactive({
  name: '',
  menu_name: '',
  description: '',
  menu_path: '',
  menu_icon: '',
  parent_id: 0,
  sort_order: 0
})

// 表单验证规则
const permissionFormRules: FormRules = {
  name: [
    { required: true, message: '请输入权限标识', trigger: 'blur' },
    { min: 2, max: 100, message: '权限标识长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  menu_name: [
    { required: true, message: '请输入菜单名称', trigger: 'blur' },
    { min: 2, max: 50, message: '菜单名称长度在 2 到 50 个字符', trigger: 'blur' }
  ]
}

// 方法
const fetchPermissionList = async () => {
  try {
    loading.value = true
    const response = await permissionApi.getPermissions(
      pagination.page,
      pagination.pageSize,
      searchQuery.value
    )
    permissionList.value = response.items
    pagination.total = response.total
  } catch (error: any) {
    ElMessage.error('获取权限列表失败：' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchPermissionList()
}

const handleSortChange = () => {
  fetchPermissionList()
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  pagination.page = 1
  fetchPermissionList()
}

const handleCurrentChange = (val: number) => {
  pagination.page = val
  fetchPermissionList()
}

const refreshPermissionList = () => {
  fetchPermissionList()
}

const showCreateDialog = () => {
  dialogMode.value = 'create'
  resetForm()
  dialogVisible.value = true
}

const showEditDialog = (permission: Permission) => {
  console.log('触发编辑权限对话框，传入权限:', permission)
  dialogMode.value = 'edit'
  currentPermission.value = permission
  
  // 填充表单数据
  permissionForm.name = permission.name
  permissionForm.menu_name = permission.menu_name
  permissionForm.description = permission.description || ''
  permissionForm.menu_path = permission.menu_path || ''
  permissionForm.menu_icon = permission.menu_icon || ''
  permissionForm.parent_id = permission.parent_id || 0
  permissionForm.sort_order = permission.sort_order || 0
  
  dialogVisible.value = true
  console.log('dialogVisible设置为:', dialogVisible.value)
}

const resetForm = () => {
  permissionForm.name = ''
  permissionForm.menu_name = ''
  permissionForm.description = ''
  permissionForm.menu_path = ''
  permissionForm.menu_icon = ''
  permissionForm.parent_id = 0
  permissionForm.sort_order = 0
  currentPermission.value = null
  permissionFormRef.value?.resetFields()
}

const submitForm = async () => {
  if (!permissionFormRef.value) return
  
  try {
    await permissionFormRef.value.validate()
    submitting.value = true
    
    if (dialogMode.value === 'create') {
      const permissionData: PermissionCreate = {
        name: permissionForm.name,
        menu_name: permissionForm.menu_name,
        description: permissionForm.description,
        menu_path: permissionForm.menu_path,
        menu_icon: permissionForm.menu_icon,
        parent_id: permissionForm.parent_id,
        sort_order: permissionForm.sort_order
      }
      await permissionApi.createPermission(permissionData)
      ElMessage.success('权限创建成功')
    } else {
      const permissionData: PermissionCreate = {
        name: permissionForm.name,
        menu_name: permissionForm.menu_name,
        description: permissionForm.description,
        menu_path: permissionForm.menu_path,
        menu_icon: permissionForm.menu_icon,
        parent_id: permissionForm.parent_id,
        sort_order: permissionForm.sort_order
      }
      await permissionApi.updatePermission(currentPermission.value!.id, permissionData)
      ElMessage.success('权限更新成功')
    }
    
    dialogVisible.value = false
    fetchPermissionList()
  } catch (error: any) {
    ElMessage.error('操作失败：' + (error.message || '未知错误'))
  } finally {
    submitting.value = false
  }
}

const confirmDelete = (permission: Permission) => {
  ElMessageBox.confirm(
    `确定要删除权限 "${permission.menu_name}" 吗？此操作不可恢复。`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await permissionApi.deletePermission(permission.id)
      ElMessage.success('权限删除成功')
      fetchPermissionList()
    } catch (error: any) {
      ElMessage.error('删除失败：' + (error.message || '未知错误'))
    }
  })
}

// 生命周期
onMounted(() => {
  fetchPermissionList()
})
</script>

<style scoped>
.permission-management {
  padding: 20px;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.actions {
  display: flex;
  gap: 12px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.text-placeholder {
  color: var(--el-text-color-placeholder);
  font-style: italic;
}

.mr-1 {
  margin-right: 8px;
}

.permission-table-card {
  flex: 1; /* Make card take available height */
  overflow: hidden; /* Hide card's own scrollbar if content overflows */
}

.permission-table-card .el-card__body {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow-x: auto; /* Enable horizontal scrollbar for table content */
}

.el-table {
  /* Remove fixed width if present, allow content to dictate width */
  min-width: 100%; /* Ensure table is at least 100% of parent, and can grow */
}
</style>