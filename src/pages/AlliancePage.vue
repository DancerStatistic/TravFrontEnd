<template>
  <q-page class="dashboard-page">
    <!-- Hero Section -->
    <section class="page-hero bg-accent text-white">
      <div class="container">
        <div class="row items-center q-py-xl">
          <div class="col-12 col-md-8">
            <h1 class="page-title q-mb-md">Alliance Analytics</h1>
            <p class="page-subtitle">
              Explore alliance statistics with daily caching and progressive loading
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
                <div class="text-h5 q-mb-xs">{{ displayRows.length.toLocaleString() }}</div>
                <div class="text-caption text-grey-7">Total Alliances</div>
              </q-card-section>
            </q-card>
          </div>

          <div class="col-12 col-sm-6 col-md-3">
            <q-card flat bordered class="stat-card">
              <q-card-section class="text-center">
                <q-icon name="people" size="32px" color="primary" class="q-mb-sm" />
                <div class="text-h5 q-mb-xs">{{ totalPlayers.toLocaleString() }}</div>
                <div class="text-caption text-grey-7">Total Players (loaded)</div>
              </q-card-section>
            </q-card>
          </div>

          <div class="col-12 col-sm-6 col-md-3">
            <q-card flat bordered class="stat-card">
              <q-card-section class="text-center">
                <q-icon name="group" size="32px" color="secondary" class="q-mb-sm" />
                <div class="text-h5 q-mb-xs">{{ totalPopulation.toLocaleString() }}</div>
                <div class="text-caption text-grey-7">Total Population (loaded)</div>
              </q-card-section>
            </q-card>
          </div>

          <div class="col-12 col-sm-6 col-md-3">
            <q-card flat bordered class="stat-card">
              <q-card-section class="text-center">
                <q-icon name="bolt" size="32px" color="positive" class="q-mb-sm" />
                <div class="text-h5 q-mb-xs">{{ backendModeLabel }}</div>
                <div class="text-caption text-grey-7">Load Mode</div>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </div>
    </section>

    <!-- Main Content -->
    <section class="content-section q-pa-md">
      <div class="container">
        <q-card flat bordered class="main-card">
          <q-card-section>
            <div class="row items-center q-col-gutter-md">
              <div class="col-12 col-md-6">
                <q-input v-model="filters.alliance" outlined dense clearable label="Filter by tag…">
                  <template #prepend><q-icon name="filter_list" /></template>
                </q-input>
              </div>
              <div class="col-12 col-md-6 row justify-end items-center q-gutter-sm">
                <q-btn dense outline icon="refresh" label="Refresh" :loading="loading" @click="refresh()" />
                <q-btn dense outline icon="delete" label="Clear cache (today)" :disable="loading" @click="clearTodayCache()" />
              </div>
            </div>

            <q-banner v-if="loadHint" class="q-mt-md" dense rounded :class="backendMode === 'fast' ? 'bg-blue-1 text-blue-9' : 'bg-amber-1 text-amber-9'">
              <template #avatar>
                <q-icon :name="backendMode === 'fast' ? 'check_circle' : 'info'" :color="backendMode === 'fast' ? 'blue' : 'amber'" />
              </template>
              {{ loadHint }}
              <template #action>
                <q-chip
                  v-if="backendMode"
                  dense
                  size="sm"
                  :color="backendMode === 'fast' ? 'blue-2' : 'amber-2'"
                  :text-color="backendMode === 'fast' ? 'blue-9' : 'amber-9'"
                  :icon="backendMode === 'fast' ? 'bolt' : 'hourglass_empty'"
                  :label="backendModeLabel"
                />
              </template>
            </q-banner>
          </q-card-section>

          <q-separator />

          <q-card-section class="q-pa-none">
            <q-table
              :columns="columns"
              :rows="displayRows"
              row-key="alliance"
              flat
              bordered
              separator="cell"
              :loading="loading"
              :pagination="pagination"
              @update:pagination="onPagination"
              :rows-per-page-options="[20, 50, 100]"
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
                  <q-skeleton v-if="props.value == null" type="text" width="40px" />
                  <q-chip v-else :label="props.value" color="primary" text-color="white" size="sm" />
                </q-td>
              </template>

              <template #body-cell-population="props">
                <q-td :props="props" class="text-right">
                  <q-skeleton v-if="props.value == null" type="text" width="70px" />
                  <strong v-else class="text-accent">{{ Number(props.value || 0).toLocaleString() }}</strong>
                </q-td>
              </template>

              <template #body-cell-topRegion="props">
                <q-td :props="props">
                  <q-skeleton v-if="props.value == null" type="text" width="90px" />
                  <q-chip v-else-if="props.value" :label="props.value" color="secondary" text-color="white" size="sm" />
                  <span v-else class="text-grey-6">—</span>
                </q-td>
              </template>

              <template #no-data>
                <div class="text-center q-pa-xl">
                  <q-icon name="groups" size="4rem" class="text-grey q-mb-md" />
                  <div class="text-h6 text-grey">No alliances found</div>
                  <div class="text-body2 text-grey-7 q-mt-sm">Try adjusting your filter</div>
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
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { api } from 'boot/axios'

/* -----------------------------
 * Daily cache (UTC)
 * ----------------------------- */
function dayKeyUTC() {
  return new Date().toISOString().slice(0, 10)
}
function cacheKey(base) {
  return `${base}:${dayKeyUTC()}`
}
function readCache(key) {
  try {
    const raw = localStorage.getItem(key)
    if (!raw) return null
    return JSON.parse(raw)
  } catch {
    return null
  }
}
function writeCache(key, data) {
  try {
    localStorage.setItem(key, JSON.stringify(data))
  } catch {}
}
function removeCache(key) {
  try {
    localStorage.removeItem(key)
  } catch {}
}

/* -----------------------------
 * Concurrency helper
 * ----------------------------- */
async function mapLimit(items, limit, mapper) {
  const ret = new Array(items.length)
  let i = 0
  const workers = new Array(Math.min(limit, items.length)).fill(0).map(async () => {
    while (i < items.length) {
      const idx = i++
      ret[idx] = await mapper(items[idx], idx)
    }
  })
  await Promise.all(workers)
  return ret
}

const router = useRouter()
const loading = ref(false)

const backendMode = ref('') // "fast" | "fallback"
const loadHint = ref('')

const pagination = ref({
  sortBy: 'population',
  descending: true,
  page: 1,
  rowsPerPage: 20
})

const columns = [
  { name: 'alliance', label: 'Alliance', field: 'alliance', sortable: true },
  { name: 'players', label: '# Players', field: 'players', sortable: true, align: 'right' },
  { name: 'population', label: 'Population', field: 'population', sortable: true, align: 'right' },
  { name: 'topRegion', label: 'Top Region', field: 'topRegion', sortable: true }
]

const filters = reactive({ alliance: '' })

/**
 * Base rows (unsorted storage).
 * In fallback mode these start null and fill in.
 */
const rows = ref([])

/* -----------------------------
 * Navigation
 * ----------------------------- */
function goToDetail(evt, row) {
  router.push({ name: 'alliance-detail', params: { tag: row.alliance } })
}

/* -----------------------------
 * Fast path: /api/alliances
 * ----------------------------- */
function normalizeAllianceRow(a) {
  const tag = (a?.alliance_tag ?? a?.tag ?? a?.alliance ?? a?.name ?? a?.id ?? '').toString().trim()
  const players = a?.players ?? a?.player_count ?? a?.members ?? a?.member_count ?? null
  const population = a?.population ?? a?.pop ?? a?.total_population ?? null
  const topRegion = a?.topRegion ?? a?.top_region ?? null

  return {
    alliance: tag,
    players: players == null ? null : Number(players),
    population: population == null ? null : Number(population),
    topRegion: topRegion == null ? null : String(topRegion)
  }
}

async function loadAlliancesFast() {
  const key = cacheKey('alliances:list')
  const cached = readCache(key)
  if (Array.isArray(cached)) {
    rows.value = cached
    backendMode.value = 'fast'
    loadHint.value = 'Loaded from cache (today).'
    refreshFast({ silent: true })
    return true
  }
  return refreshFast({ silent: false })
}

async function refreshFast({ silent }) {
  if (!silent) loading.value = true
  try {
    const res = await api.get('/api/alliances')
    const data = res?.data
    const list = Array.isArray(data) ? data : Array.isArray(data?.items) ? data.items : null
    if (!list) return false

    const normalized = list
      .map(normalizeAllianceRow)
      .filter(r => r.alliance.length > 0)
      .filter(r => r.alliance.toLowerCase() !== 'natars') // exclude NPC
    rows.value = normalized
    writeCache(cacheKey('alliances:list'), normalized)

    backendMode.value = 'fast'
    loadHint.value = silent ? 'Updated in background.' : 'Loaded via single API call and cached for today.'
    return true
  } catch {
    return false
  } finally {
    if (!silent) loading.value = false
  }
}

/* -----------------------------
 * Fallback: global population rank from villages (used for sorting BEFORE stats exist)
 * ----------------------------- */
const alliancePopMap = ref(new Map()) // tag -> pop (estimated)
const rankBuilt = ref(false)

function rankCacheKey() {
  return cacheKey('alliances:popMap')
}

function readVillageAllianceTag(v) {
  const raw =
    (v?.alliance ??
      v?.alliance_tag ??
      v?.allianceTag ??
      v?.ally_tag ??
      v?.allyTag ??
      v?.ally ??
      '') ?? ''
  const tag = String(raw).trim()
  if (!tag || tag.toLowerCase() === 'natars') return 'No alliance'
  return tag
}

async function buildAlliancePopMap() {
  if (rankBuilt.value) return

  const cached = readCache(rankCacheKey())
  if (cached && typeof cached === 'object' && Array.isArray(cached.entries)) {
    alliancePopMap.value = new Map(cached.entries)
    rankBuilt.value = true
    return
  }

  let villages = []
  try {
    const { data } = await api.get('/api/villages?limit=20000')
    villages = Array.isArray(data) ? data : (Array.isArray(data?.villages) ? data.villages : [])
  } catch {
    try {
      const { data } = await api.get('/api/villages')
      villages = Array.isArray(data) ? data : (Array.isArray(data?.villages) ? data.villages : [])
    } catch {
      villages = []
    }
  }

  const totals = new Map()
  for (const v of villages) {
    const tag = readVillageAllianceTag(v)
    if (tag === 'No alliance') continue // skip NPC / no-alliance for alliance ranking
    const pop = Number(v?.population || 0)
    totals.set(tag, (totals.get(tag) || 0) + pop)
  }

  alliancePopMap.value = totals
  rankBuilt.value = true
  writeCache(rankCacheKey(), { entries: Array.from(totals.entries()) })
}

function estimatedPop(tag) {
  return alliancePopMap.value.get(tag) || 0
}

/* -----------------------------
 * Filtering + sorting (CRITICAL FIX)
 * We sort in Vue using either real population or estimated population,
 * so the “first page” is truly the top-pop alliances even before stats load.
 * ----------------------------- */
const filteredBaseRows = computed(() => {
  const f = (filters.alliance || '').trim().toLowerCase()
  if (!f) return rows.value
  return rows.value.filter(r => (r.alliance || '').toLowerCase().includes(f))
})

function sortKey(row, sortBy) {
  if (sortBy === 'population') {
    if (row.population != null) return Number(row.population) || 0
    return estimatedPop(row.alliance)
  }
  if (sortBy === 'players') {
    return Number(row.players) || 0
  }
  if (sortBy === 'alliance') {
    return (row.alliance || '').toLowerCase()
  }
  if (sortBy === 'topRegion') {
    return (row.topRegion || '').toLowerCase()
  }
  return 0
}

const displayRows = computed(() => {
  const list = [...filteredBaseRows.value]
  const sortBy = pagination.value.sortBy || 'population'
  const desc = !!pagination.value.descending

  list.sort((a, b) => {
    const ka = sortKey(a, sortBy)
    const kb = sortKey(b, sortBy)

    if (typeof ka === 'string' && typeof kb === 'string') {
      const cmp = ka.localeCompare(kb)
      return desc ? -cmp : cmp
    }

    const na = Number(ka) || 0
    const nb = Number(kb) || 0
    const cmp = na === nb ? 0 : (na < nb ? -1 : 1)
    return desc ? -cmp : cmp
  })

  return list
})

/* -----------------------------
 * Aggregates (loaded only)
 * ----------------------------- */
const totalPlayers = computed(() => displayRows.value.reduce((sum, r) => sum + (Number(r.players) || 0), 0))
const totalPopulation = computed(() => displayRows.value.reduce((sum, r) => sum + (Number(r.population) || 0), 0))

const backendModeLabel = computed(() => {
  if (backendMode.value === 'fast') return 'Fast (1 call)'
  if (backendMode.value === 'fallback') return 'Lazy (pop-first)'
  return '—'
})

/* -----------------------------
 * Fallback path:
 * - fetch tags list
 * - load stats for the VISIBLE slice of displayRows (already pop-sorted)
 * ----------------------------- */
function tagStatsCacheKey(tag) {
  return cacheKey(`alliances:tag:${encodeURIComponent(tag)}`)
}

function applyTagStats(tag, stats) {
  const idx = rows.value.findIndex(r => r.alliance === tag)
  if (idx === -1) return
  rows.value[idx] = { ...rows.value[idx], ...stats }
}

async function fetchStatsForTag(tag) {
  const cached = readCache(tagStatsCacheKey(tag))
  if (cached && typeof cached === 'object') {
    applyTagStats(tag, cached)
    return
  }

  try {
    const { data } = await api.get(`/api/alliance/${encodeURIComponent(tag)}/villages`)
    const vs = Array.isArray(data) ? data : Array.isArray(data?.villages) ? data.villages : []

    const playerSet = new Set(
      vs.map(v => (v.player_name ?? v.player ?? '').toString().trim()).filter(Boolean)
    )
    const totalPop = vs.reduce((sum, v) => sum + (Number(v.population) || 0), 0)

    const regionTotals = {}
    for (const v of vs) {
      const region = (v.region ?? '').toString().trim()
      if (!region) continue
      regionTotals[region] = (regionTotals[region] || 0) + (Number(v.population) || 0)
    }
    let topRegion = ''
    let topVal = -1
    for (const [r, val] of Object.entries(regionTotals)) {
      if (val > topVal) {
        topVal = val
        topRegion = r
      }
    }

    const stats = { players: playerSet.size, population: totalPop, topRegion }
    applyTagStats(tag, stats)
    writeCache(tagStatsCacheKey(tag), stats)
  } catch {
    const stats = { players: 0, population: 0, topRegion: '' }
    applyTagStats(tag, stats)
    writeCache(tagStatsCacheKey(tag), stats)
  }
}

function visibleTagsForCurrentPage() {
  const { page, rowsPerPage } = pagination.value
  const start = (page - 1) * rowsPerPage
  const end = start + rowsPerPage
  return displayRows.value.slice(start, end).map(r => r.alliance)
}

async function loadVisibleStats() {
  const tags = visibleTagsForCurrentPage()
  const need = tags.filter(tag => {
    const r = rows.value.find(x => x.alliance === tag)
    return r && (r.players == null || r.population == null || r.topRegion == null)
  })
  if (!need.length) return
  await mapLimit(need, 6, async (tag) => fetchStatsForTag(tag))
}

async function loadAlliancesFallback() {
  backendMode.value = 'fallback'
  loadHint.value =
    'Backend does not provide aggregated alliance stats; ordering by estimated population and loading visible top-pop alliances first (cached per alliance for today).'

  const listKey = cacheKey('alliances:tags')
  const cachedTags = readCache(listKey)

  // Build pop map first so sorting works immediately
  await buildAlliancePopMap()

  if (Array.isArray(cachedTags) && cachedTags.length) {
    rows.value = cachedTags.map(tag => ({ alliance: tag, players: null, population: null, topRegion: null }))
    await loadVisibleStats()
    return
  }

  loading.value = true
  try {
    const { data: tags } = await api.get('/api/alliance')
    if (!Array.isArray(tags) || !tags.length) {
      rows.value = []
      return
    }
    const cleaned = tags.map(t => String(t).trim()).filter(Boolean)
    rows.value = cleaned.map(tag => ({ alliance: tag, players: null, population: null, topRegion: null }))
    writeCache(listKey, cleaned)
  } finally {
    loading.value = false
  }

  await loadVisibleStats()
}

/* -----------------------------
 * Public actions
 * ----------------------------- */
async function refresh() {
  clearTodayCache()
  await loadAlliances()
}

function clearTodayCache() {
  removeCache(cacheKey('alliances:list'))
  removeCache(cacheKey('alliances:tags'))
  removeCache(rankCacheKey())
  alliancePopMap.value = new Map()
  rankBuilt.value = false
  loadHint.value = 'Cleared today’s cache. Stats will repopulate as you browse.'
}

/* -----------------------------
 * Pagination hook
 * ----------------------------- */
async function onPagination(val) {
  pagination.value = val
  if (backendMode.value === 'fallback') {
    await loadVisibleStats()
  }
}

/* -----------------------------
 * Main loader
 * ----------------------------- */
async function loadAlliances() {
  const ok = await loadAlliancesFast()
  if (!ok) {
    await loadAlliancesFallback()
  }
}

watch(
  () => filters.alliance,
  async () => {
    if (backendMode.value === 'fallback') {
      await Promise.resolve()
      await loadVisibleStats()
    }
  }
)

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
  transition: transform 0.2s, box-shadow 0.2s, opacity 0.3s ease-in;
  height: 100%;
  animation: fadeInUp 0.4s ease-out;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
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

  &:hover {
    text-decoration: underline;
  }
}
</style>
