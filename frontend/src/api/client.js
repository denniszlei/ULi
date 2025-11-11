import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const client = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
client.interceptors.request.use(
  (config) => {
    // 可以在这里添加token等认证信息
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
client.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    const message = error.response?.data?.error?.message || error.message || '请求失败'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

// API方法
export const api = {
  // API Sources
  getApiSources: () => client.get('/api-sources'),
  createApiSource: (data) => client.post('/api-sources', data),
  updateApiSource: (id, data) => client.put(`/api-sources/${id}`, data),
  deleteApiSource: (id) => client.delete(`/api-sources/${id}`),
  testApiSource: (id) => client.post(`/api-sources/${id}/test`),
  refreshModels: (id) => client.post(`/api-sources/${id}/refresh`),

  // Models
  getModels: (params) => client.get('/models', { params }),
  getModel: (id) => client.get(`/models/${id}`),
  renameModel: (id, data) => client.put(`/models/${id}/rename`, data),
  batchRenameModels: (data) => client.post('/models/batch-rename', data),
  deleteModel: (id) => client.delete(`/models/${id}`),
  batchDeleteModels: (data) => client.post('/models/batch-delete', data),

  // Providers
  getProviders: () => client.get('/providers'),
  getMappings: () => client.get('/mappings'),
  getModelGroups: () => client.get('/mappings/groups'),
  getProviderSplits: () => client.get('/mappings/splits'),

  // Config
  generateConfig: (data) => client.post('/config/generate', data),
  previewConfig: () => client.get('/config/preview'),
  applyConfig: () => client.post('/config/apply'),
  validateConfig: () => client.post('/config/validate'),

  // Health
  getHealth: () => client.get('/health'),
  getProviderHealth: () => client.get('/health/providers'),
  triggerHealthCheck: () => client.post('/health/check')
}

export default client