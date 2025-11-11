import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: () => import('../views/Dashboard.vue'),
      meta: { title: '仪表盘' }
    },
    {
      path: '/api-sources',
      name: 'api-sources',
      component: () => import('../views/ApiSources.vue'),
      meta: { title: 'API源管理' }
    },
    {
      path: '/models',
      name: 'models',
      component: () => import('../views/ModelManagement.vue'),
      meta: { title: '模型管理' }
    },
    {
      path: '/config',
      name: 'config',
      component: () => import('../views/Configuration.vue'),
      meta: { title: '配置管理' }
    }
  ]
})

router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title || 'uni-load-improved'} - LLM API网关管理系统`
  next()
})

export default router