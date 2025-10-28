<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          @click="toggleLeftDrawer"
        />

        <q-toolbar-title>
          Taller Dashboard
        </q-toolbar-title>

        <q-btn flat icon="logout" @click="logout" label="Cerrar Sesión" />
      </q-toolbar>
    </q-header>

    <q-drawer
      v-model="leftDrawerOpen"
      show-if-above
      bordered
    >
      <q-list>
        <q-item-label header>
          Menú de Navegación
        </q-item-label>

        <q-item
          v-for="link in essentialLinks"
          :key="link.title"
          clickable
          :to="link.link"
          exact
        >
          <q-item-section avatar>
            <q-icon :name="link.icon" />
          </q-item-section>
          <q-item-section>
            <q-item-label>{{ link.title }}</q-item-label>
            <q-item-label caption>{{ link.caption }}</q-item-label>
          </q-item-section>
        </q-item>

        <q-separator class="q-my-md" />

        <q-expansion-item
          v-if="authStore.isAdmin"
          icon="admin_panel_settings"
          label="Administración"
          caption="Gestión del Sistema"
          :default-opened="true"
        >
          <q-list class="q-pl-lg">
            <q-item clickable to="/admin/tecnicos">
              <q-item-section avatar>
                <q-icon name="engineering" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Gestionar Técnicos</q-item-label>
              </q-item-section>
            </q-item>
            </q-list>
        </q-expansion-item>

      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from 'stores/auth' // Asegúrate que la ruta a tu store sea correcta

const leftDrawerOpen = ref(false)
const authStore = useAuthStore()

// Lista de enlaces para el menú principal
const essentialLinks = [
  {
    title: 'Dashboard',
    caption: 'Métricas y KPIs',
    icon: 'dashboard',
    link: '/'
  },
  {
    title: 'Gestión de Trabajos',
    caption: 'Tabla y Kanban',
    icon: 'build',
    link: '/trabajos'
  },
  {
    title: 'Historial',
    caption: 'Trabajos Entregados',
    icon: 'history',
    link: '/historial' // Corregido de '/history' a '/historial' si así lo prefieres
  }
]

function toggleLeftDrawer () {
  leftDrawerOpen.value = !leftDrawerOpen.value
}

function logout() {
  authStore.logout()
  // Opcional: Redirigir al login
  // import { useRouter } from 'vue-router'
  // const router = useRouter()
  // router.push('/login')
}
</script>