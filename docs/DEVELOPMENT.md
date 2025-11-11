
# uni-load-improved 开发文档

本文档面向希望参与uni-load-improved项目开发的开发者，提供完整的开发环境搭建、代码结构、开发规范等信息。

## 目录

- [开发环境搭建](#开发环境搭建)
- [项目结构](#项目结构)
- [后端开发](#后端开发)
- [前端开发](#前端开发)
- [测试](#测试)
- [代码规范](#代码规范)
- [构建和部署](#构建和部署)
- [调试技巧](#调试技巧)

---

## 开发环境搭建

### 前置要求

#### 必需软件

- **Python 3.11+** - 后端开发语言
- **Node.js 16+** - 前端开发环境
- **Git** - 版本控制
- **Docker & Docker Compose** - 容器化测试

#### 推荐工具

- **VS Code** - 代码编辑器
- **Postman** - API测试
- **DBeaver** - 数据库管理
- **Vue DevTools** - Vue调试工具

### 克隆项目

```bash
# 克隆仓库
git clone https://github.com/your-org/uni-load-improved.git
cd uni-load-improved

# 创建开发分支
git checkout -b feature/your-feature-name
```

### 后端环境搭建

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 安装开发依赖
pip install pytest pytest-asyncio pytest-cov black flake8 mypy

# 配置环境变量
cp ../.env.example ../.env
# 编辑.env文件，设置开发环境配置

# 初始化数据库
python ../scripts/init_db.py

# 启动开发服务器
uvicorn app.main:app --reload --port 8080
```

访问 http://localhost:8080/docs 查看API文档

### 前端环境搭建

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问 http://localhost:5173 查看前端应用

### IDE配置

#### VS Code推荐插件

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "vue.volar",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "ms-azuretools.vscode-docker"
  ]
}
```

#### VS Code设置

```json
{
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  }
}
```

---

## 项目结构

### 整体结构

```
uni-load-improved/
├── backend/              # 后端服务
│   ├── app/             # 应用代码
│   ├── tests/           # 测试代码
│   └── requirements.txt # Python依赖
├── frontend/            # 前端应用
│   ├── src/            # 源代码
│   └── package.json    # Node依赖
├── docker/             # Docker配置
├── docs/               # 文档
├── scripts/            # 工具脚本
└── config/             # 配置文件
```

### 后端结构详解

```
backend/app/
├── __init__.py
├── main.py              # 应用入口
├── config.py            # 配置管理
├── database.py          # 数据库连接
├── api/                 # API路由
│   ├── __init__.py
│   ├── api_sources.py   # API源管理路由
│   ├── models.py        # 模型管理路由
│   ├── providers.py     # Provider管理路由
│   └── config.py        # 配置管理路由
├── models/              # 数据模型（ORM）
│   ├── __init__.py
│   ├── api_source.py    # API源模型
│   ├── model.py         # 模型模型
│   └── provider_model.py # Provider模型
├── schemas/             # Pydantic schemas
│   ├── __init__.py
│   ├── api_source.py    # API源schema
│   ├── model.py         # 模型schema
│   └── config.py        # 配置schema
├── services/            # 业务逻辑
│   ├── __init__.py
│   ├── api_aggregator.py    # API聚合服务
│   ├── model_manager.py     # 模型管理服务
│   ├── config_generator.py  # 配置生成服务
│   └── health_monitor.py    # 健康监控服务
└── utils/               # 工具函数
    ├── __init__.py
    ├── encryption.py    # 加密工具
    └── normalization.py # 标准化工具
```

### 前端结构详解

```
frontend/src/
├── main.js              # 应用入口
├── App.vue              # 根组件
├── views/               # 页面视图
│   ├── Dashboard.vue        # 仪表盘
│   ├── ApiSources.vue       # API源管理
│   ├── ModelManagement.vue  # 模型管理
│   └── Configuration.vue    # 配置管理
├── components/          # 通用组件
│   ├── Layout.vue           # 布局组件
│   ├── ApiSourceForm.vue    # API源表单
│   ├── ModelRenameDialog.vue # 模型重命名对话框
│   ├── ProviderStatus.vue   # Provider状态
│   └── ConfigPreview.vue    # 配置预览
├── api/                 # API客户端
│   └── client.js        # HTTP请求封装
└── router/              # 路由配置
    └── index.js
```

---

## 后端开发

### FastAPI框架使用

#### 创建新的API端点

```python
# backend/app/api/example.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.example import ExampleCreate, ExampleResponse

router = APIRouter()

@router.get("/examples", response_model=List[ExampleResponse])
async def get_examples(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """获取示例列表"""
    # 实现查询逻辑
    return []

@router.post("/examples", response_model=ExampleResponse)
async def create_example(
    example: ExampleCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建示例"""
    # 实现创建逻辑
    pass
```

#### 注册路由

```python
# backend/app/main.py
from app.api import example

app.include_router(example.router, prefix="/api/v1", tags=["Examples"])
```

### 数据库模型

#### 定义ORM模型

```python
# backend/app/models/example.py
from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Example(Base):
    """示例模型"""
    __tablename__ = "examples"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

#### 定义Pydantic Schema

```python
# backend/app/schemas/example.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ExampleBase(BaseModel):
    """基础schema"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None

class ExampleCreate(ExampleBase):
    """创建schema"""
    pass

class ExampleUpdate(BaseModel):
    """更新schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None

class ExampleResponse(ExampleBase):
    """响应schema"""
    id: int
    enabled: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
```

### 服务层设计

#### 创建服务类

```python
# backend/app/services/example_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.models.example import Example
from app.schemas.example import ExampleCreate, ExampleUpdate

class ExampleService:
    """示例服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Example]:
        """获取所有示例"""
        result = await self.db.execute(
            select(Example)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_id(self, example_id: int) -> Optional[Example]:
        """根据ID获取示例"""
        result = await self.db.execute(
            select(Example).where(Example.id == example_id)
        )
        return result.scalar_one_or_none()
    
    async def create(self, data: ExampleCreate) -> Example:
        """创建示例"""
        example = Example(**data.dict())
        self.db.add(example)
        await self.db.commit()
        await self.db.refresh(example)
        return example
    
    async def update(
        self,
        example_id: int,
        data: ExampleUpdate
    ) -> Optional[Example]:
        """更新示例"""
        example = await self.get_by_id(example_id)
        if not example:
            return None
        
        for key, value in data.dict(exclude_unset=True).items():
            setattr(example, key, value)
        
        await self.db.commit()
        await self.db.refresh(example)
        return example
    
    async def delete(self, example_id: int) -> bool:
        """删除示例"""
        example = await self.get_by_id(example_id)
        if not example:
            return False
        
        await self.db.delete(example)
        await self.db.commit()
        return True
```

### 工具函数

#### 加密工具

```python
# backend/app/utils/encryption.py
from cryptography.fernet import Fernet
from app.config import settings

class Encryptor:
    """加密工具类"""
    
    def __init__(self):
        self.cipher = Fernet(settings.ENCRYPTION_KEY.encode())
    
    def encrypt(self, text: str) -> str:
        """加密文本"""
        return self.cipher.encrypt(text.encode()).decode()
    
    def decrypt(self, encrypted_text: str) -> str:
        """解密文本"""
        return self.cipher.decrypt(encrypted_text.encode()).decode()

# 全局实例
encryptor = Encryptor()
```

#### 标准化工具

```python
# backend/app/utils/normalization.py
import re
from typing import List, Dict

class ModelNameNormalizer:
    """模型名称标准化工具"""
    
    def __init__(self, rules: List[Dict[str, str]] = None):
        self.rules = rules or self._default_rules()
    
    def _default_rules(self) -> List[Dict[str, str]]:
        """默认标准化规则"""
        return [
            {"pattern": r"-\d{8}$", "replacement": ""},  # 移除日期
            {"pattern": r"-preview$", "replacement": ""},  # 移除preview
            {"pattern": r"-\d{4}$", "replacement": ""},  # 移除年份
        ]
    
    def normalize(self, name: str) -> str:
        """标准化模型名称"""
        normalized = name.lower()
        
        for rule in self.rules:
            normalized = re.sub(
                rule["pattern"],
                rule["replacement"],
                normalized
            )
        
        return normalized

# 全局实例
normalizer = ModelNameNormalizer()
```

---

## 前端开发

### Vue 3 Composition API

#### 创建新组件

```vue
<!-- frontend/src/components/ExampleComponent.vue -->
<template>
  <div class="example-component">
    <h2>{{ title }}</h2>
    <el-button @click="handleClick">点击我</el-button>
    <p>计数: {{ count }}</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// Props
const props = defineProps({
  title: {
    type: String,
    required: true
  }
})

// Emits
const emit = defineEmits(['update', 'delete'])

// 响应式数据
const count = ref(0)

// 计算属性
const doubleCount = computed(() => count.value * 2)

// 方法
const handleClick = () => {
  count.value++
  ElMessage.success('点击成功')
  emit('update', count.value)
}

// 生命周期
onMounted(() => {
  console.log('组件已挂载')
})
</script>

<style scoped>
.example-component {
  padding: 20px;
}
</style>
```

### 组件设计原则

#### 1. 单一职责

每个组件只负责一个功能：

```vue
<!-- ❌ 不好：一个组件做太多事 -->
<template>
  <div>
    <form>...</form>
    <table>...</table>
    <chart>...</chart>
  </div>
</template>

<!-- ✅ 好：拆分为多个组件 -->
<template>
  <div>
    <DataForm />
    <DataTable />
    <DataChart />
  </div>
</template>
```

#### 2. Props向下，Events向上

```vue
<!-- 父组件 -->
<template>
  <ChildComponent
    :data="parentData"
    @update="handleUpdate"
  />
</template>

<!-- 子组件 -->
<script setup>
const props = defineProps(['data'])
const emit = defineEmits(['update'])

const handleChange = (newData) => {
  emit('update', newData)
}
</script>
```

#### 3. 使用组合式函数

```javascript
// frontend/src/composables/useApiSource.js
import { ref } from 'vue'
import { api } from '@/api/client'

export function useApiSource() {
  const sources = ref([])
  const loading = ref(false)
  const error = ref(null)
  
  const fetchSources = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('/api-sources')
      sources.value = response.data
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }
  
  return {
    sources,
    loading,
    error,
    fetchSources
  }
}
```

使用组合式函数：

```vue
<script setup>
import { onMounted } from 'vue'
import { useApiSource } from '@/composables/useApiSource'

const { sources, loading, error, fetchSources } = useApiSource()

onMounted(() => {
  fetchSources()
})
</script>
```

### API调用

#### API客户端封装

```javascript
// frontend/src/api/client.js
import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const client = axios.create({
  baseURL: '/api/v1',
  timeout: 30000
})

// 请求拦截器
client.interceptors.request.use(
  config => {
    // 添加认证token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
client.interceptors.response.use(
  response => {
    return response
  },
  error => {
    // 统一错误处理
    const message = error.response?.data?.detail || error.message
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

// API方法
export const api = {
  // API源
  getApiSources: () => client.get('/api-sources'),
  createApiSource: (data) => client.post('/api-sources', data),
  updateApiSource: (id, data) => client.put(`/api-sources/${id}`, data),
  deleteApiSource: (id) => client.delete(`/api-sources/${id}`),
  
  // 模型
  getModels: (params) => client.get('/models', { params }),
  renameModel: (id, data) => client.put(`/models/${id}/rename`, data),
  deleteModel: (id) => client.delete(`/models/${id}`),
  
  // 配置
  generateConfig: () => client.post('/config/generate'),
  applyConfig: () => client.post('/config/apply'),
}
```

### 样式规范

#### 使用Scoped样式

```vue
<style scoped>
/* 组件样式只在当前组件生效 */
.component-class {
  color: #333;
}
</style>
```

#### 使用CSS变量

```css
/* 定义全局变量 */
:root {
  --primary-color: #409eff;
  --success-color: #67c23a;
  --warning-color: #e6a23c;
  --danger-color: #f56c6c;
  --spacing-unit: 8px;
}

/* 使用变量 */
.button {
  background-color: var(--primary-color);
  padding: calc(var(--spacing-unit) * 2);
}
```

---

## 测试

### 后端测试

#### 单元测试

```python
# backend/tests/test_services/test_example_service.py
import pytest
from app.services.example_service import ExampleService
from app.schemas.example import ExampleCreate

@pytest.mark.asyncio
async def test_create_example(db_session):
    """测试创建示例"""
    service = ExampleService(db_session)
    data = ExampleCreate(name="Test", description="Test description")
    
    example = await service.create(data)
    
    assert example.id is not None
    assert example.name == "Test"
    assert example.description == "Test description"

@pytest.mark.asyncio
async def test_get_example_by_id(db_session):
    """测试根据ID获取示例"""
    service = ExampleService(db_session)
    
    # 创建测试数据
    data = ExampleCreate(name="Test", description="Test")
    created = await service.create(data)
    
    # 获取数据
    example = await service.get_by_id(created.id)
    
    assert example is not None
    assert example.id == created.id
```

#### API测试

```python
# backend/tests/test_api/test_example.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_examples(client: AsyncClient):
    """测试获取示例列表"""
    response = await client.get("/api/v1/examples")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_create_example(client: AsyncClient):
    """测试创建示例"""
    data = {
        "name": "Test Example",
        "description": "Test description"
    }
    
    response = await client.post("/api/v1/examples", json=data)
    
    assert response.status_code == 200
    result = response.json()
    assert result["name"] == data["name"]
    assert result["description"] == data["description"]
```

#### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_services/test_example_service.py

# 运行并显示覆盖率
pytest --cov=app --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html
```

### 前端测试

#### 组件测试

```javascript
// frontend/tests/components/ExampleComponent.spec.js
import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import ExampleComponent from '@/components/ExampleComponent.vue'

describe('ExampleComponent', () => {
  it('renders properly', () => {
    const wrapper = mount(ExampleComponent, {
      props: { title: 'Test Title' }
    })
    
    expect(wrapper.text()).toContain('Test Title')
  })
  
  it('emits update event on button click', async () => {
    const wrapper = mount(ExampleComponent, {
      props: { title: 'Test' }
    })
    
    await wrapper.find('button').trigger('click')
    
    expect(wrapper.emitted()).toHaveProperty('update')
  })
})
```

#### 运行测试

```bash
# 运行所有测试
npm run test

# 运行并监听变化
npm run test:watch

# 生成覆盖率报告
npm run test:coverage
```

---

## 代码规范

### Python代码规范（PEP 8）

#### 命名规范

```python
# 类名：大驼峰
class ApiSourceService:
    pass

# 函数名：小写+下划线
def get_api_sources():
    pass

# 变量名：小写+下划线
api_source_list = []

# 常量：大写+下划线
MAX_RETRY_COUNT = 3

# 私有方法：前缀下划线
def _internal_method():
    pass
```

#### 文档字符串

```python
def create_api_source(name: str, base_url: str, api_key: str) -> ApiSource:
    """
    创建API源
    
    Args:
        name: API源名称
        base_url: API基础URL
        api_key: API密钥
    
    Returns:
        ApiSource: 创建的API源对象
    
    Raises:
        ValueError: 如果参数无效
        DatabaseError: 如果数据库操作失败
    
    Example:
        >>> source = create_api_source("OpenAI", "https://api.openai.com/v1", "sk-xxx")
        >>> print(source.name)
        OpenAI
    """
    pass
```

#### 类型注解

```python
from typing import List, Optional, Dict, Any

def process_models(
    models: List[Dict[str, Any]],
    filter_enabled: bool = True
) -> Optional[List[str]]:
    """处理模型列表"""
    pass
```

### JavaScript代码规范

#### 命名规范

```javascript
// 类名：大驼峰
class ApiSourceManager {
}

// 函数名：小驼峰
function getApiSources() {
}

// 变量名：小驼峰
const apiSourceList = []

// 常量：大写+下划线
const MAX_RETRY_COUNT = 3

// 组件名：大驼峰
const ApiSourceForm = {}
```

#### JSDoc注释

```javascript
/**
 * 创建API源
 * @param {string} name - API源名称
 * @param {string} baseUrl - API基础URL
 * @param {string} apiKey - API密钥
 * @returns {Promise<Object>} API源对象
 * @throws {Error} 如果创建失败
 */
async function createApiSource(name, baseUrl, apiKey) {
  // 实现
}
```

### Git提交规范

#### 提交消息格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Type类型

- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具相关

#### 示例

```bash
# 新功能
git commit -m "feat(api): add model rename endpoint"

# 修复bug
git commit -m "fix(ui): fix model list pagination issue"

# 文档更新
git commit -m "docs: update API documentation"

# 重构
git commit -m "refactor(service): simplify config generation logic"
```

---

## 构建和部署

### Docker镜像构建

```bash
# 构建all-in-one镜像
docker build -f docker/Dockerfile -t uni-load-improved:latest .

# 构建后端镜像
docker build -f docker/Dockerfile.backend -t uni-load-backend:latest .

# 构建前端镜像
docker build -f docker/Dockerfile.frontend -t uni-load-frontend:latest .

# 多架构构建
docker buildx build --platform linux/amd64,linux/arm64 \
  -t uni-load-improved:latest .
```

### CI/CD配置

#### GitHub Actions示例

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        run: |
          cd backend
          pytest --cov=app
  
  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          cd frontend
          npm install
      
      - name: Run tests
        run: |
          cd frontend
          npm run test
  
  build:
    needs: [test-backend, test-frontend]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: |
          docker build -f docker/Dockerfile \
            -t uni-load-improved:${{ github.sha }} .
```

---

## 调试技巧

### 后端调试

#### 使用pdb调试

```python
# 在代码中插入断点
import pdb; pdb.set_trace()

# 或使用breakpoint()（Python 3.7+）
breakpoint()
```

#### VS Code调试配置

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--reload",
        "--port",
        "8080"
      ],
      "jinja": true,
      "justMyCode": false,
      "cwd": "${workspaceFolder}/backend"
    }
  ]
}
```

### 前端调试

#### Vue DevTools

1. 安装Vue DevTools浏览器扩展
2. 打开开发者工具
3. 切换到Vue标签
4. 查看组件树、状态、事件等

#### 浏览器调试

```javascript
// 在代码中插入断点
debugger;

// 使用console
console.log('Debug info:', data)
console.table(arrayData)
console.group('Group name')
console.log('Item 1')
console.log('Item 2')
console.groupEnd()
```

---

## 常见问题

### Q: 如何添加新的API端点？

A: 参考[创建新的API端点](#创建新的api端点)章节

### Q: 如何添加新的数据库表？

A: 
1. 在`backend/app/models/`创建模型文件
2. 定义ORM模型
3. 运行数据库迁移

### Q: 如何添加新的前端页面？

A:
1. 在`frontend/src/views/`创建Vue组件
2. 在`frontend/src/router/index.js`添加路由
3. 在Layout组件添加导航链接

---

## 参考资源

- [FastAPI文档](https://fastapi.tiangolo.com/)
- [Vue 3文档](https://vuejs.org/)
- [Element Plus文档](https://element-plus.org/)
- [SQLAlchemy文档](https://docs.sqlalchemy.org/)