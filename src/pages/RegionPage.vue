<template>
  <q-page class="dashboard-page">
    <!-- Hero Section -->
    <section class="page-hero bg-positive text-white">
      <div class="container">
        <div class="row items-center q-py-xl">
          <div class="col-12 col-md-8">
            <h1 class="page-title q-mb-md">Region Analysis</h1>
            <p class="page-subtitle">
              Progressive region loading (no more “N requests at once”) with daily caching
            </p>
          </div>
          <div class="col-12 col-md-4 q-mt-md q-mt-md-none text-center">
            <q-icon name="terrain" size="120px" class="hero-icon" />
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
                <q-icon name="terrain" size="32px" color="positive" class="q-mb-sm" />
                <div class="text-h5 q-mb-xs">{{ rows.length.toLocaleString() }}</div>
                <div class="text-caption text-grey-7">Total Regions</div>
              </q-card-section>
            </q-card>
          </div>

          <div class="col-12 col-sm-6 col-md-3">
            <q-card flat bordered class="stat-card">
              <q-card-section class="text-center">
                <q-icon name="location_city" size="32px" color="secondary" class="q-mb-sm" />
                <div class="text-h5 q-mb-xs">{{ totalVillages.toLocaleString() }}</div>
                <div class="text-caption text-grey-7">Total Villages (loaded)</div>
              </q-card-section>
            </q-card>
          </div>

          <div class="col-12 col-sm-6 col-md-3">
            <q-card flat bordered class="stat-card">
              <q-card-section class="text-center">
                <q-icon name="group" size="32px" color="primary" class="q-mb-sm" />
                <div class="text-h5 q-mb-xs">{{ totalPopulation.toLocaleString() }}</div>
                <div class="text-caption text-grey-7">Total Population (loaded)</div>
              </q-card-section>
            </q-card>
          </div>

          <div class="col-12 col-sm-6 col-md-3">
            <q-card flat bordered class="stat-card">
              <q-card-section class="text-center">
                <q-icon name="speed" size="32px" color="accent" class="q-mb-sm" />
                <div class="text-h5 q-mb-xs">{{ loadedCount.toLocaleString() }}</div>
                <div class="text-caption text-grey-7">Regions Loaded</div>
              </q-card-section>
            </q-card>
          </div>
        </div>

        <div class="row q-mt-md">
          <div class="col-12 row justify-end q-gutter-sm">
            <q-btn dense outline icon="refresh" label="Refresh" :loading="loading" @click="refresh()" />
            <q-btn dense outline icon="delete" label="Clear cache (today)" :disable="loading" @click="clearTodayCache()" />
          </div>
        </div>
      </div>
    </section>

    <!-- Main Content -->
    <section class="content-section q-pa-md">
      <div class="container">
        <div class="row q-col-gutter-md">
          <!-- LEFT PANEL: Regions Table -->
          <div class="col-12 col-lg-8">
            <q-card flat bordered class="main-card">
              <q-card-section>
                <div class="text-h6 q-mb-xs">Regions Overview</div>
                <div class="text-caption text-grey-7">
                  Loads region names instantly; stats load progressively for the visible page (cached per region for today).
                </div>
              </q-card-section>

              <q-separator />

              <q-card-section class="q-pa-none">
                <q-table
                  :columns="columns"
                  :rows="rows"
                  row-key="region"
                  flat
                  bordered
                  separator="cell"
                  :loading="loading"
                  :pagination="pagination"
                  @update:pagination="onPagination"
                  :rows-per-page-options="[10, 20, 50, 100]"
                  class="modern-table"
                  @row-click="goToDetail"
                >
                  <template #body-cell-region="props">
                    <q-td :props="props">
                      <router-link
                        :to="{ name: 'region-detail', params: { name: props.row.region } }"
                        class="region-link"
                      >
                        <q-icon name="terrain" size="16px" class="q-mr-xs" />
                        {{ props.row.region }}
                      </router-link>
                    </q-td>
                  </template>

                  <template #body-cell-villages="props">
                    <q-td :props="props" class="text-right">
                      <q-skeleton v-if="props.value == null" type="text" width="50px" />
                      <strong v-else>{{ Number(props.value || 0).toLocaleString() }}</strong>
                    </q-td>
                  </template>

                  <template #body-cell-population="props">
                    <q-td :props="props" class="text-right">
                      <q-skeleton v-if="props.value == null" type="text" width="80px" />
                      <strong v-else class="text-positive">{{ Number(props.value || 0).toLocaleString() }}</strong>
                    </q-td>
                  </template>

                  <template #body-cell-displayAlliance="props">
                    <q-td :props="props">
                      <q-skeleton v-if="props.value == null" type="text" width="90px" />
                      <q-chip
                        v-else-if="props.value"
                        :label="props.value"
                        :color="props.row.npcDominated ? 'negative' : 'secondary'"
                        text-color="white"
                        size="sm"
                      />
                      <span v-else class="text-grey-6">—</span>
                    </q-td>
                  </template>

                  <template #no-data>
                    <div class="text-center q-pa-xl">
                      <q-icon name="terrain" size="4rem" class="text-grey q-mb-md" />
                      <div class="text-h6 text-grey">No regions found</div>
                    </div>
                  </template>

                  <template #loading>
                    <q-inner-loading showing color="positive" />
                  </template>
                </q-table>
              </q-card-section>
            </q-card>
          </div>

          <!-- RIGHT PANEL: Mini-Map + Top Alliance List -->
          <div class="col-12 col-lg-4">
            <q-card flat bordered class="main-card">
              <q-card-section>
                <div class="text-h6 q-mb-md">Map &amp; Top Alliances</div>
              </q-card-section>
              <q-separator />
              <q-card-section>
                <div class="full-map q-mb-md" @click="openMapDialog">
                  <object
                    ref="miniSvgObject"
                    type="image/svg+xml"
                    data="/regions.svg"
                    class="map-object"
                    @load="onMiniMapLoad"
                  ></object>
                  <div class="map-click-overlay" />
                </div>

                <div class="region-list">
                  <q-list bordered>
                    <q-item v-for="r in rows" :key="r.region">
                      <q-item-section>
                        <div class="text-subtitle2">{{ r.region }}</div>
                        <div class="text-caption">
                          Top Alliance:
                          <strong :class="{ 'text-red': r.npcDominated }">
                            <span v-if="r.displayAlliance == null">…</span>
                            <span v-else>{{ r.displayAlliance || '—' }}</span>
                          </strong>
                        </div>
                      </q-item-section>
                    </q-item>
                  </q-list>
                </div>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </div>
    </section>

    <!-- FULL-SCREEN SVG DIALOG -->
    <q-dialog
      v-model="mapDialog"
      maximized
      transition-show="zoom"
      transition-hide="zoom"
      class="no-scroll-dialog"
    >
      <q-card flat class="dialog-card">
        <q-toolbar class="bg-primary text-white dialog-toolbar">
          <q-btn dense flat round icon="close" @click="mapDialog = false" />
          <q-toolbar-title>Region Map Overview</q-toolbar-title>
        </q-toolbar>
        <div class="modal-svg-container">
          <q-inner-loading :showing="!mapDialogLoaded" color="primary">
            <q-spinner size="50px" />
            <div class="text-body2 q-mt-md">Loading map...</div>
          </q-inner-loading>
          <object
            ref="modalSvgObject"
            type="image/svg+xml"
            data="/regions.svg"
            class="modal-map-object"
            @load="onModalMapLoad"
          ></object>
        </div>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from 'boot/axios'

/* -----------------------------
 * Daily cache (UTC day)
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

/* -----------------------------
 * State
 * ----------------------------- */
const router = useRouter()
const loading = ref(false)

const rows = ref([]) // { region, villages, population, displayAlliance, npcDominated } (stats may be null while loading)
const pagination = ref({
  sortBy: 'population',
  descending: true,
  page: 1,
  rowsPerPage: 20
})

const mapDialog = ref(false)
const mapDialogLoaded = ref(false)
const miniSvgObject = ref(null)
const modalSvgObject = ref(null)

/* -----------------------------
 * Columns
 * ----------------------------- */
const columns = [
  { name: 'region', label: 'Region', field: 'region', sortable: true },
  { name: 'villages', label: '# Villages', field: 'villages', sortable: true, align: 'right' },
  { name: 'population', label: 'Population', field: 'population', sortable: true, align: 'right' },
  { name: 'displayAlliance', label: 'Top Alliance', field: 'displayAlliance', sortable: true }
]

/* -----------------------------
 * Aggregates (loaded only)
 * ----------------------------- */
const totalVillages = computed(() => rows.value.reduce((sum, r) => sum + (Number(r.villages) || 0), 0))
const totalPopulation = computed(() => rows.value.reduce((sum, r) => sum + (Number(r.population) || 0), 0))
const loadedCount = computed(() => rows.value.reduce((c, r) => c + (r.population != null ? 1 : 0), 0))

/* -----------------------------
 * Navigation
 * ----------------------------- */
function goToDetail(evt, row) {
  router.push({ name: 'region-detail', params: { name: row.region } })
}

/* -----------------------------
 * Region stats caching per region
 * ----------------------------- */
function regionStatsKey(region) {
  return cacheKey(`region:stats:${encodeURIComponent(region)}`)
}

function applyRegionStats(region, stats) {
  const idx = rows.value.findIndex(r => r.region === region)
  if (idx === -1) return
  rows.value[idx] = { ...rows.value[idx], ...stats }
}

/* -----------------------------
 * Compute region stats via villages endpoint
 * ----------------------------- */
async function fetchRegionStats(region) {
  // 1) cache
  const cached = readCache(regionStatsKey(region))
  if (cached && typeof cached === 'object') {
    applyRegionStats(region, cached)
    return
  }

  // 2) compute
  try {
    const { data } = await api.get(`/api/region/${encodeURIComponent(region)}/villages`)
    const vs = Array.isArray(data) ? data : Array.isArray(data?.villages) ? data.villages : []

    const totalPop = vs.reduce((s, v) => s + (Number(v.population) || 0), 0)

    // count alliances per region (filter out NPC - Natars)
    const counts = {}
    for (const v of vs) {
      const raw = (v.alliance ?? v.alliance_tag ?? '').toString().trim()
      const a = !raw || raw.toLowerCase() === 'natars' ? 'No alliance' : raw
      counts[a] = (counts[a] || 0) + 1
    }
    const sorted = Object.entries(counts)
      .filter(([tag]) => tag !== 'No alliance')
      .sort(([, a], [, b]) => b - a)

    let displayAlliance = ''
    let npcDominated = false
    if (sorted.length) {
      displayAlliance = sorted[0][0]
      npcDominated = (counts['No alliance'] || 0) > (counts[sorted[0][0]] || 0)
    }

    const stats = {
      villages: vs.length,
      population: totalPop,
      displayAlliance,
      npcDominated
    }

    applyRegionStats(region, stats)
    writeCache(regionStatsKey(region), stats)
  } catch {
    const stats = { villages: 0, population: 0, displayAlliance: '', npcDominated: false }
    applyRegionStats(region, stats)
    writeCache(regionStatsKey(region), stats)
  }
}

/* -----------------------------
 * Visible-page progressive loading
 * ----------------------------- */
function visibleRegionsForCurrentPage() {
  const list = rows.value
  const { page, rowsPerPage } = pagination.value
  const start = (page - 1) * rowsPerPage
  const end = start + rowsPerPage
  return list.slice(start, end).map(r => r.region)
}

async function loadVisibleStats() {
  const regions = visibleRegionsForCurrentPage()
  const need = regions.filter(region => {
    const r = rows.value.find(x => x.region === region)
    return r && r.population == null
  })
  if (!need.length) return

  await mapLimit(need, 6, async (region) => fetchRegionStats(region))
}

async function onPagination(val) {
  pagination.value = val
  await loadVisibleStats()
}

/* -----------------------------
 * Main loader
 * ----------------------------- */
async function loadRegions() {
  // quick restore of today’s list if present
  const listKey = cacheKey('regions:names')
  const cachedNames = readCache(listKey)
  if (Array.isArray(cachedNames) && cachedNames.length) {
    rows.value = cachedNames.map(region => ({
      region,
      villages: null,
      population: null,
      displayAlliance: null,
      npcDominated: false
    }))
    // load visible stats immediately
    await loadVisibleStats()
    // SWR: refresh names in background (optional)
    refreshNames({ silent: true })
    return
  }

  loading.value = true
  try {
    const { data: names } = await api.get('/api/region')
    if (!Array.isArray(names) || !names.length) {
      rows.value = []
      return
    }

    const cleaned = names.map(n => String(n).trim()).filter(Boolean)
    writeCache(listKey, cleaned)

    rows.value = cleaned.map(region => ({
      region,
      villages: null,
      population: null,
      displayAlliance: null,
      npcDominated: false
    }))
  } finally {
    loading.value = false
  }

  await loadVisibleStats()
}

async function refreshNames({ silent }) {
  if (!silent) loading.value = true
  try {
    const { data: names } = await api.get('/api/region')
    if (!Array.isArray(names) || !names.length) return
    const cleaned = names.map(n => String(n).trim()).filter(Boolean)
    writeCache(cacheKey('regions:names'), cleaned)

    // keep already loaded stats where possible
    const existing = new Map(rows.value.map(r => [r.region, r]))
    rows.value = cleaned.map(region => existing.get(region) || ({
      region,
      villages: null,
      population: null,
      displayAlliance: null,
      npcDominated: false
    }))
  } finally {
    if (!silent) loading.value = false
  }
}

/* -----------------------------
 * Actions
 * ----------------------------- */
async function refresh() {
  clearTodayCache()
  await loadRegions()
}

function clearTodayCache() {
  removeCache(cacheKey('regions:names'))
  // per-region caches are intentionally not swept (no index); they refresh as you browse pages
}

/* -----------------------------
 * SVG Map Dialog hooks (existing behavior)
 * ----------------------------- */
function openMapDialog() {
  mapDialogLoaded.value = false
  mapDialog.value = true
}
function onMiniMapLoad() {}
function onModalMapLoad() {
  mapDialogLoaded.value = true
}

onMounted(loadRegions)
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
  background: linear-gradient(135deg, $positive 0%, #167a4b 100%);
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
    transition: background-color 0.2s ease, transform 0.1s ease;

    &:hover {
      background-color: $grey-2;
      transform: translateX(2px);
    }
  }
}

.region-link {
  color: $positive;
  text-decoration: none;
  font-weight: 500;
  display: inline-flex;
  align-items: center;

  &:hover {
    text-decoration: underline;
  }
}

.full-map {
  position: relative;
  border: 1px solid $grey-4;
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
}
.map-object {
  width: 100%;
  height: 220px;
  display: block;
}
.map-click-overlay {
  position: absolute;
  inset: 0;
}
</style>
