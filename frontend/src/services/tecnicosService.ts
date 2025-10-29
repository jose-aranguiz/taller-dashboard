import { api } from 'src/boot/axios';
import { Notify } from 'quasar';

// Definimos una interfaz simple para el técnico (¡TypeScript!)
interface Tecnico {
  id: number;
  nombre: string;
  // Agrega aquí otros campos si los hubiera, ej: especialidad
}

// Interfaz para la creación (no se necesita ID)
interface TecnicoCreate {
  nombre: string;
}

export const tecnicosService = {
  /**
   * Obtiene la lista completa de técnicos.
   */
  getTecnicos: async (): Promise<Tecnico[]> => {
    try {
      const response = await api.get<Tecnico[]>('/tecnicos/');
      return response.data;
    } catch (error) {
      Notify.create({
        type: 'negative',
        message: 'Error al cargar los técnicos',
      });
      console.error('Error fetching tecnicos:', error);
      throw error; // Propagamos el error para que el componente pueda reaccionar
    }
  },

  /**
   * Crea un nuevo técnico.
   */
  createTecnico: async (tecnicoData: TecnicoCreate): Promise<Tecnico> => {
    try {
      const response = await api.post<Tecnico>('/tecnicos/', tecnicoData);
      Notify.create({
        type: 'positive',
        message: 'Técnico creado exitosamente',
      });
      return response.data;
    } catch (error) {
      Notify.create({
        type: 'negative',
        message: 'Error al crear el técnico',
      });
      console.error('Error creating tecnico:', error);
      throw error;
    }
  },

  /**
   * Elimina un técnico por su ID.
   */
  deleteTecnico: async (id: number): Promise<void> => {
    try {
      await api.delete(`/tecnicos/${id}`);
      Notify.create({
        type: 'positive',
        message: 'Técnico eliminado',
      });
    } catch (error) {
      Notify.create({
        type: 'negative',
        message: 'Error al eliminar el técnico. (Asegúrate de que no esté asignado a un trabajo)',
      });
      console.error(`Error deleting tecnico ${id}:`, error);
      throw error;
    }
  },
};