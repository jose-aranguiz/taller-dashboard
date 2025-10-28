<template>
  <q-card style="width: 500px; max-width: 80vw;">
    <q-bar class="bg-primary text-white">
      <div class="text-h6">Historial del Trabajo #{{ trabajoId }}</div>
      <q-space />
      <q-btn dense flat icon="close" @click="$emit('close')"><q-tooltip>Cerrar</q-tooltip></q-btn>
    </q-bar>
    <q-separator />
    <q-card-section v-if="isLoading" class="text-center">
      <q-spinner color="primary" size="3em" />
    </q-card-section>
    <q-card-section v-else-if="historial.length">
      <q-timeline color="secondary">
        <q-timeline-entry
          v-for="evento in historial"
          :key="evento.id"
          :title="evento.estado.replace(/_/g, ' ')"
          :subtitle="formatLocalDate(evento.fecha_inicio)"
          icon="schedule"
          side="left"
        >
          <div>
            <strong>Duración:</strong> {{ calcularDuracion(evento.fecha_inicio, evento.fecha_fin) }}
            <div v-if="evento.estado === 'trabajo detenido'" class="q-mt-sm text-caption">
              <q-separator class="q-my-xs" />
              <div v-if="evento.motivo_detencion"><strong>Motivo:</strong> {{ evento.motivo_detencion }}</div>
              <div v-if="evento.detalle_motivo"><strong>Detalle:</strong> {{ evento.detalle_motivo }}</div>
              <div v-if="evento.fecha_eta"><strong>ETA:</strong> {{ formatLocalDate(evento.fecha_eta) }}</div>
            </div>
          </div>
        </q-timeline-entry>
      </q-timeline>
    </q-card-section>
    <q-card-section v-else>
      <div class="text-center text-grey-7">No hay historial para este trabajo.</div>
    </q-card-section>
  </q-card>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { Notify } from 'quasar'; // ✨ 1. Importar Notify
import { api } from 'boot/axios'; // ✨ 2. Importar 'api' en lugar de 'axios'
import { format, differenceInMinutes } from 'date-fns';
import { es } from 'date-fns/locale';

const props = defineProps({ trabajoId: Number });
defineEmits(['close']);

const historial = ref([]);
const isLoading = ref(true);

onMounted(async () => {
  try {
    // ✨ 3. Usar 'api' en lugar de 'axios'
    const response = await api.get(`/api/trabajos/${props.trabajoId}/historial`);
    historial.value = response.data;
  } catch (error) {
    // ✨ 4. Mejorar el manejo de errores
    console.error("Error al cargar historial:", error);
    if (error.response?.status !== 401) {
      Notify.create({
        type: 'negative',
        message: 'No se pudo cargar el historial.'
      });
    }
  } finally {
    isLoading.value = false;
  }
});

const formatLocalDate = (utcDate) => {
  if (!utcDate) return 'N/A';
  const localDate = new Date(utcDate);
  return format(localDate, "dd-MM-yyyy HH:mm", { locale: es });
};

const calcularDuracion = (inicio, fin) => {
    if (!fin) return 'En proceso...';
    const diff = differenceInMinutes(new Date(fin), new Date(inicio));
    if (diff < 0) return 'N/A';
    const days = Math.floor(diff / 1440);
    const hours = Math.floor((diff % 1440) / 60);
    const minutes = diff % 60;
    let result = '';
    if (days > 0) result += `${days}d `;
    if (hours > 0) result += `${hours}h `;
    if (minutes > 0 || result === '') result += `${minutes}m`;
    return result.trim() || 'Menos de 1m';
}
</script>