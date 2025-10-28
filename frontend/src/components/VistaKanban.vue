<template>
  <q-scroll-area style="height: 80vh; width: 100%;">
    <div v-if="!isLoading" class="kanban-board row no-wrap q-col-gutter-md q-pa-sm">
      <div v-for="columna in columnasKanban" :key="columna.estado" class="col-auto" style="width: 290px;">
        <q-card class="column-card full-height">
          <q-card-section class="bg-grey-2 text-center sticky-header">
            <div class="text-subtitle1 text-weight-medium text-capitalize text-grey-8">{{ columna.estado.replace(/_/g, ' ') }}
              <q-badge color="primary" align="middle" class="q-ml-sm">{{ columna.trabajos.length }}</q-badge>
            </div>
          </q-card-section>
          
          <draggable
            :list="columna.trabajos"
            group="trabajos"
            item-key="id"
            class="kanban-column"
            @end="onDragEnd"
            :data-estado-destino="columna.estado"
          >
            <template #item="{ element }">
              <q-card class="job-card cursor-pointer" dense flat bordered @click="emit('detalle', element.id)">
                <q-card-section class="q-pa-sm">
                  <div class="row items-center no-wrap q-mb-xs">
                    <q-icon name="circle" :color="getSlaColor(element.dias_de_estadia_activa)" class="q-mr-sm" size="xs" />
                    <div class="text-weight-bold text-center col">{{ element.patente || 'Sin Patente' }}</div>
                  </div>
                  <q-separator />
                  <div class="row items-center justify-center q-gutter-md q-mt-sm text-grey-8">
                    <q-icon name="person" size="sm" class="cursor-pointer">
                      <q-tooltip anchor="bottom middle" self="top middle">
                        <strong>Cliente:</strong> {{ element.cliente_nombre || 'N/A' }}
                      </q-tooltip>
                    </q-icon>
                    <q-icon name="support_agent" size="sm" class="cursor-pointer">
                      <q-tooltip anchor="bottom middle" self="top middle">
                        <strong>Asesor:</strong> {{ element.asesor_servicio || 'N/A' }}
                      </q-tooltip>
                    </q-icon>
                    <q-icon name="event" size="sm" class="cursor-pointer">
                      <q-tooltip anchor="bottom middle" self="top middle">
                        <strong>Creado:</strong> {{ formatDate(element.fecha_creacion_pedido) }}
                      </q-tooltip>
                    </q-icon>
                  </div>
                </q-card-section>
              </q-card>
            </template>
          </draggable>
        </q-card>
      </div>
    </div>
    
    <div v-else class="kanban-board row no-wrap q-col-gutter-md q-pa-sm">
      <div v-for="n in 4" :key="n" class="col-auto" style="width: 290px;">
        <q-card class="column-card full-height">
          <q-card-section class="bg-grey-2 text-center sticky-header">
            <q-skeleton animation="blink" type="text" width="60%" class="q-mx-auto" />
          </q-card-section>
          <div class="q-pa-sm">
            <q-card v-for="i in 3" :key="i" class="q-mb-sm" flat bordered>
              <q-item>
                <q-item-section>
                  <q-item-label>
                    <q-skeleton type="text" />
                  </q-item-label>
                  <q-item-label caption>
                    <q-skeleton type="text" width="40%" />
                  </q-item-label>
                </q-item-section>
              </q-item>
            </q-card>
          </div>
        </q-card>
      </div>
    </div>
  </q-scroll-area>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useQuasar } from 'quasar';
import draggable from 'vuedraggable';
import { storeToRefs } from 'pinia';
import { useTrabajosStore } from 'stores/trabajosStore';
import { useWorkflow } from 'src/composables/useWorkflow';
import MotivoDetencionDialog from 'components/MotivoDetencionDialog.vue';
import AsignarTecnicoDialog from 'components/AsignarTecnicoDialog.vue';

// Interfaces para tipado estricto
interface Trabajo {
  id: number;
  estado_actual: string;
  dias_de_estadia_activa: number | null;
  patente: string | null;
  cliente_nombre: string | null;
  asesor_servicio: string | null;
  fecha_creacion_pedido: string | null;
}

interface DragEndEvent {
  item: {
    __draggable_context: {
      element: Trabajo;
    };
  };
  to: HTMLElement;
  from: HTMLElement;
}

const emit = defineEmits<{
  (e: 'detalle', id: number | string): void;
}>();

const $q = useQuasar();
const trabajosStore = useTrabajosStore();
const { ESTADOS } = useWorkflow();

const { trabajos, isLoading } = storeToRefs(trabajosStore);

const columnasKanban = computed(() => {
  const ordenDeseado = ["agendado", "espera de trabajo", "en trabajo", "trabajo detenido", "en lavado", "control de calidad", "listo para entrega"];
  const trabajosValidos = trabajos.value.filter((t): t is Trabajo => t && typeof t.id !== 'undefined');
  
  return ordenDeseado.map(estado => ({
    estado,
    trabajos: trabajosValidos.filter(t => t.estado_actual === estado)
  }));
});

const getSlaColor = (dias: number | null | undefined): string => {
  if (dias === null || typeof dias === 'undefined') return 'grey-5';
  if (dias <= 2) return 'green';
  if (dias <= 4) return 'orange';
  return 'red';
};

const formatDate = (value: string | null): string => {
  if (!value) return 'N/A';
  const options: Intl.DateTimeFormatOptions = { year: 'numeric', month: '2-digit', day: '2-digit' };
  return new Date(value).toLocaleDateString('es-CL', options);
};

const onDragEnd = async (event: DragEndEvent) => {
  const trabajoId = event.item.__draggable_context.element.id;
  const nuevoEstado = event.to.getAttribute('data-estado-destino');
  const estadoAnterior = event.from.getAttribute('data-estado-destino');
  
  if (!trabajoId || !nuevoEstado || nuevoEstado === estadoAnterior) {
    await trabajosStore.fetchTrabajos(); // Revierte el cambio visual si es inválido
    return;
  }

  let dialogData: Record<string, unknown> = {};
  let proceed = true;

  try {
    if (nuevoEstado === ESTADOS.DETENIDO) {
      dialogData = await new Promise((resolve, reject) => {
        $q.dialog({
          component: MotivoDetencionDialog,
          componentProps: { trabajoId: trabajoId }
        }).onOk(resolve).onCancel(() => reject(new Error('Dialogo cancelado')));
      });
    } else if (nuevoEstado === ESTADOS.EN_TRABAJO) {
      dialogData = await new Promise((resolve, reject) => {
        $q.dialog({
          component: AsignarTecnicoDialog
        }).onOk(resolve).onCancel(() => reject(new Error('Dialogo cancelado')));
      });
    }
  } catch {
    proceed = false;
  }
  
  if (proceed) {
    const payload = { nuevo_estado: nuevoEstado, ...dialogData };
    try {
      await trabajosStore.updateEstado(trabajoId, payload);
    } catch {
      // Si la API falla, el store notifica y revertimos el cambio visual
      await trabajosStore.fetchTrabajos();
    }
  } else {
    // Si el usuario cancela un diálogo, revertimos el cambio visual
    await trabajosStore.fetchTrabajos();
  }
};
</script>

<style scoped>
.kanban-board { align-items: flex-start; }
.column-card { display: flex; flex-direction: column; background-color: #f4f5f7; border-radius: 8px; }
.kanban-column { min-height: 65vh; flex-grow: 1; padding: 8px; }
.job-card { margin-bottom: 8px; border-radius: 4px; transition: box-shadow 0.2s, border-color 0.2s; background-color: white; }
.job-card:hover { box-shadow: 0 4px 8px rgba(0,0,0,0.1); border-left: 3px solid var(--q-primary); }
.sticky-header { position: sticky; top: 0; z-index: 1; border-bottom: 2px solid #e0e0e0; }
</style>