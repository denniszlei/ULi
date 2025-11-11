# Docker快速开始指南

本指南帮助您快速使用Docker部署uni-load-improved项目。

## 🚀 5分钟快速部署

### 步骤1: 安装Docker

确保已安装Docker和Docker Compose：

```bash
# 检查Docker版本
docker --version
docker-compose --version

# 如果未安装，请访问：
# https://docs.docker.com/get-docker/
```

### 步骤2: 克隆项目

```bash
git clone <repository-url>
cd uni-load-improved
```

### 步骤3: 配置环境

```bash
cd docker
cp .env.docker.example .env

# 编辑.env文件（可选）
# 至少修改SECRET_KEY
vim .env
```

### 步骤4: 启动服务

```bash
# 一键启动
docker-compose up -d

# 查看启动日志
docker-compose logs -f
```

### 步骤5: 访问服务

打开浏览器访问：

- **Web UI**: http://localhost:8080
- **gpt-load**: http://localhost:3001
- **uni-api**: http://localhost:8000

## 📋 常用命令

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose stop

# 启动服务
docker-compose start

# 重启服务
docker-compose restart

# 完全删除（包括数据卷）
docker-compose down -v
```

## 🔧 使用部署脚本

项目提供了便捷的部署脚本：

```bash
cd docker
chmod +x deploy.sh

# 部署
./deploy.sh deploy

# 查看状态
./deploy.sh status

# 备份数据
./deploy.sh backup

# 查看日志
./deploy.sh logs
```

## 📚 详细文档

完整的部署文档请查看：[docker/README.md](docker/README.md)

包含：
- 详细配置说明
- 多种部署方式
- 故障排查指南
- 最佳实践
- 运维管理

## ⚠️ 注意事项

1. **生产环境部署**：务必修改`.env`中的`SECRET_KEY`
2. **端口冲突**：确保8080、3001、8000端口未被占用
3. **资源要求**：至少2GB内存和5GB磁盘空间
4. **数据持久化**：数据保存在`docker/data`目录

## 🆘 遇到问题？

1. 查看日志：`docker-compose logs -f`
2. 检查健康状态：`docker-compose exec uni-load-improved /healthcheck.sh`
3. 查看详细文档：[docker/README.md](docker/README.md)
4. 提交Issue：[GitHub Issues](https://github.com/your-org/uni-load-improved/issues)

## 🎯 下一步

- 配置Provider和模型
- 生成gpt-load和uni-api配置
- 查看监控和日志
- 设置自动备份

祝您使用愉快！🎉