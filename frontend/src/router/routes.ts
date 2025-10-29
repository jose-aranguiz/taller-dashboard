// src/router/routes.ts
import { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  // --- GRUPO DE RUTAS PRIVADAS ---
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', component: () => import('pages/IndexPage.vue') },
      { path: 'trabajos', component: () => import('pages/TrabajosPage.vue') },
      { path: 'historial', component: () => import('pages/HistorialPage.vue') },
      {
        path: 'admin/tecnicos',
        component: () => import('pages/TecnicosPage.vue'),
        meta: { requiresAdmin: true },
      },
    ],
  },

  // --- GRUPO DE RUTAS PÚBLICAS (MODIFICADO) ---
  // Ahora todas las rutas hijas usarán PublicLayout.vue
  {
    path: '/', // <-- Se mantiene el path base
    component: () => import('layouts/PublicLayout.vue'), // <-- USA EL LAYOUT PÚBLICO
    children: [
      {
        path: 'login', // La ruta completa será /login
        component: () => import('pages/LoginPage.vue'),
      },
      {
        path: 'register', // La ruta completa será /register
        component: () => import('pages/RegisterPage.vue'),
      },
    ],
  },

  // --- RUTA CATCH-ALL (404) ---
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
];

export default routes;