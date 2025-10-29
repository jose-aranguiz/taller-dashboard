import { defineStore } from 'pinia';
import { api } from 'boot/axios';
import { Notify } from 'quasar';

// --- 1. Definimos Interfaces ---
interface User {
  username: string;
  email: string;
  role: 'admin' | 'user' | 'guest'; // Asumimos estos roles
  id: number;
  // Agrega más campos si 'user' tiene más datos
}

interface AuthState {
  token: string | null;
  user: User | null;
}

export const useAuthStore = defineStore('auth', {
  // --- 2. Tipamos el State ---
  state: (): AuthState => ({
    token: localStorage.getItem('token') || null,
    // Le decimos a JSON.parse que espere 'null' como string si no encuentra nada
    user: JSON.parse(localStorage.getItem('user') || 'null'),
  }),
  getters: {
    // --- 3. Tipamos los Getters ---
    isAuthenticated: (state: AuthState): boolean => !!state.token,
    isAdmin: (state: AuthState): boolean => !!(state.user && state.user.role === 'admin'),
    userRole: (state: AuthState): 'admin' | 'user' | 'guest' => state.user?.role || 'guest',
    username: (state: AuthState): string => state.user?.username || 'Invitado',
  },
  actions: {
    // --- 4. Tipamos las Acciones ---
    async login(credentials: URLSearchParams) {
      try {
        // Tipamos la respuesta esperada de la API
        const response = await api.post<{ access_token: string; user: User }>('/token', credentials);
        
        const { access_token, user } = response.data;
        this.setAuth(access_token, user);
        Notify.create({ type: 'positive', message: `Bienvenido, ${user.username}!` });
        return true;
      } catch (error) {
        Notify.create({ type: 'negative', message: 'Error de autenticación', caption: 'Usuario o contraseña incorrectos.' });
        return false;
      }
    },

    logout() {
      this.clearAuth();
      Notify.create({ type: 'info', message: 'Sesión cerrada.' });
    },

    setAuth(token: string, user: User) {
      this.token = token;
      this.user = user;
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(user));
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    },

    clearAuth() {
      this.token = null;
      this.user = null;
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      delete api.defaults.headers.common['Authorization'];
    },

    initializeAuth() {
      if (this.token) {
        api.defaults.headers.common['Authorization'] = `Bearer ${this.token}`;
      }
    },
  },
});