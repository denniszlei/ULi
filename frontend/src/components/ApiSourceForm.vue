<template>
  <el-dialog
    :model-value="visible"
    :title="mode === 'create' ? '添加API源' : '编辑API源'"
    width="600px"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="100px"
    >
      <el-form-item label="名称" prop="name">
        <el-input
          v-model="formData.name"
          placeholder="请输入API源名称"
          clearable
        />
      </el-form-item>
      
      <el-form-item label="Base URL" prop="base_url">
        <el-input
          v-model="formData.base_url"
          placeholder="https://api.example.com/v1"
          clearable
        >
          <template #append>
            <el-button
              :icon="Connection"
              :loading="testing"
              @click="handleTestConnection"
            >
              测试连接
            </el-button>
          </template>
        </el-input>
      </el-form-item>
      
      <el-form-item label="API Key" prop="api_key">
        <el-input
          v-model="formData.api_key"
          type="password"
          placeholder="请输入API Key"
          show-password
          clearable
        />
      </el-form-item>
      
      <el-form-item label="优先级" prop="priority">
        <el-input-number
          v-model="formData.priority"
          :min="0"
          :max="100"
          placeholder="0-100"
        />
        <span class="form-tip">数值越大优先级越高</span>
      </el-form-item>
      
      <el-form-item label="启用状态" prop="enabled">
        <el-switch v-model="formData.enabled" />
      </el-form-item>
      
      <el-alert
        v-if="testResult"
        :type="testResult.success ? 'success' : 'error'"
        :title="testResult.message"
        :closable="false"
        show-icon
        class="test-result"
      />
    </el-form>
    
    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">
        {{ mode === 'create' ? '创建' : '保存' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Connection } from '@element-plus/icons-vue'
import { api } from '@/api/client'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  mode: {
    type: String,
    default: 'create', // 'create' | 'edit'
    validator: (value) => ['create', 'edit'].includes(value)
  },
  data: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:visible', 'success', 'cancel'])

const formRef = ref(null)
const testing = ref(false)
const submitting = ref(false)
const testResult = ref(null)

const formData = reactive({
  name: '',
  base_url: '',
  api_key: '',
  priority: 0,
  enabled: true
})

const rules = {
  name: [
    { required: true, message: '请输入API源名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  base_url: [
    { required: true, message: '请输入Base URL', trigger: 'blur' },
    {
      pattern: /^https?:\/\/.+/,
      message: '请输入有效的URL（以http://或https://开头）',
      trigger: 'blur'
    }
  ],
  api_key: [
    { required: true, message: '请输入API Key', trigger: 'blur' }
  ]
}

// 监听props.data变化，更新表单数据
watch(() => props.data, (newData) => {
  if (newData && Object.keys(newData).length > 0) {
    Object.assign(formData, {
      name: newData.name || '',
      base_url: newData.base_url || '',
      api_key: newData.api_key || '',
      priority: newData.priority || 0,
      enabled: newData.enabled !== undefined ? newData.enabled : true
    })
  }
}, { immediate: true, deep: true })

// 监听visible变化，重置表单
watch(() => props.visible, (newVal) => {
  if (!newVal) {
    resetForm()
  }
})

const resetForm = () => {
  formRef.value?.resetFields()
  testResult.value = null
  Object.assign(formData, {
    name: '',
    base_url: '',
    api_key: '',
    priority: 0,
    enabled: true
  })
}

const handleTestConnection = async () => {
  // 先验证必填字段
  try {
    await formRef.value.validateField(['base_url', 'api_key'])
  } catch {
    ElMessage.warning('请先填写Base URL和API Key')
    return
  }
  
  testing.value = true
  testResult.value = null
  
  try {
    // 如果是编辑模式且有ID，使用现有的测试接口
    if (props.mode === 'edit' && props.data.id) {
      const result = await api.testApiSource(props.data.id)
      testResult.value = {
        success: result.success,
        message: result.success
          ? `连接成功！响应时间: ${result.response_time}ms`
          : `连接失败: ${result.error}`
      }
    } else {
      // 创建模式，临时测试连接
      // 这里需要后端提供一个临时测试接口
      ElMessage.info('连接测试功能需要后端支持')
      testResult.value = {
        success: true,
        message: '请确保URL和API Key正确'
      }
    }
  } catch (error) {
    testResult.value = {
      success: false,
      message: `测试失败: ${error.message}`
    }
  } finally {
    testing.value = false
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  
  submitting.value = true
  
  try {
    if (props.mode === 'create') {
      await api.createApiSource(formData)
      ElMessage.success('API源创建成功')
    } else {
      await api.updateApiSource(props.data.id, formData)
      ElMessage.success('API源更新成功')
    }
    
    emit('success')
    handleClose()
  } catch (error) {
    ElMessage.error(props.mode === 'create' ? '创建失败' : '更新失败')
  } finally {
    submitting.value = false
  }
}

const handleClose = () => {
  emit('update:visible', false)
  emit('cancel')
}
</script>

<style scoped>
.form-tip {
  margin-left: 10px;
  font-size: 12px;
  color: #909399;
}

.test-result {
  margin-top: 10px;
}
</style>