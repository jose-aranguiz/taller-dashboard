<template>
  <q-page class="q-pa-md bg-grey-2">
    <div class="row q-col-gutter-md q-mb-md">
      <div class="col">
        <q-card flat bordered>
          <q-card-section class="text-center">
            <div class="text-h4 text-weight-bold text-primary">{{ pagination.rowsNumber }}</div>
            <div class="text-subtitle1 text-grey-8">Total Activos</div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <q-card class="q-mb-md q-pa-sm" flat bordered>
      <div class="row items-center q-gutter-sm">
        <q-input dense outlined v-model="filters.search" placeholder="Buscar..." class="col-xs-12 col-sm-auto col-grow" :debounce="300">
          <template v-slot:prepend><q-icon name="search" /></template>
        </q-input>

        <q-btn icon="filter_list" flat round>
          <q-tooltip>Filtros Avanzados</q-tooltip>
          <q-popup-proxy>
            <q-card class="q-pa-md" style="min-width: 300px">
              <div class="text-h6 q-mb-md">Filtros</div>
              <q-select dense outlined v-model="filters.estado_actual" :options="opcionesEstado" label="Estado" clearable class="q-mb-sm" />
              <q-select dense outlined v-model="filters.asesor_servicio" :options="opcionesAsesor" label="Asesor" clearable class="q-mb-sm" />
              <q-input dense outlined readonly label="Rango de Fechas" :model-value="formatDateRange">
                  <template v-slot:append>
                    <q-icon name="event" class="cursor-pointer">
                      <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                        <q-date v-model="filters.dateRange" range />
                      </q-popup-proxy>
                    </q-icon>
                  </template>
              </q-input>
              <q-btn label="Limpiar Filtros" flat color="primary" @click="trabajosStore.limpiarFiltros" class="q-mt-md" />
            </q-card>
          </q-popup-proxy>
        </q-btn>

        <q-btn icon="view_column" flat round>
          <q-tooltip>Gestionar Columnas</q-tooltip>
          <q-popup-proxy>
            <q-card class="q-pa-md">
              <div class="text-h6 q-mb-sm">Gestionar Columnas</div>
              <q-list bordered separator>
                <draggable
                  :list="columnOptions"
                  @end="handleColumnDragEnd"
                  item-key="name"
                  tag="div"
                  handle=".handle"
                >
                  <template #item="{ element: column }">
                    <q-item>
                      <q-item-section avatar>
                        <q-icon name="drag_indicator" class="handle cursor-pointer" />
                      </q-item-section>
                      <q-item-section>{{ column.label }}</q-item-section>
                      <q-item-section side>
                        <q-toggle v-model="column.visible" dense />
                      </q-item-section>
                    </q-item>
                  </template>
                </draggable>
              </q-list>
            </q-card>
          </q-popup-proxy>
        </q-btn>

        <q-separator vertical inset />

        <q-btn color="secondary" icon="upload_file" label="Cargar Excel" @click="abrirDialogoUploader" />
        <q-space />

        <q-btn-toggle v-model="viewMode" toggle-color="primary" push glossy :options="[{icon: 'table_rows', value: 'tabla'}, {icon: 'view_kanban', value: 'kanban'}]" />
      </div>
    </q-card>

    <transition name="fade" mode="out-in">
      <div :key="viewMode">
        <VistaTabla
          v-if="viewMode === 'tabla'"
          :key="visibleColumns.join(',')"
          :visible-columns="visibleColumns"
          @ver-historial="abrirDialogoHistorial"
          @detalle="abrirDetalle"
        />
        <VistaKanban
          v-else-if="viewMode === 'kanban'"
          @detalle="abrirDetalle"
        />
      </div>
    </transition>

    <q-dialog v-model="detalleVisible">
        <DetalleTrabajo
          v-if="selectedTrabajoId"
          :trabajo-id="selectedTrabajoId"
          style="width: 700px; max-width: 80vw;"
          @close="detalleVisible = false"
        />
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted, watch, computed, defineAsyncComponent } from 'vue';
import { useQuasar } from 'quasar';
import draggable from 'vuedraggable';
import { storeToRefs } from 'pinia';
import { useTrabajosStore } from 'stores/trabajosStore';

// Carga asíncrona de componentes para mejorar el rendimiento inicial (Code Splitting)
const VistaTabla = defineAsyncComponent(() => import('components/VistaTabla.vue'));
const VistaKanban = defineAsyncComponent(() => import('components/VistaKanban.vue'));
const DetalleTrabajo = defineAsyncComponent(() => import('components/DetalleTrabajo.vue'));
const ExcelUploader = defineAsyncComponent(() => import('components/ExcelUploader.vue'));
const HistorialTrabajoDialog = defineAsyncComponent(() => import('components/HistorialTrabajoDialog.vue'));

const $q = useQuasar();
const trabajosStore = useTrabajosStore();

// Se extrae el estado y los getters del store de Pinia manteniendo la reactividad
const {
  pagination,
  filters,
  opcionesAsesor,
  formatDateRange
} = storeToRefs(trabajosStore);

const opcionesEstado = ref(['agendado', 'espera de trabajo', 'en trabajo', 'trabajo detenido', 'en lavado', 'control de calidad', 'listo para entrega']);

// Refs locales para el control de la UI de esta página
const viewMode = ref('tabla');
const detalleVisible = ref(false);
const selectedTrabajoId = ref(null);

// Lógica para la gestión de columnas (se mantiene local porque es específica de esta vista)
const COLUMN_CONFIG_KEY = 'taller-dashboard-column-config';
const getDefaultColumnOptions = () => ([
  { name: 'actions', label: 'Acciones', visible: true },
  { name: 'alerta_eta', label: 'Alerta ETA', visible: true },
  { name: 'fecha_creacion_pedido', label: 'Fecha Pedido', visible: true },
  { name: 'pedido_dbm', label: 'Pedido DBM', visible: true },
  { name: 'tipo_pedido', label: 'Tipo Pedido', visible: true },
  { name: 'patente', label: 'Patente', visible: true },
  { name: 'cliente_nombre', label: 'Cliente', visible: true },
  { name: 'detalle_pedido', label: 'Descripción de Tarea', visible: true },
  { name: 'dias_de_estadia_activa', label: 'Días Activos', visible: true },
  { name: 'asesor_servicio', label: 'Asesor', visible: true },
  { name: 'tecnico_asignado', label: 'Técnico', visible: true },
  { name: 'estado_actual', label: 'Estado', visible: true }
]);
const columnOptions = ref([]);

const loadColumnConfig = () => {
  const savedConfigRaw = localStorage.getItem(COLUMN_CONFIG_KEY);
  if (savedConfigRaw) {
    try {
      const savedConfig = JSON.parse(savedConfigRaw);
      const defaults = getDefaultColumnOptions();
      const savedNames = new Set(savedConfig.map(c => c.name));
      const mergedConfig = [...savedConfig];
      defaults.forEach(defaultCol => {
        if (!savedNames.has(defaultCol.name)) {
          mergedConfig.push(defaultCol);
        }
      });
      columnOptions.value = mergedConfig;
    } catch (e) {
      console.error("Error al cargar configuración de columnas, usando defaults.", e);
      columnOptions.value = getDefaultColumnOptions();
    }
  } else {
    columnOptions.value = getDefaultColumnOptions();
  }
};
watch(columnOptions, (newValue) => { localStorage.setItem(COLUMN_CONFIG_KEY, JSON.stringify(newValue)); }, { deep: true });
const visibleColumns = computed(() => columnOptions.value.filter(c => c.visible).map(c => c.name));

function handleColumnDragEnd(event) {
  const { oldIndex, newIndex } = event;
  const itemToMove = columnOptions.value.splice(oldIndex, 1)[0];
  columnOptions.value.splice(newIndex, 0, itemToMove);
}

// Funciones para interactuar con diálogos y UI local
function abrirDialogoUploader() {
  $q.dialog({ component: ExcelUploader }).onOk(() => {
    pagination.value.page = 1;
    trabajosStore.fetchTrabajos();
  });
}

function abrirDetalle(id) {
  selectedTrabajoId.value = id;
  detalleVisible.value = true;
}

function abrirDialogoHistorial(trabajoId) {
  $q.dialog({
    component: HistorialTrabajoDialog,
    componentProps: { trabajoId: trabajoId }
  });
}

// Observa cambios en los filtros del store para volver a cargar los datos
watch(filters, () => {
  pagination.value.page = 1;
  trabajosStore.fetchTrabajos();
}, { deep: true });

// Carga inicial de datos al montar el componente
onMounted(() => {
  loadColumnConfig();
  trabajosStore.fetchTrabajos();
});
</script>