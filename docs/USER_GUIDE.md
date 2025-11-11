
# uni-load-improved 用户指南

欢迎使用 uni-load-improved！本指南将帮助你快速上手并充分利用系统的各项功能。

## 目录

- [第一章：入门](#第一章入门)
- [第二章：安装部署](#第二章安装部署)
- [第三章：基本使用](#第三章基本使用)
- [第四章：高级功能](#第四章高级功能)
- [第五章：最佳实践](#第五章最佳实践)
- [第六章：故障排查](#第六章故障排查)

---

## 第一章：入门

### 1.1 什么是uni-load-improved

uni-load-improved 是一个整合型的LLM大模型API网关系统，它能够：

- **统一管理**多个API提供商（OpenAI、Azure、Claude等）
- **自动生成**负载均衡配置
- **智能调度**请求到不同的API提供商
- **实时监控**API提供商的健康状态

### 1.2 为什么需要这个项目

#### 解决的问题

1. **API分散管理** - 不同的API提供商需要分别管理
2. **配置复杂** - 手动编写负载均衡配置容易出错
3. **缺乏监控** - 难以了解各个API提供商的状态
4. **模型命名不统一** - 不同提供商的模型名称各异

#### 带来的价值

- ✅ 一个界面管理所有API
- ✅ 自动生成配置，减少人工错误
- ✅ 实时健康监控，及时发现问题
- ✅ 统一模型命名，简化使用

### 1.3 基本概念说明

#### API源（API Source）

API源是指一个API提供商的配置，包含：
- **名称**：自定义的显示名称，如"OpenAI Main"
- **Base URL**：API的基础地址，如`https://api.openai.com/v1`
- **API Key**：访问API的密钥

#### 模型（Model）

模型是API提供商提供的AI模型，如GPT-4、Claude-3等。每个模型有：
- **原始名称**：API提供商返回的原始名称
- **标准化名称**：系统自动标准化后的名称
- **自定义名称**：用户可以自定义的显示名称

#### Provider

Provider是gpt-load中的概念，代表一个API提供商的实例。在uni-load-improved中：
- 一个API源可能被拆分为多个Provider
- 每个Provider对应一个模型
- 这样可以实现更精细的负载均衡

#### 聚合分组（Aggregate Group）

当多个Provider提供相同的模型时，系统会自动创建聚合分组：
- 将相同模型的Provider组合在一起
- 实现智能负载均衡
- 提高可用性和性能

---

## 第二章：安装部署

### 2.1 Docker部署（推荐）

#### 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- 2GB+ 可用内存
- 5GB+ 可用磁盘空间

#### 详细步骤

**步骤1：克隆项目**

```bash
git clone https://github.com/your-org/uni-load-improved.git
cd uni-load-improved
```

**步骤2：进入docker目录**

```bash
cd docker
```

**步骤3：配置环境变量**

```bash
# 复制示例配置
cp .env.docker.example .env

# 编辑配置文件
vim .env  # 或使用其他编辑器
```

主要配置项：

```bash
# 服务模式（internal: 容器内运行，external: 外部服务）
GPT_LOAD_MODE=internal
UNI_API_MODE=internal

# 端口配置
UNI_LOAD_PORT=8080
GPT_LOAD_PORT=3001
UNI_API_PORT=8000

# 数据库路径
DATABASE_URL=sqlite:////app/data/uni-load.db

# 加密密钥（生产环境务必修改）
ENCRYPTION_KEY=your-encryption-key-here-change-in-production
```

**步骤4：启动服务**

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

**步骤5：验证部署**

```bash
# 检查健康状态
curl http://localhost:8080/api/v1/health

# 预期响应
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "uni-load-improved"
}
```

**步骤6：访问Web UI**

打开浏览器访问：http://localhost:8080

### 2.2 手动部署

#### 后端部署

```bash
# 1. 创建虚拟环境
cd backend
python -m venv venv

# 2. 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp ../.env.example ../.env
# 编辑.env文件

# 5. 初始化数据库
python ../scripts/init_db.py

# 6. 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

#### 前端部署

```bash
# 1. 安装依赖
cd frontend
npm install

# 2. 构建生产版本
npm run build

# 3. 部署到Web服务器
# 将dist目录内容复制到Nginx或其他Web服务器
```

### 2.3 配置说明

#### 环境变量配置

详细的环境变量说明请参考 [配置文档](CONFIGURATION.md)

#### 数据持久化

Docker部署时，以下目录会被持久化：

```yaml
volumes:
  - ./data/config:/app/config    # 配置文件
  - ./data/db:/app/data          # 数据库
  - ./data/logs:/app/logs        # 日志文件
```

### 2.4 常见问题

#### 端口被占用

如果8080端口被占用，可以修改`.env`文件中的`UNI_LOAD_PORT`：

```bash
UNI_LOAD_PORT=8888
```

然后重启服务：

```bash
docker-compose down
docker-compose up -d
```

#### 容器无法启动

查看详细日志：

```bash
docker-compose logs uni-load-improved
```

检查配置文件：

```bash
docker-compose config
```

#### 数据库初始化失败

手动初始化数据库：

```bash
docker-compose exec uni-load-improved python /app/scripts/init_db.py
```

---

## 第三章：基本使用

### 3.1 添加第一个API源

#### 步骤1：进入API源管理页面

1. 打开Web UI：http://localhost:8080
2. 点击左侧菜单的"API源管理"

#### 步骤2：添加API源

点击"添加API源"按钮，填写以下信息：

```yaml
名称: OpenAI Main
Base URL: https://api.openai.com/v1
API Key: sk-xxxxxxxxxxxxxxxxxxxxx
```

**字段说明：**

- **名称**：自定义名称，用于识别这个API源
- **Base URL**：API的基础地址，必须以`/v1`结尾
- **API Key**：从API提供商获取的密钥

#### 步骤3：测试连接

点击"测试连接"按钮，系统会：
1. 验证Base URL是否可访问
2. 验证API Key是否有效
3. 尝试获取模型列表

如果测试成功，会显示"连接成功"的提示。

#### 步骤4：保存并获取模型

点击"保存"按钮后，系统会自动：
1. 保存API源配置
2. 获取该API源的模型列表
3. 标准化模型名称
4. 显示在模型管理页面

### 3.2 查看和管理模型

#### 查看模型列表

1. 点击左侧菜单的"模型管理"
2. 可以看到所有已获取的模型

模型列表显示：
- **原始名称**：API提供商返回的原始名称
- **标准化名称**：系统自动标准化后的名称
- **自定义名称**：用户设置的显示名称
- **所属API源**：模型来自哪个API源
- **状态**：启用/禁用

#### 筛选模型

使用页面顶部的筛选器：

```
按API源筛选: [选择API源]
按状态筛选: [全部/启用/禁用]
搜索: [输入模型名称]
```

### 3.3 重命名模型

#### 单个重命名

1. 在模型列表中找到要重命名的模型
2. 点击"重命名"按钮
3. 输入新的显示名称
4. 点击"确定"

**示例：**

```
原始名称: gpt-4-0125-preview
标准化名称: gpt-4
自定义名称: GPT-4 Turbo  ← 你可以设置为这个
```

#### 批量重命名

1. 勾选要重命名的多个模型
2. 点击"批量重命名"按钮
3. 使用规则批量设置名称

**批量重命名规则：**

```
规则1：移除日期后缀
gpt-4-0125-preview → gpt-4

规则2：统一命名格式
gpt4 → gpt-4
claude3 → claude-3

规则3：自定义前缀
gpt-4 → openai-gpt-4
```

### 3.4 删除不需要的模型

#### 单个删除

1. 在模型列表中找到要删除的模型
2. 点击"删除"按钮
3. 确认删除

**注意：** 删除是软删除，模型会被标记为禁用，不会从数据库中真正删除。

#### 批量删除

1. 勾选要删除的多个模型
2. 点击"批量删除"按钮
3. 确认删除

**使用场景：**

- 删除不需要的embedding模型
- 删除过时的模型版本
- 删除测试模型

### 3.5 生成配置文件

#### 步骤1：进入配置管理页面

点击左侧菜单的"配置管理"

#### 步骤2：生成配置

点击"生成配置"按钮，系统会自动：

1. **分析模型分布**
   - 统计每个API源的模型数量
   - 识别相同名称的模型

2. **拆分Provider**
   - 将同一API源的多个模型拆分为独立Provider
   - 例如：`openai-main` → `openai-main-0`, `openai-main-1`, `openai-main-2`

3. **创建聚合分组**
   - 将相同模型的Provider组合
   - 例如：`gpt-4` → `agg-gpt-4` (包含多个Provider)

4. **生成配置文件**
   - gpt-load配置：负载均衡规则
   - uni-api配置：统一网关配置

#### 步骤3：预览配置

生成后可以预览配置内容：

**gpt-load配置示例：**

```yaml
providers:
  - name: openai-main-0
    base_url: https://api.openai.com/v1
    api_key: sk-xxx
    models: [gpt-4]
  
  - name: azure-backup-0
    base_url: https://azure.openai.com/v1
    api_key: xxx
    models: [gpt-4]

groups:
  - name: openai-main-0
    providers: [openai-main-0]
    strategy: fixed_priority
  
  - name: azure-backup-0
    providers: [azure-backup-0]
    strategy: fixed_priority

aggregate_groups:
  - name: agg-gpt-4
    groups: [openai-main-0, azure-backup-0]
    strategy: smart_round_robin

model_redirects:
  gpt-4: agg-gpt-4
```

**uni-api配置示例：**

```yaml
providers:
  - provider: gpt-4
    base_url: http://localhost:3001/proxy/gpt-4
    api: openai
    models: [gpt-4]
```

#### 步骤4：下载配置

可以下载配置文件到本地：

- 点击"下载gpt-load配置"
- 点击"下载uni-api配置"

### 3.6 应用配置

#### 自动应用（推荐）

点击"应用配置"按钮，系统会自动：

1. 将配置写入gpt-load和uni-api的配置文件
2. 触发服务重新加载配置
3. 验证配置是否生效

#### 手动应用

如果使用外部的gpt-load和uni-api服务：

1. 下载配置文件
2. 手动复制到对应服务的配置目录
3. 重启服务

```bash
# 重启gpt-load
systemctl restart gpt-load

# 重启uni-api
systemctl restart uni-api
```

### 3.7 使用统一API

配置应用后，就可以通过uni-api访问所有模型了。

#### 基本请求

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

#### Python示例

```python
import openai

openai.api_base = "http://localhost:8000/v1"
openai.api_key = "YOUR_API_KEY"

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)

print(response.choices[0].message.content)
```

#### Node.js示例

```javascript
const OpenAI = require('openai');

const openai = new OpenAI({
  baseURL: 'http://localhost:8000/v1',
  apiKey: 'YOUR_API_KEY'
});

async function main() {
  const completion = await openai.chat.completions.create({
    model: 'gpt-4',
    messages: [
      { role: 'user', content: 'Hello!' }
    ]
  });
  
  console.log(completion.choices[0].message.content);
}

main();
```

---

## 第四章：高级功能

### 4.1 Provider自动拆分原理

#### 为什么需要拆分

假设你有一个OpenAI API源，提供了3个模型：
- gpt-4
- gpt-3.5-turbo
- text-embedding-ada-002

如果不拆分，gpt-load会将这3个模型作为一个Provider，无法实现：
- 针对不同模型的独立负载均衡
- 不同模型使用不同的API Key
- 精细的流量控制

#### 拆分后的效果

系统会自动拆分为3个Provider：

```yaml
openai-main-0:  # gpt-4
  base_url: https://api.openai.com/v1
  api_key: sk-xxx
  models: [gpt-4]

openai-main-1:  # gpt-3.5-turbo
  base_url: https://api.openai.com/v1
  api_key: sk-xxx
  models: [gpt-3.5-turbo]

openai-main-2:  # text-embedding-ada-002
  base_url: https://api.openai.com/v1
  api_key: sk-xxx
  models: [text-embedding-ada-002]
```

#### 聚合分组

如果多个API源都提供gpt-4，系统会创建聚合分组：

```yaml
agg-gpt-4:
  groups:
    - openai-main-0
    - azure-backup-0
    - cloudflare-0
  strategy: smart_round_robin
```

请求`gpt-4`时，会自动在这3个Provider之间负载均衡。

### 4.2 批量操作

#### 批量重命名

**场景1：统一添加前缀**

```
选择多个模型 → 批量重命名 → 添加前缀"openai-"
gpt-4 → openai-gpt-4
gpt-3.5-turbo → openai-gpt-3.5-turbo
```

**场景2：移除版本号**

```
选择多个模型 → 批量重命名 → 移除日期后缀
gpt-4-0125-preview → gpt-4
gpt-4-1106-preview → gpt-4
```

**场景3：统一命名格式**

```
选择多个模型 → 批量重命名 → 应用规则
gpt4 → gpt-4
claude3 → claude-3
gemini-pro → gemini-pro
```

#### 批量删除

**场景1：删除embedding模型**

```
筛选：模型名称包含"embedding"
选择所有 → 批量删除
```

**场景2：删除旧版本模型**

```
筛选：模型名称包含日期
选择所有 → 批量删除
```

### 4.3 健康监控

#### 查看健康状态

在仪表盘页面可以看到：

- **在线Provider数量**
- **离线Provider数量**
- **平均响应时间**
- **最近24小时的可用性**

#### 健康检查机制

系统会定期（默认5分钟）检查每个API源：

1. 发送测试请求到`/v1/models`端点
2. 记录响应时间
3. 更新健康状态

**健康状态：**

- 🟢 **健康**：响应时间 < 2秒
- 🟡 **警告**：响应时间 2-5秒
- 🔴 **异常**：响应时间 > 5秒或请求失败

#### 自动禁用

如果某个Provider连续3次健康检查失败，系统会：

1. 自动禁用该Provider
2. 从负载均衡中移除
3. 发送告警通知（如果配置了）

#### 手动健康检查

在API源管理页面，点击"健康检查"按钮可以立即检查。

### 4.4 配置历史和回滚

#### 查看配置历史

在配置管理页面，点击"配置历史"可以看到：

- 配置生成时间
- 配置内容快照
- Provider数量
- 模型数量

#### 回滚配置

如果新配置有问题，可以回滚到之前的版本：

1. 在配置历史中选择要回滚的版本
2. 点击"回滚"按钮
3. 确认回滚

系统会：
1. 恢复之前的配置
2. 重新应用到gpt-load和uni-api
3. 验证配置是否生效

### 4.5 外部服务集成

#### 使用外部gpt-load

如果你已经有运行中的gpt-load服务：

1. 修改`.env`配置：

```bash
GPT_LOAD_MODE=external
GPT_LOAD_URL=http://your-gpt-load-server:3001
```

2. 重启uni-load-improved

3. 生成配置时，系统会通过API推送配置到外部服务

#### 使用外部uni-api

类似地，配置外部uni-api：

```bash
UNI_API_MODE=external
UNI_API_URL=http://your-uni-api-server:8000
```

#### API认证

如果外部服务需要认证，在`.env`中配置：

```bash
GPT_LOAD_API_KEY=your-gpt-load-api-key
UNI_API_API_KEY=your-uni-api-api-key
```

---

## 第五章：最佳实践

### 5.1 模型命名建议

#### 统一命名规范

建议使用以下命名规范：

```
格式：<提供商>-<模型系列>-<版本>

示例：
openai-gpt-4
openai-gpt-3.5-turbo
anthropic-claude-3-opus
google-gemini-pro
```

#### 避免的命名

❌ 不推荐：
- 包含日期：`gpt-4-0125-preview`
- 包含特殊字符：`gpt-4@latest`
- 过长的名称：`openai-gpt-4-turbo-preview-with-vision`

✅ 推荐：
- 简洁明了：`gpt-4`
- 有意义的后缀：`gpt-4-turbo`
- 统一格式：`claude-3-opus`

### 5.2 性能优化建议

#### 1. 合理设置健康检查间隔

```bash
# 生产环境：5-10分钟
HEALTH_CHECK_INTERVAL=300

# 开发环境：1-2分钟
HEALTH_CHECK_INTERVAL=60
```

#### 2. 使用缓存

系统会自动缓存模型列表，避免频繁请求API。

#### 3. 配置合适的超时时间

```bash
# 请求超时（秒）
REQUEST_TIMEOUT=60

# 健康检查超时（秒）
HEALTH_CHECK_TIMEOUT=30
```

#### 4. 限制并发请求

```bash
# 最大并发请求数
MAX_CONCURRENT_REQUESTS=100
```

### 5.3 安全配置建议

#### 1. 修改默认加密密钥

```bash
# 生成随机密钥
openssl rand -hex 32

# 在.env中配置
ENCRYPTION_KEY=生成的随机密钥
```

#### 2. 使用HTTPS

在生产环境中，建议使用Nginx反向代理并配置HTTPS：

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 3. 限制访问IP

```nginx
location / {
    allow 192.168.1.0/24;
    deny all;
    proxy_pass http://localhost:8080;
}
```

#### 4. 启用API密钥认证

```bash
# 在.env中配置
API_KEY=your-secret-api-key
```

然后在请求时带上密钥：

```bash
curl -H "X-API-Key: your-secret-api-key" \
  http://localhost:8080/api/v1/api-sources
```

### 5.4 备份和恢复

#### 备份数据

```bash
# 备份数据库
docker-compose exec uni-load-improved \
  cp /app/data/uni-load.db /app/backups/uni-load-$(date +%Y%m%d).db

# 备份配置
docker-compose exec uni-load-improved \
  tar czf /app/backups/config-$(date +%Y%m%d).tar.gz /app/config

# 导出到主机
docker cp uni-load-improved:/app/backups ./backups
```

#### 自动备份

创建定时任务：

```bash
# 编辑crontab
crontab -e

# 添加每天凌晨2点备份
0 2 * * * /path/to/backup.sh
```

备份脚本示例：

```bash
#!/bin/bash
cd /path/to/uni-load-improved/docker
./deploy.sh backup
```

#### 恢复数据

```bash
# 停止服务
docker-compose down

# 恢复数据库
docker cp ./backups/uni-load-20240115.db \
  uni-load-improved:/app/data/uni-load.db

# 恢复配置
docker cp ./backups/config-20240115.tar.gz \
  uni-load-improved:/tmp/
docker-compose exec uni-load-improved \
  tar xzf /tmp/config-20240115.tar.gz -C /

# 启动服务
docker-compose up -d
```

---

## 第六章：故障排查

### 6.1 常见问题和解决方案

#### 问题1：无法添加API源

**症状：**
- 点击"保存"后提示"连接失败"
- 测试连接超时

**可能原因：**
1. Base URL不正确
2. API Key无效
3. 网络连接问题
4. API提供商服务异常

**解决方案：**

```bash
# 1. 检查Base URL格式
# 正确：https://api.openai.com/v1
# 错误：https://api.openai.com（缺少/v1）

# 2. 验证API Key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"

# 3. 检查网络连接
ping api.openai.com

# 4. 查看容器日志
docker-compose logs uni-load-improved
```

#### 问题2：模型列表为空

**症状：**
- 添加API源成功，但模型列表为空

**可能原因：**
1. API Key权限不足
2. API提供商没有可用模型
3. 获取模型列表失败

**解决方案：**

```bash
# 1. 手动刷新模型列表
# 在API源管理页面点击"刷新模型"按钮

# 2. 检查API Key权限
# 确保API Key有访问模型列表的权限

# 3. 查看详细日志
docker-compose logs -f uni-load-improved | grep "fetch_models"
```

#### 问题3：配置生成失败

**症状：**
- 点击"生成配置"后提示错误

**可能原因：**
1. 没有启用的模型
2. 数据库连接失败
3. 配置文件路径不存在

**解决方案：**

```bash
# 1. 检查是否有启用的模型
# 在模型管理页面确认至少有一个启用的模型

# 2. 检查数据库
docker-compose exec uni-load-improved \
  ls -lh /app/data/uni-load.db

# 3. 检查配置目录
docker-compose exec uni-load-improved \
  ls -lh /app/config/

# 4. 手动创建配置目录
docker-compose exec uni-load-improved \
  mkdir -p /app/config
```

#### 问题4：应用配置失败

**症状：**
- 配置生成成功，但应用失败

**可能原因：**
1. gpt-load或uni-api服务未运行
2. 配置文件权限问题
3. 配置格式错误

**解决方案：**

```bash
# 1. 检查服务状态
docker-compose ps

# 2. 检查配置文件权限
docker-compose exec uni-load-improved \
  ls -lh /app/config/

# 3. 手动验证配置
docker-compose exec uni-load-improved \
  cat /app/config/gpt-load.yaml

# 4. 手动重启服务
docker-compose restart
```

### 6.2 日志查看

#### 查看所有日志

```bash
# 实时查看所有日志
docker-compose logs -f

# 查看最近100行
docker-compose logs --tail=100

# 查看特定服务的日志
docker
-compose logs uni-load-improved
```

#### 查看应用日志文件

```bash
# 进入容器
docker-compose exec uni-load-improved bash

# 查看应用日志
tail -f /app/logs/uni-load.log

# 搜索错误
grep ERROR /app/logs/uni-load.log

# 搜索特定关键词
grep "fetch_models" /app/logs/uni-load.log
```

#### 日志级别

可以在`.env`中调整日志级别：

```bash
# DEBUG: 详细调试信息
# INFO: 一般信息（默认）
# WARNING: 警告信息
# ERROR: 错误信息
LOG_LEVEL=DEBUG
```

### 6.3 调试技巧

#### 启用调试模式

```bash
# 修改.env
DEBUG=true
LOG_LEVEL=DEBUG

# 重启服务
docker-compose restart
```

#### 使用浏览器开发者工具

1. 打开Web UI
2. 按F12打开开发者工具
3. 切换到"Network"标签
4. 执行操作，查看API请求和响应

#### 直接测试API

```bash
# 测试健康检查
curl http://localhost:8080/api/v1/health

# 测试获取API源列表
curl http://localhost:8080/api/v1/api-sources

# 测试获取模型列表
curl http://localhost:8080/api/v1/models
```

#### 检查数据库

```bash
# 进入容器
docker-compose exec uni-load-improved bash

# 使用sqlite3查看数据库
sqlite3 /app/data/uni-load.db

# 查看表结构
.schema

# 查看API源
SELECT * FROM api_sources;

# 查看模型
SELECT * FROM models;

# 退出
.quit
```

### 6.4 性能问题

#### 响应慢

**可能原因：**
1. 数据库查询慢
2. 外部API响应慢
3. 资源不足

**解决方案：**

```bash
# 1. 检查资源使用
docker stats uni-load-improved

# 2. 增加资源限制
# 编辑docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G

# 3. 优化数据库
docker-compose exec uni-load-improved \
  sqlite3 /app/data/uni-load.db "VACUUM;"
```

#### 内存占用高

```bash
# 1. 检查内存使用
docker stats uni-load-improved

# 2. 减少Worker数量
# 修改.env
WORKERS=2

# 3. 重启服务
docker-compose restart
```

### 6.5 获取帮助

如果以上方法都无法解决问题：

1. **查看文档**
   - [FAQ常见问题](FAQ.md)
   - [配置文档](CONFIGURATION.md)
   - [开发文档](DEVELOPMENT.md)

2. **搜索Issues**
   - 访问 [GitHub Issues](https://github.com/your-org/uni-load-improved/issues)
   - 搜索类似问题

3. **提交Issue**
   - 描述问题现象
   - 提供错误日志
   - 说明环境信息（操作系统、Docker版本等）
   - 提供复现步骤

4. **社区支持**
   - 加入讨论组
   - 查看Wiki文档

---

## 附录

### A. 快捷键

Web UI支持以下快捷键：

| 快捷键 | 功能 |
|--------|------|
| `Ctrl + K` | 全局搜索 |
| `Ctrl + R` | 刷新当前页面 |
| `Ctrl + S` | 保存当前表单 |
| `Esc` | 关闭对话框 |

### B. API端点速查

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/health` | GET | 健康检查 |
| `/api/v1/api-sources` | GET | 获取API源列表 |
| `/api/v1/api-sources` | POST | 创建API源 |
| `/api/v1/models` | GET | 获取模型列表 |
| `/api/v1/models/{id}/rename` | PUT | 重命名模型 |
| `/api/v1/config/generate` | POST | 生成配置 |

详细API文档请参考 [API文档](API.md)

### C. 配置文件位置

| 文件 | 路径 | 说明 |
|------|------|------|
| 环境变量 | `.env` | 环境配置 |
| 应用配置 | `config/config.yaml` | 应用配置 |
| gpt-load配置 | `config/gpt-load.yaml` | 负载均衡配置 |
| uni-api配置 | `config/uni-api.yaml` | 网关配置 |
| 数据库 | `data/uni-load.db` | SQLite数据库 |
| 日志 | `logs/uni-load.log` | 应用日志 |

### D. 术语表

| 术语 | 说明 |
|------|------|
| API源 | API提供商的配置信息 |
| Provider | gpt-load中的API提供商实例 |
| 模型 | AI模型，如GPT-4、Claude-3 |
| 标准化 | 将模型名称转换为统一格式 |
| 聚合分组 | 将多个Provider组合的负载均衡组 |
| 健康检查 | 定期检查API提供商的可用性 |

### E. 版本兼容性

| 组件 | 最低版本 | 推荐版本 |
|------|---------|---------|
| Docker | 20.10 | 24.0+ |
| Docker Compose | 2.0 | 2.20+ |
| Python | 3.11 | 3.11+ |
| Node.js | 16.0 | 18.0+ |
| gpt-load | 1.0 | 最新版 |
| uni-api | 1.0 | 最新版 |

---

## 更新日志

- **2024-01-15**: 初始版本发布
- 更多更新请查看 [CHANGELOG.md](../CHANGELOG.md)

---

## 反馈

如果你在使用过程中遇到问题或有改进建议，欢迎：

- 提交 [Issue](https://github.com/your-org/uni-load-improved/issues)
- 发起 [Pull Request](https://github.com/your-org/uni-load-improved/pulls)
- 参与 [讨论](https://github.com/your-org/uni-load-improved/discussions)

感谢你使用 uni-load-improved！