<!-- MainDashboard.vue (FULL integrated - all chart types + per-widget data sources wired to backend like other pages) -->
<template>
    <q-layout class="dashboard" view="hHh Lpr lFf">
      <q-header elevated class="dashboard__header">
        <q-toolbar class="q-px-md">
          <q-toolbar-title class="text-weight-medium">Dashboard</q-toolbar-title>
  
          <div class="row items-center q-gutter-sm dashboard__headerActions">
            <q-toggle v-model="isEditMode" label="Edit layout" dense />
            <q-btn dense outline icon="save" label="Save" :disable="!isEditMode" @click="saveLayout()" />
            <q-btn dense outline icon="restart_alt" label="Reset" @click="resetLayout()" />
          </div>
        </q-toolbar>
      </q-header>
  
      <q-page-container>
        <q-page class="dashboard__page">
          <!-- Floating palette -->
          <transition name="dash-palette">
            <div v-if="isEditMode" class="dashboard__paletteWrap">
              <q-card bordered class="dashboard__palette">
                <div class="row items-center q-px-sm q-pt-sm q-pb-xs">
                  <div class="text-subtitle2">Elements</div>
                  <q-space />
                  <q-btn dense flat round icon="close" class="text-grey-7" @click="isEditMode = false" />
                </div>
  
                <div class="q-px-sm q-pb-sm">
                  <q-input v-model="paletteQuery" dense outlined placeholder="Search…">
                    <template #prepend><q-icon name="search" /></template>
                  </q-input>
                  <div class="text-caption text-grey-7 q-mt-xs">Drag into the canvas</div>
                </div>
  
                <q-separator />
  
                <q-scroll-area class="dashboard__paletteScroll" @wheel.stop @touchmove.stop>
                  <div class="q-pa-sm">
                    <div class="dashboard__paletteGrid">
                      <div
                        v-for="p in filteredPalette"
                        :key="p.type"
                        class="dashboard__paletteItem grid-stack-item palette-item"
                        :data-type="p.type"
                        :gs-w="p.w"
                        :gs-h="p.h"
                        :gs-min-w="p.minW"
                        :gs-min-h="p.minH"
                        role="button"
                        tabindex="0"
                        @keydown.enter.prevent="addWidget(p.type)"
                        @click="addWidget(p.type)"
                        title="Drag into canvas (or click to add)"
                      >
                        <div class="grid-stack-item-content dashboard__paletteThumb">
                          <div class="dashboard__paletteThumbTop">
                            <q-icon :name="p.icon" size="18px" class="text-grey-8" />
                            <div class="text-body2 text-weight-medium">{{ p.label }}</div>
                          </div>
  
                          <div class="dashboard__palettePreview">
                            <div v-if="p.type === 'header'" class="ppPrev">
                              <div class="ppLine ppLine--w72" />
                              <div class="ppLine ppLine--w44" />
                            </div>
                            <div v-else-if="p.type === 'text'" class="ppPrev">
                              <div class="ppLine ppLine--w92" />
                              <div class="ppLine ppLine--w86" />
                              <div class="ppLine ppLine--w60" />
                              <div class="ppLine ppLine--w74" />
                            </div>
                            <div v-else class="ppPrev">
                              <svg viewBox="0 0 120 54" class="ppSvg">
                                <path
                                  d="M5 40 C 25 18, 35 50, 55 30 S 90 10, 115 22"
                                  class="ppStroke"
                                  fill="none"
                                />
                                <line x1="6" y1="46" x2="114" y2="46" class="ppAxis" />
                                <line x1="6" y1="8" x2="6" y2="46" class="ppAxis" />
                              </svg>
                            </div>
                          </div>
  
                          <div class="text-caption text-grey-6 q-mt-xs">{{ p.hint }}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </q-scroll-area>
              </q-card>
            </div>
          </transition>
  
          <transition name="drop-hint">
            <div v-if="isEditMode && isDraggingIn" class="dashboard__dropHint">Drop on the grid</div>
          </transition>
  
          <div v-if="isEditMode && showDesignGrid" class="dashboard__gridOverlay" :style="gridOverlayStyle" />
  
          <!-- Canvas -->
          <div
            ref="gridEl"
            class="grid-stack dashboard__grid"
            :class="{ 'is-edit': isEditMode, 'drop-armed': isEditMode && isDraggingIn }"
          >
            <div
              v-for="w in widgets"
              :key="w.id"
              class="grid-stack-item"
              :class="{ 'cell-outline': isEditMode && showCellOutlines }"
              :gs-id="w.id"
              :gs-x="w.x"
              :gs-y="w.y"
              :gs-w="w.w"
              :gs-h="w.h"
              :gs-min-w="w.minW ?? 8"
              :gs-min-h="w.minH ?? 2"
            >
              <div class="grid-stack-item-content dashboard__itemContent">
                <q-card flat bordered class="dashboard__card">
                  <q-card-section class="dashboard__cardHeader">
                    <div class="row items-center no-wrap" style="min-width: 0; flex: 1;">
                      <div class="text-subtitle1 ellipsis">
                        <template v-if="isEditMode && isDesignBlock(w)">
                          <q-input v-model="w.title" dense borderless class="dashboard__titleInput" placeholder="Title" />
                        </template>
                        <template v-else>
                          {{ w.title }}
                        </template>
                      </div>
                    </div>
  
                    <q-space />
  
                    <div class="row items-center q-gutter-xs">
                      <q-btn
                        dense
                        flat
                        round
                        icon="tune"
                        class="text-grey-7"
                        @mousedown.stop
                        @touchstart.stop
                        @click.stop="openWidgetCustomizer(w.id)"
                      >
                        <q-tooltip>Customize</q-tooltip>
                      </q-btn>
  
                      <template v-if="isEditMode">
                        <q-btn
                          dense
                          flat
                          round
                          icon="delete"
                          class="text-grey-7"
                          @mousedown.stop
                          @touchstart.stop
                          @click.stop="removeWidget(w.id)"
                        >
                          <q-tooltip>Remove</q-tooltip>
                        </q-btn>
                        <q-icon name="open_with" size="18px" class="text-grey-7" />
                      </template>
                    </div>
                  </q-card-section>
  
                  <q-separator />
  
                  <q-card-section class="dashboard__cardBody">
                    <div class="dashboard__cardBodyInner">
                      <div v-if="isChartWidget(w)" class="dashboard__runtimeWrap">
                        <div v-if="runtimeFor(w.id).error" class="dashboard__runtimeError">
                          <q-icon name="error_outline" class="q-mr-sm" />
                          <span class="text-body2">{{ runtimeFor(w.id).error }}</span>
                          <q-space />
                          <q-btn dense flat icon="refresh" label="Retry" @click="refreshWidget(w)" />
                        </div>
  
                        <component :is="widgetComponents[w.type]" v-bind="getWidgetProps(w)" />
  
                        <q-inner-loading :showing="runtimeFor(w.id).loading">
                          <q-spinner size="34px" />
                        </q-inner-loading>
                      </div>
  
                      <component v-else :is="widgetComponents[w.type]" v-bind="getWidgetProps(w)" />
                    </div>
                  </q-card-section>
                </q-card>
              </div>
            </div>
          </div>
  
          <!-- Per-widget customizer -->
          <q-dialog v-model="customizeOpen" persistent>
            <q-card style="width: 720px; max-width: 92vw;">
              <q-card-section class="row items-center no-wrap">
                <div class="text-subtitle1 ellipsis">Customize: {{ customizeWidget?.title || 'Widget' }}</div>
                <q-space />
                <q-btn dense flat round icon="close" @click="closeCustomizer" />
              </q-card-section>
  
              <q-separator />
  
              <q-card-section class="q-gutter-md">
                <template v-if="customizeWidget && isChartWidget(customizeWidget)">
                  <div class="row q-col-gutter-md">
                    <div class="col-12 col-sm-6">
                      <q-input v-model="customizeDraft.title" dense outlined label="Title" />
                    </div>
  
                    <div class="col-12 col-sm-6">
                      <q-select
                        v-model="customizeDraft.sourceKey"
                        dense
                        outlined
                        emit-value
                        map-options
                        label="Data source"
                        :options="customizeSourceOptions"
                        @update:model-value="onSourceKeyChanged"
                      />
                    </div>
                  </div>
  
                  <!-- Source parameters (shown only when required) -->
                  <div class="row q-col-gutter-md">
                    <div v-if="sourceNeeds(customizeDraft.sourceKey, 'player')" class="col-12 col-sm-6">
                      <q-select
                        v-model="customizeDraft.params.playerName"
                        dense
                        outlined
                        use-input
                        fill-input
                        hide-selected
                        input-debounce="0"
                        label="Player"
                        :options="playerOptionsFiltered"
                        :loading="optionsLoading.players"
                        @filter="filterPlayers"
                        emit-value
                        map-options
                      />
                    </div>
  
                    <div v-if="sourceNeeds(customizeDraft.sourceKey, 'alliance')" class="col-12 col-sm-6">
                      <q-select
                        v-model="customizeDraft.params.allianceTag"
                        dense
                        outlined
                        use-input
                        fill-input
                        hide-selected
                        input-debounce="0"
                        label="Alliance"
                        :options="allianceOptionsFiltered"
                        :loading="optionsLoading.alliances"
                        @filter="filterAlliances"
                        emit-value
                        map-options
                      />
                    </div>
  
                    <div v-if="sourceNeeds(customizeDraft.sourceKey, 'region')" class="col-12 col-sm-6">
                      <q-select
                        v-model="customizeDraft.params.regionName"
                        dense
                        outlined
                        use-input
                        fill-input
                        hide-selected
                        input-debounce="0"
                        label="Region"
                        :options="regionOptionsFiltered"
                        :loading="optionsLoading.regions"
                        @filter="filterRegions"
                        emit-value
                        map-options
                      />
                    </div>
  
                    <div v-if="sourceNeeds(customizeDraft.sourceKey, 'playerB')" class="col-12 col-sm-6">
                      <q-select
                        v-model="customizeDraft.params.playerNameB"
                        dense
                        outlined
                        use-input
                        fill-input
                        hide-selected
                        input-debounce="0"
                        label="Player B"
                        :options="playerOptionsFiltered"
                        :loading="optionsLoading.players"
                        @filter="filterPlayers"
                        emit-value
                        map-options
                      />
                    </div>
  
                    <div v-if="sourceNeeds(customizeDraft.sourceKey, 'topN')" class="col-12 col-sm-6">
                      <q-input
                        v-model.number="customizeDraft.params.topN"
                        type="number"
                        dense
                        outlined
                        label="Top N"
                        :min="1"
                        :max="50"
                      />
                    </div>
  
                    <div v-if="sourceNeeds(customizeDraft.sourceKey, 'limitVillages')" class="col-12 col-sm-6">
                      <q-input
                        v-model.number="customizeDraft.params.villageLimit"
                        type="number"
                        dense
                        outlined
                        label="Village sample limit"
                        hint="Used for density/quadrant calculations (performance)."
                        :min="200"
                        :max="20000"
                      />
                    </div>
                  </div>
  
                  <q-separator class="q-my-sm" />
  
                  <div class="row q-col-gutter-md">
                    <div class="col-12 col-sm-6">
                      <q-select
                        v-model="customizeDraft.colorMode"
                        dense
                        outlined
                        emit-value
                        map-options
                        label="Color mode"
                        :options="[
                          { label: 'Single', value: 'single' },
                          { label: 'Per-series', value: 'series' }
                        ]"
                      />
                    </div>
                  </div>
  
                  <!-- Single color -->
                  <div v-if="customizeDraft.colorMode === 'single'">
                    <q-input v-model="customizeDraft.color" dense outlined label="Color" placeholder="#3f51b5">
                      <template #append>
                        <q-btn dense flat round icon="palette">
                          <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                            <q-color v-model="customizeDraft.color" />
                          </q-popup-proxy>
                        </q-btn>
                      </template>
                    </q-input>
                    <div class="text-caption text-grey-7 q-mt-xs">Applied as a single palette/monochrome where possible.</div>
                  </div>
  
                  <!-- Per-series colors -->
                  <div v-else>
                    <div class="row items-center q-gutter-sm">
                      <div class="text-caption text-grey-7">Series colors</div>
                      <q-space />
                      <q-btn dense outline icon="add" label="Add color" @click="addSeriesColor()" />
                      <q-btn dense flat icon="restart_alt" label="Reset" @click="resetSeriesColorsToDefaults()" />
                    </div>
  
                    <div class="q-mt-sm">
                      <div v-for="(c, idx) in customizeDraft.colors" :key="idx" class="row items-center q-gutter-sm q-mb-sm">
                        <div class="text-caption text-grey-7" style="width: 70px;">#{{ idx + 1 }}</div>
  
                        <q-input v-model="customizeDraft.colors[idx]" dense outlined placeholder="#3f51b5" class="col">
                          <template #append>
                            <q-btn dense flat round icon="palette">
                              <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                                <q-color v-model="customizeDraft.colors[idx]" />
                              </q-popup-proxy>
                            </q-btn>
                          </template>
                        </q-input>
  
                        <q-btn
                          dense
                          flat
                          round
                          icon="delete"
                          class="text-grey-7"
                          :disable="customizeDraft.colors.length <= 1"
                          @click="removeSeriesColor(idx)"
                        />
                      </div>
  
                      <div class="text-caption text-grey-7">
                        These map to series order. For stacked/treemap/heatmap/donut, this becomes the palette.
                      </div>
                    </div>
                  </div>
                </template>
  
                <div v-else class="text-caption text-grey-7">This widget has no chart-specific options.</div>
              </q-card-section>
  
              <q-separator />
  
              <q-card-actions align="right">
                <q-btn flat label="Cancel" @click="closeCustomizer" />
                <q-btn unelevated color="primary" label="Apply" @click="applyCustomizer" />
              </q-card-actions>
            </q-card>
          </q-dialog>
  
          <!-- Bottom dock -->
          <!-- <transition name="dash-fab">
            <div v-if="isEditMode" class="dashboard__dockWrap">
              <q-card class="dashboard__dock" bordered>
                <div class="row items-center no-wrap q-gutter-sm">
                  <q-icon name="dashboard_customize" class="text-grey-7" />
                  <div class="text-caption text-grey-7">Add</div>
  
                  <q-separator vertical />
  
                  <q-btn dense flat icon="title" label="Header" @click="addWidget('header')" />
                  <q-btn dense flat icon="text_fields" label="Text" @click="addWidget('text')" />
  
                  <q-separator vertical />
  
                  <q-btn dense flat icon="show_chart" label="Line" @click="addWidget('line')" />
                  <q-btn dense flat icon="bar_chart" label="Bar" @click="addWidget('bar')" />
                  <q-btn dense flat icon="donut_large" label="Donut" @click="addWidget('donut')" />
                  <q-btn dense flat icon="area_chart" label="Area" @click="addWidget('area')" />
                  <q-btn dense flat icon="timeline" label="Spark" @click="addWidget('spark')" />
  
                  <q-btn dense flat icon="scatter_plot" label="Scatter" @click="addWidget('scatter')" />
                  <q-btn dense flat icon="bubble_chart" label="Bubble" @click="addWidget('bubble')" />
                  <q-btn dense flat icon="grid_on" label="Heatmap" @click="addWidget('heatmap')" />
                  <q-btn dense flat icon="candlestick_chart" label="Candles" @click="addWidget('candlestick')" />
                  <q-btn dense flat icon="radar" label="Radar" @click="addWidget('radar')" />
                  <q-btn dense flat icon="speed" label="Radial" @click="addWidget('radialbar')" />
                  <q-btn dense flat icon="account_tree" label="Treemap" @click="addWidget('treemap')" />
                  <q-btn dense flat icon="rule" label="Box" @click="addWidget('boxplot')" />
                  <q-btn dense flat icon="stacked_line_chart" label="Range" @click="addWidget('rangearea')" />
                  <q-btn dense flat icon="layers" label="Stacked" @click="addWidget('stackedbar')" />
                  <q-btn dense flat icon="insights" label="Mixed" @click="addWidget('mixed')" />
                  <q-btn dense flat icon="view_timeline" label="Timeline" @click="addWidget('timeline')" />
  
                  <q-space />
  
                  <q-btn dense flat round icon="close" class="text-grey-7" @click="isEditMode = false">
                    <q-tooltip>Exit edit</q-tooltip>
                  </q-btn>
                </div>
              </q-card>
            </div>
          </transition> -->
        </q-page>
      </q-page-container>
  
      <q-footer class="dashboard__footer q-pa-sm">asdadas</q-footer>
    </q-layout>
  </template>
  
  <script setup>
  import { ref, shallowRef, onMounted, watch, nextTick, computed, onBeforeUnmount } from 'vue'
  import { Notify } from 'quasar'
  import { api } from 'boot/axios'
  import { GridStack } from 'gridstack'
  import 'gridstack/dist/gridstack.min.css'
  
  /* existing chart widgets */
  import LineChart from './charts/LineChart.vue'
  import BarChart from './charts/BarChart.vue'
  import DonutChart from './charts/DonutChart.vue'
  import AreaChart from './charts/AreaChart.vue'
  import SparkLine from './charts/SparkLine.vue'
  
  /* other chart types */
  import ScatterChart from './charts/ScatterChart.vue'
  import BubbleChart from './charts/BubbleChart.vue'
  import HeatmapChart from './charts/HeatmapChart.vue'
  import CandlestickChart from './charts/CandlestickChart.vue'
  import RadarChart from './charts/RadarChart.vue'
  import RadialBarChart from './charts/RadialBarChart.vue'
  import TreemapChart from './charts/TreemapChart.vue'
  import BoxPlotChart from './charts/BoxPlotChart.vue'
  import RangeAreaChart from './charts/RangeAreaChart.vue'
  import StackedBarChart from './charts/StackedBarChart.vue'
  import MixedChart from './charts/MixedChart.vue'
  import TimelineRangeBarChart from './charts/TimelineRangeBarChart.vue'
  
  import TextBlock from './widgets/TextBlock.vue'
  import HeaderBlock from './widgets/HeaderBlock.vue'
  
  const GRID_COLS = 120
  const DEFAULT_CELL_HEIGHT = 90
  const MIN_CELL_PX = 32
  
  const showDesignGrid = ref(true)
  const showCellOutlines = ref(true)
  const squareGrid = ref(true)
  const cellHeightPx = ref(DEFAULT_CELL_HEIGHT)
  
  const isDraggingIn = ref(false)
  let scrollLockCount = 0
  function lockScroll () { scrollLockCount++; if (scrollLockCount === 1) document.body.classList.add('dashboard-scroll-locked') }
  function unlockScroll () { scrollLockCount = Math.max(0, scrollLockCount - 1); if (scrollLockCount === 0) document.body.classList.remove('dashboard-scroll-locked') }
  
  /* Palette */
  const paletteQuery = ref('')
  const palette = [
    { type: 'header', label: 'Header', icon: 'title', hint: 'Section title / divider', w: 120, h: 3, minW: 60, minH: 2 },
    { type: 'text', label: 'Text', icon: 'text_fields', hint: 'Notes / description', w: 60, h: 6, minW: 28, minH: 3 },
  
    { type: 'line', label: 'Line chart', icon: 'show_chart', hint: 'Trends over time', w: 60, h: 8, minW: 40, minH: 6 },
    { type: 'bar', label: 'Bar chart', icon: 'bar_chart', hint: 'Compare categories', w: 60, h: 8, minW: 40, minH: 6 },
    { type: 'donut', label: 'Donut', icon: 'donut_large', hint: 'Composition', w: 40, h: 7, minW: 28, minH: 5 },
    { type: 'area', label: 'Area chart', icon: 'area_chart', hint: 'Volume + trend', w: 40, h: 7, minW: 28, minH: 5 },
    { type: 'spark', label: 'Sparkline', icon: 'timeline', hint: 'Tiny trend', w: 40, h: 6, minW: 28, minH: 4 },
  
    { type: 'scatter', label: 'Scatter', icon: 'scatter_plot', hint: 'Correlation / clusters', w: 60, h: 8, minW: 40, minH: 6 },
    { type: 'bubble', label: 'Bubble', icon: 'bubble_chart', hint: 'Scatter + size', w: 60, h: 8, minW: 40, minH: 6 },
    { type: 'heatmap', label: 'Heatmap', icon: 'grid_on', hint: 'Matrix intensity', w: 60, h: 8, minW: 40, minH: 6 },
    { type: 'candlestick', label: 'Candlestick', icon: 'candlestick_chart', hint: 'Ranges over time', w: 60, h: 8, minW: 40, minH: 6 },
  
    { type: 'radar', label: 'Radar', icon: 'radar', hint: 'Multi-metric comparison', w: 50, h: 8, minW: 36, minH: 6 },
    { type: 'radialbar', label: 'RadialBar', icon: 'speed', hint: 'Gauge / progress', w: 40, h: 7, minW: 28, minH: 5 },
  
    { type: 'treemap', label: 'Treemap', icon: 'account_tree', hint: 'Hierarchical share', w: 60, h: 8, minW: 40, minH: 6 },
    { type: 'boxplot', label: 'BoxPlot', icon: 'rule', hint: 'Distribution + outliers', w: 60, h: 8, minW: 40, minH: 6 },
    { type: 'rangearea', label: 'RangeArea', icon: 'stacked_line_chart', hint: 'Min/Max envelope', w: 60, h: 8, minW: 40, minH: 6 },
    { type: 'stackedbar', label: 'Stacked bar', icon: 'layers', hint: 'Composition per category', w: 60, h: 8, minW: 40, minH: 6 },
    { type: 'mixed', label: 'Mixed', icon: 'insights', hint: 'Bar + line combo', w: 60, h: 8, minW: 40, minH: 6 },
    { type: 'timeline', label: 'Timeline', icon: 'view_timeline', hint: 'Range bars / gantt-like', w: 70, h: 8, minW: 48, minH: 6 }
  ]
  const filteredPalette = computed(() => {
    const q = paletteQuery.value.trim().toLowerCase()
    if (!q) return palette
    return palette.filter(p => `${p.label} ${p.type} ${p.hint}`.toLowerCase().includes(q))
  })
  
  /* colors */
  const DEFAULT_COLOR = '#3f51b5'
  const DEFAULT_SERIES_COLORS = ['#3f51b5', '#26a69a', '#ef5350', '#ab47bc', '#ffa726', '#5c6bc0']
  
  /* widget storage */
  const STORAGE_KEY = 'dashboard:gridstack:v14'
  const gridEl = ref(null)
  const grid = shallowRef(null)
  const isEditMode = ref(false)
  
  /* components map */
  const widgetComponents = {
    line: LineChart,
    bar: BarChart,
    donut: DonutChart,
    area: AreaChart,
    spark: SparkLine,
  
    scatter: ScatterChart,
    bubble: BubbleChart,
    heatmap: HeatmapChart,
    candlestick: CandlestickChart,
    radar: RadarChart,
    radialbar: RadialBarChart,
    treemap: TreemapChart,
    boxplot: BoxPlotChart,
    rangearea: RangeAreaChart,
    stackedbar: StackedBarChart,
    mixed: MixedChart,
    timeline: TimelineRangeBarChart,
  
    text: TextBlock,
    header: HeaderBlock
  }
  
  /* chart-type check */
  function isChartWidget (w) {
    return [
      'line', 'bar', 'donut', 'area', 'spark',
      'scatter', 'bubble', 'heatmap', 'candlestick',
      'radar', 'radialbar', 'treemap', 'boxplot',
      'rangearea', 'stackedbar', 'mixed', 'timeline'
    ].includes(w?.type)
  }
  
  /* -----------------------------
   * Data source registry (backend-connected)
   * ----------------------------- */
  const SOURCE_REGISTRY = {
    /* Players snapshot (/api/players) */
    'players.topPop': { label: 'Players: Top population', needs: ['topN'] },
    'players.topVillages': { label: 'Players: Top villages', needs: ['topN'] },
    'players.popVsVillages': { label: 'Players: Population vs villages (scatter)', needs: [] },
    'players.popDistribution': { label: 'Players: Population distribution (boxplot)', needs: [] },
    'players.allianceShareTopPlayers': { label: 'Players: Alliance share (top players donut)', needs: ['topN'] },
  
    /* Alliances snapshot (/api/alliances) */
    'alliances.topVillages': { label: 'Alliances: Top villages', needs: ['topN'] },
  
    /* Player history (/api/player/<name>/history) */
    'playerHistory.population': { label: 'Player history: Population', needs: ['player'] },
    'playerHistory.villages': { label: 'Player history: Villages', needs: ['player'] },
    'playerHistory.popOHLC': { label: 'Player history: Population OHLC (candles)', needs: ['player'] },
    'playerHistory.envelope': { label: 'Player history: Population envelope (range area)', needs: ['player'] },
  
    /* Alliance villages (/api/alliance/<tag>/villages) */
    'alliance.villagesQuadrants': { label: 'Alliance: Village count by quadrant (stacked)', needs: ['alliance', 'limitVillages'] },
  
    /* Region villages (/api/region/<name>/villages) */
    'region.villagesQuadrants': { label: 'Region: Village count by quadrant (stacked)', needs: ['region', 'limitVillages'] },
  
    /* World villages (/api/villages/latest) */
    'world.villageDensity': { label: 'World: Village density heatmap (sample)', needs: ['limitVillages'] },
  
    /* Comparisons */
    'compare.playersRadar': { label: 'Compare 2 players (radar)', needs: ['player', 'playerB'] },
    'player.popVsTopRadial': { label: 'Player pop vs top player (radial)', needs: ['player'] },
  
    /* Timeline (no canonical backend timeline yet; keep a real-data-adjacent source for now) */
    'timeline.fromHistorySpacing': { label: 'Timeline: From player history day gaps (demo from history)', needs: ['player'] }
  }
  
  function sourceNeeds (sourceKey, need) {
    const s = SOURCE_REGISTRY[sourceKey]
    if (!s) return false
    return s.needs.includes(need)
  }
  
  /* Per-chart selectable sources (at least one backend-driven option each) */
  const sourcesByChartType = computed(() => ({
    line: ['playerHistory.population', 'playerHistory.villages', 'players.topPop'],
    bar: ['players.topPop', 'players.topVillages', 'alliances.topVillages'],
    donut: ['players.allianceShareTopPlayers'],
    area: ['playerHistory.population', 'playerHistory.villages'],
    spark: ['playerHistory.population', 'players.topPop'],
    scatter: ['players.popVsVillages'],
    bubble: ['players.popVsVillages'],
    heatmap: ['world.villageDensity'],
    candlestick: ['playerHistory.popOHLC'],
    radar: ['compare.playersRadar'],
    radialbar: ['player.popVsTopRadial'],
    treemap: ['players.topPop'],
    boxplot: ['players.popDistribution'],
    rangearea: ['playerHistory.envelope'],
    stackedbar: ['alliance.villagesQuadrants', 'region.villagesQuadrants'],
    mixed: ['playerHistory.population'],
    timeline: ['timeline.fromHistorySpacing']
  }))
  
  function defaultSourceForType (type) {
    const list = sourcesByChartType.value[type] || []
    return list[0] || ''
  }
  
  function ensureWidgetConfig (w) {
    if (!w) return
    if (!w.config) w.config = {}
  
    if (!w.config.color) w.config.color = DEFAULT_COLOR
    if (w.config.colorMode !== 'series' && w.config.colorMode !== 'single') w.config.colorMode = 'single'
  
    // v14: sourceKey + params (keep backward compatibility with old string `source`)
    if (!w.config.sourceKey) w.config.sourceKey = w.config.source || defaultSourceForType(w.type)
    if (!w.config.params) w.config.params = {}
  
    // defaults for params
    if (typeof w.config.params.topN !== 'number') w.config.params.topN = 10
    if (typeof w.config.params.villageLimit !== 'number') w.config.params.villageLimit = 5000
  }
  
  /* -----------------------------
   * Options loading (players / alliances / regions) like other pages
   * ----------------------------- */
  const optionsLoading = ref({ players: false, alliances: false, regions: false })
  const playerOptionsAll = ref([])
  const playerOptionsFiltered = ref([])
  const allianceOptionsAll = ref([])
  const allianceOptionsFiltered = ref([])
  const regionOptionsAll = ref([])
  const regionOptionsFiltered = ref([])
  
  function normalizePlayerRow (p) {
    return {
      name: String(p?.name ?? p?.player_name ?? p?.player ?? ''),
      alliance: String(p?.alliance ?? p?.alliance_tag ?? p?.tag ?? ''),
      villages: Number(p?.villages ?? p?.village_count ?? 0),
      population: Number(p?.population ?? p?.pop ?? 0)
    }
  }
  
  function normalizeAllianceRow (a) {
    return {
      tag: String(a?.alliance_tag ?? a?.tag ?? a?.alliance ?? ''),
      villages: Number(a?.villages ?? a?.village_count ?? 0),
      population: Number(a?.population ?? a?.total_pop ?? a?.pop ?? 0)
    }
  }
  
  async function loadOptionsOnce () {
    // players
    optionsLoading.value.players = true
    try {
      const { data } = await api.get('/api/players?limit=10000')
      const rows = (Array.isArray(data) ? data : []).map(normalizePlayerRow).filter(x => x.name)
      playerOptionsAll.value = rows
        .sort((a, b) => b.population - a.population)
        .map(p => ({ label: `${p.name} (${p.population.toLocaleString()} pop)`, value: p.name }))
      playerOptionsFiltered.value = playerOptionsAll.value
    } catch {
      playerOptionsAll.value = []
      playerOptionsFiltered.value = []
    } finally {
      optionsLoading.value.players = false
    }
  
    // alliances
    optionsLoading.value.alliances = true
    try {
      const { data } = await api.get('/api/alliances')
      const rows = (Array.isArray(data) ? data : []).map(normalizeAllianceRow).filter(x => x.tag)
      allianceOptionsAll.value = rows
        .sort((a, b) => b.villages - a.villages)
        .map(a => ({ label: `${a.tag} (${a.villages.toLocaleString()} villages)`, value: a.tag }))
      allianceOptionsFiltered.value = allianceOptionsAll.value
    } catch {
      allianceOptionsAll.value = []
      allianceOptionsFiltered.value = []
    } finally {
      optionsLoading.value.alliances = false
    }
  
    // regions (names list)
    optionsLoading.value.regions = true
    try {
      const { data } = await api.get('/api/region')
      const names = Array.isArray(data) ? data : (Array.isArray(data?.regions) ? data.regions : [])
      regionOptionsAll.value = (names || []).map(r => ({
        label: String(r?.name ?? r?.region ?? r),
        value: String(r?.name ?? r?.region ?? r)
      })).filter(o => o.value)
      regionOptionsFiltered.value = regionOptionsAll.value
    } catch {
      regionOptionsAll.value = []
      regionOptionsFiltered.value = []
    } finally {
      optionsLoading.value.regions = false
    }
  }
  
  function filterPlayers (needle, update) {
    update(() => {
      const n = (needle || '').trim().toLowerCase()
      if (!n) return (playerOptionsFiltered.value = playerOptionsAll.value.slice(0, 50))
      playerOptionsFiltered.value = playerOptionsAll.value.filter(o => (o.label || '').toLowerCase().includes(n)).slice(0, 50)
    })
  }
  function filterAlliances (needle, update) {
    update(() => {
      const n = (needle || '').trim().toLowerCase()
      if (!n) return (allianceOptionsFiltered.value = allianceOptionsAll.value.slice(0, 50))
      allianceOptionsFiltered.value = allianceOptionsAll.value.filter(o => (o.label || '').toLowerCase().includes(n)).slice(0, 50)
    })
  }
  function filterRegions (needle, update) {
    update(() => {
      const n = (needle || '').trim().toLowerCase()
      if (!n) return (regionOptionsFiltered.value = regionOptionsAll.value.slice(0, 80))
      regionOptionsFiltered.value = regionOptionsAll.value.filter(o => (o.label || '').toLowerCase().includes(n)).slice(0, 80)
    })
  }
  
  /* -----------------------------
   * Runtime cache + fetchers
   * ----------------------------- */
  const memCache = new Map()
  async function cached (key, fn) {
    if (memCache.has(key)) return memCache.get(key)
    const p = Promise.resolve().then(fn).catch(err => { memCache.delete(key); throw err })
    memCache.set(key, p)
    return p
  }
  
  async function fetchPlayers () {
    return cached('players:10000', async () => {
      const { data } = await api.get('/api/players?limit=10000')
      return (Array.isArray(data) ? data : []).map(normalizePlayerRow).filter(p => p.name)
    })
  }
  
  async function fetchAlliances () {
    return cached('alliances', async () => {
      const { data } = await api.get('/api/alliances')
      return (Array.isArray(data) ? data : []).map(normalizeAllianceRow).filter(a => a.tag)
    })
  }
  
  async function fetchPlayerHistory (playerName) {
    const key = `playerHistory:${playerName}`
    return cached(key, async () => {
      const res = await api.get(`/api/player/${encodeURIComponent(playerName)}/history?no_cache=1`)
      const payload = res.data?.data ?? res.data
      const history = payload?.history || payload || []
      return Array.isArray(history) ? history : []
    })
  }
  
  async function fetchAllianceVillages (tag, limit) {
    const key = `allianceVillages:${tag}:${limit}`
    return cached(key, async () => {
      const res = await api.get(`/api/alliance/${encodeURIComponent(tag)}/villages?limit=${encodeURIComponent(limit)}&no_cache=1`)
      const rows = res.data?.villages || res.data || []
      return Array.isArray(rows) ? rows : []
    })
  }
  
  async function fetchRegionVillages (regionName, limit) {
    const key = `regionVillages:${regionName}:${limit}`
    return cached(key, async () => {
      const res = await api.get(`/api/region/${encodeURIComponent(regionName)}/villages?limit=${encodeURIComponent(limit)}&no_cache=1`)
      const rows = res.data?.villages || res.data || []
      return Array.isArray(rows) ? rows : []
    })
  }
  
  async function fetchWorldVillages (limit) {
    const key = `worldVillages:${limit}`
    return cached(key, async () => {
      const res = await api.get(`/api/villages/latest?limit=${encodeURIComponent(limit)}&no_cache=1`)
      const rows = res.data?.villages || res.data || []
      return Array.isArray(rows) ? rows : []
    })
  }
  
  function xyFromVillageRow (row) {
    const x = Number(row.x ?? row.village_x ?? row.coord_x ?? row.cx)
    const y = Number(row.y ?? row.village_y ?? row.coord_y ?? row.cy)
    return { x: Number.isFinite(x) ? x : 0, y: Number.isFinite(y) ? y : 0 }
  }
  
  function quadrantOf (x, y) {
    // Travian style: x/y negative/positive => 4 quadrants
    if (x >= 0 && y >= 0) return 'SE'
    if (x >= 0 && y < 0) return 'NE'
    if (x < 0 && y >= 0) return 'SW'
    return 'NW'
  }
  
  /* -----------------------------
   * Runtime state per widget
   * ----------------------------- */
  const widgetRuntime = ref({}) // { [id]: { loading, error, props } }
  function runtimeFor (id) {
    return widgetRuntime.value[id] || { loading: false, error: '', props: {} }
  }
  function setRuntime (id, patch) {
    widgetRuntime.value = { ...widgetRuntime.value, [id]: { ...(widgetRuntime.value[id] || { loading: false, error: '', props: {} }), ...patch } }
  }
  
  /* chart props resolver: pass both `color` and `colors` */
  function effectiveColors (w) {
    const mode = w.config?.colorMode
    if (mode === 'series' && Array.isArray(w.config?.colors) && w.config.colors.length) return [...w.config.colors]
    return null
  }
  
  async function buildChartProps (w) {
    ensureWidgetConfig(w)
    const color = w.config?.color || DEFAULT_COLOR
    const colors = effectiveColors(w)
    const sourceKey = w.config?.sourceKey || defaultSourceForType(w.type)
    const params = w.config?.params || {}
    const topN = Math.max(1, Math.min(50, Number(params.topN || 10)))
    const villageLimit = Math.max(200, Math.min(20000, Number(params.villageLimit || 5000)))
  
    // -------- Players snapshot --------
    if (sourceKey === 'players.topPop') {
      const players = await fetchPlayers()
      const top = [...players].sort((a, b) => b.population - a.population).slice(0, topN)
      if (w.type === 'line') return { data: top.map(p => ({ label: p.name, value: p.population })), color, colors }
      if (w.type === 'bar') return { categories: top.map(p => p.name), series: [{ name: 'Population', data: top.map(p => p.population) }], color, colors, horizontal: true }
      if (w.type === 'treemap') return { series: [{ data: top.map(p => ({ x: p.name, y: p.population })) }], color, colors }
      if (w.type === 'spark') return { series: [{ name: 'Top pop', data: top.map(p => p.population) }], color, colors }
      // fallback
      return { data: top.map(p => ({ label: p.name, value: p.population })), color, colors }
    }
  
    if (sourceKey === 'players.topVillages') {
      const players = await fetchPlayers()
      const top = [...players].sort((a, b) => b.villages - a.villages).slice(0, topN)
      if (w.type === 'bar') return { categories: top.map(p => p.name), series: [{ name: 'Villages', data: top.map(p => p.villages) }], color, colors, horizontal: true }
      if (w.type === 'line') return { data: top.map(p => ({ label: p.name, value: p.villages })), color, colors }
      return { categories: top.map(p => p.name), series: [{ name: 'Villages', data: top.map(p => p.villages) }], color, colors }
    }
  
    if (sourceKey === 'players.popVsVillages') {
      const players = await fetchPlayers()
      const pts = players
        .filter(p => Number.isFinite(p.population) && Number.isFinite(p.villages))
        .slice(0, 2000)
  
      if (w.type === 'bubble') {
        return {
          series: [
            {
              name: 'Players',
              data: pts.slice(0, 250).map(p => ({
                x: p.villages,
                y: p.population,
                z: Math.max(3, Math.min(60, Math.round(p.population / 2500)))
              }))
            }
          ],
          xTitle: 'Villages',
          yTitle: 'Population',
          color,
          colors
        }
      }
  
      // scatter default
      return {
        series: [{ name: 'Players', data: pts.slice(0, 1500).map(p => [p.villages, p.population]) }],
        xTitle: 'Villages',
        yTitle: 'Population',
        color,
        colors
      }
    }
  
    if (sourceKey === 'players.popDistribution') {
      const players = await fetchPlayers()
      const pops = players.map(p => Number(p.population || 0)).filter(n => Number.isFinite(n)).sort((a, b) => a - b)
      if (!pops.length) return { series: [{ name: 'Distribution', data: [] }], color, colors }
  
      // build boxplot buckets by quantiles (Q1..Q4)
      const bucketCount = 6
      const buckets = []
      for (let i = 0; i < bucketCount; i++) {
        const start = Math.floor((i / bucketCount) * pops.length)
        const end = Math.floor(((i + 1) / bucketCount) * pops.length)
        const slice = pops.slice(start, Math.max(start + 1, end))
        const min = slice[0]
        const max = slice[slice.length - 1]
        const q1 = slice[Math.floor(slice.length * 0.25)]
        const med = slice[Math.floor(slice.length * 0.5)]
        const q3 = slice[Math.floor(slice.length * 0.75)]
        buckets.push({ x: `B${i + 1}`, y: [min, q1, med, q3, max] })
      }
  
      return { series: [{ name: 'Population', data: buckets }], color, colors }
    }
  
    if (sourceKey === 'players.allianceShareTopPlayers') {
      const players = await fetchPlayers()
      const top = [...players].sort((a, b) => b.population - a.population).slice(0, topN)
      const map = new Map()
      for (const p of top) {
        const tag = (p.alliance || 'No alliance').trim() || 'No alliance'
        map.set(tag, (map.get(tag) || 0) + 1)
      }
      const pairs = [...map.entries()].sort((a, b) => b[1] - a[1]).slice(0, 12)
      return {
        series: pairs.map(([, c]) => c),
        labels: pairs.map(([t]) => t),
        color,
        colors
      }
    }
  
    // -------- Alliances snapshot --------
    if (sourceKey === 'alliances.topVillages') {
      const alliances = await fetchAlliances()
      const top = [...alliances].sort((a, b) => b.villages - a.villages).slice(0, topN)
      return { categories: top.map(a => a.tag), series: [{ name: 'Villages', data: top.map(a => a.villages) }], color, colors, horizontal: true }
    }
  
    // -------- Player history --------
    if (sourceKey === 'playerHistory.population' || sourceKey === 'playerHistory.villages') {
      const name = String(params.playerName || '').trim()
      if (!name) throw new Error('Select a player for this source.')
      const hist = await fetchPlayerHistory(name)
      if (!hist.length) return { data: [], color, colors }
  
      const key = sourceKey === 'playerHistory.villages' ? 'villages' : 'population'
      const data = hist.map(h => ({ label: String(h.date ?? h.dump_date ?? ''), value: Number(h?.[key] || 0) }))
  
      if (w.type === 'line') return { data, color, colors }
      if (w.type === 'area') return { categories: data.map(d => d.label), series: [{ name: key === 'villages' ? 'Villages' : 'Population', data: data.map(d => d.value) }], color, colors }
      if (w.type === 'mixed') {
        // mixed: column = population, line = villages if present
        const categories = data.map(d => d.label)
        const pop = hist.map(h => Number(h.population || 0))
        const vill = hist.map(h => Number(h.villages || 0))
        return {
          categories,
          series: [
            { name: 'Population', type: 'column', data: pop },
            { name: 'Villages', type: 'line', data: vill }
          ],
          color,
          colors
        }
      }
      if (w.type === 'spark') {
        return { series: [{ name: key === 'villages' ? 'Villages' : 'Population', data: data.map(d => d.value) }], color, colors }
      }
  
      return { data, color, colors }
    }
  
    if (sourceKey === 'playerHistory.popOHLC') {
      const name = String(params.playerName || '').trim()
      if (!name) throw new Error('Select a player for this source.')
      const hist = await fetchPlayerHistory(name)
      if (hist.length < 2) return { series: [{ name: 'Population', data: [] }], color, colors }
  
      const points = hist
        .map(h => ({ x: String(h.date ?? h.dump_date ?? ''), v: Number(h.population || 0) }))
        .filter(p => p.x)
  
      const candles = []
      for (let i = 1; i < points.length; i++) {
        const prev = points[i - 1].v
        const curr = points[i].v
        const low = Math.min(prev, curr)
        const high = Math.max(prev, curr)
        candles.push({ x: points[i].x, y: [prev, high, low, curr] }) // [open, high, low, close]
      }
      return { series: [{ name: 'Population', data: candles }], color, colors }
    }
  
    if (sourceKey === 'playerHistory.envelope') {
      const name = String(params.playerName || '').trim()
      if (!name) throw new Error('Select a player for this source.')
      const hist = await fetchPlayerHistory(name)
      if (!hist.length) return { series: [{ name: 'Min/Max', data: [] }], color, colors }
  
      const window = 3
      const series = hist.map((h, idx) => {
        const start = Math.max(0, idx - window)
        const end = Math.min(hist.length, idx + window + 1)
        const slice = hist.slice(start, end).map(x => Number(x.population || 0))
        const min = Math.min(...slice)
        const max = Math.max(...slice)
        return { x: String(h.date ?? h.dump_date ?? ''), y: [min, max] }
      })
      return { series: [{ name: 'Min/Max', data: series }], color, colors }
    }
  
    // -------- Quadrant breakdowns from villages list --------
    if (sourceKey === 'alliance.villagesQuadrants') {
      const tag = String(params.allianceTag || '').trim()
      if (!tag) throw new Error('Select an alliance for this source.')
      const rows = await fetchAllianceVillages(tag, villageLimit)
  
      const counts = { NW: 0, NE: 0, SW: 0, SE: 0 }
      for (const r of rows) {
        const { x, y } = xyFromVillageRow(r)
        counts[quadrantOf(x, y)]++
      }
  
      // stacked: single series is acceptable; also works as a simple bar if your component expects stacked
      return { categories: ['NW', 'NE', 'SW', 'SE'], series: [{ name: tag, data: [counts.NW, counts.NE, counts.SW, counts.SE] }], color, colors }
    }
  
    if (sourceKey === 'region.villagesQuadrants') {
      const rn = String(params.regionName || '').trim()
      if (!rn) throw new Error('Select a region for this source.')
      const rows = await fetchRegionVillages(rn, villageLimit)
  
      const counts = { NW: 0, NE: 0, SW: 0, SE: 0 }
      for (const r of rows) {
        const { x, y } = xyFromVillageRow(r)
        counts[quadrantOf(x, y)]++
      }
      return { categories: ['NW', 'NE', 'SW', 'SE'], series: [{ name: rn, data: [counts.NW, counts.NE, counts.SW, counts.SE] }], color, colors }
    }
  
    // -------- World density heatmap (sample) --------
    if (sourceKey === 'world.villageDensity') {
      const rows = await fetchWorldVillages(villageLimit)
  
      // bucket x/y into 10 bins each, heatmap expects series by y-bins with x labels
      const bins = 10
      const xs = []
      const ys = []
      for (const r of rows) {
        const { x, y } = xyFromVillageRow(r)
        xs.push(x); ys.push(y)
      }
      const xmin = Math.min(...xs, -200)
      const xmax = Math.max(...xs, 200)
      const ymin = Math.min(...ys, -200)
      const ymax = Math.max(...ys, 200)
  
      function binIndex (v, vmin, vmax) {
        if (vmax === vmin) return 0
        const t = (v - vmin) / (vmax - vmin)
        return Math.max(0, Math.min(bins - 1, Math.floor(t * bins)))
      }
  
      const gridCounts = Array.from({ length: bins }, () => Array.from({ length: bins }, () => 0))
      for (const r of rows) {
        const { x, y } = xyFromVillageRow(r)
        const xi = binIndex(x, xmin, xmax)
        const yi = binIndex(y, ymin, ymax)
        gridCounts[yi][xi]++
      }
  
      const xLabels = Array.from({ length: bins }, (_, i) => `X${i + 1}`)
      const yLabels = Array.from({ length: bins }, (_, i) => `Y${i + 1}`)
  
      const series = yLabels.map((yl, yi) => ({
        name: yl,
        data: xLabels.map((xl, xi) => ({ x: xl, y: gridCounts[yi][xi] }))
      }))
  
      return { series, color, colors }
    }
  
    // -------- Comparisons --------
    if (sourceKey === 'compare.playersRadar') {
      const a = String(params.playerName || '').trim()
      const b = String(params.playerNameB || '').trim()
      if (!a || !b) throw new Error('Select Player and Player B for this source.')
      const players = await fetchPlayers()
      const pa = players.find(p => p.name === a)
      const pb = players.find(p => p.name === b)
      if (!pa || !pb) throw new Error('Selected players not found in snapshot.')
  
      const categories = ['Population', 'Villages']
      return {
        categories,
        series: [
          { name: a, data: [pa.population, pa.villages] },
          { name: b, data: [pb.population, pb.villages] }
        ],
        color,
        colors
      }
    }
  
    if (sourceKey === 'player.popVsTopRadial') {
      const name = String(params.playerName || '').trim()
      if (!name) throw new Error('Select a player for this source.')
      const players = await fetchPlayers()
      const top = [...players].sort((a, b) => b.population - a.population)[0]
      const me = players.find(p => p.name === name)
      if (!me || !top) throw new Error('Player/top not found.')
  
      const pct = top.population > 0 ? Math.round((me.population / top.population) * 100) : 0
      return { series: [Math.max(0, Math.min(100, pct))], labels: ['% of top pop'], color, colors }
    }
  
    // -------- Timeline (derived from history spacing) --------
    if (sourceKey === 'timeline.fromHistorySpacing') {
      const name = String(params.playerName || '').trim()
      if (!name) throw new Error('Select a player for this source.')
      const hist = await fetchPlayerHistory(name)
      if (hist.length < 2) return { series: [{ name: 'Gaps', data: [] }], color, colors }
  
      // represent each day gap as a range bar: [idx, idx+1]
      const data = hist.slice(1).map((h, i) => ({ x: String(h.date ?? h.dump_date ?? `D${i + 2}`), y: [i, i + 1] }))
      return { series: [{ name: 'Gaps', data }], color, colors }
    }
  
    // fallback: keep old demo-compatible behavior if unknown
    return { color, colors }
  }
  
  async function refreshWidget (w) {
    if (!w || !isChartWidget(w)) return
    ensureWidgetConfig(w)
  
    const id = w.id
    setRuntime(id, { loading: true, error: '' })
  
    try {
      const props = await buildChartProps(w)
      setRuntime(id, { loading: false, error: '', props })
    } catch (e) {
      const msg = e?.message ? String(e.message) : 'Failed to load data for widget'
      setRuntime(id, { loading: false, error: msg, props: {} })
    }
  }
  
  let refreshRaf = 0
  function refreshAllWidgets () {
    cancelAnimationFrame(refreshRaf)
    refreshRaf = requestAnimationFrame(async () => {
      const list = widgets.value.filter(isChartWidget)
      await Promise.allSettled(list.map(refreshWidget))
      triggerChartResizeNudge()
    })
  }
  
  /* -----------------------------
   * Customizer dialog
   * ----------------------------- */
  const customizeOpen = ref(false)
  const customizeWidgetId = ref(null)
  const customizeWidget = computed(() => widgets.value.find(w => w.id === customizeWidgetId.value) || null)
  
  const customizeDraft = ref({
    title: '',
    sourceKey: '',
    params: { playerName: '', playerNameB: '', allianceTag: '', regionName: '', topN: 10, villageLimit: 5000 },
    colorMode: 'single',
    color: DEFAULT_COLOR,
    colors: [...DEFAULT_SERIES_COLORS]
  })
  
  const customizeSourceOptions = computed(() => {
    const w = customizeWidget.value
    if (!w) return []
    const keys = sourcesByChartType.value[w.type] || []
    return keys
      .filter(k => SOURCE_REGISTRY[k])
      .map(k => ({ value: k, label: SOURCE_REGISTRY[k].label }))
  })
  
  function onSourceKeyChanged () {
    // ensure required params exist (do not auto-pick values)
    const k = customizeDraft.value.sourceKey
    const needs = SOURCE_REGISTRY[k]?.needs || []
    if (!needs.includes('topN') && typeof customizeDraft.value.params.topN !== 'number') customizeDraft.value.params.topN = 10
    if (!needs.includes('limitVillages') && typeof customizeDraft.value.params.villageLimit !== 'number') customizeDraft.value.params.villageLimit = 5000
  }
  
  function openWidgetCustomizer (id) {
    const w = widgets.value.find(x => x.id === id)
    if (!w) return
    if (isChartWidget(w)) ensureWidgetConfig(w)
  
    const currentMode = w.config?.colorMode || 'single'
    const currentColors = Array.isArray(w.config?.colors) && w.config.colors.length ? [...w.config.colors] : [...DEFAULT_SERIES_COLORS]
  
    customizeWidgetId.value = id
    customizeDraft.value = {
      title: w.title ?? '',
      sourceKey: w.config?.sourceKey ?? defaultSourceForType(w.type),
      params: {
        playerName: w.config?.params?.playerName ?? '',
        playerNameB: w.config?.params?.playerNameB ?? '',
        allianceTag: w.config?.params?.allianceTag ?? '',
        regionName: w.config?.params?.regionName ?? '',
        topN: Number.isFinite(w.config?.params?.topN) ? w.config.params.topN : 10,
        villageLimit: Number.isFinite(w.config?.params?.villageLimit) ? w.config.params.villageLimit : 5000
      },
      colorMode: currentMode,
      color: w.config?.color ?? DEFAULT_COLOR,
      colors: currentColors
    }
    customizeOpen.value = true
  }
  
  function closeCustomizer () {
    customizeOpen.value = false
    customizeWidgetId.value = null
  }
  
  function addSeriesColor () {
    customizeDraft.value.colors.push(
      DEFAULT_SERIES_COLORS[customizeDraft.value.colors.length % DEFAULT_SERIES_COLORS.length]
    )
  }
  function removeSeriesColor (idx) {
    if (customizeDraft.value.colors.length <= 1) return
    customizeDraft.value.colors.splice(idx, 1)
  }
  function resetSeriesColorsToDefaults () {
    customizeDraft.value.colors = [...DEFAULT_SERIES_COLORS]
  }
  
  function applyCustomizer () {
    const w = customizeWidget.value
    if (!w) return closeCustomizer()
    if (isChartWidget(w)) ensureWidgetConfig(w)
  
    w.title = customizeDraft.value.title
  
    if (isChartWidget(w)) {
      w.config.sourceKey = customizeDraft.value.sourceKey || w.config.sourceKey
      w.config.source = w.config.sourceKey // keep old field updated for backward compatibility
      w.config.params = { ...(w.config.params || {}), ...(customizeDraft.value.params || {}) }
  
      w.config.colorMode = customizeDraft.value.colorMode === 'series' ? 'series' : 'single'
      if (w.config.colorMode === 'series') {
        const cleaned = (customizeDraft.value.colors || []).map(s => (s || '').trim()).filter(Boolean)
        w.config.colors = cleaned.length ? cleaned : [...DEFAULT_SERIES_COLORS]
        w.config.color = w.config.colors[0] || DEFAULT_COLOR
      } else {
        w.config.color = (customizeDraft.value.color || '').trim() || DEFAULT_COLOR
        delete w.config.colors
      }
    }
  
    saveLayout()
    refreshWidget(w)
    triggerChartResizeNudge()
    closeCustomizer()
  }
  
  /* -----------------------------
   * Widget prop binding
   * ----------------------------- */
  function isDesignBlock (w) {
    return w.type === 'text' || w.type === 'header'
  }
  
  function getWidgetProps (w) {
    if (isChartWidget(w)) {
      const r = runtimeFor(w.id)
      // always include colors so charts keep styling even while loading
      ensureWidgetConfig(w)
      const base = { color: w.config.color || DEFAULT_COLOR, colors: effectiveColors(w) }
      return { ...base, ...(r.props || {}) }
    }
    if (w.type === 'text') return { edit: isEditMode.value, text: w.text ?? '', onUpdateText: (val) => (w.text = val) }
    if (w.type === 'header') return { edit: isEditMode.value, subtitle: w.subtitle ?? '', onUpdateSubtitle: (val) => (w.subtitle = val) }
    return {}
  }
  
  /* defaults */
  const defaultWidgets = [
    { id: 'line', type: 'line', title: 'Chart 1', x: 0, y: 0, w: 60, h: 8, minW: 40, minH: 6 },
    { id: 'bar', type: 'bar', title: 'Chart 2', x: 60, y: 0, w: 60, h: 8, minW: 40, minH: 6 },
    { id: 'donut', type: 'donut', title: 'Chart 3', x: 0, y: 8, w: 40, h: 7, minW: 28, minH: 5 },
    { id: 'area', type: 'area', title: 'Chart 4', x: 40, y: 8, w: 40, h: 7, minW: 28, minH: 5 },
    { id: 'scatter', type: 'scatter', title: 'Scatter', x: 80, y: 8, w: 40, h: 7, minW: 28, minH: 5 }
  ]
  
  function cloneDefaults () {
    return defaultWidgets.map(w => {
      const ww = { ...w }
      if (isChartWidget(ww)) ensureWidgetConfig(ww)
      return ww
    })
  }
  
  function loadWidgets () {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      if (!raw) return cloneDefaults()
      const saved = JSON.parse(raw)
      if (Array.isArray(saved) && saved.length) {
        return saved.map(w => {
          const ww = { ...w }
          if (isChartWidget(ww)) ensureWidgetConfig(ww)
          return ww
        })
      }
      return cloneDefaults()
    } catch {
      return cloneDefaults()
    }
  }
  
  const widgets = ref(loadWidgets())
  
  /* overlay */
  const gridOverlayStyle = computed(() => ({
    '--grid-cols': String(GRID_COLS),
    '--grid-row': `${cellHeightPx.value}px`
  }))
  
  function triggerChartResizeNudge () {
    window.dispatchEvent(new Event('resize'))
  }
  
  let chartResizeRaf = 0
  function triggerChartResizeNudgeRaf () {
    cancelAnimationFrame(chartResizeRaf)
    chartResizeRaf = requestAnimationFrame(() => window.dispatchEvent(new Event('resize')))
  }
  
  /* resizing */
  function recomputeCellHeightFromWidth () {
    if (!gridEl.value) return
    const w = gridEl.value.clientWidth || 0
    if (!w) return
    cellHeightPx.value = Math.max(MIN_CELL_PX, Math.floor(w / GRID_COLS))
  }
  function applyCellHeightToGrid () {
    if (!grid.value) return
    grid.value.cellHeight(cellHeightPx.value)
    grid.value.onParentResize?.()
    triggerChartResizeNudge()
  }
  async function settleAfterPaint () {
    await nextTick()
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        if (squareGrid.value) recomputeCellHeightFromWidth()
        else cellHeightPx.value = DEFAULT_CELL_HEIGHT
        applyCellHeightToGrid()
      })
    })
  }
  
  let resizeObserver = null
  let resizeRaf = 0
  function attachResizeObserver () {
    if (!gridEl.value || typeof ResizeObserver === 'undefined') return
    resizeObserver = new ResizeObserver(() => {
      cancelAnimationFrame(resizeRaf)
      resizeRaf = requestAnimationFrame(() => {
        if (squareGrid.value) {
          recomputeCellHeightFromWidth()
          applyCellHeightToGrid()
        } else {
          grid.value?.onParentResize?.()
          triggerChartResizeNudge()
        }
      })
    })
    resizeObserver.observe(gridEl.value)
  }
  function detachResizeObserver () {
    if (resizeObserver) { resizeObserver.disconnect(); resizeObserver = null }
    cancelAnimationFrame(resizeRaf)
    resizeRaf = 0
  }
  
  /* gridstack */
  function purgePaletteClonesInGrid () {
    const root = gridEl.value
    if (!root) return
    root.querySelectorAll('.grid-stack-item.palette-item').forEach((n) => n.remove())
  }
  
  function initGrid () {
    if (!gridEl.value) return
    if (squareGrid.value) recomputeCellHeightFromWidth()
  
    grid.value = GridStack.init(
      {
        column: GRID_COLS,
        margin: 8,
        float: true,
        cellHeight: cellHeightPx.value,
        animate: true,
        resizable: { handles: 'all' },
        draggable: { handle: '.dashboard__cardHeader' },
        acceptWidgets: '.grid-stack-item'
      },
      gridEl.value
    )
  
    grid.value.enableMove(false)
    grid.value.enableResize(false)
  
// Avoid continuous resize events: they cause tooltip jitter
grid.value.on('resizestop', () => {
  purgePaletteClonesInGrid()
  triggerChartResizeNudge()
})

grid.value.on('dragstop', () => {
  purgePaletteClonesInGrid()
  triggerChartResizeNudge()
})

    grid.value.on('dragstop', () => { purgePaletteClonesInGrid(); triggerChartResizeNudge() })
  
    grid.value.on('dropped', async (event, previousWidget, newWidget) => {
      isDraggingIn.value = false
      unlockScroll()
      const el = newWidget?.el
      if (!el) return
  
      const content = el.querySelector('.grid-stack-item-content')
      if (content) content.innerHTML = ''
  
      const type = el.getAttribute('data-type') || 'text'
      const x = newWidget.x ?? 0
      const y = newWidget.y ?? 0
      const w = newWidget.w ?? parseInt(el.getAttribute('gs-w') || '60', 10)
      const h = newWidget.h ?? parseInt(el.getAttribute('gs-h') || '6', 10)
      const minW = parseInt(el.getAttribute('gs-min-w') || '28', 10)
      const minH = parseInt(el.getAttribute('gs-min-h') || '3', 10)
  
      grid.value?.removeWidget(el, false)
      purgePaletteClonesInGrid()
  
      await addWidget(type, { x, y, w, h, minW, minH }, { skipAutoPlace: true })
      await nextTick()
      purgePaletteClonesInGrid()
    })
  
    GridStack.setupDragIn('.dashboard__paletteItem', {
      appendTo: 'body',
      helper: 'clone',
      scroll: false,
      start: () => { isDraggingIn.value = true; lockScroll() },
      stop: () => { isDraggingIn.value = false; unlockScroll() }
    })
  
    triggerChartResizeNudge()
  }
  
  /* layout ops */
  function makeId (prefix) {
    return `${prefix}-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`
  }
  function findNextY () {
    return widgets.value.reduce((m, w) => Math.max(m, (w.y ?? 0) + (w.h ?? 1)), 0)
  }
  
  async function addWidget (type, override = null, opts = null) {
    const id = makeId(type)
    const preset = palette.find(p => p.type === type)
    const skipAutoPlace = !!opts?.skipAutoPlace
  
    const y = skipAutoPlace ? (override?.y ?? 0) : findNextY()
    const x = skipAutoPlace ? (override?.x ?? 0) : 0
  
    let wObj = {
      id,
      type,
      title: preset?.label ?? 'New widget',
      x,
      y,
      w: preset?.w ?? 60,
      h: preset?.h ?? 6,
      minW: preset?.minW ?? 28,
      minH: preset?.minH ?? 3
    }
  
    if (type === 'header') { wObj.title = 'Section title'; wObj.subtitle = wObj.subtitle ?? 'Optional subtitle' }
    if (type === 'text') { wObj.title = 'Notes'; wObj.text = wObj.text ?? 'Type here...' }
    if (isChartWidget(wObj)) ensureWidgetConfig(wObj)
  
    if (override) wObj = { ...wObj, ...override }
  
    widgets.value.push(wObj)
    await nextTick()
  
    const vueEl = gridEl.value?.querySelector?.(`.grid-stack-item[gs-id="${CSS.escape(id)}"]`)
    if (grid.value && vueEl) {
      grid.value.makeWidget(vueEl)
      triggerChartResizeNudge()
    }
  
    saveLayout()
  
    if (isChartWidget(wObj)) {
      // lazy-load data for new widget
      refreshWidget(wObj)
    }
  }
  
  async function removeWidget (id) {
    const idx = widgets.value.findIndex(w => w.id === id)
    if (idx === -1) return
  
    const el = gridEl.value?.querySelector?.(`.grid-stack-item[gs-id="${CSS.escape(id)}"]`)
    if (grid.value && el) grid.value.removeWidget(el, false)
  
    widgets.value.splice(idx, 1)
    await nextTick()
    saveLayout()
  
    // cleanup runtime
    const copy = { ...widgetRuntime.value }
    delete copy[id]
    widgetRuntime.value = copy
  }
  
  function saveLayout () {
    if (!grid.value) { localStorage.setItem(STORAGE_KEY, JSON.stringify(widgets.value)); return }
    const items = grid.value.save(false)
    const byId = new Map(items.map(i => [i.id, i]))
  
    const merged = widgets.value.map(w => {
      const i = byId.get(w.id)
      if (!i) return { ...w }
      return { ...w, x: i.x, y: i.y, w: i.w, h: i.h }
    })
  
    widgets.value = merged
    localStorage.setItem(STORAGE_KEY, JSON.stringify(merged))
  }
  
  async function resetLayout () {
    localStorage.removeItem(STORAGE_KEY)
    widgets.value = cloneDefaults()
  
    await nextTick()
    detachResizeObserver()
  
    if (grid.value) {
      grid.value.destroy(false)
      grid.value = null
    }
  
    await nextTick()
    initGrid()
    attachResizeObserver()
    await settleAfterPaint()
  
    refreshAllWidgets()
    Notify.create({ type: 'info', message: 'Dashboard reset.' })
  }
  
  watch(isEditMode, async (enabled) => {
    if (!grid.value) return
    grid.value.enableMove(enabled)
    grid.value.enableResize(enabled)
  
    if (enabled) {
      await nextTick()
      GridStack.setupDragIn('.dashboard__paletteItem', {
        appendTo: 'body',
        helper: 'clone',
        scroll: false,
        start: () => { isDraggingIn.value = true; lockScroll() },
        stop: () => { isDraggingIn.value = false; unlockScroll() }
      })
      await settleAfterPaint()
    } else {
      saveLayout()
    }
  })
  
  let refreshDebounce = 0

function scheduleRefreshAll () {
  clearTimeout(refreshDebounce)
  refreshDebounce = setTimeout(() => {
    refreshAllWidgets()
  }, 120)
}

watch(
  () =>
    widgets.value
      .filter(isChartWidget)
      .map((w) => ({
        id: w.id,
        type: w.type,
        title: w.title,
        sourceKey: w.config?.sourceKey,
        // only stringifying the param blocks avoids deep-watch recursion
        params: JSON.stringify(w.config?.params || {}),
        colorMode: w.config?.colorMode,
        color: w.config?.color,
        colors: JSON.stringify(w.config?.colors || []),
        // layout changes should not trigger data refresh:
        x: w.x, y: w.y, w: w.w, h: w.h
      })),
  () => {
    scheduleRefreshAll()
  },
  { deep: false, flush: 'post' }
)

onBeforeUnmount(() => {
  clearTimeout(refreshDebounce)
})

  
  onMounted(async () => {
    await nextTick()
    initGrid()
    attachResizeObserver()
    await settleAfterPaint()
    purgePaletteClonesInGrid()
  
    // load select options and initial widget data
    await loadOptionsOnce()
    refreshAllWidgets()
  })
  
  onBeforeUnmount(() => {
    unlockScroll()
    detachResizeObserver()
    cancelAnimationFrame(chartResizeRaf)
    cancelAnimationFrame(refreshRaf)
    if (grid.value) { grid.value.destroy(false); grid.value = null }
  })
  </script>
  
  <style scoped>

    /* Let chart tooltips escape their containers */
.dashboard__cardBodyInner,
.dashboard__runtimeWrap,
.dashboard__itemContent,
.grid-stack-item-content {
  overflow: visible !important;
}

/* ApexCharts tooltip: disable transform transitions that cause bounce */
.dashboard__cardBodyInner :deep(.apexcharts-tooltip),
.dashboard__cardBodyInner :deep(.apexcharts-xaxistooltip) {
  transition: none !important;
  will-change: auto !important;
}

/* Sometimes the inner svg wrapper gets constrained */
.dashboard__cardBodyInner :deep(.apexcharts-canvas) {
  width: 100% !important;
}

  .dashboard-scroll-locked {
    overflow: hidden !important;
  }
  
  .dashboard {
    min-height: 100vh;
    position: relative;
    isolation: isolate;
  }
  
  .dashboard__header {
    position: sticky;
    top: 0;
    z-index: 20;
  }
  
  .dashboard__footer {
    position: sticky;
    bottom: 0;
    z-index: 20;
  }
  
  .dashboard__page {
    position: relative;
    min-height: calc(100vh - 96px);
    padding: 12px;
  }
  
  .dashboard__grid {
    position: relative;
    z-index: 2;
    min-height: 60vh;
  }
  
  .dashboard__itemContent {
    height: 100%;
    padding: 8px;
    box-sizing: border-box;
  }
  
  .dashboard__card {
    height: 100%;
    display: flex;
    flex-direction: column;
  }
  
  .dashboard__cardHeader {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .dashboard__cardBody {
    flex: 1;
    min-height: 0;
  }
  
  .dashboard__cardBodyInner {
    height: 100%;
    min-height: 0;
    position: relative;
  }
  
  .dashboard__runtimeWrap {
    height: 100%;
    min-height: 0;
    position: relative;
  }
  
  .dashboard__runtimeError {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 10px;
    border-radius: 8px;
    background: rgba(255, 82, 82, 0.08);
    border: 1px solid rgba(255, 82, 82, 0.25);
    margin-bottom: 8px;
  }
  
  .dashboard__paletteWrap {
    position: fixed;
    top: 72px;
    right: 12px;
    width: 320px;
    z-index: 50;
  }
  
  .dashboard__paletteScroll {
    height: calc(100vh - 190px);
  }
  
  .dashboard__paletteGrid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 10px;
  }
  
  .dashboard__paletteItem {
    cursor: grab;
  }
  
  .dashboard__paletteThumb {
    padding: 10px;
    border-radius: 10px;
    background: rgba(0, 0, 0, 0.03);
    border: 1px solid rgba(0, 0, 0, 0.08);
  }
  
  .dashboard__paletteThumbTop {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .dashboard__palettePreview {
    margin-top: 8px;
    height: 54px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .ppSvg {
    width: 100%;
    height: 54px;
  }
  
  .ppStroke {
    stroke: rgba(25, 118, 210, 0.65);
    stroke-width: 3;
  }
  
  .ppAxis {
    stroke: rgba(0, 0, 0, 0.18);
    stroke-width: 1;
  }
  
  .ppPrev .ppLine {
    height: 8px;
    border-radius: 6px;
    background: rgba(0, 0, 0, 0.08);
    margin: 6px 0;
  }
  
  .ppLine--w92 { width: 92%; }
  .ppLine--w86 { width: 86%; }
  .ppLine--w74 { width: 74%; }
  .ppLine--w72 { width: 72%; }
  .ppLine--w60 { width: 60%; }
  .ppLine--w44 { width: 44%; }
  
  .dashboard__dockWrap {
    position: fixed;
    left: 12px;
    right: 12px;
    bottom: 14px;
    z-index: 40;
  }
  
  .dashboard__dock {
    padding: 6px 10px;
    border-radius: 12px;
  }
  
  .dashboard__dropHint {
    position: fixed;
    top: 84px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 60;
    padding: 8px 12px;
    border-radius: 999px;
    background: rgba(25, 118, 210, 0.12);
    border: 1px solid rgba(25, 118, 210, 0.25);
  }
  
  .dashboard__gridOverlay {
    position: absolute;
    inset: 12px;
    z-index: 1;
    pointer-events: none;
    background-image:
      linear-gradient(to right, rgba(0,0,0,0.05) 1px, transparent 1px),
      linear-gradient(to bottom, rgba(0,0,0,0.05) 1px, transparent 1px);
    background-size:
      calc(100% / var(--grid-cols)) var(--grid-row),
      calc(100% / var(--grid-cols)) var(--grid-row);
    border-radius: 12px;
  }
  
  .cell-outline .dashboard__card {
    outline: 1px dashed rgba(0, 0, 0, 0.18);
    outline-offset: -6px;
  }
  </style>
  