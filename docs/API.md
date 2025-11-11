# uni-load-improved API文档

本文档详细描述了uni-load-improved提供的所有REST API接口。

## 基本信息

- **Base URL**: `http://localhost:8080/api/v1`
- **认证方式**: API Key（可选）
- **请求格式**: JSON
- **响应格式**: JSON
- **字符编码**: UTF-8

## 认证

如果启用了API Key认证，需要在请求头中包含：

```http
X-API-Key: your-api-key-here
```

## 通用响应格式

### 成功响应

```json
{
  "data": {},
  "message": "Success"
}
```

### 错误响应

```json
{
  "detail": "Error message"
}
```

## API端点

### 健康检查

#### GET /health

检查服务健康状态

**请求示例：**

```bash
curl http://localhost:8080/api/v1/health
```

**响应示例：**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "uni-load-improved"
}
```

---

## API源管理

### GET /api-sources

获取所有API源列表

**查询参数：**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| skip | integer | 否 | 跳过记录数，默认0 |
| limit | integer | 否 | 返回记录数，默认100 |

**请求示例：**

```bash
curl http://localhost:8080/api/v1/api-sources?skip=0&limit=10
```

**响应示例：**

```json
[
  {
    "id": "source-001",
    "name": "OpenAI Main",
    "base_url": "https://api.openai.com/v1",
    "enabled": true,
    "model_count": 5,
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-01-15T10:00:00Z"
  }
]
```

### POST /api-sources

创建新的API源

**请求体：**

```json
{
  "name": "OpenAI Main",
  "base_url": "https://api.openai.com/v1",
  "api_key": "sk-xxxxxxxxxxxxx"
}
```

**响应示例：**

```json
{
  "id": "source-001",
  "name": "OpenAI Main",
  "base_url": "https://api.openai.com/v1",
  "enabled": true,
  "model_count": 0,
  "created_at": "2024-01-15T10:00:00Z"
}
```

### PUT /api-sources/{source_id}

更新API源

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| source_id | string | API源ID |

**请求体：**

```json
{
  "name": "OpenAI Main Updated",
  "enabled": true
}
```

### DELETE /api-sources/{source_id}

删除API源

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| source_id | string | API源ID |

**响应示例：**

```json
{
  "message": "API source deleted successfully"
}
```

### POST /api-sources/{source_id}/test

测试API源连接

**响应示例：**

```json
{
  "status": "success",
  "message": "Connection successful",
  "response_time": 150
}
```

### POST /api-sources/{source_id}/refresh

刷新API源的模型列表

**响应示例：**

```json
{
  "message": "Models refreshed successfully",
  "model_count": 5
}
```

---

## 模型管理

### GET /models

获取模型列表

**查询参数：**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| provider_id | string | 否 | 按API源筛选 |
| enabled | boolean | 否 | 按状态筛选 |
| search | string | 否 | 搜索模型名称 |
| skip | integer | 否 | 跳过记录数 |
| limit | integer | 否 | 返回记录数 |

**请求示例：**

```bash
curl "http://localhost:8080/api/v1/models?provider_id=source-001&enabled=true"
```

**响应示例：**

```json
[
  {
    "id": "model-001",
    "original_name": "gpt-4-0125-preview",
    "normalized_name": "gpt-4",
    "display_name": "GPT-4 Turbo",
    "provider_id": "source-001",
    "provider_name": "OpenAI Main",
    "enabled": true,
    "created_at": "2024-01-15T10:00:00Z"
  }
]
```

### GET /models/{model_id}

获取单个模型详情

**响应示例：**

```json
{
  "id": "model-001",
  "original_name": "gpt-4-0125-preview",
  "normalized_name": "gpt-4",
  "display_name": "GPT-4 Turbo",
  "provider_id": "source-001",
  "provider_name": "OpenAI Main",
  "enabled": true,
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z"
}
```

### PUT /models/{model_id}/rename

重命名模型

**请求体：**

```json
{
  "display_name": "GPT-4 Turbo"
}
```

**响应示例：**

```json
{
  "id": "model-001",
  "display_name": "GPT-4 Turbo",
  "message": "Model renamed successfully"
}
```

### POST /models/batch-rename

批量重命名模型

**请求体：**

```json
{
  "renames": [
    {
      "model_id": "model-001",
      "display_name": "GPT-4 Turbo"
    },
    {
      "model_id": "model-002",
      "display_name": "GPT-3.5 Turbo"
    }
  ]
}
```

**响应示例：**

```json
{
  "success_count": 2,
  "failed_count": 0,
  "message": "Batch rename completed"
}
```

### DELETE /models/{model_id}

删除模型（软删除）

**响应示例：**

```json
{
  "message": "Model deleted successfully"
}
```

### POST /models/batch-delete

批量删除模型

**请求体：**

```json
{
  "model_ids": ["model-001", "model-002"]
}
```

**响应示例：**

```json
{
  "success_count": 2,
  "failed_count": 0,
  "message": "Batch delete completed"
}
```

---

## Provider管理

### GET /providers

获取Provider列表

**响应示例：**

```json
[
  {
    "id": "openai-main-0",
    "original_provider_id": "source-001",
    "model": "gpt-4",
    "enabled": true
  }
]
```

### POST /providers/split/{source_id}

拆分API源的Provider

**响应示例：**

```json
{
  "original_provider_id": "source-001",
  "split_providers": [
    {
      "id": "source-001-0",
      "model": "gpt-4"
    },
    {
      "id": "source-001-1",
      "model": "gpt-3.5-turbo"
    }
  ]
}
```

---

## 配置管理

### POST /config/generate

生成配置文件

**响应示例：**

```json
{
  "gpt_load_config": {
    "providers": [...],
    "groups": [...],
    "aggregate_groups": [...],
    "model_redirects": {...}
  },
  "uni_api_config": {
    "providers": [...]
  },
  "statistics": {
    "provider_count": 5,
    "model_count": 10,
    "aggregate_group_count": 3
  }
}
```

### GET /config/preview

预览配置

**查询参数：**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| type | string | 是 | gpt-load 或 uni-api |
| format | string | 否 | yaml 或 json，默认yaml |

**响应示例：**

```yaml
providers:
  - name: openai-main-0
    base_url: https://api.openai.com/v1
    api_key: sk-xxx
    models: [gpt-4]
```

### GET /config/download/{type}

下载配置文件

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| type | string | gpt-load 或 uni-api |

**响应**: 文件下载

### POST /config/apply

应用配置到服务

**响应示例：**

```json
{
  "message": "Configuration applied successfully",
  "gpt_load_status": "reloaded",
  "uni_api_status": "reloaded"
}
```

### GET /config/history

获取配置历史

**响应示例：**

```json
[
  {
    "id": "config-001",
    "created_at": "2024-01-15T10:00:00Z",
    "provider_count": 5,
    "model_count": 10,
    "config_snapshot": {...}
  }
]
```

---

## 健康监控

### POST /health/check-all

检查所有API源的健康状态

**响应示例：**

```json
{
  "total": 5,
  "healthy": 4,
  "unhealthy": 1,
  "results": [
    {
      "provider_id": "source-001",
      "status": "healthy",
      "response_time": 150,
      "checked_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

### GET /health/statistics

获取健康统计信息

**响应示例：**

```json
{
  "total_providers": 5,
  "healthy_providers": 4,
  "unhealthy_providers": 1,
  "average_response_time": 200,
  "uptime_percentage": 80.0
}
```

### GET /health/history/{source_id}

获取API源的健康历史

**响应示例：**

```json
[
  {
    "checked_at": "2024-01-15T10:00:00Z",
    "status": "healthy",
    "response_time": 150
  }
]
```

---

## 错误码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 409 | 资源冲突 |
| 500 | 服务器内部错误 |
| 501 | 功能未实现 |
| 503 | 服务不可用 |

---

## 使用示例

### Python示例

```python
import requests

BASE_URL = "http://localhost:8080/api/v1"
API_KEY = "your-api-key"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# 获取API源列表
response = requests.get(f"{BASE_URL}/api-sources", headers=headers)
sources = response.json()

# 创建API源
data = {
    "name": "OpenAI Main",
    "base_url": "https://api.openai.com/v1",
    "api_key": "sk-xxx"
}
response = requests.post(f"{BASE_URL}/api-sources", json=data, headers=headers)
source = response.json()

# 生成配置
response = requests.post(f"{BASE_URL}/config/generate", headers=headers)
config = response.json()
```

### JavaScript示例

```javascript
const BASE_URL = 'http://localhost:8080/api/v1';
const API_KEY = 'your-api-key';

const headers = {
  'X-API-Key': API_KEY,
  'Content-Type': 'application/json'
};

// 获取API源列表
fetch(`${BASE_URL}/api-sources`, { headers })
  .then(res => res.json())
  .then(sources => console.log(sources));

// 创建API源
fetch(`${BASE_URL}/api-sources`, {
  method: 'POST',
  headers,
  body: JSON.stringify({
    name: 'OpenAI Main',
    base_url: 'https://api.openai.com/v1',
    api_key: 'sk-xxx'
  })
})
  .then(res => res.json())
  .then(source => console.log(source));
```

### cURL示例

```bash
# 获取API源列表
curl -H "X-API-Key: your-api-key" \
  http://localhost:8080/api/v1/api-sources

# 创建API源
curl -X POST \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "OpenAI Main",
    "base_url": "https://api.openai.com/v1",
    "api_key": "sk-xxx"
  }' \
  http://localhost:8080/api/v1/api-sources

# 生成配置
curl -X POST \
  -H "X-API-Key: your-api-key" \
  http://localhost:8080/api/v1/config/generate
```

---

## 交互式API文档

访问 http://localhost:8080/docs 可以查看Swagger UI交互式API文档，支持：

- 查看所有API端点
- 在线测试API
- 查看请求/响应示例
- 下载OpenAPI规范

---

## 更新日志

- **2024-01-15**: 初始版本发布

---

## 反馈

如有API相关问题，请提交 [Issue](https://github.com/your-org/uni-load-improved/issues)