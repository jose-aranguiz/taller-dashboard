<template>
  <div>
    <q-table
      :rows="trabajos"
      :columns="columnasVisibles"
      row-key="id"
      :loading="isLoading"
      v-model:pagination="pagination"
      @request="trabajosStore.handleRequest"
      flat
      bordered
      dense
    >
      <template v-slot:body="props">
        <q-tr :props="props" class="relative-position" :class="getAntiguedadClass(props.row.dias_de_estadia_activa)">
          <q-inner-loading
            :showing="updatingIds.has(props.row.id)"
            label-class="text-teal"
            label-style="font-size: 1.1em"
          />

          <q-td key="actions" :props="props">
            <q-btn flat round dense icon="history" @click="abrirDialogoHistorial(props.row)">
              <q-tooltip>Ver Historial de Tiempos</q-tooltip>
            </q-btn>
            <q-btn flat round dense icon="visibility" @click="emit('detalle', props.row.id)">
              <q-tooltip>Ver Detalles</q-tooltip>
            </q-btn>
          </q-td>

          <q-td key="alerta_eta" :props="props">
            <q-chip
              v-if="getEtaStatus(props.row.eta_fecha)"
              dense square
              :color="getEtaStatus(props.row.eta_fecha)!.color"
              text-color="white"
              class="text-weight-bold"
            >
              {{ getEtaStatus(props.row.eta_fecha)!.label }}
              <q-tooltip v-if="props.row.eta_motivo">{{ props.row.eta_motivo }} - {{ format(new Date(props.row.eta_fecha), 'dd/MM/yyyy HH:mm') }}</q-tooltip>
            </q-chip>
          </q-td>

          <q-td key="fecha_creacion_pedido" :props="props">{{ props.row.fecha_creacion_pedido ? new Date(props.row.fecha_creacion_pedido).toLocaleDateString('es-CL') : 'N/A' }}</q-td>
          <q-td key="pedido_dbm" :props="props"><span class="text-weight-bold text-primary">{{ props.row.pedido_dbm }}</span></q-td>
          <q-td key="tipo_pedido" :props="props">{{ props.row.tipo_pedido }}</q-td>
          <q-td key="patente" :props="props">{{ props.row.patente }}</q-td>
          <q-td key="cliente_nombre" :props="props">{{ props.row.cliente_nombre }}</q-td>
          <q-td key="detalle_pedido" :props="props" class="cursor-pointer">
            <div class="truncate-text">{{ props.row.detalle_pedido || 'Sin descripción' }}</div>
            <q-popup-edit
              :model-value="props.row.detalle_pedido"
              v-slot="scope"
              @save="(newVal) => trabajosStore.updateDescripcion(props.row.id, newVal)"
              title="Editar Descripción" buttons label-set="Guardar" label-cancel="Cancelar"
              :validate="val => val && val.length > 0"
            >
              <q-input type="textarea" v-model="scope.value" dense autofocus counter @keyup.enter.stop />
            </q-popup-edit>
          </q-td>
          <q-td key="dias_de_estadia_activa" :props="props" class="text-center">
            <q-chip dense square :color="getAntiguedadColor(props.row.dias_de_estadia_activa)" text-color="white" class="text-weight-bold">
              {{ props.row.dias_de_estadia_activa }}
            </q-chip>
          </q-td>
          <q-td key="asesor_servicio" :props="props">{{ props.row.asesor_servicio }}</q-td>
          <q-td key="tecnico_asignado" :props="props">
            <span v-if="props.row.tecnico_asignado">{{ props.row.tecnico_asignado.nombre_completo }}</span>
            <q-chip v-else dense square icon="person_add" label="No asignado" color="grey-6" text-color="white" />
          </q-td>
          <q-td key="estado_actual" :props="props">
            <q-btn-dropdown
              split dense unelevated size="sm"
              :color="getEstadoColor(props.row.estado_actual)"
              :label="props.row.estado_actual.replace(/_/g, ' ')"
              @click="abrirDialogoHistorial(props.row)"
              class="full-width"
            >
              <q-tooltip anchor="top middle" self="bottom middle" :offset="[10, 10]">
                Clic para ver historial. Use la flecha para cambiar estado.
              </q-tooltip>
              <q-list dense>
                <q-item
                  v-for="estado in getNextStates(props.row.estado_actual)"
                  :key="estado" clickable v-close-popup
                  @click="confirmarUpdateEstado({ id: props.row.id, nuevo_estado: estado })"
                >
                  <q-item-section><q-item-label>{{ estado.replace(/_/g, ' ') }}</q-item-label></q-item-section>
                </q-item>
              </q-list>
            </q-btn-dropdown>
          </q-td>
        </q-tr>
      </template>
      
      <template v-slot:no-data>
        <div class="full-width row flex-center text-grey q-gutter-sm q-pa-lg">
          <q-icon size="2em" name="sentiment_dissatisfied" />
          <span>No se encontraron trabajos para mostrar.</span>
        </div>
      </template>
      
      <template v-slot:loading>
        <q-inner-loading showing color="primary" />
        <q-tr v-for="n in 5" :key="n">
          <q-td v-for="col in columnasVisibles" :key="col.name" class="text-left">
            <q-skeleton animation="blink" type="text" width="85%" />
          </q-td>
        </q-tr>
      </template>
    </q-table>

    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useQuasar } from 'quasar';
import { storeToRefs } from 'pinia';
import { useTrabajosStore } from 'stores/trabajosStore';
import { useWorkflow, Estado } from 'src/composables/useWorkflow';
import { format, isPast, isToday, isTomorrow, formatDistanceToNowStrict } from 'date-fns';
import { es } from 'date-fns/locale';
import MotivoDetencionDialog from 'components/MotivoDetencionDialog.vue';
import AsignarTecnicoDialog from 'components/AsignarTecnicoDialog.vue';
// ✨ REFACTORIZACIÓN 1: Importamos el componente de diálogo centralizado
import HistorialTrabajoDialog from 'components/HistorialTrabajoDialog.vue';

// --- Interfaces de Tipos ---
interface EstadoHistorial {
  estado: Estado;
  fecha: string;
  duracion?: string; // Ej: "2 días, 3 horas"
}

interface Trabajo {
  id: number;
  dias_de_estadia_activa: number | null;
  eta_fecha: string | null;
  eta_motivo: string | null;
  fecha_creacion_pedido: string | null;
  tecnico_asignado: { nombre_completo: string } | null;
  estado_actual: Estado;
  pedido_dbm: string;
  historial_estados?: EstadoHistorial[]; // ✨ NUEVO: Para la línea de tiempo
  [key: string]: unknown;
}

interface Props {
  visibleColumns: string[]
}

// --- Props y Emits ---
const props = defineProps<Props>();
const emit = defineEmits<{
  (e: 'detalle', id: number | string): void;
}>();

// --- Composables y Stores ---
const $q = useQuasar();
const trabajosStore = useTrabajosStore();
const { getEstadoColor, getNextStates, ESTADOS } = useWorkflow();
const { trabajos, isLoading, pagination, updatingIds } = storeToRefs(trabajosStore);

// --- ✨ LÓGICA PARA EL DIÁLOGO DE HISTORIAL (Refactorizada) ---

// ✨ REFACTORIZACIÓN 2: Eliminamos los 'ref's de 'mostrarDialogoHistorial' y 'trabajoSeleccionado'

// ✨ REFACTORIZACIÓN 3: La función ahora usa $q.dialog para llamar al componente reutilizable
const abrirDialogoHistorial = (trabajo: Trabajo) => {
  $q.dialog({
    component: HistorialTrabajoDialog,
    componentProps: {
      trabajoId: trabajo.id
    }
  });
};

// --- Lógica Principal del Componente ---
const confirmarUpdateEstado = async (payload: { id: number | string, nuevo_estado: string }) => {
  let dialogData: Record<string, unknown> = {};
  let proceed = true;

  try {
    if (payload.nuevo_estado === ESTADOS.DETENIDO) {
      dialogData = await new Promise((resolve, reject) => {
        $q.dialog({
          component: MotivoDetencionDialog,
          componentProps: { trabajoId: payload.id }
        }).onOk(resolve).onCancel(() => reject(new Error('Dialogo cancelado')));
      });
    } else if (payload.nuevo_estado === ESTADOS.EN_TRABAJO) {
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
    const finalPayload = { ...payload, ...dialogData };
    if (payload.nuevo_estado === ESTADOS.ENTREGADO) {
      $q.dialog({
        title: 'Confirmar Acción',
        message: `¿Está seguro de que desea marcar el trabajo como <strong>"${payload.nuevo_estado.replace(/_/g, ' ')}"</strong>?`,
        html: true,
        cancel: { label: 'Cancelar', flat: true },
        ok: { label: 'Confirmar', color: 'primary' },
      }).onOk(() => {
        trabajosStore.updateEstado(payload.id as number, finalPayload);
      });
    } else {
      trabajosStore.updateEstado(payload.id as number, finalPayload);
    }
  }
};

// --- Funciones de Utilidad Visual ---
const getAntiguedadClass = (dias: number | null): string => {
  if (dias === null) return '';
  if (dias > 5) return 'alerta-peligro';
  if (dias > 2) return 'alerta-advertencia';
  return '';
};

const getAntiguedadColor = (dias: number | null): string => {
  if (dias === null) return 'grey-7';
  if (dias > 5) return 'red-8';
  if (dias > 2) return 'orange-8';
  return 'grey-7';
};

// ✨ FUNCIÓN DE ALERTAS ETA ACTUALIZADA
const getEtaStatus = (etaFecha: string | null): { color: string, label: string } | null => {
  if (!etaFecha) return null; // No retorna nada si no hay fecha
  const etaDate = new Date(etaFecha);

  if (isPast(etaDate)) {
    return { color: 'red-8', label: 'VENCIDO' };
  }
  if (isToday(etaDate) || isTomorrow(etaDate)) {
    const distance = formatDistanceToNowStrict(etaDate, { locale: es, addSuffix: true });
    return { color: 'orange-8', label: `Vence ${distance.replace('en', '')}` };
  }
  return { color: 'green-8', label: `En Plazo` };
};

// --- Columnas de la Tabla ---
const allColumns = [
    { name: 'actions', label: 'Acciones', align: 'center' as const, style: 'width: 100px;' },
    { name: 'alerta_eta', label: 'Alerta ETA', align: 'center' as const, style: 'width: 150px;' },
    { name: 'fecha_creacion_pedido', label: 'Fecha Pedido', field: 'fecha_creacion_pedido', align: 'left' as const, sortable: true },
    { name: 'pedido_dbm', label: 'Pedido DBM', field: 'pedido_dbm', align: 'left' as const, sortable: true },
    { name: 'tipo_pedido', label: 'Tipo Pedido', field: 'tipo_pedido', align: 'left' as const },
    { name: 'patente', label: 'Patente', field: 'patente', align: 'left' as const },
    { name: 'cliente_nombre', label: 'Cliente', field: 'cliente_nombre', align: 'left' as const, style: 'min-width: 200px;' },
    { name: 'detalle_pedido', label: 'Descripción', field: 'detalle_pedido', align: 'left' as const, style: 'white-space: normal; min-width: 250px;' },
    { name: 'dias_de_estadia_activa', label: 'Días Activos', field: 'dias_de_estadia_activa', align: 'center' as const, sortable: true },
    { name: 'asesor_servicio', label: 'Asesor', field: 'asesor_servicio', align: 'left' as const, style: 'min-width: 180px;' },
    { name: 'tecnico_asignado', label: 'Técnico', field: (row: Trabajo) => (row.tecnico_asignado ? row.tecnico_asignado.nombre_completo : null), align: 'left' as const, style: 'min-width: 180px;' },
    { name: 'estado_actual', label: 'Estado', field: 'estado_actual', align: 'center' as const, style: 'width: 180px;' },
];

const columnasVisibles = computed(() =>
  allColumns.filter(col => props.visibleColumns.includes(col.name))
);
</script>

<style scoped>
.truncate-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 250px;
}

.alerta-advertencia {
  background-color: rgba(255, 193, 7, 0.1) !important;
}

.alerta-peligro {
  background-color: rgba(239, 83, 80, 0.1) !important;
}

.q-tr {
  transition: background-color 0.3s ease;
}
</style>