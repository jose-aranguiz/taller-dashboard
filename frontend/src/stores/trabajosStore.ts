import { defineStore } from 'pinia';
import { Notify } from 'quasar';
import { trabajosService } from 'src/services/trabajosService';
import type { Estado } from 'src/composables/useWorkflow';

// --- DEFINICIÓN DE TIPOS ---
// ... (los tipos se mantienen igual)
interface EstadoHistorial {
  estado: Estado;
  fecha: string;
  duracion?: string;
}
interface Trabajo {
  id: number;
  estado_actual: Estado;
  historial_estados?: EstadoHistorial[];
  [key: string]: any;
}
interface TrabajosState {
  trabajos: Trabajo[];
  isLoading: boolean;
  updatingIds: Set<number>;
  pagination: {
    sortBy: string;
    descending: boolean;
    page: number;
    rowsPerPage: number;
    rowsNumber: number;
  };
  filters: {
    search: string;
    estado_actual: Estado | null;
    asesor_servicio: string | null;
    dateRange: { from: string; to: string } | null;
  };
  opcionesAsesor: string[];
}

export const useTrabajosStore = defineStore('trabajos', {
  state: (): TrabajosState => ({
    trabajos: [],
    isLoading: false,
    updatingIds: new Set(),
    pagination: {
      sortBy: 'fecha_creacion_pedido',
      descending: true,
      page: 1,
      rowsPerPage: 15,
      rowsNumber: 0
    },
    filters: {
      search: '',
      estado_actual: null,
      asesor_servicio: null,
      dateRange: null
    },
    opcionesAsesor: []
  }),

  getters: {
    formatDateRange: (state) => {
      if (!state.filters.dateRange) return '';
      const { from, to } = state.filters.dateRange;
      return `${from} - ${to}`;
    }
  },

  actions: {
    /**
     * Obtiene la lista de trabajos desde la API aplicando paginación y filtros.
     */
    async fetchTrabajos() {
      this.isLoading = true;
      try {
        const params = {
          page: this.pagination.page,
          size: this.pagination.rowsPerPage,
          sort_by: this.pagination.sortBy,
          sort_order: this.pagination.descending ? 'desc' : 'asc',
          search: this.filters.search || undefined,
          estado_actual: this.filters.estado_actual || undefined,
          asesor_servicio: this.filters.asesor_servicio || undefined,
          fecha_inicio: this.filters.dateRange?.from || undefined,
          fecha_fin: this.filters.dateRange?.to || undefined
        };

        const response = await trabajosService.getAll(params);
        this.trabajos = response.data.items;
        this.pagination.rowsNumber = response.data.total;
        
        if (response.data.items.length > 0) {
           this.opcionesAsesor = [...new Set(response.data.items.map(item => item.asesor_servicio).filter(Boolean))];
        }

      } catch (err: any) {
        if (err.response?.status !== 401) {
          Notify.create({ type: 'negative', message: 'No se pudieron cargar los trabajos.' });
        }
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Actualiza el estado de un trabajo específico.
     */
    async updateEstado(id: number, payload: Record<string, any>) {
      this.updatingIds.add(id);
      try {
        const response = await trabajosService.updateEstado(id, payload);
        Notify.create({ type: 'positive', message: 'Estado actualizado correctamente.' });

        if (payload.nuevo_estado === 'entregado al cliente') {
          this.trabajos = this.trabajos.filter(t => t.id !== id);
          this.pagination.rowsNumber--;
        } else {
          const trabajoIndex = this.trabajos.findIndex(t => t.id === id);
          if (trabajoIndex !== -1) {
            
            // ✨ CORRECCIÓN PARA LAS ALERTAS ETA:
            // En lugar de un reemplazo directo ( this.trabajos[trabajoIndex] = response.data; ),
            // fusionamos el estado anterior, la respuesta del servidor y el payload.
            // Esto asegura que campos como 'eta_fecha' del payload se mantengan
            // aunque el 'response.data' del servidor no los incluya.
            this.trabajos[trabajoIndex] = {
              ...this.trabajos[trabajoIndex], // 1. Mantenemos los datos antiguos
              ...response.data,             // 2. Sobrescribimos con la respuesta del servidor (ej. estado_actual)
              ...payload                    // 3. Sobrescribimos con el payload (ej. eta_fecha, eta_motivo)
            };
          }
        }
      } catch (error: any) {
        Notify.create({ type: 'negative', message: 'No se pudo actualizar el estado.', caption: error.response?.data?.detail });
        throw error; // Relanzamos el error para que el componente pueda manejarlo si es necesario.
      } finally {
        this.updatingIds.delete(id);
      }
    },

    /**
     * Actualiza la descripción de la tarea de un trabajo.
     */
    async updateDescripcion(id: number, descripcion: string) {
        this.updatingIds.add(id);
        try {
          const response = await trabajosService.updateDetalles(id, { detalle_pedido: descripcion });
          Notify.create({ type: 'positive', message: 'Descripción actualizada.' });

          const trabajoIndex = this.trabajos.findIndex(t => t.id === id);
          if (trabajoIndex !== -1) {
              // ✨ BUENA PRÁCTICA: Hacemos la misma fusión aquí por consistencia.
              this.trabajos[trabajoIndex] = {
                ...this.trabajos[trabajoIndex],
                ...response.data,
                detalle_pedido: descripcion
              };
          }
        } catch (error: any) {
            Notify.create({ type: 'negative', message: 'Error al actualizar la descripción.', caption: error.response?.data?.detail });
        } finally {
            this.updatingIds.delete(id);
        }
    },
    
    /**
     * Obtiene el historial detallado de estados para un trabajo específico.
     */
    async fetchHistorial(id: number): Promise<EstadoHistorial[] | null> {
      try {
        const response = await trabajosService.getHistorial(id);
        const trabajoIndex = this.trabajos.findIndex(t => t.id === id);
        if (trabajoIndex !== -1) {
          this.trabajos[trabajoIndex].historial_estados = response.data;
        }
        return response.data;
      } catch (error: any) {
        if (error.response?.status !== 401) {
          Notify.create({ type: 'negative', message: 'No se pudo cargar el historial del trabajo.' });
        }
        return null;
      }
    },

    /**
     * Limpia todos los filtros aplicados y vuelve a cargar los datos.
     */
    limpiarFiltros() {
      this.filters = { search: '', estado_actual: null, asesor_servicio: null, dateRange: null };
      this.fetchTrabajos();
    },

    /**
     * Maneja las peticiones de la QTable (paginación, ordenamiento).
     */
    handleRequest(props: { pagination: TrabajosState['pagination'] }) {
      this.pagination = props.pagination;
      this.fetchTrabajos();
    }
  }
});