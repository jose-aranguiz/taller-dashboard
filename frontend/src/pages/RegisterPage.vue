<template>
  <q-page class="flex flex-center bg-grey-2">
    <q-card style="width: 400px">
      <q-card-section class="text-center">
        <div class="text-h6">Crear Cuenta</div>
      </q-card-section>

      <q-card-section>
        <q-form @submit.prevent="handleRegister">
          <q-input v-model="username" label="Usuario" outlined class="q-mb-md" />
          <q-input v-model="email" label="Email" type="email" outlined class="q-mb-md" />
          <q-input v-model="password" label="Contraseña" type="password" outlined class="q-mb-md" />
          <q-btn type="submit" label="Registrarse" color="primary" class="full-width" />
        </q-form>
      </q-card-section>
       <q-card-section class="text-center">
        ¿Ya tienes una cuenta? <router-link to="/login">Inicia sesión</router-link>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from 'stores/auth'
import { useQuasar } from 'quasar'

const username = ref('')
const email = ref('')
const password = ref('')
const authStore = useAuthStore()
const $q = useQuasar()

const handleRegister = async () => {
  try {
    await authStore.register({
      username: username.value,
      email: email.value,
      password: password.value
    })
  } catch (error) {
     $q.notify({ type: 'negative', message: error.response?.data?.detail || 'Error en el registro.' })
  }
}
</script>