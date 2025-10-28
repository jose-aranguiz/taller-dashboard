<template>
  <q-page class="flex flex-center bg-grey-2">
    <q-card style="width: 400px">
      <q-card-section class="text-center">
        <div class="text-h6">Iniciar Sesión</div>
        <div class="text-subtitle2">Bienvenido de vuelta</div>
      </q-card-section>

      <q-card-section>
        <q-form @submit.prevent="handleLogin">
          <q-input v-model="username" label="Usuario" outlined class="q-mb-md" />
          <q-input v-model="password" label="Contraseña" type="password" outlined class="q-mb-md" />
          <q-btn type="submit" label="Ingresar" color="primary" class="full-width" :loading="isLoading" />
        </q-form>
      </q-card-section>

      <q-card-section class="text-center">
        ¿No tienes una cuenta? <router-link to="/register">Regístrate aquí</router-link>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from 'stores/auth'
import { useQuasar } from 'quasar'
import { useRouter } from 'vue-router' // ✨ 1. IMPORTAMOS EL ROUTER

const username = ref('')
const password = ref('')
const isLoading = ref(false)
const authStore = useAuthStore()
const $q = useQuasar()
const router = useRouter() // ✨ 2. INICIALIZAMOS EL ROUTER

const handleLogin = async () => {
  isLoading.value = true
  try {
    await authStore.login({ username: username.value, password: password.value })
    
    // ✨ 3. REDIRIGIMOS TRAS UN LOGIN EXITOSO
    await router.push('/')

  } catch (error) {
    console.error('Login failed:', error)
    const message = error.response?.data?.detail || 'Usuario o contraseña incorrectos.'
    $q.notify({ type: 'negative', message: message })
  } finally {
    isLoading.value = false
  }
}
</script>