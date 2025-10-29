import { boot } from 'quasar/wrappers';
import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import { Notify } from 'quasar';
import { useAuthStore } from 'stores/auth'; // Importamos el store de Auth

// 1. CREACIÓN DE LA INSTANCIA DE AXIOS
const api: AxiosInstance = axios.create({
  baseURL: '/api',
});

// 2. EXPORTACIÓN PARA USO EXTERNO
// Exportamos la instancia `api` para poder importarla directamente.
export { api };

// 3. ARCHIVO DE ARRANQUE (BOOT)
// Usamos el tipo 'BootFileParams' para tipar los parámetros
export default boot(({ app, router }) => {

  // 4. INTERCEPTOR DE PETICIONES (REQUEST)
  api.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      // Obtenemos el token desde el store de Pinia, que es más seguro y reactivo
      const authStore = useAuthStore();
      const token = authStore.token;

      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // 5. INTERCEPTOR DE RESPUESTAS (RESPONSE)
  api.interceptors.response.use(
    (response) => response,
    (error) => {
      // Verificamos si el error es de tipo 401 (Unauthorized).
      if (error.response && error.response.status === 401) {
        Notify.create({
          type: 'negative',
          message: 'Tu sesión ha expirado. Por favor, inicia sesión de nuevo.',
          position: 'top',
        });
        
        // Usamos la acción de logout del store para limpiar el estado y localStorage
        const authStore = useAuthStore();
        authStore.logout(); // Esto ya limpia el token y el usuario
        
        // Redirigimos al usuario a la página de login.
        router.push('/login');
      }
      
      return Promise.reject(error);
    }
  );

  // 6. INYECCIÓN EN LA APP DE VUE
  // Hacemos que `api` esté disponible globalmente
  app.config.globalProperties.$api = api;
});