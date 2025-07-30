<template>
  <div class="ab-test-management">
    <el-card class="header-card">
      <div class="header-content">
        <div class="title-section">
          <h2>AB测试管理</h2>
          <p class="subtitle">创建和管理AB测试，对比不同配置的性能表现</p>
        </div>
        <div class="action-section">
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            创建测试
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 测试列表 -->
    <el-card class="test-list-card">
      <template #header>
        <div class="card-header">
          <span>测试列表</span>
          <div class="header-actions">
            <el-select v-model="statusFilter" placeholder="状态筛选" clearable @change="loadTests">
              <el-option label="全部" value="" />
              <el-option label="草稿" value="draft" />
              <el-option label="进行中" value="active" />
              <el-option label="暂停" value="paused" />
              <el-option label="已完成" value="completed" />
              <el-option label="已分析" value="analyzed" />
            </el-select>
            <el-button @click="loadTests">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="tests" v-loading="loading" stripe>
        <el-table-column prop="name" label="测试名称" min-width="200">
          <template #default="{ row }">
            <div class="test-name">
              <span class="name">{{ row.name }}</span>
              <el-tag :type="getStatusType(row.status)" size="small">
                {{ getStatusText(row.status) }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="test_type" label="测试类型" width="150">
          <template #default="{ row }">
            <el-tag type="info" size="small">{{ getTestTypeText(row.test_type) }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="traffic_split" label="流量分配" width="120">
          <template #default="{ row }">
            <span>{{ (row.traffic_split * 100).toFixed(0) }}% / {{ ((1 - row.traffic_split) * 100).toFixed(0) }}%</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button-group>
              <el-button size="small" @click="viewTest(row)">查看</el-button>
              <el-button 
                size="small" 
                type="primary" 
                v-if="row.status === 'draft'"
                @click="startTest(row)"
              >
                启动
              </el-button>
              <el-button 
                size="small" 
                type="warning" 
                v-if="row.status === 'active'"
                @click="pauseTest(row)"
              >
                暂停
              </el-button>
              <el-button 
                size="small" 
                type="success" 
                v-if="['active', 'paused'].includes(row.status)"
                @click="completeTest(row)"
              >
                完成
              </el-button>
              <el-button 
                size="small" 
                type="danger" 
                @click="deleteTest(row)"
              >
                删除
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建测试对话框 -->
    <el-dialog 
      v-model="showCreateDialog" 
      title="创建AB测试" 
      width="800px"
      :close-on-click-modal="false"
    >
      <el-form 
        ref="createFormRef" 
        :model="createForm" 
        :rules="createRules" 
        label-width="120px"
      >
        <el-form-item label="测试名称" prop="name">
          <el-input v-model="createForm.name" placeholder="请输入测试名称" />
        </el-form-item>
        
        <el-form-item label="测试描述" prop="description">
          <el-input 
            v-model="createForm.description" 
            type="textarea" 
            :rows="3"
            placeholder="请输入测试描述"
          />
        </el-form-item>
        
        <el-form-item label="测试类型" prop="test_type">
          <el-select v-model="createForm.test_type" placeholder="请选择测试类型" @change="onTestTypeChange">
            <el-option label="模型对比" value="model_comparison" />
            <el-option label="检索方法对比" value="retrieval_method" />
            <el-option label="分块大小对比" value="chunk_size" />
            <el-option label="上下文窗口对比" value="context_window" />
            <el-option label="RAG vs 基线" value="rag_vs_baseline" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="流量分配" prop="traffic_split">
          <el-slider 
            v-model="createForm.traffic_split" 
            :min="0.1" 
            :max="0.9" 
            :step="0.1"
            show-input
            :format-tooltip="(val) => `${(val * 100).toFixed(0)}%`"
          />
        </el-form-item>
        
        <el-form-item label="样本大小" prop="sample_size">
          <el-input-number 
            v-model="createForm.sample_size" 
            :min="10" 
            :max="10000"
            placeholder="可选，留空表示无限制"
          />
        </el-form-item>
        
        <el-form-item label="持续天数" prop="duration_days">
          <el-input-number 
            v-model="createForm.duration_days" 
            :min="1" 
            :max="365"
            placeholder="可选，留空表示无限制"
          />
        </el-form-item>
        
        <!-- 配置模板选择 -->
        <el-form-item label="配置模板">
          <el-select v-model="selectedTemplate" placeholder="选择配置模板" @change="applyTemplate">
            <el-option 
              v-for="template in configTemplates" 
              :key="template.name"
              :label="template.name"
              :value="template"
            />
          </el-select>
        </el-form-item>
        
        <!-- A组配置 -->
        <el-divider content-position="left">A组配置</el-divider>
        <el-form-item label="A组配置" prop="group_a_config">
          <el-input 
            v-model="groupAConfigText" 
            type="textarea" 
            :rows="6"
            placeholder="请输入A组配置（JSON格式）"
            @input="updateGroupAConfig"
          />
        </el-form-item>
        
        <!-- B组配置 -->
        <el-divider content-position="left">B组配置</el-divider>
        <el-form-item label="B组配置" prop="group_b_config">
          <el-input 
            v-model="groupBConfigText" 
            type="textarea" 
            :rows="6"
            placeholder="请输入B组配置（JSON格式）"
            @input="updateGroupBConfig"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createTest" :loading="creating">
          创建测试
        </el-button>
      </template>
    </el-dialog>

    <!-- 测试详情对话框 -->
    <el-dialog 
      v-model="showDetailDialog" 
      title="测试详情" 
      width="1000px"
      :close-on-click-modal="false"
    >
      <div v-if="selectedTest" class="test-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="测试名称">{{ selectedTest.name }}</el-descriptions-item>
          <el-descriptions-item label="测试类型">{{ getTestTypeText(selectedTest.test_type) }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(selectedTest.status)">
              {{ getStatusText(selectedTest.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="流量分配">
            {{ (selectedTest.traffic_split * 100).toFixed(0) }}% / {{ ((1 - selectedTest.traffic_split) * 100).toFixed(0) }}%
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(selectedTest.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="开始时间" v-if="selectedTest.started_at">
            {{ formatDate(selectedTest.started_at) }}
          </el-descriptions-item>
        </el-descriptions>
        
        <el-divider content-position="left">配置详情</el-divider>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <h4>A组配置</h4>
            <pre class="config-json">{{ JSON.stringify(selectedTest.group_a_config, null, 2) }}</pre>
          </el-col>
          <el-col :span="12">
            <h4>B组配置</h4>
            <pre class="config-json">{{ JSON.stringify(selectedTest.group_b_config, null, 2) }}</pre>
          </el-col>
        </el-row>
        
        <el-divider content-position="left">测试摘要</el-divider>
        
        <div v-if="testSummary" class="test-summary">
          <el-row :gutter="20">
            <el-col :span="6">
              <el-statistic title="总会话数" :value="testSummary.total_sessions" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="总交互数" :value="testSummary.total_interactions" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="成功率" :value="(testSummary.success_rate * 100).toFixed(1)" suffix="%" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="平均响应时间" :value="testSummary.avg_response_time_ms" suffix="ms" />
            </el-col>
          </el-row>
          
          <el-row :gutter="20" style="margin-top: 20px;">
            <el-col :span="12">
              <h4>A组统计</h4>
              <p>会话数: {{ testSummary.group_a_sessions }}</p>
            </el-col>
            <el-col :span="12">
              <h4>B组统计</h4>
              <p>会话数: {{ testSummary.group_b_sessions }}</p>
            </el-col>
          </el-row>
        </div>
        
        <div class="detail-actions">
          <el-button @click="calculateMetrics" :loading="calculating">
            计算指标
          </el-button>
          <el-button @click="viewMetrics" v-if="hasMetrics">
            查看指标
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { abTestingApi, type ABTest, type ABTestCreate, type ABTestSummary, type TestConfigTemplate } from '@/api/ab-testing'

// 响应式数据
const loading = ref(false)
const creating = ref(false)
const calculating = ref(false)
const tests = ref<ABTest[]>([])
const statusFilter = ref('')
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const selectedTest = ref<ABTest | null>(null)
const testSummary = ref<ABTestSummary | null>(null)
const hasMetrics = ref(false)
const configTemplates = ref<TestConfigTemplate[]>([])
const selectedTemplate = ref<TestConfigTemplate | null>(null)

// 创建表单
const createFormRef = ref()
const createForm = reactive<ABTestCreate>({
  name: '',
  description: '',
  test_type: 'model_comparison',
  traffic_split: 0.5,
  sample_size: undefined,
  duration_days: undefined,
  group_a_config: {},
  group_b_config: {},
  config: {}
})

const groupAConfigText = ref('{}')
const groupBConfigText = ref('{}')

// 表单验证规则
const createRules = {
  name: [
    { required: true, message: '请输入测试名称', trigger: 'blur' }
  ],
  test_type: [
    { required: true, message: '请选择测试类型', trigger: 'change' }
  ],
  group_a_config: [
    { required: true, message: '请输入A组配置', trigger: 'blur' }
  ],
  group_b_config: [
    { required: true, message: '请输入B组配置', trigger: 'blur' }
  ]
}

// 生命周期
onMounted(() => {
  loadTests()
  loadConfigTemplates()
})

// 方法
const loadTests = async () => {
  loading.value = true
  try {
    const params: any = {}
    if (statusFilter.value) {
      params.status_filter = statusFilter.value
    }
    tests.value = await abTestingApi.getTests(params)
  } catch (error) {
    ElMessage.error('加载测试列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const loadConfigTemplates = async () => {
  try {
    configTemplates.value = await abTestingApi.getConfigTemplates()
  } catch (error) {
    console.error('加载配置模板失败:', error)
  }
}

const createTest = async () => {
  if (!createFormRef.value) return
  
  try {
    await createFormRef.value.validate()
    creating.value = true
    
    // 解析JSON配置
    try {
      createForm.group_a_config = JSON.parse(groupAConfigText.value)
      createForm.group_b_config = JSON.parse(groupBConfigText.value)
    } catch (error) {
      ElMessage.error('配置格式错误，请检查JSON格式')
      return
    }
    
    await abTestingApi.createTest(createForm)
    ElMessage.success('测试创建成功')
    showCreateDialog.value = false
    loadTests()
    
    // 重置表单
    Object.assign(createForm, {
      name: '',
      description: '',
      test_type: 'model_comparison',
      traffic_split: 0.5,
      sample_size: undefined,
      duration_days: undefined,
      group_a_config: {},
      group_b_config: {},
      config: {}
    })
    groupAConfigText.value = '{}'
    groupBConfigText.value = '{}'
  } catch (error) {
    ElMessage.error('创建测试失败')
    console.error(error)
  } finally {
    creating.value = false
  }
}

const startTest = async (test: ABTest) => {
  try {
    await ElMessageBox.confirm('确定要启动这个测试吗？', '确认启动', {
      type: 'warning'
    })
    
    await abTestingApi.startTest(test.id)
    ElMessage.success('测试启动成功')
    loadTests()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('启动测试失败')
      console.error(error)
    }
  }
}

const pauseTest = async (test: ABTest) => {
  try {
    await ElMessageBox.confirm('确定要暂停这个测试吗？', '确认暂停', {
      type: 'warning'
    })
    
    await abTestingApi.pauseTest(test.id)
    ElMessage.success('测试暂停成功')
    loadTests()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('暂停测试失败')
      console.error(error)
    }
  }
}

const completeTest = async (test: ABTest) => {
  try {
    await ElMessageBox.confirm('确定要完成这个测试吗？', '确认完成', {
      type: 'warning'
    })
    
    await abTestingApi.completeTest(test.id)
    ElMessage.success('测试完成成功')
    loadTests()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('完成测试失败')
      console.error(error)
    }
  }
}

const deleteTest = async (test: ABTest) => {
  try {
    await ElMessageBox.confirm('确定要删除这个测试吗？此操作不可恢复！', '确认删除', {
      type: 'error'
    })
    
    await abTestingApi.deleteTest(test.id)
    ElMessage.success('测试删除成功')
    loadTests()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除测试失败')
      console.error(error)
    }
  }
}

const viewTest = async (test: ABTest) => {
  selectedTest.value = test
  showDetailDialog.value = true
  
  try {
    testSummary.value = await abTestingApi.getTestSummary(test.id)
  } catch (error) {
    console.error('加载测试摘要失败:', error)
  }
}

const calculateMetrics = async () => {
  if (!selectedTest.value) return
  
  calculating.value = true
  try {
    await abTestingApi.calculateMetrics(selectedTest.value.id)
    ElMessage.success('指标计算完成')
    hasMetrics.value = true
  } catch (error) {
    ElMessage.error('指标计算失败')
    console.error(error)
  } finally {
    calculating.value = false
  }
}

const viewMetrics = () => {
  // 这里可以跳转到指标详情页面
  ElMessage.info('功能开发中...')
}

const onTestTypeChange = () => {
  // 根据测试类型设置默认配置
  selectedTemplate.value = null
  groupAConfigText.value = '{}'
  groupBConfigText.value = '{}'
}

const applyTemplate = (template: TestConfigTemplate) => {
  if (!template) return
  
  createForm.test_type = template.test_type as any
  createForm.group_a_config = template.group_a_config
  createForm.group_b_config = template.group_b_config
  createForm.config = template.config
  
  groupAConfigText.value = JSON.stringify(template.group_a_config, null, 2)
  groupBConfigText.value = JSON.stringify(template.group_b_config, null, 2)
}

const updateGroupAConfig = () => {
  try {
    createForm.group_a_config = JSON.parse(groupAConfigText.value)
  } catch (error) {
    // JSON解析错误时不更新
  }
}

const updateGroupBConfig = () => {
  try {
    createForm.group_b_config = JSON.parse(groupBConfigText.value)
  } catch (error) {
    // JSON解析错误时不更新
  }
}

// 工具方法
const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    draft: '',
    active: 'success',
    paused: 'warning',
    completed: 'info',
    analyzed: 'primary'
  }
  return statusMap[status] || ''
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    draft: '草稿',
    active: '进行中',
    paused: '暂停',
    completed: '已完成',
    analyzed: '已分析'
  }
  return statusMap[status] || status
}

const getTestTypeText = (type: string) => {
  const typeMap: Record<string, string> = {
    model_comparison: '模型对比',
    retrieval_method: '检索方法对比',
    chunk_size: '分块大小对比',
    context_window: '上下文窗口对比',
    rag_vs_baseline: 'RAG vs 基线'
  }
  return typeMap[type] || type
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}
</script>

<style scoped>
.ab-test-management {
  padding: 20px;
}

.header-card {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-section h2 {
  margin: 0 0 8px 0;
  color: #303133;
}

.subtitle {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.test-list-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.test-name {
  display: flex;
  align-items: center;
  gap: 10px;
}

.name {
  font-weight: 500;
}

.test-detail {
  max-height: 600px;
  overflow-y: auto;
}

.config-json {
  background: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  white-space: pre-wrap;
  word-break: break-all;
}

.test-summary {
  margin: 20px 0;
}

.detail-actions {
  margin-top: 20px;
  text-align: center;
}

:deep(.el-descriptions__label) {
  font-weight: 600;
}

:deep(.el-statistic__content) {
  font-size: 24px;
  font-weight: 600;
}
</style> 