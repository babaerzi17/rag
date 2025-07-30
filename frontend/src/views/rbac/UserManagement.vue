<template>
  <div class="user-management">
    <!-- 页面标题 -->
    <!-- <div class="page-header">
      <h1>用户管理</h1>
      <p>管理系统用户信息、角色分配和权限控制</p>
    </div> -->

    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索用户名或邮箱"
          :prefix-icon="Search"
          @input="handleSearch"
          clearable
          style="width: 300px"
        />
      </div>
      <div class="actions">
        <el-button type="primary" :icon="Plus" @click="showCreateDialog" size="small">
          新增用户
        </el-button>
        <el-button :icon="Refresh" @click="refreshUserList" size="small">
          刷新
        </el-button>
      </div>
    </div>

    <!-- 用户表格 -->
    <el-card shadow="never">
      <el-table
        :data="userList"
        v-loading="loading"
        stripe
        style="width: 100%"
        max-height="calc(100vh - 310px)" # 调整最大高度以消除页面滚动条
        @sort-change="handleSortChange"
      >
        <el-table-column label="序号" width="80">
          <template #default="scope">
            {{ pagination.pageSize * (pagination.page - 1) + scope.$index + 1 }}
          </template>
        </el-table-column>
        <el-table-column prop="username" label="用户名" min-width="120" sortable />
        <el-table-column prop="email" label="邮箱" min-width="200" sortable />
        <el-table-column prop="full_name" label="姓名" min-width="120" />
        <el-table-column label="角色" min-width="150">
          <template #default="{ row }">
            <el-tag
              v-for="role in row.roles"
              :key="role"
              :type="role === 'admin' ? 'danger' : 'primary'"
              size="small"
              class="mr-1"
            >
              {{ role }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
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
              :icon="Key"
              @click="showPasswordDialog(row)"
            >
              重置
            </el-button>
            <el-button
              type="danger"
              size="small"
              :icon="Delete"
              @click="confirmDelete(row)"
              :disabled="row.username === 'admin'"
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

    <!-- 新增/编辑用户对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? '新增用户' : '编辑用户'"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="userFormRef"
        :model="userForm"
        :rules="userFormRules"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="userForm.username"
            :disabled="dialogMode === 'edit'"
            placeholder="请输入用户名"
          />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="姓名" prop="full_name">
          <el-input v-model="userForm.full_name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item
          v-if="dialogMode === 'create'"
          label="密码"
          prop="password"
        >
          <el-input
            v-model="userForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch
            v-model="userForm.is_active"
            active-text="启用"
            inactive-text="禁用"
          />
        </el-form-item>
        <el-form-item label="角色" prop="roles">
          <el-checkbox-group v-model="userForm.roles">
            <el-checkbox label="admin">管理员</el-checkbox>
            <el-checkbox label="user">普通用户</el-checkbox>
          </el-checkbox-group>
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

    <!-- 重置密码对话框 -->
    <el-dialog v-model="passwordDialogVisible" title="重置" width="400px">
      <el-form ref="passwordFormRef" :model="passwordForm" :rules="passwordRules">
        <el-form-item label="新密码" prop="new_password">
          <el-input
            v-model="passwordForm.new_password"
            type="password"
            placeholder="请输入新密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input
            v-model="passwordForm.confirm_password"
            type="password"
            placeholder="请再次输入新密码"
            show-password
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="passwordDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitPasswordReset" :loading="submitting">
            重置
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
import type { User, UserCreate, UserUpdate } from '@/types'
import { userApi } from '@/api/users'

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const userList = ref<User[]>([])
const searchQuery = ref('')
const dialogVisible = ref(false)
const passwordDialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const currentUser = ref<User | null>(null)

// 表单引用
const userFormRef = ref<FormInstance>()
const passwordFormRef = ref<FormInstance>()

// 分页数据
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 用户表单数据
const userForm = reactive({
  username: '',
  email: '',
  full_name: '',
  password: '',
  is_active: true,
  roles: [] as string[]
})

// 密码表单数据
const passwordForm = reactive({
  new_password: '',
  confirm_password: ''
})

// 表单验证规则
const userFormRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在 3 到 50 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6个字符', trigger: 'blur' }
  ]
}

const passwordRules: FormRules = {
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6个字符', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.new_password) {
          callback(new Error('两次输入密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 方法
const fetchUserList = async () => {
  try {
    loading.value = true
    const response = await userApi.getUsers(
      pagination.page,
      pagination.pageSize,
      searchQuery.value
    )
    userList.value = response.items
    pagination.total = response.total
  } catch (error: any) {
    ElMessage.error('获取用户列表失败：' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchUserList()
}

const handleSortChange = () => {
  fetchUserList()
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  pagination.page = 1
  fetchUserList()
}

const handleCurrentChange = (val: number) => {
  pagination.page = val
  fetchUserList()
}

const refreshUserList = () => {
  fetchUserList()
}

const showCreateDialog = () => {
  dialogMode.value = 'create'
  resetForm()
  dialogVisible.value = true
}

const showEditDialog = (user: User) => {
  console.log('触发编辑对话框，传入用户:', user); // 添加日志
  dialogMode.value = 'edit'
  currentUser.value = user
  
  // 填充表单数据
  userForm.username = user.username
  userForm.email = user.email
  userForm.full_name = user.full_name || ''
  userForm.is_active = user.is_active
  userForm.roles = [...(user.roles || [])] // 确保 user.roles 是一个数组
  
  dialogVisible.value = true
  console.log('dialogVisible设置为:', dialogVisible.value); // 添加日志
}

const showPasswordDialog = (user: User) => {
  currentUser.value = user
  passwordForm.new_password = ''
  passwordForm.confirm_password = ''
  passwordDialogVisible.value = true
}

const resetForm = () => {
  userForm.username = ''
  userForm.email = ''
  userForm.full_name = ''
  userForm.password = ''
  userForm.is_active = true
  userForm.roles = []
  currentUser.value = null
  userFormRef.value?.resetFields()
}

const submitForm = async () => {
  if (!userFormRef.value) return
  
  try {
    await userFormRef.value.validate()
    submitting.value = true
    
    if (dialogMode.value === 'create') {
      const userData: UserCreate = {
        username: userForm.username,
        email: userForm.email,
        password: userForm.password,
        full_name: userForm.full_name || undefined
      }
      await userApi.createUser(userData)
      
      // 如果有角色需要分配，创建用户后再更新角色
      if (userForm.roles.length > 0) {
        const newUserResponse = await userApi.getUsers(1, 1, userForm.username)
        if (newUserResponse.items.length > 0) {
          await userApi.updateUserRoles(newUserResponse.items[0].id, userForm.roles)
        }
      }
      
      ElMessage.success('用户创建成功')
    } else {
      const userData: UserUpdate = {
        email: userForm.email,
        full_name: userForm.full_name || undefined,
        is_active: userForm.is_active
      }
      await userApi.updateUser(currentUser.value!.id, userData)
      
      // 更新角色
      await userApi.updateUserRoles(currentUser.value!.id, userForm.roles)
      
      ElMessage.success('用户更新成功')
    }
    
    dialogVisible.value = false
    fetchUserList()
  } catch (error: any) {
    ElMessage.error('操作失败：' + (error.message || '未知错误'))
  } finally {
    submitting.value = false
  }
}

const submitPasswordReset = async () => {
  if (!passwordFormRef.value || !currentUser.value) return
  
  try {
    await passwordFormRef.value.validate()
    submitting.value = true
    
    await userApi.resetUserPassword(currentUser.value.id, passwordForm.new_password)
    
    ElMessage.success('密码重置成功')
    passwordDialogVisible.value = false
  } catch (error: any) {
    ElMessage.error('密码重置失败：' + (error.message || '未知错误'))
  } finally {
    submitting.value = false
  }
}

const confirmDelete = (user: User) => {
  if (user.username === 'admin') {
    ElMessage.warning('系统管理员账户不允许删除。')
    return
  }

  ElMessageBox.confirm(
    `确定要删除用户 "${user.username}" 吗？此操作不可恢复。`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await userApi.deleteUser(user.id)
      ElMessage.success('用户删除成功')
      fetchUserList()
    } catch (error: any) {
      ElMessage.error('删除失败：' + (error.message || '未知错误'))
    }
  })
}

// 生命周期
onMounted(() => {
  fetchUserList()
})
</script>

<style scoped>
.user-management {
  padding: 20px;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden; /* 防止组件自身出现滚动条 */
}

.page-header {
  margin-bottom: 20px;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.page-header p {
  color: #606266;
  font-size: 14px;
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

.mr-1 {
  margin-right: 4px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>