<template>
  <q-page class="dashboard-page">
    <!-- Hero Section -->
    <section class="page-hero bg-positive text-white">
      <div class="container">
        <div class="row items-center q-py-xl">
          <div class="col-12 col-md-8">
            <h1 class="page-title q-mb-md">Region Analysis</h1>
            <p class="page-subtitle">
              Examine regional statistics, top alliances per region, and territorial control patterns
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
                <div class="text-h5 q-mb-xs">{{ rows.length }}</div>
                <div class="text-caption text-grey-7">Total Regions</div>
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
                <q-icon name="group" size="32px" color="primary" class="q-mb-sm" />
                <div class="text-h5 q-mb-xs">{{ totalPopulation.toLocaleString() }}</div>
                <div class="text-caption text-grey-7">Total Population</div>
              </q-card-section>
            </q-card>
          </div>
          <div class="col-12 col-sm-6 col-md-3">
            <q-card flat bordered class="stat-card">
              <q-card-section class="text-center">
                <q-icon name="groups" size="32px" color="accent" class="q-mb-sm" />
                <div class="text-h5 q-mb-xs">{{ uniqueAlliances }}</div>
                <div class="text-caption text-grey-7">Unique Alliances</div>
              </q-card-section>
            </q-card>
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
                <div class="text-h6 q-mb-md">Regions Overview</div>
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
                  @update:pagination="val => { pagination = val }"
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
                      <strong>{{ props.value.toLocaleString() }}</strong>
                    </q-td>
                  </template>
                  <template #body-cell-population="props">
                    <q-td :props="props" class="text-right">
                      <strong class="text-positive">{{ props.value.toLocaleString() }}</strong>
                    </q-td>
                  </template>
                  <template #body-cell-displayAlliance="props">
                    <q-td :props="props">
                      <q-chip
                        v-if="props.value"
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
        <div class="map-click-overlay"/>
      </div>

      <div class="region-list">
        <q-list bordered>
          <q-item v-for="r in rows" :key="r.region">
            <q-item-section>
              <div class="text-subtitle2">{{ r.region }}</div>
              <div class="text-caption">
                Top Alliance:
                <strong :class="{ 'text-red': r.npcDominated }">
                  {{ r.displayAlliance || '—' }}
                </strong>
              </div>
            </q-item-section>
          </q-item>
        </q-list>
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
          <q-btn dense flat round icon="close" @click="mapDialog = false"/>
          <q-toolbar-title>Region Map Overview</q-toolbar-title>
        </q-toolbar>
        <div class="modal-svg-container">
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
import { useRouter }    from 'vue-router'
import { api }          from 'boot/axios'

/* — CACHING — */
const CACHE_KEY = 'regionsCache'
const CACHE_TTL = 1000 * 60 * 60 * 24

function loadFromCache() {
  try {
    const raw = JSON.parse(localStorage.getItem(CACHE_KEY) || 'null')
    if (raw && Date.now() - raw.ts < CACHE_TTL) return raw.data
  } catch {}
  return null
}
function saveToCache(data) {
  localStorage.setItem(CACHE_KEY,
    JSON.stringify({ ts: Date.now(), data })
  )
}

/* — STATE — */
const router     = useRouter()
const loading    = ref(false)
const rows       = ref([])
const pagination = ref({ 
  sortBy: 'population',
  descending: true,
  page: 1,
  rowsPerPage: 20
})
const mapDialog  = ref(false)

/* refs to our <object> tags */
const miniSvgObject  = ref(null)
const modalSvgObject = ref(null)

/* — COLUMNS — */
const columns = [
  { name: 'region',          label: 'Region',       field: 'region',          sortable: true },
  { name: 'villages',        label: '# Villages',   field: 'villages',        sortable: true, align:'right' },
  { name: 'population',      label: 'Population',   field: 'population',      sortable: true, align:'right' },
  { name: 'displayAlliance', label: 'Top Alliance', field: 'displayAlliance', sortable: true }
]

const totalVillages = computed(() => {
  return rows.value.reduce((sum, r) => sum + (r.villages || 0), 0)
})

const totalPopulation = computed(() => {
  return rows.value.reduce((sum, r) => sum + (r.population || 0), 0)
})

const uniqueAlliances = computed(() => {
  const alliances = new Set()
  rows.value.forEach(r => {
    if (r.displayAlliance) alliances.add(r.displayAlliance)
  })
  return alliances.size
})

/* — LOAD DATA — */
async function loadRegions() {
  const cached = loadFromCache()
  if (cached) {
    rows.value = cached
    return
  }

  loading.value = true
  try {
    // 1) fetch the list of region names
    const { data: names } = await api.get('/api/region')
    
    if (!Array.isArray(names) || names.length === 0) {
      console.warn('No regions found')
      rows.value = []
      return
    }

    // 2) for each region, fetch its villages & compute stats
    const stats = await Promise.all(names.map(async region => {
      try {
        const { data } = await api.get(
          `/api/region/${encodeURIComponent(region)}/villages`
        )
        
        if (!data || !data.villages) {
          console.error(`No villages data for region ${region}:`, data)
          return {
            region,
            villages: 0,
            population: 0,
            displayAlliance: '',
            npcDominated: false
          }
        }
        
        const vs = data.villages
        const totalPop = vs.reduce((s,v) => s + (Number(v.population)||0), 0)

        // count alliances per region
        const counts = {}
        vs.forEach(v => {
          const a = v.alliance || v.alliance_tag || 'Natars'
          counts[a] = (counts[a]||0) + 1
        })
        const sorted = Object.entries(counts)
                             .sort(([,a],[,b]) => b - a)

        let displayAlliance = '', npcDominated = false
        if (sorted.length) {
          if (sorted[0][0] === 'Natars' && sorted.length > 1) {
            npcDominated    = true
            displayAlliance = sorted[1][0]
          }
          else {
            displayAlliance = sorted[0][0]
          }
        }

        return {
          region,
          villages:        vs.length,
          population:      totalPop,
          displayAlliance,
          npcDominated
        }
      } catch (err) {
        console.error(`Error fetching villages for region ${region}:`, err)
        return {
          region,
          villages: 0,
          population: 0,
          displayAlliance: '',
          npcDominated: false
        }
      }
    }))

    rows.value = stats.filter(r => r) // Filter out any null/undefined results
    saveToCache(rows.value)
  } catch (err) {
    console.error('Error loading regions:', err)
    rows.value = []
  } finally {
    loading.value = false
  }
}

/* — ROUTER — */
function goToDetail(evt, row) {
  router.push({ name: 'region-detail', params: { name: row.region } })
}

/* — SVG ANNOTATION — */
function getRegionColor(i) {
  return `hsl(${(i*137)%360},60%,70%)`
}

function annotateSvg(svg) {
  if (!svg) return
  rows.value.forEach((r,idx) => {
    const els = svg.querySelectorAll(`#${CSS.escape(r.region)}`)
    if (!els.length) return
    const color = getRegionColor(idx)
    els.forEach(el => {
      el.setAttribute('fill', color)
      el.setAttribute('stroke','#333')
      el.setAttribute('stroke-width','0.2')
    })

    // label only on first
    const first = els[0]
    const bb = first.getBBox()
    const x = bb.x + bb.width/2
    const y = bb.y + bb.height/2

    const text = document.createElementNS(
      'http://www.w3.org/2000/svg','text'
    )
    text.setAttribute('x',      x    )
    text.setAttribute('y',      y    )
    text.setAttribute('text-anchor','middle')
    text.setAttribute('alignment-baseline','middle')
    text.setAttribute('font-size','5')
    text.setAttribute('fill','#222')
    text.setAttribute('font-family','sans-serif')
    text.setAttribute('pointer-events','none')
    text.innerHTML =
      `${r.region}<tspan x="${x}" dy="6">(${r.displayAlliance})</tspan>`

    first.parentNode.appendChild(text)
  })
}

/* — MOUNT — */
onMounted(loadRegions)

function onMiniMapLoad() {
  const doc = miniSvgObject.value.contentDocument
  annotateSvg(doc && doc.querySelector('svg'))
}
function onModalMapLoad() {
  const doc = modalSvgObject.value.contentDocument
  annotateSvg(doc && doc.querySelector('svg'))
}
function openMapDialog() {
  mapDialog.value = true
}
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
  background: linear-gradient(135deg, $positive 0%, #1a9539 100%);
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

.region-link {
  color: $positive;
  text-decoration: none;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  transition: color 0.2s;
  
  &:hover {
    color: #1a9539;
    text-decoration: underline;
  }
}

.full-map {
  position: relative;
  flex-shrink: 0;
  height: 300px;
  background: #fafafa;
  border-radius: 4px;
  overflow: hidden;
}

.map-object {
  width: 100%;
  height: 100%;
  display: block;
}

.map-click-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  cursor: zoom-in;
}

.region-list {
  overflow-y: auto;
  max-height: 400px;
}

.text-red {
  color: #e74c3c;
}

/* dialog tweaks */
.no-scroll-dialog .q-dialog__inner { overflow:hidden !important; }
.dialog-card {
  display:flex; flex-direction:column; height:100vh; background:transparent;
}
.dialog-toolbar { z-index:10; }
.modal-svg-container {
  flex:1; position:relative; overflow:hidden;
}
.modal-map-object {
  width:100%; height:100%; display:block;
}
</style>
