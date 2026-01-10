<template>
  <q-page class="trade-page">
    <q-splitter
      v-if="$q.screen.gt.sm"
      v-model="splitter"
      unit="px"
      :limits="[320, 560]"
      class="trade-splitter"
    >
      <!-- LEFT -->
      <template #before>
        <aside class="side">
          <div class="side__titlebar">
            <div class="side__title">
              <q-icon name="swap_horiz" class="q-mr-sm" />
              Trade Route Simulator
            </div>

            <q-space />

            <q-chip dense square :color="loaded ? 'positive' : 'grey-7'" text-color="white">
              {{ loaded ? 'loaded' : 'not loaded' }}
            </q-chip>
          </div>

          <q-tabs
            v-model="tab"
            dense
            inline-label
            outside-arrows
            mobile-arrows
            class="side__tabs"
            active-color="primary"
            indicator-color="primary"
          >
            <q-tab name="scope" icon="public" label="Data scope" />
            <q-tab name="sim" icon="route" label="Simulation" />
            <q-tab name="display" icon="tune" label="Display" />
          </q-tabs>

          <q-separator />

          <q-tab-panels v-model="tab" animated class="side__panels">
            <!-- SCOPE -->
            <q-tab-panel name="scope" class="q-pa-md">
              <q-card flat bordered class="panel-card">
                <q-card-section class="panel-card__head">
                  <div class="text-subtitle2">Load villages</div>
                  <q-space />
                  <q-btn dense flat icon="delete_sweep" @click="clearAll">
                    <q-tooltip>Clear</q-tooltip>
                  </q-btn>
                </q-card-section>

                <q-separator />

                <q-card-section class="q-gutter-md">
                  <div class="row q-col-gutter-sm">
                    <div class="col-12">
                      <q-select
                        v-model="scopeMode"
                        dense
                        filled
                        emit-value
                        map-options
                        :options="scopeModeOptions"
                        label="Mode"
                        hint="World loads the latest dump; filters are applied server-side where possible."
                      />
                    </div>

                    <div class="col-12" v-if="scopeMode === 'alliances'">
                      <q-select
                        v-model="selectedAlliances"
                        dense
                        filled
                        multiple
                        use-input
                        clearable
                        input-debounce="150"
                        option-label="label"
                        option-value="value"
                        :options="allianceOptionsFiltered"
                        label="Alliances"
                        hint="Pick one or more alliances to load only their villages."
                        @filter="filterAllianceOptions"
                      />
                    </div>

                    <div class="col-12" v-if="scopeMode === 'players'">
                      <q-select
                        v-model="selectedPlayers"
                        dense
                        filled
                        multiple
                        use-input
                        clearable
                        input-debounce="150"
                        option-label="label"
                        option-value="value"
                        :options="playerOptionsFiltered"
                        label="Players"
                        hint="Pick one or more players to load only their villages."
                        @filter="filterPlayerOptions"
                      />
                    </div>

                    <div class="col-12" v-if="scopeMode === 'region'">
                      <q-input
                        v-model="regionName"
                        dense
                        filled
                        label="Region"
                        hint="Uses the backend region matcher (same as your existing /api/region/<name>/villages route)."
                      />
                    </div>

                    <div class="col-12">
                      <q-slider
                        v-model="maxVillages"
                        :min="200"
                        :max="20000"
                        :step="100"
                        label
                        label-always
                        dense
                      />
                      <div class="text-caption text-grey-5">
                        Max villages to request: <b>{{ maxVillages.toLocaleString() }}</b>
                        <span class="q-ml-sm">·</span>
                        <span class="q-ml-sm">If the backend supports limit, it’s applied there; otherwise we downsample client-side.</span>
                      </div>
                    </div>

                    <div class="col-12">
                      <q-toggle v-model="dimInactive" dense label="Dim inactive (non-selected) villages" />
                    </div>

                    <div class="col-12">
                      <div class="row q-col-gutter-sm">
                        <div class="col">
                          <q-btn
                            color="primary"
                            class="full-width"
                            icon="cloud_download"
                            label="Load"
                            :loading="loading"
                            @click="loadVillages"
                          />
                        </div>
                        <div class="col">
                          <q-btn
                            outline
                            color="grey-4"
                            text-color="white"
                            class="full-width"
                            icon="center_focus_strong"
                            label="Fit"
                            :disable="!villages.length"
                            @click="fitToVillages"
                          />
                        </div>
                      </div>
                    </div>

                    <div class="col-12">
                      <q-banner v-if="loadError" rounded class="bg-negative text-white">
                        <div class="text-weight-bold">Load failed</div>
                        <div class="text-body2">{{ loadError }}</div>
                      </q-banner>

                      <q-banner v-else-if="!backendSupportsWorld" rounded class="bg-warning text-black">
                        <div class="text-weight-bold">Backend missing world endpoint</div>
                        <div class="text-body2">
                          This page expects either:
                          <b>/api/villages/latest</b> (recommended) or your existing per-scope routes.
                          If you only have per-scope routes, load by alliance/player/region.
                        </div>
                      </q-banner>
                    </div>
                  </div>
                </q-card-section>
              </q-card>

              <q-card flat bordered class="panel-card q-mt-md">
                <q-card-section class="panel-card__head">
                  <div class="text-subtitle2">Search & select villages</div>
                  <q-space />
                  <q-chip dense square color="grey-8" text-color="white">
                    {{ selectedVillageIds.size }} / {{ villages.length }} selected
                  </q-chip>
                </q-card-section>

                <q-separator />

                <q-card-section class="q-gutter-sm">
                  <q-input
                    v-model="villageSearch"
                    dense
                    filled
                    clearable
                    placeholder="Search by village / player / alliance…"
                  >
                    <template #prepend><q-icon name="search" /></template>
                  </q-input>

                  <div class="row q-col-gutter-sm">
                    <div class="col">
                      <q-btn
                        dense
                        outline
                        class="full-width"
                        icon="select_all"
                        label="Select visible"
                        :disable="!villages.length"
                        @click="selectVisibleVillages"
                      />
                    </div>
                    <div class="col">
                      <q-btn
                        dense
                        outline
                        class="full-width"
                        icon="deselect"
                        label="Clear selection"
                        :disable="!selectedVillageIds.size"
                        @click="selectedVillageIds.clear()"
                      />
                    </div>
                  </div>

                  <div class="vlist">
                    <div
                      v-for="v in visibleVillagesLimited"
                      :key="v.id"
                      class="vrow"
                      :class="{ 'is-selected': selectedVillageIds.has(v.id) }"
                      @click="toggleVillageSelected(v.id)"
                    >
                      <div class="vrow__main">
                        <div class="vrow__name">{{ v.name }}</div>
                        <div class="vrow__meta">
                          <span>{{ v.x }}|{{ v.y }}</span>
                          <span class="dot">·</span>
                          <span>{{ v.player || '—' }}</span>
                          <span class="dot">·</span>
                          <span>{{ v.alliance || '—' }}</span>
                        </div>
                      </div>

                      <q-btn
                        dense
                        flat
                        round
                        icon="center_focus_strong"
                        @click.stop="centerOnVillage(v)"
                      >
                        <q-tooltip>Center</q-tooltip>
                      </q-btn>
                    </div>

                    <div v-if="visibleVillages.length > visibleVillagesLimited.length" class="vlist__more">
                      Showing {{ visibleVillagesLimited.length }} / {{ visibleVillages.length }} (narrow your search).
                    </div>
                  </div>
                </q-card-section>
              </q-card>
            </q-tab-panel>

            <!-- SIM -->
            <q-tab-panel name="sim" class="q-pa-md">
              <q-card flat bordered class="panel-card">
                <q-card-section class="panel-card__head">
                  <div class="text-subtitle2">Simulation</div>
                  <q-space />
                  <q-chip dense square color="grey-8" text-color="white">
                    t={{ formatClock(simClockSeconds) }}
                  </q-chip>
                </q-card-section>

                <q-separator />

                <q-card-section class="q-gutter-md">
                  <q-select
                    v-model="clockMode"
                    dense
                    filled
                    emit-value
                    map-options
                    :options="clockModeOptions"
                    label="Clock mode"
                  />

                  <div class="row items-center q-gutter-sm">
                    <q-slider
                      v-model="speed"
                      :min="0"
                      :max="10"
                      :step="1"
                      label
                      label-always
                      dense
                      class="col"
                    />
                    <q-chip dense square color="grey-8" text-color="white">
                      ×{{ speed }}
                    </q-chip>
                  </div>

                  <div class="row q-col-gutter-sm">
                    <div class="col">
                      <q-btn
                        color="primary"
                        class="full-width"
                        icon="play_arrow"
                        label="Start"
                        :disable="clockMode !== 'live' || !villages.length"
                        @click="startSim"
                      />
                    </div>
                    <div class="col">
                      <q-btn
                        outline
                        class="full-width"
                        icon="pause"
                        label="Pause"
                        :disable="!simRunning"
                        @click="stopSim"
                      />
                    </div>
                  </div>

                  <q-banner rounded class="bg-grey-10 text-grey-2">
                    Pick villages on the left. This page keeps the rendering fast by drawing villages on a canvas and
                    only updating on animation frames.
                  </q-banner>
                </q-card-section>
              </q-card>
            </q-tab-panel>

            <!-- DISPLAY -->
            <q-tab-panel name="display" class="q-pa-md">
              <q-card flat bordered class="panel-card">
                <q-card-section class="panel-card__head">
                  <div class="text-subtitle2">Display</div>
                </q-card-section>

                <q-separator />

                <q-card-section class="q-gutter-md">
                  <q-toggle v-model="showGrid" dense label="Grid" />
                  <q-toggle v-model="showAxes" dense label="Axes" />
                  <q-toggle v-model="showLabels" dense label="Labels (selected only)" />
                  <q-toggle v-model="showRings" dense label="Rings (selected only)" />

                  <q-slider
                    v-model="pointSize"
                    :min="1"
                    :max="6"
                    :step="1"
                    dense
                    label
                    label-always
                  />

                  <q-slider
                    v-model="inactiveAlpha"
                    :min="0.05"
                    :max="1"
                    :step="0.05"
                    dense
                    label
                    label-always
                  >
                    <template #label>
                      Inactive alpha: {{ inactiveAlpha.toFixed(2) }}
                    </template>
                  </q-slider>
                </q-card-section>
              </q-card>
            </q-tab-panel>
          </q-tab-panels>
        </aside>
      </template>

      <!-- RIGHT -->
      <template #after>
        <section class="stage">
          <!-- TOP HUD (replicates global map feel) -->
          <div class="hud">
            <div class="hud__row">
              <q-btn dense flat round icon="home" @click="fitToVillages">
                <q-tooltip>Fit</q-tooltip>
              </q-btn>

              <q-btn dense flat round icon="refresh" @click="resetView">
                <q-tooltip>Reset view</q-tooltip>
              </q-btn>

              <q-space />

              <div class="hud__coords">
                Cursor: <b>{{ Math.round(cursor.x) }}|{{ Math.round(cursor.y) }}</b>
                <span class="dot">·</span>
                Zoom: <b>{{ Math.round(zoomK * 100) }}%</b>
              </div>

              <q-space />

              <div class="hud__zoom">
                <q-btn dense flat round icon="remove" @click="zoomBy(0.8)">
                  <q-tooltip>Zoom out</q-tooltip>
                </q-btn>

                <q-slider
                  v-model="zoomSlider"
                  dense
                  :min="Math.round(MIN_ZOOM * 100)"
                  :max="500"
                  :step="1"
                  class="hud__slider"
                  @change="applyZoomSlider"
                />

                <div class="hud__zoomtxt">{{ zoomSlider }}%</div>

                <q-btn dense flat round icon="add" @click="zoomBy(1.25)">
                  <q-tooltip>Zoom in</q-tooltip>
                </q-btn>
              </div>

              <q-toggle v-model="showRings" dense label="Rings" class="q-ml-sm" />
            </div>
          </div>

          <!-- CANVAS LAYERS -->
          <div class="canvas-wrap" ref="wrapEl">
            <canvas ref="bgCanvas" class="layer" />
            <canvas ref="fgCanvas" class="layer" />
            <!-- tiny svg overlay just for labels/rings (optional) -->
            <svg ref="overlaySvg" class="overlay" @pointermove="onPointerMove" @pointerleave="onPointerLeave">
              <g :transform="overlayTransform">
                <template v-if="showRings">
                  <circle
                    v-for="id in Array.from(selectedVillageIds)"
                    :key="'r' + id"
                    :cx="byId.get(id)?.x ?? 0"
                    :cy="byId.get(id)?.y ?? 0"
                    :r="10"
                    class="ring"
                  />
                </template>

                <template v-if="showLabels">
                  <text
                    v-for="id in Array.from(selectedVillageIds)"
                    :key="'t' + id"
                    :x="(byId.get(id)?.x ?? 0) + 2"
                    :y="(byId.get(id)?.y ?? 0) - 2"
                    class="label"
                  >
                    {{ byId.get(id)?.name }}
                  </text>
                </template>
              </g>
            </svg>

            <q-inner-loading :showing="loading">
              <q-spinner color="primary" size="2em" />
            </q-inner-loading>

            <div v-if="hoverTip.show" class="tip" :style="{ left: hoverTip.x + 'px', top: hoverTip.y + 'px' }">
              <div class="tip__name">{{ hoverTip.v?.name }}</div>
              <div class="tip__meta">
                {{ hoverTip.v?.x }}|{{ hoverTip.v?.y }}
                <span class="dot">·</span>
                {{ hoverTip.v?.player || '—' }}
                <span class="dot">·</span>
                {{ hoverTip.v?.alliance || '—' }}
              </div>
            </div>
          </div>
        </section>
      </template>
    </q-splitter>

    <!-- MOBILE: stack -->
    <div v-else class="mobile">
      <div class="q-pa-md">
        <q-banner rounded class="bg-grey-10 text-grey-2">
          This page is optimized for desktop (split view). On mobile, use the Data scope tab to load villages and then
          pan/zoom on the map.
        </q-banner>
      </div>
      <div class="q-pa-md">
        <q-btn color="primary" icon="cloud_download" label="Load" class="full-width" :loading="loading" @click="loadVillages" />
      </div>
      <div class="mobile__map">
        <div class="canvas-wrap" ref="wrapEl">
          <canvas ref="bgCanvas" class="layer" />
          <canvas ref="fgCanvas" class="layer" />
          <svg ref="overlaySvg" class="overlay" @pointermove="onPointerMove" @pointerleave="onPointerLeave">
            <g :transform="overlayTransform" />
          </svg>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { useQuasar } from 'quasar'
import * as d3 from 'd3'
import { api } from 'boot/axios'

/**
 * World bounds: match your global map (-200..200).
 * Canvas renderer maps world->screen using the same d3-zoom transform.
 */
const MAP_MIN = -200
const MAP_MAX = 200
const MAP_SIZE = MAP_MAX - MAP_MIN

// Zoom limits (similar feel to your global map)
const MAX_ZOOM_OUT_PERCENT = 50
const MIN_ZOOM = 1 / (MAX_ZOOM_OUT_PERCENT / 100) // ~0.558
const MAX_ZOOM = 50

const $q = useQuasar()

/* Layout */
const splitter = ref(360)
const tab = ref('scope')

/* State */
const loading = ref(false)
const loaded = ref(false)
const loadError = ref('')

/* Scope UI */
const scopeMode = ref('world') // world | alliances | players | region
const scopeModeOptions = [
  { label: 'World (latest dump)', value: 'world' },
  { label: 'Alliances', value: 'alliances' },
  { label: 'Players', value: 'players' },
  { label: 'Region', value: 'region' }
]

const selectedAlliances = ref([])
const selectedPlayers = ref([])
const regionName = ref('')
const maxVillages = ref(8000)
const dimInactive = ref(true)

/* Display */
const showGrid = ref(true)
const showAxes = ref(true)
const showLabels = ref(true)
const showRings = ref(false)
const pointSize = ref(2)
const inactiveAlpha = ref(0.25)

/* Simulation */
const clockMode = ref('live')
const clockModeOptions = [
  { label: 'Live (animated)', value: 'live' },
  { label: 'Manual (scrub)', value: 'manual' }
]
const speed = ref(1)
const simClockSeconds = ref(0)
const simRunning = ref(false)
let simTimer = null

/* Villages */
const villages = ref([]) // {id,name,x,y,player,alliance}
const byId = computed(() => new Map(villages.value.map(v => [v.id, v])))
const selectedVillageIds = reactive(new Set())

/* Search list */
const villageSearch = ref('')
const visibleVillages = computed(() => {
  const q = (villageSearch.value || '').trim().toLowerCase()
  if (!q) return villages.value
  return villages.value.filter(v => {
    return (
      String(v.name || '').toLowerCase().includes(q) ||
      String(v.player || '').toLowerCase().includes(q) ||
      String(v.alliance || '').toLowerCase().includes(q) ||
      `${v.x}|${v.y}`.includes(q)
    )
  })
})
const visibleVillagesLimited = computed(() => visibleVillages.value.slice(0, 250))

function toggleVillageSelected(id) {
  if (selectedVillageIds.has(id)) selectedVillageIds.delete(id)
  else selectedVillageIds.add(id)
  renderAll()
}
function centerOnVillage(v) {
  centerAt(v.x, v.y)
}
function selectVisibleVillages() {
  visibleVillages.value.forEach(v => selectedVillageIds.add(v.id))
  renderAll()
}

/* Alliance / Player options */
const allianceOptionsAll = ref([])
const playerOptionsAll = ref([])

const allianceOptionsFiltered = ref([])
const playerOptionsFiltered = ref([])

function filterAllianceOptions(val, update) {
  update(() => {
    const q = (val || '').toLowerCase()
    allianceOptionsFiltered.value = !q
      ? allianceOptionsAll.value
      : allianceOptionsAll.value.filter(o => o.label.toLowerCase().includes(q))
  })
}
function filterPlayerOptions(val, update) {
  update(() => {
    const q = (val || '').toLowerCase()
    playerOptionsFiltered.value = !q
      ? playerOptionsAll.value
      : playerOptionsAll.value.filter(o => o.label.toLowerCase().includes(q))
  })
}

/* Backend capability flag */
const backendSupportsWorld = ref(true)

/* Canvas + zoom */
const wrapEl = ref(null)
const bgCanvas = ref(null)
const fgCanvas = ref(null)
const overlaySvg = ref(null)

const cursor = reactive({ x: 0, y: 0 })
const hoverTip = reactive({ show: false, x: 0, y: 0, v: null })

let zoom = null
let transform = d3.zoomIdentity
const zoomK = ref(1)
const zoomSlider = ref(100)

const overlayTransform = computed(() => `translate(${transform.x},${transform.y}) scale(${transform.k})`)

let rafRender = 0
function scheduleRender() {
  cancelAnimationFrame(rafRender)
  rafRender = requestAnimationFrame(renderAll)
}

function resizeCanvases() {
  const wrap = wrapEl.value
  if (!wrap) return
  const r = wrap.getBoundingClientRect()
  const w = Math.max(1, Math.floor(r.width))
  const h = Math.max(1, Math.floor(r.height))

  for (const c of [bgCanvas.value, fgCanvas.value]) {
    if (!c) continue
    const dpr = window.devicePixelRatio || 1
    c.width = Math.floor(w * dpr)
    c.height = Math.floor(h * dpr)
    c.style.width = w + 'px'
    c.style.height = h + 'px'
    const ctx = c.getContext('2d')
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  }

  if (overlaySvg.value) {
    overlaySvg.value.setAttribute('width', String(w))
    overlaySvg.value.setAttribute('height', String(h))
    overlaySvg.value.setAttribute('viewBox', `0 0 ${w} ${h}`)
  }

  // Update zoom extent to replicate global-map feel
  if (zoom && wrapEl.value) {
    zoom.extent([[0, 0], [w, h]])
    // translateExtent in WORLD coords: stops pan jump
    zoom.translateExtent([[MAP_MIN - 30, MAP_MIN - 30], [MAP_MAX + 30, MAP_MAX + 30]])
  }

  scheduleRender()
}

function worldToScreen(x, y) {
  return {
    x: transform.applyX(x),
    y: transform.applyY(y)
  }
}

function screenToWorld(px, py) {
  return {
    x: transform.invertX(px),
    y: transform.invertY(py)
  }
}

function syncSliderFromZoom() {
  zoomSlider.value = Math.max(Math.round(MIN_ZOOM * 100), Math.min(500, Math.round(zoomK.value * 100)))
}

function applyZoomSlider() {
  if (!wrapEl.value || !zoom) return
  const k = Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, zoomSlider.value / 100))
  const r = wrapEl.value.getBoundingClientRect()
  const cx = (r.width / 2 - transform.x) / transform.k
  const cy = (r.height / 2 - transform.y) / transform.k
  centerAt(cx, cy, k)
}

function zoomBy(factor) {
  const nextK = Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, transform.k * factor))
  const wrap = wrapEl.value
  if (!wrap) return
  const r = wrap.getBoundingClientRect()
  const cx = (r.width / 2 - transform.x) / transform.k
  const cy = (r.height / 2 - transform.y) / transform.k
  centerAt(cx, cy, nextK)
}

function centerAt(x, y, k) {
  if (!wrapEl.value || !zoom) return
  const r = wrapEl.value.getBoundingClientRect()
  const kk = Number.isFinite(k) ? k : transform.k
  const tx = r.width / 2 - kk * x
  const ty = r.height / 2 - kk * y
  const t = d3.zoomIdentity.translate(tx, ty).scale(kk)

  d3.select(wrapEl.value).transition().duration(220).call(zoom.transform, t)
}

function fitToVillages() {
  if (!wrapEl.value || !zoom || !villages.value.length) return
  const r = wrapEl.value.getBoundingClientRect()
  const pad = 20

  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity
  villages.value.forEach(v => {
    minX = Math.min(minX, v.x); maxX = Math.max(maxX, v.x)
    minY = Math.min(minY, v.y); maxY = Math.max(maxY, v.y)
  })

  minX = Math.max(MAP_MIN, minX); maxX = Math.min(MAP_MAX, maxX)
  minY = Math.max(MAP_MIN, minY); maxY = Math.min(MAP_MAX, maxY)

  const wWorld = Math.max(1e-6, maxX - minX)
  const hWorld = Math.max(1e-6, maxY - minY)

  const kx = (r.width - pad * 2) / wWorld
  const ky = (r.height - pad * 2) / hWorld
  const k = Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, Math.min(kx, ky)))

  const cx = (minX + maxX) / 2
  const cy = (minY + maxY) / 2
  centerAt(cx, cy, k)
}

function resetView() {
  centerAt(0, 0, 1)
}

/* Rendering (fast) */
function renderAll() {
  renderBackground()
  renderVillages()
}

function renderBackground() {
  const c = bgCanvas.value
  if (!c) return
  const ctx = c.getContext('2d')
  const wrap = wrapEl.value
  if (!wrap) return
  const r = wrap.getBoundingClientRect()

  ctx.clearRect(0, 0, r.width, r.height)

  // Axes
  if (showAxes.value) {
    ctx.save()
    ctx.globalAlpha = 0.15
    ctx.lineWidth = 1
    ctx.beginPath()
    const p0 = worldToScreen(MAP_MIN - 1000, 0)
    const p1 = worldToScreen(MAP_MAX + 1000, 0)
    ctx.moveTo(p0.x, p0.y); ctx.lineTo(p1.x, p1.y)

    const p2 = worldToScreen(0, MAP_MIN - 1000)
    const p3 = worldToScreen(0, MAP_MAX + 1000)
    ctx.moveTo(p2.x, p2.y); ctx.lineTo(p3.x, p3.y)
    ctx.strokeStyle = '#ffffff'
    ctx.stroke()
    ctx.restore()
  }

  // Grid (world-space grid like your global map)
  if (showGrid.value) {
    ctx.save()
    ctx.globalAlpha = 0.08
    ctx.strokeStyle = '#ffffff'
    ctx.lineWidth = 1

    const step = 10
    for (let x = MAP_MIN; x <= MAP_MAX; x += step) {
      const a = worldToScreen(x, MAP_MIN)
      const b = worldToScreen(x, MAP_MAX)
      ctx.beginPath()
      ctx.moveTo(a.x, a.y)
      ctx.lineTo(b.x, b.y)
      ctx.stroke()
    }
    for (let y = MAP_MIN; y <= MAP_MAX; y += step) {
      const a = worldToScreen(MAP_MIN, y)
      const b = worldToScreen(MAP_MAX, y)
      ctx.beginPath()
      ctx.moveTo(a.x, a.y)
      ctx.lineTo(b.x, b.y)
      ctx.stroke()
    }
    ctx.restore()
  }

  // World bounds
  ctx.save()
  ctx.globalAlpha = 0.25
  ctx.strokeStyle = '#00ffff'
  ctx.setLineDash([6, 5])
  ctx.lineWidth = 2
  const tl = worldToScreen(MAP_MIN, MAP_MIN)
  const br = worldToScreen(MAP_MAX, MAP_MAX)
  ctx.strokeRect(tl.x, tl.y, br.x - tl.x, br.y - tl.y)
  ctx.restore()
}

function renderVillages() {
  const c = fgCanvas.value
  if (!c) return
  const ctx = c.getContext('2d')
  const wrap = wrapEl.value
  if (!wrap) return
  const r = wrap.getBoundingClientRect()

  ctx.clearRect(0, 0, r.width, r.height)

  // Small performance trick: avoid drawing ultra-tiny points when zoomed far out
  const base = pointSize.value
  const radius = Math.max(0.75, base * Math.max(0.7, Math.min(1.6, transform.k ** 0.15)))

  // Draw villages
  for (const v of villages.value) {
    const p = worldToScreen(v.x, v.y)
    const active = selectedVillageIds.has(v.id)
    const alpha = active ? 0.9 : (dimInactive.value ? inactiveAlpha.value : 0.9)

    ctx.globalAlpha = alpha
    ctx.beginPath()
    ctx.arc(p.x, p.y, radius, 0, Math.PI * 2)
    ctx.fillStyle = active ? '#ffd54f' : '#ffffff'
    ctx.fill()
  }

  // Highlight selection outlines
  if (selectedVillageIds.size) {
    ctx.save()
    ctx.globalAlpha = 0.9
    ctx.strokeStyle = '#ff00ff'
    ctx.lineWidth = 1.5
    for (const id of selectedVillageIds) {
      const v = byId.value.get(id)
      if (!v) continue
      const p = worldToScreen(v.x, v.y)
      ctx.beginPath()
      ctx.arc(p.x, p.y, radius + 2.5, 0, Math.PI * 2)
      ctx.stroke()
    }
    ctx.restore()
  }
}

/* Hover picking (simple nearest) */
function findNearestVillage(worldPt, maxDistWorld = 2.5) {
  let best = null
  let bestD2 = maxDistWorld * maxDistWorld
  for (const v of villages.value) {
    const dx = v.x - worldPt.x
    const dy = v.y - worldPt.y
    const d2 = dx * dx + dy * dy
    if (d2 < bestD2) {
      bestD2 = d2
      best = v
    }
  }
  return best
}

function onPointerMove(evt) {
  const wrap = wrapEl.value
  if (!wrap) return
  const r = wrap.getBoundingClientRect()
  const px = evt.clientX - r.left
  const py = evt.clientY - r.top
  const w = screenToWorld(px, py)
  cursor.x = w.x
  cursor.y = w.y

  // hover tooltip
  const v = findNearestVillage(w, 3 / Math.max(0.6, transform.k))
  if (v) {
    hoverTip.show = true
    hoverTip.x = evt.clientX + 10
    hoverTip.y = evt.clientY + 10
    hoverTip.v = v
  } else {
    hoverTip.show = false
    hoverTip.v = null
  }
}
function onPointerLeave() {
  hoverTip.show = false
  hoverTip.v = null
}

/* Load villages (supports multiple players/alliances) */
function normalizeVillageRow(row, fallbackId) {
  const x = Number(row.x ?? row.village_x ?? row.coord_x ?? row.cx)
  const y = Number(row.y ?? row.village_y ?? row.coord_y ?? row.cy)
  const name = row.village_name ?? row.name ?? row.village ?? row.title ?? 'Village'
  const player = row.player_name ?? row.player ?? row.owner ?? ''
  const alliance = row.alliance_tag ?? row.alliance ?? row.tag ?? ''
  const id =
    row.village_id ??
    row.id ??
    row.vid ??
    `${name}:${x}|${y}:${player}:${alliance}:${fallbackId}`

  return {
    id: String(id),
    name: String(name),
    x: Number.isFinite(x) ? x : 0,
    y: Number.isFinite(y) ? y : 0,
    player: player ? String(player) : '',
    alliance: alliance ? String(alliance) : ''
  }
}

async function fetchAlliancesAndPlayersOnce() {
  // alliances
  try {
    const { data } = await api.get('/api/alliances')
    const opts = (Array.isArray(data) ? data : []).map(a => ({
      label: `${a.alliance_tag} (${Number(a.villages || 0).toLocaleString()} villages)`,
      value: a.alliance_tag
    }))
    allianceOptionsAll.value = opts
    allianceOptionsFiltered.value = opts
  } catch {
    allianceOptionsAll.value = []
    allianceOptionsFiltered.value = []
  }

  // players
  try {
    const { data } = await api.get('/api/players?limit=10000')
    const opts = (Array.isArray(data) ? data : []).map(p => ({
      label: `${p.player_name} (${Number(p.villages || 0).toLocaleString()} villages)`,
      value: p.player_name
    }))
    playerOptionsAll.value = opts
    playerOptionsFiltered.value = opts
  } catch {
    playerOptionsAll.value = []
    playerOptionsFiltered.value = []
  }
}

async function loadVillages() {
  loading.value = true
  loadError.value = ''
  backendSupportsWorld.value = true

  try {
    let rows = []

    // Prefer a dedicated world endpoint if you add it (recommended):
    // GET /api/villages/latest?limit=...
    if (scopeMode.value === 'world') {
      try {
        const { data } = await api.get(`/api/villages/latest?limit=${encodeURIComponent(maxVillages.value)}&no_cache=1`)
        rows = Array.isArray(data) ? data : (data?.villages || [])
      } catch (e) {
        backendSupportsWorld.value = false
        throw new Error('World mode requires /api/villages/latest (see backend patch below) or use player/alliance/region mode.')
      }
    }

    // Alliances: use your existing per-scope route
    if (scopeMode.value === 'alliances') {
      const tags = (selectedAlliances.value || []).filter(Boolean)
      if (!tags.length) throw new Error('Select at least one alliance.')
      const results = await Promise.all(tags.map(tag =>
        api.get(`/api/alliance/${encodeURIComponent(tag)}/villages?limit=${encodeURIComponent(maxVillages.value)}`)
          .then(r => r.data)
      ))
      rows = results.flat()
    }

    // Players: use your existing per-scope route
    if (scopeMode.value === 'players') {
      const names = (selectedPlayers.value || []).filter(Boolean)
      if (!names.length) throw new Error('Select at least one player.')
      const results = await Promise.all(names.map(name =>
        api.get(`/api/player/${encodeURIComponent(name)}/villages?limit=${encodeURIComponent(maxVillages.value)}`)
          .then(r => r.data)
      ))
      rows = results.flat()
    }

    // Region: use your existing per-scope route
    if (scopeMode.value === 'region') {
      const rn = (regionName.value || '').trim()
      if (!rn) throw new Error('Enter a region name.')
      const { data } = await api.get(`/api/region/${encodeURIComponent(rn)}/villages?limit=${encodeURIComponent(maxVillages.value)}`)
      rows = Array.isArray(data) ? data : []
    }

    // Normalize + de-dup by id
    const normalized = rows.map((row, i) => normalizeVillageRow(row, i))
    const seen = new Set()
    const deduped = []
    for (const v of normalized) {
      if (seen.has(v.id)) continue
      seen.add(v.id)
      // clamp to world bounds
      v.x = Math.max(MAP_MIN, Math.min(MAP_MAX, v.x))
      v.y = Math.max(MAP_MIN, Math.min(MAP_MAX, v.y))
      deduped.push(v)
    }

    // If backend ignored limit, downsample (stable)
    let final = deduped
    if (final.length > maxVillages.value) {
      const step = Math.ceil(final.length / maxVillages.value)
      final = final.filter((_, idx) => idx % step === 0)
    }

    villages.value = final
    loaded.value = true
    selectedVillageIds.clear()
    hoverTip.show = false
    hoverTip.v = null

    await nextTick()
    fitToVillages()
    renderAll()
  } catch (err) {
    console.error(err)
    loadError.value = String(err?.message || err || 'Unknown error')
    villages.value = []
    loaded.value = false
    selectedVillageIds.clear()
    renderAll()
  } finally {
    loading.value = false
  }
}

function clearAll() {
  villages.value = []
  selectedVillageIds.clear()
  loaded.value = false
  loadError.value = ''
  renderAll()
}

/* Simulation */
function startSim() {
  if (simRunning.value) return
  simRunning.value = true
  const tick = () => {
    simClockSeconds.value += Math.max(0, speed.value)
    scheduleRender()
  }
  simTimer = window.setInterval(tick, 1000)
}
function stopSim() {
  simRunning.value = false
  if (simTimer) window.clearInterval(simTimer)
  simTimer = null
}
function formatClock(s) {
  const sec = Math.max(0, Number(s) || 0)
  const h = Math.floor(sec / 3600)
  const m = Math.floor((sec % 3600) / 60)
  const ss = Math.floor(sec % 60)
  const pad = n => String(n).padStart(2, '0')
  return `${pad(h)}:${pad(m)}:${pad(ss)}`
}

/* Lifecycle */
let ro = null
function lockPageScroll() {
  document.body.classList.add('trade-no-scroll')
  document.documentElement.classList.add('trade-no-scroll')
}
function unlockPageScroll() {
  document.body.classList.remove('trade-no-scroll')
  document.documentElement.classList.remove('trade-no-scroll')
}

onMounted(async () => {
  lockPageScroll()
  await nextTick()

  // Setup d3-zoom on wrapper (replicates your global map wheel/drag behavior)
  if (wrapEl.value) {
    zoom = d3.zoom()
      .scaleExtent([MIN_ZOOM, MAX_ZOOM])
      .on('zoom', (event) => {
        transform = event.transform
        zoomK.value = transform.k
        syncSliderFromZoom()
        scheduleRender()
      })

    d3.select(wrapEl.value).call(zoom).on('dblclick.zoom', null)
  }

  resizeCanvases()
  ro = new ResizeObserver(() => resizeCanvases())
  if (wrapEl.value) ro.observe(wrapEl.value)

  await fetchAlliancesAndPlayersOnce()

  // Start centered (like your requirement for the global map)
  resetView()
  renderAll()
})

onBeforeUnmount(() => {
  unlockPageScroll()
  stopSim()
  if (ro) ro.disconnect()
  ro = null
  cancelAnimationFrame(rafRender)
})

watch([showGrid, showAxes, pointSize, inactiveAlpha, dimInactive], () => scheduleRender())
watch([showLabels, showRings], () => scheduleRender())
</script>

<style scoped>
.trade-page {
  height: 100vh !important;
  overflow: hidden !important;
}

.trade-splitter {
  height: 100vh !important;
  overflow: hidden !important;
}

/* LEFT */
.side {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #0d0d0d;
  color: #eaeaea;
  overflow: hidden;
}

.side__titlebar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.03);
}

.side__title {
  display: flex;
  align-items: center;
  font-weight: 800;
  letter-spacing: 0.2px;
}

.side__tabs {
  background: rgba(255, 255, 255, 0.02);
}

.side__panels {
  flex: 1;
  min-height: 0;
  overflow: auto;
}

.panel-card {
  background: rgba(255, 255, 255, 0.03);
  border-color: rgba(255, 255, 255, 0.08);
}

.panel-card__head {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
}

.vlist {
  max-height: 320px;
  overflow: auto;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  background: rgba(0, 0, 0, 0.25);
}

.vrow {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  cursor: pointer;
}

.vrow:hover {
  background: rgba(255, 255, 255, 0.04);
}

.vrow.is-selected {
  background: rgba(255, 213, 79, 0.12);
  outline: 1px solid rgba(255, 213, 79, 0.25);
}

.vrow__main {
  flex: 1;
  min-width: 0;
}

.vrow__name {
  font-weight: 800;
  color: rgba(255, 255, 255, 0.92);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.vrow__meta {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.65);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.vlist__more {
  padding: 10px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.65);
}

.dot {
  opacity: 0.6;
  margin: 0 6px;
}

/* RIGHT */
.stage {
  height: 100%;
  min-height: 0;
  position: relative;
  overflow: hidden;
  background: #000;
}

/* HUD */
.hud {
  position: absolute;
  left: 12px;
  right: 12px;
  top: 12px;
  z-index: 20;
  pointer-events: none;
}

.hud__row {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(0, 0, 0, 0.12);
  box-shadow: 0 10px 26px rgba(0, 0, 0, 0.35);
  border-radius: 14px;
  padding: 10px;
  backdrop-filter: blur(10px);
  pointer-events: auto;
  overflow-x: auto;
}

.hud__coords {
  font-size: 12px;
  color: rgba(0, 0, 0, 0.82);
  white-space: nowrap;
}

.hud__zoom {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 270px;
  flex: 0 0 auto;
}

.hud__slider {
  width: 160px;
}

.hud__zoomtxt {
  width: 56px;
  text-align: right;
  font-size: 12px;
  opacity: 0.9;
  color: rgba(0, 0, 0, 0.85);
}

/* Map */
.canvas-wrap {
  position: absolute;
  inset: 0;
  padding-top: 0;
  overflow: hidden;
}

.layer {
  position: absolute;
  inset: 0;
  display: block;
}

.overlay {
  position: absolute;
  inset: 0;
  pointer-events: auto;
}

.ring {
  fill: rgba(255, 0, 255, 0.08);
  stroke: rgba(255, 0, 255, 0.8);
  stroke-width: 1.5;
  vector-effect: non-scaling-stroke;
}

.label {
  font-size: 10px;
  fill: rgba(255, 255, 255, 0.92);
  paint-order: stroke;
  stroke: rgba(0, 0, 0, 0.7);
  stroke-width: 2;
  vector-effect: non-scaling-stroke;
}

/* Tooltip */
.tip {
  position: fixed;
  z-index: 30;
  pointer-events: none;
  background: rgba(0, 0, 0, 0.92);
  color: #fff;
  padding: 8px 10px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  box-shadow: 0 14px 30px rgba(0, 0, 0, 0.55);
  min-width: 160px;
}

.tip__name {
  font-weight: 800;
  margin-bottom: 2px;
}

.tip__meta {
  font-size: 12px;
  opacity: 0.85;
}

/* Mobile */
.mobile {
  height: 100vh;
  overflow: hidden;
  background: #000;
  display: flex;
  flex-direction: column;
}
.mobile__map {
  flex: 1;
  min-height: 0;
  position: relative;
}

/* Global scroll lock class */
:global(html.trade-no-scroll),
:global(body.trade-no-scroll) {
  overflow: hidden !important;
}
</style>
