import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/views/Layout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/dashboard'
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue')
      },
      {
        path: 'templates',
        name: 'Templates',
        component: () => import('@/views/Templates.vue'),
        meta: { roles: ['admin'] }
      },
      {
        path: 'upload',
        name: 'Upload',
        component: () => import('@/views/Upload.vue'),
        meta: { roles: ['admin', 'user'] }
      },
      {
        path: 'records',
        name: 'Records',
        component: () => import('@/views/Records.vue')
      },
      {
        path: 'plans',
        name: 'Plans',
        component: () => import('@/views/Plans.vue')
      },
      {
        path: 'audit',
        name: 'Audit',
        component: () => import('@/views/Audit.vue'),
        meta: { roles: ['admin', 'auditor'] }
      },
      {
        path: 'alerts',
        name: 'Alerts',
        component: () => import('@/views/Alerts.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  const requiresAuth = to.meta.requiresAuth !== false
  const requiredRoles = to.meta.roles

  if (requiresAuth && !userStore.token) {
    next('/login')
  } else if (requiredRoles && !requiredRoles.includes(userStore.user?.role)) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
