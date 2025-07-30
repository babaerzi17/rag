<template>
  <div class="role-management">
    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索角色名称或描述"
          :prefix-icon="Search"
          @input="handleSearch"
          clearable
          style="width: 300px"
        />
      </div>
      <div class="actions">
        <el-button type="primary" :icon="Plus" @click="showCreateDialog" size="small">
          新增角色
        </el-button>
        <el-button :icon="Refresh" @click="refreshRoleList" size="small">
          刷新
        </el-button>
      </div>
    </div>

    <!-- 角色表格 -->
    <el-card shadow="never">
      <el-table
        :data="roleList"
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
        <el-table-column prop="name" label="角色名称" min-width="150" sortable />
        <el-table-column prop="description" label="角色描述" min-width="200" />
        <el-table-column label="权限数量" width="100">
          <template #default="{ row }">
            <el-tag type="info" size="small">{{ row.permissions?.length || 0 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="用户数量" width="100">
          <template #default="{ row }">
            <el-tag type="success" size="small">{{ row.userCount || 0 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
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
              :icon="Key"
              @click="showPermissionDialog(row)"
            >
              权限
            </el-button>
            <el-button
              type="danger"
              size="small"
              :icon="Delete"
              @click="confirmDelete(row)"
              :disabled="row.name === 'admin'"
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

    <!-- 新增/编辑角色对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? '新增角色' : '编辑角色'"
      width="500px"
      @close="resetForm"
    >
      <el-form
        ref="roleFormRef"
        :model="roleForm"
        :rules="roleFormRules"
        label-width="100px"
      >
        <el-form-item label="角色名称" prop="name">
          <el-input
            v-model="roleForm.name"
            placeholder="请输入角色名称"
          />
        </el-form-item>
        <el-form-item label="角色描述" prop="description">
          <el-input
            v-model="roleForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入角色描述"
          />
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

    <!-- 角色权限管理对话框 -->
    <el-dialog
      v-model="permissionDialogVisible"
      title="角色权限管理"
      width="700px"
      @close="resetPermissionForm"
    >
      <div v-if="currentRole" class="permission-content">
        <div class="role-info">
          <p class="mb-4">
            正在为角色 "<strong class="role-name">{{ currentRole.name }}</strong>" 分配权限
          </p>
          <p class="permission-summary">
            已选择 <strong>{{ selectedPermissions.length }}</strong> 项权限，
            共 <strong>{{ allPermissions.length }}</strong> 项可用权限
          </p>
        </div>
        
        <el-divider />
        
        <div class="permission-list">
          <el-checkbox-group v-model="selectedPermissions">
            <div v-for="permission in allPermissions" :key="permission.id" class="permission-item">
              <el-checkbox :value="permission.name">
                <div class="permission-info">
                  <div class="permission-header">
                    <span class="permission-icon">{{ permission.menu_icon || '📄' }}</span>
                    <strong class="menu-name">{{ permission.menu_name }}</strong>
                    <el-tag size="small" type="info" class="permission-tag">{{ permission.name }}</el-tag>
                  </div>
                  <div v-if="permission.menu_path" class="permission-path">
                    路径: {{ permission.menu_path }}
                  </div>
                </div>
              </el-checkbox>
            </div>
          </el-checkbox-group>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="permissionDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="updateRolePermissions" :loading="submitting">
            保存权限 ({{ selectedPermissions.length }})
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
  Key
} from '@element-plus/icons-vue'
import type { Role, RoleCreate, RoleUpdate, Permission } from '@/types'
import { roleApi } from '@/api/roles'
import { permissionApi } from '@/api/permissions'

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const roleList = ref<Role[]>([])
const allPermissions = ref<Permission[]>([])
const searchQuery = ref('')
const dialogVisible = ref(false)
const permissionDialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const currentRole = ref<Role | null>(null)
const selectedPermissions = ref<string[]>([])

// 表单引用
const roleFormRef = ref<FormInstance>()

// 分页数据
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 角色表单数据
const roleForm = reactive({
  name: '',
  description: ''
})

// 表单验证规则
const roleFormRules: FormRules = {
  name: [
    { required: true, message: '请输入角色名称', trigger: 'blur' },
    { min: 2, max: 50, message: '角色名称长度在 2 到 50 个字符', trigger: 'blur' }
  ]
}

// 方法
const fetchRoleList = async () => {
  try {
    loading.value = true
    const response = await roleApi.getRoles(
      pagination.page,
      pagination.pageSize,
      searchQuery.value
    )
    roleList.value = response.items
    pagination.total = response.total
  } catch (error: any) {
    ElMessage.error('获取角色列表失败：' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const fetchAllPermissions = async () => {
  try {
    const response = await permissionApi.getPermissions(1, 1000) // 获取所有权限
    allPermissions.value = response.items
  } catch (error: any) {
    ElMessage.error('获取权限列表失败：' + (error.message || '未知错误'))
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchRoleList()
}

const handleSortChange = () => {
  fetchRoleList()
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  pagination.page = 1
  fetchRoleList()
}

const handleCurrentChange = (val: number) => {
  pagination.page = val
  fetchRoleList()
}

const refreshRoleList = () => {
  fetchRoleList()
}

const showCreateDialog = () => {
  dialogMode.value = 'create'
  resetForm()
  dialogVisible.value = true
}

const showEditDialog = (role: Role) => {
  dialogMode.value = 'edit'
  currentRole.value = role
  
  // 填充表单数据
  roleForm.name = role.name
  roleForm.description = role.description || ''
  
  dialogVisible.value = true
}

const showPermissionDialog = async (role: Role) => {
  try {
    currentRole.value = role
    
    // 首先获取完整的角色信息（包含权限）
    const fullRole = await roleApi.getRoleById(role.id)
    currentRole.value = fullRole
    
    // 获取角色当前权限
    selectedPermissions.value = fullRole.permissions?.map(p => p.name) || []
    
    console.log('当前角色:', fullRole.name)
    console.log('当前角色权限:', selectedPermissions.value)
    console.log('所有可用权限:', allPermissions.value.map(p => p.name))
    
    permissionDialogVisible.value = true
  } catch (error: any) {
    ElMessage.error('获取角色权限失败：' + (error.message || '未知错误'))
  }
}

const resetForm = () => {
  roleForm.name = ''
  roleForm.description = ''
  currentRole.value = null
  roleFormRef.value?.resetFields()
}

const resetPermissionForm = () => {
  selectedPermissions.value = []
  currentRole.value = null
}

const submitForm = async () => {
  if (!roleFormRef.value) return
  
  try {
    await roleFormRef.value.validate()
    submitting.value = true
    
    if (dialogMode.value === 'create') {
      const roleData: RoleCreate = {
        name: roleForm.name,
        description: roleForm.description
      }
      await roleApi.createRole(roleData)
      ElMessage.success('角色创建成功')
    } else {
      const roleData: RoleUpdate = {
        name: roleForm.name,
        description: roleForm.description
      }
      await roleApi.updateRole(currentRole.value!.id, roleData)
      ElMessage.success('角色更新成功')
    }
    
    dialogVisible.value = false
    fetchRoleList()
  } catch (error: any) {
    ElMessage.error('操作失败：' + (error.message || '未知错误'))
  } finally {
    submitting.value = false
  }
}

const updateRolePermissions = async () => {
  if (!currentRole.value) return
  
  try {
    submitting.value = true
    await roleApi.updateRolePermissions(currentRole.value.id, selectedPermissions.value)
    ElMessage.success('角色权限更新成功')
    permissionDialogVisible.value = false
    fetchRoleList()
  } catch (error: any) {
    ElMessage.error('更新权限失败：' + (error.message || '未知错误'))
  } finally {
    submitting.value = false
  }
}

const confirmDelete = (role: Role) => {
  if (role.name === 'admin') {
    ElMessage.warning('系统管理员角色不允许删除')
    return
  }
  
  ElMessageBox.confirm(
    `确定要删除角色 "${role.name}" 吗？此操作不可恢复。`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await roleApi.deleteRole(role.id)
      ElMessage.success('角色删除成功')
      fetchRoleList()
    } catch (error: any) {
      ElMessage.error('删除失败：' + (error.message || '未知错误'))
    }
  })
}

// 生命周期
onMounted(() => {
  fetchRoleList()
  fetchAllPermissions()
})
</script>

<style scoped>
.role-management {
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

.permission-content .mb-4 {
  margin-bottom: 16px;
}

.role-info {
  background: var(--el-bg-color-page);
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.role-name {
  color: var(--el-color-primary);
}

.permission-summary {
  margin: 8px 0;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.permission-list {
  max-height: 400px;
  overflow-y: auto;
}

.permission-item {
  margin-bottom: 16px;
  padding: 12px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  transition: all 0.3s;
}

.permission-item:hover {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}

.permission-info {
  margin-left: 8px;
}

.permission-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.permission-icon {
  font-size: 16px;
  width: 20px;
  text-align: center;
}

.menu-name {
  color: var(--el-text-color-primary);
  font-size: 14px;
}

.permission-tag {
  margin-left: auto;
}

.permission-path {
  color: var(--el-text-color-secondary);
  font-size: 12px;
  margin-top: 4px;
}

.permission-label {
  display: inline-block;
}
</style>