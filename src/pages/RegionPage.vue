<template>
  <q-page padding class="row no-wrap regions-page">

    <!-- LEFT PANEL: Regions Table -->
    <div class="region-table column">
      <q-toolbar class="bg-primary text-white">
        <q-toolbar-title>Regions</q-toolbar-title>
      </q-toolbar>
      <div class="table-container">
        <q-table
          :columns="columns"
          :rows="rows"
          row-key="region"
          flat bordered separator="cell"
          :loading="loading"
          :pagination.sync="pagination"
          :rows-per-page-options="[10, 20, 50, 100]"
          @row-click="goToDetail"
        >
          <template #no-data>
            <q-spinner-dots size="2em" color="primary"/>
            <div class="text-center q-mt-md">No regions found.</div>
          </template>
        </q-table>
      </div>
    </div>

    <!-- RIGHT PANEL: Mini-Map + Top Alliance List -->
    <div class="region-map column">
      <q-toolbar class="bg-secondary text-white">
        <q-toolbar-title>Map &amp; Top Alliance</q-toolbar-title>
      </q-toolbar>

      <div class="full-map" @click="openMapDialog">
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
      </div>
    </div>

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
import { ref, onMounted } from 'vue'
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
const pagination = ref({ page: 1, rowsPerPage: 20 })
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

<style scoped>
.regions-page {
  height: calc(100vh - var(--q-header-height));
  padding: 0;
}

/* flex columns */
.region-table, .region-map {
  display: flex; flex-direction: column; min-height: 0;
}
.region-table {
  flex:1; border-right:1px solid #e0e0e0;
}
.table-container {
  flex:1; overflow:auto; min-height:0;
}

.region-map {
  width:300px;
}
.full-map {
  position:relative; flex-shrink:0; height:300px; background:#fafafa;
}
.map-object {
  width:100%; height:100%; display:block;
}
.map-click-overlay {
  position:absolute; top:0; left:0; right:0; bottom:0;
  cursor:zoom-in;
}
.region-list {
  overflow-y:auto;
  max-height: calc(100vh - 300px - 148px);
}
.text-red { color:#e74c3c; }

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
