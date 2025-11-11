<template>
  <Layout>
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>API源列表</span>
          <el-space>
            <el-button
              type="primary"
              :icon="Plus"
              @click="handleAdd"
            >
              添加API源
            </el-button>
            <el-button
              :icon="Refresh"
              :loading="loading"
              @click="loadApiSources"
            >
              刷新
            </el-button>
          </el-space>
        </div>
      </template>
      
      <el-table
        v-loading="loading"
        :data="apiSources"
        style="width: 100%"
        stripe
      >
        <el-table-column prop="name" label="名称" min-width="150" />
        
        <el-table-column prop="base_url" label="Base URL" min-width="250" show-overflow-tooltip />
        
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'danger'" size="small">
              {{ row.enabled ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="优先级" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="info" size="small">{{ row.priority || 0 }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="模型数量" width="100" align="center">
          <template #default="{ row }">
            <el-badge :value="getModelCount(row.id)" :max="99" type="primary">
              <el-icon><Box /></el-icon>
            </el-badge>
          </template>
        </el-table-column>
        
        <el-table-column label="最后检查" width="160" show-overflow-tooltip>
          <template #default="{ row }">
            {{ formatTime(row.updated_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="320" fixed="right">
          <template #default="{ row }">
            <el-space :size="4">
              <el-button
                size="small"
                :icon="Connection"
                :loading="testingIds.includes(row.id)"
                @click="handleTest(row)"
              >
                测试
              </el-button>
              <el-button
                size="small"
                :icon="Refresh"
                :loading="refreshingIds.includes(row.id)"
                @click="handleRefresh(row)"
              >
                刷新模型
              </el-button>
              <el-button
                size="small"
                type="primary"
                :icon="Edit"
                @click="handleEdit(row)"
              >
                编辑
              </el-button>
              <el-button
                size="small"
                type="danger"
                :icon="Delete"
                @click="handleDelete(row)"
              >
                删除
              </el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>
      
      <el-empty v-if="!loading && apiSources.length === 0" description="暂无API源，请添加" />
    </el-card>
    
    <!-- API源表单对话框 -->
    <ApiSourceForm
      v-model:visible="formVisible"
      :mode="formMode"
      :data="currentSource"
      @success="handleFormSuccess"
    />
  </Layout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Refresh,
  Connection,
  Edit,
  Delete,
  Box
} from '@element-plus/icons-vue'
import Layout from '@/components/Layout.vue'
import ApiSourceForm from '@/components/ApiSourceForm.vue'
import { api } from '@/api/client'

const loading = ref(false)
const apiSources = ref([])
const modelCounts = ref({})
const testingIds = ref([])
const refreshingIds = ref([])

const formVisible = ref(false)
const formMode = ref('create')
const currentSource = ref({})

const loadApiSources = async () => {
  loading.value = true
  try {
    const data = await api.getApiSources()
    apiSources.value = data.providers || []
    
    // 加载每个API源的模型数量
    await loadModelCounts()
  } catch (error) {
    console.error('加载API源失败:', error)
    ElMessage.error('加载API源失败')
  } finally {
    loading.value = false
  }
}

const loadModelCounts = async () => {
  try {
    const data = await api.getModels()
    const counts = {}
    
    if (data.models) {
      data.models.forEach(model => {
        const providerId = model.provider_id
        counts[providerId] = (counts[providerId] || 0) + 1
      })
    }
    
    modelCounts.value = counts
  } catch (error) {
    console.error('加载模型数量失败:', error)
  }
}

const getModelCount = (providerId) => {
  return modelCounts.value[providerId] || 0
}

const handleAdd = () => {
  formMode.value = 'create'
  currentSource.value = {}
  formVisible.value = true
}

const handleEdit = (row) => {
  formMode.value = 'edit'
  currentSource.value = { ...row }
  formVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除API源 "${row.name}" 吗？这将同时删除该源下的所有模型。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await api.deleteApiSource(row.id)
    ElMessage.success('删除成功')
    await loadApiSources()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleTest = async (row) => {
  testingIds.value.push(row.id)
  try {
    const result = await api.testApiSource(row.id)
    
    if (result.success) {
      ElMessage.success(`连接成功！响应时间: ${result.response_time}ms`)
    } else {
      ElMessage.error(`连接失败: ${result.error}`)
    }
  } catch (error) {
    ElMessage.error('测试连接失败')
  } finally {
    testingIds.value = testingIds.value.filter(id => id !== row.id)
  }
}

const handleRefresh = async (row) => {
  refreshingIds.value.push(row.id)
  try {
    const result = await api.refreshModels(row.id)
    ElMessage.success(`刷新成功！获取到 ${result.total || 0} 个模型`)
    await loadModelCounts()
  } catch (error) {
    ElMessage.error('刷新模型列表失败')
  } finally {
    refreshingIds.value = refreshingIds.value.filter(id => id !== row.id)
  }
}

const handleFormSuccess = async () => {
  await loadApiSources()
}

const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  const date = new Date(timeStr)
  const now = new Date()
  const diff = Math.floor((now - date) / 1000)
  
  if (diff < 60) return `${diff}秒前`
  if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`
  if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`
  return date.toLocaleDateString('zh-CN')
}

onMounted(() => {
  loadApiSources()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
}

:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-table__header) {
  font-weight: 600;
}
</style>