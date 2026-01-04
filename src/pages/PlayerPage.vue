<template>
  <q-page class="dashboard-page column items-start q-pa-md">
    <q-card flat class="w-full max-w-xl q-mb-md">
      <q-card-section>
        <div class="text-h6">Player Dashboard</div>
      </q-card-section>
      <q-card-section>
        <q-form @submit.prevent="onSearch">
          <div class="row items-center q-gutter-sm">
            <div class="col">
              <q-input
                v-model="search"
                label="Go to player…"
                dense
                outlined
                clearable
              />
            </div>
            <q-btn label="Go" type="submit" color="primary" />
          </div>
        </q-form>
      </q-card-section>
    </q-card>

    <q-card flat class="w-full max-w-xl">
      <q-card-section>
        <q-input
          v-model="nameFilter"
          placeholder="Filter table…"
          dense
          outlined
          clearable
        />
      </q-card-section>
      <q-separator />
      <q-card-section class="q-pa-none">
        <q-table
          :columns="columns"
          :rows="filteredPlayers"
          row-key="name"
          flat
          bordered
          separator="cell"
          :loading="loading"
          :pagination.sync="pagination"
          :rows-per-page-options="[20, 50, 100]"
          :sort-by="['population']"
          :sort-desc="[true]"
        >
          <template #body-cell-name="props">
            <q-td :props="props">
              <a
                :href="detailUrl(props.row.name)"
                target="_blank"
                rel="noopener"
              >
                {{ props.row.name }}
              </a>
            </q-td>
          </template>
          <template #no-data>
            <div class="text-center q-pa-md">
              <q-icon name="person_off" size="2rem" class="text-grey" />
              <div class="text-grey">No players found.</div>
            </div>
          </template>
        </q-table>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted, onActivated } from 'vue'
import { useRouter } from 'vue-router'
import { api } from 'boot/axios'

const router     = useRouter()
const search     = ref('')
const nameFilter = ref('')
const players    = ref([])
const loading    = ref(false)
const pagination = ref({ page: 1, rowsPerPage: 20 })

const columns = [
  { name: 'name',       label: 'Player',     field: 'name',       sortable: true },
  { name: 'alliance',   label: 'Alliance',   field: 'alliance',   sortable: true },
  { name: 'villages',   label: '# Villages', field: 'villages',   sortable: true, align: 'right' },
  { name: 'population', label: 'Population', field: 'population', sortable: true, align: 'right' }
]

function onSearch() {
  const name = search.value.trim()
  if (name) {
    router.push({ name: 'player-detail', params: { name } })
  }
}

function detailUrl(playerName) {
  return router.resolve({
    name: 'player-detail',
    params: { name: playerName }
  }).href
}

const filteredPlayers = computed(() => {
  const f = nameFilter.value.trim().toLowerCase()
  return players.value.filter(p =>
    !f || p.name.toLowerCase().includes(f)
  )
})

// Now simply fetch JSON!
async function loadPlayers() {
  loading.value = true
  try {
    const { data } = await api.get("/api/players?limit=300")
    players.value = data
  }
  finally {
    loading.value = false
  }
}

onMounted(loadPlayers)
onActivated(loadPlayers)
</script>

<style scoped>
.dashboard-page {
  min-height: calc(100vh - var(--q-header-height));
}
</style>
