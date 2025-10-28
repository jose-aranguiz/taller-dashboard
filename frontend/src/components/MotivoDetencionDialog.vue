<template>
  <q-dialog ref="dialogRef" @hide="onDialogHide">
    <q-card class="q-dialog-plugin" style="width: 500px; max-width: 80vw;">
      <q-form @submit.prevent="onOKClick">
        <q-card-section class="bg-primary text-white">
          <div class="text-h6">Detener Trabajo #{{ trabajoId }}</div>
        </q-card-section>

        <q-card-section class="q-gutter-md">
          <q-select
            v-model="motivoDetencion"
            :options="opcionesMotivo"
            label="Motivo de la detención"
            outlined
            :rules="[val => !!val || 'El motivo es requerido']"
            autofocus
          />

          <div :key="motivoDetencion">
            <q-input
              v-if="motivoDetencion === 'Espera de Aprobación Cliente'"
              outlined
              v-model="formattedEta"
              label="Fecha Límite de Aprobación"
              :hint="`Máximo 2 días hábiles. Límite: ${formattedMaxDate}`"
              readonly
            >
              <template v-slot:append>
                <q-icon name="event" class="cursor-pointer">
                  <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                    <q-date v-model="fechaETA" mask="YYYY-MM-DD" :options="dateOptionsAprobacion" />
                  </q-popup-proxy>
                </q-icon>
              </template>
            </q-input>

            <q-banner v-if="motivoDetencion === 'Espera de Repuesto a Pedido'" class="bg-grey-2">
              <template v-slot:avatar><q-icon name="schedule" color="primary" /></template>
              <div class="text-caption">La alerta se programará automáticamente para:</div>
              <div class="text-weight-bold">{{ formattedEta }}</div>
            </q-banner>

            <q-input
              v-if="motivoDetencion === 'VOR'"
              outlined
              readonly
              label="Fecha y Hora ETA (VOR)"
              v-model="formattedEta"
            >
              <template v-slot:append>
                <q-icon name="event" class="cursor-pointer">
                  <q-popup-proxy ref="etaPopupProxy" cover>
                    <div class="row items-start">
                      <q-date v-model="fechaETA" mask="YYYY-MM-DD HH:mm" />
                      <q-time v-model="fechaETA" mask="YYYY-MM-DD HH:mm" format24h @update:model-value="etaPopupProxy.hide()" />
                    </div>
                  </q-popup-proxy>
                </q-icon>
              </template>
            </q-input>
          </div>

          <q-input
            v-model="detalleMotivo"
            label="Detalle Adicional (Opcional)"
            outlined
            type="textarea"
            autogrow
          />
        </q-card-section>

        <q-card-actions align="right" class="q-pa-md">
          <q-btn flat label="Cancelar" @click="onDialogCancel" />
          <q-btn type="submit" color="primary" label="Confirmar Detención" :disable="!motivoDetencion" />
        </q-card-actions>
      </q-form>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useDialogPluginComponent } from 'quasar';
import { format, parseISO, startOfToday } from 'date-fns';
import { es } from 'date-fns/locale';
import { useDateHelpers } from '../composables/useDateHelpers';

defineProps({
  trabajoId: [String, Number]
});

// ✨ CORRECCIÓN: Esta línea es necesaria por la misma razón que en AsignarTecnicoDialog
defineEmits([...useDialogPluginComponent.emits])

const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } = useDialogPluginComponent();
const { calculateAprobacionEta, calculateRepuestoEta } = useDateHelpers();
const etaPopupProxy = ref(null);

const motivoDetencion = ref(null);
const detalleMotivo = ref('');
const fechaETA = ref(null);
const maxDateForAprobacion = ref(null);

const opcionesMotivo = [
  'Espera de Aprobación Cliente',
  'Espera de Repuesto a Pedido',
  'VOR', // Vehicle Off Road
  'Consulta Técnica',
  'Otro'
];

watch(motivoDetencion, (newMotivo) => {
  fechaETA.value = null; // Reset date on reason change
  if (newMotivo === 'Espera de Aprobación Cliente') {
    const maxDate = calculateAprobacionEta();
    maxDateForAprobacion.value = maxDate;
    fechaETA.value = format(maxDate, "yyyy-MM-dd'T'HH:mm:ss");
  } else if (newMotivo === 'Espera de Repuesto a Pedido') {
    fechaETA.value = format(calculateRepuestoEta(), "yyyy-MM-dd'T'HH:mm:ss");
  }
});

const formattedEta = computed(() => {
  if (!fechaETA.value) return '';
  const dateObj = parseISO(fechaETA.value);
  const formatString = motivoDetencion.value === 'Espera de Aprobación Cliente'
    ? "EEEE dd 'de' MMMM, yyyy"
    : "EEEE dd 'de' MMMM, yyyy 'a las' HH:mm 'hrs.'";
  return format(dateObj, formatString, { locale: es });
});

const formattedMaxDate = computed(() => {
  if (!maxDateForAprobacion.value) return '';
  return format(maxDateForAprobacion.value, "dd 'de' MMMM, yyyy", { locale: es });
});

const dateOptionsAprobacion = (date) => {
  const today = format(startOfToday(), 'yyyy/MM/dd');
  const maxDate = format(maxDateForAprobacion.value, 'yyyy/MM/dd');
  return date >= today && date <= maxDate;
};

function onOKClick() {
  onDialogOK({
    motivo_detencion: motivoDetencion.value,
    detalle_motivo: detalleMotivo.value,
    eta_fecha: fechaETA.value ? new Date(fechaETA.value) : null,
    eta_motivo: motivoDetencion.value
  });
}
</script>

<style scoped>
.q-time {
  box-shadow: none;
  border-left: 1px solid #ddd;
  border-radius: 0;
}
</style>