<template>
  <Layout>
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="API源数量" :value="stats.apiSources">
            <template #prefix>
              <el-icon color="#409eff"><Connection /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="模型总数" :value="stats.totalModels">
            <template #prefix>
              <el-icon color="#67c23a"><Box /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="在线Provider" :value="stats.healthyProviders">
            <template #prefix>
              <el-icon color="#67c23a"><SuccessFilled /></el-icon>
            </template>
            <template #suffix>
              <span class="stat-suffix">/ {{ stats.totalProviders }}</span>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="system-status">
            <div class="status-title">系统状态</div>
            <div class="status-value">
              <el-tag
                :type="getStatusType(stats.systemStatus)"
                size="large"
                effect="dark"
              >
                {{ getStatusText(stats.systemStatus) }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="content-row">
      <el-col :xs="24" :lg="16">
        <el-card shadow="hover" class="content-card">
          <template #header>
            <div class="card-header">
              <span>Provider健康状态</span>
              <el-button
                size="small"
                :icon="Refresh"
                :loading="refreshing"
                @click="handleRefreshHealth"
              >
                刷新
              </el-button>
            </div>
          </template>
          
          <ProviderStatus
            ref="providerStatusRef"
            :auto-refresh="false"
            @refresh="handleProviderRefresh"
          />
        </el-card>
      </el-col>
      
      <el-col :xs="24" :lg="8">
        <el-card shadow="hover" class="content-card">
          <template #header>
            <div class="card-header">
              <span>快速操作</span>
            </div>
          </template>
          
          <el-space direction="vertical" :size="12" style="width: 100%">
            <el-button
              type="primary"
              :icon="Plus"
              style="width: 100%"
              @click="$router.push('/api-sources')"
            >
              添加API源
            </el-button>
            
            <el-button
              type="success"
              :icon="View"
              style="width: 100%"
              @click="$router.push('/models')"
            >
              管理模型
            </el-button>
            
            <el-button
              type="warning"
              :icon="Setting"
              style="width: 100%"
              @click="$router.push('/config')"
            >
              生成配置
            </el-button>
            
            <el-divider />
            
            <el-button
              :icon="Refresh"
              style="width: 100%"
              :loading="checkingHealth"
              @click="handleCheckAllHealth"
            >
              检查所有Provider健康状态
            </el-button>
          </el-space>
        </el-card>
        
        <el-card shadow="hover" class="content-card" style="margin-top: 20px">
          <template #header>
            <div class="card-header">
              <span>系统信息</span>
            </div>
          </template>
          
          <el-descriptions :column="1" size="small" border>
            <el-descriptions-item label="最后更新">
              {{ formatTime(stats.lastUpdate) }}
            </el-descriptions-item>
            <el-descriptions-item label="配置状态">
              <el-tag :type="stats.configGenerated ? 'success' : 'warning'" size="small">
                {{ stats.configGenerated ? '已生成' : '未生成' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="已重命名模型">
              {{ stats.renamedModels }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </Layout>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Connection,
  Box,
  SuccessFilled,
  Refresh,
  Plus,
  View,
  Setting
} from '@element-plus/icons-vue'
import Layout from '@/components/Layout.vue'
import ProviderStatus from '@/components/ProviderStatus.vue'
import { api } from '@/api/client'

const providerStatusRef = ref(null)
const refreshing = ref(false)
const checkingHealth = ref(false)

const stats = ref({
  apiSources: 0,
  totalModels: 0,
  healthyProviders: 0,
  totalProviders: 0,
  systemStatus: 'healthy',
  lastUpdate: new Date().toISOString(),
  configGenerated: false,
  renamedModels: 0
})

let autoRefreshTimer = null

const loadStats = async () => {
  try {
    // 加载健康状态
    const healthData = await api.getHealth()
    stats.value.systemStatus = healthData.status || 'healthy'
    stats.value.healthyProviders = healthData.providers?.healthy || 0
    stats.value.totalProviders = healthData.providers?.total || 0
    
    // 加载API源列表
    const sourcesData = await api.getApiSources()
    stats.value.apiSources = sourcesData.providers?.length || 0
    
    // 加载模型统计
    const modelsData = await api.getModels()
    stats.value.totalModels = modelsData.models?.length || 0
    stats.value.renamedModels = modelsData.models?.filter(m => m.display_name)?.length || 0
    
    // 检查配置状态
    try {
      const configData = await api.previewConfig()
      stats.value.configGenerated = !!(configData.gpt_load_config || configData.uni_api_config)
    } catch {
      stats.value.configGenerated = false
    }
    
    stats.value.lastUpdate = new Date().toISOString()
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const handleRefreshHealth = () => {
  refreshing.value = true
  providerStatusRef.value?.handleRefresh()
  setTimeout(() => {
    refreshing.value = false
  }, 1000)
}

const handleProviderRefresh = (providers) => {
  // 更新Provider统计
  stats.value.totalProviders = providers.length
  stats.value.healthyProviders = providers.filter(p => p.status === 'healthy').length
}

const handleCheckAllHealth = async () => {
  checkingHealth.value = true
  try {
    await api.triggerHealthCheck()
    ElMessage.success('健康检查已触发')
    // 等待一会儿后刷新数据
    setTimeout(() => {
      loadStats()
      handleRefreshHealth()
    }, 2000)
  } catch (error) {
    ElMessage.error('触发健康检查失败')
  } finally {
    checkingHealth.value = false
  }
}

const getStatusType = (status) => {
  const typeMap = {
    healthy: 'success',
    degraded: 'warning',
    unhealthy: 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    healthy: '正常',
    degraded: '降级',
    unhealthy: '异常'
  }
  return textMap[status] || '未知'
}

const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

onMounted(() => {
  loadStats()
  
  // 每30秒自动刷新统计数据
  autoRefreshTimer = setInterval(() => {
    loadStats()
  }, 30000)
})

onUnmounted(() => {
  if (autoRefreshTimer) {
    clearInterval(autoRefreshTimer)
  }
})
</script>

<style scoped>
.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  height: 100%;
}

.stat-card :deep(.el-statistic__head) {
  font-size: 14px;
  color: #909399;
}

.stat-card :deep(.el-statistic__content) {
  font-size: 28px;
  font-weight: 600;
}

.stat-suffix {
  font-size: 16px;
  color: #909399;
  margin-left: 4px;
}

.system-status {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.status-title {
  font-size: 14px;
  color: #909399;
}

.status-value {
  display: flex;
  align-items: center;
  justify-content: center;
}

.content-row {
  margin-bottom: 20px;
}

.content-card {
  margin-bottom: 20px;
}

.content-card:last-child {
  margin-bottom: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
}

@media (max-width: 768px) {
  .stats-row {
    margin-bottom: 10px;
  }
  
  .stat-card {
    margin-bottom: 10px;
  }
}
</style>