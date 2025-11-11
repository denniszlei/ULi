<template>
  <el-dialog
    :model-value="visible"
    title="重命名模型"
    width="500px"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="100px"
    >
      <el-form-item label="原始名称">
        <el-input :value="modelData.original_name" disabled />
      </el-form-item>
      
      <el-form-item label="标准化名称">
        <el-input :value="modelData.normalized_name" disabled />
      </el-form-item>
      
      <el-form-item label="显示名称" prop="display_name">
        <el-input
          v-model="formData.display_name"
          placeholder="请输入自定义显示名称"
          clearable
        />
        <div class="form-tip">留空则使用标准化名称</div>
      </el-form-item>
    </el-form>
    
    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">
        确定
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '@/api/client'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  modelData: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:visible', 'success', 'cancel'])

const formRef = ref(null)
const submitting = ref(false)

const formData = reactive({
  display_name: ''
})

const rules = {
  display_name: [
    { max: 100, message: '长度不能超过 100 个字符', trigger: 'blur' }
  ]
}

watch(() => props.modelData, (newData) => {
  if (newData && Object.keys(newData).length > 0) {
    formData.display_name = newData.display_name || ''
  }
}, { immediate: true, deep: true })

watch(() => props.visible, (newVal) => {
  if (!newVal) {
    formRef.value?.resetFields()
  }
})

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  
  submitting.value = true
  
  try {
    await api.renameModel(props.modelData.id, {
      display_name: formData.display_name || null
    })
    ElMessage.success('模型重命名成功')
    emit('success')
    handleClose()
  } catch (error) {
    ElMessage.error('重命名失败')
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
  margin-top: 5px;
  font-size: 12px;
  color: #909399;
}
</style>