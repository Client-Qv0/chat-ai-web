import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: () => import('@/views/Home.vue') },
    { path: '/login', component: () => import('@/views/Login.vue') },
    { path: '/register', component: () => import('@/views/Register.vue') },
    { path: '/recovery', component: () => import('@/views/Recovery.vue') },
    { path: '/403', component: () => import('@/views/Forbidden.vue') },
    {
      path: '/chat',
      component: () => import('@/views/chat/ChatLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', component: () => import('@/views/chat/EmptyChat.vue') },
        { path: ':routeId', component: () => import('@/views/chat/ChatWindow.vue') },
      ],
    },
    {
      path: '/api',
      component: () => import('@/views/api/ApiLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', redirect: '/api/index' },
        { path: 'index', component: () => import('@/views/api/ApiDocs.vue') },
        { path: 'token', component: () => import('@/views/api/TokenUsage.vue') },
        { path: 'key', component: () => import('@/views/api/ApiKeyManage.vue') },
      ],
    },
    { path: '/user/:phone', component: () => import('@/views/user/UserProfile.vue'), meta: { requiresAuth: true } },
    { path: '/admin', component: () => import('@/views/admin/AdminLayout.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
  ],
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('access_token')
  if (to.meta.requiresAuth && !token) {
    return next('/login')
  }
  if (to.meta.requiresAdmin) {
    const raw = localStorage.getItem('user_info')
    if (raw) {
      const user = JSON.parse(raw)
      if (user.role !== 'admin') return next('/403')
    } else {
      return next('/login')
    }
  }
  next()
})

export default router
