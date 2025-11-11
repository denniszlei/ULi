# uni-load-improved 前端

这是uni-load-improved项目的前端应用，使用Vue 3 + Element Plus构建的现代化管理界面。

## 技术栈

- **Vue 3** - 渐进式JavaScript框架
- **Vue Router** - 官方路由管理器
- **Pinia** - 状态管理
- **Element Plus** - UI组件库
- **Axios** - HTTP客户端
- **Vite** - 构建工具
- **js-yaml** - YAML解析库

## 项目结构

```
frontend/
├── src/
│   ├── components/          # 可复用组件
│   │   ├── Layout.vue              # 布局组件
│   │   ├── ApiSourceForm.vue       # API源表单
│   │   ├── ModelRenameDialog.vue   # 模型重命名对话框
│   │   ├── ProviderStatus.vue      # Provider状态组件
│   │   └── ConfigPreview.vue       # 配置预览组件
│   ├── views/               # 页面视图
│   │   ├── Dashboard.vue           # 仪表盘
│   │   ├── ApiSources.vue          # API源管理
│   │   ├── ModelManagement.vue     # 模型管理
│   │   └── Configuration.vue       # 配置管理
│   ├── api/                 # API客户端
│   │   └── client.js               # HTTP请求封装
│   ├── router/              # 路由配置
│   │   └── index.js
│   ├── App.vue              # 根组件
│   └── main.js              # 入口文件
├── index.html
├── package.json
├── vite.config.js
└── README.md
```

## 功能特性

### 1. 仪表盘 (Dashboard)
- 系统状态概览
- API源、模型、Provider统计
- Provider健康状态监控
- 快速操作入口
- 自动刷新数据

### 2. API源管理 (ApiSources)
- API源列表展示
- 添加/编辑/删除API源
- 测试API连接
- 刷新模型列表
- 模型数量统计

### 3. 模型管理 (ModelManagement)
- 模型列表展示
- 按Provider筛选
- 模型名称搜索
- 单个/批量重命名
- 单个/批量删除
- 显示原始名称、标准化名称、自定义名称

### 4. 配置管理 (Configuration)
- 生成gpt-load配置
- 生成uni-api配置
- 配置预览（YAML/JSON格式）
- 配置下载
- 配置验证
- 配置应用

## 开发指南

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
npm run dev
```

应用将在 http://localhost:5173 启动

### 生产构建

```bash
npm run build
```

构建产物将输出到 `dist` 目录

### 预览生产构建

```bash
npm run preview
```

## API配置

前端通过 `/api/v1` 路径与后端通信。在开发模式下，Vite会将API请求代理到后端服务器。

如需修改后端地址，请编辑 `vite.config.js` 中的代理配置：

```javascript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',  // 后端地址
        changeOrigin: true
      }
    }
  }
})
```

## 组件说明

### Layout.vue
共享布局组件，包含顶部导航栏和主内容区域。所有页面视图都应该包裹在此组件中。

### ApiSourceForm.vue
API源表单组件，支持创建和编辑模式。包含表单验证、连接测试等功能。

**Props:**
- `visible`: 对话框显示状态
- `mode`: 'create' | 'edit'
- `data`: API源数据对象

**Events:**
- `success`: 提交成功
- `cancel`: 取消操作

### ModelRenameDialog.vue
模型重命名对话框组件，用于修改模型的显示名称。

**Props:**
- `visible`: 对话框显示状态
- `modelData`: 模型数据对象

**Events:**
- `success`: 重命名成功
- `cancel`: 取消操作

### ProviderStatus.vue
Provider健康状态组件，显示所有Provider的在线状态、响应时间等信息。

**Props:**
- `autoRefresh`: 是否自动刷新
- `refreshInterval`: 刷新间隔（毫秒）

**Events:**
- `refresh`: 刷新完成

### ConfigPreview.vue
配置预览对话框组件，支持YAML/JSON格式切换、复制、下载等功能。

**Props:**
- `visible`: 对话框显示状态
- `title`: 标题
- `config`: 配置对象或字符串
- `defaultFormat`: 默认格式 'yaml' | 'json'
- `stats`: 统计信息对象

## 样式规范

项目使用Element Plus的默认主题，主色调为蓝色 (#409eff)。

自定义样式遵循以下规范：
- 使用scoped样式避免污染全局
- 间距使用8px的倍数
- 响应式断点：xs(768px), sm(992px), md(1200px), lg(1920px)

## 浏览器支持

- Chrome >= 87
- Firefox >= 78
- Safari >= 14
- Edge >= 88

## 开发注意事项

1. **API调用**: 所有API调用都应通过 `@/api/client.js` 中的封装方法
2. **错误处理**: API错误会自动显示Element Plus的消息提示
3. **加载状态**: 使用loading状态提供用户反馈
4. **确认对话框**: 危险操作（删除等）必须使用确认对话框
5. **响应式设计**: 确保在不同屏幕尺寸下都能正常使用

## 常见问题

### Q: 如何添加新的页面？
A: 
1. 在 `src/views/` 创建新的Vue组件
2. 在 `src/router/index.js` 添加路由配置
3. 在 `Layout.vue` 的导航菜单中添加入口

### Q: 如何调用后端API？
A:
1. 在 `src/api/client.js` 中添加API方法
2. 在组件中导入并调用：`import { api } from '@/api/client'`

### Q: 如何处理表单验证？
A: 使用Element Plus的表单验证规则，参考 `ApiSourceForm.vue` 的实现

## 贡献指南

1. 遵循Vue 3 Composition API风格
2. 使用ESLint进行代码检查
3. 组件应该是可复用和可测试的
4. 提交前确保没有console.log等调试代码

## 许可证

MIT