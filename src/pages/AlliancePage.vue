<template>
  <q-page class="dashboard-page">
    <!-- Hero Section -->
    <section class="page-hero bg-accent text-white">
      <div class="container">
        <div class="row items-center q-py-xl">
          <div class="col-12 col-md-8">
            <h1 class="page-title q-mb-md">Alliance Overview</h1>
            <p class="page-subtitle">
              Analyze alliance strength, member counts, territory distribution, and competitive rankings
            </p>
          </div>
          <div class="col-12 col-md-4 q-mt-md q-mt-md-none text-center">
            <q-icon name="groups" size="120px" class="hero-icon" />
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
                <q-icon name="groups" size="32px" color="accent" class="q-mb-sm" />
                <div class="text-h5 q-mb-xs">{{ filteredRows.length }}</div>
                <div class="text-caption text-grey-7">Total Alliances</div>
              </q-card-section>
            </q-card>
          </div>
          <div class="col-12 col-sm-6 col-md-3">
            <q-card flat bordered class="stat-card">
              <q-card-section class="text-center">
                <q-icon name="people" size="32px" color="primary" class="q-mb-sm" />
                <div class="text-h5 q-mb-xs">{{ totalPlayers.toLocaleString() }}</div>
                <div class="text-caption text-grey-7">Total Players</div>
              </q-card-section>
            </q-card>
          </div>
          <div class="col-12 col-sm-6 col-md-3">
            <q-card flat bordered class="stat-card">
              <q-card-section class="text-center">
                <q-icon name="location_city" size="32px" color="secondary" class="q-mb-sm" />
                <div class="text-h5 q-mb-xs">{{ totalVillages.toLocaleString() }}</div>
                <div class="text-caption text-grey-7">Total Villages</div>
              </q-card-section>
            </q-card>
          </div>
          <div class="col-12 col-sm-6 col-md-3">
            <q-card flat bordered class="stat-card">
              <q-card-section class="text-center">
                <q-icon name="trending_up" size="32px" color="positive" class="q-mb-sm" />
                <div class="text-h5 q-mb-xs">{{ totalPopulation.toLocaleString() }}</div>
                <div class="text-caption text-grey-7">Total Population</div>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </div>
    </section>

    <!-- Table Section -->
    <section class="content-section q-pa-md">
      <div class="container">
        <q-card flat bordered class="main-card">
          <q-card-section>
            <div class="row items-center q-mb-md">
              <div class="col-12 col-md-6">
                <q-input
                  v-model="filters.alliance"
                  placeholder="Filter by alliance name…"
                  outlined
                  clearable
                  dense
                >
                  <template #prepend>
                    <q-icon name="search" />
                  </template>
                </q-input>
              </div>
              <div class="col-12 col-md-6 q-mt-md q-mt-md-none">
                <q-input
                  v-model="filters.population"
                  placeholder="Filter by population…"
                  outlined
                  clearable
                  dense
                >
                  <template #prepend>
                    <q-icon name="filter_list" />
                  </template>
                </q-input>
              </div>
            </div>
          </q-card-section>
          <q-separator />
          <q-card-section class="q-pa-none">
            <q-table
              :columns="columns"
              :rows="filteredRows"
              row-key="alliance"
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
              @row-click="goToDetail"
            >
              <template #body-cell-alliance="props">
                <q-td :props="props">
                  <router-link
                    :to="{ name: 'alliance-detail', params: { tag: props.row.alliance } }"
                    class="alliance-link"
                  >
                    <q-icon name="groups" size="16px" class="q-mr-xs" />
                    {{ props.row.alliance }}
                  </router-link>
                </q-td>
              </template>
              <template #body-cell-players="props">
                <q-td :props="props" class="text-right">
                  <q-chip
                    :label="props.value"
                    color="primary"
                    text-color="white"
                    size="sm"
                  />
                </q-td>
              </template>
              <template #body-cell-population="props">
                <q-td :props="props" class="text-right">
                  <strong class="text-accent">{{ props.value.toLocaleString() }}</strong>
                </q-td>
              </template>
              <template #body-cell-topRegion="props">
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
              <template #no-data>
                <div class="text-center q-pa-xl">
                  <q-icon name="groups" size="4rem" class="text-grey q-mb-md" />
                  <div class="text-h6 text-grey">No alliances found</div>
                  <div class="text-body2 text-grey-7 q-mt-sm">Try adjusting your filters</div>
                </div>
              </template>
              <template #loading>
                <q-inner-loading showing color="accent" />
              </template>
            </q-table>
          </q-card-section>
        </q-card>
      </div>
    </section>
  </q-page>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from 'boot/axios'

const CACHE_KEY   = 'alliancesCache'
const CACHE_TTL   = 1000 * 60 * 60 * 24  // 24h

const router     = useRouter()
const loading    = ref(false)
const rows       = ref([])
const pagination = ref({ 
  sortBy: 'population',
  descending: true,
  page: 1,
  rowsPerPage: 20
})

const columns = [
  { name: 'alliance',   label: 'Alliance',   field: 'alliance',   sortable: true },
  { name: 'players',    label: '# Players',  field: 'players',    sortable: true, align: 'right' },
  { name: 'population', label: 'Population', field: 'population', sortable: true, align: 'right' },
  { name: 'topRegion',  label: 'Top Region', field: 'topRegion',  sortable: true }
]

const filters = reactive({
  alliance: '',
  players: '',
  population: '',
  topRegion: ''
})

function goToDetail(evt, row) {
  router.push({ name: 'alliance-detail', params: { tag: row.alliance } })
}

function loadFromCache() {
  try {
    const raw = localStorage.getItem(CACHE_KEY)
    if (!raw) return null
    const { ts, data } = JSON.parse(raw)
    if ((Date.now() - ts) < CACHE_TTL) {
      return data
    }
  }
  catch {}
  return null
}

function saveToCache(data) {
  localStorage.setItem(CACHE_KEY, JSON.stringify({ ts: Date.now(), data }))
}

async function loadAlliances() {
  const cached = loadFromCache()
  if (cached) {
    rows.value = cached
    return
  }

  loading.value = true
  try {
    // 1) fetch all alliance tags directly
    const { data: tags } = await api.get('/api/alliance')
    
    // Validate response
    if (!Array.isArray(tags)) {
      console.error('Expected array of tags, got:', tags)
      return
    }
    
    if (tags.length === 0) {
      console.warn('No alliance tags found')
      rows.value = []
      return
    }

    // 2) for each tag, fetch its villages & compute stats
    const statsPromises = tags.map(async tag => {
      try {
        const { data } = await api.get(
          `/api/alliance/${encodeURIComponent(tag)}/villages`
        )
        
        if (!data || !data.villages) {
          console.error(`No villages data for alliance ${tag}:`, data)
          return {
            alliance: tag,
            players: 0,
            population: 0,
            topRegion: ''
          }
        }
        
        const vs = data.villages

        // count unique players
        const playerSet = new Set(vs.map(v => v.player_name || v.player || '').filter(Boolean))
        const totalPop  = vs.reduce((sum, v) => sum + (Number(v.population)||0), 0)

        // find top region by population
        const regionTotals = {}
        vs.forEach(v => {
          const region = v.region || ''
          if (region) {
            regionTotals[region] = (regionTotals[region]||0) + (Number(v.population)||0)
          }
        })
        let topR = '', topVal = -1
        Object.entries(regionTotals).forEach(([r,val]) => {
          if (val > topVal) {
            topVal = val
            topR   = r
          }
        })

        return {
          alliance:   tag,
          players:    playerSet.size,
          population: totalPop,
          topRegion:  topR
        }
      } catch (err) {
        console.error(`Error fetching villages for alliance ${tag}:`, err)
        return {
          alliance: tag,
          players: 0,
          population: 0,
          topRegion: ''
        }
      }
    })

    const result = await Promise.all(statsPromises)
    rows.value = result.filter(r => r) // Filter out any null/undefined results
    saveToCache(result)
  } catch (err) {
    console.error('Error loading alliances:', err)
    rows.value = []
  } finally {
    loading.value = false
  }
}

const filteredRows = computed(() => {
  return rows.value.filter(r =>
    Object.entries(filters).every(([k, v]) => {
      if (!v) return true
      return String(r[k]).toLowerCase().includes(v.toLowerCase())
    })
  )
})

const totalPlayers = computed(() => {
  return filteredRows.value.reduce((sum, r) => sum + (r.players || 0), 0)
})

const totalVillages = computed(() => {
  return filteredRows.value.reduce((sum, r) => {
    // Estimate villages from population if not available
    return sum + (r.village_count || Math.floor((r.population || 0) / 100))
  }, 0)
})

const totalPopulation = computed(() => {
  return filteredRows.value.reduce((sum, r) => sum + (r.population || 0), 0)
})

onMounted(loadAlliances)
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
  background: linear-gradient(135deg, $accent 0%, #1d7a6f 100%);
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
  
  .q-table tbody tr {
    cursor: pointer;
    
    &:hover {
      background-color: $grey-2;
    }
  }
}

.alliance-link {
  color: $accent;
  text-decoration: none;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  transition: color 0.2s;
  
  &:hover {
    color: #1f8b7d;
    text-decoration: underline;
  }
}
</style>
