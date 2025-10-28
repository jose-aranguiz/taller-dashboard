<template>
  <q-dialog ref="dialogRef" @hide="onDialogHide">
    <q-card class="q-dialog-plugin">
      <q-card-section class="bg-primary text-white">
        <div class="text-h6">Cargar Trabajos desde Excel</div>
      </q-card-section>

      <q-card-section>
        <q-uploader
          :factory="uploaderFactory"
          label="Seleccionar archivo Excel (.xlsx, .xls)"
          accept=".xlsx, .xls"
          max-files="1"
          auto-upload
          @uploaded="onUploadSuccess"
          @failed="onUploadFail"
          @rejected="onRejected"
          field-name="file"
          class="full-width"
        />
      </q-card-section>

      <q-card-actions align="right">
        <q-btn color="primary" flat label="Cerrar" @click="onDialogCancel" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { useDialogPluginComponent, useQuasar } from 'quasar'
import { useAuthStore } from 'stores/auth'

defineEmits([
  ...useDialogPluginComponent.emits
])

const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } = useDialogPluginComponent()
const $q = useQuasar()
const authStore = useAuthStore()

const uploaderFactory = () => {
  return new Promise((resolve, reject) => {
    // --- ✨ LÍNEAS DE DEPURACIÓN AÑADIDAS ✨ ---
    console.log('Token disponible en el factory del uploader:', authStore.token);

    if (!authStore.token) {
      console.error('¡No se encontró token! Rechazando la subida.');
      $q.notify({
        type: 'negative',
        message: 'No estás autenticado. Inicia sesión de nuevo.'
      })
      return reject(new Error('No autenticado'))
    }
    
    // Creamos la configuración para la petición de subida
    console.log('Configurando la subida con el token.');
    resolve({
      url: '/api/trabajos/upload-excel/',
      method: 'POST',
      headers: [
        { name: 'Authorization', value: `Bearer ${authStore.token}` }
      ]
    })
  })
}

const onUploadSuccess = ({ xhr }) => {
  const response = JSON.parse(xhr.response)
  $q.notify({
    type: 'positive',
    message: response.mensaje || 'Archivo procesado exitosamente.',
    caption: `Creados: ${response.creados}, Actualizados: ${response.actualizados}`
  })
  onDialogOK()
}

const onUploadFail = ({ xhr }) => {
  let detail = 'Error desconocido.'
  try {
    const response = JSON.parse(xhr.response)
    detail = response.detail || 'El servidor no proporcionó detalles.'
  } catch {
    detail = 'No se pudo comunicar con el servidor o la respuesta no es válida.'
  }

  $q.notify({
    type: 'negative',
    message: 'Error al procesar el archivo',
    caption: detail
  })
}

const onRejected = (rejectedEntries) => {
  $q.notify({
    type: 'negative',
    message: `${rejectedEntries.length} archivo(s) no pasaron la validación`,
    caption: 'Asegúrate de que sea un archivo .xlsx o .xls'
  })
}
</script>