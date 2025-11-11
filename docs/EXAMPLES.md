# uni-load-improved 使用示例

本文档提供实际使用场景的详细示例，帮助你快速上手uni-load-improved。

## 目录

- [示例1：添加OpenAI API](#示例1添加openai-api)
- [示例2：整合多个API提供商](#示例2整合多个api提供商)
- [示例3：自定义模型名称](#示例3自定义模型名称)
- [示例4：负载均衡配置](#示例4负载均衡配置)
- [示例5：健康监控和故障转移](#示例5健康监控和故障转移)
- [示例6：批量操作](#示例6批量操作)

---

## 示例1：添加OpenAI API

### 场景说明

你有一个OpenAI API密钥，想要通过uni-load-improved统一管理和使用。

### 操作步骤

#### 1. 添加API源

打开Web UI，进入"API源管理"页面：

```yaml
名称: OpenAI Official
Base URL: https://api.openai.com/v1
API Key: sk-proj-xxxxxxxxxxxxxxxxxxxxx
```

点击"测试连接"，确认连接成功后保存。

#### 2. 查看模型列表

系统自动获取模型列表，你会看到：

| 原始名称 | 标准化名称 | 自定义名称 |
|---------|-----------|-----------|
| gpt-4-0125-preview | gpt-4 | - |
| gpt-4-turbo-preview | gpt-4-turbo | - |
| gpt-3.5-turbo-0125 | gpt-3.5-turbo | - |
| text-embedding-ada-002 | text-embedding-ada-002 | - |

#### 3. 重命名模型（可选）

如果你想使用更友好的名称：

```
gpt-4 → GPT-4 Turbo
gpt-3.5-turbo → GPT-3.5 Turbo
```

#### 4. 生成配置

进入"配置管理"页面，点击"生成配置"。

生成的gpt-load配置：

```yaml
providers:
  - name: openai-official-0
    base_url: https://api.openai.com/v1
    api_key: sk-proj-xxx
    models: [gpt-4-0125-preview]
  
  - name: openai-official-1
    base_url: https://api.openai.com/v1
    api_key: sk-proj-xxx
    models: [gpt-3.5-turbo-0125]

groups:
  - name: openai-official-0
    providers: [openai-official-0]
    strategy: fixed_priority
  
  - name: openai-official-1
    providers: [openai-official-1]
    strategy: fixed_priority

model_redirects:
  gpt-4: openai-official-0
  gpt-3.5-turbo: openai-official-1
```

#### 5. 应用配置

点击"应用配置"，配置自动应用到gpt-load和uni-api。

#### 6. 使用统一API

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "gpt-4",
    "messages": [
      {"role": "user", "content": "Hello!"}
    ]
  }'
```

### 预期结果

- ✅ 成功添加OpenAI API源
- ✅ 自动获取4个模型
- ✅ 生成负载均衡配置
- ✅ 可以通过统一API访问

---

## 示例2：整合多个API提供商

### 场景说明

你有多个API提供商的账号，想要整合到一起使用，实现负载均衡和故障转移。

### 提供商列表

1. OpenAI Official
2. Azure OpenAI
3. Cloudflare Workers AI

### 操作步骤

#### 1. 添加所有API源

**OpenAI Official:**
```yaml
名称: OpenAI Official
Base URL: https://api.openai.com/v1
API Key: sk-proj-xxx
```

**Azure OpenAI:**
```yaml
名称: Azure OpenAI
Base URL: https://your-resource.openai.azure.com/openai/deployments/your-deployment/v1
API Key: your-azure-key
```

**Cloudflare:**
```yaml
名称: Cloudflare AI
Base URL: https://api.cloudflare.com/client/v4/accounts/xxx/ai/v1
API Key: your-cf-token
```

#### 2. 查看整合后的模型

系统会自动标准化模型名称：

| API源 | 原始名称 | 标准化名称 |
|------|---------|-----------|
| OpenAI | gpt-4-0125-preview | gpt-4 |
| Azure | gpt-4 | gpt-4 |
| Cloudflare | @cf/meta/llama-2-7b | llama-2-7b |

#### 3. 生成聚合配置

系统自动识别相同模型并创建聚合分组：

```yaml
aggregate_groups:
  - name: agg-gpt-4
    groups:
      - openai-official-0
      - azure-openai-0
    strategy: smart_round_robin

model_redirects:
  gpt-4: agg-gpt-4
  llama-2-7b: cloudflare-ai-0
```

#### 4. 测试负载均衡

```python
import openai

openai.api_base = "http://localhost:8000/v1"
openai.api_key = "YOUR_API_KEY"

# 多次请求会自动在OpenAI和Azure之间负载均衡
for i in range(10):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Request {i}"}]
    )
    print(f"Request {i}: {response.choices[0].message.content}")
```

### 预期结果

- ✅ 3个API源全部添加成功
- ✅ gpt-4模型自动聚合
- ✅ 请求自动负载均衡
- ✅ 单个提供商故障不影响服务

---

## 示例3：自定义模型名称

### 场景说明

不同API提供商的模型名称不统一，你想要使用自己的命名规范。

### 原始模型名称

| API源 | 原始名称 |
|------|---------|
| OpenAI | gpt-4-0125-preview |
| Azure | gpt-4-turbo |
| 通义千问 | qwen-turbo |
| 文心一言 | ernie-bot-4 |

### 目标命名

统一使用`provider-model-version`格式：

```
openai-gpt4-turbo
azure-gpt4-turbo
qwen-turbo-latest
ernie-bot4-latest
```

### 操作步骤

#### 1. 批量重命名

在"模型管理"页面：

1. 选择所有OpenAI模型
2. 点击"批量重命名"
3. 应用规则：添加前缀"openai-"

重复以上步骤处理其他提供商。

#### 2. 手动调整

对于特殊情况，手动重命名：

```
gpt-4-0125-preview → openai-gpt4-turbo
qwen-turbo → qwen-turbo-latest
```

#### 3. 生成配置

配置会使用你的自定义名称：

```yaml
model_redirects:
  openai-gpt4-turbo: openai-official-0
  azure-gpt4-turbo: azure-openai-0
  qwen-turbo-latest: qwen-0
  ernie-bot4-latest: ernie-0
```

#### 4. 使用自定义名称

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openai-gpt4-turbo",
    "messages": [...]
  }'
```

### 预期结果

- ✅ 所有模型使用统一命名规范
- ✅ 易于识别和管理
- ✅ 配置清晰明了

---

## 示例4：负载均衡配置

### 场景说明

你有3个OpenAI API密钥，想要实现智能负载均衡，优先使用响应快的API。

### API密钥列表

```
sk-proj-key1-xxx (主要)
sk-proj-key2-xxx (备用1)
sk-proj-key3-xxx (备用2)
```

### 操作步骤

#### 1. 添加3个API源

```yaml
# API源1
名称: OpenAI Main
Base URL: https://api.openai.com/v1
API Key: sk-proj-key1-xxx

# API源2
名称: OpenAI Backup1
Base URL: https://api.openai.com/v1
API Key: sk-proj-key2-xxx

# API源3
名称: OpenAI Backup2
Base URL: https://api.openai.com/v1
API Key: sk-proj-key3-xxx
```

#### 2. 统一模型名称

将所有gpt-4模型重命名为统一的名称，确保它们会被聚合。

#### 3. 生成配置

系统自动创建聚合分组：

```yaml
aggregate_groups:
  - name: agg-gpt-4
    groups:
      - openai-main-0
      - openai-backup1-0
      - openai-backup2-0
    strategy: smart_round_robin
    health_check: true
    fallback: true
```

#### 4. 配置负载均衡策略

编辑生成的配置，调整策略：

```yaml
aggregate_groups:
  - name: agg-gpt-4
    groups:
      - openai-main-0
      - openai-backup1-0
      - openai-backup2-0
    strategy: smart_round_robin  # 智能轮询，考虑响应时间
    weights: [50, 30, 20]  # 权重分配
    health_check: true
    fallback: true
    retry: 3
```

#### 5. 测试负载分布

```python
import openai
import time
from collections import Counter

openai.api_base = "http://localhost:8000/v1"
openai.api_key = "YOUR_API_KEY"

# 发送100个请求，统计分布
results = []
for i in range(100):
    start = time.time()
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hi"}]
    )
    duration = time.time() - start
    results.append(duration)
    
print(f"平均响应时间: {sum(results)/len(results):.2f}秒")
print(f"最快响应: {min(results):.2f}秒")
print(f"最慢响应: {max(results):.2f}秒")
```

### 预期结果

- ✅ 请求自动分配到3个API
- ✅ 响应快的API获得更多请求
- ✅ 单个API故障自动切换
- ✅ 整体响应时间优化

---

## 示例5：健康监控和故障转移

### 场景说明

你想要实时监控API提供商的健康状态，并在故障时自动切换。

### 操作步骤

#### 1. 启用健康检查

在`.env`文件中配置：

```bash
HEALTH_CHECK_ENABLED=true
HEALTH_CHECK_INTERVAL=300  # 5分钟检查一次
HEALTH_CHECK_TIMEOUT=30
HEALTH_CHECK_RETRY=3
```

#### 2. 查看健康状态

在仪表盘页面查看：

```
总Provider数: 5
健康: 4 🟢
异常: 1 🔴
平均响应时间: 250ms
```

#### 3. 配置告警（可选）

编辑`config/config.yaml`：

```yaml
monitoring:
  enabled: true
  alerts:
    - type: email
      recipients: [admin@example.com]
      conditions:
        - unhealthy_count > 2
        - response_time > 5000
```

#### 4. 测试故障转移

模拟API故障：

```bash
# 临时禁用一个API源
curl -X PUT http://localhost:8080/api/v1/api-sources/source-001 \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'
```

发送请求，观察自动切换：

```python
import openai

openai.api_base = "http://localhost:8000/v1"

# 即使一个API故障，请求仍然成功
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Test"}]
)
print("请求成功，自动切换到健康的API")
```

#### 5. 查看健康历史

```bash
curl http://localhost:8080/api/v1/health/history/source-001
```

响应：

```json
[
  {
    "checked_at": "2024-01-15T10:00:00Z",
    "status": "healthy",
    "response_time": 150
  },
  {
    "checked_at": "2024-01-15T10:05:00Z",
    "status": "unhealthy",
    "response_time": null,
    "error": "Connection timeout"
  }
]
```

### 预期结果

- ✅ 实时监控所有API状态
- ✅ 故障自动检测
- ✅ 自动切换到健康的API
- ✅ 告警通知（如果配置）

---

## 示例6：批量操作

### 场景说明

你有100个模型，需要批量处理：删除embedding模型，重命名chat模型。

### 操作步骤

#### 1. 批量删除embedding模型

在"模型管理"页面：

1. 在搜索框输入"embedding"
2. 点击"全选"
3. 点击"批量删除"
4. 确认删除

或使用API：

```bash
curl -X POST http://localhost:8080/api/v1/models/batch-delete \
  -H "Content-Type: application/json" \
  -d '{
    "model_ids": ["model-001", "model-002", "model-003"]
  }'
```

#### 2. 批量重命名chat模型

使用批量重命名功能：

```bash
curl -X POST http://localhost:8080/api/v1/models/batch-rename \
  -H "Content-Type: application/json" \
  -d '{
    "renames": [
      {"model_id": "model-010", "display_name": "gpt-4-turbo"},
      {"model_id": "model-011", "display_name": "gpt-3.5-turbo"},
      {"model_id": "model-012", "display_name": "claude-3-opus"}
    ]
  }'
```

#### 3. 使用Python脚本批量处理

```python
import requests

BASE_URL = "http://localhost:8080/api/v1"

# 获取所有模型
response = requests.get(f"{BASE_URL}/models")
models = response.json()

# 筛选需要重命名的模型
renames = []
for model in models:
    if "gpt" in model["original_name"].lower():
        # 移除日期后缀
        new_name = model["original_name"].split("-")[0:2]
        new_name = "-".join(new_name)
        renames.append({
            "model_id": model["id"],
            "display_name": new_name
        })

# 批量重命名
response = requests.post(
    f"{BASE_URL}/models/batch-rename",
    json={"renames": renames}
)

print(f"成功重命名 {response.json()['success_count']} 个模型")
```

### 预期结果

- ✅ 快速删除不需要的模型
- ✅ 批量重命名节省时间
- ✅ 支持脚本自动化

---

## 更多示例

### 集成到现有项目

```python
# your_app.py
import openai

# 配置使用uni-load-improved
openai.api_base = "http://localhost:8000/v1"
openai.api_key = "YOUR_API_KEY"

def chat(message):
    response = openai.ChatCompletion.create(
        model="gpt-4",  # 使用统一的模型名称
        messages=[{"role": "user", "content": message}]
    )
    return response.choices[0].message.content

# 无需修改其他代码，透明切换
```

### Docker Compose集成

```yaml
version: '3.8'

services:
  your-app:
    image: your-app:latest
    environment:
      - OPENAI_API_BASE=http://uni-load-improved:8000/v1
      - OPENAI_API_KEY=your-key
    depends_on:
      - uni-load-improved
  
  uni-load-improved:
    image: uni-load-improved:latest
    ports:
      - "8080:8080"
      - "8000:8000"
```

---

## 总结

通过以上示例，你应该能够：

- ✅ 添加和管理API源
- ✅ 整合多个提供商
- ✅ 自定义模型名称
- ✅ 配置负载均衡
- ✅ 监控健康状态
- ✅ 批量处理模型

## 需要帮助？

- 查看[用户指南](USER_GUIDE.md)
- 查看[FAQ](FAQ.md)
- 提交[Issue](https://github.com/your-org/uni-load-improved/issues)

---

**最后更新**: 2024-01-15