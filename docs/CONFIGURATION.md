# uni-load-improved 配置文档

本文档详细说明uni-load-improved的所有配置选项。

## 目录

- [环境变量配置](#环境变量配置)
- [应用配置文件](#应用配置文件)
- [gpt-load配置](#gpt-load配置)
- [uni-api配置](#uni-api配置)
- [配置示例](#配置示例)

---

## 环境变量配置

环境变量通过`.env`文件配置，位于项目根目录。

### 基础配置

```bash
# 应用名称
APP_NAME=uni-load-improved

# 应用版本
VERSION=1.0.0

# 调试模式
DEBUG=false

# 服务监听地址
UNI_LOAD_HOST=0.0.0.0

# 服务监听端口
UNI_LOAD_PORT=8080
```

### 服务模式配置

```bash
# gpt-load服务模式
# internal: 在同一容器内运行
# external: 连接到外部服务
GPT_LOAD_MODE=internal

# gpt-load服务URL（external模式时使用）
GPT_LOAD_URL=http://localhost:3001

# gpt-load配置文件路径
GPT_LOAD_CONFIG_PATH=./config/gpt-load.yaml

# uni-api服务模式
UNI_API_MODE=internal

# uni-api服务URL（external模式时使用）
UNI_API_URL=http://localhost:8000

# uni-api配置文件路径
UNI_API_CONFIG_PATH=./config/uni-api.yaml
```

### 数据库配置

```bash
# 数据库连接URL
# SQLite示例
DATABASE_URL=sqlite:///./data/uni-load.db

# PostgreSQL示例（生产环境推荐）
# DATABASE_URL=postgresql://user:password@localhost:5432/uniload

# MySQL示例
# DATABASE_URL=mysql://user:password@localhost:3306/uniload
```

### 健康检查配置

```bash
# 是否启用健康检查
HEALTH_CHECK_ENABLED=true

# 健康检查间隔（秒）
HEALTH_CHECK_INTERVAL=300

# 健康检查超时（秒）
HEALTH_CHECK_TIMEOUT=30

# 健康检查重试次数
HEALTH_CHECK_RETRY=3
```

### 日志配置

```bash
# 日志级别
# DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# 日志格式
# json, text
LOG_FORMAT=json

# 日志文件路径
LOG_FILE=./logs/uni-load.log
```

### 安全配置

```bash
# API访问密钥（可选）
# 如果设置，所有API请求需要在Header中包含X-API-Key
API_KEY=your-secret-api-key-here

# 加密密钥（用于加密存储的API密钥）
# 生产环境务必修改此值
ENCRYPTION_KEY=your-encryption-key-here-change-in-production

# 生成随机加密密钥的命令：
# openssl rand -hex 32
```

### 性能配置

```bash
# Worker进程数
WORKERS=4

# 最大并发请求数
MAX_CONCURRENT_REQUESTS=100

# 请求超时时间（秒）
REQUEST_TIMEOUT=60
```

### CORS配置

```bash
# 允许的源
# * 表示允许所有源（开发环境）
# 生产环境应指定具体域名
CORS_ORIGINS=*

# 生产环境示例：
# CORS_ORIGINS=https://your-domain.com,https://admin.your-domain.com
```

---

## 应用配置文件

应用配置文件为`config/config.yaml`，提供更详细的配置选项。

### 完整配置示例

```yaml
# uni-load-improved 配置文件
version: "1.0"

# 服务器配置
server:
  host: "0.0.0.0"
  port: 8080
  debug: false
  workers: 4

# 集成服务配置
services:
  gpt_load:
    mode: "internal"  # internal | external
    url: "http://localhost:3001"
    config_path: "/app/config/gpt-load.yaml"
    api_key: ""  # external模式时需要
  
  uni_api:
    mode: "internal"
    url: "http://localhost:8000"
    config_path: "/app/config/uni-api.yaml"
    api_key: ""

# 数据库配置
database:
  url: "sqlite:///./data/uni-load.db"
  pool_size: 5
  max_overflow: 10
  echo: false  # 是否打印SQL语句

# 健康检查配置
health_check:
  enabled: true
  interval: 300  # 秒
  timeout: 30
  retry: 3
  endpoints:
    - "/v1/models"
    - "/v1/chat/completions"

# 模型标准化规则
normalization:
  rules:
    # 移除日期后缀
    - pattern: "-\\d{8}$"
      replacement: ""
    # 移除preview后缀
    - pattern: "-preview$"
      replacement: ""
    # 移除年份后缀
    - pattern: "-\\d{4}$"
      replacement: ""
    # 统一gpt命名
    - pattern: "^gpt-?(\\d+\\.?\\d*)"
      replacement: "gpt-\\1"
  lowercase: true
  remove_special_chars: true

# 日志配置
logging:
  level: "INFO"
  format: "json"
  file: "/app/logs/uni-load.log"
  rotation: "1 day"
  retention: "30 days"
  compression: "gz"

# 安全配置
security:
  encryption_key: "your-encryption-key-here"
  api_key: ""
  rate_limit:
    enabled: true
    requests_per_minute: 60
  cors:
    origins: ["*"]
    methods: ["GET", "POST", "PUT", "DELETE"]
    headers: ["*"]

# 缓存配置
cache:
  enabled: true
  type: "memory"  # memory | redis
  ttl: 300  # 秒
  redis:
    host: "localhost"
    port: 6379
    db: 0
    password: ""

# 性能配置
performance:
  max_concurrent_requests: 100
  request_timeout: 60
  connection_pool_size: 10
  keep_alive_timeout: 5

# 监控配置
monitoring:
  enabled: true
  metrics_port: 9090
  prometheus:
    enabled: true
    path: "/metrics"
```

---

## gpt-load配置

gpt-load配置由系统自动生成，位于`config/gpt-load.yaml`。

### 配置结构

```yaml
# Provider配置
providers:
  - name: openai-main-0
    base_url: https://api.openai.com/v1
    api_key: sk-xxx
    models: [gpt-4]
    enabled: true
    priority: 10
    timeout: 60
    retry: 3

# 普通分组配置
groups:
  - name: openai-main-0
    providers: [openai-main-0]
    strategy: fixed_priority
    health_check: true

# 聚合分组配置
aggregate_groups:
  - name: agg-gpt-4
    groups: [openai-main-0, azure-backup-0]
    strategy: smart_round_robin
    fallback: true
    health_check: true

# 模型重定向配置
model_redirects:
  gpt-4: agg-gpt-4
  gpt-3.5-turbo: agg-gpt-3.5-turbo
```

### 负载均衡策略

| 策略 | 说明 |
|------|------|
| fixed_priority | 固定优先级，按顺序使用 |
| round_robin | 轮询 |
| smart_round_robin | 智能轮询，考虑响应时间 |
| random | 随机选择 |
| least_connections | 最少连接数 |

---

## uni-api配置

uni-api配置由系统自动生成，位于`config/uni-api.yaml`。

### 配置结构

```yaml
# Provider配置
providers:
  - provider: gpt-4
    base_url: http://localhost:3001/proxy/gpt-4
    api: openai
    models: [gpt-4]
    enabled: true
  
  - provider: gpt-3.5-turbo
    base_url: http://localhost:3001/proxy/gpt-3.5-turbo
    api: openai
    models: [gpt-3.5-turbo]
    enabled: true

# API配置
api:
  port: 8000
  bind: "0.0.0.0"
  workers: 4
  log_level: "info"
  timeout: 60

# 认证配置
auth:
  enabled: false
  api_keys: []

# 限流配置
rate_limit:
  enabled: true
  requests_per_minute: 60
  burst: 10
```

---

## 配置示例

### 开发环境配置

```bash
# .env
DEBUG=true
LOG_LEVEL=DEBUG
GPT_LOAD_MODE=internal
UNI_API_MODE=internal
DATABASE_URL=sqlite:///./data/uni-load-dev.db
```

### 生产环境配置

```bash
# .env
DEBUG=false
LOG_LEVEL=INFO
GPT_LOAD_MODE=external
GPT_LOAD_URL=http://gpt-load-service:3001
UNI_API_MODE=external
UNI_API_URL=http://uni-api-service:8000
DATABASE_URL=postgresql://user:password@postgres:5432/uniload
ENCRYPTION_KEY=<生成的随机密钥>
API_KEY=<生成的随机密钥>
CORS_ORIGINS=https://your-domain.com
```

### Docker Compose配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  uni-load-improved:
    image: uni-load-improved:latest
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/uniload
      - GPT_LOAD_MODE=internal
      - UNI_API_MODE=internal
    volumes:
      - ./config:/app/config
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - postgres
  
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=uniload
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## 配置验证

### 验证环境变量

```bash
# 检查环境变量
docker-compose exec uni-load-improved env | grep UNI_LOAD
```

### 验证配置文件

```bash
# 检查配置文件语法
docker-compose exec uni-load-improved \
  python -c "import yaml; yaml.safe_load(open('/app/config/config.yaml'))"
```

### 测试配置

```bash
# 测试健康检查
curl http://localhost:8080/api/v1/health

# 测试API连接
curl http://localhost:8080/api/v1/api-sources
```

---

## 配置最佳实践

### 1. 安全性

- ✅ 修改默认加密密钥
- ✅ 使用强密码
- ✅ 限制CORS源
- ✅ 启用API Key认证
- ❌ 不要在代码中硬编码密钥

### 2. 性能

- ✅ 根据CPU核心数调整Worker数量
- ✅ 启用缓存
- ✅ 使用PostgreSQL替代SQLite（生产环境）
- ✅ 配置合适的超时时间

### 3. 可靠性

- ✅ 启用健康检查
- ✅ 配置重试机制
- ✅ 设置合理的超时时间
- ✅ 启用日志轮转

### 4. 监控

- ✅ 启用Prometheus指标
- ✅ 配置日志聚合
- ✅ 设置告警规则

---

## 故障排查

### 配置不生效

1. 检查配置文件语法
2. 重启服务
3. 查看日志

### 性能问题

1. 增加Worker数量
2. 启用缓存
3. 优化数据库查询

### 连接问题

1. 检查网络配置
2. 验证URL和端口
3. 检查防火墙规则

---

## 参考资源

- [用户指南](USER_GUIDE.md)
- [开发文档](DEVELOPMENT.md)
- [API文档](API.md)

---

## 更新日志

- **2024-01-15**: 初始版本发布