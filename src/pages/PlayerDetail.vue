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
          dense flat round icon="open_in_new"
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
      <!-- Map -->
      <q-card flat bordered class="map-card q-mb-lg">
        <q-card-section class="row items-center q-gutter-sm">
          <div class="text-subtitle2">Villages map</div>
          <q-space />
          <q-btn flat dense icon="center_focus_strong" @click="fitToContent">
            <q-tooltip>Fit to player villages</q-tooltip>
          </q-btn>
          <q-btn flat dense icon="refresh" @click="resetView">
            <q-tooltip>Reset view</q-tooltip>
          </q-btn>
        </q-card-section>

        <div class="map-area" ref="mapAreaEl" @contextmenu.capture="onContextMenu">
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
                x="-200" y="-200" width="400" height="400"
                :href="bgUrl" :xlink:href="bgUrl"
                preserveAspectRatio="none" opacity="0.65"
              />
              <!-- grid & axes -->
              <rect x="-200" y="-200" width="400" height="400" fill="url(#grid10)"/>
              <line x1="-200" y1="0" x2="200" y2="0" stroke="#9e9e9e" stroke-width="1.2" vector-effect="non-scaling-stroke" />
              <line x1="0"   y1="-200" x2="0"   y2="200" stroke="#9e9e9e" stroke-width="1.2" vector-effect="non-scaling-stroke" />
              <rect x="-200" y="-200" width="400" height="400" fill="none" stroke="#00e5ff" stroke-width="1.2" opacity="0.25" vector-effect="non-scaling-stroke" />

              <!-- markers -->
              <g ref="markersGroup" id="markersLayer"></g>

              <!-- hover highlight -->
              <g id="overlayLayer">
                <circle v-if="selection" :cx="selection.x" :cy="selection.y" :r="2.4"
                        fill="none" stroke="#00e5ff" stroke-width="0.8" vector-effect="non-scaling-stroke" />
                <circle v-if="selection" :cx="selection.x" :cy="selection.y" :r="0.9"
                        fill="#00e5ff" opacity="0.85" />
              </g>

              <circle cx="0" cy="0" r="0.9" fill="#ff5252" opacity="0.9" />
            </g>

            <!-- screen-fixed coord labels -->
            <g>
              <text ref="labelLeft"   text-anchor="end"    alignment-baseline="middle" class="coord-label"/>
              <text ref="labelRight"  text-anchor="start"  alignment-baseline="middle" class="coord-label"/>
              <text ref="labelTop"    text-anchor="middle" alignment-baseline="hanging" class="coord-label"/>
              <text ref="labelBottom" text-anchor="middle" alignment-baseline="baseline" class="coord-label"/>
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
          <div class="col text-caption">Cursor: X {{ cursor.x.toFixed(0) }} / Y {{ cursor.y.toFixed(0) }}</div>
          <div class="col text-caption text-right">Zoom: {{ zoomK.toFixed(2) }}×</div>
        </div>

        <!-- Right-click -->
        <q-menu context-menu touch-position>
          <q-list style="min-width: 220px">
            <q-item-label header>Map</q-item-label>
            <q-item clickable :disable="!ctx.hasMarker" v-close-popup @click="centerOnContext">
              <q-item-section avatar><q-icon name="center_focus_strong" /></q-item-section>
              <q-item-section>Center on this village</q-item-section>
            </q-item>
          </q-list>
        </q-menu>
      </q-card>

      <!-- Villages table -->
      <q-card flat bordered>
        <q-card-section class="row items-center q-gutter-sm">
          <q-input
            v-model="filter"
            dense outlined clearable debounce="150"
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
          flat bordered separator="cell"
          :pagination="pagination"
          :rows-per-page-options="[10,20,50,0]"
          :filter="filter"
          dense
          wrap-cells
          @row-click="(_, row) => centerFromCoords(row.coords)"
        >
          <template #body-cell-coords="props">
            <q-td :props="props">
              <a
                :href="makeMapLink(props.row.coords)"
                target="_blank" rel="noopener"
                @mouseenter="hoverCoords(props.row.coords)"
                @mouseleave="selection = null"
                @click.stop
              >{{ props.row.coords }}</a>
            </q-td>
          </template>

          <template #body-cell-alliance="props">
            <q-td :props="props">
              <RouterLink
                v-if="props.row.alliance"
                :to="{ name:'alliance-detail', params:{ tag: props.row.alliance } }"
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
  </q-page>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick, watch, onBeforeUnmount } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import * as d3 from 'd3'
import { api } from 'boot/axios'
import bgUrl from 'assets/background.png'

/* routing */
const route   = useRoute()
const router  = useRouter()
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

/* tribe mapping */
const TRIBE_MAP = {
  1:'Romans', 2:'Teutons', 3:'Gauls', 4:'Nature',
  5:'Natars', 6:'Egyptians', 7:'Huns', 8:'Spartans', 9:'Vikings'
}
function mapTribe(t) {
  if (t == null) return 'Unknown'
  const n = Number(t)
  if (Number.isFinite(n) && TRIBE_MAP[n]) return TRIBE_MAP[n]
  const s = String(t).trim()
  return TRIBE_MAP[s] || s || 'Unknown'
}

/* table data */
const villages   = ref([])
const filter     = ref('')
const pagination = ref({ page:1, rowsPerPage:10 })
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
function toMapCoords (evt) {
  const [sx, sy] = d3.pointer(evt, svg.value)
  const t = d3.zoomTransform(svg.value)
  return { x: t.invertX(sx), y: t.invertY(sy) }
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

function centerAt (x, y, k = d3.zoomTransform(svg.value).k || 1) {
  const rect = getContainerRect()
  if (!rect || !Number.isFinite(x) || !Number.isFinite(y)) return
  k = Number.isFinite(k) && k > 0 ? k : 1
  const tx = rect.width  / 2 - k * x
  const ty = rect.height / 2 - k * y
  suppressSnap = true
  d3.select(svg.value).transition().duration(200)
    .call(zoom.transform, d3.zoomIdentity.translate(tx, ty).scale(k))
    .on('end', () => { suppressSnap = false })
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
function fitToContent () {
  const rect = getContainerRect()
  if (!rect) return
  const bbox = villagesBBox()
  const pad = 1.06
  const k = Math.max(0.5, Math.min(rect.width / (bbox.width * pad), rect.height / (bbox.height * pad)))
  const cx = bbox.x + bbox.width / 2
  const cy = bbox.y + bbox.height / 2
  centerAt(cx, cy, k)
}
function resetView () { centerAt(0, 0, 1) }

/* pointer + context (throttled UI updates) */
let cursorTick = 0
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

function onContextMenu (e) {
  const el = e.target.closest('.marker')
  ctx.hasMarker = !!el
  if (el) {
    const bb = el.getBBox()
    ctx.point = { x: bb.x + bb.width / 2, y: bb.y + bb.height / 2 }
  } else {
    ctx.point = toMapCoords(e)
  }
}
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
      const tip = `Village: ${d.village}<br>Player: ${d.player}<br>Population: ${d.population.toLocaleString()}<br>Alliance: ${d.alliance}<br>Tribe: ${d.tribe}`
      tooltip.value = { show:true, x:e.clientX+8, y:e.clientY+8, content: sanitizeTooltip(tip) }
      ctx.hasMarker = true
    })
    .on('pointerout', () => hideTooltip())
}

/* data loading */
const error   = ref(null)
function resetState() {
  error.value = null
  villages.value = []
  playerId.value = null
  selection.value = null
}

const raf2 = () => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))

async function loadAll() {
  try {
    const { data } = await api.get(`/api/player/${encodeURIComponent(playerName.value)}/villages`)
    villages.value = (data.villages || []).map(r => ({
      village:       r.village_name,
      coords:        `(${r.x},${r.y})`,
      x:             r.x,
      y:             r.y,
      population:    Number(r.population || 0),
      victoryPoints: Number(r.victory_points || 0),
      alliance:      r.alliance_tag || '',
      region:        r.region || '',
      tribe:         mapTribe(r.tribe),
      player:        r.player_name || '',
      player_id:     r.player_id || r.playerId || null
    }))
    playerId.value = villages.value[0]?.player_id || null

    await nextTick()
    await raf2()        // allow layout to settle
    ensureZoom()
    drawMarkers()
    fitToContent()
    updateLabels()
  } catch (e) {
    console.error(e)
    error.value = `Failed to load data for “${playerName.value}”.`
  }
}

/* zoom init + resize */
let zoomInited = false
let roMap = null
let zoomTick = 0
function ensureZoom() {
  if (zoomInited) return
  zoom = d3.zoom()
    .scaleExtent([0.5, 50])
    .extent(() => {
      const r = getContainerRect()
      return r ? [[0, 0], [r.width, r.height]] : [[0, 0], [1000, 1000]]
    })
    .on('zoom', ({ transform }) => {
      d3.select(viewportEl.value).attr('transform', transform)
      // throttle zoom readout to keep UI snappy
      const now = performance.now()
      if (now - zoomTick > 80) {
        zoomTick = now
        zoomK.value = transform.k
        updateLabels()
      }
    })
    .on('end', () => snapBack())
  d3.select(svg.value).call(zoom)

  // ResizeObserver: update extents & labels (no auto-fit to avoid loops)
  roMap = new ResizeObserver(async () => {
    await raf2()
    d3.select(svg.value).call(zoom.extent(() => {
      const r = getContainerRect()
      return r ? [[0, 0], [r.width, r.height]] : [[0, 0], [1000, 1000]]
    }))
    updateLabels()
  })
  if (mapAreaEl.value) roMap.observe(mapAreaEl.value)

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
onMounted(loadAll)
onBeforeUnmount(() => { if (roMap && mapAreaEl.value) roMap.unobserve(mapAreaEl.value) })
</script>

<style scoped>
.player-detail-page { background: #0d0d0d; }
.content-wrap       { max-width: 1400px; margin: 0 auto; }

.map-card { background: #0d0d0d; }
.map-area {
  position: relative;
  height: 360px;
  min-height: 240px;
  background: #000;
  border-top: 1px solid #1f1f1f;
}
.map-area > .map-svg {
  position: absolute; inset: 0; width: 100%; height: 100%; background: #000;
  will-change: transform;
}

/* Markers: exact 1×1, crisp */
.map-area :deep(#markersLayer .marker) {
  vector-effect: non-scaling-stroke;
  image-rendering: pixelated;
}

/* Labels */
.coord-label { fill: #bbb; font-size: 11px; user-select: none; pointer-events: none; }

/* Tooltip */
.tooltip {
  position: fixed; pointer-events: none; background: rgba(0,0,0,0.9); color: #fff;
  padding: 6px 8px; border-radius: 4px; font-size: .8rem; white-space: nowrap; z-index: 1000;
  border: 1px solid rgba(255,255,255,0.08);
}

/* Statusbar */
.statusbar { height: 28px; border-top: 1px solid #1f1f1f; background: #0d0d0d; color: #ddd; }
</style>
