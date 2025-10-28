// src/services/trabajosService.ts

import { api } from 'boot/axios';
import { AxiosResponse } from 'axios'; // ✨ Importamos el tipo de respuesta de Axios

/**
 * Este objeto encapsula todas las llamadas a la API relacionadas con los trabajos.
 */
export const trabajosService = {
  /**
   * Obtiene la lista de trabajos activos con filtros y paginación.
   */
  getAll(params: Record<string, any>): Promise<AxiosResponse<any>> { // ✨ Tipamos los params y el retorno
    return api.get('/trabajos/', { params });
  },

  /**
   * Actualiza el estado de un trabajo específico.
   */
  updateEstado(id: number | string, payload: Record<string, any>): Promise<AxiosResponse<any>> { // ✨ Tipamos id, payload y el retorno
    return api.patch(`/trabajos/${id}/estado`, payload);
  },

  /**
   * Actualiza los detalles de un trabajo (como la descripción).
   */
  updateDetalles(id: number | string, payload: Record<string, any>): Promise<AxiosResponse<any>> { // ✨ Tipamos id, payload y el retorno
    return api.patch(`/trabajos/${id}`, payload);
  },

  /**
   * Obtiene el historial de estados de un trabajo.
   */
  getHistorial(id: number | string): Promise<AxiosResponse<any>> { // ✨ Tipamos id y el retorno
    return api.get(`/trabajos/${id}/historial`);
  }
};