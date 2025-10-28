import js from '@eslint/js';
import globals from 'globals';
import pluginVue from 'eslint-plugin-vue';
import pluginQuasar from '@quasar/app-vite/eslint';
import typescriptEslint from '@typescript-eslint/eslint-plugin';
import typescriptParser from '@typescript-eslint/parser';
import vueParser from 'vue-eslint-parser';
import prettierSkipFormatting from '@vue/eslint-config-prettier/skip-formatting';

export default [
  // 1. Objeto de Ignorados Globales
  {
    // ESLint requiere que "ignores" sea la única clave en este objeto.
    // Quasar ya ignora node_modules y otras carpetas relevantes.
    ignores: [
      'dist',
      '.quasar',
      'src-capacitor',
      'src-cordova',
      'www',
      '*.md'
    ]
  },

  // 2. Recomendaciones Base de Quasar
  // Contiene reglas y configuraciones específicas para proyectos Quasar.
  ...pluginQuasar.configs.recommended(),

  // 3. Configuración para TypeScript (LA CLAVE DEL PROBLEMA)
  // Este bloque aplica reglas de TypeScript a todos los archivos relevantes.
  {
    files: ['**/*.{ts,tsx,vue,js,jsx}'], // Aplica a todos los archivos de script
    plugins: {
      '@typescript-eslint': typescriptEslint,
    },
    languageOptions: {
      parser: typescriptParser, // Usa el parser de TypeScript
      parserOptions: {
        project: true, // Habilita reglas que requieren información de tipos
        tsconfigRootDir: import.meta.dirname,
      },
    },
    rules: {
      ...typescriptEslint.configs['eslint-recommended'].rules,
      ...typescriptEslint.configs.recommended.rules,
    },
  },

  // 4. Configuración Específica para Vue
  // Este bloque se enfoca solo en los archivos .vue.
  {
    files: ['**/*.vue'],
    plugins: {
      vue: pluginVue,
    },
    // Usa vue-eslint-parser para el template, y le indica que use el parser de TS para el <script>
    languageOptions: {
      parser: vueParser,
      parserOptions: {
        parser: typescriptParser,
        extraFileExtensions: ['.vue'],
      },
    },
    // Usa un conjunto de reglas más robusto para Vue 3.
    rules: {
      ...pluginVue.configs['flat/recommended'].rules,
    },
  },

  // 5. Configuración General del Proyecto (Reglas y Globales)
  {
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: {
        ...globals.browser,
        ...globals.node,
        process: 'readonly',
        ga: 'readonly',
        cordova: 'readonly',
        Capacitor: 'readonly',
        chrome: 'readonly',
        browser: 'readonly',
      },
    },
    rules: {
      'prefer-promise-reject-errors': 'off',
      // Permite el debugger solo en desarrollo
      'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'off',
      // Reglas adicionales recomendadas:
      'vue/multi-word-component-names': 'off', // Muy común desactivarla en proyectos Quasar
      'vue/no-reserved-component-names': 'off',
    },
  },

  // 6. Configuración para Service Workers (si aplica)
  {
    files: ['src-pwa/custom-service-worker.js'],
    languageOptions: {
      globals: {
        ...globals.serviceworker,
      },
    },
  },
  
  // 7. Integración con Prettier (SIEMPRE AL FINAL)
  // Desactiva cualquier regla de formato de ESLint para que Prettier tenga el control.
  prettierSkipFormatting,
];