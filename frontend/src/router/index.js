import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/',
    component: () => import('../views/Layout.vue'),
    children: [
      {
        path: '',
        redirect: '/dashboard'
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue')
      },
      {
        path: 'personas',
        name: 'Personas',
        component: () => import('../views/Personas.vue')
      },
      {
        path: 'personas/create',
        name: 'PersonaCreate',
        component: () => import('../views/PersonaEdit.vue')
      },
      {
        path: 'personas/:id/edit',
        name: 'PersonaEdit',
        component: () => import('../views/PersonaEdit.vue')
      },
      {
        path: 'tg-accounts',
        name: 'TgAccounts',
        component: () => import('../views/TgAccounts.vue')
      },
      {
        path: 'memories',
        name: 'Memories',
        component: () => import('../views/Memories.vue')
      },
      {
        path: 'conversations',
        name: 'Conversations',
        component: () => import('../views/Conversations.vue')
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('../views/Settings.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
