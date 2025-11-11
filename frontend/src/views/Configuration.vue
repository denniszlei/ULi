<template>
  <Layout>
    <el-row :gutter="20">
      <el-col :xs="24" :lg="12">
        <el-card shadow="hover" class="config-card">
          <template #header>
            <div class="card-header">
              <span>gpt-load配置</span>
              <el-space>
                <el-button
                  size="small"
                  :icon="View"
                  :disabled="!gptLoadConfig"
                  @click="handlePreview('gpt-load')"
                >
                  预览
                </el-button>
                <el-button
                  size="small"
                  :icon="Download"
                  :disabled="!gptLoadConfig"
                  @click="handleDownload('gpt-load')"
                >
                  下载
                </el-button>
              </el-space>
            </div>
          </template>
          
          <div v-if="gptLoadConfig" class="config-content">
            <el-scrollbar height="400px">
              <pre class="config-preview">{{ gptLoadConfig }}</pre>
            </el-scrollbar>
            
            <div class="config-stats">
              <el-descriptions :column="2" size="small" border>
                <el-descriptions-item label="Providers">
                  {{ gptLoadStats.providers || 0 }}
                </el-descriptions-item>
                <el-descriptions-item label="Groups">
                  {{ gptLoadStats.groups || 0 }}
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </div>
          
          <el-empty v-else description="暂无配置，请先生成配置" />
        </el-card>
      </el-col>
      
      <el-col :xs="24" :lg="12">
        <el-card shadow="hover" class="config-card">
          <template #header>
            <div class="card-header">
              <span>uni-api配置</span>
              <el-space>
                <el-button
                  size="small"
                  :icon="View"
                  :disabled="!uniApiConfig"
                  @click="handlePreview('uni-api')"
                >
                  预览
                </el-button>
                <el-button
                  size="small"
                  :icon="Download"
                  :disabled="!uniApiConfig"
                  @click="handleDownload('uni-api')"
                >
                  下载
                </el-button>
              </el-space>
            </div>
          </template>
          
          <div v-if="uniApiConfig" class="config-content">
            <el-scrollbar height="400px">
              <pre class="config-preview">{{ uniApiConfig }}</pre>
            </el-scrollbar>
            
            <div class="config-stats">
              <el-descriptions :column="2" size="small" border>
                <el-descriptions-item label="Providers">
                  {{ uniApiStats.providers || 0 }}
                </el-descriptions-item>
                <el-descriptions-item label="Models">
                  {{ uniApiStats.models || 0 }}
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </div>
          
          <el-empty v-else description="暂无配置，请先生成配置" />
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="hover" class="action-card">
      <template #header>
        <span>配置操作</span>
      </template>
      
      <el-space wrap :size="12">
        <el-button
          type="primary"
          :icon="Refresh"
          :loading="generating"
          @click="handleGenerate"
        >
          生成配置
        </el-button>
        
        <el-button
          type="success"
          :icon="Check"
          :disabled="!hasConfig"
          :loading="applying"
          @click="handleApply"
        >
          应用配置
        </el-button>
        
        <el-button
          type="warning"
          :icon="CircleCheck"
          :disabled="!hasConfig"
          :loading="validating"
          @click="handleValidate"
        >
          验证配置
        </el-button>
        
        <el-divider direction="vertical" />
        
        <el-button
          :icon="Refresh"
          :loading="loading"
          @click="loadConfig"
        >
          刷新
        </el-button>
      </el-space>
      
      <el-alert
        v-if="lastGenerated"
        :title="`最后生成时间: ${formatTime(lastGenerated)}`"
        type="info"
        :closable="false"
        style="margin-top: 16px"
      />
    </el-card>
    
    <!-- 配置预览对话框 -->
    <ConfigPreview
      v-model:visible="previewVisible"
      :title="previewTitle"
      :config="previewConfig"
      :stats="previewStats"
    />
  </Layout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  View,
  Download,
  Refresh,
  Check,
  CircleCheck
} from '@element-plus/icons-vue'
import Layout from '@/components/Layout.vue'
import ConfigPreview from '@/components/ConfigPreview.vue'
import { api } from '@/api/client'
import yaml from 'js-yaml'

const loading = ref(false)
const generating = ref(false)
const applying = ref(false)
const validating = ref(false)

const gptLoadConfig = ref('')
const uniApiConfig = ref('')
const lastGenerated = ref(null)

const gptLoadStats = ref({})
const uniApiStats = ref({})

const previewVisible = ref(false)
const previewTitle = ref('')
const previewConfig = ref('')
const previewStats = ref(null)

const hasConfig = computed(() => gptLoadConfig.value || uniApiConfig.value)

const loadConfig = async () => {
  loading.value = true
  try {
    const data = await api.previewConfig()
    gptLoadConfig.value = data.gpt_load_config || ''
    uniApiConfig.value = data.uni_api_config || ''
    lastGenerated.value = data.generated_at || null
    
    // 解析配置统计信息
    parseConfigStats()
  } catch (error) {
    console.error('加载配置失败:', error)
  } finally {
    loading.value = false
  }
}

const parseConfigStats = () => {
  try {
    if (gptLoadConfig.value) {
      const config = yaml.load(gptLoadConfig.value)
      gptLoadStats.value = {
        providers: config.providers?.length || 0,
        groups: config.groups?.length || 0
      }
    }
    
    if (uniApiConfig.value) {
      const config = yaml.load(uniApiConfig.value)
      uniApiStats.value = {
        providers: config.providers?.length || 0,
        models: config.providers?.reduce((sum, p) => sum + (p.models?.length || 0), 0) || 0
      }
    }
  } catch (error) {
    console.error('解析配置统计失败:', error)
  }
}

const handleGenerate = async () => {
  try {
    await ElMessageBox.confirm(
      '生成新配置将覆盖现有配置，是否继续？',
      '生成确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
  } catch {
    return
  }
  
  generating.value = true
  try {
    await api.generateConfig({ force: true })
    ElMessage.success('配置生成成功')
    await loadConfig()
  } catch (error) {
    ElMessage.error('配置生成失败')
  } finally {
    generating.value = false
  }
}

const handleApply = async () => {
  try {
    await ElMessageBox.confirm(
      '应用配置将重启相关服务，可能会短暂中断服务，是否继续？',
      '应用确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
  } catch {
    return
  }
  
  applying.value = true
  try {
    const result = await api.applyConfig()
    
    if (result.success) {
      ElMessage.success('配置应用成功')
    } else {
      ElMessage.warning('配置应用部分成功，请查看日志')
    }
  } catch (error) {
    ElMessage.error('配置应用失败')
  } finally {
    applying.value = false
  }
}

const handleValidate = async () => {
  validating.value = true
  try {
    const result = await api.validateConfig()
    
    if (result.valid) {
      ElMessage.success('配置验证通过')
    } else {
      ElMessageBox.alert(
        result.errors?.join('\n') || '配置验证失败',
        '验证结果',
        {
          type: 'error',
          confirmButtonText: '确定'
        }
      )
    }
  } catch (error) {
    ElMessage.error('配置验证失败')
  } finally {
    validating.value = false
  }
}

const handlePreview = (type) => {
  if (type === 'gpt-load') {
    previewTitle.value = 'gpt-load配置'
    previewConfig.value = gptLoadConfig.value
    previewStats.value = gptLoadStats.value
  } else {
    previewTitle.value = 'uni-api配置'
    previewConfig.value = uniApiConfig.value
    previewStats.value = uniApiStats.value
  }
  previewVisible.value = true
}

const handleDownload = (type) => {
  try {
    const config = type === 'gpt-load' ? gptLoadConfig.value : uniApiConfig.value
    const filename = type === 'gpt-load' ? 'gpt-load.yaml' : 'uni-api.yaml'
    
    const blob = new Blob([config], { type: 'text/yaml' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    
    ElMessage.success('下载成功')
  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error('下载失败')
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
    minute: '2-digit',
    second: '2-digit'
  })
}

onMounted(() => {
  loadConfig()
})
</script>

<style scoped>
.config-card {
  margin-bottom: 20px;
  height: calc(100% - 20px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
}

.config-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.config-preview {
  margin: 0;
  padding: 16px;
  background-color: #f5f7fa;
  border-radius: 4px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.6;
  color: #2c3e50;
  white-space: pre;
  word-wrap: normal;
  overflow-x: auto;
}

.config-stats {
  padding-top: 12px;
  border-top: 1px solid #e4e7ed;
}

.action-card {
  margin-bottom: 20px;
}

@media (max-width: 992px) {
  .config-card {
    height: auto;
  }
}
</style>