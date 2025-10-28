// src/stores/auth.js

// ✨ MARCADOR DE IMPORTACIÓN
console.log('A. MÓDULO stores/auth.js IMPORTADO.');

import { defineStore } from 'pinia';
import { api } from 'boot/axios';
import { ref, computed } from 'vue';

// ✨ NOTA: Se ha eliminado la importación y el uso de useRouter() de aquí
// para romper la dependencia circular, como en la corrección anterior.

export const useAuthStore = defineStore('auth', () => {
  // --- STATE ---
  const token = ref(localStorage.getItem('user-token') || null);
  const user = ref(JSON.parse(localStorage.getItem('user-data')) || null);

  // --- GETTERS ---
  const isAuthenticated = computed(() => !!token.value);
  const isAdmin = computed(() => user.value?.role === 'admin');

  // --- ACTIONS ---
  async function fetchUser() {
    if (token.value) {
      try {
        const response = await api.get('/auth/users/me');
        user.value = response.data;
        localStorage.setItem('user-data', JSON.stringify(response.data));
      } catch (error) {
        console.error('No se pudo obtener la información del usuario. Token podría ser inválido.', error);
        await logout();
      }
    }
  }

  function setToken(newToken) {
    token.value = newToken;
    localStorage.setItem('user-token', newToken);
    api.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
  }

  async function login(credentials) {
    const params = new URLSearchParams();
    params.append('username', credentials.username);
    params.append('password', credentials.password);
    
    const response = await api.post('/auth/token', params);
    setToken(response.data.access_token);
    
    await fetchUser();
  }

  async function logout() {
    token.value = null;
    user.value = null;
    localStorage.removeItem('user-token');
    localStorage.removeItem('user-data');
    delete api.defaults.headers.common['Authorization'];
  }

  // --- LÓGICA DE INICIALIZACIÓN ---
  if (token.value) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token.value}`;
    if (!user.value) {
      fetchUser();
    }
  }

  return {
    token,
    user,
    isAuthenticated,
    isAdmin,
    login,
    logout,
    fetchUser
  };
});