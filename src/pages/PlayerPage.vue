<template>
  <q-page class="dashboard-page">
    <!-- Hero Section -->
    <section class="page-hero bg-primary text-white">
      <div class="container">
        <div class="row items-center q-py-xl">
          <div class="col-12 col-md-8">
            <h1 class="page-title q-mb-md">Player Analytics</h1>
            <p class="page-subtitle">
              Explore player statistics, village counts, and population data across the game world
            </p>
          </div>
          <div class="col-12 col-md-4 q-mt-md q-mt-md-none text-center">
            <q-icon name="people" size="120px" class="hero-icon" />
          </div>
        </div>
      </div>
    </section>

    <!-- Stats Cards -->
    <section class="stats-section q-pa-md">
      <div class="container">
        <div class="row q-col-gutter-md">
          <div class="col-12 col-sm-6 col-md-3">
            <q-card flat bordered class="stat-card">
              <q-card-section class="text-center">
                <q-icon name="people" size="32px" color="primary" class="q-mb-sm" />
                <div class="text-h5 q-mb-xs">{{ filteredPlayers.length }}</div>
                <div class="text-caption text-grey-7">Total Players</div>
              </q-card-section>
            </q-card>
          </div>
          <div class="col-12 col-sm-6 col-md-3">
            <q-card flat bordered class="stat-card">
              <q-card-section class="text-center">
                <q-icon name="location_city" size="32px" color="secondary" class="q-mb-sm" />
                <div class="text-h5 q-mb-xs">{{ totalVillages }}</div>
                <div class="text-caption text-grey-7">Total Villages</div>
              </q-card-section>
            </q-card>
          </div>
          <div class="col-12 col-sm-6 col-md-3">
            <q-card flat bordered class="stat-card">
              <q-card-section class="text-center">
                <q-icon name="group" size="32px" color="accent" class="q-mb-sm" />
                <div class="text-h5 q-mb-xs">{{ totalPopulation.toLocaleString() }}</div>
                <div class="text-caption text-grey-7">Total Population</div>
              </q-card-section>
            </q-card>
          </div>
          <div class="col-12 col-sm-6 col-md-3">
            <q-card flat bordered class="stat-card">
              <q-card-section class="text-center">
                <q-icon name="trending_up" size="32px" color="positive" class="q-mb-sm" />
                <div class="text-h5 q-mb-xs">{{ avgPopulation.toLocaleString() }}</div>
                <div class="text-caption text-grey-7">Avg Population</div>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </div>
    </section>

    <!-- Search and Table Section -->
    <section class="content-section q-pa-md">
      <div class="container">
        <q-card flat bordered class="main-card">
          <q-card-section>
            <div class="row items-center q-gutter-md q-mb-md">
              <div class="col-12 col-md-6">
                <q-input
                  v-model="search"
                  label="Search player by name…"
                  outlined
                  clearable
                  @keyup.enter="onSearch"
                >
                  <template #prepend>
                    <q-icon name="search" />
                  </template>
                </q-input>
              </div>
              <div class="col-12 col-md-6">
                <q-btn
                  label="Go to Player"
                  color="primary"
                  icon="person"
                  unelevated
                  @click="onSearch"
                  class="full-width"
                />
              </div>
            </div>
            <q-separator class="q-mb-md" />
            <q-input
              v-model="nameFilter"
              placeholder="Filter table by name…"
              outlined
              clearable
              dense
            >
              <template #prepend>
                <q-icon name="filter_list" />
              </template>
            </q-input>
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
              :pagination="pagination"
              @update:pagination="val => { pagination = val }"
              :rows-per-page-options="[20, 50, 100]"
              :sort-by="['population']"
              :sort-desc="[true]"
              class="modern-table"
            >
              <template #body-cell-name="props">
                <q-td :props="props">
                  <router-link
                    :to="{ name: 'player-detail', params: { name: props.row.name } }"
                    class="player-link"
                  >
                    <q-icon name="person" size="16px" class="q-mr-xs" />
                    {{ props.row.name }}
                  </router-link>
                </q-td>
              </template>
              <template #body-cell-alliance="props">
                <q-td :props="props">
                  <q-chip
                    v-if="props.value"
                    :label="props.value"
                    color="secondary"
                    text-color="white"
                    size="sm"
                  />
                  <span v-else class="text-grey-6">—</span>
                </q-td>
              </template>
              <template #body-cell-population="props">
                <q-td :props="props" class="text-right">
                  <strong class="text-primary">{{ props.value.toLocaleString() }}</strong>
                </q-td>
              </template>
              <template #no-data>
                <div class="text-center q-pa-xl">
                  <q-icon name="person_off" size="4rem" class="text-grey q-mb-md" />
                  <div class="text-h6 text-grey">No players found</div>
                  <div class="text-body2 text-grey-7 q-mt-sm">Try adjusting your search or filter</div>
                </div>
              </template>
              <template #loading>
                <q-inner-loading showing color="primary" />
              </template>
            </q-table>
          </q-card-section>
        </q-card>
      </div>
    </section>
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
const pagination = ref({ 
  sortBy: 'population',
  descending: true,
  page: 1,
  rowsPerPage: 20
})

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

const totalVillages = computed(() => {
  return filteredPlayers.value.reduce((sum, p) => sum + (p.villages || 0), 0)
})

const totalPopulation = computed(() => {
  return filteredPlayers.value.reduce((sum, p) => sum + (p.population || 0), 0)
})

const avgPopulation = computed(() => {
  if (filteredPlayers.value.length === 0) return 0
  return Math.round(totalPopulation.value / filteredPlayers.value.length)
})

// Now simply fetch JSON!
async function loadPlayers() {
  loading.value = true
  try {
    const { data } = await api.get("/api/players?limit=1000")
    players.value = data
  }
  finally {
    loading.value = false
  }
}

onMounted(loadPlayers)
onActivated(loadPlayers)
</script>

<style scoped lang="scss">
.dashboard-page {
  min-height: calc(100vh - var(--q-header-height));
}

.container {
  max-width: 1400px;
  margin: 0 auto;
}

.page-hero {
  background: linear-gradient(135deg, $primary 0%, #d49a0f 100%);
  padding: 2rem 1rem;
}

.page-title {
  font-size: 3rem;
  font-weight: 700;
  margin: 0;
  
  @media (max-width: 600px) {
    font-size: 2rem;
  }
}

.page-subtitle {
  font-size: 1.2rem;
  opacity: 0.95;
  margin: 0;
  
  @media (max-width: 600px) {
    font-size: 1rem;
  }
}

.hero-icon {
  opacity: 0.3;
}

.stats-section {
  background: $grey-1;
}

.stat-card {
  transition: transform 0.2s, box-shadow 0.2s;
  height: 100%;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  }
}

.content-section {
  background: $grey-1;
  min-height: 400px;
}

.main-card {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.modern-table {
  .q-table__top {
    padding: 1rem;
  }
  
  .q-table tbody td {
    font-size: 0.95rem;
  }
  
  .q-table tbody tr:hover {
    background-color: $grey-2;
  }
}

.player-link {
  color: $primary;
  text-decoration: none;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  transition: color 0.2s;
  
  &:hover {
    color: #d49a0f;
    text-decoration: underline;
  }
}
</style>
