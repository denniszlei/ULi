# 更新日志

本文档记录uni-load-improved项目的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [未发布]

### 计划中
- 配置历史和回滚功能
- 多用户支持
- 权限管理系统
- 统计分析功能
- 告警通知系统
- 插件系统

## [1.0.0] - 2024-01-15

### 新增
- 🎉 初始版本发布
- ✨ API聚合功能 - 从多个API提供商获取模型列表
- ✨ 模型管理功能 - 重命名、删除、批量操作
- ✨ Provider自动拆分 - 同一Provider的多个模型自动拆分
- ✨ 配置自动生成 - 自动生成gpt-load和uni-api配置
- ✨ 健康监控功能 - 实时监控API提供商状态
- ✨ Web UI界面 - Vue 3 + Element Plus现代化界面
- ✨ Docker部署支持 - 一键部署，支持多架构
- ✨ API密钥加密存储 - 保护敏感信息
- 📝 完整的文档体系 - 用户指南、开发文档、API文档等

### 核心功能

#### API源管理
- 添加、编辑、删除API源
- 测试API连接
- 刷新模型列表
- 查看API源统计信息

#### 模型管理
- 查看所有模型列表
- 按API源筛选模型
- 搜索模型名称
- 单个/批量重命名模型
- 单个/批量删除模型
- 查看模型详情

#### Provider管理
- 自动拆分Provider
- 查看Provider列表
- Provider状态监控

#### 配置管理
- 自动生成gpt-load配置
- 自动生成uni-api配置
- 配置预览（YAML/JSON格式）
- 配置下载
- 配置应用
- 配置验证

#### 健康监控
- 定期健康检查
- 实时状态显示
- 响应时间统计
- 可用性统计
- 健康历史记录

### 技术栈

#### 后端
- Python 3.11+
- FastAPI - Web框架
- SQLAlchemy - ORM
- SQLite - 数据库
- Pydantic - 数据验证
- httpx - HTTP客户端

#### 前端
- Vue 3 - JavaScript框架
- Element Plus - UI组件库
- Vue Router - 路由管理
- Axios - HTTP客户端
- Vite - 构建工具

#### 部署
- Docker - 容器化
- Docker Compose - 容器编排
- Nginx - Web服务器
- Supervisor - 进程管理

### 文档
- README.md - 项目说明
- USER_GUIDE.md - 用户指南
- DEVELOPMENT.md - 开发文档
- API.md - API文档
- CONFIGURATION.md - 配置文档
- FAQ.md - 常见问题
- EXAMPLES.md - 使用示例
- CONTRIBUTING.md - 贡献指南
- CHANGELOG.md - 更新日志

### 架构设计
- 模块化设计
- 服务层分离
- RESTful API
- 异步处理
- 错误处理机制
- 日志系统

### 安全特性
- API密钥加密存储
- 可选的API Key认证
- CORS配置
- 请求限流
- 输入验证

### 性能优化
- 异步HTTP请求
- 数据库连接池
- 缓存机制
- 批量操作支持

## [0.9.0] - 2024-01-10 (Beta)

### 新增
- Beta版本发布
- 基础功能实现
- 核心API开发
- 前端界面原型

### 改进
- 优化数据库结构
- 改进错误处理
- 完善日志系统

### 修复
- 修复模型获取失败的问题
- 修复配置生成错误
- 修复UI显示问题

## [0.5.0] - 2024-01-05 (Alpha)

### 新增
- Alpha版本发布
- 项目初始化
- 基础架构搭建
- 核心功能原型

### 技术选型
- 确定技术栈
- 设计数据库结构
- 规划API接口

## 版本说明

### 版本号格式

版本号格式：`主版本号.次版本号.修订号`

- **主版本号**：不兼容的API修改
- **次版本号**：向下兼容的功能性新增
- **修订号**：向下兼容的问题修正

### 变更类型

- **新增 (Added)**: 新功能
- **改进 (Changed)**: 现有功能的变更
- **弃用 (Deprecated)**: 即将移除的功能
- **移除 (Removed)**: 已移除的功能
- **修复 (Fixed)**: Bug修复
- **安全 (Security)**: 安全相关的修复

## 升级指南

### 从0.9.0升级到1.0.0

1. **备份数据**
   ```bash
   docker-compose exec uni-load-improved \
     cp /app/data/uni-load.db /app/backups/
   ```

2. **拉取最新镜像**
   ```bash
   docker-compose pull
   ```

3. **重启服务**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

4. **验证升级**
   ```bash
   curl http://localhost:8080/api/v1/health
   ```

### 破坏性变更

#### 1.0.0
- 无破坏性变更

## 已知问题

### 1.0.0
- 配置历史功能尚未实现
- 多用户支持尚未实现
- 部分API端点返回501（功能未实现）

## 路线图

### 1.1.0 (计划中)
- [ ] 配置历史和回滚
- [ ] 配置比较功能
- [ ] 批量导入API源
- [ ] 模型标签功能

### 1.2.0 (计划中)
- [ ] 多用户支持
- [ ] 权限管理
- [ ] 用户组功能
- [ ] 操作审计日志

### 2.0.0 (计划中)
- [ ] 插件系统
- [ ] 自定义负载均衡策略
- [ ] 高级统计分析
- [ ] 告警通知系统
- [ ] WebSocket实时更新

## 贡献者

感谢所有为uni-load-improved做出贡献的开发者！

- [@your-name](https://github.com/your-name) - 项目创建者和主要维护者

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 链接

- [项目主页](https://github.com/your-org/uni-load-improved)
- [问题反馈](https://github.com/your-org/uni-load-improved/issues)
- [文档](https://docs.uni-load-improved.com)

---

**注意**: 本项目遵循语义化版本规范。在1.0.0之前的版本可能会有破坏性变更。