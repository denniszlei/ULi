<template>
  <Layout>
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>模型列表</span>
          <el-space>
            <el-select
              v-model="filterProvider"
              placeholder="筛选Provider"
              clearable
              style="width: 200px"
              @change="handleFilterChange"
            >
              <el-option label="全部Provider" value="" />
              <el-option
                v-for="provider in providers"
                :key="provider.id"
                :label="provider.name"
                :value="provider.id"
              />
            </el-select>
            
            <el-input
              v-model="searchText"
              placeholder="搜索模型名称"
              clearable
              style="width: 200px"
              :prefix-icon="Search"
            />
            
            <el-button
              type="danger"
              :icon="Delete"
              :disabled="selectedModels.length === 0"
              @click="handleBatchDelete"
            >
              批量删除 ({{ selectedModels.length }})
            </el-button>
            
            <el-button
              :icon="Refresh"
              :loading="loading"
              @click="loadModels"
            >
              刷新
            </el-button>
          </el-space>
        </div>
      </template>
      
      <el-table
        v-loading="loading"
        :data="filteredModels"
        style="width: 100%"
        stripe
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column label="显示名称" min-width="200">
          <template #default="{ row }">
            <div class="model-name">
              <span class="name-text">{{ row.display_name || row.normalized_name }}</span>
              <el-tag v-if="row.display_name" type="success" size="small" effect="plain">
                已重命名
              </el-tag>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="original_name" label="原始名称" min-width="200" show-overflow-tooltip />
        
        <el-table-column prop="normalized_name" label="标准化名称" min-width="180" show-overflow-tooltip />
        
        <el-table-column label="所属Provider" min-width="150">
          <template #default="{ row }">
            <el-tag type="info" size="small">
              {{ getProviderName(row.provider_id) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'danger'" size="small">
              {{ row.enabled ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="创建时间" width="160" show-overflow-tooltip>
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-space :size="4">
              <el-button
                size="small"
                type="primary"
                :icon="Edit"
                @click="handleRename(row)"
              >
                重命名
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
      
      <el-empty v-if="!loading && models.length === 0" description="暂无模型数据" />
      
      <div v-if="filteredModels.length > 0" class="table-footer">
        <el-text type="info">
          共 {{ filteredModels.length }} 个模型
          <span v-if="searchText || filterProvider">（已筛选）</span>
        </el-text>
      </div>
    </el-card>
    
    <!-- 重命名对话框 -->
    <ModelRenameDialog
      v-model:visible="renameVisible"
      :model-data="currentModel"
      @success="handleRenameSuccess"
    />
  </Layout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search,
  Refresh,
  Edit,
  Delete
} from '@element-plus/icons-vue'
import Layout from '@/components/Layout.vue'
import ModelRenameDialog from '@/components/ModelRenameDialog.vue'
import { api } from '@/api/client'

const loading = ref(false)
const models = ref([])
const providers = ref([])
const searchText = ref('')
const filterProvider = ref('')
const selectedModels = ref([])

const renameVisible = ref(false)
const currentModel = ref({})

const filteredModels = computed(() => {
  let result = models.value
  
  // 按Provider筛选
  if (filterProvider.value) {
    result = result.filter(m => m.provider_id === filterProvider.value)
  }
  
  // 按名称搜索
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    result = result.filter(m =>
      m.display_name?.toLowerCase().includes(search) ||
      m.original_name?.toLowerCase().includes(search) ||
      m.normalized_name?.toLowerCase().includes(search)
    )
  }
  
  return result
})

const loadModels = async () => {
  loading.value = true
  try {
    const data = await api.getModels()
    models.value = data.models || []
  } catch (error) {
    console.error('加载模型失败:', error)
    ElMessage.error('加载模型失败')
  } finally {
    loading.value = false
  }
}

const loadProviders = async () => {
  try {
    const data = await api.getApiSources()
    providers.value = data.providers || []
  } catch (error) {
    console.error('加载Provider失败:', error)
  }
}

const getProviderName = (providerId) => {
  const provider = providers.value.find(p => p.id === providerId)
  return provider?.name || providerId
}

const handleSelectionChange = (selection) => {
  selectedModels.value = selection
}

const handleFilterChange = () => {
  // 筛选变化时清空选择
  selectedModels.value = []
}

const handleRename = (row) => {
  currentModel.value = { ...row }
  renameVisible.value = true
}

const handleRenameSuccess = async () => {
  await loadModels()
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除模型 "${row.display_name || row.normalized_name}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await api.deleteModel(row.id)
    ElMessage.success('删除成功')
    await loadModels()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleBatchDelete = async () => {
  if (selectedModels.value.length === 0) {
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedModels.value.length} 个模型吗？`,
      '批量删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const ids = selectedModels.value.map(m => m.id)
    const result = await api.batchDeleteModels({ model_ids: ids })
    
    ElMessage.success(`成功删除 ${result.deleted || ids.length} 个模型`)
    selectedModels.value = []
    await loadModels()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  loadModels()
  loadProviders()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
}

.model-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.name-text {
  font-weight: 500;
}

.table-footer {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
  text-align: right;
}

:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-table__header) {
  font-weight: 600;
}
</style>