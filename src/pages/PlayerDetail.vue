<template>
  <q-page class="player-detail-page column no-wrap">
    <!-- Toolbar -->
    <q-toolbar class="bg-primary text-white">
      <q-btn dense flat round icon="arrow_back" @click="goBack" />
      <q-toolbar-title>Player: {{ playerName }}</q-toolbar-title>

      <div class="row items-center q-gutter-sm on-right q-pr-sm">
        <q-chip dense square color="white" text-color="primary" icon="groups">
          {{ kpis.villages }} villages
        </q-chip>
        <q-chip dense square color="white" text-color="primary" icon="diversity_3">
          {{ kpis.population.toLocaleString() }} pop
        </q-chip>
        <q-chip dense square color="white" text-color="primary" icon="star">
          {{ kpis.vp.toLocaleString() }} VP
        </q-chip>

        <q-btn
          v-if="playerId"
          dense
          flat
          round
          icon="open_in_new"
          :href="profileLink"
          target="_blank"
        >
          <q-tooltip>Open Travian profile</q-tooltip>
        </q-btn>
      </div>
    </q-toolbar>

    <!-- Error -->
    <div v-if="error" class="q-pa-md">
      <q-banner type="negative">{{ error }}</q-banner>
    </div>

    <!-- Content -->
    <div v-else class="q-pa-md content-wrap">
      <div class="row q-col-gutter-md">
        <!-- Left Column: Player Stats -->
        <div class="col-12 col-md-4">
          <q-card flat bordered class="q-mb-md">
            <q-card-section class="bg-primary text-white">
              <div class="text-h6">Player Statistics</div>
            </q-card-section>

            <q-card-section v-if="villages.length > 0" class="q-pa-none">
              <q-list>
                <q-item>
                  <q-item-section>
                    <q-item-label>Total Villages</q-item-label>
                    <q-item-label caption>{{ kpis.villages }}</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-icon name="home" color="primary" />
                  </q-item-section>
                </q-item>

                <q-separator />

                <q-item>
                  <q-item-section>
                    <q-item-label>Total Population</q-item-label>
                    <q-item-label caption>{{ kpis.population.toLocaleString() }}</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-icon name="groups" color="green" />
                  </q-item-section>
                </q-item>

                <q-separator />

                <q-item>
                  <q-item-section>
                    <q-item-label>Victory Points</q-item-label>
                    <q-item-label caption>{{ kpis.vp.toLocaleString() }}</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-icon name="military_tech" color="amber" />
                  </q-item-section>
                </q-item>
              </q-list>
            </q-card-section>

            <q-card-section v-else class="text-center q-pa-lg">
              <q-spinner color="primary" size="3em" />
              <div class="q-mt-sm">Loading player data...</div>
            </q-card-section>
          </q-card>

          <q-card flat bordered class="q-mb-md">
            <q-card-section class="bg-primary text-white">
              <div class="text-h6">Village Distribution by Tribe</div>
            </q-card-section>
            <q-card-section>
              <div v-if="villages.length > 0">
                <div v-for="tribe in tribeDistribution" :key="tribe.name" class="q-mb-sm">
                  <div class="row items-center q-gutter-sm">
                    <div class="col-3 text-right">
                      <q-badge :color="getTribeColor(tribe.name)" class="text-body2">
                        {{ tribe.name || 'Unknown' }}
                      </q-badge>
                    </div>
                    <div class="col-6">
                      <q-linear-progress
                        :value="tribe.count / villages.length"
                        :color="getTribeColor(tribe.name)"
                        size="20px"
                      >
                        <div class="absolute-full flex flex-center">
                          <q-badge
                            :color="getTribeColor(tribe.name, true)"
                            :text-color="$q.dark.isActive ? 'white' : 'dark'"
                            :label="`${tribe.count} (${((tribe.count / villages.length) * 100).toFixed(1)}%)`"
                          />
                        </div>
                      </q-linear-progress>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="text-center q-pa-lg">
                <q-spinner color="primary" size="2em" />
                <div class="q-mt-sm">Loading village data...</div>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <!-- Right Column: Map & Charts Tabs -->
        <div class="col-12 col-md-8">
          <q-card flat bordered class="map-card">
            <!-- Tabs -->
            <q-tabs
              v-model="activeTab"
              dense
              class="text-grey"
              active-color="primary"
              indicator-color="primary"
              align="left"
            >
              <q-tab name="map" label="Villages Map" icon="map" />
              <q-tab name="charts" label="Charts" icon="show_chart" />
            </q-tabs>

            <q-separator />

            <q-tab-panels v-model="activeTab" animated class="tab-panels-container">
              <!-- Villages Map Tab -->
              <q-tab-panel name="map" class="q-pa-none map-tab-panel">
                <div class="map-controls q-pa-sm row items-center q-gutter-sm">
                  <q-space />
                  <q-btn flat dense icon="center_focus_strong" @click="fitToContent">
                    <q-tooltip>Fit to player villages</q-tooltip>
                  </q-btn>
                  <q-btn flat dense icon="refresh" @click="resetView">
                    <q-tooltip>Reset view</q-tooltip>
                  </q-btn>
                </div>

            <div
              class="map-area"
              ref="mapAreaEl"
              @contextmenu.capture="onContextMenu"
              style="min-height: 500px;"
            >
              <svg
                class="map-svg"
                ref="svg"
                viewBox="-200 -200 400 400"
                preserveAspectRatio="xMidYMid meet"
                @mouseleave="hideTooltip"
                @pointerdown="onPointerDown"
                @pointermove="onPointerMove"
                @pointerup="onPointerUp"
              >
                <defs>
                  <pattern id="grid1" width="1" height="1" patternUnits="userSpaceOnUse">
                    <path d="M1 0 L0 0 0 1" fill="none" stroke="#343434" stroke-width="0.05" />
                  </pattern>
                  <pattern id="grid10" width="10" height="10" patternUnits="userSpaceOnUse">
                    <rect width="10" height="10" fill="url(#grid1)" />
                    <path d="M10 0 L0 0 0 10" fill="none" stroke="#585858" stroke-width="0.15" />
                  </pattern>
                </defs>

                <g ref="viewportEl">
                  <!-- background -->
                  <image
                    x="-200"
                    y="-200"
                    width="400"
                    height="400"
                    :href="bgUrl"
                    :xlink:href="bgUrl"
                    preserveAspectRatio="none"
                    opacity="0.65"
                  />

                  <!-- grid & axes -->
                  <rect x="-200" y="-200" width="400" height="400" fill="url(#grid10)" />
                  <line
                    x1="-200"
                    y1="0"
                    x2="200"
                    y2="0"
                    stroke="#9e9e9e"
                    stroke-width="1.2"
                    vector-effect="non-scaling-stroke"
                  />
                  <line
                    x1="0"
                    y1="-200"
                    x2="0"
                    y2="200"
                    stroke="#9e9e9e"
                    stroke-width="1.2"
                    vector-effect="non-scaling-stroke"
                  />
                  <rect
                    x="-200"
                    y="-200"
                    width="400"
                    height="400"
                    fill="none"
                    stroke="#00e5ff"
                    stroke-width="1.2"
                    opacity="0.25"
                    vector-effect="non-scaling-stroke"
                  />

                  <!-- markers -->
                  <g ref="markersGroup" id="markersLayer"></g>

                  <!-- hover highlight -->
                  <g id="overlayLayer">
                    <circle
                      v-if="selection"
                      :cx="selection.x"
                      :cy="selection.y"
                      :r="2.4"
                      fill="none"
                      stroke="#00e5ff"
                      stroke-width="0.8"
                      vector-effect="non-scaling-stroke"
                    />
                    <circle
                      v-if="selection"
                      :cx="selection.x"
                      :cy="selection.y"
                      :r="0.9"
                      fill="#00e5ff"
                      opacity="0.85"
                    />
                  </g>

                  <circle cx="0" cy="0" r="0.9" fill="#ff5252" opacity="0.9" />
                </g>

                <!-- screen-fixed coord labels -->
                <g>
                  <text
                    ref="labelLeft"
                    text-anchor="end"
                    alignment-baseline="middle"
                    class="coord-label"
                  />
                  <text
                    ref="labelRight"
                    text-anchor="start"
                    alignment-baseline="middle"
                    class="coord-label"
                  />
                  <text
                    ref="labelTop"
                    text-anchor="middle"
                    alignment-baseline="hanging"
                    class="coord-label"
                  />
                  <text
                    ref="labelBottom"
                    text-anchor="middle"
                    alignment-baseline="baseline"
                    class="coord-label"
                  />
                </g>
              </svg>

              <!-- Tooltip -->
              <div
                v-if="tooltip.show"
                class="tooltip"
                :style="{ top: tooltip.y + 'px', left: tooltip.x + 'px' }"
                v-html="tooltip.content"
              />
            </div>

            <div class="statusbar row items-center q-px-sm q-py-xs">
              <div class="col text-caption">
                Cursor: X {{ cursor.x.toFixed(0) }} / Y {{ cursor.y.toFixed(0) }}
              </div>
              <div class="col text-caption text-right">
                Zoom: {{ zoomK.toFixed(2) }}×
              </div>
            </div>

                <!-- Enhanced Context Menu -->
                <q-menu
                  v-model="showContextMenu"
                  context-menu
                  touch-position
                  @before-show="onBeforeContextMenuShow"
                  @hide="onContextMenuHide"
                  :style="{ left: `${contextPosition.x}px`, top: `${contextPosition.y}px` }"
                  class="context-menu"
                >
                  <q-list>
                    <q-item-label header>Village Actions</q-item-label>

                    <q-item clickable v-close-popup @click="centerOnContext" :disable="!ctx.hasMarker">
                      <q-item-section avatar><q-icon name="center_focus_strong" /></q-item-section>
                      <q-item-section>Center on village</q-item-section>
                    </q-item>

                    <q-item clickable v-close-popup @click="copyCoordinates">
                      <q-item-section avatar><q-icon name="content_copy" /></q-item-section>
                      <q-item-section>Copy coordinates</q-item-section>
                    </q-item>

                    <q-item clickable v-close-popup :href="getTravianMapLink" target="_blank">
                      <q-item-section avatar><q-icon name="open_in_new" /></q-item-section>
                      <q-item-section>Open in Travian Map</q-item-section>
                    </q-item>

                    <q-separator />

                    <q-item-label header>Map Controls</q-item-label>

                    <q-item clickable v-close-popup @click="fitToContent">
                      <q-item-section avatar><q-icon name="zoom_out_map" /></q-item-section>
                      <q-item-section>Fit to villages</q-item-section>
                    </q-item>

                    <q-item clickable v-close-popup @click="resetView">
                      <q-item-section avatar><q-icon name="refresh" /></q-item-section>
                      <q-item-section>Reset view</q-item-section>
                    </q-item>
                  </q-list>
                </q-menu>
              </q-tab-panel>

              <!-- Charts Tab -->
              <q-tab-panel name="charts" class="q-pa-md charts-tab-panel">
                <PlayerHistoryCharts 
                  v-if="playerHistory.length > 0"
                  :player-name="playerName" 
                  :history-data="playerHistory"
                />
                <div v-else class="text-center q-pa-lg text-grey-6">
                  <q-icon name="show_chart" size="3em" class="q-mb-md" />
                  <div>No historical data available for this player.</div>
                </div>
              </q-tab-panel>
            </q-tab-panels>
          </q-card>
        </div>
      </div>

      <!-- Villages table -->
      <div class="q-mt-md">
        <q-card flat bordered>
          <q-card-section class="row items-center q-gutter-sm">
            <q-input
              v-model="filter"
              dense
              outlined
              clearable
              debounce="150"
              placeholder="Filter villages / coords / alliance / region / tribe…"
              class="col-12 col-sm-6"
            >
              <template #append><q-icon name="search" /></template>
            </q-input>
            <q-space />
            <q-btn flat dense icon="file_download" @click="downloadCsv" :disable="!villages.length">
              <q-tooltip>Download CSV</q-tooltip>
            </q-btn>
          </q-card-section>

          <q-table
            :columns="columns"
            :rows="villagesFiltered"
            row-key="coords"
            flat
            bordered
            separator="cell"
            :pagination="pagination"
            :rows-per-page-options="[10, 20, 50, 0]"
            :filter="filter"
            dense
            wrap-cells
            @row-click="(_, row) => centerFromCoords(row.coords)"
          >
            <template #body-cell-coords="props">
              <q-td :props="props">
                <a
                  :href="makeMapLink(props.row.coords)"
                  target="_blank"
                  rel="noopener"
                  @mouseenter="hoverCoords(props.row.coords)"
                  @mouseleave="selection = null"
                  @click.stop
                >
                  {{ props.row.coords }}
                </a>
              </q-td>
            </template>

            <template #body-cell-alliance="props">
              <q-td :props="props">
                <RouterLink
                  v-if="props.row.alliance"
                  :to="{ name: 'alliance-detail', params: { tag: props.row.alliance } }"
                >
                  {{ props.row.alliance }}
                </RouterLink>
                <span v-else class="text-grey-6">—</span>
              </q-td>
            </template>

            <template #body-cell-tribe="props">
              <q-td :props="props">
                <q-badge outline color="grey-7">{{ props.row.tribe }}</q-badge>
              </q-td>
            </template>

            <template #no-data>
              <div class="text-center q-mt-md">No villages found.</div>
            </template>
          </q-table>
        </q-card>
      </div>
    </div>
  </q-page>
</template>


<script setup>
import { ref, reactive, computed, onMounted, nextTick, watch, onBeforeUnmount } from 'vue'
import { useQuasar, Notify } from 'quasar'
import PlayerHistoryCharts from 'src/components/PlayerHistoryCharts.vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import * as d3 from 'd3'
import { api } from 'boot/axios'
import bgUrl from 'assets/background.png'

/* routing */
const $q = useQuasar()
const route = useRoute()
const router = useRouter()
const playerName = ref(route.params.name)
watch(() => route.params.name, async (n) => {
  playerName.value = n
  resetState()
  await loadAll()
})

function goBack () {
  if (window.history.length > 1) router.back()
  else router.push('/')
}

/* 
 * Tribe mapping with case-insensitive matching
 * To debug, add this to browser console:
 *   window.debugTribe = function(t) {
 *     const s = String(t).trim().toLowerCase();
 *     return {
 *       input: t,
 *       type: typeof t,
 *       normalized: s,
 *       mapped: TRIBE_MAP[s] || 'No direct match',
 *       allTribes: TRIBE_MAP
 *     };
 *   }
 */
const TRIBE_MAP = {
  // Number to name mapping
  1: 'Romans', 2: 'Teutons', 3: 'Gauls', 4: 'Nature',
  5: 'Natars', 6: 'Egyptians', 7: 'Huns', 8: 'Spartans', 9: 'Vikings',
  // Case-insensitive string matching
  'romans': 'Romans', 'teutons': 'Teutons', 'gauls': 'Gauls', 'nature': 'Nature',
  'natars': 'Natars', 'egyptians': 'Egyptians', 'huns': 'Huns', 
  'spartans': 'Spartans', 'vikings': 'Vikings'
}

function mapTribe(t) {
  if (t == null || t === '') return 'Unknown'
  
  // Try to match by number
  const n = Number(t)
  if (!isNaN(n) && TRIBE_MAP[n]) return TRIBE_MAP[n]
  
  // Try to match by string (case-insensitive)
  const s = String(t).trim().toLowerCase()
  if (s in TRIBE_MAP) return TRIBE_MAP[s]
  
  // Try direct match with any case
  const directMatch = Object.entries(TRIBE_MAP).find(([_, value]) => 
    String(value).toLowerCase() === s
  )
  
  if (directMatch) return directMatch[1]
  
  // Fallback: capitalize first letter
  return s ? s.charAt(0).toUpperCase() + s.slice(1) : 'Unknown'
}

/* table data */
const villages   = ref([])
const filter     = ref('')
const pagination = ref({ page:1, rowsPerPage:10 })
const activeTab  = ref('map')

// Compute tribe distribution for the village distribution chart
const tribeDistribution = computed(() => {
  const tribes = {};
  
  villages.value.forEach(village => {
    const tribeName = village.tribe || 'Unknown';
    if (!tribes[tribeName]) {
      tribes[tribeName] = 0;
    }
    tribes[tribeName]++;
  });

  return Object.entries(tribes)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count);
});

// Get color for each tribe
function getTribeColor(tribeName, isLight = false) {
  const colors = {
    'Roman': 'blue',
    'Teuton': 'grey',
    'Gaul': 'green',
    'Nature': 'light-green',
    'Natar': 'red',
    'Egyptian': 'amber',
    'Hun': 'brown',
    'Spartan': 'red-10',
    'Unknown': 'grey-6'
  };

  const baseColor = colors[tribeName] || 'grey-5';
  return isLight ? `${baseColor}-2` : baseColor;
}
const columns = [
  { name:'village',       label:'Village',      field:'village',       align:'left',  sortable:true },
  { name:'coords',        label:'Coords',       field:'coords',        align:'left',  sortable:true },
  { name:'population',    label:'Population',   field:'population',    align:'right', sortable:true },
  { name:'victoryPoints', label:'VP',           field:'victoryPoints', align:'right', sortable:true },
  { name:'alliance',      label:'Alliance',     field:'alliance',      align:'left',  sortable:true },
  { name:'region',        label:'Region',       field:'region',        align:'left',  sortable:true },
  { name:'tribe',         label:'Tribe',        field:'tribe',         align:'left',  sortable:true }
]
const villagesFiltered = computed(() => {
  const q = filter.value.trim().toLowerCase()
  if (!q) return villages.value
  return villages.value.filter(r =>
    (r.village  || '').toLowerCase().includes(q) ||
    (r.coords   || '').toLowerCase().includes(q) ||
    (r.alliance || '').toLowerCase().includes(q) ||
    (r.region   || '').toLowerCase().includes(q) ||
    (r.tribe    || '').toLowerCase().includes(q)
  )
})

/* KPIs & links */
const playerId = ref(null)
const kpis = computed(() => {
  const v = villages.value
  const villagesCount = v.length
  const population = v.reduce((s, r) => s + (r.population || 0), 0)
  const vp         = v.reduce((s, r) => s + (r.victoryPoints || 0), 0)
  return { villages: villagesCount, population, vp }
})
const profileLink = computed(() =>
  playerId.value ? `https://nys.x1.europe.travian.com/profile/${playerId.value}` : '#'
)


function safeNotify(opts) {
  // Works whether Notify plugin is enabled or not
  if ($q && typeof $q.notify === 'function') {
    $q.notify(opts)
    return
  }
  console.warn('Notify unavailable:', opts?.message || opts)
}

const notifyError = (message) => {
  // Prefer Quasar Notify plugin API
  if (Notify?.create) {
    Notify.create({ type: 'negative', message })
    return
  }
  // Fallback if Notify plugin isn't available
  if ($q?.notify) {
    $q.notify({ type: 'negative', message })
    return
  }
  console.warn('Notify unavailable:', message)
}



/* helpers */
function makeMapLink(coords) {
  const m = coords.match(/\((-?\d+),\s*(-?\d+)\)/)
  return m ? `https://nys.x1.europe.travian.com/karte.php?x=${m[1]}&y=${m[2]}` : '#'
}
function parseCoords (coords) {
  const m = coords.match(/\((-?\d+),\s*(-?\d+)\)/)
  return m ? { x: Number(m[1]), y: Number(m[2]) } : null
}
function sanitizeTooltip (html) {
  try { if (window.DOMPurify?.sanitize) return window.DOMPurify.sanitize(html, { USE_PROFILES: { html:true, svg:true } }) } catch {}
  return String(html).replace(/<script[\s\S]*?<\/script>/gi, '')
}

/* map state */
const mapAreaEl    = ref(null)
const svg          = ref(null)
const viewportEl   = ref(null)
const markersGroup = ref(null)

const zoomK        = ref(1)
const cursor       = ref({ x:0, y:0 })
const tooltip      = ref({ show:false, x:0, y:0, content:'' })
const selection    = ref(null)
const ctx          = reactive({ hasMarker:false, point:null })

/* labels refs */
const labelLeft   = ref(null)
const labelRight  = ref(null)
const labelTop    = ref(null)
const labelBottom = ref(null)

/* world & zoom */
const WORLD = { x0:-200, y0:-200, x1:200, y1:200 }
let zoom
let suppressSnap = false // guard to avoid endless end->snap->transform loops

function getContainerRect () {
  const el = mapAreaEl.value || svg.value
  if (!el) return null
  const r = el.getBoundingClientRect()
  return (r.width > 0 && r.height > 0) ? r : null
}
function toMapCoords(evt) {
  if (!svg.value) return { x: 0, y: 0 }
  const pt = new DOMPoint(evt.clientX, evt.clientY)
  const svgPt = pt.matrixTransform(svg.value.getScreenCTM().inverse())
  return { x: svgPt.x, y: svgPt.y }
}

function updateLabels () {
  const box = getContainerRect()
  if (!box) return
  const t = d3.zoomTransform(svg.value)
  d3.select(labelLeft.value).text(t.invertX(0).toFixed(0)).attr('x', 5).attr('y', box.height / 2)
  d3.select(labelRight.value).text(t.invertX(box.width).toFixed(0)).attr('x', box.width - 5).attr('y', box.height / 2)
  d3.select(labelTop.value).text(t.invertY(0).toFixed(0)).attr('x', box.width / 2).attr('y', 5)
  d3.select(labelBottom.value).text(t.invertY(box.height).toFixed(0)).attr('x', box.width / 2).attr('y', box.height - 5)
}

function clampTransform(t) {
  const rect = getContainerRect()
  if (!rect) return t
  const { width:w, height:h } = rect
  const k = t.k
  let { x:tx, y:ty } = t

  const minTx = w - WORLD.x1 * k
  const maxTx = -WORLD.x0 * k
  const minTy = h - WORLD.y1 * k
  const maxTy = -WORLD.y0 * k

  if ((WORLD.x1 - WORLD.x0) * k <= w) {
    tx = (w - k * (WORLD.x1 - WORLD.x0)) / 2 - WORLD.x0 * k
  } else {
    tx = Math.max(Math.min(tx, maxTx), minTx)
  }
  if ((WORLD.y1 - WORLD.y0) * k <= h) {
    ty = (h - k * (WORLD.y1 - WORLD.y0)) / 2 - WORLD.y0 * k
  } else {
    ty = Math.max(Math.min(ty, maxTy), minTy)
  }
  return d3.zoomIdentity.translate(tx, ty).scale(k)
}
function snapBack() {
  if (suppressSnap) return
  const cur = d3.zoomTransform(svg.value)
  const clamped = clampTransform(cur)
  if (clamped.x !== cur.x || clamped.y !== cur.y) {
    suppressSnap = true
    d3.select(svg.value).transition().duration(100).call(zoom.transform, clamped).on('end', () => { suppressSnap = false })
  }
}

function centerAt(x, y, k = d3.zoomTransform(svg.value).k || 1) {
  const rect = getContainerRect()
  if (!rect || !Number.isFinite(x) || !Number.isFinite(y)) return
  
  k = Math.max(0.1, Math.min(k, 50)) // Ensure k is within reasonable bounds
  const tx = rect.width / 2 - k * x
  const ty = rect.height / 2 - k * y
  
  suppressSnap = true
  d3.select(svg.value)
    .transition()
    .duration(200)
    .call(
      zoom.transform,
      d3.zoomIdentity.translate(tx, ty).scale(k)
    )
    .on('end', () => { 
      suppressSnap = false 
      updateLabels()
    })
}

/* fit to the actual villages (built from rows) */
function villagesBBox() {
  if (!villages.value.length) return { x:-200, y:-200, width:400, height:400 }
  let minx=Infinity, miny=Infinity, maxx=-Infinity, maxy=-Infinity
  for (const r of villages.value) {
    const x = +r.x
    const y = -(+r.y) // svg coords
    if (x   < minx) minx = x
    if (y   < miny) miny = y
    if (x+1 > maxx) maxx = x+1
    if (y+1 > maxy) maxy = y+1
  }
  return { x:minx, y:miny, width:maxx-minx, height:maxy-miny }
}
function fitToContent() {
  const rect = getContainerRect()
  if (!rect || !villages.value.length) return
  
  const bbox = villagesBBox()
  const pad = 1.2 // Slightly more padding
  const k = Math.min(
    rect.width / (bbox.width * pad),
    rect.height / (bbox.height * pad)
  )
  
  const cx = bbox.x + bbox.width / 2
  const cy = bbox.y + bbox.height / 2
  const kClamped = Math.max(0.5, Math.min(k, 10)) // Limit max zoom
  
  centerAt(cx, cy, kClamped)
}
function resetView() {
  const rect = getContainerRect()
  if (!rect) return
  
  // Calculate the scale to fit the world view
  const worldWidth = WORLD.x1 - WORLD.x0
  const worldHeight = WORLD.y1 - WORLD.y0
  const scaleX = rect.width / (worldWidth * 1.1)  // 10% padding
  const scaleY = rect.height / (worldHeight * 1.1) // 10% padding
  const scale = Math.min(scaleX, scaleY, 1) // Don't zoom in beyond 1:1
  
  // Center the view
  const tx = (rect.width - worldWidth * scale) / 2 - WORLD.x0 * scale
  const ty = (rect.height - worldHeight * scale) / 2 - WORLD.y0 * scale
  
  // Apply the transform
  suppressSnap = true
  d3.select(svg.value)
    .transition()
    .duration(200)
    .call(
      zoom.transform,
      d3.zoomIdentity
        .translate(tx, ty)
        .scale(scale)
    )
    .on('end', () => {
      suppressSnap = false
      updateLabels()
    })
}

/* pointer + context (throttled UI updates) */
let cursorTick = 0
const showContextMenu = ref(false)
const contextPosition = ref({ x: 0, y: 0 })
function onPointerDown (evt) { throttledCursor(evt) }
function onPointerMove (evt) { throttledCursor(evt) }
function onPointerUp   (evt) { throttledCursor(evt) }
function throttledCursor(evt) {
  const now = performance.now()
  if (now - cursorTick < 60) return // ~16fps for statusbar
  cursorTick = now
  const p = toMapCoords(evt)
  cursor.value = p
}
function hideTooltip() { tooltip.value.show = false }

function onContextMenu(e) {
  e.preventDefault()
  const el = e.target.closest('.marker')
  ctx.hasMarker = !!el
  
  // Remove previous highlight if any
  d3.select(svg.value).selectAll('.marker.highlighted')
    .classed('highlighted', false)
    .attr('width', 1)
    .attr('height', 1)
    .attr('x', d => d.x - 0.5)
    .attr('y', d => d.y - 0.5)
  
  if (el) {
    // Highlight the selected village
    const marker = d3.select(el)
    marker
      .classed('highlighted', true)
      .attr('width', 2)
      .attr('height', 2)
      .attr('x', d => d.x - 1)
      .attr('y', d => d.y - 1)
      
    const bb = el.getBBox()
    ctx.point = { x: bb.x + bb.width / 2, y: bb.y + bb.height / 2 }
  } else {
    ctx.point = toMapCoords(e)
  }
  
  // Prevent any zoom behavior
  if (e.type === 'dblclick') {
    e.stopPropagation()
    return false
  }
  
  contextPosition.value = { x: e.clientX, y: e.clientY }
  showContextMenu.value = true
  return false
}

function onBeforeContextMenuShow() {
  document.addEventListener('click', handleClickOutside)
}

function onContextMenuHide() {
  document.removeEventListener('click', handleClickOutside)
}

function handleClickOutside(event) {
  if (showContextMenu.value && !event.target.closest('.q-menu')) {
    showContextMenu.value = false
  }
}

function copyCoordinates() {
  if (ctx.point) {
    const coords = `${Math.round(ctx.point.x)},${Math.round(-ctx.point.y)}`
    navigator.clipboard.writeText(coords)
  }
}

const getTravianMapLink = computed(() => {
  if (!ctx.point) return '#'
  const x = Math.round(ctx.point.x)
  const y = Math.round(-ctx.point.y)
  return `https://ts1.x1.europe.travian.com/karte.php?x=${x}&y=${y}`
})
function centerOnContext () { if (ctx.point) centerAt(ctx.point.x, ctx.point.y) }

/* hover from table */
function hoverCoords (coords) {
  const pt = parseCoords(coords)
  selection.value = pt ? { x: pt.x, y: -pt.y } : null
}
function centerFromCoords (coords) {
  const pt = parseCoords(coords)
  if (pt) centerAt(pt.x, -pt.y)
}

/* draw markers directly from villages */
function allianceColor(tag) {
  const s = (tag || 'Natars') + ''
  let h = 0
  for (let i=0;i<s.length;i++) h = (h*31 + s.charCodeAt(i)) >>> 0
  return `hsl(${h % 360},70%,50%)`
}
function drawMarkers() {
  const root = d3.select(markersGroup.value)
  root.selectAll('*').remove()
  if (!villages.value.length) return

  const data = villages.value.map(v => ({
    x: +v.x,
    y: -(+v.y),
    alliance: v.alliance || 'Natars',
    tribe: v.tribe || 'Unknown',
    village: v.village,
    player: v.player || playerName.value,
    population: +v.population || 0,
    fill: allianceColor(v.alliance)
  }))

  root.selectAll('rect.marker')
    .data(data)
    .enter()
    .append('rect')
    .attr('class', d => `marker alliance-${(d.alliance||'').toLowerCase().replace(/[^a-z0-9]+/g,'-')}`)
    .attr('x', d => d.x)
    .attr('y', d => d.y)
    .attr('width', 1)
    .attr('height', 1)
    .attr('fill', d => d.fill)
    .attr('stroke', 'black')
    .attr('stroke-width', 0.05)
    .attr('shape-rendering', 'crispEdges')
    .attr('vector-effect', 'non-scaling-stroke')
    .on('pointerover', (e, d) => {
      const coords = toMapCoords(e)
      const tip = `Village: ${d.village}<br>Player: ${d.player}<br>Population: ${d.population.toLocaleString()}<br>Alliance: ${d.alliance}<br>Tribe: ${d.tribe}`
      
      // Get the current transform to convert from SVG to screen coordinates
      const transform = d3.zoomTransform(svg.value)
      const screenX = transform.applyX(coords.x) + 10
      const screenY = transform.applyY(coords.y) + 10
      
      tooltip.value = { 
        show: true, 
        x: screenX, 
        y: screenY, 
        content: sanitizeTooltip(tip) 
      }
      ctx.hasMarker = true
    })
    .on('pointerout', () => hideTooltip())
}

/* data loading */
const error = ref(null)
const playerHistory = ref([])
function resetState() {
  error.value = null
  villages.value = []
  playerId.value = null
  selection.value = null
  playerHistory.value = []
}

const raf2 = () => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))

function debugHistoryData(history) {
  console.group('Player History Debug')
  console.log('History data received:', history)

  if (!Array.isArray(history) || history.length === 0) {
    console.warn('No history data available')
    console.groupEnd()
    return
  }

  console.log(`Found ${history.length} days of data`)

  // Log first and last entry
  console.log('First entry:', history[0])
  if (history.length > 1) {
    console.log('Last entry:', history[history.length - 1])
  }

  // Check data structure
  const sample = history[0] || {}
  const hasDate = !!(sample.date ?? sample.dump_date ?? sample.dumpDate)

  const missingFields = []
  if (!hasDate) missingFields.push('date')
  if (!('population' in sample)) missingFields.push('population')
  if (!('villages' in sample)) missingFields.push('villages')

  if (missingFields.length > 0) {
    console.error('Missing required fields:', missingFields)
  }

  // Check date range (supports both date and dump_date)
  const dates = history
    .map(h => (h.date ?? h.dump_date ?? h.dumpDate))
    .filter(Boolean)
    .sort()

  console.log('Date range:', dates[0], 'to', dates[dates.length - 1])

  console.groupEnd()
}


async function loadPlayerHistory () {
  try {
    const response = await api.get(
      `/api/player/${encodeURIComponent(playerName.value)}/history`,
      { params: { no_cache: 1 } }
    )

    const rawHistory =
      response?.data?.data?.history ??
      response?.data?.history ??
      []

    const normalized = (Array.isArray(rawHistory) ? rawHistory : [])
      .map((r) => {
        const date = (r?.date ?? r?.dump_date ?? r?.dumpDate ?? '').toString()
        return {
          ...r,
          date // <-- guarantees the field your frontend expects
        }
      })
      // Optional safety: drop broken rows (prevents chart issues)
      .filter(r => (r.date || '').trim().length > 0)

    playerHistory.value = normalized
    debugHistoryData(playerHistory.value)
  } catch (err) {
    console.error('Error loading player history:', err)
    playerHistory.value = []
    $q.notify({
      type: 'negative',
      message: 'Failed to load player history',
      timeout: 3000
    })
  }
}




async function loadAll() {
  console.log('loadAll called for player:', playerName.value);
  
  // Validate player name before making any API calls
  if (!playerName.value) {
    error.value = 'No player name provided.'
    console.error('No player name provided');
    return false;
  }
  
  // Load player history
  await loadPlayerHistory()

  try {
    let playerTribe = null
    
    // Try to get player info to determine tribe
    try {
      console.log('Fetching players list...');
      const playersResponse = await api.get('/api/players');
      console.log('Players list response:', playersResponse);
      
      const player = playersResponse.data?.find(p => p.name === playerName.value);
      
      if (player) {
        console.log('Found player in players list:', player);
        window.debugPlayer = player;
        playerTribe = player.tribe_id || player.tribeId || player.tribe || null;
        console.log('Player tribe:', playerTribe);
      } else {
        console.warn('Player not found in players list');
      }
    } catch (e) {
      console.warn('Could not fetch players list:', e);
    }
    
    // Fetch villages for the player
    try {
      console.log(`Fetching villages for player: ${playerName.value}`);
      const response = await api.get(`/api/player/${encodeURIComponent(playerName.value)}/villages`);
      console.log('Villages API response:', response);
      
      const villagesData = response.data?.villages || [];
      console.log('Villages data:', villagesData);
      
      if (!villagesData.length) {
        console.warn('No villages data received or empty array');
        error.value = 'No villages found for this player.';
        return false;
      }
      
      window.debugVillage = () => villagesData[0];
      
      // Process villages data
      villages.value = villagesData.map(r => {
        console.log('Processing village:', r);
        const villageTribe = r.tribe_id || r.tribeId || r.tribe || 'Unknown';
        
        return {
          village:       r.village_name || r.name || 'Unnamed Village',
          coords:        `(${r.x},${r.y})`,
          x:             Number(r.x) || 0,
          y:             Number(r.y) || 0,
          population:    Number(r.population || 0),
          victoryPoints: Number(r.victory_points || r.victoryPoints || 0),
          alliance:      r.alliance_tag || r.alliance || '',
          region:        r.region || '',
          tribe:         playerTribe ? mapTribe(playerTribe) : mapTribe(villageTribe),
          player:        r.player_name || r.playerName || playerName.value,
          player_id:     r.player_id || r.playerId || null
        };
      });
      
      console.log('Processed villages:', villages.value);
      
      playerId.value = villages.value[0]?.player_id || null;
      console.log('Set playerId:', playerId.value);
      
      return true;
      
    } catch (e) {
      console.error('Error fetching villages:', e);
      error.value = `Failed to load villages for "${playerName.value}".`;
      return false;
    }
    
  } catch (e) {
    console.error('Error in loadAll:', e);
    error.value = `Failed to load data for "${playerName.value}".`;
    return false;
  }
}

/* zoom init + resize */
/* zoom init + resize */
let zoomInited = false
let roMap = null

function ensureZoom () {
  if (zoomInited) return
  if (!svg.value || !viewportEl.value) return

  // Helper: keep zoom extents in sync with container size + world bounds
  const updateZoomExtents = () => {
    const r = getContainerRect()
    if (!r) return

    // extent = screen-space (px) box the zoom uses as its viewport
    zoom.extent([[0, 0], [r.width, r.height]])

    // translateExtent = world-space bounds (your viewBox / map units)
    // This prevents panning outside WORLD without custom snap/clamp fights.
    zoom.translateExtent([[WORLD.x0, WORLD.y0], [WORLD.x1, WORLD.y1]])
  }

  // Create d3 zoom behavior with panning disabled
  zoom = d3.zoom()
    .scaleExtent([0.1, 50])
    .filter((event) => {
      // Only allow wheel events for zooming, disable all other interactions
      if (event.type === 'wheel') return true;
      return false;
    })
    .on('zoom', (event) => {
      const { transform } = event;
      const rect = getContainerRect();
      
      if (!rect) return;
      
      // Calculate center of the container
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      
      // Create a transform that only applies zoom (keeps the center fixed)
      const newTransform = d3.zoomIdentity
        .translate(centerX, centerY)
        .scale(transform.k)
        .translate(-centerX / transform.k, -centerY / transform.k);
      
      // Apply the transform to the viewport
      d3.select(viewportEl.value).attr('transform', newTransform);
      
      // Update UI state
      zoomK.value = transform.k;
      updateLabels();
    })

  // Get container dimensions
  const containerRect = getContainerRect();
  
  // Apply zoom to SVG with proper constraints
  const zoomSelection = d3.select(svg.value)
    .call(zoom)
    .on('dblclick.zoom', null); // redundant with filter, but harmless
    
  // Only apply initial transform if we have container dimensions
  if (containerRect) {
    // Store the initial transform
    const initialTransform = d3.zoomIdentity
      .translate(containerRect.width / 2, containerRect.height / 2)
      .scale(0.5);
    
    // Apply the initial transform
    zoomSelection.call(zoom.transform, initialTransform);
    
    // Also apply it directly to the viewport to prevent any flicker
    d3.select(viewportEl.value).attr('transform', initialTransform);
  }

  // Handle wheel events for smooth zooming centered on the viewport
  if (mapAreaEl.value) {
    mapAreaEl.value.addEventListener(
      'wheel',
      (e) => {
        // Only prevent default if not holding ctrl (to allow page zoom with ctrl+wheel)
        if (!e.ctrlKey) {
          e.preventDefault();
          
          // Calculate zoom factor based on wheel delta
          const delta = -e.deltaY * (e.deltaMode === 1 ? 0.05 : e.deltaMode ? 1 : 0.002);
          const zoomFactor = Math.exp(delta);
          
          // Get current transform
          const t = d3.zoomTransform(svg.value);
          
          // Calculate new scale with bounds checking
          const newK = Math.max(0.1, Math.min(50, t.k * zoomFactor));
          
          // Only update if scale changed
          if (newK !== t.k) {
            // Get container dimensions
            const rect = getContainerRect();
            if (!rect) return;
            
            // Calculate center of the container
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            // Create a new transform that keeps the center point fixed
            const newTransform = d3.zoomIdentity
              .translate(centerX, centerY)
              .scale(newK)
              .translate(-centerX / newK, -centerY / newK);
            
            // Apply the new transform
            d3.select(svg.value).call(zoom.transform, newTransform);
          }
        }
      },
      { passive: false }
    );
  }

  // ResizeObserver: update extents & labels on size change
  roMap = new ResizeObserver(async () => {
    await raf2()
    updateZoomExtents()
    updateLabels()
  })

  if (mapAreaEl.value) roMap.observe(mapAreaEl.value)

  // Initialize extents once
  updateZoomExtents()
  updateLabels()

  zoomInited = true
}


/* CSV download */
function downloadCsv() {
  if (!villages.value.length) return
  const headers = ['Village','Coords','Population','VP','Alliance','Region','Tribe']
  const lines = [headers.join(',')]
  for (const r of villages.value) {
    const row = [
      r.village ?? '',
      r.coords ?? '',
      r.population ?? 0,
      r.victoryPoints ?? 0,
      r.alliance ?? '',
      r.region ?? '',
      r.tribe ?? ''
    ].map(v => `"${String(v).replace(/"/g,'""')}"`)
    lines.push(row.join(','))
  }
  const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `player_${playerName.value}_villages.csv`
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

/* lifecycle */
// Add resetViewNoAnimation function
function resetViewNoAnimation() {
  const rect = getContainerRect()
  if (!rect) return
  
  // Calculate the scale to fit the world view
  const worldWidth = WORLD.x1 - WORLD.x0
  const worldHeight = WORLD.y1 - WORLD.y0
  const scaleX = rect.width / (worldWidth * 1.1)
  const scaleY = rect.height / (worldHeight * 1.1)
  const scale = Math.min(scaleX, scaleY, 1)
  
  // Center the view
  const tx = (rect.width - worldWidth * scale) / 2 - WORLD.x0 * scale
  const ty = (rect.height - worldHeight * scale) / 2 - WORLD.y0 * scale
  
  // Apply transform immediately without animation
  suppressSnap = true
  const transform = d3.zoomIdentity
    .translate(tx, ty)
    .scale(scale)
  
  d3.select(svg.value)
    .call(zoom.transform, transform)
  
  // Update labels immediately
  updateLabels()
  suppressSnap = false
}

onMounted(async () => {
  try {
    console.log('Component mounted, initializing...');
    console.log('Player name:', playerName.value);
    
    // First, ensure the container is properly sized
    await nextTick();
    console.log('Container should be ready');
    
    // Initialize zoom first to set up the behavior
    ensureZoom();
    console.log('Zoom behavior initialized');
    
    // Load data
    console.log('Loading data...');
    const loadSuccess = await loadAll();
    console.log('Data loaded, success:', loadSuccess);
    
    await nextTick();
    console.log('Villages after load:', villages.value);
    
    if (villages.value.length > 0) {
      // Draw markers
      console.log('Drawing markers...');
      drawMarkers();
      
      // Set initial zoom level (centered at 0,0)
      console.log('Setting initial zoom level');
      const scale = 0.5;
      
      // Apply the transform through D3 zoom to ensure consistency
      const transform = d3.zoomIdentity
        .translate(0, 0) // Keep centered at origin
        .scale(scale);
      
      d3.select(svg.value)
        .call(zoom.transform, transform);
      
      // Update labels
      updateLabels();
    }
  } catch (error) {
    console.error('Error during initialization:', error)
  }
})

onBeforeUnmount(() => { 
  if (roMap && mapAreaEl.value) roMap.unobserve(mapAreaEl.value) 
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.player-detail-page {
  min-height: 100%;
  background-color: #f5f5f5;
}

.content-wrap {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
  max-width: 100%;
  overflow: hidden;
}

.map-card {
  flex: 0 0 auto;
  height: 60vh;
  min-height: 400px;
  display: flex;
  flex-direction: column;
  position: relative;
}

.tab-panels-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.map-tab-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.map-controls {
  background: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
}

.charts-tab-panel {
  height: 100%;
  overflow-y: auto;
}

.map-area {
  flex: 1;
  position: relative;
  overflow: hidden;
  background: #1a1a1a;
}

.map-svg {
  width: 100%;
  height: 100%;
  touch-action: none;
}

.coord-label {
  fill: rgba(255, 255, 255, 0.7);
  font-size: 10px;
  font-family: monospace;
  pointer-events: none;
  user-select: none;
  text-shadow: 0 0 2px #000, 0 0 2px #000, 0 0 2px #000;
}

.tooltip {
  position: absolute;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 0.5rem;
  border-radius: 4px;
  pointer-events: none;
  z-index: 1000;
  font-size: 12px;
  line-height: 1.4;
  max-width: 240px;
}

.marker {
  cursor: pointer;
  transition: all 0.2s ease;
  pointer-events: all;
  
  &.highlighted {
    stroke: #ffeb3b !important;
    stroke-width: 0.2 !important;
    filter: drop-shadow(0 0 3px rgba(255, 235, 59, 0.8));
    animation: pulse 1.5s infinite;
  }
  
  @keyframes pulse {
    0% { filter: drop-shadow(0 0 2px rgba(255, 235, 59, 0.8)); }
    50% { filter: drop-shadow(0 0 5px rgba(255, 235, 59, 1)); }
    100% { filter: drop-shadow(0 0 2px rgba(255, 235, 59, 0.8)); }
  }
}

.statusbar {
  background: #f0f0f0;
  border-top: 1px solid #e0e0e0;
  font-size: 0.8rem;
  color: #666;
}

/* Context Menu Styles */
.context-menu {
  z-index: 7000;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  border-radius: 4px;
}

.context-menu :deep(.q-item) {
  min-height: 36px;
  padding: 8px 16px;
  font-size: 0.9rem;
}

.context-menu :deep(.q-item__section--avatar) {
  min-width: 32px;
  color: #1976d2;
}

.context-menu :deep(.q-item__label) {
  font-size: 0.9em;
  font-weight: 500;
  color: #333;
}

.context-menu :deep(.q-item.q-item--clickable:hover) {
  background: #f0f7ff;
}

.context-menu :deep(.q-item.q-item--active) {
  color: #1976d2;
  background: #e3f2fd;
}

.context-menu :deep(.q-item.q-item--dense) {
  min-height: 32px;
  padding: 4px 16px;
}

.context-menu :deep(.q-item__label--header) {
  color: #666;
  font-weight: 600;
  font-size: 0.8em;
  padding: 8px 16px 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.context-menu :deep(.q-separator) {
  margin: 4px 0;
}

:deep(.q-table) {
  table-layout: fixed;
}

:deep(.q-table th) {
  font-weight: 600;
  background: #f5f5f5;
}

:deep(.q-table tbody tr) {
  cursor: pointer;
}

:deep(.q-table tbody tr:hover) {
  background: #f0f7ff;
}

:deep(.q-table td) {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

:deep(.q-table th:first-child),
:deep(.q-table td:first-child) {
  padding-left: 16px;
}

:deep(.q-table th:last-child),
:deep(.q-table td:last-child) {
  padding-right: 16px;
}

:deep(.q-table--dense .q-table th),
:deep(.q-table--dense .q-table td) {
  padding: 4px 8px;
}
</style>
