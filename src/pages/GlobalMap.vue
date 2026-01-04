<template>
  <q-layout class="full-view">
    <!-- HEADER -->
    <q-header elevated>
      <q-toolbar>
        <q-btn
          dense
          flat
          round
          icon="menu"
          @click="mobileSidebarOpen = !mobileSidebarOpen"
          class="lt-md"
        />
        <q-btn
          dense
          flat
          round
          icon="tune"
          @click="sidebarOpen = !sidebarOpen"
          class="gt-sm"
        />
        <q-toolbar-title>Interactive Global Map</q-toolbar-title>
        <q-space />
        <q-btn dense flat icon="refresh" @click="reloadMarkers(true)" :loading="loading" :disable="loading">
          <q-tooltip>Refresh markers (bypass cache)</q-tooltip>
        </q-btn>
        <q-btn dense flat icon="download" @click="exportPNG">
          <q-tooltip>Export PNG (screenshot)</q-tooltip>
        </q-btn>
      </q-toolbar>
    </q-header>

    <!-- PAGE -->
    <q-page-container class="q-pa-none">
      <q-page class="full-page q-pa-none row no-wrap">

        <!-- LEFT SIDEBAR - Desktop Drawer -->
        <q-drawer
          v-model="sidebarOpen"
          show-if-above
          :width="320"
          :breakpoint="1024"
          bordered
          class="menu-column-drawer bg-dark"
        >
          <q-list padding class="sidebar-content">
            <!-- GENERAL CONTROLS -->
            <div class="menu-section">
              <div class="section-header">
                <q-icon name="settings" class="q-mr-sm" />
                General Controls
              </div>
              <div class="section-scroll q-gutter-sm q-pa-sm">
                <q-toggle v-model="showBackground" label="Background Image" dense dark />
                <q-slider v-model="bgOpacity" :min="0" :max="1" :step="0.05" label label-always dark>
                  <template #label>BG Opacity: {{ bgOpacity.toFixed(2) }}</template>
                </q-slider>

                <q-toggle v-model="showGrid" label="Grid" dense dark />
                <q-slider v-model="gridOpacity" :min="0" :max="1" :step="0.05" label label-always dark>
                  <template #label>Grid Opacity: {{ gridOpacity.toFixed(2) }}</template>
                </q-slider>
                <q-slider v-model="gridSize" :min="0.5" :max="10" :step="0.5" label label-always dark>
                  <template #label>Grid Size: {{ gridSize }}u</template>
                </q-slider>

                <q-separator spaced dark />
                <div class="row q-col-gutter-sm">
                  <div class="col">
                    <q-input v-model.number="gotoX" type="number" label="Goto X" dense outlined dark />
                  </div>
                  <div class="col">
                    <q-input v-model.number="gotoY" type="number" label="Goto Y" dense outlined dark />
                  </div>
                </div>
                <q-btn class="full-width q-mt-sm" color="primary" icon="my_location" label="Center on coords" @click="centerOnCoords" />
              </div>

              <div class="section-actions">
                <q-btn class="full-width" color="primary" label="Toggle All Markers" @click="toggleAllMarkers" />
              </div>
            </div>

            <!-- GROUP FILTERS - Excluding regions -->
            <div class="menu-section" v-for="grp in ['alliances','tribes']" :key="grp">
              <div class="section-header">
                <q-icon name="filter_list" class="q-mr-sm" />
                {{ capitalize(grp) }}
              </div>

              <div class="q-pa-sm">
                <q-input
                  dense outlined clearable
                  v-model="groupFilters[grp]"
                  :label="`Filter ${capitalize(grp)}...`"
                  @update:model-value="filterGroup(grp)"
                  dark
                >
                  <template #append><q-icon name="search" /></template>
                </q-input>
                <div class="row q-col-gutter-sm q-mt-sm">
                  <div class="col-4"><q-btn size="sm" color="primary" outline label="All"   @click="selectGroup(grp,'all')" /></div>
                  <div class="col-4"><q-btn size="sm" color="primary" outline label="None"  @click="selectGroup(grp,'none')" /></div>
                  <div class="col-4"><q-btn size="sm" color="primary" outline label="Invert" @click="selectGroup(grp,'invert')" /></div>
                </div>
              </div>

              <div class="section-scroll">
                <div :ref="el => (groupRefs[grp] = el)" v-html="toggles[grp]" class="q-pa-sm" />
              </div>
            </div>

            <!-- DRAWING & MEASURE -->
            <div class="menu-section">
              <div class="section-header">
                <q-icon name="brush" class="q-mr-sm" />
                Drawing / Measure
              </div>

              <div class="section-scroll q-pa-sm q-gutter-sm">
                <q-select
                  dense outlined
                  v-model="drawMode"
                  :options="drawOptions"
                  label="Mode"
                  emit-value map-options
                  dark
                />
                <div class="row q-col-gutter-sm">
                  <div class="col-6">
                    <q-input v-model="drawColor" label="Color" type="color" dense outlined dark />
                  </div>
                  <div class="col-6">
                    <q-slider v-model="drawWidth" :min="1" :max="10" :step="1" label label-always dark />
                  </div>
                </div>
                <q-toggle v-model="snapToGrid" label="Snap to grid" dense dark />
                <div class="row q-col-gutter-sm">
                  <div class="col-6"><q-btn class="full-width" color="info" label="Undo"  :disable="!canUndo"  @click="undo" /></div>
                  <div class="col-6"><q-btn class="full-width" color="info" label="Redo"  :disable="!canRedo"  @click="redo" /></div>
                </div>
                <div class="row q-col-gutter-sm q-mt-sm">
                  <div class="col-6"><q-btn class="full-width" color="negative" label="Clear" @click="clearDrawings" /></div>
                  <div class="col-6">
                    <q-btn-dropdown class="full-width" color="secondary" label="Save / Load">
                      <q-list>
                        <q-item clickable v-close-popup @click="exportDrawings"><q-item-section>Export JSON</q-item-section></q-item>
                        <q-item clickable v-close-popup @click="importDrawings"><q-item-section>Import JSON</q-item-section></q-item>
                        <q-separator />
                        <q-item clickable v-close-popup @click="saveToLocal"><q-item-section>Save to LocalStorage</q-item-section></q-item>
                        <q-item clickable v-close-popup @click="loadFromLocal"><q-item-section>Load from LocalStorage</q-item-section></q-item>
                      </q-list>
                    </q-btn-dropdown>
                  </div>
                </div>
              </div>
            </div>

          </q-list>
        </q-drawer>

        <!-- MAP COLUMN -->
        <div class="map-column">
          <!-- Important: do NOT preventDefault here, so Quasar context-menu can show -->
          <div class="svg-container" @contextmenu.capture="onContextMenu">
            <svg
              ref="svg"
              id="svgMap"
              preserveAspectRatio="xMidYMid meet"
              @mouseleave="hideTooltip"
              @pointerdown="onPointerDown"
              @pointermove="onPointerMove"
              @pointerup="onPointerUp"
            >
              <defs>
                <pattern id="grid" :width="gridSize" :height="gridSize" patternUnits="userSpaceOnUse">
                  <path :d="`M${gridSize} 0 L0 0 L0 ${gridSize}`" fill="none" stroke="gray" stroke-width="0.05" :opacity="gridOpacity" />
                </pattern>
              </defs>

              <!-- Zoomable world -->
              <g id="viewport">
                <!-- Solid black world background -->
                <rect x="-100000" y="-100000" width="200000" height="200000" fill="#000" />

                <!-- Aspect-correct background image -->
                <image
                  id="bgImage"
                  :x="bgRect.x" :y="bgRect.y" :width="bgRect.width" :height="bgRect.height"
                  :style="{ display: showBackground ? 'block' : 'none', opacity: bgOpacity }"
                  href="/background.png"
                  preserveAspectRatio="none"
                />

                <!-- Grid -->
                <rect
                  id="gridRect"
                  x="-100000" y="-100000" width="200000" height="200000"
                  :style="{ display: showGrid ? 'block' : 'none' }"
                  fill="url(#grid)"
                />

                <!-- Axes (subtle) -->
                <line x1="-20000" y1="0" x2="20000" y2="0" stroke="white" stroke-width="0.1" opacity="0.12"/>
                <line x1="0" y1="-20000" x2="0" y2="20000" stroke="white" stroke-width="0.1" opacity="0.12"/>

                <!-- Markers -->
                <g ref="markersGroup" id="markersLayer" v-html="markers"></g>

                <!-- Drawings -->
                <g id="drawLayer" style="pointer-events: none;">
                  <template v-for="(d,i) in drawings" :key="i">
                    <line v-if="d.type==='line'" :x1="d.x1" :y1="d.y1" :x2="d.x2" :y2="d.y2" v-bind="d.style" />
                    <rect v-else-if="d.type==='rect'" :x="d.x" :y="d.y" :width="d.width" :height="d.height" v-bind="d.style" />
                    <circle v-else-if="d.type==='circle'" :cx="d.cx" :cy="d.cy" :r="d.r" v-bind="d.style" />
                    <path v-else-if="d.type==='path'" :d="d.d" fill="none" v-bind="d.style" />
                    <g v-else-if="d.type==='measure'">
                      <line :x1="d.x1" :y1="d.y1" :x2="d.x2" :y2="d.y2" v-bind="d.style" />
                      <text :x="(d.x1+d.x2)/2" :y="(d.y1+d.y2)/2 - 0.5" font-size="1.5" text-anchor="middle" class="measure-label">
                        {{ Number(d.distance).toFixed(1) }} tiles
                      </text>
                    </g>
                    <text v-else-if="d.type==='text'" :x="d.x" :y="d.y" v-bind="d.style">{{ d.text }}</text>
                  </template>
                </g>

                <!-- Live preview -->
                <g id="previewLayer" ref="previewLayer" style="pointer-events: none;"></g>
              </g>

              <!-- Screen-fixed coord labels -->
              <g id="coordLabels">
                <text id="labelLeft"   text-anchor="end"    alignment-baseline="middle" class="coord-label"/>
                <text id="labelRight"  text-anchor="start"  alignment-baseline="middle" class="coord-label"/>
                <text id="labelTop"    text-anchor="middle" alignment-baseline="hanging" class="coord-label"/>
                <text id="labelBottom" text-anchor="middle" alignment-baseline="baseline" class="coord-label"/>
              </g>
            </svg>

            <!-- Right-click context menu -->
            <q-menu context-menu>
              <q-list style="min-width: 220px">
                <q-item-label header>Actions</q-item-label>
                <q-item clickable :disable="!ctx.hasMarker" @click="centerOnContext" v-close-popup>
                  <q-item-section avatar><q-icon name="center_focus_strong" /></q-item-section>
                  <q-item-section>Center map on this village</q-item-section>
                </q-item>
              </q-list>
            </q-menu>

            <q-inner-loading :showing="loading">
              <q-spinner color="primary" size="2em" />
            </q-inner-loading>

            <!-- TOOLTIP -->
            <div v-if="tooltip.show" class="tooltip" :style="{ top: tooltip.y + 'px', left: tooltip.x + 'px' }" v-html="tooltip.content" />
          </div>

          <!-- Status bar -->
          <div class="statusbar row items-center q-px-sm q-py-xs">
            <div class="col text-caption">Cursor: X {{ cursor.x.toFixed(0) }} / Y {{ cursor.y.toFixed(0) }}</div>
            <div class="col text-caption text-right">Zoom: {{ zoomK.toFixed(2) }}×</div>
          </div>

          <!-- FAB controls -->
          <q-fab
            vertical-actions-align="right"
            color="primary"
            icon="map"
            direction="up"
            class="fab"
            :class="{ 'fab-mobile': $q.screen.lt.md }"
          >
            <q-fab-action color="primary" icon="add" @click="zoomBy(1.25)"   label="Zoom In" />
            <q-fab-action color="primary" icon="remove" @click="zoomBy(0.8)" label="Zoom Out" />
            <q-fab-action color="secondary" icon="center_focus_strong" @click="resetView" label="Reset View" />
            <q-fab-action color="secondary" icon="crop_free" @click="fitToContent" label="Fit to Map" />
            <q-fab-action color="accent" icon="straighten" @click="drawMode='measure'" label="Measure" />
          </q-fab>
        </div>

      </q-page>
    </q-page-container>

    <!-- Mobile Bottom Sheet -->
    <q-dialog
      v-model="mobileSidebarOpen"
      position="bottom"
      class="lt-md"
    >
      <q-card style="min-height: 70vh; max-height: 90vh;" class="bg-dark text-white">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Map Controls</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        <q-card-section class="q-pt-none sidebar-content" style="max-height: calc(70vh - 60px); overflow-y: auto;">
          <q-list padding>
            <!-- GENERAL CONTROLS -->
            <div class="menu-section">
              <div class="section-header">
                <q-icon name="settings" class="q-mr-sm" />
                General Controls
              </div>
              <div class="section-scroll q-gutter-sm q-pa-sm">
                <q-toggle v-model="showBackground" label="Background Image" dense dark />
                <q-slider v-model="bgOpacity" :min="0" :max="1" :step="0.05" label label-always dark>
                  <template #label>BG Opacity: {{ bgOpacity.toFixed(2) }}</template>
                </q-slider>

                <q-toggle v-model="showGrid" label="Grid" dense dark />
                <q-slider v-model="gridOpacity" :min="0" :max="1" :step="0.05" label label-always dark>
                  <template #label>Grid Opacity: {{ gridOpacity.toFixed(2) }}</template>
                </q-slider>
                <q-slider v-model="gridSize" :min="0.5" :max="10" :step="0.5" label label-always dark>
                  <template #label>Grid Size: {{ gridSize }}u</template>
                </q-slider>

                <q-separator spaced dark />
                <div class="row q-col-gutter-sm">
                  <div class="col">
                    <q-input v-model.number="gotoX" type="number" label="Goto X" dense outlined dark />
                  </div>
                  <div class="col">
                    <q-input v-model.number="gotoY" type="number" label="Goto Y" dense outlined dark />
                  </div>
                </div>
                <q-btn class="full-width q-mt-sm" color="primary" icon="my_location" label="Center on coords" @click="centerOnCoords" />
              </div>

              <div class="section-actions">
                <q-btn class="full-width" color="primary" label="Toggle All Markers" @click="toggleAllMarkers" />
              </div>
            </div>

            <!-- GROUP FILTERS - Excluding regions -->
            <div class="menu-section" v-for="grp in ['alliances','tribes']" :key="grp">
              <div class="section-header">
                <q-icon name="filter_list" class="q-mr-sm" />
                {{ capitalize(grp) }}
              </div>

              <div class="q-pa-sm">
                <q-input
                  dense outlined clearable
                  v-model="groupFilters[grp]"
                  :label="`Filter ${capitalize(grp)}...`"
                  @update:model-value="filterGroup(grp)"
                  dark
                >
                  <template #append><q-icon name="search" /></template>
                </q-input>
                <div class="row q-col-gutter-sm q-mt-sm">
                  <div class="col-4"><q-btn size="sm" color="primary" outline label="All"   @click="selectGroup(grp,'all')" /></div>
                  <div class="col-4"><q-btn size="sm" color="primary" outline label="None"  @click="selectGroup(grp,'none')" /></div>
                  <div class="col-4"><q-btn size="sm" color="primary" outline label="Invert" @click="selectGroup(grp,'invert')" /></div>
                </div>
              </div>

              <div class="section-scroll">
                <div :ref="el => (groupRefs[grp] = el)" v-html="toggles[grp]" class="q-pa-sm" />
              </div>
            </div>

            <!-- DRAWING & MEASURE -->
            <div class="menu-section">
              <div class="section-header">
                <q-icon name="brush" class="q-mr-sm" />
                Drawing / Measure
              </div>

              <div class="section-scroll q-pa-sm q-gutter-sm">
                <q-select
                  dense outlined
                  v-model="drawMode"
                  :options="drawOptions"
                  label="Mode"
                  emit-value map-options
                  dark
                />
                <div class="row q-col-gutter-sm">
                  <div class="col-6">
                    <q-input v-model="drawColor" label="Color" type="color" dense outlined dark />
                  </div>
                  <div class="col-6">
                    <q-slider v-model="drawWidth" :min="1" :max="10" :step="1" label label-always dark />
                  </div>
                </div>
                <q-toggle v-model="snapToGrid" label="Snap to grid" dense dark />
                <div class="row q-col-gutter-sm">
                  <div class="col-6"><q-btn class="full-width" color="info" label="Undo"  :disable="!canUndo"  @click="undo" /></div>
                  <div class="col-6"><q-btn class="full-width" color="info" label="Redo"  :disable="!canRedo"  @click="redo" /></div>
                </div>
                <div class="row q-col-gutter-sm q-mt-sm">
                  <div class="col-6"><q-btn class="full-width" color="negative" label="Clear" @click="clearDrawings" /></div>
                  <div class="col-6">
                    <q-btn-dropdown class="full-width" color="secondary" label="Save / Load">
                      <q-list>
                        <q-item clickable v-close-popup @click="exportDrawings"><q-item-section>Export JSON</q-item-section></q-item>
                        <q-item clickable v-close-popup @click="importDrawings"><q-item-section>Import JSON</q-item-section></q-item>
                        <q-separator />
                        <q-item clickable v-close-popup @click="saveToLocal"><q-item-section>Save to LocalStorage</q-item-section></q-item>
                        <q-item clickable v-close-popup @click="loadFromLocal"><q-item-section>Load from LocalStorage</q-item-section></q-item>
                      </q-list>
                    </q-btn-dropdown>
                  </div>
                </div>
              </div>
            </div>

          </q-list>
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- PLAYER PROFILE DIALOG -->
    <q-dialog v-model="profileDialog">
      <q-card style="min-width: 500px; max-width: 800px">
        <q-card-section class="row items-center">
          <div class="text-h6">Player: {{ profile.name }}</div>
          <q-space/>
          <q-btn icon="close" flat round dense @click="profileDialog=false"/>
        </q-card-section>
        <q-separator/>
        <q-card-section v-if="profile.villages.length">
          <q-table
            :columns="profileColumns"
            :rows="profile.villages"
            row-key="coords"
            dense flat wrap-cells
            :rows-per-page-options="[10,20,50,0]"
          />
        </q-card-section>
        <q-card-section v-else class="text-grey">No villages found.</q-card-section>
        <q-card-actions align="right">
          <div class="text-subtitle2">Total population: {{ profile.totalPopulation }}</div>
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-layout>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick, onBeforeUnmount, watch } from 'vue'
import { api } from 'boot/axios'
import { useQuasar } from 'quasar'
import * as d3 from 'd3'

/* === State === */
const $q = useQuasar()
const loading = ref(false)
const sidebarOpen = ref($q.screen.gt.sm) // Open on desktop, closed on mobile by default
const mobileSidebarOpen = ref(false)

// Watch sidebarOpen to sync with mobile dialog
watch(() => $q.screen.lt.md, (isMobile) => {
  if (isMobile) {
    mobileSidebarOpen.value = sidebarOpen.value
  }
})

watch(sidebarOpen, (val) => {
  if ($q.screen.lt.md) {
    mobileSidebarOpen.value = val
  }
})

watch(mobileSidebarOpen, (val) => {
  if ($q.screen.lt.md) {
    sidebarOpen.value = val
  }
})

/** Map & zoom */
const svg = ref(null)
const markersGroup = ref(null)
const previewLayer = ref(null)
let zoom // d3 zoom instance
const zoomK = ref(1)
const cursor = ref({ x: 0, y: 0 })
const gotoX = ref(0)
const gotoY = ref(0)

/** Layers */
const showBackground = ref(true)
const bgOpacity = ref(0.6)
const showGrid = ref(true)
const gridOpacity = ref(0.35)
const gridSize = ref(2)

/** Markers & filters */
const markers = ref('')
const toggles = ref({ alliances: '', tribes: '' })
const groupRefs = { alliances: null, tribes: null }
const groupFilters = ref({ alliances: '', tribes: '' })
let masterVisible = true

/** Background image metrics + computed rect (in map coords) */
const bgMeta = reactive({ w: 0, h: 0, loaded: false })
const bgRect = reactive({ x: -400, y: -400, width: 800, height: 800 })
let initialFitted = false

/** Tooltip */
const tooltip = ref({ show: false, x: 0, y: 0, content: '' })

/** Context menu state (right-click) */
const ctx = reactive({ hasMarker: false, point: null })

/** Player dialog */
const profileDialog = ref(false)
const profile = ref({ name: '', villages: [], totalPopulation: 0 })
const profileColumns = [
  { name:'village',       label:'Village',    field:'village' },
  { name:'coords',        label:'Coords',     field:'coords' },
  { name:'population',    label:'Population', field:'population', align:'right' },
  { name:'victoryPoints', label:'VP',         field:'victoryPoints', align:'right' },
  { name:'alliance',      label:'Alliance',   field:'alliance' },
  { name:'region',        label:'Region',     field:'region'   },
  { name:'tribe',         label:'Tribe',      field:'tribe'    }
]

/** Drawing / history / measure */
const drawMode = ref(null) // null|'line'|'rect'|'circle'|'path'|'text'|'measure'
const drawOptions = [
  { label:'Off', value:null },
  { label:'Line', value:'line' },
  { label:'Rect', value:'rect' },
  { label:'Circle', value:'circle' },
  { label:'Freehand', value:'path' },
  { label:'Text', value:'text' },
  { label:'Measure', value:'measure' }
]
const drawColor = ref('#ff0000')
const drawWidth = ref(2)
const snapToGrid = ref(false)

const drawings = ref([])
const history = ref([])
const historyIndex = ref(-1)
const canUndo = computed(() => historyIndex.value > 0)
const canRedo = computed(() => history.value.length && historyIndex.value < history.value.length - 1)

/* === Utils === */
const CACHE_KEY = 'markersCache'
const CACHE_TTL = 15 * 60 * 1000 // 15 minutes
const DEFAULT_WORLD = { x: -400, y: -400, width: 800, height: 800 } // fallback world

const capitalize = (s) => s.charAt(0).toUpperCase() + s.slice(1)

function pushHistory () {
  history.value = history.value.slice(0, historyIndex.value + 1)
  history.value.push(JSON.parse(JSON.stringify(drawings.value)))
  historyIndex.value = history.value.length - 1
}
function undo () { if (canUndo.value) { historyIndex.value--; drawings.value = JSON.parse(JSON.stringify(history.value[historyIndex.value])) } }
function redo () { if (canRedo.value) { historyIndex.value++; drawings.value = JSON.parse(JSON.stringify(history.value[historyIndex.value])) } }
function clearDrawings () { drawings.value = []; pushHistory(); saveToLocal() }
function saveToLocal () { localStorage.setItem('drawings', JSON.stringify(drawings.value)) }
function loadFromLocal () {
  const raw = localStorage.getItem('drawings')
  if (raw) { drawings.value = JSON.parse(raw); pushHistory() }
}

/** Sanitizer for tooltips (DOMPurify if available) */
function sanitize (html) {
  try {
    if (window.DOMPurify?.sanitize) return window.DOMPurify.sanitize(html, { USE_PROFILES: { html: true, svg: true } })
  } catch {}
  return String(html).replace(/<script[\s\S]*?>[\s\S]*?<\/script>/gi, '')
}

/* === Marker filtering === */
const elementText = (el) => (el.textContent || '').toLowerCase()
function filterGroup (group) {
  const root = groupRefs[group]
  if (!root) return
  const term = (groupFilters.value[group] || '').toLowerCase().trim()
  Array.from(root.querySelectorAll('label, .q-checkbox, .q-option, div, span')).forEach(el => {
    const match = term === '' || elementText(el).includes(term)
    el.style.display = match ? '' : 'none'
  })
}
function selectGroup (group, mode) {
  const root = groupRefs[group]
  if (!root) return
  const boxes = root.querySelectorAll(`.${group.slice(0, -1)}-checkbox`)
  boxes.forEach(cb => {
    if (mode === 'all') cb.checked = true
    else if (mode === 'none') cb.checked = false
    else cb.checked = !cb.checked
  })
  updateMarkersVisibility()
}

/* === Visibility === */
function getClassValue (el, prefix) {
  const c = Array.from(el.classList).find(x => x.startsWith(prefix))
  return c ? c.slice(prefix.length) : ''
}
function updateMarkersVisibility () {
  if (!markersGroup.value) return
  const groupCheck = (type, val) => document.getElementById(`toggle${capitalize(type)}-${val}`)?.checked !== false
  markersGroup.value.querySelectorAll('.marker').forEach(node => {
    const alliance = getClassValue(node, 'alliance-')
    const region   = getClassValue(node, 'region-')
    const tribe    = getClassValue(node, 'tribe-')
    const on =
      masterVisible &&
      (alliance ? groupCheck('Alliance', alliance) : true) &&
      (region   ? groupCheck('Region',   region)   : true) &&
      (tribe    ? groupCheck('Tribe',    tribe)    : true)
    node.style.display = on ? 'block' : 'none'
  })
}

/* === Tooltip & profile === */
const hideTooltip = () => { tooltip.value.show = false }
async function openPlayerProfile (owner) {
  try {
    const { data } = await api.get(`/api/player/${encodeURIComponent(owner)}/villages`)
    profile.value.name = data.player
    profile.value.villages = data.villages
    profile.value.totalPopulation = data.villages.reduce((s, v) => s + (v.population || 0), 0)
  } catch {
    $q.notify({ type: 'negative', message: `Failed to load ${owner}` })
    profile.value = { name: owner, villages: [], totalPopulation: 0 }
  }
  profileDialog.value = true
}

/* === Pointer -> map coords === */
function toMapCoords (evt) {
  const [sx, sy] = d3.pointer(evt, svg.value)
  const t = d3.zoomTransform(svg.value)
  return { x: t.invertX(sx), y: t.invertY(sy) }
}
const snap = (v) => (snapToGrid.value ? Math.round(v / gridSize.value) * gridSize.value : v)

/* === Drawing / Measure === */
let previewElem = null
let anchor = null
let isDrawing = false

function applyPreviewStyle (el) {
  el.setAttribute('stroke', drawColor.value)
  el.setAttribute('stroke-width', drawWidth.value)
  if (['rect', 'circle'].includes(drawMode.value)) el.setAttribute('fill', drawColor.value + '33')
  else el.setAttribute('fill', 'none')
  if (el.tagName === 'path') {
    el.setAttribute('stroke-linecap', 'round')
    el.setAttribute('stroke-linejoin', 'round')
  }
}

function onPointerDown (evt) {
  const p = toMapCoords(evt)
  cursor.value = p

  if (!drawMode.value) return
  evt.preventDefault()

  const pt = { x: snap(p.x), y: snap(p.y) }

  if (drawMode.value === 'text') {
    const txt = prompt('Enter text:')
    if (txt) {
      drawings.value.push({
        type: 'text', x: pt.x, y: pt.y, text: txt,
        style: { stroke: drawColor.value, 'stroke-width': drawWidth.value, fill: 'none' }
      })
      pushHistory(); saveToLocal()
    }
    return
  }

  if (drawMode.value === 'measure') {
    if (!anchor) { anchor = pt; isDrawing = true } else {
      const dist = Math.hypot(pt.x - anchor.x, pt.y - anchor.y)
      drawings.value.push({
        type: 'measure',
        x1: anchor.x, y1: anchor.y, x2: pt.x, y2: pt.y,
        distance: dist,
        style: { stroke: '#00bcd4', 'stroke-width': 1.5, 'stroke-dasharray': '2 2', fill: 'none' }
      })
      pushHistory(); saveToLocal()
      anchor = null; isDrawing = false
      if (previewElem) { previewLayer.value.removeChild(previewElem); previewElem = null }
    }
    return
  }

  isDrawing = true
  anchor = pt
  const ns = 'http://www.w3.org/2000/svg'
  if (drawMode.value === 'line') {
    previewElem = document.createElementNS(ns, 'line')
    previewElem.setAttribute('x1', pt.x)
    previewElem.setAttribute('y1', pt.y)
    previewElem.setAttribute('x2', pt.x)
    previewElem.setAttribute('y2', pt.y)
  } else if (drawMode.value === 'rect') {
    previewElem = document.createElementNS(ns, 'rect')
    previewElem.setAttribute('x', pt.x)
    previewElem.setAttribute('y', pt.y)
    previewElem.setAttribute('width', 0)
    previewElem.setAttribute('height', 0)
  } else if (drawMode.value === 'circle') {
    previewElem = document.createElementNS(ns, 'circle')
    previewElem.setAttribute('cx', pt.x)
    previewElem.setAttribute('cy', pt.y)
    previewElem.setAttribute('r', 0)
  } else if (drawMode.value === 'path') {
    previewElem = document.createElementNS(ns, 'path')
    previewElem.setAttribute('d', `M${pt.x},${pt.y}`)
  }
  applyPreviewStyle(previewElem)
  previewLayer.value.appendChild(previewElem)
}

function onPointerMove (evt) {
  const p = toMapCoords(evt)
  cursor.value = p

  if (!isDrawing || !previewElem) return
  evt.preventDefault()
  const pt = { x: snap(p.x), y: snap(p.y) }

  switch (drawMode.value) {
    case 'line':
      previewElem.setAttribute('x2', pt.x)
      previewElem.setAttribute('y2', pt.y)
      break
    case 'rect': {
      const x = Math.min(anchor.x, pt.x); const y = Math.min(anchor.y, pt.y)
      const w = Math.abs(pt.x - anchor.x); const h = Math.abs(pt.y - anchor.y)
      previewElem.setAttribute('x', x); previewElem.setAttribute('y', y)
      previewElem.setAttribute('width', w); previewElem.setAttribute('height', h)
      break
    }
    case 'circle': {
      const r = Math.hypot(pt.x - anchor.x, pt.y - anchor.y)
      previewElem.setAttribute('r', r)
      break
    }
    case 'path': {
      const d = previewElem.getAttribute('d') + ` L${pt.x},${pt.y}`
      previewElem.setAttribute('d', d)
      break
    }
    case 'measure': {
      previewElem?.remove()
      const ns = 'http://www.w3.org/2000/svg'
      previewElem = document.createElementNS(ns, 'line')
      previewElem.setAttribute('x1', anchor.x)
      previewElem.setAttribute('y1', anchor.y)
      previewElem.setAttribute('x2', pt.x)
      previewElem.setAttribute('y2', pt.y)
      previewElem.setAttribute('stroke', '#00bcd4')
      previewElem.setAttribute('stroke-width', 1)
      previewElem.setAttribute('stroke-dasharray', '2 2')
      previewElem.setAttribute('fill', 'none')
      previewLayer.value.appendChild(previewElem)
      break
    }
  }
}

function onPointerUp (evt) {
  if (!isDrawing || !previewElem || drawMode.value === 'measure') return
  evt.preventDefault()
  const finalize = (shape) => { drawings.value.push(shape); pushHistory(); saveToLocal() }
  const color = drawColor.value; const width = drawWidth.value

  if (drawMode.value === 'line') {
    finalize({
      type: 'line',
      x1: +previewElem.getAttribute('x1'), y1: +previewElem.getAttribute('y1'),
      x2: +previewElem.getAttribute('x2'), y2: +previewElem.getAttribute('y2'),
      style: { stroke: color, 'stroke-width': width, fill: 'none' }
    })
  } else if (drawMode.value === 'rect') {
    finalize({
      type: 'rect',
      x: +previewElem.getAttribute('x'), y: +previewElem.getAttribute('y'),
      width: +previewElem.getAttribute('width'), height: +previewElem.getAttribute('height'),
      style: { stroke: color, 'stroke-width': width, fill: color + '33' }
    })
  } else if (drawMode.value === 'circle') {
    finalize({
      type: 'circle',
      cx: +previewElem.getAttribute('cx'), cy: +previewElem.getAttribute('cy'),
      r: +previewElem.getAttribute('r'),
      style: { stroke: color, 'stroke-width': width, fill: color + '33' }
    })
  } else if (drawMode.value === 'path') {
    finalize({
      type: 'path',
      d: previewElem.getAttribute('d'),
      style: { stroke: color, 'stroke-width': width, fill: 'none', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }
    })
  }

  previewLayer.value.removeChild(previewElem)
  previewElem = null
  isDrawing = false
  anchor = null
}

/* Keyboard */
function onKeydown (evt) {
  if ((evt.ctrlKey || evt.metaKey) && !evt.shiftKey && evt.key === 'z') { undo(); evt.preventDefault() }
  else if ((evt.ctrlKey || evt.metaKey) && (evt.key === 'y' || (evt.shiftKey && evt.key === 'Z'))) { redo(); evt.preventDefault() }
  else if (evt.key === 'Escape') {
    drawMode.value = null
    previewElem?.remove(); previewElem = null
    isDrawing = false; anchor = null
  }
}

/* === Zoom helpers === */
function centerAt (x, y, k = d3.zoomTransform(svg.value).k) {
  const rect = svg.value.getBoundingClientRect()
  const tx = rect.width / 2 - k * x
  const ty = rect.height / 2 - k * y
  const t = d3.zoomIdentity.translate(tx, ty).scale(k)
  d3.select(svg.value).transition().duration(250).call(zoom.transform, t)
}
function resetView () {
  // Full view of the map (background + markers)
  fitToContent()
}
function zoomBy (factor) {
  d3.select(svg.value).transition().duration(200).call(zoom.scaleBy, factor)
}
function centerOnCoords () {
  const [x, y] = [Number(gotoX.value) || 0, Number(gotoY.value) || 0]
  centerAt(x, y)
}
function fitToBBox (bbox, pad = 1.0) {
  if (!bbox || bbox.width <= 0 || bbox.height <= 0) return
  const rect = svg.value.getBoundingClientRect()
  const k = Math.min(rect.width / (bbox.width * pad), rect.height / (bbox.height * pad))
  centerAt(bbox.x + bbox.width / 2, bbox.y + bbox.height / 2, k)
}
function fitToMarkers () {
  const g = markersGroup.value
  if (!g) return
  const bbox = g.getBBox()
  if (bbox.width === 0 || bbox.height === 0) return
  fitToBBox(bbox, 1.02)
}
function unionBBox (a, b) {
  const x = Math.min(a.x, b.x)
  const y = Math.min(a.y, b.y)
  const x2 = Math.max(a.x + a.width, b.x + b.width)
  const y2 = Math.max(a.y + a.height, b.y + b.height)
  return { x, y, width: x2 - x, height: y2 - y }
}
const markersBBoxOrDefault = () => {
  const g = markersGroup.value
  if (g) {
    const bb = g.getBBox()
    if (bb.width > 0 && bb.height > 0) return bb
  }
  return { ...DEFAULT_WORLD }
}
function fitToContent () {
  const mbox = markersBBoxOrDefault()
  const bbox = unionBBox(mbox, bgRect)
  fitToBBox(bbox, 1.02)
}

/* === Background layout: aspect-correct image placement === */
const layoutBackground = () => {
  if (!bgMeta.loaded || bgMeta.w === 0 || bgMeta.h === 0) return
  const target = markersBBoxOrDefault()
  const rImg = bgMeta.w / bgMeta.h
  const rBox = target.width / target.height

  if (rImg >= rBox) {
    const height = target.height
    const width = height * rImg
    const x = target.x + (target.width - width) / 2
    const y = target.y
    Object.assign(bgRect, { x, y, width, height })
  } else {
    const width = target.width
    const height = width / rImg
    const x = target.x
    const y = target.y + (target.height - height) / 2
    Object.assign(bgRect, { x, y, width, height })
  }

  if (!initialFitted) {
    initialFitted = true
    const all = unionBBox(markersBBoxOrDefault(), bgRect)
    fitToBBox(all, 1.02)
  }
}

/* === Markers load & bind === */
async function reloadMarkers (force = false) {
  loading.value = true
  try {
    let payload = null
    if (!force) {
      try {
        const raw = localStorage.getItem(CACHE_KEY)
        if (raw) {
          const { at, data } = JSON.parse(raw)
          if (Date.now() - at < CACHE_TTL) payload = data
        }
      } catch (e) {
        console.warn('Failed to parse cache:', e)
        // Clear invalid cache
        localStorage.removeItem(CACHE_KEY)
      }
    }
    if (!payload) {
      try {
        const { data } = await api.get('/api/markers')
        if (!data) {
          console.error('API returned empty data')
          return
        }
        payload = data
        localStorage.setItem(CACHE_KEY, JSON.stringify({ at: Date.now(), data }))
      } catch (error) {
        console.error('Failed to load markers from API:', error)
        // Try to use cached data even if expired
        try {
          const raw = localStorage.getItem(CACHE_KEY)
          if (raw) {
            const { data } = JSON.parse(raw)
            payload = data
            console.warn('Using expired cache due to API error')
          }
        } catch (e) {
          console.error('No valid cache available:', e)
        }
        if (!payload) {
          throw error // Re-throw if we have no fallback
        }
      }
    }
    
    if (!payload) {
      console.error('No markers data available')
      markers.value = ''
      toggles.value = { alliances: '', regions: '', tribes: '' }
      return
    }
    
    markers.value = payload?.markers || ''
    toggles.value = {
      alliances: payload?.alliance_checkboxes || '',
      tribes:    payload?.tribe_checkboxes    || ''
    }
    
    if (!markers.value) {
      console.warn('Markers data is empty. Payload:', payload)
    }
    
    await nextTick()

    // Delegated events for group checkbox changes
    ;['alliances','tribes'].forEach(grp => {
      const root = groupRefs[grp]
      if (!root) return
      root.addEventListener('change', (e) => {
        const t = e.target
        if (t && (t.classList.contains('alliance-checkbox') || t.classList.contains('region-checkbox') || t.classList.contains('tribe-checkbox'))) {
          updateMarkersVisibility()
        }
      })
    })

    // Marker events via delegation
    bindMarkerDelegatedEvents()

    updateMarkersVisibility()
    layoutBackground()
  } catch (error) {
    console.error('Error loading markers:', error)
    markers.value = ''
    toggles.value = { alliances: '', tribes: '' }
  } finally {
    loading.value = false
  }
}

function bindMarkerDelegatedEvents () {
  const root = markersGroup.value
  if (!root) return

  root.onpointerover = (e) => {
    const el = e.target.closest('.marker')
    if (!el) return
    const tip = el.getAttribute('data-tooltip') || ''
    const content = sanitize(tip.replace(/<br>/g, '<br/>'))
    tooltip.value = { show: true, x: e.clientX + 8, y: e.clientY + 8, content }
  }
  root.onpointerout = (e) => {
    if (e.relatedTarget && e.currentTarget.contains(e.relatedTarget)) return
    hideTooltip()
  }
  root.onclick = async (e) => {
    const el = e.target.closest('.marker')
    if (!el) return
    let owner = (el.getAttribute('data-player') || '').replace(/^'+|'+$/g, '')
    if (owner) await openPlayerProfile(owner)
  }
}

/* === Right-click context menu helpers === */
function onContextMenu (e) {
  // runs before QMenu shows (capture phase)
  const el = e.target.closest('.marker')
  ctx.hasMarker = !!el
  if (el) {
    // center of marker bbox in map coords
    const bb = el.getBBox()
    ctx.point = { x: bb.x + bb.width / 2, y: bb.y + bb.height / 2 }
  } else {
    ctx.point = toMapCoords(e)
  }
}
function centerOnContext () {
  if (!ctx.point) return
  centerAt(ctx.point.x, ctx.point.y)
}

/* === Marker master toggle === */
function toggleAllMarkers () {
  masterVisible = !masterVisible
  updateMarkersVisibility()
}

/* === PNG Export === */
async function exportPNG () {
  await nextTick()
  const s = svg.value
  const clone = s.cloneNode(true)
  Array.from(clone.querySelectorAll('.q-inner-loading, .q-menu, .q-dialog')).forEach(n => n.remove())

  const serializer = new XMLSerializer()
  const svgStr = serializer.serializeToString(clone)
  const blob = new Blob([svgStr], { type: 'image/svg+xml;charset=utf-8' })
  const url = URL.createObjectURL(blob)

  const img = new Image()
  img.onload = () => {
    const rect = s.getBoundingClientRect()
    const canvas = document.createElement('canvas')
    canvas.width = Math.max(1, Math.round(rect.width))
    canvas.height = Math.max(1, Math.round(rect.height))
    const ctx2d = canvas.getContext('2d')
    ctx2d.fillStyle = '#000' // black background to match map
    ctx2d.fillRect(0, 0, canvas.width, canvas.height)
    ctx2d.drawImage(img, 0, 0, canvas.width, canvas.height)
    URL.revokeObjectURL(url)
    canvas.toBlob(b => {
      const dl = document.createElement('a')
      dl.href = URL.createObjectURL(b)
      dl.download = `map-${Date.now()}.png`
      dl.click()
      setTimeout(() => URL.revokeObjectURL(dl.href), 5000)
    }, 'image/png')
  }
  img.onerror = () => { URL.revokeObjectURL(url); $q.notify({ type: 'negative', message: 'Failed to export PNG' }) }
  img.src = url
}

/* === Lifecycle === */
function updateLabels () {
  const box = svg.value.getBoundingClientRect()
  const t = d3.zoomTransform(svg.value)
  d3.select('#labelLeft').text(t.invertX(0).toFixed(0)).attr('x', 5).attr('y', box.height / 2)
  d3.select('#labelRight').text(t.invertX(box.width).toFixed(0)).attr('x', box.width - 5).attr('y', box.height / 2)
  d3.select('#labelTop').text(t.invertY(0).toFixed(0)).attr('x', box.width / 2).attr('y', 5)
  d3.select('#labelBottom').text(t.invertY(box.height).toFixed(0)).attr('x', box.width / 2).attr('y', box.height - 5)
}

onMounted(async () => {
  window.addEventListener('keydown', onKeydown)

  // Load background image intrinsic size for aspect-correct placement
  const img = new Image()
  img.onload = () => { bgMeta.w = img.naturalWidth; bgMeta.h = img.naturalHeight; bgMeta.loaded = true; layoutBackground() }
  img.src = '/background.png'

  // d3 zoom
  zoom = d3.zoom()
    .filter(e => e.type === 'wheel' ? true : !drawMode.value) // block panning while drawing
    .scaleExtent([0.5, 50])
    .on('zoom', ({ transform }) => {
      d3.select('#viewport').attr('transform', transform)
      zoomK.value = transform.k
      updateLabels()
    })

  d3.select(svg.value).call(zoom)

  // drawings history
  loadFromLocal()
  if (history.value.length === 0) pushHistory()

  // markers (will call layoutBackground and then fit once)
  await reloadMarkers(false)
  updateLabels()

  // Initial fit fallback if markers empty & bg already known
  if (!initialFitted && bgMeta.loaded) {
    initialFitted = true
    fitToBBox(bgRect, 1.02)
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeydown)
})

/* Reactivity */
watch(groupFilters, (v) => {
  Object.keys(v).forEach(grp => filterGroup(grp))
}, { deep: true })
</script>

<style scoped>
html, body, #q-app { height: 100%; margin: 0; }
.full-page { display: flex; flex-direction: row; height: calc(100% - var(--q-header-height)); }

/* Sidebar */
.menu-column { width: 320px; overflow-y: auto; border-right: 1px solid var(--q-primary-1, #2a2a2a); background: #0d0d0d; color: #eaeaea; }
.menu-column-drawer { background: #0d0d0d; color: #eaeaea; }
.sidebar-content { background: #0d0d0d; color: #eaeaea; }
.menu-section { margin-bottom: 1rem; border-bottom: 1px solid #1f1f1f; }
.section-header { padding: 0.5rem 1rem; display: flex; align-items: center; font-weight: 600; }
.section-scroll { max-height: 180px; overflow-y: auto; padding: 0 0.5rem 0.5rem 0.5rem; }
.section-actions { padding: 0.5rem 1rem 1rem 1rem; }

@media (max-width: 1023px) {
  .menu-column {
    display: none;
  }
}

/* Map column is black to match background */
.map-column { flex: 1; position: relative; overflow: hidden; background: #000; }
.svg-container { width: 100%; height: calc(100% - 28px); position: relative; background: #000; }
.svg-container svg { position: absolute; inset: 0; width: 100%; height: 100%; background: #000; }

/* Tooltip on dark bg */
.tooltip {
  position: fixed; pointer-events: none;
  background: rgba(0, 0, 0, 0.9); color: #fff;
  padding: 6px 8px; border-radius: 4px; font-size: .8rem;
  white-space: nowrap; z-index: 1000; border: 1px solid rgba(255,255,255,0.08);
}

/* Labels */
.coord-label { fill: #bbb; font-size: 11px; user-select: none; }

/* Statusbar */
.statusbar {
  height: 28px; border-top: 1px solid #1f1f1f;
  background: #0d0d0d; color: #ddd;
}

/* FAB */
.fab { position: absolute; right: 16px; bottom: 16px; z-index: 5; }
.fab-mobile { bottom: 80px; }

/* Measure label */
.measure-label { paint-order: stroke; stroke: #000; stroke-width: 0.6; fill: #fff; }
</style>
