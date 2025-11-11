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

### 服务集成配置

```bash
# gpt-load服务URL
# Docker部署时使用容器名称
GPT_LOAD_URL=http://gpt-load:3001

# gpt-load认证密钥（务必修改为强密码）
# 推荐格式: sk-prod-[32位随机字符串]
GPT_LOAD_AUTH_KEY=sk-gptload-change-this-key-to-strong-password

# uni-api服务URL
# Docker部署时使用容器名称
UNI_API_URL=http://uni-api:8000

# 配置文件路径（Docker卷挂载）
CONFIG_DIR=/app/config
```

**重要说明**：
- gpt-load和uni-api使用官方Docker镜像独立部署
- gpt-load配置存储在数据库中，不是通过配置文件
- uni-api配置通过api.yaml文件
- 配置更新后需要重启对应服务才能生效

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
    url: "http://gpt-load:3001"
    auth_key: ""  # gpt-load的AUTH_KEY
    health_check_interval: 300
  
  uni_api:
    url: "http://uni-api:8000"
    config_path: "/app/config/api.yaml"
    health_check_interval: 300

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

**重要说明**：gpt-load使用数据库存储配置，不是通过YAML文件。

### 配置方式

1. **通过Web管理界面**（推荐）
   - 访问 http://localhost:3001
   - 使用AUTH_KEY登录
   - 在界面中配置Provider和分组

2. **通过uni-load-improved**
   - uni-load-improved会生成配置数据
   - 但gpt-load需要通过其管理API或重启来加载

### 配置存储

```bash
# gpt-load配置存储位置
./data/gpt-load/gpt-load.db  # SQLite数据库

# 环境变量配置
PORT=3001
AUTH_KEY=your-auth-key
DATABASE_DSN=  # 留空使用SQLite
```

### 配置更新流程

1. uni-load-improved生成配置
2. 配置保存到文件（供参考）
3. **需要手动重启gpt-load服务**
4. gpt-load从数据库加载配置

```bash
# 重启gpt-load
docker-compose restart gpt-load
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

uni-api配置通过`api.yaml`文件，由uni-load-improved自动生成。

### 配置文件位置

```bash
# Docker部署
./data/config/api.yaml

# 容器内路径
/home/api.yaml  # uni-api容器内的配置文件路径
```

### 配置结构

```yaml
# Provider配置
providers:
  - provider: gptload-gpt-4
    base_url: http://gpt-load:3001/proxy/gpt-4
    api: sk-dummy-key  # uni-api需要一个API key，但实际不使用
    model:
      - gpt-4
  
  - provider: gptload-gpt-3.5-turbo
    base_url: http://gpt-load:3001/proxy/gpt-3.5-turbo
    api: sk-dummy-key
    model:
      - gpt-3.5-turbo

# API密钥配置（可选）
api_keys:
  - api: sk-your-custom-key
    model: ["*"]  # 允许访问所有模型
```

### 配置更新流程

1. uni-load-improved生成api.yaml
2. 文件保存到共享卷
3. **需要重启uni-api服务**
4. uni-api加载新配置

```bash
# 重启uni-api
docker-compose restart uni-api
```

### 环境变量

```bash
# uni-api容器环境变量
TZ=Asia/Shanghai

# 可选：通过URL加载配置
CONFIG_URL=http://your-server/api.yaml
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