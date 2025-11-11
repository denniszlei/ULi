# uni-load-improved 部署方案

本文档提供uni-load-improved的多种部署方案，根据不同场景选择合适的部署方式。

## 目录

- [方案对比](#方案对比)
- [方案A：标准Docker部署（推荐）](#方案a标准docker部署推荐)
- [方案B：独立部署](#方案b独立部署)
- [方案C：仅配置管理](#方案c仅配置管理)
- [方案D：Kubernetes部署](#方案dkubernetes部署)

---

## 方案对比

| 方案 | 适用场景 | 复杂度 | 维护成本 | 推荐度 |
|------|---------|--------|---------|--------|
| 方案A：标准Docker | 生产环境、测试环境 | ⭐⭐ | 低 | ⭐⭐⭐⭐⭐ |
| 方案B：独立部署 | 已有gpt-load/uni-api | ⭐⭐⭐ | 中 | ⭐⭐⭐ |
| 方案C：仅配置管理 | 外部服务集成 | ⭐ | 低 | ⭐⭐⭐⭐ |
| 方案D：Kubernetes | 大规模生产环境 | ⭐⭐⭐⭐⭐ | 高 | ⭐⭐⭐⭐ |

---

## 方案A：标准Docker部署（推荐）

### 架构说明

使用Docker Compose部署三个独立服务：
- **gpt-load**: 官方镜像 `ghcr.io/tbphp/gpt-load:latest`
- **uni-api**: 官方镜像 `yym68686/uni-api:latest`
- **uni-load-improved**: 配置管理界面

### 部署步骤

#### 1. 准备环境

```bash
# 克隆项目
git clone <repository-url>
cd uni-load-improved/docker

# 复制环境变量配置
cp .env.example .env
```

#### 2. 配置环境变量

编辑 `.env` 文件：

```bash
# 端口配置
UNI_LOAD_PORT=8080
GPT_LOAD_PORT=3001
UNI_API_PORT=8000

# gpt-load认证密钥（务必修改）
GPT_LOAD_AUTH_KEY=sk-prod-$(openssl rand -hex 16)

# 安全配置
SECRET_KEY=$(openssl rand -hex 32)
```

#### 3. 启动服务

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

#### 4. 验证部署

```bash
# 检查gpt-load
curl http://localhost:3001/health

# 检查uni-api
curl http://localhost:8000/

# 访问uni-load-improved
# 浏览器打开: http://localhost:8080
```

### 目录结构

```
docker/
├── docker-compose.yml          # Docker Compose配置
├── .env                        # 环境变量
└── data/                       # 数据持久化
    ├── config/                 # 配置文件
    │   └── api.yaml           # uni-api配置
    ├── gpt-load/              # gpt-load数据
    │   └── gpt-load.db        # gpt-load数据库
    ├── uni-api/               # uni-api数据
    ├── db/                    # uni-load-improved数据库
    └── logs/                  # 日志文件
```

### 配置更新流程

```bash
# 1. 在Web UI中修改配置并生成
# 2. 重启服务应用新配置
docker-compose restart gpt-load uni-api

# 3. 验证配置
curl http://localhost:8000/v1/models
```

### 优点

- ✅ 使用官方镜像，稳定可靠
- ✅ 一键部署，简单快速
- ✅ 服务独立，易于维护
- ✅ 数据持久化，安全可靠

### 缺点

- ❌ 需要Docker环境
- ❌ 配置更新需要重启服务

---

## 方案B：独立部署

### 适用场景

- 已有运行中的gpt-load或uni-api服务
- 需要更灵活的部署方式
- 不想使用Docker

### 部署步骤

#### 1. 部署gpt-load

```bash
# 方法1：使用Docker
docker run -d \
  --name gpt-load \
  -p 3001:3001 \
  -e AUTH_KEY=your-auth-key \
  -v ./gpt-load-data:/app/data \
  ghcr.io/tbphp/gpt-load:latest

# 方法2：从源码构建
git clone https://github.com/tbphp/gpt-load.git
cd gpt-load
cp .env.example .env
# 编辑.env配置
make run
```

#### 2. 部署uni-api

```bash
# 方法1：使用Docker
docker run -d \
  --name uni-api \
  -p 8000:8000 \
  -v ./api.yaml:/home/api.yaml \
  yym68686/uni-api:latest

# 方法2：从源码构建
git clone https://github.com/yym68686/uni-api.git
cd uni-api
pip install -r requirements.txt
# 创建api.yaml配置文件
python main.py
```

#### 3. 部署uni-load-improved

```bash
# 后端
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 配置环境变量
export GPT_LOAD_URL=http://localhost:3001
export UNI_API_URL=http://localhost:8000
export GPT_LOAD_AUTH_KEY=your-auth-key

# 启动后端
uvicorn app.main:app --host 0.0.0.0 --port 8080

# 前端
cd frontend
npm install
npm run build
# 部署dist目录到Nginx或其他Web服务器
```

### 配置说明

```bash
# uni-load-improved环境变量
GPT_LOAD_URL=http://localhost:3001
UNI_API_URL=http://localhost:8000
GPT_LOAD_AUTH_KEY=your-gpt-load-auth-key
DATABASE_URL=sqlite:///./data/uni-load.db
```

### 优点

- ✅ 灵活性高
- ✅ 可以使用现有服务
- ✅ 便于调试和开发

### 缺点

- ❌ 部署复杂
- ❌ 需要手动管理多个服务
- ❌ 配置更新需要手动操作

---

## 方案C：仅配置管理

### 适用场景

- 已有完整的gpt-load和uni-api部署
- 只需要配置管理界面
- 外部服务由其他团队维护

### 部署步骤

#### 1. 修改docker-compose.yml

注释掉gpt-load和uni-api服务：

```yaml
version: '3.8'

services:
  # gpt-load:
  #   ...（注释掉）
  
  # uni-api:
  #   ...（注释掉）
  
  uni-load-improved:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    image: uni-load-improved:latest
    container_name: uni-load-improved
    restart: unless-stopped
    ports:
      - "${UNI_LOAD_PORT:-8080}:8080"
    volumes:
      - ./data/config:/app/config
      - ./data/db:/app/data
      - ./data/logs:/app/logs
    environment:
      - GPT_LOAD_URL=http://your-gpt-load-server:3001
      - UNI_API_URL=http://your-uni-api-server:8000
      - GPT_LOAD_AUTH_KEY=your-auth-key
      - DATABASE_URL=sqlite:////app/data/uni-load.db
```

#### 2. 启动服务

```bash
docker-compose up -d uni-load-improved
```

#### 3. 配置工作流

1. 在uni-load-improved Web UI中配置
2. 生成配置文件
3. 下载配置文件
4. 手动复制到外部服务
5. 重启外部服务

```bash
# 示例：更新外部gpt-load配置
scp ./data/config/gpt-load.yaml user@gpt-load-server:/path/to/config/
ssh user@gpt-load-server "systemctl restart gpt-load"

# 示例：更新外部uni-api配置
scp ./data/config/api.yaml user@uni-api-server:/path/to/config/
ssh user@uni-api-server "systemctl restart uni-api"
```

### 优点

- ✅ 轻量级部署
- ✅ 不影响现有服务
- ✅ 配置集中管理

### 缺点

- ❌ 需要手动同步配置
- ❌ 配置应用不自动化
- ❌ 需要访问外部服务器

---

## 方案D：Kubernetes部署

### 适用场景

- 大规模生产环境
- 需要高可用性
- 已有Kubernetes集群

### 部署清单

#### 1. ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: uni-load-config
  namespace: uni-load
data:
  GPT_LOAD_URL: "http://gpt-load-service:3001"
  UNI_API_URL: "http://uni-api-service:8000"
  LOG_LEVEL: "INFO"
```

#### 2. Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: uni-load-secrets
  namespace: uni-load
type: Opaque
stringData:
  GPT_LOAD_AUTH_KEY: "your-auth-key"
  SECRET_KEY: "your-secret-key"
```

#### 3. gpt-load Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gpt-load
  namespace: uni-load
spec:
  replicas: 2
  selector:
    matchLabels:
      app: gpt-load
  template:
    metadata:
      labels:
        app: gpt-load
    spec:
      containers:
      - name: gpt-load
        image: ghcr.io/tbphp/gpt-load:latest
        ports:
        - containerPort: 3001
        env:
        - name: PORT
          value: "3001"
        - name: AUTH_KEY
          valueFrom:
            secretKeyRef:
              name: uni-load-secrets
              key: GPT_LOAD_AUTH_KEY
        volumeMounts:
        - name: data
          mountPath: /app/data
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: gpt-load-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: gpt-load-service
  namespace: uni-load
spec:
  selector:
    app: gpt-load
  ports:
  - port: 3001
    targetPort: 3001
```

#### 4. uni-api Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: uni-api
  namespace: uni-load
spec:
  replicas: 2
  selector:
    matchLabels:
      app: uni-api
  template:
    metadata:
      labels:
        app: uni-api
    spec:
      containers:
      - name: uni-api
        image: yym68686/uni-api:latest
        ports:
        - containerPort: 8000
        volumeMounts:
        - name: config
          mountPath: /home/api.yaml
          subPath: api.yaml
      volumes:
      - name: config
        configMap:
          name: uni-api-config
---
apiVersion: v1
kind: Service
metadata:
  name: uni-api-service
  namespace: uni-load
spec:
  selector:
    app: uni-api
  ports:
  - port: 8000
    targetPort: 8000
```

#### 5. uni-load-improved Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: uni-load-improved
  namespace: uni-load
spec:
  replicas: 2
  selector:
    matchLabels:
      app: uni-load-improved
  template:
    metadata:
      labels:
        app: uni-load-improved
    spec:
      containers:
      - name: uni-load-improved
        image: uni-load-improved:latest
        ports:
        - containerPort: 8080
        envFrom:
        - configMapRef:
            name: uni-load-config
        - secretRef:
            name: uni-load-secrets
        volumeMounts:
        - name: data
          mountPath: /app/data
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: uni-load-improved-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: uni-load-improved-service
  namespace: uni-load
spec:
  type: LoadBalancer
  selector:
    app: uni-load-improved
  ports:
  - port: 80
    targetPort: 8080
```

### 部署命令

```bash
# 创建命名空间
kubectl create namespace uni-load

# 应用配置
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/gpt-load.yaml
kubectl apply -f k8s/uni-api.yaml
kubectl apply -f k8s/uni-load-improved.yaml

# 查看状态
kubectl get pods -n uni-load
kubectl get svc -n uni-load
```

### 优点

- ✅ 高可用性
- ✅ 自动扩缩容
- ✅ 滚动更新
- ✅ 服务发现

### 缺点

- ❌ 部署复杂
- ❌ 需要Kubernetes知识
- ❌ 维护成本高

---

## 配置更新说明

### 重要提示

**gpt-load和uni-api都不支持配置热重载**，配置更新后必须重启服务。

### Docker部署

```bash
# 重启服务
docker-compose restart gpt-load uni-api

# 或单独重启
docker-compose restart gpt-load
docker-compose restart uni-api
```

### Kubernetes部署

```bash
# 滚动重启
kubectl rollout restart deployment/gpt-load -n uni-load
kubectl rollout restart deployment/uni-api -n uni-load

# 查看重启状态
kubectl rollout status deployment/gpt-load -n uni-load
```

### 独立部署

```bash
# systemd服务
systemctl restart gpt-load
systemctl restart uni-api

# Docker容器
docker restart gpt-load
docker restart uni-api
```

---

## 监控和日志

### Docker部署

```bash
# 查看日志
docker-compose logs -f gpt-load
docker-compose logs -f uni-api
docker-compose logs -f uni-load-improved

# 查看资源使用
docker stats
```

### Kubernetes部署

```bash
# 查看日志
kubectl logs -f deployment/gpt-load -n uni-load
kubectl logs -f deployment/uni-api -n uni-load

# 查看资源使用
kubectl top pods -n uni-load
```

---

## 故障排查

### 常见问题

#### 1. 服务无法启动

```bash
# 检查日志
docker-compose logs <service-name>

# 检查配置
docker-compose config

# 检查端口占用
netstat -tulpn | grep -E '8080|3001|8000'
```

#### 2. 配置不生效

```bash
# 确认配置文件已更新
cat ./data/config/api.yaml

# 重启服务
docker-compose restart gpt-load uni-api

# 验证配置
curl http://localhost:8000/v1/models
```

#### 3. 服务间通信失败

```bash
# 检查网络
docker network ls
docker network inspect uni-load-network

# 测试连通性
docker-compose exec uni-load-improved curl http://gpt-load:3001/health
```

---

## 最佳实践

### 1. 安全配置

- ✅ 修改默认密钥
- ✅ 使用强密码
- ✅ 限制网络访问
- ✅ 启用HTTPS

### 2. 性能优化

- ✅ 合理设置资源限制
- ✅ 启用缓存
- ✅ 使用PostgreSQL替代SQLite（生产环境）

### 3. 备份策略

```bash
# 定时备份脚本
#!/bin/bash
BACKUP_DIR="./backups/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# 备份数据库
docker cp gpt-load:/app/data/gpt-load.db $BACKUP_DIR/
docker cp uni-load-improved:/app/data/uni-load.db $BACKUP_DIR/

# 备份配置
docker cp uni-api:/home/api.yaml $BACKUP_DIR/
```

### 4. 监控告警

- 配置Prometheus监控
- 设置告警规则
- 集成日志聚合系统

---

## 总结

| 场景 | 推荐方案 |
|------|---------|
| 快速开始 | 方案A：标准Docker部署 |
| 已有服务 | 方案B：独立部署 或 方案C：仅配置管理 |
| 生产环境 | 方案A：标准Docker部署 |
| 大规模部署 | 方案D：Kubernetes部署 |

选择合适的部署方案，根据实际需求进行调整和优化。

---

**最后更新**: 2024-01-15
**版本**: 1.0.0