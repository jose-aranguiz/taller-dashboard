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
  ...pluginQuasar.configs.recommended(),

  // 3. Configuración para TypeScript (Archivos .ts, .js)
  {
    // --- 👇 CAMBIO 1: Quitamos '.vue' de esta lista ---
    files: ['**/*.{ts,tsx,js,jsx}'], 
    plugins: {
      '@typescript-eslint': typescriptEslint,
    },
    languageOptions: {
      parser: typescriptParser, 
      parserOptions: {
        // --- 👇 CAMBIO 2: Somos explícitos con la ruta del proyecto ---
        project: './tsconfig.json', 
        tsconfigRootDir: import.meta.dirname,
      },
    },
    rules: {
      ...typescriptEslint.configs['eslint-recommended'].rules,
      ...typescriptEslint.configs.recommended.rules,
    },
  },

  // 4. Configuración Específica para Vue (Archivos .vue)
  {
    files: ['**/*.vue'],
    plugins: {
      vue: pluginVue,
    },
    languageOptions: {
      parser: vueParser,
      parserOptions: {
        parser: typescriptParser,
        extraFileExtensions: ['.vue'],
        // --- 👇 CAMBIO 3: Añadimos la configuración explícita del proyecto AQUÍ TAMBIÉN ---
        project: './tsconfig.json',
        tsconfigRootDir: import.meta.dirname,
      },
    },
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
      'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'off',
      'vue/multi-word-component-names': 'off', 
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
  prettierSkipFormatting,
];