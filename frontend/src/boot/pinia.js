// src/boot/pinia.js
import { createPinia } from 'pinia'

// ✨ 1. PRIMER MARCADOR
console.log('1. EJECUTANDO boot/pinia.js...');

export default ({ app }) => {
  const pinia = createPinia()
  app.use(pinia)

  // ✨ 2. SEGUNDO MARCADOR
  console.log('2. PINIA INSTALADO CORRECTAMENTE EN LA APP.');
}