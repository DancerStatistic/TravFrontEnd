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
              <!-- AUTOCOMPLETE -->
              <div class="col-12 col-md-6">
                <q-select
                  v-model="selectedPlayer"
                  :options="playerOptions"
                  use-input
                  fill-input
                  hide-selected
                  clearable
                  outlined
                  label="Search player by name…"
                  input-debounce="0"
                  behavior="menu"
                  :loading="loading || optionsLoading"
                  @filter="filterPlayers"
                  @update:model-value="onSelectedPlayer"
                >
                  <template #prepend>
                    <q-icon name="search" />
                  </template>

                  <template #no-option>
                    <q-item>
                      <q-item-section class="text-grey-7">
                        No matching players
                      </q-item-section>
                    </q-item>
                  </template>

                  <template #option="scope">
                    <q-item v-bind="scope.itemProps">
                      <q-item-section>
                        <q-item-label class="text-weight-medium">
                          {{ scope.opt.label }}
                        </q-item-label>
                        <q-item-label caption>
                          {{ scope.opt.alliance || '—' }}
                          • {{ (scope.opt.villages || 0).toLocaleString() }} villages
                          • {{ (scope.opt.population || 0).toLocaleString() }} pop
                        </q-item-label>
                      </q-item-section>
                    </q-item>
                  </template>
                </q-select>
              </div>

              <div class="col-12 col-md-6">
                <q-btn
                  label="Go to Player"
                  color="primary"
                  icon="person"
                  unelevated
                  @click="goToSelectedPlayer"
                  class="full-width"
                  :disable="!selectedPlayer"
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
              @update:pagination="(val) => (pagination = val)"
              :rows-per-page-options="[20, 50, 100]"
              :sort-by="['population']"
              :sort-desc="[true]"
              class="modern-table"
            >
              <template #body-cell-name="props">
                <q-td :props="props">
                  <router-link
                    v-if="props.row?.name"
                    :to="{ name: 'player-detail', params: { name: props.row.name } }"
                    class="player-link"
                  >
                    <q-icon name="person" size="16px" class="q-mr-xs" />
                    {{ props.row.name }}
                  </router-link>

                  <span v-else class="text-grey-6">Unknown</span>
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
import { ref, computed, onMounted, onActivated, watch } from 'vue'
import { useRouter } from 'vue-router'
import { api } from 'boot/axios'

const router = useRouter()

/* -----------------------------
 * State
 * ----------------------------- */
const players = ref([])
const loading = ref(false)

const nameFilter = ref('')

let pagination = ref({
  sortBy: 'population',
  descending: true,
  page: 1,
  rowsPerPage: 20
})

/**
 * Autocomplete state
 */
const selectedPlayer = ref(null)
const playerOptions = ref([])
const optionsLoading = ref(false)

/* -----------------------------
 * Alliance enrichment cache (shared concept with AlliancePage)
 * ----------------------------- */
const PLAYER_ALLIANCE_CACHE_KEY = 'playerAllianceByName'
const PLAYER_ALLIANCE_CACHE_TTL = 1000 * 60 * 60 // 60 mins

function loadAllianceMap() {
  try {
    const raw = localStorage.getItem(PLAYER_ALLIANCE_CACHE_KEY)
    if (!raw) return {}
    const parsed = JSON.parse(raw)
    const ts = parsed?.ts
    const data = parsed?.data
    if (!ts || !data || typeof data !== 'object') return {}
    if ((Date.now() - ts) > PLAYER_ALLIANCE_CACHE_TTL) return {}
    return data
  } catch {
    return {}
  }
}

function saveAllianceMap(map) {
  try {
    localStorage.setItem(PLAYER_ALLIANCE_CACHE_KEY, JSON.stringify({ ts: Date.now(), data: map }))
  } catch {
    // ignore
  }
}

const allianceMap = ref(loadAllianceMap())
const inflight = new Set()

function readAllianceFromVillageRow(r) {
  // PlayerDetail.vue uses: r.alliance_tag || r.alliance || ''
  const raw = (r?.alliance_tag ?? r?.allianceTag ?? r?.alliance ?? r?.ally_tag ?? r?.allyTag ?? '') ?? ''
  return String(raw).trim()
}

async function fetchAllianceForPlayer(playerName) {
  const name = String(playerName || '').trim()
  if (!name) return ''

  if (allianceMap.value[name]) return allianceMap.value[name]
  if (inflight.has(name)) return ''

  inflight.add(name)
  try {
    const { data } = await api.get(`/api/player/${encodeURIComponent(name)}/villages`)
    const vs = Array.isArray(data?.villages) ? data.villages : []
    const firstWithAlliance = vs.find(v => !!readAllianceFromVillageRow(v)) || vs[0]
    const tag = readAllianceFromVillageRow(firstWithAlliance)
    if (tag) {
      allianceMap.value = { ...allianceMap.value, [name]: tag }
      saveAllianceMap(allianceMap.value)
      return tag
    }
    return ''
  } catch {
    return ''
  } finally {
    inflight.delete(name)
  }
}

/**
 * Enrich only the rows we’re actually showing (avoids 1000+ calls).
 * Uses small concurrency.
 */
async function enrichVisibleAlliances(list) {
  const missing = (list || [])
    .map(p => p?.name)
    .filter(Boolean)
    .filter(name => !String(getAllianceForName(name)).trim())

  // unique
  const uniq = Array.from(new Set(missing))
  if (uniq.length === 0) return

  const CONCURRENCY = 6
  for (let i = 0; i < uniq.length; i += CONCURRENCY) {
    const batch = uniq.slice(i, i + CONCURRENCY)
    const results = await Promise.all(batch.map(n => fetchAllianceForPlayer(n)))

    // patch players array in-place so QTable updates
    if (results.some(Boolean)) {
      const mapNow = allianceMap.value
      players.value = (players.value || []).map(p => {
        const name = p?.name
        if (!name) return p
        const cached = mapNow[name]
        if (cached && !p.alliance) return { ...p, alliance: cached }
        return p
      })
    }
  }
}

function getAllianceForName(name) {
  const n = String(name || '').trim()
  return (n && allianceMap.value?.[n]) ? allianceMap.value[n] : ''
}

/* -----------------------------
 * Table columns
 * ----------------------------- */
const columns = [
  { name: 'name', label: 'Player', field: 'name', sortable: true },
  { name: 'alliance', label: 'Alliance', field: 'alliance', sortable: true },
  { name: 'villages', label: '# Villages', field: 'villages', sortable: true, align: 'right' },
  { name: 'population', label: 'Population', field: 'population', sortable: true, align: 'right' }
]

/* -----------------------------
 * Navigation
 * ----------------------------- */
function goToSelectedPlayer() {
  if (!selectedPlayer.value?.value) return
  router.push({ name: 'player-detail', params: { name: selectedPlayer.value.value } })
}

function onSelectedPlayer(val) {
  if (!val?.value) return
  router.push({ name: 'player-detail', params: { name: val.value } })
}

/**
 * QSelect filter
 */
function filterPlayers(needle, update) {
  update(async () => {
    optionsLoading.value = true
    const n = (needle || '').trim().toLowerCase()

    let list = (players.value || []).map(p => ({
      label: p.name,
      value: p.name,
      alliance: p.alliance,
      villages: p.villages,
      population: p.population
    }))

    if (n) list = list.filter(o => (o.label || '').toLowerCase().includes(n))
    list.sort((a, b) => Number(b.population || 0) - Number(a.population || 0))
    playerOptions.value = list.slice(0, 40)

    // Enrich alliances for shown autocomplete results
    await enrichVisibleAlliances(playerOptions.value.map(o => ({ name: o.value, alliance: o.alliance })))

    // Refresh options from updated players/cache
    playerOptions.value = (playerOptions.value || []).map(o => ({
      ...o,
      alliance: o.alliance || getAllianceForName(o.value)
    }))

    optionsLoading.value = false
  })
}

/* -----------------------------
 * Derived stats + filters
 * ----------------------------- */
const filteredPlayers = computed(() => {
  const f = nameFilter.value.trim().toLowerCase()
  return (players.value || []).filter(p => !f || (p.name || '').toLowerCase().includes(f))
})

const totalVillages = computed(() => filteredPlayers.value.reduce((sum, p) => sum + Number(p.villages || 0), 0))
const totalPopulation = computed(() => filteredPlayers.value.reduce((sum, p) => sum + Number(p.population || 0), 0))
const avgPopulation = computed(() => (filteredPlayers.value.length ? Math.round(totalPopulation.value / filteredPlayers.value.length) : 0))

/**
 * Current visible rows (for alliance enrichment)
 */
const visibleRows = computed(() => {
  const rows = filteredPlayers.value || []
  const { page, rowsPerPage } = pagination.value || { page: 1, rowsPerPage: 20 }
  const start = (Math.max(1, page) - 1) * rowsPerPage
  const end = start + rowsPerPage
  return rows.slice(start, end)
})

watch(
  () => [visibleRows.value.map(r => r.name).join('|'), pagination.value.page, pagination.value.rowsPerPage],
  async () => {
    await enrichVisibleAlliances(visibleRows.value)
  },
  { immediate: true }
)

/* -----------------------------
 * Load data
 * ----------------------------- */
async function loadPlayers() {
  loading.value = true
  try {
    const { data } = await api.get('/api/players?limit=1000')
    const rows = Array.isArray(data) ? data : []

    const cached = allianceMap.value || {}

    players.value = rows
      .map((p) => {
        const name =
          (p?.name ?? p?.player_name ?? p?.playerName ?? p?.player)?.toString().trim() || ''

        // direct field from /api/players (often empty)
        let alliance =
          (p?.alliance ?? p?.alliance_tag ?? p?.allianceTag)?.toString().trim() || ''

        // fallback from cache (filled by per-player villages calls)
        if (!alliance && name && cached[name]) alliance = cached[name]

        return {
          ...p,
          name,
          alliance, // do NOT default to Natars; empty should stay empty if unknown
          villages: Number(p?.villages ?? 0),
          population: Number(p?.population ?? 0)
        }
      })
      .filter((p) => p.name.length > 0)
  } finally {
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
