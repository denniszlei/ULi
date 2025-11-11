<template>
  <el-dialog
    :model-value="visible"
    :title="`${title} - 配置预览`"
    width="800px"
    @close="handleClose"
  >
    <div class="config-preview-container">
      <div class="preview-header">
        <el-radio-group v-model="format" size="small">
          <el-radio-button label="yaml">YAML</el-radio-button>
          <el-radio-button label="json">JSON</el-radio-button>
        </el-radio-group>
        
        <el-space>
          <el-button
            size="small"
            :icon="CopyDocument"
            @click="handleCopy"
          >
            复制
          </el-button>
          <el-button
            size="small"
            :icon="Download"
            @click="handleDownload"
          >
            下载
          </el-button>
        </el-space>
      </div>
      
      <div class="preview-content">
        <el-scrollbar height="500px">
          <pre class="code-block"><code>{{ formattedConfig }}</code></pre>
        </el-scrollbar>
      </div>
      
      <div v-if="stats" class="preview-stats">
        <el-descriptions :column="3" size="small" border>
          <el-descriptions-item label="Providers">
            {{ stats.providers || 0 }}
          </el-descriptions-item>
          <el-descriptions-item label="Models">
            {{ stats.models || 0 }}
          </el-descriptions-item>
          <el-descriptions-item label="Groups">
            {{ stats.groups || 0 }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </div>
    
    <template #footer>
      <el-button @click="handleClose">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { CopyDocument, Download } from '@element-plus/icons-vue'
import yaml from 'js-yaml'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: '配置'
  },
  config: {
    type: [Object, String],
    default: () => ({})
  },
  defaultFormat: {
    type: String,
    default: 'yaml',
    validator: (value) => ['yaml', 'json'].includes(value)
  },
  stats: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:visible', 'close'])

const format = ref(props.defaultFormat)

const formattedConfig = computed(() => {
  if (!props.config) return ''
  
  try {
    // 如果config已经是字符串，尝试解析它
    let configObj = props.config
    if (typeof props.config === 'string') {
      try {
        configObj = yaml.load(props.config)
      } catch {
        // 如果解析失败，直接返回原字符串
        return props.config
      }
    }
    
    // 根据选择的格式转换
    if (format.value === 'json') {
      return JSON.stringify(configObj, null, 2)
    } else {
      return yaml.dump(configObj, {
        indent: 2,
        lineWidth: -1,
        noRefs: true
      })
    }
  } catch (error) {
    console.error('格式化配置失败:', error)
    return String(props.config)
  }
})

watch(() => props.defaultFormat, (newVal) => {
  format.value = newVal
})

const handleCopy = async () => {
  try {
    await navigator.clipboard.writeText(formattedConfig.value)
    ElMessage.success('已复制到剪贴板')
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败')
  }
}

const handleDownload = () => {
  try {
    const blob = new Blob([formattedConfig.value], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${props.title.toLowerCase().replace(/\s+/g, '-')}.${format.value}`
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

const handleClose = () => {
  emit('update:visible', false)
  emit('close')
}
</script>

<style scoped>
.config-preview-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.preview-content {
  background-color: #f5f7fa;
  border-radius: 4px;
  overflow: hidden;
}

.code-block {
  margin: 0;
  padding: 16px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #2c3e50;
  background-color: transparent;
  white-space: pre;
  word-wrap: normal;
  overflow-x: auto;
}

.code-block code {
  background-color: transparent;
  padding: 0;
  border-radius: 0;
}

.preview-stats {
  padding-top: 12px;
  border-top: 1px solid #e4e7ed;
}
</style>