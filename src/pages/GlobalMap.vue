<template>
  <q-page class="fit q-pa-none">
    <!-- Desktop: split panel inside the page -->
    <q-splitter
      v-if="$q.screen.gt.sm"
      v-model="splitter"
      unit="px"
      :limits="[280, 520]"
      class="fit"
    >
      <template #before>
        <div class="panel">
          <MapSidebarContent
            :showBackground="showBackground"
            :bgOpacity="bgOpacity"
            :showGrid="showGrid"
            :gridOpacity="gridOpacity"
            :gridSize="gridSize"
            :gotoX="gotoX"
            :gotoY="gotoY"
            :groupFilters="groupFilters"
            :toggles="toggles"
            :drawMode="drawMode"
            :drawOptions="drawOptions"
            :drawColor="drawColor"
            :drawWidth="drawWidth"
            :snapToGrid="snapToGrid"
            :canUndo="canUndo"
            :canRedo="canRedo"
            @update:showBackground="val => showBackground = val"
            @update:bgOpacity="val => bgOpacity = val"
            @update:showGrid="val => showGrid = val"
            @update:gridOpacity="val => gridOpacity = val"
            @update:gridSize="val => gridSize = val"
            @update:gotoX="val => gotoX = val"
            @update:gotoY="val => gotoY = val"
            @center-on-coords="centerOnCoords"
            @toggle-all-markers="toggleAllMarkers"
            @filter-group="filterGroup"
            @select-group="selectGroup"
            @update:drawMode="val => drawMode = val"
            @update:drawColor="val => drawColor = val"
            @update:drawWidth="val => drawWidth = val"
            @update:snapToGrid="val => snapToGrid = val"
            @undo="undo"
            @redo="redo"
            @clear-drawings="clearDrawings"
            @export-drawings="exportDrawings"
            @import-drawings="importDrawings"
            @save-to-local="saveToLocal"
            @load-from-local="loadFromLocal"
          />
        </div>
      </template>

      <template #after>
        <div class="map-column">
          <div class="map-controls">
            <q-btn round color="primary" icon="add" @click="zoomBy(1.25)" size="sm" class="control-btn">
              <q-tooltip>Zoom In</q-tooltip>
            </q-btn>
            <q-btn round color="primary" icon="remove" @click="zoomBy(0.8)" size="sm" class="control-btn">
              <q-tooltip>Zoom Out</q-tooltip>
            </q-btn>
            <q-btn round color="secondary" icon="center_focus_strong" @click="resetView" size="sm" class="control-btn">
              <q-tooltip>Reset View</q-tooltip>
            </q-btn>
            <q-btn round color="secondary" icon="crop_free" @click="fitToContent" size="sm" class="control-btn">
              <q-tooltip>Fit to Map</q-tooltip>
            </q-btn>
            <q-btn
              round
              color="accent"
              icon="straighten"
              @click="drawMode='measure'"
              size="sm"
              class="control-btn"
              :class="{'active': drawMode === 'measure'}"
            >
              <q-tooltip>Measure</q-tooltip>
            </q-btn>
          </div>

          <div class="svg-container">
            <svg
              ref="svg"
              id="svgMap"
              preserveAspectRatio="xMidYMid meet"
              @contextmenu.prevent="onContextMenu"
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

              <g id="viewport">
                <rect x="-100000" y="-100000" width="200000" height="200000" fill="#000" />

                <image
                  id="bgImage"
                  :x="bgRect.x" :y="bgRect.y" :width="bgRect.width" :height="bgRect.height"
                  :style="{ display: showBackground ? 'block' : 'none', opacity: bgOpacity }"
                  href="/background.png"
                  preserveAspectRatio="none"
                />

                <rect
                  id="gridRect"
                  x="-100000" y="-100000" width="200000" height="200000"
                  :style="{ display: showGrid ? 'block' : 'none' }"
                  fill="url(#grid)"
                />

                <line x1="-20000" y1="0" x2="20000" y2="0" stroke="white" stroke-width="0.1" opacity="0.12"/>
                <line x1="0" y1="-20000" x2="0" y2="20000" stroke="white" stroke-width="0.1" opacity="0.12"/>

                <g ref="markersGroup" id="markersLayer" v-html="markers"></g>

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

                <g id="previewLayer" ref="previewLayer" style="pointer-events: none;"></g>
              </g>

              <g id="coordLabels">
                <text id="labelLeft"   text-anchor="end"    alignment-baseline="middle" class="coord-label"/>
                <text id="labelRight"  text-anchor="start"  alignment-baseline="middle" class="coord-label"/>
                <text id="labelTop"    text-anchor="middle" alignment-baseline="hanging" class="coord-label"/>
                <text id="labelBottom" text-anchor="middle" alignment-baseline="baseline" class="coord-label"/>
              </g>
            </svg>

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

            <q-inner-loading :showing="loading">
              <q-spinner color="primary" size="2em" />
            </q-inner-loading>

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
        </div>
      </template>
    </q-splitter>

    <!-- Mobile: show the map full screen, controls open as bottom sheet -->
    <div v-else class="map-column">
      <div class="map-controls">
        <q-btn round color="primary" icon="add" @click="zoomBy(1.25)" size="sm" class="control-btn">
          <q-tooltip>Zoom In</q-tooltip>
        </q-btn>
        <q-btn round color="primary" icon="remove" @click="zoomBy(0.8)" size="sm" class="control-btn">
          <q-tooltip>Zoom Out</q-tooltip>
        </q-btn>
        <q-btn round color="secondary" icon="center_focus_strong" @click="resetView" size="sm" class="control-btn">
          <q-tooltip>Reset View</q-tooltip>
        </q-btn>
        <q-btn round color="secondary" icon="crop_free" @click="fitToContent" size="sm" class="control-btn">
          <q-tooltip>Fit to Map</q-tooltip>
        </q-btn>
        <q-btn
          round
          color="accent"
          icon="straighten"
          @click="drawMode='measure'"
          size="sm"
          class="control-btn"
          :class="{'active': drawMode === 'measure'}"
        >
          <q-tooltip>Measure</q-tooltip>
        </q-btn>
      </div>

      <div class="svg-container">
        <svg
          ref="svg"
          id="svgMap"
          preserveAspectRatio="xMidYMid meet"
          @contextmenu.prevent="onContextMenu"
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

          <g id="viewport">
            <rect x="-100000" y="-100000" width="200000" height="200000" fill="#000" />

            <image
              id="bgImage"
              :x="bgRect.x" :y="bgRect.y" :width="bgRect.width" :height="bgRect.height"
              :style="{ display: showBackground ? 'block' : 'none', opacity: bgOpacity }"
              href="/background.png"
              preserveAspectRatio="none"
            />

            <rect
              id="gridRect"
              x="-100000" y="-100000" width="200000" height="200000"
              :style="{ display: showGrid ? 'block' : 'none' }"
              fill="url(#grid)"
            />

            <line x1="-20000" y1="0" x2="20000" y2="0" stroke="white" stroke-width="0.1" opacity="0.12"/>
            <line x1="0" y1="-20000" x2="0" y2="20000" stroke="white" stroke-width="0.1" opacity="0.12"/>

            <g ref="markersGroup" id="markersLayer" v-html="markers"></g>

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

            <g id="previewLayer" ref="previewLayer" style="pointer-events: none;"></g>
          </g>

          <g id="coordLabels">
            <text id="labelLeft"   text-anchor="end"    alignment-baseline="middle" class="coord-label"/>
            <text id="labelRight"  text-anchor="start"  alignment-baseline="middle" class="coord-label"/>
            <text id="labelTop"    text-anchor="middle" alignment-baseline="hanging" class="coord-label"/>
            <text id="labelBottom" text-anchor="middle" alignment-baseline="baseline" class="coord-label"/>
          </g>
        </svg>

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
    </div>

    <!-- Mobile menu button -->
    <q-btn
      v-if="$q.screen.lt.md"
      round
      color="primary"
      icon="menu"
      class="fixed-top-left q-ma-md"
      style="z-index: 2000"
      @click="mobileSidebarOpen = true"
    />

    <!-- Mobile Bottom Sheet -->
    <q-dialog
      v-if="$q.screen.lt.md"
      v-model="mobileSidebarOpen"
      position="bottom"
      full-width
      :maximized="$q.screen.lt.sm"
      transition-show="slide-up"
      transition-hide="slide-down"
    >
      <q-card class="bg-dark text-white" :style="$q.screen.lt.sm ? 'height: 90vh;' : 'min-height: 70vh; max-height: 90vh;'">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Map Controls</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section class="q-pt-none">
          <MapSidebarContent
            :showBackground="showBackground"
            :bgOpacity="bgOpacity"
            :showGrid="showGrid"
            :gridOpacity="gridOpacity"
            :gridSize="gridSize"
            :gotoX="gotoX"
            :gotoY="gotoY"
            :groupFilters="groupFilters"
            :toggles="toggles"
            :drawMode="drawMode"
            :drawOptions="drawOptions"
            :drawColor="drawColor"
            :drawWidth="drawWidth"
            :snapToGrid="snapToGrid"
            :canUndo="canUndo"
            :canRedo="canRedo"
            @update:showBackground="val => showBackground = val"
            @update:bgOpacity="val => bgOpacity = val"
            @update:showGrid="val => showGrid = val"
            @update:gridOpacity="val => gridOpacity = val"
            @update:gridSize="val => gridSize = val"
            @update:gotoX="val => gotoX = val"
            @update:gotoY="val => gotoY = val"
            @center-on-coords="centerOnCoords"
            @toggle-all-markers="toggleAllMarkers"
            @filter-group="filterGroup"
            @select-group="selectGroup"
            @update:drawMode="val => drawMode = val"
            @update:drawColor="val => drawColor = val"
            @update:drawWidth="val => drawWidth = val"
            @update:snapToGrid="val => snapToGrid = val"
            @undo="undo"
            @redo="redo"
            @clear-drawings="clearDrawings"
            @export-drawings="exportDrawings"
            @import-drawings="importDrawings"
            @save-to-local="saveToLocal"
            @load-from-local="loadFromLocal"
          />
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- PLAYER PROFILE DIALOG -->
    <q-dialog v-model="profileDialog">
      <q-card style="min-width: 500px; max-width: 800px">
        <q-card-section class="row items-center q-pb-sm">
          <div class="text-h6">Player: {{ profileData.name }}</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section class="q-pt-none">
          <div v-if="profileData.alliance" class="text-subtitle1">
            Alliance: {{ profileData.alliance.name }} ({{ profileData.alliance.rank }})
          </div>
          <div class="text-subtitle1">Villages: {{ profileData.villages?.length || 0 }}</div>
          <div class="text-subtitle1">Points: {{ profileData.points?.toLocaleString() || 0 }}</div>
          <div class="text-subtitle1">Rank: {{ profileData.rank || 'N/A' }}</div>
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- Context Menu -->
    <q-menu
      v-model="showContextMenu"
      context-menu
      touch-position
      :style="{ left: `${contextPosition.x}px`, top: `${contextPosition.y}px` }"
      class="context-menu"
      @before-show="onBeforeContextMenuShow"
      @hide="onContextMenuHide"
    >
      <q-list>
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

        <q-item clickable v-close-popup @click="resetView">
          <q-item-section avatar><q-icon name="refresh" /></q-item-section>
          <q-item-section>Reset view</q-item-section>
        </q-item>
      </q-list>
    </q-menu>
  </q-page>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount, computed, nextTick, watch } from 'vue';
import { useQuasar } from 'quasar';
import * as d3 from 'd3';
import { api } from 'boot/axios';
import MapSidebarContent from 'src/components/MapSidebarContent.vue';

/* === State === */
const $q = useQuasar()
const loading = ref(false)

// Initialize Quasar plugins if not already done
if (!window.Quasar) {
  window.Quasar = { notify: $q.notify };
}
const splitter = ref(320);
const mobileSidebarOpen = ref(false);
let handleCheckboxChange = null;

/** Map & zoom */
const svg = ref(null);
const markersGroup = ref(null);
const previewLayer = ref(null);
let zoom; // d3 zoom instance
const zoomK = ref(1);
const cursor = ref({ x: 0, y: 0 });
const gotoX = ref(0);
const gotoY = ref(0);

/** Layers */
const showBackground = ref(true);
const bgOpacity = ref(0.6);
const showGrid = ref(true);
const gridOpacity = ref(0.35);
const gridSize = ref(2);

/** Markers & filters */
const markers = ref('');
const toggles = ref({ alliances: '', tribes: '' });
const groupRefs = { alliances: null, tribes: null };
const groupFilters = ref({ alliances: '', tribes: '' });
let masterVisible = true;

/** Background image metrics */
const bgMeta = reactive({ w: 0, h: 0, loaded: false });
const bgRect = reactive({ x: -400, y: -400, width: 800, height: 800 });
let initialFitted = false;

/** Tooltip */
const tooltip = ref({ show: false, x: 0, y: 0, content: '' });

/* === Context Menu === */
const showContextMenu = ref(false);
const contextPosition = ref({ x: 0, y: 0 });
const ctx = reactive({
  point: null,
  hasMarker: false,
  marker: null
});

function onBeforeContextMenuShow() {
  document.addEventListener('click', handleClickOutside);
}

function onContextMenuHide() {
  document.removeEventListener('click', handleClickOutside);
}

function handleClickOutside(event) {
  if (showContextMenu.value && !event.target.closest('.q-menu')) {
    showContextMenu.value = false;
  }
}



const getTravianMapLink = computed(() => {
  if (!ctx.point) return '#';
  const x = Math.round(ctx.point.x);
  const y = Math.round(-ctx.point.y);
  return `https://${$q.cookies.get('server') || 'ts1.x1.europe'}.travian.com/karte.php?x=${x}&y=${y}`;
});

/** Player dialog */
const profileDialog = ref(false);
const profileData = ref({ name: '', alliance: null, villages: [], points: 0, rank: null });

/** Drawing */
const drawMode = ref(null);
const drawOptions = [
  { label: 'Off', value: null },
  { label: 'Line', value: 'line' },
  { label: 'Rect', value: 'rect' },
  { label: 'Circle', value: 'circle' },
  { label: 'Freehand', value: 'path' },
  { label: 'Text', value: 'text' },
  { label: 'Measure', value: 'measure' }
];
const drawColor = ref('#ff0000');
const drawWidth = ref(2);
const snapToGrid = ref(false);
const drawings = ref([]);
const history = ref([]);
const historyIndex = ref(-1);
const canUndo = computed(() => historyIndex.value > 0);
const canRedo = computed(() => Boolean(history.value.length && historyIndex.value < history.value.length - 1));

/* === Utils === */
const capitalize = (s) => s.charAt(0).toUpperCase() + s.slice(1);

function pushHistory() {
  history.value = history.value.slice(0, historyIndex.value + 1);
  history.value.push(JSON.parse(JSON.stringify(drawings.value)));
  historyIndex.value = history.value.length - 1;
}

function undo() {
  if (canUndo.value) {
    historyIndex.value--;
    drawings.value = JSON.parse(JSON.stringify(history.value[historyIndex.value]));
  }
}

function redo() {
  if (canRedo.value) {
    historyIndex.value++;
    drawings.value = JSON.parse(JSON.stringify(history.value[historyIndex.value]));
  }
}

function clearDrawings() {
  drawings.value = [];
  pushHistory();
  saveToLocal();
}

function saveToLocal() {
  localStorage.setItem('drawings', JSON.stringify(drawings.value));
}

function loadFromLocal() {
  const raw = localStorage.getItem('drawings');
  if (raw) {
    drawings.value = JSON.parse(raw);
    pushHistory();
  }
}

function exportDrawings() {
  const dataStr = JSON.stringify(drawings.value, null, 2);
  const dataBlob = new Blob([dataStr], { type: 'application/json' });
  const url = URL.createObjectURL(dataBlob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `drawings-${Date.now()}.json`;
  link.click();
  URL.revokeObjectURL(url);
}

function importDrawings() {
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = 'application/json';
  input.onchange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        try {
          drawings.value = JSON.parse(event.target.result);
          pushHistory();
          saveToLocal();
        } catch (err) {
          console.error('Failed to import drawings:', err);
        }
      };
      reader.readAsText(file);
    }
  };
  input.click();
}

/* === Marker Management === */
// Fit the map to show all content
function fitToContent() {
  if (!svg.value || !zoom) return;
  const mbox = markersBBoxOrDefault();
  const bbox = unionBBox(mbox, bgRect);
  fitToBBox(bbox, 1.02);
}

/* === Marker loading === */
const CACHE_KEY = 'markersCache';
const CACHE_TTL = 15 * 60 * 1000; // 15 minutes

async function reloadMarkers(force = false) {
  loading.value = true;
  try {
    let payload = null;
    if (!force) {
      try {
        const raw = localStorage.getItem(CACHE_KEY);
        if (raw) {
          const { at, data } = JSON.parse(raw);
          if (Date.now() - at < CACHE_TTL) payload = data;
        }
      } catch (e) {
        console.warn('Failed to parse cache:', e);
        localStorage.removeItem(CACHE_KEY);
      }
    }
    if (!payload) {
      try {
        const { data } = await api.get('/api/markers');
        if (!data) {
          console.error('API returned empty data');
          return;
        }
        payload = data;
        localStorage.setItem(CACHE_KEY, JSON.stringify({ at: Date.now(), data }));
      } catch (error) {
        console.error('Failed to load markers from API:', error);
        // Try to use cached data even if expired
        try {
          const raw = localStorage.getItem(CACHE_KEY);
          if (raw) {
            const { data } = JSON.parse(raw);
            payload = data;
            console.warn('Using expired cache due to API error');
          }
        } catch (e) {
          console.error('No valid cache available:', e);
        }
        if (!payload) {
          throw error;
        }
      }
    }
    
    if (!payload) {
      console.error('No markers data available');
      markers.value = '';
      toggles.value = { alliances: '', tribes: '' };
      return;
    }
    
    markers.value = payload?.markers || '';
    toggles.value = {
      alliances: payload?.alliance_checkboxes || '',
      tribes: payload?.tribe_checkboxes || ''
    };
    
    if (!markers.value) {
      console.warn('Markers data is empty. Payload:', payload);
    }
    
    await nextTick();
    

    
    // Marker events via delegation
    bindMarkerEvents();
    
    updateMarkersVisibility();
    layoutBackground();
  } catch (error) {
    console.error('Error loading markers:', error);
    markers.value = '';
    toggles.value = { alliances: '', tribes: '' };
  } finally {
    loading.value = false;
  }
}

/* === Marker filtering === */
const elementText = (el) => (el.textContent || '').toLowerCase();

async function filterGroup(group) {
  await nextTick();
  // Find the group container in the DOM (it's in MapSidebarContent)
  const containers = document.querySelectorAll('.section-scroll');
  let root = null;
  for (const container of containers) {
    if (container.innerHTML.includes(`toggle${capitalize(group.slice(0, -1))}`)) {
      root = container;
      break;
    }
  }
  if (!root) return;
  const term = (groupFilters.value[group] || '').toLowerCase().trim();
  Array.from(root.querySelectorAll('label, .q-checkbox, .q-option, div, span')).forEach(el => {
    const match = term === '' || elementText(el).includes(term);
    el.style.display = match ? '' : 'none';
  });
}

async function selectGroup(group, mode) {
  await nextTick();
  const checkboxClass = `${group.slice(0, -1)}-checkbox`;
  const boxes = document.querySelectorAll(`.${checkboxClass}`);
  boxes.forEach(cb => {
    if (mode === 'all') cb.checked = true;
    else if (mode === 'none') cb.checked = false;
    else cb.checked = !cb.checked;
  });
  updateMarkersVisibility();
}

function toggleAllMarkers() {
  masterVisible = !masterVisible;
  updateMarkersVisibility();
}

function bindMarkerEvents() {
  const root = markersGroup.value;
  if (!root) return;
  
  root.onpointerover = (e) => {
    const el = e.target.closest('.marker');
    if (!el) return;
    const tip = el.getAttribute('data-tooltip') || '';
    const content = sanitize(tip.replace(/<br>/g, '<br/>'));
    tooltip.value = { show: true, x: e.clientX + 8, y: e.clientY + 8, content };
  };
  
  root.onpointerout = (e) => {
    if (e.relatedTarget && e.currentTarget.contains(e.relatedTarget)) return;
    hideTooltip();
  };
  
  root.onclick = async (e) => {
    const el = e.target.closest('.marker');
    if (!el) return;
    let owner = (el.getAttribute('data-player') || '').replace(/^'+|'+$/g, '');
    if (owner) {
      try {
        const { data } = await api.get(`/api/player/${encodeURIComponent(owner)}/villages`);
        profileData.value = {
          name: data.player || owner,
          alliance: data.alliance || null,
          villages: data.villages || [],
          points: data.points || 0,
          rank: data.rank || null
        };
        profileDialog.value = true;
      } catch (err) {
        console.error('Failed to load player data:', err);
      }
    }
  };
}

function getClassValue(el, prefix) {
  const c = Array.from(el.classList).find(x => x.startsWith(prefix));
  return c ? c.slice(prefix.length) : '';
}

function updateMarkersVisibility() {
  if (!markersGroup.value) return;
  const groupCheck = (type, val) => {
    const checkbox = document.getElementById(`toggle${capitalize(type)}-${val}`);
    return checkbox ? checkbox.checked !== false : true;
  };
  
  markersGroup.value.querySelectorAll('.marker').forEach(node => {
    const alliance = getClassValue(node, 'alliance-');
    const region = getClassValue(node, 'region-');
    const tribe = getClassValue(node, 'tribe-');
    const on =
      masterVisible &&
      (alliance ? groupCheck('Alliance', alliance) : true) &&
      (region ? groupCheck('Region', region) : true) &&
      (tribe ? groupCheck('Tribe', tribe) : true);
    node.style.display = on ? 'block' : 'none';
  });
}

function sanitize(html) {
  try {
    if (window.DOMPurify?.sanitize) {
      return window.DOMPurify.sanitize(html, { USE_PROFILES: { html: true, svg: true } });
    }
  } catch {}
  return String(html).replace(/<script[\s\S]*?>[\s\S]*?<\/script>/gi, '');
}

const DEFAULT_WORLD = { x: -400, y: -400, width: 800, height: 800 };

function markersBBoxOrDefault() {
  const g = markersGroup.value;
  if (g) {
    const bb = g.getBBox();
    if (bb.width > 0 && bb.height > 0) return bb;
  }
  return { ...DEFAULT_WORLD };
}

function unionBBox(a, b) {
  const x = Math.min(a.x, b.x);
  const y = Math.min(a.y, b.y);
  const x2 = Math.max(a.x + a.width, b.x + b.width);
  const y2 = Math.max(a.y + a.height, b.y + b.height);
  return { x, y, width: x2 - x, height: y2 - y };
}

function fitToBBox(bbox, pad = 1.0) {
  if (!bbox || bbox.width <= 0 || bbox.height <= 0) return;
  if (!svg.value || !zoom) return;

  syncZoomExtents();

  const rect = svg.value.getBoundingClientRect();
  const k = Math.min(rect.width / (bbox.width * pad), rect.height / (bbox.height * pad));
  centerAt(bbox.x + bbox.width / 2, bbox.y + bbox.height / 2, k);
}


function centerAt(x, y, k = d3.zoomTransform(svg.value).k) {
  if (!svg.value || !zoom) return;

  syncZoomExtents();

  const rect = svg.value.getBoundingClientRect();
  const tx = rect.width / 2 - k * x;
  const ty = rect.height / 2 - k * y;
  const t = d3.zoomIdentity.translate(tx, ty).scale(k);
  d3.select(svg.value).transition().duration(250).call(zoom.transform, t);
}


function layoutBackground() {
  if (!bgMeta.loaded || bgMeta.w === 0 || bgMeta.h === 0) return;
  const target = markersBBoxOrDefault();
  const rImg = bgMeta.w / bgMeta.h;
  const rBox = target.width / target.height;
  
  if (rImg >= rBox) {
    const height = target.height;
    const width = height * rImg;
    const x = target.x + (target.width - width) / 2;
    const y = target.y;
    Object.assign(bgRect, { x, y, width, height });
  } else {
    const width = target.width;
    const height = width / rImg;
    const x = target.x;
    const y = target.y + (target.height - height) / 2;
    Object.assign(bgRect, { x, y, width, height });
  }
  
  if (!initialFitted) {
    initialFitted = true;
    const all = unionBBox(markersBBoxOrDefault(), bgRect);
    fitToBBox(all, 1.02);
  }
}

/* === Zoom helpers === */
function zoomBy(factor) {
  if (svg.value && zoom) {
    d3.select(svg.value).transition().duration(200).call(zoom.scaleBy, factor);
  }
}

function resetView() {
  fitToContent();
}

function centerOnCoords() {
  const [x, y] = [Number(gotoX.value) || 0, Number(gotoY.value) || 0];
  centerAt(x, y);
}

const handleResize = () => {
  if (!svg.value || !zoom) return;

  const rect = svg.value.getBoundingClientRect();
  if (!rect || rect.width <= 0 || rect.height <= 0) return;

  syncZoomExtents();

  const t = d3.zoomTransform(svg.value);
  if (!Number.isFinite(t.x) || !Number.isFinite(t.y) || !Number.isFinite(t.k)) return;

  d3.select(svg.value).call(zoom.transform, t);
};




function onContextMenu(e) {
  e.preventDefault();
  const el = e.target.closest('.marker');
  ctx.hasMarker = !!el;
  ctx.marker = el;
  
  if (el) {
    const bb = el.getBBox();
    ctx.point = { x: bb.x + bb.width / 2, y: bb.y + bb.height / 2 };
  } else {
    const rect = svg.value.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const transform = d3.zoomTransform(svg.value);
    ctx.point = {
      x: (x - transform.x) / transform.k,
      y: (y - transform.y) / transform.k
    };
  }
  
  // Set context menu position and show it
  contextPosition.value = { x: e.clientX, y: e.clientY };
  showContextMenu.value = true;
  
  // Prevent any zoom behavior
  if (e.type === 'dblclick') {
    e.stopPropagation();
    return false;
  }
  
  return false;
}



function copyCoordinates() {
if (!ctx.point) return;
const x = Math.round(ctx.point.x);
const y = Math.round(ctx.point.y);
const coordText = `${x}|${y}`;
navigator.clipboard.writeText(coordText).then(() => {
$q.notify({
message: 'Coordinates copied to clipboard!',
color: 'positive',
position: 'top',
timeout: 1000
});
});
}

const startMeasuring = () => {
if (!ctx.point) return;
drawMode.value = 'measure';
const point = ctx.point;

// Clear any existing preview
previewLayer.value.innerHTML = '';

// Create a preview line
const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
line.setAttribute('x1', point.x);
line.setAttribute('y1', point.y);
line.setAttribute('x2', point.x);
line.setAttribute('y2', point.y);
line.setAttribute('stroke', 'red');
line.setAttribute('stroke-width', '0.1');
line.setAttribute('stroke-dasharray', '0.2,0.2');

previewLayer.value.appendChild(line);

// Update the preview on mouse move
const onMouseMove = (e) => {
const pt = toMapCoords(e);
line.setAttribute('x2', pt.x);
line.setAttribute('y2', pt.y);
};

// Clean up on next click
const onClick = (e) => {
svg.value.removeEventListener('mousemove', onMouseMove);
svg.value.removeEventListener('click', onClick);
previewLayer.value.removeChild(line);
drawMode.value = null;
};

svg.value.addEventListener('mousemove', onMouseMove);
svg.value.addEventListener('click', onClick, { once: true });
};

const addMarkerAtPoint = () => {
if (!ctx.point) return;

// You can customize this to show a dialog for marker details
$q.dialog({
title: 'Add Marker',
message: 'Enter marker name:',
prompt: {
model: '',
type: 'text',
isValid: val => val.length > 0,
label: 'Marker name',
hint: 'Enter a name for this marker'
},
cancel: true,
persistent: true
}).onOk(name => {
// Here you would typically add the marker to your markers array
// and save it to your backend or local storage
$q.notify({
message: `Marker "${name}" added at (${Math.round(ctx.point.x)}|${Math.round(ctx.point.y)})`,
color: 'positive',
position: 'top',
timeout: 2000
});

// TODO: Add the actual marker to your markers array and save it
// This is a placeholder for the actual implementation
});
};

const showVillageInfo = () => {
if (!ctx.hasMarker || !ctx.marker) return;

// Extract village info from the marker
const villageInfo = {
name: ctx.marker.getAttribute('data-name') || 'Unknown Village',
x: Math.round(parseFloat(ctx.marker.getAttribute('data-x'))),
y: Math.round(parseFloat(ctx.marker.getAttribute('data-y'))),
// Add more info as needed from your marker data attributes
};

$q.dialog({
title: 'Village Information',
message: `
<div class="text-h6">${villageInfo.name}</div>
<div>Coordinates: ${villageInfo.x}|${villageInfo.y}</div>
<div>Player: ${ctx.marker.getAttribute('data-player') || 'Unknown'}</div>
<div>Alliance: ${ctx.marker.getAttribute('data-alliance') || 'None'}</div>
`,
html: true,
style: 'min-width: 300px;',
ok: {
label: 'Close',
flat: true
},
cancel: false
});
};

/* === Pointer handlers === */
let previewElem = null;
let anchor = null;
let isDrawing = false;

function toMapCoords(evt) {
  if (!svg.value) return { x: 0, y: 0 };
  const [sx, sy] = d3.pointer(evt, svg.value);
  const t = d3.zoomTransform(svg.value);
  return { x: t.invertX(sx), y: t.invertY(sy) };
}

const snap = (v) => (snapToGrid.value ? Math.round(v / gridSize.value) * gridSize.value : v);

function applyPreviewStyle(el) {
  el.setAttribute('stroke', drawColor.value);
  el.setAttribute('stroke-width', drawWidth.value);
  if (['rect', 'circle'].includes(drawMode.value)) el.setAttribute('fill', drawColor.value + '33');
  else el.setAttribute('fill', 'none');
  if (el.tagName === 'path') {
    el.setAttribute('stroke-linecap', 'round');
    el.setAttribute('stroke-linejoin', 'round');
  }
}

function onPointerDown(evt) {
  const p = toMapCoords(evt);
  cursor.value = p;
  
  if (!drawMode.value) return;
  evt.preventDefault();
  
  const pt = { x: snap(p.x), y: snap(p.y) };
  
  if (drawMode.value === 'text') {
    const txt = prompt('Enter text:');
    if (txt) {
      drawings.value.push({
        type: 'text', x: pt.x, y: pt.y, text: txt,
        style: { stroke: drawColor.value, 'stroke-width': drawWidth.value, fill: 'none' }
      });
      pushHistory(); saveToLocal();
    }
    return;
  }
  
  if (drawMode.value === 'measure') {
    if (!anchor) { anchor = pt; isDrawing = true } else {
      const dist = Math.hypot(pt.x - anchor.x, pt.y - anchor.y);
      drawings.value.push({
        type: 'measure',
        x1: anchor.x, y1: anchor.y, x2: pt.x, y2: pt.y,
        distance: dist,
        style: { stroke: '#00bcd4', 'stroke-width': 1.5, 'stroke-dasharray': '2 2', fill: 'none' }
      });
      pushHistory(); saveToLocal();
      anchor = null; isDrawing = false;
      if (previewElem) { previewLayer.value.removeChild(previewElem); previewElem = null }
    }
    return;
  }
  
  isDrawing = true;
  anchor = pt;
  const ns = 'http://www.w3.org/2000/svg';
  if (drawMode.value === 'line') {
    previewElem = document.createElementNS(ns, 'line');
    previewElem.setAttribute('x1', pt.x);
    previewElem.setAttribute('y1', pt.y);
    previewElem.setAttribute('x2', pt.x);
    previewElem.setAttribute('y2', pt.y);
  } else if (drawMode.value === 'rect') {
    previewElem = document.createElementNS(ns, 'rect');
    previewElem.setAttribute('x', pt.x);
    previewElem.setAttribute('y', pt.y);
    previewElem.setAttribute('width', 0);
    previewElem.setAttribute('height', 0);
  } else if (drawMode.value === 'circle') {
    previewElem = document.createElementNS(ns, 'circle');
    previewElem.setAttribute('cx', pt.x);
    previewElem.setAttribute('cy', pt.y);
    previewElem.setAttribute('r', 0);
  } else if (drawMode.value === 'path') {
    previewElem = document.createElementNS(ns, 'path');
    previewElem.setAttribute('d', `M${pt.x},${pt.y}`);
  }
  applyPreviewStyle(previewElem);
  previewLayer.value.appendChild(previewElem);
}

function onPointerMove(evt) {
  const p = toMapCoords(evt);
  cursor.value = p;
  
  if (!isDrawing || !previewElem) return;
  evt.preventDefault();
  const pt = { x: snap(p.x), y: snap(p.y) };
  
  switch (drawMode.value) {
    case 'line':
      previewElem.setAttribute('x2', pt.x);
      previewElem.setAttribute('y2', pt.y);
      break;
    case 'rect': {
      const x = Math.min(anchor.x, pt.x); const y = Math.min(anchor.y, pt.y);
      const w = Math.abs(pt.x - anchor.x); const h = Math.abs(pt.y - anchor.y);
      previewElem.setAttribute('x', x); previewElem.setAttribute('y', y);
      previewElem.setAttribute('width', w); previewElem.setAttribute('height', h);
      break;
    }
    case 'circle': {
      const r = Math.hypot(pt.x - anchor.x, pt.y - anchor.y);
      previewElem.setAttribute('r', r);
      break;
    }
    case 'path': {
      const d = previewElem.getAttribute('d') + ` L${pt.x},${pt.y}`;
      previewElem.setAttribute('d', d);
      break;
    }
    case 'measure': {
      previewElem?.remove();
      const ns = 'http://www.w3.org/2000/svg';
      previewElem = document.createElementNS(ns, 'line');
      previewElem.setAttribute('x1', anchor.x);
      previewElem.setAttribute('y1', anchor.y);
      previewElem.setAttribute('x2', pt.x);
      previewElem.setAttribute('y2', pt.y);
      previewElem.setAttribute('stroke', '#00bcd4');
      previewElem.setAttribute('stroke-width', 1);
      previewElem.setAttribute('stroke-dasharray', '2 2');
      previewElem.setAttribute('fill', 'none');
      previewLayer.value.appendChild(previewElem);
      break;
    }
  }
}

function onPointerUp(evt) {
  if (!isDrawing || !previewElem || drawMode.value === 'measure') return;
  evt.preventDefault();
  const finalize = (shape) => { drawings.value.push(shape); pushHistory(); saveToLocal() };
  const color = drawColor.value; const width = drawWidth.value;
  
  if (drawMode.value === 'line') {
    finalize({
      type: 'line',
      x1: +previewElem.getAttribute('x1'), y1: +previewElem.getAttribute('y1'),
      x2: +previewElem.getAttribute('x2'), y2: +previewElem.getAttribute('y2'),
      style: { stroke: color, 'stroke-width': width, fill: 'none' }
    });
  } else if (drawMode.value === 'rect') {
    finalize({
      type: 'rect',
      x: +previewElem.getAttribute('x'), y: +previewElem.getAttribute('y'),
      width: +previewElem.getAttribute('width'), height: +previewElem.getAttribute('height'),
      style: { stroke: color, 'stroke-width': width, fill: color + '33' }
    });
  } else if (drawMode.value === 'circle') {
    finalize({
      type: 'circle',
      cx: +previewElem.getAttribute('cx'), cy: +previewElem.getAttribute('cy'),
      r: +previewElem.getAttribute('r'),
      style: { stroke: color, 'stroke-width': width, fill: color + '33' }
    });
  } else if (drawMode.value === 'path') {
    finalize({
      type: 'path',
      d: previewElem.getAttribute('d'),
      style: { stroke: color, 'stroke-width': width, fill: 'none', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }
    });
  }
  
  previewLayer.value.removeChild(previewElem);
  previewElem = null;
  isDrawing = false;
  anchor = null;
}

function onKeydown(evt) {
  if ((evt.ctrlKey || evt.metaKey) && !evt.shiftKey && evt.key === 'z') { undo(); evt.preventDefault(); }
  else if ((evt.ctrlKey || evt.metaKey) && (evt.key === 'y' || (evt.shiftKey && evt.key === 'Z'))) { redo(); evt.preventDefault(); }
  else if (evt.key === 'Escape') {
    drawMode.value = null;
    previewElem?.remove(); previewElem = null;
    isDrawing = false; anchor = null;
  }
}



function centerOnContext() {
  if (!ctx.value?.point) return;
  centerAt(ctx.value.point.x, ctx.value.point.y);
}


function hideTooltip() {
  tooltip.value.show = false;
}


function syncZoomExtents() {
  if (!svg.value || !zoom) return;

  const r = svg.value.getBoundingClientRect();
  if (!r || r.width <= 0 || r.height <= 0) return;

  // Tell D3 what the visible pixel extent is (prevents 0×0 extent bugs)
  zoom.extent([[0, 0], [r.width, r.height]]);

  // Optional but recommended: keep panning bounded to your huge world rect
  zoom.translateExtent([[-100000, -100000], [100000, 100000]]);
}


/* === Lifecycle === */
onMounted(async () => {
  window.addEventListener('keydown', onKeydown);
  await nextTick();
  
  if (svg.value) {
    // Initialize d3 zoom
    zoom = d3.zoom()
  .scaleExtent([0.1, 50])
  .on('zoom', (event) => {
    const { transform } = event;

    if (!Number.isFinite(transform.x) || !Number.isFinite(transform.y) || !Number.isFinite(transform.k)) return;

    d3.select(svg.value).select('#viewport').attr('transform', transform);
    zoomK.value = transform.k;
  });

syncZoomExtents();

d3.select(svg.value)
  .call(zoom)
  .on('dblclick.zoom', null);

    
    // Initial transform - center and scale to show content
    const svgRect = svg.value.getBoundingClientRect();
    if (svgRect.width > 0 && svgRect.height > 0) {
      const defaultScale = Math.min(svgRect.width, svgRect.height) / 2000;
      const initialTransform = d3.zoomIdentity
        .translate(svgRect.width / 2, svgRect.height / 2)
        .scale(defaultScale);
      d3.select(svg.value).call(zoom.transform, initialTransform);
    }
    
    window.addEventListener('resize', handleResize);
  }
  
  handleCheckboxChange = (e) => {
    const t = e.target;
    if (!t) return;
    if (
      t.classList.contains('alliance-checkbox') ||
      t.classList.contains('tribe-checkbox') ||
      t.classList.contains('region-checkbox') // if you have regions too
    ) {
      updateMarkersVisibility();
    }
  };
  document.addEventListener('change', handleCheckboxChange);


  // Load drawings
  loadFromLocal();
  if (history.value.length === 0) pushHistory();
  
  // Load markers
  await reloadMarkers();


// ---- DEBUG HOOKS (remove later) ----
window.__mapDbg = {
  get svg() { return svg.value; },
  get viewport() { return svg.value?.querySelector('#viewport'); },
  get markersLayer() { return svg.value?.querySelector('#markersLayer'); },
  get markersGroup() { return markersGroup.value; },
  get markersHtml() { return markers.value; },
  get zoomTransform() { return svg.value ? d3.zoomTransform(svg.value) : null; },
  fitToContent,
  syncZoomExtents,
  updateMarkersVisibility,
  reloadMarkers,
  dump() {
    const s = svg.value;
    const vp = s?.querySelector('#viewport');
    const ml = s?.querySelector('#markersLayer');
    const mg = markersGroup.value;

    console.log('--- MAP DBG ---');
    console.log('svg:', s);
    console.log('svg rect:', s?.getBoundingClientRect());
    console.log('viewport:', vp, 'transform attr:', vp?.getAttribute('transform'));
    console.log('d3 transform:', s ? d3.zoomTransform(s) : null);
    console.log('markers string length:', (markers.value || '').length);
    console.log('markersLayer children:', ml?.childNodes?.length, 'markersGroup children:', mg?.childNodes?.length);
    console.log('.marker count:', mg?.querySelectorAll?.('.marker')?.length);
    console.log('first 300 chars markers:', (markers.value || '').slice(0, 300));
    if (mg) {
      const bb = safeBBox(mg);
      console.log('markersGroup bbox:', bb);
    }
    console.log('--- END DBG ---');
  }
};

function safeBBox(node) {
  try { return node.getBBox(); } catch (e) { return { error: String(e) }; }
}


await nextTick();

// Wait 1 frame so splitter/layout settles (prevents 0×0 extent on first fit)
requestAnimationFrame(() => {
  syncZoomExtents();
  fitToContent();
});

  // Load background image
  const img = new Image();
  img.onload = () => {
    const w = img.naturalWidth;
    const h = img.naturalHeight;
    
    if (Number.isFinite(w) && Number.isFinite(h) && w > 0 && h > 0) {
      bgMeta.w = w;
      bgMeta.h = h;
      bgMeta.loaded = true;
      
      // Center in world coords
      bgRect.x = -w / 2;
      bgRect.y = -h / 2;
      bgRect.width = w;
      bgRect.height = h;
      
      // Layout background and fit
      layoutBackground();
      if (!initialFitted) {
        setTimeout(() => {
          fitToContent();
          initialFitted = true;
        }, 100);
      }
    }
  };
  img.onerror = () => {
    console.warn('Background image failed to load; using defaults');
    bgMeta.w = 800;
    bgMeta.h = 800;
    bgMeta.loaded = true;
    bgRect.x = -400;
    bgRect.y = -400;
    bgRect.width = 800;
    bgRect.height = 800;
    
    setTimeout(() => {
      fitToContent();
    }, 100);
  };
    // IMPORTANT: trigger load
    img.src = '/background.png';
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize);
  window.removeEventListener('keydown', onKeydown);
  if (handleCheckboxChange) {
    document.removeEventListener('change', handleCheckboxChange);
    handleCheckboxChange = null;
  }
});

// Watch for filter changes
watch(groupFilters, (v) => {
  Object.keys(v).forEach(grp => filterGroup(grp));
}, { deep: true });

</script>

<style scoped>

/* Force the q-page to have a real height */
.q-page {
  min-height: 100vh !important;
}

/* Force the splitter to have a real height */
.q-splitter.fit {
  height: 100vh !important;
}

/* Force the right panel (map) to have a real height */
.map-column {
  height: 100vh !important;
  min-height: 0 !important;
}

/* Force the svg container to take available height */
.svg-container {
  flex: 1;
  min-height: 0 !important;
}

/* Make the SVG fill it */
#svgMap {
  width: 100%;
  height: 100%;
  display: block;
}


.panel {
  height: 100%;
  overflow-y: auto;
  background: #0d0d0d;
  color: #eaeaea;
}

.map-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  background: #000;
  min-width: 0;
  overflow: hidden;
  height: 100%;
}

.map-controls {
  position: absolute;
  right: 20px;
  top: 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  z-index: 10000;
  background: rgba(13, 13, 13, 0.9);
  border-radius: 24px;
  padding: 12px 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.2);
  /* Force hardware acceleration */
  transform: translateZ(0);
  -webkit-transform: translateZ(0);
  -moz-transform: translateZ(0);
  -ms-transform: translateZ(0);
}

.map-controls .q-btn {
  margin: 0;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  width: 36px;
  height: 36px;
  font-size: 16px;
  transition: all 0.2s ease;
}

.map-controls .q-btn:hover {
  background: var(--q-primary);
  transform: scale(1.1);
}

.map-controls .q-btn i {
  font-size: 16px;
}

.map-controls .q-btn.active {
  background: var(--q-primary);
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.3);
}

/* Make sure tooltips are visible */
.map-controls .q-tooltip {
  font-size: 12px;
  padding: 4px 8px;
  background: rgba(0, 0, 0, 0.9);
  color: white;
  border-radius: 4px;
  pointer-events: none;
  z-index: 2000;
}

.svg-container { 
  flex: 1;
  width: 100%; 
  position: relative; 
  background: #000; 
  overflow: hidden;
  /* Ensure proper stacking context */
  z-index: 1;
}

.svg-container svg { 
  position: absolute; 
  top: 0;
  left: 0;
  width: 100%; 
  height: 100%; 
  background: #000; 
}

/* Tooltip on dark bg */
.tooltip {
  position: fixed;
  pointer-events: none;
  background: rgba(0, 0, 0, 0.9);
  color: #fff;
  padding: 6px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  white-space: nowrap;
  z-index: 1000;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

/* Labels */
.coord-label {
  fill: #bbb;
  font-size: 11px;
  user-select: none;
}

/* Statusbar */
.statusbar {
  height: 28px;
  border-top: 1px solid #1f1f1f;
  background: #0d0d0d;
  color: #ddd;
  display: flex;
  align-items: center;
  padding: 0 8px;
  flex-shrink: 0;
  position: relative;
  z-index: 2;
}

/* FAB */
.fab {
  position: absolute;
  right: 16px;
  bottom: 16px;
  z-index: 5;
}

.fab-mobile {
  bottom: 80px;
}

/* Measure label */
.measure-label {
  paint-order: stroke;
  stroke: #000;
  stroke-width: 0.6;
  fill: #fff;
}

/* Mobile adjustments */
@media (max-width: 599px) {
  .fab {
    right: 8px;
    bottom: 8px;
  }
  
  .fab-mobile {
    bottom: 72px;
  }
  
  .statusbar {
    font-size: 0.8rem;
  }
}

/* Ensure the drawer takes full height on mobile */
.q-drawer {
  height: 100vh !important;
  margin-top: 0 !important;
  will-change: transform;
}

/* Fix for Quasar drawer positioning */
.q-drawer-container {
  overflow: hidden;
  position: relative;
  height: 100%;
}

/* Ensure the map takes full available space */
#svgMap {
  width: 100%;
  height: 100%;
  display: block;
}

/* Fix for the mobile dialog */
.q-dialog__inner > div {
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

/* Ensure the map container doesn't scroll the page */
body.body--has-drawer {
  overflow: hidden;
}
</style>
