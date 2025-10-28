<template>
  <q-page class="q-pa-md">
    <div class="text-h4 q-mb-md">Historial de Trabajos Completados</div>

    <div class="row q-col-gutter-md q-mb-md">
      <div class="col-12 col-sm-6">
        <q-card flat bordered>
          <q-card-section class="text-center">
            <div class="text-h5 text-weight-bold text-green-8">{{ summary.trabajosCompletados }}</div>
            <div class="text-subtitle2 text-grey-8">Trabajos en Periodo</div>
          </q-card-section>
        </q-card>
      </div>
      <div class="col-12 col-sm-6">
        <q-card flat bordered>
          <q-card-section class="text-center">
            <div class="text-h5 text-weight-bold text-green-8">
              {{ new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP' }).format(summary.totalFacturado) }}
            </div>
            <div class="text-subtitle2 text-grey-8">Total Facturado en Periodo</div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <q-card flat bordered>
       <q-table
        title="Trabajos Completados"
        :rows="trabajos"
        :columns="columns"
        row-key="id"
        :loading="isLoading"
        v-model:pagination="pagination"
        @request="onRequest"
      >
        <template v-slot:top>
          <div class="q-table__title">Trabajos Completados</div>
          <q-space />
          <div class="row q-gutter-sm items-center">
            <q-input dense outlined readonly label="Filtrar por Fecha" :model-value="formatDateRange" style="min-width: 220px;">
              <template v-slot:append>
                <q-icon name="event" class="cursor-pointer">
                  <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                    <q-date v-model="filters.dateRange" range @update:model-value="onRequest({ pagination, filters })" />
                  </q-popup-proxy>
                </q-icon>
              </template>
            </q-input>
            <q-input dense outlined debounce="300" v-model="filters.search" placeholder="Buscar..." style="width: 250px;">
              <template v-slot:append><q-icon name="search" /></template>
            </q-input>
             <q-btn flat color="primary" @click="limpiarFiltros" label="Limpiar" />
          </div>
        </template>

        <template v-slot:body-cell-actions="props">
          <q-td :props="props">
            <q-btn flat round dense icon="visibility" @click="abrirDetalle(props.row.id)">
              <q-tooltip>Ver Detalles del Trabajo</q-tooltip>
            </q-btn>
          </q-td>
        </template>

        <template v-slot:no-data>
          <div class="full-width row flex-center text-grey q-gutter-sm q-pa-lg">
            <q-icon size="2em" name="history" />
            <span>No se encontraron trabajos para los filtros seleccionados.</span>
          </div>
        </template>
      </q-table>
    </q-card>

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
import { ref, onMounted, computed, watch } from 'vue';
import { api } from 'boot/axios';
import { useQuasar } from 'quasar';
import DetalleTrabajo from 'components/DetalleTrabajo.vue';

const $q = useQuasar();
const trabajos = ref([]);
const isLoading = ref(false);
const filters = ref({
  search: '',
  dateRange: null
});
const summary = ref({
  trabajosCompletados: 0,
  totalFacturado: 0
});

const pagination = ref({
  sortBy: 'fecha_creacion_pedido',
  descending: true,
  page: 1,
  rowsPerPage: 15,
  rowsNumber: 0
});

const columns = [
  { name: 'actions', label: 'Acciones', align: 'center' },
  { name: 'pedido_dbm', label: 'Pedido DBM', field: 'pedido_dbm', align: 'left', sortable: true },
  { name: 'patente', label: 'Patente', field: 'patente', align: 'left', sortable: true },
  { name: 'cliente_nombre', label: 'Cliente', field: 'cliente_nombre', align: 'left', sortable: true },
  {
    name: 'fecha_cierre_pedido',
    label: 'Fecha Cierre',
    field: 'fecha_cierre_pedido',
    sortable: true,
    format: val => val ? new Date(val).toLocaleDateString('es-CL') : 'N/A'
  },
  {
    name: 'total_pedido',
    label: 'Total',
    field: 'total_pedido',
    sortable: true,
    format: val => val != null ? new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP' }).format(val) : 'N/A'
  }
];

const detalleVisible = ref(false);
const selectedTrabajoId = ref(null);

function abrirDetalle(id) {
  selectedTrabajoId.value = id;
  detalleVisible.value = true;
}

const formatDateRange = computed(() => {
  if (!filters.value.dateRange) return 'Cualquier fecha';
  const { from, to } = filters.value.dateRange;
  return to ? `${from} - ${to}` : from;
});

function limpiarFiltros() {
  filters.value = { search: '', dateRange: null };
}

watch(filters, () => {
  onRequest({ pagination: pagination.value, filters: filters.value })
}, { deep: true });

const onRequest = async (props) => {
  const { page, rowsPerPage, sortBy, descending } = props.pagination;

  isLoading.value = true;

  try {
    const params = {
      activos: false,
      page: page,
      limit: rowsPerPage,
      sort_by: sortBy,
      sort_order: descending ? 'desc' : 'asc',
      search: filters.value.search,
      fecha_desde: filters.value.dateRange?.from?.replace(/\//g, '-'),
      fecha_hasta: filters.value.dateRange?.to?.replace(/\//g, '-')
    }
    Object.keys(params).forEach(key => (params[key] === null || params[key] === undefined || params[key] === '') && delete params[key]);

    const response = await api.get('/trabajos/', { params });

    trabajos.value = response.data.items;
    // Asumiendo que el backend puede devolver un objeto 'summary'
    if (response.data.summary) {
      summary.value = response.data.summary;
    }

    pagination.value.rowsNumber = response.data.total;
    pagination.value.page = page;
    pagination.value.rowsPerPage = rowsPerPage;
    pagination.value.sortBy = sortBy;
    pagination.value.descending = descending;

} catch (error) {
    console.error('Error al obtener el historial:', error);
    $q.notify({ type: 'negative', message: 'Error al obtener el historial.' });

  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  onRequest({ pagination: pagination.value });
});
</script>