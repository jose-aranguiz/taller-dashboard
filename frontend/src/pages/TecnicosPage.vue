<template>
  <q-page padding>
    <div class="row justify-between items-center q-mb-md">
      <h5 class="q-my-none text-primary">Gestión de Técnicos</h5>
      <q-btn
        color="primary"
        label="Agregar Técnico"
        icon="add"
        @click="abrirDialog"
      />
    </div>

    <q-spinner-grid
      v-if="loading"
      color="primary"
      size="xl"
      class="absolute-center"
    />

    <q-list v-else bordered separator>
      <q-item v-for="tecnico in tecnicos" :key="tecnico.id">
        <q-item-section>
          <q-item-label>{{ tecnico.nombre }}</q-item-label>
        </q-item-section>
        <q-item-section side>
          <q-btn
            flat
            dense
            round
            color="negative"
            icon="delete"
            @click="eliminarTecnico(tecnico.id)"
          />
        </q-item-section>
      </q-item>
    </q-list>

    <q-dialog v-model="dialogAgregar">
      <q-card style="min-width: 350px">
        <q-card-section>
          <div class="text-h6">Nuevo Técnico</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-input
            dense
            v-model="nuevoTecnico"
            label="Nombre del Técnico"
            autofocus
            @keyup.enter="agregarTecnico"
          />
        </q-card-section>

        <q-card-actions align="right" class="text-primary">
          <q-btn flat label="Cancelar" v-close-popup />
          <q-btn flat label="Guardar" @click="agregarTecnico" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { tecnicosService } from 'src/services/tecnicosService';
import { useQuasar } from 'quasar';

const $q = useQuasar();
const tecnicos = ref([]);
const loading = ref(true);
const nuevoTecnico = ref('');
const dialogAgregar = ref(false);

async function fetchTecnicos() {
  loading.value = true;
  try {
    // Usamos el servicio centralizado
    tecnicos.value = await tecnicosService.getTecnicos();
  } catch (error) {
    // El servicio ya notifica el error, aquí solo manejamos el estado local
    // 👇 CORRECCIÓN AQUÍ: Usamos la variable 'error'
    console.error('Fallo al cargar técnicos en la página', error);
  } finally {
    loading.value = false;
  }
}

onMounted(fetchTecnicos);

function abrirDialog() {
  nuevoTecnico.value = '';
  dialogAgregar.value = true;
}

async function agregarTecnico() {
  if (!nuevoTecnico.value.trim()) {
    $q.notify({
      type: 'warning',
      message: 'El nombre no puede estar vacío.',
    });
    return;
  }

  try {
    // Usamos el servicio centralizado
    const tecnicoCreado = await tecnicosService.createTecnico({
      nombre: nuevoTecnico.value,
    });
    // Actualizamos la lista local
    tecnicos.value.push(tecnicoCreado);
    dialogAgregar.value = false;
  } catch (error) {
    // El servicio ya notifica, solo logueamos el fallo
    // 👇 CORRECCIÓN AQUÍ: Usamos la variable 'error'
    console.error('Fallo al agregar técnico en la página', error);
  }
}

async function eliminarTecnico(id) {
  $q.dialog({
    title: 'Confirmar',
    message: '¿Estás seguro de que quieres eliminar a este técnico?',
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      // Usamos el servicio centralizado
      await tecnicosService.deleteTecnico(id);
      // Actualizamos la lista local
      tecnicos.value = tecnicos.value.filter((t) => t.id !== id);
    } catch (error) {
      // El servicio ya notifica, solo logueamos el fallo
      // 👇 CORRECCIÓN AQUÍ: Usamos la variable 'error'
      console.error('Fallo al eliminar técnico en la página', error);
    }
  });
}
</script>