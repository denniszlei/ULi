# 贡献指南

感谢你考虑为uni-load-improved做出贡献！本文档将指导你如何参与项目开发。

## 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [开发流程](#开发流程)
- [代码规范](#代码规范)
- [提交规范](#提交规范)
- [Pull Request流程](#pull-request流程)
- [问题反馈](#问题反馈)

---

## 行为准则

### 我们的承诺

为了营造一个开放和友好的环境，我们承诺：

- 使用友好和包容的语言
- 尊重不同的观点和经验
- 优雅地接受建设性批评
- 关注对社区最有利的事情
- 对其他社区成员表示同理心

### 不可接受的行为

- 使用性化的语言或图像
- 人身攻击或侮辱性评论
- 公开或私下骚扰
- 未经许可发布他人的私人信息
- 其他不道德或不专业的行为

---

## 如何贡献

### 报告Bug

如果你发现了Bug，请：

1. **检查是否已存在** - 在[Issues](https://github.com/your-org/uni-load-improved/issues)中搜索类似问题
2. **创建新Issue** - 如果没有找到，创建新的Issue
3. **提供详细信息** - 包括以下内容：
   - Bug的清晰描述
   - 复现步骤
   - 预期行为
   - 实际行为
   - 截图（如果适用）
   - 环境信息（操作系统、Docker版本等）

**Bug报告模板：**

```markdown
**描述Bug**
简要描述Bug是什么。

**复现步骤**
1. 进入 '...'
2. 点击 '....'
3. 滚动到 '....'
4. 看到错误

**预期行为**
描述你期望发生什么。

**实际行为**
描述实际发生了什么。

**截图**
如果适用，添加截图帮助解释问题。

**环境信息：**
 - 操作系统: [例如 Ubuntu 22.04]
 - Docker版本: [例如 24.0.0]
 - 浏览器: [例如 Chrome 120]
 - 项目版本: [例如 1.0.0]

**附加信息**
添加任何其他相关信息。
```

### 提出新功能

如果你有新功能的想法：

1. **检查是否已存在** - 搜索现有的Feature Request
2. **创建Feature Request** - 详细描述你的想法
3. **讨论可行性** - 等待维护者和社区的反馈

**功能请求模板：**

```markdown
**功能描述**
清晰简洁地描述你想要的功能。

**问题背景**
描述这个功能要解决什么问题。例如：我总是感到沮丧当 [...]

**期望的解决方案**
描述你希望如何实现这个功能。

**替代方案**
描述你考虑过的其他替代方案。

**附加信息**
添加任何其他相关信息或截图。
```

### 改进文档

文档改进同样重要！你可以：

- 修正拼写或语法错误
- 改进现有文档的清晰度
- 添加缺失的文档
- 翻译文档到其他语言

---

## 开发流程

### 1. Fork项目

点击GitHub页面右上角的"Fork"按钮。

### 2. 克隆你的Fork

```bash
git clone https://github.com/your-username/uni-load-improved.git
cd uni-load-improved
```

### 3. 添加上游仓库

```bash
git remote add upstream https://github.com/your-org/uni-load-improved.git
```

### 4. 创建分支

```bash
# 从main分支创建新分支
git checkout -b feature/your-feature-name

# 或修复bug
git checkout -b fix/your-bug-fix
```

分支命名规范：
- `feature/` - 新功能
- `fix/` - Bug修复
- `docs/` - 文档更新
- `refactor/` - 代码重构
- `test/` - 测试相关
- `chore/` - 构建/工具相关

### 5. 设置开发环境

参考[开发文档](docs/DEVELOPMENT.md)设置开发环境。

### 6. 进行开发

- 编写代码
- 添加测试
- 更新文档
- 遵循代码规范

### 7. 提交更改

```bash
git add .
git commit -m "feat: add amazing feature"
```

### 8. 保持同步

```bash
# 获取上游更新
git fetch upstream

# 合并到你的分支
git rebase upstream/main
```

### 9. 推送到你的Fork

```bash
git push origin feature/your-feature-name
```

### 10. 创建Pull Request

在GitHub上创建Pull Request。

---

## 代码规范

### Python代码规范

遵循[PEP 8](https://pep8.org/)规范：

```python
# 好的示例
def get_api_sources(skip: int = 0, limit: int = 100) -> List[ApiSource]:
    """
    获取API源列表
    
    Args:
        skip: 跳过的记录数
        limit: 返回的记录数
    
    Returns:
        API源列表
    """
    pass

# 不好的示例
def getApiSources(s=0,l=100):
    pass
```

**代码检查工具：**

```bash
# 安装工具
pip install black flake8 mypy

# 格式化代码
black backend/

# 检查代码风格
flake8 backend/

# 类型检查
mypy backend/
```

### JavaScript代码规范

遵循[Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)：

```javascript
// 好的示例
async function fetchApiSources() {
  try {
    const response = await api.get('/api-sources')
    return response.data
  } catch (error) {
    console.error('Failed to fetch API sources:', error)
    throw error
  }
}

// 不好的示例
function fetchApiSources() {
  return api.get('/api-sources').then(r => r.data)
}
```

**代码检查工具：**

```bash
# 安装工具
npm install --save-dev eslint prettier

# 检查代码
npm run lint

# 格式化代码
npm run format
```

### Vue组件规范

```vue
<!-- 好的示例 -->
<template>
  <div class="api-source-form">
    <el-form :model="form" :rules="rules">
      <el-form-item label="名称" prop="name">
        <el-input v-model="form.name" />
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

const form = reactive({
  name: ''
})

const rules = {
  name: [
    { required: true, message: '请输入名称', trigger: 'blur' }
  ]
}
</script>

<style scoped>
.api-source-form {
  padding: 20px;
}
</style>
```

---

## 提交规范

### Commit Message格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type类型

| Type | 说明 |
|------|------|
| feat | 新功能 |
| fix | Bug修复 |
| docs | 文档更新 |
| style | 代码格式（不影响代码运行） |
| refactor | 重构 |
| perf | 性能优化 |
| test | 测试相关 |
| chore | 构建/工具相关 |
| revert | 回滚 |

### Scope范围

| Scope | 说明 |
|-------|------|
| api | API相关 |
| ui | UI相关 |
| db | 数据库相关 |
| config | 配置相关 |
| docs | 文档相关 |

### 示例

```bash
# 新功能
git commit -m "feat(api): add model batch rename endpoint"

# Bug修复
git commit -m "fix(ui): fix pagination issue in model list"

# 文档更新
git commit -m "docs: update API documentation"

# 重构
git commit -m "refactor(service): simplify config generation logic"

# 性能优化
git commit -m "perf(db): optimize model query performance"
```

---

## Pull Request流程

### 1. 创建PR

- 填写PR模板
- 提供清晰的标题和描述
- 关联相关Issue
- 添加适当的标签

**PR模板：**

```markdown
## 变更类型
- [ ] Bug修复
- [ ] 新功能
- [ ] 文档更新
- [ ] 代码重构
- [ ] 性能优化
- [ ] 其他

## 变更描述
简要描述你的变更。

## 相关Issue
Closes #123

## 测试
描述你如何测试这些变更。

## 截图
如果适用，添加截图。

## 检查清单
- [ ] 代码遵循项目规范
- [ ] 已添加测试
- [ ] 所有测试通过
- [ ] 已更新文档
- [ ] 提交消息遵循规范
```

### 2. 代码审查

- 等待维护者审查
- 根据反馈进行修改
- 保持沟通

### 3. 合并

- 审查通过后，维护者会合并你的PR
- 你的贡献将出现在下一个版本中

---

## 问题反馈

### 提问前

1. 阅读[文档](docs/)
2. 搜索[已有Issues](https://github.com/your-org/uni-load-improved/issues)
3. 查看[FAQ](docs/FAQ.md)

### 提问时

- 使用清晰的标题
- 提供详细的上下文
- 包含相关的代码片段
- 说明你已经尝试过的方法

---

## 开发技巧

### 调试

```bash
# 后端调试
cd backend
python -m pdb app/main.py

# 前端调试
cd frontend
npm run dev
# 然后在浏览器中使用Vue DevTools
```

### 测试

```bash
# 运行后端测试
cd backend
pytest

# 运行前端测试
cd frontend
npm run test
```

### 文档预览

```bash
# 使用Markdown预览工具
# VS Code: Ctrl+Shift+V
# 或使用在线工具如 https://dillinger.io/
```

---

## 获取帮助

如果你需要帮助：

1. **查看文档** - [docs/](docs/)
2. **搜索Issues** - 可能已有答案
3. **提问** - 创建新Issue
4. **讨论** - 参与[Discussions](https://github.com/your-org/uni-load-improved/discussions)

---

## 致谢

感谢所有贡献者！你们的贡献让uni-load-improved变得更好。

### 贡献者列表

查看[贡献者页面](https://github.com/your-org/uni-load-improved/graphs/contributors)

---

## 许可证

通过贡献代码，你同意你的贡献将在[MIT许可证](LICENSE)下发布。

---

**再次感谢你的贡献！** 🎉