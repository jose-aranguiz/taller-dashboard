<template>
  <q-dialog ref="dialogRef" @hide="onDialogHide">
    <q-card style="width: 500px; max-width: 80vw;">
      <q-bar class="bg-primary text-white">
        <div class="text-h6">Cronología del Trabajo #{{ trabajoId }}</div>
        <q-space />
        <q-btn dense flat icon="close" @click="onDialogCancel"><q-tooltip>Cerrar</q-tooltip></q-btn>
      </q-bar>
      <q-separator />

      <q-card-section v-if="isLoading" class="text-center q-pa-lg">
        <q-spinner color="primary" size="3em" />
        <div class="q-mt-md">Cargando historial...</div>
      </q-card-section>

      <q-card-section v-else-if="historial.length" style="max-height: 60vh" class="scroll">
        <q-timeline color="secondary">
          <q-timeline-entry
            v-for="evento in historial"
            :key="evento.id"
            :title="evento.estado.replace(/_/g, ' ')"
            :subtitle="formatLocalDate(evento.fecha_inicio)"
            icon="event"
            side="left"
          >
            <div>
              <strong>Duración:</strong> {{ calcularDuracion(evento.fecha_inicio, evento.fecha_fin) }}
              <div v-if="evento.estado === 'trabajo detenido'" class="q-mt-sm text-caption text-grey-8">
                <q-separator class="q-my-xs" />
                <div v-if="evento.motivo_detencion"><strong>Motivo:</strong> {{ evento.motivo_detencion }}</div>
                <div v-if="evento.detalle_motivo"><strong>Detalle:</strong> {{ evento.detalle_motivo }}</div>
                <div v-if="evento.fecha_eta"><strong>ETA:</strong> {{ formatLocalDate(evento.fecha_eta) }}</div>
              </div>
            </div>
          </q-timeline-entry>
        </q-timeline>
      </q-card-section>

      <q-card-section v-else class="q-pa-lg">
        <div class="text-center text-grey-7">
          <q-icon name="info" size="2em" class="q-mb-sm" />
          <div>No hay historial de estados para este trabajo.</div>
        </div>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useDialogPluginComponent, Notify } from 'quasar';
import { formatDistanceStrict } from 'date-fns';
import { es } from 'date-fns/locale';
// ✨ CORRECCIÓN: Importamos el servicio en lugar de 'api'
import { trabajosService } from 'src/services/trabajosService';

const props = defineProps({
  trabajoId: [Number, String]
});

// ✨ CORRECCIÓN: Esta línea faltaba y causaba el error 'unmount'
defineEmits([...useDialogPluginComponent.emits]);

const { dialogRef, onDialogHide, onDialogCancel } = useDialogPluginComponent();
const historial = ref([]);
const isLoading = ref(true);

onMounted(async () => {
  if (!props.trabajoId) {
    isLoading.value = false;
    return;
  }
  try {
    // ✨ CORRECCIÓN: Usamos el servicio para obtener el historial
    const response = await trabajosService.getHistorial(props.trabajoId);
    historial.value = response.data;
  } catch (error) {
    console.error("Error al cargar historial:", error);
    Notify.create({
      type: 'negative',
      message: 'No se pudo cargar el historial del trabajo.'
    });
  } finally {
    isLoading.value = false;
  }
});

const formatLocalDate = (utcDateString) => {
  if (!utcDateString || typeof utcDateString !== 'string') return 'N/A';
  const correctedUtcString = utcDateString.endsWith('Z') ? utcDateString : utcDateString + 'Z';
  const date = new Date(correctedUtcString);
  
  const options = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
    timeZone: 'America/Santiago'
  };

  return new Intl.DateTimeFormat('es-CL', options).format(date).replace('a las', '');
};

const calcularDuracion = (inicio, fin) => {
    if (!fin) return 'En proceso...';
    return formatDistanceStrict(new Date(fin), new Date(inicio), { locale: es, roundingMethod: 'ceil' });
}
</script>