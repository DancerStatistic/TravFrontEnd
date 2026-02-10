<!-- MainDashboard.vue (FULL integrated - all chart types + per-widget data sources wired to backend like other pages) -->
<template>
    <q-layout class="dashboard" view="hHh Lpr lFf">
      <q-header elevated class="dashboard__header">
        <q-toolbar class="q-px-md">
          <q-toolbar-title class="text-weight-medium">Dashboard</q-toolbar-title>
  
          <div class="row items-center q-gutter-sm dashboard__headerActions">
            <q-toggle v-model="isEditMode" label="Edit layout" dense />
            <q-select
              v-model="selectedLayoutId"
              dense
              outlined
              clearable
              :options="layoutOptions"
              placeholder="Load layout"
              emit-value
              map-options
              options-dense
              style="min-width: 160px"
              @update:model-value="onLoadLayout"
            >
              <template #prepend><q-icon name="folder_open" /></template>
            </q-select>
            <q-btn dense outline icon="save" label="Save" :disable="!isEditMode" @click="saveLayout()" />
            <q-btn dense outline icon="save_as" label="Save as…" :disable="!isEditMode" @click="showSaveAsDialog = true" />
            <q-btn dense outline icon="restart_alt" label="Reset" @click="resetLayout()" />
          </div>
        </q-toolbar>
      </q-header>
  
      <q-dialog v-model="showSaveAsDialog" persistent>
        <q-card style="min-width: 320px">
          <q-card-section>
            <div class="text-h6">Save layout</div>
          </q-card-section>
          <q-card-section>
            <q-input v-model="saveAsName" outlined dense label="Layout name" autofocus @keyup.enter="doSaveAs" />
          </q-card-section>
          <q-card-actions align="right">
            <q-btn flat label="Cancel" @click="showSaveAsDialog = false" />
            <q-btn unelevated color="primary" label="Save" :disable="!saveAsName.trim()" @click="doSaveAs" />
          </q-card-actions>
        </q-card>
      </q-dialog>

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
                      >
                        <template #hint>
                          <div v-if="customizeDraft.sourceKey && SOURCE_REGISTRY[customizeDraft.sourceKey]" class="text-caption text-grey-7 q-mt-xs">
                            {{ SOURCE_REGISTRY[customizeDraft.sourceKey].label }}
                          </div>
                        </template>
                      </q-select>
                    </div>
                  </div>

                  <!-- Data source description -->
                  <q-banner v-if="customizeDraft.sourceKey && SOURCE_REGISTRY[customizeDraft.sourceKey]" dense rounded class="bg-blue-1 text-blue-9 q-mt-sm">
                    <template #avatar>
                      <q-icon name="info" color="blue" />
                    </template>
                    <div class="text-caption">
                      <strong>{{ SOURCE_REGISTRY[customizeDraft.sourceKey].label }}</strong>
                      <div v-if="SOURCE_REGISTRY[customizeDraft.sourceKey].needs && SOURCE_REGISTRY[customizeDraft.sourceKey].needs.length" class="q-mt-xs">
                        <span class="text-grey-7">Required: </span>
                        <q-chip
                          v-for="need in SOURCE_REGISTRY[customizeDraft.sourceKey].needs"
                          :key="need"
                          dense
                          size="sm"
                          color="blue-2"
                          text-color="blue-9"
                          :label="need === 'player' ? 'Player' : need === 'playerB' ? 'Player B' : need === 'alliance' ? 'Alliance' : need === 'allianceB' ? 'Alliance B' : need === 'region' ? 'Region' : need === 'topN' ? 'Top N' : need === 'limitVillages' ? 'Village Limit' : need"
                        />
                      </div>
                    </div>
                  </q-banner>
  
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

                    <div v-if="sourceNeeds(customizeDraft.sourceKey, 'allianceB')" class="col-12 col-sm-6">
                      <q-select
                        v-model="customizeDraft.params.allianceTagB"
                        dense
                        outlined
                        use-input
                        fill-input
                        hide-selected
                        input-debounce="0"
                        label="Alliance B"
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

                  <!-- Quick pick buttons for common configurations -->
                  <div v-if="customizeDraft.sourceKey && (sourceNeeds(customizeDraft.sourceKey, 'player') || sourceNeeds(customizeDraft.sourceKey, 'topN'))" class="q-mt-md">
                    <div class="text-caption text-grey-7 q-mb-xs">Quick picks:</div>
                    <div class="row q-gutter-xs">
                      <q-btn
                        v-if="sourceNeeds(customizeDraft.sourceKey, 'player') && topPlayerName"
                        dense
                        outline
                        size="sm"
                        label="Use top player"
                        icon="star"
                        @click="customizeDraft.params.playerName = topPlayerName; customizeDraft.title = getTitleForSource(customizeDraft.sourceKey, customizeDraft.params)"
                      />
                      <q-btn
                        v-if="sourceNeeds(customizeDraft.sourceKey, 'topN')"
                        dense
                        outline
                        size="sm"
                        label="Top 10"
                        @click="customizeDraft.params.topN = 10; customizeDraft.title = getTitleForSource(customizeDraft.sourceKey, customizeDraft.params)"
                      />
                      <q-btn
                        v-if="sourceNeeds(customizeDraft.sourceKey, 'topN')"
                        dense
                        outline
                        size="sm"
                        label="Top 20"
                        @click="customizeDraft.params.topN = 20; customizeDraft.title = getTitleForSource(customizeDraft.sourceKey, customizeDraft.params)"
                      />
                      <q-btn
                        v-if="sourceNeeds(customizeDraft.sourceKey, 'topN')"
                        dense
                        outline
                        size="sm"
                        label="Top 50"
                        @click="customizeDraft.params.topN = 50; customizeDraft.title = getTitleForSource(customizeDraft.sourceKey, customizeDraft.params)"
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
  import { filterNpcPlayers, filterNpcAlliances, isNpcAlliance } from 'src/constants/npc'
  import { useDashboardLayoutsStore } from 'src/stores/dashboard-layouts'
  
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
  const layoutsStore = useDashboardLayoutsStore()
  const gridEl = ref(null)
  const grid = shallowRef(null)
  const isEditMode = ref(false)
  const showSaveAsDialog = ref(false)
  const saveAsName = ref('')
  const selectedLayoutId = ref(layoutsStore.activeLayoutId)
  const layoutOptions = computed(() =>
    layoutsStore.layouts.map((l) => ({ label: l.name, value: l.id }))
  )
  
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
    'players.villageDistribution': { label: 'Players: Village count distribution (boxplot)', needs: [] },
    'players.byAlliancePop': { label: 'Players: Population by alliance (treemap)', needs: ['topN'] },
    'players.byAllianceCount': { label: 'Players: Count by alliance (donut)', needs: [] },
    'players.growthRate': { label: 'Players: Growth rate comparison (bar)', needs: ['topN'] },
  
    /* Alliances snapshot (/api/alliances) */
    'alliances.topVillages': { label: 'Alliances: Top villages', needs: ['topN'] },
    'alliances.topPopulation': { label: 'Alliances: Top population', needs: ['topN'] },
    'alliances.playerCount': { label: 'Alliances: Player count', needs: ['topN'] },
    'alliances.popVsVillages': { label: 'Alliances: Population vs villages (scatter)', needs: [] },
    'alliances.distribution': { label: 'Alliances: Population distribution (boxplot)', needs: [] },
  
    /* Player history (/api/player/<name>/history) */
    'playerHistory.population': { label: 'Player history: Population', needs: ['player'] },
    'playerHistory.villages': { label: 'Player history: Villages', needs: ['player'] },
    'playerHistory.popOHLC': { label: 'Player history: Population OHLC (candles)', needs: ['player'] },
    'playerHistory.envelope': { label: 'Player history: Population envelope (range area)', needs: ['player'] },
    'playerHistory.growthRate': { label: 'Player history: Growth rate over time', needs: ['player'] },
    'playerHistory.popAndVillages': { label: 'Player history: Population & villages (mixed)', needs: ['player'] },
  
    /* Alliance villages (/api/alliance/<tag>/villages) */
    'alliance.villagesQuadrants': { label: 'Alliance: Village count by quadrant (stacked)', needs: ['alliance', 'limitVillages'] },
    'alliance.populationByRegion': { label: 'Alliance: Population by region (stacked)', needs: ['alliance', 'limitVillages'] },
    'alliance.topPlayers': { label: 'Alliance: Top players (bar)', needs: ['alliance', 'topN'] },
    'alliance.villageDistribution': { label: 'Alliance: Village distribution (boxplot)', needs: ['alliance', 'limitVillages'] },
  
    /* Region villages (/api/region/<name>/villages) */
    'region.villagesQuadrants': { label: 'Region: Village count by quadrant (stacked)', needs: ['region', 'limitVillages'] },
    'region.populationByAlliance': { label: 'Region: Population by alliance (stacked)', needs: ['region', 'limitVillages'] },
    'region.topPlayers': { label: 'Region: Top players (bar)', needs: ['region', 'topN'] },
    'region.topAlliances': { label: 'Region: Top alliances (bar)', needs: ['region', 'topN'] },
  
    /* World villages (/api/villages/latest) */
    'world.villageDensity': { label: 'World: Village density heatmap (sample)', needs: ['limitVillages'] },
    'world.populationByRegion': { label: 'World: Population by region (bar)', needs: ['topN'] },
    'world.villagesByRegion': { label: 'World: Villages by region (bar)', needs: ['topN'] },
    'world.allianceDistribution': { label: 'World: Alliance distribution (donut)', needs: ['limitVillages'] },
  
    /* Comparisons */
    'compare.playersRadar': { label: 'Compare 2 players (radar)', needs: ['player', 'playerB'] },
    'compare.alliancesRadar': { label: 'Compare 2 alliances (radar)', needs: ['alliance', 'allianceB'] },
    'player.popVsTopRadial': { label: 'Player pop vs top player (radial)', needs: ['player'] },
    'alliance.popVsTopRadial': { label: 'Alliance pop vs top alliance (radial)', needs: ['alliance'] },
  
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
    line: ['playerHistory.population', 'playerHistory.villages', 'playerHistory.growthRate', 'players.topPop', 'alliances.topPopulation'],
    bar: ['players.topPop', 'players.topVillages', 'players.growthRate', 'alliances.topVillages', 'alliances.topPopulation', 'alliances.playerCount', 'alliance.topPlayers', 'region.topPlayers', 'region.topAlliances', 'world.populationByRegion', 'world.villagesByRegion'],
    donut: ['players.allianceShareTopPlayers', 'players.byAllianceCount', 'world.allianceDistribution'],
    area: ['playerHistory.population', 'playerHistory.villages', 'playerHistory.growthRate'],
    spark: ['playerHistory.population', 'playerHistory.villages', 'players.topPop'],
    scatter: ['players.popVsVillages', 'alliances.popVsVillages'],
    bubble: ['players.popVsVillages', 'alliances.popVsVillages'],
    heatmap: ['world.villageDensity'],
    candlestick: ['playerHistory.popOHLC'],
    radar: ['compare.playersRadar', 'compare.alliancesRadar'],
    radialbar: ['player.popVsTopRadial', 'alliance.popVsTopRadial'],
    treemap: ['players.topPop', 'players.byAlliancePop'],
    boxplot: ['players.popDistribution', 'players.villageDistribution', 'alliances.distribution', 'alliance.villageDistribution'],
    rangearea: ['playerHistory.envelope'],
    stackedbar: ['alliance.villagesQuadrants', 'alliance.populationByRegion', 'region.villagesQuadrants', 'region.populationByAlliance'],
    mixed: ['playerHistory.population', 'playerHistory.popAndVillages'],
    timeline: ['timeline.fromHistorySpacing']
  }))
  
  function defaultSourceForType (type) {
    const list = sourcesByChartType.value[type] || []
    return list[0] || ''
  }
  
  /* -----------------------------
   * Title generation for widgets
   * ----------------------------- */
  function getTitleForSource (sourceKey, params = {}) {
    if (!sourceKey) return 'Chart'
    
    const source = SOURCE_REGISTRY[sourceKey]
    if (!source) return 'Chart'
    
    // Player history sources
    if (sourceKey === 'playerHistory.population') {
      const player = params.playerName || 'Player'
      return `${player} - Population Growth`
    }
    if (sourceKey === 'playerHistory.villages') {
      const player = params.playerName || 'Player'
      return `${player} - Village Growth`
    }
    if (sourceKey === 'playerHistory.popOHLC') {
      const player = params.playerName || 'Player'
      return `${player} - Population OHLC`
    }
    if (sourceKey === 'playerHistory.envelope') {
      const player = params.playerName || 'Player'
      return `${player} - Population Range`
    }
    if (sourceKey === 'playerHistory.growthRate') {
      const player = params.playerName || 'Player'
      return `${player} - Growth Rate`
    }
    if (sourceKey === 'playerHistory.popAndVillages') {
      const player = params.playerName || 'Player'
      return `${player} - Population & Villages`
    }
    
    // Top players sources
    if (sourceKey === 'players.topPop') {
      const topN = params.topN || 10
      return `Top ${topN} Players by Population`
    }
    if (sourceKey === 'players.topVillages') {
      const topN = params.topN || 10
      return `Top ${topN} Players by Villages`
    }
    if (sourceKey === 'players.allianceShareTopPlayers') {
      const topN = params.topN || 15
      return `Alliance Share (Top ${topN} Players)`
    }
    if (sourceKey === 'players.growthRate') {
      const topN = params.topN || 10
      return `Top ${topN} Players - Growth Rate`
    }
    if (sourceKey === 'players.byAlliancePop') {
      const topN = params.topN || 10
      return `Top ${topN} Players - Population by Alliance`
    }
    if (sourceKey === 'players.byAllianceCount') {
      return 'Players by Alliance Count'
    }
    if (sourceKey === 'players.villageDistribution') {
      return 'Player Village Distribution'
    }
    
    // Alliances
    if (sourceKey === 'alliances.topVillages') {
      const topN = params.topN || 10
      return `Top ${topN} Alliances by Villages`
    }
    if (sourceKey === 'alliances.topPopulation') {
      const topN = params.topN || 10
      return `Top ${topN} Alliances by Population`
    }
    if (sourceKey === 'alliances.playerCount') {
      const topN = params.topN || 10
      return `Top ${topN} Alliances by Player Count`
    }
    
    // Alliance villages
    if (sourceKey === 'alliance.topPlayers') {
      const tag = params.allianceTag || 'Alliance'
      const topN = params.topN || 10
      return `${tag} - Top ${topN} Players`
    }
    if (sourceKey === 'alliance.populationByRegion') {
      const tag = params.allianceTag || 'Alliance'
      return `${tag} - Population by Region`
    }
    if (sourceKey === 'alliance.villageDistribution') {
      const tag = params.allianceTag || 'Alliance'
      return `${tag} - Village Distribution`
    }
    
    // Region villages
    if (sourceKey === 'region.topPlayers') {
      const region = params.regionName || 'Region'
      const topN = params.topN || 10
      return `${region} - Top ${topN} Players`
    }
    if (sourceKey === 'region.topAlliances') {
      const region = params.regionName || 'Region'
      const topN = params.topN || 10
      return `${region} - Top ${topN} Alliances`
    }
    if (sourceKey === 'region.populationByAlliance') {
      const region = params.regionName || 'Region'
      return `${region} - Population by Alliance`
    }
    
    // World sources
    if (sourceKey === 'world.populationByRegion') {
      const topN = params.topN || 10
      return `Top ${topN} Regions by Population`
    }
    if (sourceKey === 'world.villagesByRegion') {
      const topN = params.topN || 10
      return `Top ${topN} Regions by Villages`
    }
    if (sourceKey === 'world.allianceDistribution') {
      return 'World Alliance Distribution'
    }
    
    // Comparisons
    if (sourceKey === 'compare.playersRadar') {
      const a = params.playerName || 'Player A'
      const b = params.playerNameB || 'Player B'
      return `${a} vs ${b}`
    }
    if (sourceKey === 'player.popVsTopRadial') {
      const player = params.playerName || 'Player'
      return `${player} vs Top Player`
    }
    if (sourceKey === 'compare.alliancesRadar') {
      const a = params.allianceTag || 'Alliance A'
      const b = params.allianceTagB || 'Alliance B'
      return `${a} vs ${b}`
    }
    if (sourceKey === 'alliance.popVsTopRadial') {
      const tag = params.allianceTag || 'Alliance'
      return `${tag} vs Top Alliance`
    }
    
    // Alliance/Region quadrants
    if (sourceKey === 'alliance.villagesQuadrants') {
      const tag = params.allianceTag || 'Alliance'
      return `${tag} - Village Quadrants`
    }
    if (sourceKey === 'region.villagesQuadrants') {
      const region = params.regionName || 'Region'
      return `${region} - Village Quadrants`
    }
    
    // Other sources
    if (sourceKey === 'players.popVsVillages') {
      return 'Population vs Villages'
    }
    if (sourceKey === 'players.popDistribution') {
      return 'Population Distribution'
    }
    if (sourceKey === 'world.villageDensity') {
      return 'World Village Density'
    }
    if (sourceKey === 'timeline.fromHistorySpacing') {
      const player = params.playerName || 'Player'
      return `${player} - Timeline`
    }
    
    // Fallback to source label
    return source.label || 'Chart'
  }
  
  /* -----------------------------
   * Top player storage for auto-selection
   * ----------------------------- */
  const topPlayerName = ref('')
  
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
    
    // Auto-select top player if source needs player param and it's not set
    if (sourceNeeds(w.config.sourceKey, 'player') && !w.config.params.playerName && topPlayerName.value) {
      w.config.params.playerName = topPlayerName.value
    }
    
    // Auto-generate title if not set or is generic
    if (!w.title || w.title.startsWith('Chart ') || w.title === 'Scatter') {
      w.title = getTitleForSource(w.config.sourceKey, w.config.params)
    }
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
    // players (filter out NPC - Natars)
    optionsLoading.value.players = true
    try {
      const { data } = await api.get('/api/players?limit=10000')
      const rows = filterNpcPlayers((Array.isArray(data) ? data : []).map(normalizePlayerRow).filter(x => x.name))
      const sorted = [...rows].sort((a, b) => b.population - a.population)
      
      // Store top player name for auto-selection
      if (sorted.length > 0) {
        topPlayerName.value = sorted[0].name
      }
      
      playerOptionsAll.value = sorted
        .map(p => ({ label: `${p.name} (${p.population.toLocaleString()} pop)`, value: p.name }))
      playerOptionsFiltered.value = playerOptionsAll.value
    } catch {
      playerOptionsAll.value = []
      playerOptionsFiltered.value = []
      topPlayerName.value = ''
    } finally {
      optionsLoading.value.players = false
    }
  
    // alliances (filter out NPC - Natars)
    optionsLoading.value.alliances = true
    try {
      const { data } = await api.get('/api/alliances')
      const rows = filterNpcAlliances((Array.isArray(data) ? data : []).map(normalizeAllianceRow).filter(x => x.tag))
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
      return filterNpcPlayers((Array.isArray(data) ? data : []).map(normalizePlayerRow).filter(p => p.name))
    })
  }
  
  async function fetchAlliances () {
    return cached('alliances', async () => {
      const { data } = await api.get('/api/alliances')
      return filterNpcAlliances((Array.isArray(data) ? data : []).map(normalizeAllianceRow).filter(a => a.tag))
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

    if (sourceKey === 'players.villageDistribution') {
      const players = await fetchPlayers()
      const vills = players.map(p => Number(p.villages || 0)).filter(n => Number.isFinite(n)).sort((a, b) => a - b)
      if (!vills.length) return { series: [{ name: 'Distribution', data: [] }], color, colors }

      const bucketCount = 6
      const buckets = []
      for (let i = 0; i < bucketCount; i++) {
        const start = Math.floor((i / bucketCount) * vills.length)
        const end = Math.floor(((i + 1) / bucketCount) * vills.length)
        const slice = vills.slice(start, Math.max(start + 1, end))
        const min = slice[0]
        const max = slice[slice.length - 1]
        const q1 = slice[Math.floor(slice.length * 0.25)]
        const med = slice[Math.floor(slice.length * 0.5)]
        const q3 = slice[Math.floor(slice.length * 0.75)]
        buckets.push({ x: `B${i + 1}`, y: [min, q1, med, q3, max] })
      }
      return { series: [{ name: 'Villages', data: buckets }], color, colors }
    }

    if (sourceKey === 'players.byAlliancePop') {
      const players = await fetchPlayers()
      const top = [...players].sort((a, b) => b.population - a.population).slice(0, topN)
      
      // Group by alliance and sum population
      const allianceMap = new Map()
      for (const p of top) {
        const tag = (p.alliance && p.alliance.trim()) || 'No alliance'
        allianceMap.set(tag, (allianceMap.get(tag) || 0) + p.population)
      }
      
      const pairs = [...allianceMap.entries()].sort((a, b) => b[1] - a[1]).slice(0, 20)
      return {
        series: [{ data: pairs.map(([tag, pop]) => ({ x: tag, y: pop })) }],
        color,
        colors
      }
    }

    if (sourceKey === 'players.byAllianceCount') {
      const players = await fetchPlayers()
      const allianceMap = new Map()
      for (const p of players) {
        const tag = (p.alliance && p.alliance.trim()) || 'No alliance'
        allianceMap.set(tag, (allianceMap.get(tag) || 0) + 1)
      }
      
      const pairs = [...allianceMap.entries()].sort((a, b) => b[1] - a[1]).slice(0, 15)
      return {
        series: pairs.map(([, c]) => c),
        labels: pairs.map(([t]) => t),
        color,
        colors
      }
    }

    if (sourceKey === 'players.growthRate') {
      const players = await fetchPlayers()
      const top = [...players].sort((a, b) => b.population - a.population).slice(0, topN)
      
      // Calculate growth rate from history (simplified: compare recent vs older)
      const growthRates = await Promise.all(top.map(async (p) => {
        try {
          const hist = await fetchPlayerHistory(p.name)
          if (hist.length < 2) return { name: p.name, rate: 0 }
          const recent = hist.slice(-7) // last 7 days
          const older = hist.slice(0, Math.min(7, hist.length - 7))
          if (!older.length) return { name: p.name, rate: 0 }
          const recentAvg = recent.reduce((s, h) => s + Number(h.population || 0), 0) / recent.length
          const olderAvg = older.reduce((s, h) => s + Number(h.population || 0), 0) / older.length
          const rate = olderAvg > 0 ? ((recentAvg - olderAvg) / olderAvg) * 100 : 0
          return { name: p.name, rate: Math.round(rate * 10) / 10 }
        } catch {
          return { name: p.name, rate: 0 }
        }
      }))
      
      const sorted = growthRates.sort((a, b) => b.rate - a.rate)
      return {
        categories: sorted.map(r => r.name),
        series: [{ name: 'Growth Rate %', data: sorted.map(r => r.rate) }],
        color,
        colors,
        horizontal: true
      }
    }
  
    if (sourceKey === 'players.allianceShareTopPlayers') {
      const players = await fetchPlayers()
      const top = [...players].sort((a, b) => b.population - a.population).slice(0, topN)
      
      // Enrich with alliance data from villages if alliance is missing
      const playerAllianceMap = new Map()
      for (const p of top) {
        if (p.alliance && p.alliance.trim()) {
          playerAllianceMap.set(p.name, p.alliance.trim())
        }
      }
      
      // If we're missing alliance data, try to get it from villages (skip Natars)
      if (playerAllianceMap.size < top.length * 0.5) {
        try {
          const villages = await fetchWorldVillages(5000)
          for (const v of villages) {
            const playerName = String(v?.player_name ?? v?.player ?? '').trim()
            if (playerName && !playerAllianceMap.has(playerName)) {
              const alliance = String(v?.alliance ?? v?.alliance_tag ?? '').trim()
              if (alliance && !isNpcAlliance(alliance)) {
                playerAllianceMap.set(playerName, alliance)
              }
            }
          }
        } catch (e) {
          console.warn('Failed to enrich alliance data:', e)
        }
      }
      
      const map = new Map()
      for (const p of top) {
        let tag = playerAllianceMap.get(p.name) || (p.alliance && p.alliance.trim()) || 'No alliance'
        if (isNpcAlliance(tag)) tag = 'No alliance'
        map.set(tag, (map.get(tag) || 0) + 1)
      }
      
      // Filter out "No alliance" if there are other alliances, or keep it if it's significant
      const pairs = [...map.entries()].sort((a, b) => b[1] - a[1])
      const filtered = pairs.filter(([tag]) => {
        if (tag === 'No alliance') {
          // Only show "No alliance" if it's in top 3 or represents significant portion
          const noAllianceCount = map.get('No alliance') || 0
          const total = top.length
          return noAllianceCount >= 3 || (noAllianceCount / total) > 0.2
        }
        return true
      }).slice(0, 12)
      
      return {
        series: filtered.map(([, c]) => c),
        labels: filtered.map(([t]) => t),
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

    if (sourceKey === 'alliances.topPopulation') {
      const alliances = await fetchAlliances()
      const top = [...alliances].sort((a, b) => b.population - a.population).slice(0, topN)
      return { categories: top.map(a => a.tag), series: [{ name: 'Population', data: top.map(a => a.population) }], color, colors, horizontal: true }
    }

    if (sourceKey === 'alliances.playerCount') {
      const alliances = await fetchAlliances()
      // Estimate player count from villages data
      const enriched = await Promise.all(alliances.slice(0, topN).map(async (a) => {
        try {
          const villages = await fetchAllianceVillages(a.tag, 1000)
          const playerSet = new Set(villages.map(v => String(v?.player_name ?? v?.player ?? '').trim()).filter(Boolean))
          return { tag: a.tag, count: playerSet.size }
        } catch {
          return { tag: a.tag, count: 0 }
        }
      }))
      const sorted = enriched.sort((a, b) => b.count - a.count)
      return { categories: sorted.map(a => a.tag), series: [{ name: 'Players', data: sorted.map(a => a.count) }], color, colors, horizontal: true }
    }

    if (sourceKey === 'alliances.popVsVillages') {
      const alliances = await fetchAlliances()
      const pts = alliances.filter(a => Number.isFinite(a.population) && Number.isFinite(a.villages)).slice(0, 500)
      return {
        series: [{ name: 'Alliances', data: pts.map(a => [a.villages, a.population]) }],
        xTitle: 'Villages',
        yTitle: 'Population',
        color,
        colors
      }
    }

    if (sourceKey === 'alliances.distribution') {
      const alliances = await fetchAlliances()
      const pops = alliances.map(a => Number(a.population || 0)).filter(n => Number.isFinite(n)).sort((a, b) => a - b)
      if (!pops.length) return { series: [{ name: 'Distribution', data: [] }], color, colors }

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
  
    // -------- Alliance villages --------
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

    if (sourceKey === 'alliance.populationByRegion') {
      const tag = String(params.allianceTag || '').trim()
      if (!tag) throw new Error('Select an alliance for this source.')
      const rows = await fetchAllianceVillages(tag, villageLimit)

      const regionMap = new Map()
      for (const r of rows) {
        const region = String(r?.region ?? '').trim() || 'Unknown'
        const pop = Number(r?.population || 0)
        regionMap.set(region, (regionMap.get(region) || 0) + pop)
      }

      const pairs = [...regionMap.entries()].sort((a, b) => b[1] - a[1]).slice(0, 10)
      return {
        categories: pairs.map(([r]) => r),
        series: [{ name: tag, data: pairs.map(([, pop]) => pop) }],
        color,
        colors
      }
    }

    if (sourceKey === 'alliance.topPlayers') {
      const tag = String(params.allianceTag || '').trim()
      if (!tag) throw new Error('Select an alliance for this source.')
      const rows = await fetchAllianceVillages(tag, villageLimit)

      const playerMap = new Map()
      for (const r of rows) {
        const player = String(r?.player_name ?? r?.player ?? '').trim()
        if (!player) continue
        const pop = Number(r?.population || 0)
        playerMap.set(player, (playerMap.get(player) || 0) + pop)
      }

      const pairs = [...playerMap.entries()].sort((a, b) => b[1] - a[1]).slice(0, topN)
      return {
        categories: pairs.map(([p]) => p),
        series: [{ name: 'Population', data: pairs.map(([, pop]) => pop) }],
        color,
        colors,
        horizontal: true
      }
    }

    if (sourceKey === 'alliance.villageDistribution') {
      const tag = String(params.allianceTag || '').trim()
      if (!tag) throw new Error('Select an alliance for this source.')
      const rows = await fetchAllianceVillages(tag, villageLimit)

      // Count villages per player
      const playerVillageCounts = new Map()
      for (const r of rows) {
        const player = String(r?.player_name ?? r?.player ?? '').trim()
        if (player) {
          playerVillageCounts.set(player, (playerVillageCounts.get(player) || 0) + 1)
        }
      }

      const counts = [...playerVillageCounts.values()].sort((a, b) => a - b)
      if (!counts.length) return { series: [{ name: 'Distribution', data: [] }], color, colors }

      const bucketCount = 6
      const buckets = []
      for (let i = 0; i < bucketCount; i++) {
        const start = Math.floor((i / bucketCount) * counts.length)
        const end = Math.floor(((i + 1) / bucketCount) * counts.length)
        const slice = counts.slice(start, Math.max(start + 1, end))
        const min = slice[0]
        const max = slice[slice.length - 1]
        const q1 = slice[Math.floor(slice.length * 0.25)]
        const med = slice[Math.floor(slice.length * 0.5)]
        const q3 = slice[Math.floor(slice.length * 0.75)]
        buckets.push({ x: `B${i + 1}`, y: [min, q1, med, q3, max] })
      }
      return { series: [{ name: 'Villages per Player', data: buckets }], color, colors }
    }

    // -------- Region villages --------
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

    if (sourceKey === 'region.populationByAlliance') {
      const rn = String(params.regionName || '').trim()
      if (!rn) throw new Error('Select a region for this source.')
      const rows = await fetchRegionVillages(rn, villageLimit)

      const allianceMap = new Map()
      for (const r of rows) {
        const alliance = String(r?.alliance ?? r?.alliance_tag ?? '').trim() || 'No alliance'
        const pop = Number(r?.population || 0)
        allianceMap.set(alliance, (allianceMap.get(alliance) || 0) + pop)
      }

      const pairs = [...allianceMap.entries()].sort((a, b) => b[1] - a[1]).slice(0, 10)
      return {
        categories: pairs.map(([a]) => a),
        series: [{ name: rn, data: pairs.map(([, pop]) => pop) }],
        color,
        colors
      }
    }

    if (sourceKey === 'region.topPlayers') {
      const rn = String(params.regionName || '').trim()
      if (!rn) throw new Error('Select a region for this source.')
      const rows = await fetchRegionVillages(rn, villageLimit)

      const playerMap = new Map()
      for (const r of rows) {
        const player = String(r?.player_name ?? r?.player ?? '').trim()
        if (!player) continue
        const pop = Number(r?.population || 0)
        playerMap.set(player, (playerMap.get(player) || 0) + pop)
      }

      const pairs = [...playerMap.entries()].sort((a, b) => b[1] - a[1]).slice(0, topN)
      return {
        categories: pairs.map(([p]) => p),
        series: [{ name: 'Population', data: pairs.map(([, pop]) => pop) }],
        color,
        colors,
        horizontal: true
      }
    }

    if (sourceKey === 'region.topAlliances') {
      const rn = String(params.regionName || '').trim()
      if (!rn) throw new Error('Select a region for this source.')
      const rows = await fetchRegionVillages(rn, villageLimit)

      const allianceMap = new Map()
      for (const r of rows) {
        const alliance = String(r?.alliance ?? r?.alliance_tag ?? '').trim() || 'No alliance'
        const pop = Number(r?.population || 0)
        allianceMap.set(alliance, (allianceMap.get(alliance) || 0) + pop)
      }

      const pairs = [...allianceMap.entries()].sort((a, b) => b[1] - a[1]).slice(0, topN)
      return {
        categories: pairs.map(([a]) => a),
        series: [{ name: 'Population', data: pairs.map(([, pop]) => pop) }],
        color,
        colors,
        horizontal: true
      }
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

    if (sourceKey === 'world.populationByRegion') {
      const rows = await fetchWorldVillages(villageLimit)
      const regionMap = new Map()
      for (const r of rows) {
        const region = String(r?.region ?? '').trim() || 'Unknown'
        const pop = Number(r?.population || 0)
        regionMap.set(region, (regionMap.get(region) || 0) + pop)
      }

      const pairs = [...regionMap.entries()].sort((a, b) => b[1] - a[1]).slice(0, topN)
      return {
        categories: pairs.map(([r]) => r),
        series: [{ name: 'Population', data: pairs.map(([, pop]) => pop) }],
        color,
        colors,
        horizontal: true
      }
    }

    if (sourceKey === 'world.villagesByRegion') {
      const rows = await fetchWorldVillages(villageLimit)
      const regionMap = new Map()
      for (const r of rows) {
        const region = String(r?.region ?? '').trim() || 'Unknown'
        regionMap.set(region, (regionMap.get(region) || 0) + 1)
      }

      const pairs = [...regionMap.entries()].sort((a, b) => b[1] - a[1]).slice(0, topN)
      return {
        categories: pairs.map(([r]) => r),
        series: [{ name: 'Villages', data: pairs.map(([, count]) => count) }],
        color,
        colors,
        horizontal: true
      }
    }

    if (sourceKey === 'world.allianceDistribution') {
      const rows = await fetchWorldVillages(villageLimit)
      const allianceMap = new Map()
      for (const r of rows) {
        const alliance = String(r?.alliance ?? r?.alliance_tag ?? '').trim() || 'No alliance'
        allianceMap.set(alliance, (allianceMap.get(alliance) || 0) + 1)
      }

      const pairs = [...allianceMap.entries()].sort((a, b) => b[1] - a[1]).slice(0, 15)
      return {
        series: pairs.map(([, c]) => c),
        labels: pairs.map(([t]) => t),
        color,
        colors
      }
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

    if (sourceKey === 'compare.alliancesRadar') {
      const a = String(params.allianceTag || '').trim()
      const b = String(params.allianceTagB || '').trim()
      if (!a || !b) throw new Error('Select Alliance and Alliance B for this source.')
      
      const [villagesA, villagesB] = await Promise.all([
        fetchAllianceVillages(a, 1000),
        fetchAllianceVillages(b, 1000)
      ])

      const popA = villagesA.reduce((s, v) => s + Number(v?.population || 0), 0)
      const popB = villagesB.reduce((s, v) => s + Number(v?.population || 0), 0)
      const countA = villagesA.length
      const countB = villagesB.length

      const playerSetA = new Set(villagesA.map(v => String(v?.player_name ?? v?.player ?? '').trim()).filter(Boolean))
      const playerSetB = new Set(villagesB.map(v => String(v?.player_name ?? v?.player ?? '').trim()).filter(Boolean))

      const categories = ['Population', 'Villages', 'Players']
      return {
        categories,
        series: [
          { name: a, data: [popA, countA, playerSetA.size] },
          { name: b, data: [popB, countB, playerSetB.size] }
        ],
        color,
        colors
      }
    }

    if (sourceKey === 'alliance.popVsTopRadial') {
      const tag = String(params.allianceTag || '').trim()
      if (!tag) throw new Error('Select an alliance for this source.')
      const alliances = await fetchAlliances()
      const top = [...alliances].sort((a, b) => b.population - a.population)[0]
      const me = alliances.find(a => a.tag === tag)
      if (!me || !top) throw new Error('Alliance/top not found.')

      const pct = top.population > 0 ? Math.round((me.population / top.population) * 100) : 0
      return { series: [Math.max(0, Math.min(100, pct))], labels: ['% of top alliance pop'], color, colors }
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
    params: { playerName: '', playerNameB: '', allianceTag: '', allianceTagB: '', regionName: '', topN: 10, villageLimit: 5000 },
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
    
    // Auto-fill top player if source needs player and it's not set
    if (needs.includes('player') && !customizeDraft.value.params.playerName && topPlayerName.value) {
      customizeDraft.value.params.playerName = topPlayerName.value
    }
    
    // Update title based on new source
    customizeDraft.value.title = getTitleForSource(k, customizeDraft.value.params)
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
        allianceTagB: w.config?.params?.allianceTagB ?? '',
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
  
    if (isChartWidget(w)) {
      w.config.sourceKey = customizeDraft.value.sourceKey || w.config.sourceKey
      w.config.source = w.config.sourceKey // keep old field updated for backward compatibility
      w.config.params = { ...(w.config.params || {}), ...(customizeDraft.value.params || {}) }
      
      // Use provided title, or auto-generate if empty/generic
      if (customizeDraft.value.title && !customizeDraft.value.title.startsWith('Chart ') && customizeDraft.value.title !== 'Scatter') {
        w.title = customizeDraft.value.title
      } else {
        w.title = getTitleForSource(w.config.sourceKey, w.config.params)
      }
  
      w.config.colorMode = customizeDraft.value.colorMode === 'series' ? 'series' : 'single'
      if (w.config.colorMode === 'series') {
        const cleaned = (customizeDraft.value.colors || []).map(s => (s || '').trim()).filter(Boolean)
        w.config.colors = cleaned.length ? cleaned : [...DEFAULT_SERIES_COLORS]
        w.config.color = w.config.colors[0] || DEFAULT_COLOR
      } else {
        w.config.color = (customizeDraft.value.color || '').trim() || DEFAULT_COLOR
        delete w.config.colors
      }
    } else {
      w.title = customizeDraft.value.title
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
    { 
      id: 'line', 
      type: 'line', 
      title: 'Top Player Population Growth', 
      x: 0, 
      y: 0, 
      w: 60, 
      h: 8, 
      minW: 40, 
      minH: 6,
      config: {
        sourceKey: 'playerHistory.population',
        params: { playerName: '' }, // Will be auto-filled with top player
        color: DEFAULT_COLOR,
        colorMode: 'single'
      }
    },
    { 
      id: 'bar', 
      type: 'bar', 
      title: 'Top 10 Players by Population', 
      x: 60, 
      y: 0, 
      w: 60, 
      h: 8, 
      minW: 40, 
      minH: 6,
      config: {
        sourceKey: 'players.topPop',
        params: { topN: 10 },
        color: DEFAULT_COLOR,
        colorMode: 'single'
      }
    },
    { 
      id: 'donut', 
      type: 'donut', 
      title: 'Alliance Share (Top 15 Players)', 
      x: 0, 
      y: 8, 
      w: 40, 
      h: 7, 
      minW: 28, 
      minH: 5,
      config: {
        sourceKey: 'players.allianceShareTopPlayers',
        params: { topN: 15 },
        color: DEFAULT_COLOR,
        colorMode: 'series'
      }
    },
    { 
      id: 'area', 
      type: 'area', 
      title: 'Top Player Village Growth', 
      x: 40, 
      y: 8, 
      w: 40, 
      h: 7, 
      minW: 28, 
      minH: 5,
      config: {
        sourceKey: 'playerHistory.villages',
        params: { playerName: '' }, // Will be auto-filled with top player
        color: DEFAULT_COLOR,
        colorMode: 'single'
      }
    },
    { 
      id: 'scatter', 
      type: 'scatter', 
      title: 'Population vs Villages', 
      x: 80, 
      y: 8, 
      w: 40, 
      h: 7, 
      minW: 28, 
      minH: 5,
      config: {
        sourceKey: 'players.popVsVillages',
        params: {},
        color: DEFAULT_COLOR,
        colorMode: 'single'
      }
    }
  ]
  
  function cloneDefaults () {
    return defaultWidgets.map(w => {
      const ww = { ...w }
      if (isChartWidget(ww)) {
        ensureWidgetConfig(ww)
        // Update title after ensureWidgetConfig has set params
        if (ww.config?.sourceKey) {
          ww.title = getTitleForSource(ww.config.sourceKey, ww.config.params || {})
        }
      }
      return ww
    })
  }
  
  function loadWidgets () {
    // Prefer loaded layout from store
    if (layoutsStore.activeLayoutId) {
      const loaded = layoutsStore.loadLayout(layoutsStore.activeLayoutId)
      if (loaded && Array.isArray(loaded) && loaded.length) {
        return loaded.map(w => {
          const ww = { ...w }
          if (isChartWidget(ww)) ensureWidgetConfig(ww)
          return ww
        })
      }
    }
    // Fallback: legacy localStorage or defaults
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

  async function onLoadLayout (id) {
    layoutsStore.setActiveLayout(id)
    if (!id) {
      widgets.value = loadWidgets()
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
      return
    }
    const loaded = layoutsStore.loadLayout(id)
    if (!loaded || !Array.isArray(loaded) || !loaded.length) return
    const mapped = loaded.map(w => {
      const ww = { ...w }
      if (isChartWidget(ww)) ensureWidgetConfig(ww)
      return ww
    })
    widgets.value = mapped
    selectedLayoutId.value = id
    localStorage.setItem(STORAGE_KEY, JSON.stringify(mapped))
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
    Notify.create({ type: 'info', message: `Loaded layout: ${layoutsStore.getLayout(id)?.name ?? id}` })
  }

  function doSaveAs () {
    const name = saveAsName.value.trim()
    if (!name) return
    saveLayout()
    const merged = grid.value
      ? (() => {
          const items = grid.value.save(false)
          const byId = new Map(items.map(i => [i.id, i]))
          return widgets.value.map(w => {
            const i = byId.get(w.id)
            if (!i) return { ...w }
            return { ...w, x: i.x, y: i.y, w: i.w, h: i.h }
          })
        })()
      : [...widgets.value]
    layoutsStore.saveLayout(name, merged)
    selectedLayoutId.value = layoutsStore.activeLayoutId
    showSaveAsDialog.value = false
    saveAsName.value = ''
    Notify.create({ type: 'positive', message: `Saved layout: ${name}` })
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
    let merged = widgets.value
    if (grid.value) {
      const items = grid.value.save(false)
      const byId = new Map(items.map(i => [i.id, i]))
      merged = widgets.value.map(w => {
        const i = byId.get(w.id)
        if (!i) return { ...w }
        return { ...w, x: i.x, y: i.y, w: i.w, h: i.h }
      })
      widgets.value = merged
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(merged))
    if (layoutsStore.activeLayoutId) {
      const layout = layoutsStore.getLayout(layoutsStore.activeLayoutId)
      if (layout) layoutsStore.saveLayout(layout.name, merged)
    }
  }
  
  async function resetLayout () {
    localStorage.removeItem(STORAGE_KEY)
    layoutsStore.setActiveLayout(null)
    selectedLayoutId.value = null
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
    
    // Update widgets that need player/alliance/region params after options load
    widgets.value.forEach(w => {
      if (isChartWidget(w)) {
        ensureWidgetConfig(w)
        // Update title if it was auto-generated
        if (w.config?.sourceKey) {
          w.title = getTitleForSource(w.config.sourceKey, w.config.params || {})
        }
      }
    })
    
    // Save updated widget configs
    saveLayout()
    
    // Refresh all widgets with updated configs
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
  