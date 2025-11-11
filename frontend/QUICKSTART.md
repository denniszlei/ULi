# uni-load-improved 前端快速开始指南

## 前置要求

- Node.js >= 16.0.0
- npm >= 8.0.0

## 快速开始

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:5173 查看应用

### 3. 构建生产版本

```bash
npm run build
```

构建产物将输出到 `../backend/static` 目录，可直接被后端服务使用。

## 开发流程

### 添加新功能

1. **创建组件**
   ```bash
   # 在 src/components/ 创建新组件
   touch src/components/MyComponent.vue
   ```

2. **添加路由**
   ```javascript
   // src/router/index.js
   {
     path: '/my-page',
     name: 'MyPage',
     component: () => import('../views/MyPage.vue'),
     meta: { title: '我的页面' }
   }
   ```

3. **添加API方法**
   ```javascript
   // src/api/client.js
   export const api = {
     // ... 现有方法
     myNewApi: () => client.get('/my-endpoint')
   }
   ```

### 调试技巧

1. **使用Vue DevTools**
   - 安装浏览器扩展
   - 在开发模式下自动启用

2. **查看网络请求**
   - 打开浏览器开发者工具
   - 切换到Network标签
   - 筛选XHR请求查看API调用

3. **查看控制台日志**
   - API错误会自动显示在控制台
   - 使用console.log进行调试（提交前删除）

## 常用命令

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview

# 代码检查
npm run lint

# 代码格式化
npm run lint -- --fix
```

## 项目结构说明

```
frontend/
├── src/
│   ├── components/      # 可复用组件
│   ├── views/          # 页面视图
│   ├── api/            # API客户端
│   ├── router/         # 路由配置
│   ├── App.vue         # 根组件
│   └── main.js         # 入口文件
├── public/             # 静态资源
├── index.html          # HTML模板
├── package.json        # 项目配置
└── vite.config.js      # Vite配置
```

## 与后端联调

### 开发模式

前端开发服务器会自动将 `/api` 请求代理到后端服务器（默认 http://localhost:8080）

确保后端服务已启动：
```bash
cd ../backend
python main.py
```

### 修改后端地址

编辑 `vite.config.js`：
```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://your-backend-url:port',
      changeOrigin: true
    }
  }
}
```

## 常见问题

### Q: 依赖安装失败
A: 尝试清除缓存后重新安装
```bash
rm -rf node_modules package-lock.json
npm install
```

### Q: 开发服务器启动失败
A: 检查端口5173是否被占用，或修改vite.config.js中的端口配置

### Q: API请求失败
A: 
1. 确认后端服务已启动
2. 检查浏览器控制台的网络请求
3. 确认API路径是否正确

### Q: 页面样式错乱
A: 
1. 清除浏览器缓存
2. 确认Element Plus已正确导入
3. 检查是否有CSS冲突

## 性能优化建议

1. **路由懒加载**
   - 已配置，所有路由组件都使用动态导入

2. **组件按需导入**
   - Element Plus组件已全局注册
   - 自定义组件使用时才导入

3. **生产构建优化**
   - Vite自动进行代码分割
   - 自动压缩和优化资源

## 部署说明

### 开发环境
```bash
npm run dev
```

### 生产环境
```bash
# 构建
npm run build

# 构建产物会输出到 ../backend/static
# 后端服务会自动提供这些静态文件
```

### Docker部署
前端构建已集成到项目的Docker镜像中，无需单独部署。

## 获取帮助

- 查看 [README.md](./README.md) 了解详细文档
- 查看 [架构设计文档](../docs/architecture-design-part2.md)
- 提交Issue到项目仓库

## 下一步

- 熟悉项目结构
- 查看各个组件的实现
- 尝试添加新功能
- 阅读Vue 3和Element Plus文档