<template>
  <el-card class="provider-status-card">
    <template #header>
      <div class="card-header">
        <span>Provider状态</span>
        <el-button
          size="small"
          :icon="Refresh"
          :loading="loading"
          @click="handleRefresh"
        >
          刷新
        </el-button>
      </div>
    </template>
    
    <el-empty v-if="providers.length === 0" description="暂无Provider数据" />
    
    <div v-else class="provider-list">
      <div
        v-for="provider in providers"
        :key="provider.id"
        class="provider-item"
      >
        <div class="provider-info">
          <div class="provider-name">
            <el-icon :class="getStatusClass(provider.status)">
              <component :is="getStatusIcon(provider.status)" />
            </el-icon>
            <span>{{ provider.name }}</span>
          </div>
          <div class="provider-details">
            <el-tag :type="getStatusType(provider.status)" size="small">
              {{ getStatusText(provider.status) }}
            </el-tag>
            <span v-if="provider.response_time" class="response-time">
              {{ provider.response_time }}ms
            </span>
          </div>
        </div>
        
        <div v-if="provider.error" class="provider-error">
          <el-icon><WarningFilled /></el-icon>
          <span>{{ provider.error }}</span>
        </div>
        
        <div class="provider-meta">
          <span class="meta-item">
            <el-icon><Box /></el-icon>
            模型数: {{ provider.model_count || 0 }}
          </span>
          <span v-if="provider.last_check" class="meta-item">
            <el-icon><Clock /></el-icon>
            最后检查: {{ formatTime(provider.last_check) }}
          </span>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Refresh,
  SuccessFilled,
  WarningFilled,
  CircleCloseFilled,
  Clock,
  Box
} from '@element-plus/icons-vue'
import { api } from '@/api/client'

const props = defineProps({
  autoRefresh: {
    type: Boolean,
    default: false
  },
  refreshInterval: {
    type: Number,
    default: 60000 // 60秒
  }
})

const emit = defineEmits(['refresh'])

const providers = ref([])
const loading = ref(false)
let refreshTimer = null

const loadProviders = async () => {
  loading.value = true
  try {
    const data = await api.getProviderHealth()
    providers.value = data.providers || []
    emit('refresh', providers.value)
  } catch (error) {
    console.error('加载Provider状态失败:', error)
    ElMessage.error('加载Provider状态失败')
  } finally {
    loading.value = false
  }
}

const handleRefresh = () => {
  loadProviders()
}

const getStatusIcon = (status) => {
  const iconMap = {
    healthy: SuccessFilled,
    unhealthy: CircleCloseFilled,
    timeout: WarningFilled
  }
  return iconMap[status] || WarningFilled
}

const getStatusClass = (status) => {
  return `status-icon status-${status}`
}

const getStatusType = (status) => {
  const typeMap = {
    healthy: 'success',
    unhealthy: 'danger',
    timeout: 'warning'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    healthy: '正常',
    unhealthy: '异常',
    timeout: '超时'
  }
  return textMap[status] || '未知'
}

const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  const date = new Date(timeStr)
  const now = new Date()
  const diff = Math.floor((now - date) / 1000)
  
  if (diff < 60) return `${diff}秒前`
  if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`
  if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`
  return `${Math.floor(diff / 86400)}天前`
}

onMounted(() => {
  loadProviders()
  
  if (props.autoRefresh) {
    refreshTimer = setInterval(() => {
      loadProviders()
    }, props.refreshInterval)
  }
})

// 清理定时器
if (refreshTimer) {
  clearInterval(refreshTimer)
}
</script>

<style scoped>
.provider-status-card {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.provider-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.provider-item {
  padding: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  background-color: #fafafa;
  transition: all 0.3s;
}

.provider-item:hover {
  background-color: #f5f7fa;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.provider-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.provider-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.status-icon {
  font-size: 16px;
}

.status-icon.status-healthy {
  color: #67c23a;
}

.status-icon.status-unhealthy {
  color: #f56c6c;
}

.status-icon.status-timeout {
  color: #e6a23c;
}

.provider-details {
  display: flex;
  align-items: center;
  gap: 8px;
}

.response-time {
  font-size: 12px;
  color: #909399;
}

.provider-error {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 8px;
  padding: 8px;
  background-color: #fef0f0;
  border-radius: 4px;
  font-size: 12px;
  color: #f56c6c;
}

.provider-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #909399;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>