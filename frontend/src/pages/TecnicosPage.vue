<template>
  <q-page class="q-pa-md">
    <div class="text-h4 q-mb-md">Gestión de Técnicos</div>

    <q-card flat bordered>
      <q-table
        :rows="tecnicos"
        :columns="columns"
        row-key="id"
        :loading="isLoading"
        title="Técnicos Registrados"
      >
        <template v-slot:top-right>
          <q-btn
            color="primary"
            icon="add"
            label="Crear Técnico"
            @click="openCreateDialog"
          />
        </template>
      </q-table>
    </q-card>

    <q-dialog v-model="isDialogOpen">
      <q-card style="min-width: 350px">
        <q-card-section>
          <div class="text-h6">Nuevo Técnico</div>
        </q-card-section>

        <q-form @submit.prevent="handleCreateTecnico">
          <q-card-section class="q-pt-none">
            <q-input
              v-model="newTecnico.codigo"
              label="Código de Técnico"
              autofocus
              :rules="[val => !!val || 'El código es requerido']"
            />
            <q-input
              v-model="newTecnico.nombre_completo"
              label="Nombre Completo"
              :rules="[val => !!val || 'El nombre es requerido']"
            />
          </q-card-section>

          <q-card-actions align="right">
            <q-btn flat label="Cancelar" v-close-popup />
            <q-btn type="submit" label="Crear" color="primary" />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>

  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from 'boot/axios'
import { useQuasar } from 'quasar'

const $q = useQuasar()
const tecnicos = ref([])
const isLoading = ref(false)
const isDialogOpen = ref(false)
const newTecnico = ref({
  codigo: '',
  nombre_completo: ''
})

const columns = [
  { name: 'codigo', label: 'Código', field: 'codigo', align: 'left', sortable: true },
  { name: 'nombre_completo', label: 'Nombre Completo', field: 'nombre_completo', align: 'left', sortable: true }
]

const fetchTecnicos = async () => {
  isLoading.value = true
  try {
    const response = await api.get('/tecnicos/')
    tecnicos.value = response.data
  } catch { // <-- ✨ CAMBIO AQUÍ: Se elimina la variable 'error' que no se usaba
    $q.notify({ type: 'negative', message: 'Error al cargar los técnicos.' })
  } finally {
    isLoading.value = false
  }
}

const openCreateDialog = () => {
  newTecnico.value = { codigo: '', nombre_completo: '' } // Resetea el formulario
  isDialogOpen.value = true
}

const handleCreateTecnico = async () => {
  try {
    await api.post('/tecnicos/', newTecnico.value)
    $q.notify({ type: 'positive', message: 'Técnico creado exitosamente.' })
    isDialogOpen.value = false
    fetchTecnicos() // Refresca la tabla
  } catch (error) {
    $q.notify({ type: 'negative', message: error.response?.data?.detail || 'Error al crear el técnico.' })
  }
}

onMounted(fetchTecnicos)
</script>