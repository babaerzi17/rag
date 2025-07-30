<template>
  <el-card>
    <template #header>
      <span>分块管理 - 文档ID: {{ docId }}</span>
      <el-button type="primary" size="small" @click="openAddDialog" style="float:right;">新增分块</el-button>
    </template>
    <el-table :data="chunks" v-loading="loading" style="width: 100%" stripe>
      <el-table-column prop="chunk_index" label="序号" width="80" />
      <el-table-column prop="content" label="内容" />
      <el-table-column label="操作" width="180">
        <template #default="{ row }">
          <el-button size="small" @click="openEditDialog(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteChunk(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
      v-model:current-page="pagination.page"
      v-model:page-size="pagination.pageSize"
      :total="pagination.total"
      layout="total, sizes, prev, pager, next, jumper"
      :page-sizes="[10, 20, 50, 100]"
      @size-change="loadChunks"
      @current-change="loadChunks"
      style="margin-top: 16px; text-align: right;"
    />
    <!-- 编辑/新增弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogMode === 'edit' ? '编辑分块' : '新增分块'">
      <el-form :model="editForm" label-width="60px">
        <el-form-item label="内容">
          <el-input v-model="editForm.content" type="textarea" :rows="6" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveChunk">保存</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
// 假设有API: getChunks, updateChunk, deleteChunk, addChunk
import { getChunks, updateChunk, deleteChunk, addChunk } from '@/api/document'

const route = useRoute()
const router = useRouter()
const docId = Number(route.query.docId || route.params.docId)

const chunks = ref<any[]>([])
const loading = ref(false)
const pagination = reactive({ page: 1, pageSize: 20, total: 0 })

const dialogVisible = ref(false)
const dialogMode = ref<'edit'|'add'>('edit')
const editForm = reactive({ id: null, content: '' })

const loadChunks = async () => {
  loading.value = true
  try {
    const res = await getChunks(docId, { page: pagination.page, page_size: pagination.pageSize })
    chunks.value = res.items
    pagination.total = res.total
  } catch (e) {
    ElMessage.error('加载分块失败')
  } finally {
    loading.value = false
  }
}

const openEditDialog = (row: any) => {
  dialogMode.value = 'edit'
  editForm.id = row.id
  editForm.content = row.content
  dialogVisible.value = true
}
const openAddDialog = () => {
  dialogMode.value = 'add'
  editForm.id = null
  editForm.content = ''
  dialogVisible.value = true
}
const saveChunk = async () => {
  try {
    if (dialogMode.value === 'edit') {
      await updateChunk(docId, editForm.id, { content: editForm.content })
      ElMessage.success('分块已更新')
    } else {
      await addChunk(docId, { content: editForm.content })
      ElMessage.success('分块已新增')
    }
    dialogVisible.value = false
    loadChunks()
  } catch (e) {
    ElMessage.error('保存失败')
  }
}
const deleteChunk = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除该分块吗？', '提示', { type: 'warning' })
    await deleteChunk(docId, row.id)
    ElMessage.success('分块已删除')
    loadChunks()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}
onMounted(loadChunks)
</script> 