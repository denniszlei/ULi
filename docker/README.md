# uni-load-improved Docker部署文档

本文档提供uni-load-improved项目的完整Docker部署指南，支持all-in-one容器化部署和独立组件部署。

## 目录

- [快速开始](#快速开始)
- [部署架构](#部署架构)
- [配置说明](#配置说明)
- [部署方式](#部署方式)
- [运维管理](#运维管理)
- [故障排查](#故障排查)
- [最佳实践](#最佳实践)

---

## 快速开始

### 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少2GB可用内存
- 至少5GB可用磁盘空间

### 一键部署

```bash
# 1. 克隆项目
git clone <repository-url>
cd uni-load-improved

# 2. 进入docker目录
cd docker

# 3. 复制环境变量配置
cp .env.docker.example .env

# 4. 编辑配置（可选）
vim .env

# 5. 启动服务
docker-compose up -d

# 6. 查看日志
docker-compose logs -f

# 7. 访问服务
# uni-load-improved Web UI: http://localhost:8080
# gpt-load: http://localhost:3001
# uni-api: http://localhost:8000
```

### 验证部署

```bash
# 检查容器状态
docker-compose ps

# 检查健康状态
docker-compose exec uni-load-improved /healthcheck.sh

# 查看服务日志
docker-compose logs uni-load-improved
```

---

## 部署架构

### All-in-One架构

```
┌─────────────────────────────────────────┐
│     uni-load-improved Container         │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │   Frontend (Vue.js + Nginx)      │  │
│  │   Port: 8080                     │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │   Backend (FastAPI + Python)     │  │
│  │   Port: 8080                     │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │   gpt-load Service               │  │
│  │   Port: 3001                     │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │   uni-api Service                │  │
│  │   Port: 8000                     │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │   SQLite Database                │  │
│  │   /app/data/uni-load.db          │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

### 微服务架构（可选）

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Frontend   │    │   Backend    │    │   gpt-load   │
│   (Nginx)    │───▶│  (FastAPI)   │───▶│              │
│   Port: 80   │    │  Port: 8080  │    │  Port: 3001  │
└──────────────┘    └──────────────┘    └──────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   uni-api    │
                    │  Port: 8000  │
                    └──────────────┘
```

---

## 配置说明

### 环境变量配置

主要配置文件：`.env`

```bash
# 服务模式
GPT_LOAD_MODE=internal    # internal: 容器内运行, external: 外部服务
UNI_API_MODE=internal

# 端口配置
UNI_LOAD_PORT=8080
GPT_LOAD_PORT=3001
UNI_API_PORT=8000

# 数据库
DATABASE_URL=sqlite:////app/data/uni-load.db

# 日志级别
LOG_LEVEL=INFO

# 安全配置
SECRET_KEY=your-secret-key-here
```

### 数据卷配置

```yaml
volumes:
  - ./data/config:/app/config    # 配置文件
  - ./data/db:/app/data          # 数据库
  - ./data/logs:/app/logs        # 日志文件
  - ./data/backups:/app/backups  # 备份文件
```

### 资源限制

```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
    reservations:
      cpus: '0.5'
      memory: 512M
```

---

## 部署方式

### 1. All-in-One部署（推荐）

适用于：单机部署、开发测试环境

```bash
cd docker
docker-compose up -d
```

**优点**：
- 部署简单，一键启动
- 资源占用少
- 配置管理方便

**缺点**：
- 扩展性有限
- 单点故障风险

### 2. 独立后端部署

仅部署后端服务，前端使用CDN或独立部署。

```bash
# 构建后端镜像
docker build -f docker/Dockerfile.backend -t uni-load-backend:latest .

# 运行后端容器
docker run -d \
  --name uni-load-backend \
  -p 8080:8080 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/config:/app/config \
  -e DATABASE_URL=sqlite:////app/data/uni-load.db \
  uni-load-backend:latest
```

### 3. 独立前端部署

使用Nginx部署前端静态文件。

```bash
# 构建前端镜像
docker build -f docker/Dockerfile.frontend -t uni-load-frontend:latest .

# 运行前端容器
docker run -d \
  --name uni-load-frontend \
  -p 80:80 \
  uni-load-frontend:latest
```

### 4. 外部服务集成

连接到外部的gpt-load或uni-api服务。

```bash
# 修改.env配置
GPT_LOAD_MODE=external
GPT_LOAD_URL=http://external-gpt-load:3001

UNI_API_MODE=external
UNI_API_URL=http://external-uni-api:8000

# 启动服务
docker-compose up -d
```

### 5. 多架构构建

支持AMD64和ARM64架构。

```bash
# 使用构建脚本
cd docker
chmod +x build.sh

# 构建多架构镜像
./build.sh -v 1.0.0 -p linux/amd64,linux/arm64

# 构建并推送到仓库
./build.sh -r docker.io/username -v 1.0.0 --push
```

---

## 运维管理

### 使用部署脚本

```bash
cd docker
chmod +x deploy.sh

# 部署服务
./deploy.sh deploy

# 启动服务
./deploy.sh start

# 停止服务
./deploy.sh stop

# 重启服务
./deploy.sh restart

# 查看状态
./deploy.sh status

# 查看日志
./deploy.sh logs

# 备份数据
./deploy.sh backup

# 恢复数据
./deploy.sh restore
```

### 日志管理

```bash
# 查看所有日志
docker-compose logs

# 查看特定服务日志
docker-compose logs uni-load-improved

# 实时跟踪日志
docker-compose logs -f

# 查看最近100行日志
docker-compose logs --tail=100

# 查看容器内日志文件
docker-compose exec uni-load-improved tail -f /app/logs/uni-load.log
```

### 数据备份

#### 自动备份

```bash
# 使用部署脚本备份
./deploy.sh backup
```

#### 手动备份

```bash
# 备份数据库
docker-compose exec uni-load-improved \
  cp /app/data/uni-load.db /app/backups/uni-load-$(date +%Y%m%d).db

# 备份配置
docker-compose exec uni-load-improved \
  tar czf /app/backups/config-$(date +%Y%m%d).tar.gz /app/config

# 导出备份到主机
docker cp uni-load-improved:/app/backups ./backups
```

### 数据恢复

```bash
# 使用部署脚本恢复
./deploy.sh restore

# 手动恢复
docker cp ./backups/uni-load-20240115.db \
  uni-load-improved:/app/data/uni-load.db

docker-compose restart
```

### 更新升级

```bash
# 1. 备份数据
./deploy.sh backup

# 2. 拉取最新镜像
docker-compose pull

# 3. 重启服务
docker-compose up -d

# 4. 验证服务
./deploy.sh status
```

### 配置热重载

```bash
# 修改配置后重新生成
docker-compose exec uni-load-improved \
  python /app/backend/scripts/generate_config.py

# 重载gpt-load配置
docker-compose exec uni-load-improved \
  kill -HUP $(pgrep gpt-load)

# 重载uni-api配置
docker-compose exec uni-load-improved \
  kill -HUP $(pgrep uni-api)
```

---

## 故障排查

### 常见问题

#### 1. 容器无法启动

```bash
# 查看容器日志
docker-compose logs uni-load-improved

# 检查配置文件
docker-compose config

# 检查端口占用
netstat -tulpn | grep -E '8080|3001|8000'
```

#### 2. 健康检查失败

```bash
# 手动执行健康检查
docker-compose exec uni-load-improved /healthcheck.sh

# 检查服务状态
docker-compose exec uni-load-improved ps aux

# 检查端口监听
docker-compose exec uni-load-improved netstat -tulpn
```

#### 3. 数据库连接失败

```bash
# 检查数据库文件
docker-compose exec uni-load-improved ls -lh /app/data/

# 检查数据库权限
docker-compose exec uni-load-improved stat /app/data/uni-load.db

# 重新初始化数据库
docker-compose exec uni-load-improved python /app/scripts/init_db.py
```

#### 4. 服务间通信失败

```bash
# 检查网络
docker network ls
docker network inspect uni-load-network

# 测试服务连通性
docker-compose exec uni-load-improved curl http://localhost:3001/health
docker-compose exec uni-load-improved curl http://localhost:8000/health
```

#### 5. 内存不足

```bash
# 查看容器资源使用
docker stats uni-load-improved

# 调整资源限制
# 编辑 docker-compose.yml 中的 resources 配置
```

### 调试模式

```bash
# 启用调试模式
docker-compose down
docker-compose up

# 或修改.env
DEBUG=true
LOG_LEVEL=DEBUG

docker-compose up -d
```

### 进入容器调试

```bash
# 进入容器shell
docker-compose exec uni-load-improved bash

# 以root用户进入
docker-compose exec -u root uni-load-improved bash

# 查看进程
ps aux

# 查看网络
netstat -tulpn

# 查看文件
ls -lah /app/
```

---

## 最佳实践

### 生产环境部署

1. **使用环境变量管理敏感信息**
   ```bash
   # 不要在代码中硬编码密钥
   SECRET_KEY=${SECRET_KEY}
   API_KEY=${API_KEY}
   ```

2. **配置资源限制**
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '2'
         memory: 2G
   ```

3. **启用健康检查**
   ```yaml
   healthcheck:
     test: ["CMD", "/healthcheck.sh"]
     interval: 30s
     timeout: 10s
     retries: 3
   ```

4. **配置日志轮转**
   ```yaml
   logging:
     driver: "json-file"
     options:
       max-size: "10m"
       max-file: "3"
   ```

5. **使用非root用户运行**
   ```dockerfile
   USER uniload
   ```

### 安全建议

1. **修改默认密钥**
   ```bash
   SECRET_KEY=$(openssl rand -hex 32)
   ```

2. **限制网络访问**
   ```yaml
   networks:
     uni-load-network:
       internal: true
   ```

3. **使用HTTPS**
   ```bash
   # 配置反向代理（Nginx/Traefik）
   # 使用Let's Encrypt证书
   ```

4. **定期更新镜像**
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

5. **备份策略**
   ```bash
   # 每天自动备份
   0 2 * * * /path/to/deploy.sh backup
   ```

### 性能优化

1. **调整Worker数量**
   ```bash
   WORKERS=4  # 根据CPU核心数调整
   ```

2. **启用缓存**
   ```bash
   CACHE_ENABLED=true
   CACHE_TYPE=redis
   ```

3. **数据库优化**
   ```bash
   # 使用PostgreSQL替代SQLite（生产环境）
   DATABASE_URL=postgresql://user:pass@postgres:5432/uniload
   ```

4. **使用CDN**
   ```bash
   # 前端静态资源使用CDN
   ```

### 监控和告警

1. **集成Prometheus**
   ```yaml
   environment:
     - ENABLE_METRICS=true
     - METRICS_PORT=9090
   ```

2. **配置告警**
   ```bash
   # 使用Alertmanager配置告警规则
   ```

3. **日志聚合**
   ```bash
   # 使用ELK或Loki收集日志
   ```

---

## 附录

### 文件结构

```
docker/
├── Dockerfile                          # 主Dockerfile（all-in-one）
├── Dockerfile.backend                  # 后端独立Dockerfile
├── Dockerfile.frontend                 # 前端独立Dockerfile
├── docker-compose.yml                  # Docker Compose配置
├── docker-compose.override.yml.example # 开发环境覆盖配置示例
├── .env.docker.example                 # 环境变量配置示例
├── entrypoint.sh                       # 容器启动脚本
├── healthcheck.sh                      # 健康检查脚本
├── supervisord.conf                    # Supervisor配置
├── nginx.conf                          # Nginx配置（前端）
├── build.sh                            # 构建脚本
├── deploy.sh                           # 部署脚本
└── README.md                           # 本文档
```

### 端口说明

| 服务 | 端口 | 说明 |
|------|------|------|
| uni-load-improved | 8080 | Web UI和API |
| gpt-load | 3001 | gpt-load服务 |
| uni-api | 8000 | uni-api服务 |
| Metrics | 9090 | Prometheus指标（可选） |

### 环境变量完整列表

参考 `.env.docker.example` 文件。

### 相关链接

- [项目主页](https://github.com/your-org/uni-load-improved)
- [架构设计文档](../docs/architecture-design-part2.md)
- [API文档](../docs/api.md)
- [问题反馈](https://github.com/your-org/uni-load-improved/issues)

---

## 支持

如有问题，请：

1. 查看本文档的[故障排查](#故障排查)部分
2. 查看项目[Issues](https://github.com/your-org/uni-load-improved/issues)
3. 提交新的Issue

---

**最后更新**: 2024-01-15
**版本**: 1.0.0