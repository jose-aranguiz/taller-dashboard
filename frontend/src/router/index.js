// src/router/index.js

// ✨ MARCADOR DE IMPORTACIÓN
console.log('B. MÓDULO router/index.js IMPORTADO.');

import { route } from 'quasar/wrappers'
import { createRouter, createMemoryHistory, createWebHistory, createWebHashHistory } from 'vue-router'
import routes from './routes'
import { useAuthStore } from 'stores/auth'

export default route(function () {
  // ✨ MARCADOR DE CREACIÓN
  console.log('C. CREANDO INSTANCIA DEL ROUTER...');

  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : (process.env.VUE_ROUTER_MODE === 'history' ? createWebHistory : createWebHashHistory)

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,
    history: createHistory(process.env.VUE_ROUTER_BASE)
  })

  Router.beforeEach((to, from, next) => {
    // ✨ MARCADOR DE GUARDIA
    console.log('D. DENTRO DE beforeEach - A punto de usar el store.');
    const authStore = useAuthStore()
    
    const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
    const requiresAdmin = to.matched.some(record => record.meta.requiresAdmin)

    if (requiresAuth && !authStore.isAuthenticated) {
      next({ path: '/login' })
    } else if (requiresAdmin && !authStore.isAdmin) {
      next({ path: '/' })
    } else if ((to.path === '/login' || to.path === '/register') && authStore.isAuthenticated) {
      next({ path: '/' })
    } else {
      next()
    }
  })

  return Router
})