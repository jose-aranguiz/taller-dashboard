import { boot } from 'quasar/wrappers'
import axios from 'axios'
import { Notify } from 'quasar'

// 1. CREACIÓN DE LA INSTANCIA DE AXIOS
// Se crea una instancia centralizada para toda la aplicación.
// La baseURL apunta a '/api' para que Quasar utilice el proxy configurado en `quasar.config.js`.
// Esto evita problemas de CORS durante el desarrollo.
const api = axios.create({
  baseURL: '/api'
})

export default boot(({ app, router }) => {
  // 2. INTERCEPTOR DE PETICIONES (REQUEST)
  // Esta función se ejecuta ANTES de que cada petición sea enviada a la API.
  api.interceptors.request.use(config => {
    // Busca el token de autenticación en el almacenamiento local.
    // Asegúrate de que la clave 'user-token' coincida con la que guardas al iniciar sesión.
    const token = localStorage.getItem('user-token')

    // Si el token existe, se añade a la cabecera 'Authorization'.
    // El formato `Bearer ${token}` es un estándar común.
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // Se retorna la configuración para que la petición continúe su curso.
    return config
  }, error => {
    // Si hay un error al construir la petición, se rechaza la promesa.
    return Promise.reject(error)
  })

  // 3. INTERCEPTOR DE RESPUESTAS (RESPONSE)
  // Esta función se ejecuta DESPUÉS de recibir una respuesta de la API.
  api.interceptors.response.use(
    // Si la respuesta es exitosa (código 2xx), simplemente la dejamos pasar.
    (response) => response,
    
    // Si la API responde con un error, lo manejamos aquí.
    (error) => {
      // Verificamos si el error es de tipo 401 (Unauthorized).
      if (error.response && error.response.status === 401) {
        // Si es 401, significa que la sesión del usuario ha expirado o el token es inválido.
        Notify.create({
          type: 'negative',
          message: 'Tu sesión ha expirado. Por favor, inicia sesión de nuevo.',
          position: 'top'
        })
        
        // Eliminamos el token inválido del almacenamiento.
        localStorage.removeItem('user-token')
        
        // Redirigimos al usuario a la página de login.
        router.push('/login')
      }
      
      // Rechazamos la promesa para que el bloque `.catch()` en el código que hizo la llamada (ej. en el store) también se ejecute si es necesario.
      return Promise.reject(error)
    }
  )

  // 4. INYECCIÓN EN LA APP DE VUE
  // Hacemos que la instancia `api` esté disponible globalmente en los componentes de Vue
  // a través de `this.$api` (en Options API) o `getCurrentInstance` (en Composition API).
  app.config.globalProperties.$api = api
})

// 5. EXPORTACIÓN PARA USO EXTERNO
// Exportamos la instancia `api` para poder importarla directamente en otros archivos,
// especialmente en los stores de Pinia, que es la práctica recomendada.
export { api }