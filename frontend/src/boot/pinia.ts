// src/boot/pinia.ts
import { boot } from 'quasar/wrappers';
import { createPinia } from 'pinia';

// Tipamos la función boot
export default boot(({ app }) => {
  const pinia = createPinia();
  app.use(pinia);
});