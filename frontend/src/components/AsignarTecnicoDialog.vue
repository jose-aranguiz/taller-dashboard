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
          option-label="nombre"
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
import { useDialogPluginComponent } from 'quasar'
// 👇 CAMBIO AQUÍ: Importamos el servicio
import { tecnicosService } from 'src/services/tecnicosService';

defineEmits([...useDialogPluginComponent.emits])

const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } = useDialogPluginComponent()

const tecnicoSeleccionado = ref(null)
const opcionesTecnicos = ref([])
const isLoading = ref(false)

onMounted(async () => {
  isLoading.value = true
  try {
    // 👇 CAMBIO AQUÍ: Usamos el servicio
    opcionesTecnicos.value = await tecnicosService.getTecnicos()
  } catch (error) {
    // El servicio ya notifica el error
    console.error('Error cargando técnicos en diálogo', error)
    onDialogCancel() // Cerramos el diálogo si no se pueden cargar
  } finally {
    isLoading.value = false
  }
})

function onOKClick() {
  onDialogOK({ tecnico_id: tecnicoSeleccionado.value })
}
</script>