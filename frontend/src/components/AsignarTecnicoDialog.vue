<template>
  <q-dialog ref="dialogRef" @hide="onDialogHide">
    <q-card class="q-dialog-plugin" style="width: 400px">
      <q-card-section class="bg-primary text-white">
        <div class="text-h6">Asignar Técnico</div>
      </q-card-section>

      <q-card-section>
        <p>Selecciona el técnico que se hará cargo de este trabajo.</p>
        <q-select
          v-model="tecnicoSeleccionado"
          :options="opcionesTecnicos"
          label="Técnico"
          outlined
          :loading="isLoading"
          :disable="isLoading"
          emit-value
          map-options
          option-value="id"
          option-label="nombre_completo"
          :rules="[val => !!val || 'Debes seleccionar un técnico']"
        />
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Cancelar" @click="onDialogCancel" />
        <q-btn color="primary" label="Asignar" @click="onOKClick" :disable="!tecnicoSeleccionado" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useDialogPluginComponent, useQuasar } from 'quasar'
import { api } from 'boot/axios'

// ✨ CORRECCIÓN: Esta línea es necesaria para que Quasar
// maneje correctamente el ciclo de vida del diálogo (incluyendo 'unmount').
defineEmits([...useDialogPluginComponent.emits])

const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } = useDialogPluginComponent()
const $q = useQuasar()

const tecnicoSeleccionado = ref(null)
const opcionesTecnicos = ref([])
const isLoading = ref(false)

onMounted(async () => {
  isLoading.value = true
  try {
    const response = await api.get('/tecnicos/')
    opcionesTecnicos.value = response.data
  } catch {
    $q.notify({ type: 'negative', message: 'No se pudo cargar la lista de técnicos.' })
    onDialogCancel()
  } finally {
    isLoading.value = false
  }
})

function onOKClick() {
  onDialogOK({ tecnico_id: tecnicoSeleccionado.value })
}
</script>