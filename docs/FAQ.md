# 常见问题 (FAQ)

本文档收集了uni-load-improved使用过程中的常见问题和解答。

## 目录

- [一般问题](#一般问题)
- [安装和部署](#安装和部署)
- [使用问题](#使用问题)
- [技术问题](#技术问题)
- [故障排查](#故障排查)

---

## 一般问题

### Q: uni-load-improved是什么？

A: uni-load-improved是一个整合型的LLM大模型API网关系统，它可以：
- 统一管理多个API提供商
- 自动生成负载均衡配置
- 实现模型的统一访问和智能调度
- 提供Web界面进行可视化管理

### Q: 与原uni-load有什么区别？

A: 主要区别包括：
- ✅ 模型重命名可配置化（原版硬编码）
- ✅ 支持模型删除功能
- ✅ 提供现代化Web UI
- ✅ Provider自动拆分
- ✅ 配置自动生成
- ✅ 实时健康监控

### Q: 支持哪些API提供商？

A: 支持所有兼容OpenAI API格式的提供商，包括：
- OpenAI
- Azure OpenAI
- Anthropic Claude
- Google Gemini
- 国内各大模型提供商（通义千问、文心一言等）
- 自建的OpenAI兼容API

### Q: 是否免费？

A: 是的，uni-load-improved是开源免费的，采用MIT许可证。

### Q: 需要什么技术背景？

A: 
- **使用者**：基本的命令行操作和Docker知识
- **开发者**：Python、JavaScript/Vue.js、Docker等

---

## 安装和部署

### Q: 如何安装？

A: 推荐使用Docker Compose：

```bash
git clone https://github.com/your-org/uni-load-improved.git
cd uni-load-improved/docker
cp .env.docker.example .env
docker-compose up -d
```

详见[用户指南](USER_GUIDE.md#第二章安装部署)

### Q: 支持哪些操作系统？

A: 支持所有能运行Docker的操作系统：
- Linux (Ubuntu, CentOS, Debian等)
- macOS
- Windows (WSL2)

### Q: 最低硬件要求是什么？

A: 
- **CPU**: 2核心
- **内存**: 2GB
- **磁盘**: 5GB可用空间
- **网络**: 稳定的互联网连接

### Q: 可以不用Docker部署吗？

A: 可以，但不推荐。手动部署需要：
1. 安装Python 3.11+
2. 安装Node.js 16+
3. 配置数据库
4. 配置Web服务器
5. 配置进程管理

详见[用户指南](USER_GUIDE.md#22-手动部署)

### Q: 如何升级到新版本？

A: 

```bash
# 1. 备份数据
./deploy.sh backup

# 2. 拉取最新镜像
docker-compose pull

# 3. 重启服务
docker-compose up -d

# 4. 验证
curl http://localhost:8080/api/v1/health
```

### Q: 端口被占用怎么办？

A: 修改`.env`文件中的端口配置：

```bash
UNI_LOAD_PORT=8888  # 改为其他端口
```

然后重启服务。

---

## 使用问题

### Q: 如何添加API源？

A: 
1. 打开Web UI (http://localhost:8080)
2. 点击"API源管理"
3. 点击"添加API源"
4. 填写名称、Base URL、API Key
5. 点击"测试连接"验证
6. 点击"保存"

### Q: 为什么模型列表为空？

A: 可能的原因：
1. API Key权限不足
2. Base URL不正确
3. 网络连接问题
4. API提供商服务异常

解决方法：
- 检查API Key是否有效
- 确认Base URL格式正确（需包含/v1）
- 点击"刷新模型"按钮重试
- 查看日志获取详细错误信息

### Q: 如何重命名模型？

A: 
1. 进入"模型管理"页面
2. 找到要重命名的模型
3. 点击"重命名"按钮
4. 输入新名称
5. 点击"确定"

也支持批量重命名。

### Q: 删除模型后可以恢复吗？

A: 删除是软删除，模型会被标记为禁用但不会真正删除。如需恢复：
1. 在数据库中将`enabled`字段改为`true`
2. 或重新从API源获取模型列表

### Q: 配置生成失败怎么办？

A: 检查：
1. 是否有启用的模型
2. 数据库连接是否正常
3. 配置目录是否存在
4. 查看日志获取详细错误

### Q: 如何使用生成的配置？

A: 
1. 在"配置管理"页面生成配置
2. 点击"应用配置"自动应用
3. 或下载配置文件手动部署

应用后，通过uni-api访问：

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-4", "messages": [...]}'
```

---

## 技术问题

### Q: 支持哪些数据库？

A: 
- **SQLite** (默认，适合小规模部署)
- **PostgreSQL** (推荐生产环境)
- **MySQL** (支持但不推荐)

### Q: 如何切换到PostgreSQL？

A: 修改`.env`文件：

```bash
DATABASE_URL=postgresql://user:password@postgres:5432/uniload
```

然后重启服务。

### Q: 如何备份数据？

A: 

```bash
# 使用部署脚本
./deploy.sh backup

# 或手动备份
docker cp uni-load-improved:/app/data/uni-load.db ./backup/
```

### Q: 支持多用户吗？

A: 当前版本(1.0.0)不支持，计划在1.2.0版本添加。

### Q: 如何启用HTTPS？

A: 推荐使用Nginx反向代理：

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8080;
    }
}
```

### Q: 如何扩展功能？

A: 
1. Fork项目
2. 添加新功能
3. 提交Pull Request

或等待插件系统（计划在2.0.0版本）。

### Q: API有速率限制吗？

A: 默认限制为60请求/分钟，可在配置文件中修改：

```yaml
security:
  rate_limit:
    enabled: true
    requests_per_minute: 100
```

---

## 故障排查

### Q: 容器无法启动

A: 检查：

```bash
# 查看日志
docker-compose logs uni-load-improved

# 检查端口占用
netstat -tulpn | grep 8080

# 检查配置
docker-compose config
```

### Q: Web UI无法访问

A: 
1. 确认容器正在运行：`docker-compose ps`
2. 检查端口映射是否正确
3. 检查防火墙设置
4. 尝试使用`127.0.0.1`而不是`localhost`

### Q: API请求失败

A: 
1. 检查API源配置是否正确
2. 验证API Key是否有效
3. 查看健康检查状态
4. 检查网络连接

### Q: 性能问题

A: 优化建议：
1. 增加Worker数量
2. 启用缓存
3. 使用PostgreSQL替代SQLite
4. 增加资源限制

```yaml
deploy:
  resources:
    limits:
      cpus: '4'
      memory: 4G
```

### Q: 内存占用过高

A: 
1. 减少Worker数量
2. 清理日志文件
3. 优化数据库查询
4. 重启服务

### Q: 日志在哪里？

A: 

```bash
# 容器日志
docker-compose logs -f

# 应用日志
docker-compose exec uni-load-improved tail -f /app/logs/uni-load.log
```

### Q: 如何重置数据库？

A: 

```bash
# 停止服务
docker-compose down

# 删除数据库
rm data/uni-load.db

# 重新启动
docker-compose up -d

# 数据库会自动初始化
```

### Q: 配置不生效

A: 
1. 确认已重启服务
2. 检查配置文件语法
3. 查看日志错误信息
4. 验证环境变量

### Q: 如何调试？

A: 

```bash
# 启用调试模式
DEBUG=true
LOG_LEVEL=DEBUG

# 重启服务
docker-compose restart

# 查看详细日志
docker-compose logs -f
```

---

## 更多帮助

### 找不到答案？

1. **查看文档**
   - [用户指南](USER_GUIDE.md)
   - [开发文档](DEVELOPMENT.md)
   - [API文档](API.md)
   - [配置文档](CONFIGURATION.md)

2. **搜索Issues**
   - [GitHub Issues](https://github.com/your-org/uni-load-improved/issues)

3. **提问**
   - 创建新的[Issue](https://github.com/your-org/uni-load-improved/issues/new)
   - 参与[Discussions](https://github.com/your-org/uni-load-improved/discussions)

4. **社区支持**
   - 加入讨论组
   - 查看Wiki

---

## 贡献FAQ

如果你发现了新的常见问题，欢迎：
1. 提交Issue
2. 或直接提交PR更新本文档

---

**最后更新**: 2024-01-15