// src/composables/useWorkflow.ts

import { readonly } from 'vue'

/**
 * --------------------------------------------------------------------
 * 💡 GESTIÓN DE ESTADOS Y WORKFLOW DEL TALLER 💡
 * --------------------------------------------------------------------
 * Este "composable" centraliza toda la lógica de negocio relacionada
 * con los estados de los trabajos. Al tenerlo en un solo lugar,
 * aseguramos que componentes como la Tabla, el Kanban o los Detalles
 * usen exactamente las mismas reglas y colores.
 * --------------------------------------------------------------------
 */

// 1. ESTADOS: Definimos todos los estados posibles como un objeto.
export const ESTADOS = readonly({
  AGENDADO: 'agendado',
  ESPERA: 'espera de trabajo',
  EN_TRABAJO: 'en trabajo',
  DETENIDO: 'trabajo detenido',
  EN_LAVADO: 'en lavado',
  CONTROL_CALIDAD: 'control de calidad',
  LISTO_ENTREGA: 'listo para entrega',
  ENTREGADO: 'entregado al cliente'
})

// ✨ CREAMOS UN TIPO PERSONALIZADO:
// Esto crea un tipo que solo puede ser uno de los valores del objeto ESTADOS.
// Ej: 'agendado' | 'en trabajo' | etc.
type Estado = typeof ESTADOS[keyof typeof ESTADOS];

// 2. COLORES: Mapeamos cada estado a un color de la paleta de Quasar.
// ✨ APLICAMOS EL TIPO: Record<Estado, string> asegura que cada clave sea un Estado válido.
const colores: Record<Estado, string> = {
  [ESTADOS.AGENDADO]: 'grey-7',
  [ESTADOS.ESPERA]: 'orange-8',
  [ESTADOS.EN_TRABAJO]: 'blue-8',
  [ESTADOS.DETENIDO]: 'red-8',
  [ESTADOS.EN_LAVADO]: 'light-blue-5',
  [ESTADOS.CONTROL_CALIDAD]: 'teal',
  [ESTADOS.LISTO_ENTREGA]: 'green-8',
  [ESTADOS.ENTREGADO]: 'dark'
}

// 3. TRANSICIONES: Definimos el flujo de trabajo.
// ✨ APLICAMOS EL TIPO: Record<Estado, Estado[]> asegura que tanto la clave como los valores del array sean Estados válidos.
const transicionesValidas: Record<Estado, Estado[]> = {
  [ESTADOS.AGENDADO]: [ESTADOS.ESPERA],
  [ESTADOS.ESPERA]: [ESTADOS.EN_TRABAJO, ESTADOS.EN_LAVADO],
  [ESTADOS.EN_TRABAJO]: [ESTADOS.DETENIDO, ESTADOS.CONTROL_CALIDAD, ESTADOS.EN_LAVADO],
  [ESTADOS.DETENIDO]: [ESTADOS.EN_TRABAJO],
  [ESTADOS.EN_LAVADO]: [ESTADOS.CONTROL_CALIDAD],
  [ESTADOS.CONTROL_CALIDAD]: [ESTADOS.LISTO_ENTREGA, ESTADOS.EN_TRABAJO],
  [ESTADOS.LISTO_ENTREGA]: [ESTADOS.ENTREGADO],
  [ESTADOS.ENTREGADO]: [] // Es un estado final.
}

/**
 * Función principal del composable que exportamos.
 */
export function useWorkflow () {
  /**
   * Obtiene el color asociado a un estado.
   */
  // ✨ TIPAMOS EL PARÁMETRO Y EL VALOR DE RETORNO
  const getEstadoColor = (estado: Estado): string => colores[estado] || 'primary'

  /**
   * Obtiene la lista de los próximos estados válidos.
   */
  // ✨ TIPAMOS EL PARÁMETRO Y EL VALOR DE RETORNO
  const getNextStates = (estadoActual: Estado): Estado[] => transicionesValidas[estadoActual] || []

  return {
    ESTADOS,
    getEstadoColor,
    getNextStates
  }
}