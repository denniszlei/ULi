<template>
  <el-container class="layout-container">
    <el-header class="layout-header">
      <div class="header-left">
        <h1>uni-load-improved</h1>
        <span class="subtitle">LLM API网关管理系统</span>
      </div>
      <el-menu mode="horizontal" :default-active="activeMenu" router class="header-menu">
        <el-menu-item index="/">
          <el-icon><HomeFilled /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/api-sources">
          <el-icon><Connection /></el-icon>
          <span>API源管理</span>
        </el-menu-item>
        <el-menu-item index="/models">
          <el-icon><Box /></el-icon>
          <span>模型管理</span>
        </el-menu-item>
        <el-menu-item index="/config">
          <el-icon><Setting /></el-icon>
          <span>配置管理</span>
        </el-menu-item>
      </el-menu>
    </el-header>
    
    <el-main class="layout-main">
      <slot />
    </el-main>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const activeMenu = computed(() => route.path)
</script>

<style scoped>
.layout-container {
  height: 100vh;
  overflow: hidden;
}

.layout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.header-left h1 {
  margin: 0;
  font-size: 20px;
  color: #409eff;
  font-weight: 600;
}

.subtitle {
  font-size: 12px;
  color: #909399;
}

.header-menu {
  border-bottom: none;
  flex: 1;
  justify-content: flex-end;
}

.layout-main {
  background-color: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
}
</style>