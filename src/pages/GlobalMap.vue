<template>
  <q-page class="map-page fit q-pa-none">
    <!-- Desktop -->
    <q-splitter
      v-if="$q.screen.gt.sm"
      v-model="splitter"
      unit="px"
      :limits="[280, 520]"
      class="fit map-splitter"
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
            @update:showBackground="(val) => (showBackground = val)"
            @update:bgOpacity="(val) => (bgOpacity = val)"
            @update:showGrid="(val) => (showGrid = val)"
            @update:gridOpacity="(val) => (gridOpacity = val)"
            @update:gridSize="(val) => (gridSize = val)"
            @update:gotoX="(val) => (gotoX = val)"
            @update:gotoY="(val) => (gotoY = val)"
            @center-on-coords="centerOnCoords"
            @toggle-all-markers="toggleAllMarkers"
            @filter-group="filterGroup"
            @select-group="selectGroup"
            @update:drawMode="(val) => (drawMode = val)"
            @update:drawColor="(val) => (drawColor = val)"
            @update:drawWidth="(val) => (drawWidth = val)"
            @update:snapToGrid="(val) => (snapToGrid = val)"
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
          <!-- TOP HUD -->
          <div class="map-hud">
            <div class="map-hud__row">
              <q-input
                dense
                filled
                v-model="jumpInput"
                placeholder="Jump to x|y"
                class="map-hud__jump"
                @keyup.enter="jumpToInput"
              >
                <template #prepend><q-icon name="pin_drop" /></template>
                <template #append>
                  <q-btn flat dense icon="near_me" @click="jumpToInput">
                    <q-tooltip>Center on coordinates</q-tooltip>
                  </q-btn>
                </template>
              </q-input>

              <q-space />

              <div class="map-hud__zoom">
                <q-btn flat dense round icon="remove" @click="zoomBy(0.8)">
                  <q-tooltip>Zoom out</q-tooltip>
                </q-btn>

                <q-slider
                  dense
                  v-model="zoomSlider"
                  :min="Math.round(MIN_ZOOM_K * 100)"
                  :max="500"
                  :step="1"
                  @change="applyZoomSlider"
                  class="map-hud__slider"
                />

                <div class="map-hud__zoomtext">{{ zoomSlider }}%</div>

                <q-btn flat dense round icon="add" @click="zoomBy(1.25)">
                  <q-tooltip>Zoom in</q-tooltip>
                </q-btn>
              </div>

              <q-btn flat dense round icon="timelapse" class="map-hud__distbtn">
  <q-tooltip>Distance & travel time</q-tooltip>
  <q-menu anchor="bottom right" self="top right" class="distance-menu">
    <q-card class="distance-card">
      <q-card-section class="distance-card__head">
        <div class="distance-card__title">
          <q-icon name="timelapse" size="18px" class="q-mr-sm" />
          Distance & travel time
        </div>
        <q-space />
        <q-btn dense flat round icon="my_location" @click="setRefToCursor">
          <q-tooltip>Set reference to cursor</q-tooltip>
        </q-btn>
        <q-btn dense flat round icon="center_focus_strong" @click="setRefToViewCenter">
          <q-tooltip>Set reference to view center</q-tooltip>
        </q-btn>
        <q-btn dense flat round icon="pin_drop" :disable="!ctx.point" @click="setRefToContext">
          <q-tooltip>Set reference to last right-click</q-tooltip>
        </q-btn>
      </q-card-section>

      <q-separator />

      <q-card-section class="distance-card__body">
        <div class="row q-col-gutter-sm">
          <div class="col-12">
            <q-input
              dense
              filled
              v-model="refInput"
              label="Reference (x|y)"
              placeholder="e.g. 0|0"
              @keyup.enter="applyRefInput"
            >
              <template #append>
                <q-btn flat dense icon="check" @click="applyRefInput">
                  <q-tooltip>Apply</q-tooltip>
                </q-btn>
              </template>
            </q-input>
          </div>

          <div class="col-6">
            <q-select
              dense
              filled
              v-model="tribe"
              :options="tribeOptions"
              label="Tribe"
              emit-value
              map-options
            />
          </div>

          <div class="col-6">
            <q-toggle v-model="isSpeedServer" label="Speed server (×2)" dense />
          </div>

          <div class="col-12">
            <div class="distance-card__meta">
              <div>Cursor: <b>{{ Math.round(cursor.x) }}|{{ Math.round(-cursor.y) }}</b></div>
              <div>Ref: <b>{{ Math.round(refPoint.x) }}|{{ Math.round(-refPoint.y) }}</b></div>
              <div>Distance: <b>{{ distanceTiles.toFixed(2) }}</b> tiles</div>
            </div>
          </div>

          <div class="col-12">
            <div class="row items-center q-gutter-sm">
              <div class="text-caption">Tournament Square level: <b>{{ tsLevel }}</b> (speedup {{ tsSpeedup.toFixed(1) }}×)</div>
            </div>
            <q-slider dense v-model="tsLevel" :min="0" :max="20" :step="1" label label-always />
          </div>

          <div class="col-12">
            <q-markup-table dense flat class="distance-card__table">
              <thead>
                <tr>
                  <th class="text-left">Unit</th>
                  <th class="text-right">Time</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in travelRows" :key="row.key" :class="{ 'is-highlight': row.highlight }">
                  <td class="text-left">{{ row.label }}</td>
                  <td class="text-right"><b v-if="row.highlight">{{ row.time }}</b><span v-else>{{ row.time }}</span></td>
                </tr>
              </tbody>
            </q-markup-table>
          </div>
        </div>
      </q-card-section>
    </q-card>
  </q-menu>
</q-btn>

<q-btn flat dense round icon="square_foot" :class="{ 'is-active': showRulers }" @click="toggleRulers">
                <q-tooltip>Toggle rulers</q-tooltip>
              </q-btn>

              <q-btn flat dense round :icon="showGrid ? 'grid_on' : 'grid_off'" @click="showGrid = !showGrid">
                <q-tooltip>Toggle grid</q-tooltip>
              </q-btn>

              <q-btn
                flat
                dense
                round
                :icon="showBackground ? 'wallpaper' : 'hide_image'"
                @click="showBackground = !showBackground"
              >
                <q-tooltip>Toggle background</q-tooltip>
              </q-btn>

              <q-btn flat dense round icon="refresh" @click="resetView">
                <q-tooltip>Reset view</q-tooltip>
              </q-btn>

              <q-btn flat dense round icon="fullscreen" @click="toggleFullscreen">
                <q-tooltip>Fullscreen (F)</q-tooltip>
              </q-btn>

              <q-btn flat dense round icon="image" @click="exportPng">
                <q-tooltip>Export PNG</q-tooltip>
              </q-btn>

              <q-btn flat dense round icon="help_outline" @click="helpOpen = true">
                <q-tooltip>Shortcuts</q-tooltip>
              </q-btn>
            </div>
          </div>

          <!-- RIGHT FLOATING DRAW PANEL -->
          <div class="draw-panel">
            <q-card class="draw-panel__card">
              <div class="draw-panel__head">
                <div class="draw-panel__title">
                  <q-icon name="draw" size="18px" class="q-mr-sm" />
                  Draw & Measure
                </div>

                <q-space />

                <q-btn dense flat round icon="more_vert" class="draw-panel__iconbtn">
                  <q-tooltip>More</q-tooltip>
                  <q-menu anchor="bottom right" self="top right" class="draw-panel__menu">
                    <q-list style="min-width: 220px">
                      <q-item-label header>Storage</q-item-label>

                      <q-item clickable v-close-popup @click="saveToLocal">
                        <q-item-section avatar><q-icon name="save" /></q-item-section>
                        <q-item-section>Save drawings (local)</q-item-section>
                      </q-item>

                      <q-item clickable v-close-popup @click="loadFromLocal">
                        <q-item-section avatar><q-icon name="restore" /></q-item-section>
                        <q-item-section>Load drawings (local)</q-item-section>
                      </q-item>

                      <q-separator />

                      <q-item clickable v-close-popup @click="exportDrawings">
                        <q-item-section avatar><q-icon name="download" /></q-item-section>
                        <q-item-section>Export drawings JSON</q-item-section>
                      </q-item>

                      <q-item clickable v-close-popup @click="importDrawings">
                        <q-item-section avatar><q-icon name="upload" /></q-item-section>
                        <q-item-section>Import drawings JSON</q-item-section>
                      </q-item>
                    </q-list>
                  </q-menu>
                </q-btn>

                <q-btn
                  dense
                  flat
                  round
                  :icon="drawPanelOpen ? 'expand_less' : 'expand_more'"
                  class="draw-panel__iconbtn"
                  @click="drawPanelOpen = !drawPanelOpen"
                >
                  <q-tooltip>{{ drawPanelOpen ? 'Collapse' : 'Expand' }}</q-tooltip>
                </q-btn>
              </div>

              <q-separator />

              <div v-show="drawPanelOpen" class="draw-panel__body">
                <div class="draw-panel__section">
                  <div class="draw-panel__label">Mode</div>

                  <div class="draw-panel__modes">
                    <q-btn dense flat icon="block" class="draw-panel__modebtn" :class="{ 'is-active': !drawMode }" @click="setDrawMode(null)">
                      <q-tooltip>Off</q-tooltip>
                    </q-btn>
                    <q-btn dense flat icon="show_chart" class="draw-panel__modebtn" :class="{ 'is-active': drawMode === 'line' }" @click="setDrawMode('line')">
                      <q-tooltip>Line</q-tooltip>
                    </q-btn>
                    <q-btn dense flat icon="crop_square" class="draw-panel__modebtn" :class="{ 'is-active': drawMode === 'rect' }" @click="setDrawMode('rect')">
                      <q-tooltip>Rect</q-tooltip>
                    </q-btn>
                    <q-btn dense flat icon="radio_button_unchecked" class="draw-panel__modebtn" :class="{ 'is-active': drawMode === 'circle' }" @click="setDrawMode('circle')">
                      <q-tooltip>Circle</q-tooltip>
                    </q-btn>
                    <q-btn dense flat icon="gesture" class="draw-panel__modebtn" :class="{ 'is-active': drawMode === 'path' }" @click="setDrawMode('path')">
                      <q-tooltip>Freehand</q-tooltip>
                    </q-btn>
                    <q-btn dense flat icon="title" class="draw-panel__modebtn" :class="{ 'is-active': drawMode === 'text' }" @click="setDrawMode('text')">
                      <q-tooltip>Text</q-tooltip>
                    </q-btn>
                    <q-btn dense flat icon="straighten" class="draw-panel__modebtn" :class="{ 'is-active': drawMode === 'measure' }" @click="toggleMeasureMode">
                      <q-tooltip>Measure</q-tooltip>
                    </q-btn>
                  </div>
                </div>

                <div class="draw-panel__section">
                  <div class="draw-panel__row">
                    <div class="draw-panel__label">Style</div>
                    <q-space />
                    <q-btn dense flat icon="tune" class="draw-panel__pill">
                      <q-tooltip>Advanced style</q-tooltip>
                      <q-menu anchor="bottom right" self="top right" class="draw-panel__menu">
                        <q-list style="min-width: 260px">
                          <q-item-label header>Color</q-item-label>
                          <q-item>
                            <q-item-section>
                              <q-input dense filled v-model="drawColor" label="Color (hex)" />
                            </q-item-section>
                          </q-item>

                          <q-separator />

                          <q-item-label header>Width</q-item-label>
                          <q-item>
                            <q-item-section>
                              <q-slider dense v-model="drawWidth" :min="1" :max="10" :step="1" label label-always />
                            </q-item-section>
                          </q-item>
                        </q-list>
                      </q-menu>
                    </q-btn>
                  </div>

                  <div class="draw-panel__row">
                    <div class="draw-panel__swatches">
                      <button
                        v-for="c in quickColors"
                        :key="c"
                        class="swatch"
                        :class="{ 'is-active': drawColor.toLowerCase() === c }"
                        :style="{ background: c }"
                        @click="setColor(c)"
                        type="button"
                      />
                    </div>

                    <q-space />

                    <div class="draw-panel__widths">
                      <q-btn
                        v-for="w in quickWidths"
                        :key="w"
                        dense
                        flat
                        class="draw-panel__pill"
                        :class="{ 'is-active': drawWidth === w }"
                        @click="drawWidth = w"
                      >
                        {{ w }}
                      </q-btn>
                    </div>
                  </div>
                </div>

                <div class="draw-panel__section">
                  <div class="draw-panel__label">Actions</div>

                  <div class="draw-panel__actions">
                    <q-btn dense flat icon="undo" class="draw-panel__actionbtn" :disable="!canUndo" @click="undo">
                      <q-tooltip>Undo (Ctrl/⌘+Z)</q-tooltip>
                    </q-btn>
                    <q-btn dense flat icon="redo" class="draw-panel__actionbtn" :disable="!canRedo" @click="redo">
                      <q-tooltip>Redo (Ctrl/⌘+Y)</q-tooltip>
                    </q-btn>
                    <q-btn dense flat icon="grid_4x4" class="draw-panel__actionbtn" :class="{ 'is-active': snapToGrid }" @click="snapToGrid = !snapToGrid">
                      <q-tooltip>Snap to grid</q-tooltip>
                    </q-btn>
                    <q-btn dense flat icon="delete_sweep" class="draw-panel__actionbtn" @click="clearDrawings">
                      <q-tooltip>Clear drawings</q-tooltip>
                    </q-btn>
                  </div>
                </div>
              </div>
            </q-card>
          </div>

          <!-- FULL-HEIGHT MAP STAGE -->
          <div class="map-stage" ref="stageEl">
            <div class="svg-square" ref="squareEl">
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
                    <path
                      :d="`M${gridSize} 0 L0 0 L0 ${gridSize}`"
                      fill="none"
                      stroke="gray"
                      stroke-width="0.05"
                      :opacity="gridOpacity"
                    />
                  </pattern>
                </defs>

                <g id="viewport">
                  <rect x="-100000" y="-100000" width="200000" height="200000" fill="#000" />

                  <rect
                    :x="MAP_CONTAINER.x"
                    :y="MAP_CONTAINER.y"
                    :width="MAP_CONTAINER.width"
                    :height="MAP_CONTAINER.height"
                    fill="rgba(255,255,255,0.02)"
                    stroke="rgba(255,255,255,0.06)"
                    stroke-width="0.6"
                    vector-effect="non-scaling-stroke"
                  />

                  <rect
                    :x="MAP_WORLD.x"
                    :y="MAP_WORLD.y"
                    :width="MAP_WORLD.width"
                    :height="MAP_WORLD.height"
                    fill="rgba(0,0,0,0)"
                    stroke="rgba(0,255,255,0.18)"
                    stroke-width="0.9"
                    stroke-dasharray="3 3"
                    vector-effect="non-scaling-stroke"
                  />

                  <image
                    id="bgImage"
                    :x="bgRect.x"
                    :y="bgRect.y"
                    :width="bgRect.width"
                    :height="bgRect.height"
                    :style="{ display: showBackground ? 'block' : 'none', opacity: bgOpacity }"
                    href="/background.png"
                    preserveAspectRatio="none"
                  />

                  <rect
                    id="gridRect"
                    x="-100000"
                    y="-100000"
                    width="200000"
                    height="200000"
                    :style="{ display: showGrid ? 'block' : 'none' }"
                    fill="url(#grid)"
                  />

                  <line x1="-20000" y1="0" x2="20000" y2="0" stroke="white" stroke-width="0.1" opacity="0.12" />
                  <line x1="0" y1="-20000" x2="0" y2="20000" stroke="white" stroke-width="0.1" opacity="0.12" />

                  <g ref="markersGroup" id="markersLayer" v-html="markers"></g>

                  <g id="drawLayer" style="pointer-events: none">
                    <template v-for="(d, i) in drawings" :key="i">
                      <line v-if="d.type === 'line'" :x1="d.x1" :y1="d.y1" :x2="d.x2" :y2="d.y2" v-bind="d.style" />
                      <rect v-else-if="d.type === 'rect'" :x="d.x" :y="d.y" :width="d.width" :height="d.height" v-bind="d.style" />
                      <circle v-else-if="d.type === 'circle'" :cx="d.cx" :cy="d.cy" :r="d.r" v-bind="d.style" />
                      <path v-else-if="d.type === 'path'" :d="d.d" fill="none" v-bind="d.style" />
                      <g v-else-if="d.type === 'measure'">
                        <line :x1="d.x1" :y1="d.y1" :x2="d.x2" :y2="d.y2" v-bind="d.style" />
                        <text :x="(d.x1 + d.x2) / 2" :y="(d.y1 + d.y2) / 2 - 0.5" font-size="1.5" text-anchor="middle" class="measure-label">
                          {{ Number(d.distance).toFixed(1) }} tiles
                        </text>
                      </g>
                      <text v-else-if="d.type === 'text'" :x="d.x" :y="d.y" v-bind="d.style">{{ d.text }}</text>
                    </template>
                  </g>

                  <g id="previewLayer" ref="previewLayer" style="pointer-events: none"></g>
                </g>

                <!-- RULERS -->
                <g v-if="showRulers" id="rulerOverlay" style="pointer-events: none">
                  <rect :x="0" :y="0" :width="rulerW" :height="rulerThickness" fill="rgba(0,0,0,0.55)" />
                  <rect :x="0" :y="0" :width="rulerThickness" :height="rulerH" fill="rgba(0,0,0,0.55)" />

                  <g>
                    <template v-for="t in rulerXTicks" :key="'x' + t.value">
                      <line
                        :x1="t.px"
                        :y1="rulerThickness"
                        :x2="t.px"
                        :y2="rulerThickness - (t.major ? 10 : 6)"
                        stroke="rgba(255,255,255,0.75)"
                        stroke-width="1"
                      />
                      <text
                        v-if="t.major"
                        :x="t.px"
                        :y="12"
                        fill="rgba(255,255,255,0.92)"
                        font-size="10"
                        text-anchor="middle"
                      >
                        {{ t.label }}
                      </text>
                    </template>
                  </g>

                  <g>
                    <template v-for="t in rulerYTicks" :key="'y' + t.value">
                      <line
                        :x1="rulerThickness"
                        :y1="t.py"
                        :x2="rulerThickness - (t.major ? 10 : 6)"
                        :y2="t.py"
                        stroke="rgba(255,255,255,0.75)"
                        stroke-width="1"
                      />
                      <text
                        v-if="t.major"
                        :x="12"
                        :y="t.py + 3"
                        fill="rgba(255,255,255,0.92)"
                        font-size="10"
                        text-anchor="start"
                      >
                        {{ t.label }}
                      </text>
                    </template>
                  </g>
                </g>
              </svg>

              <!-- MINIMAP -->
              <div class="minimap" v-if="minimapReady">
                <div class="minimap__header">
                  <div class="minimap__title">Minimap</div>

                  <div class="minimap__actions">
                    <q-btn dense flat round icon="remove" @click.stop="minimapZoomBy(0.85)">
                      <q-tooltip>Minimap zoom out</q-tooltip>
                    </q-btn>
                    <q-btn dense flat round icon="add" @click.stop="minimapZoomBy(1.18)">
                      <q-tooltip>Minimap zoom in</q-tooltip>
                    </q-btn>
                    <q-btn dense flat round icon="my_location" @click.stop="minimapRecenterToView()">
                      <q-tooltip>Recenter minimap</q-tooltip>
                    </q-btn>
                    <q-btn dense flat round icon="crop_free" @click.stop="minimapFitAll()">
                      <q-tooltip>Fit minimap</q-tooltip>
                    </q-btn>
                  </div>
                </div>

                <svg
                  ref="minimapSvg"
                  class="minimap__svg"
                  :viewBox="`${minimapView.x} ${minimapView.y} ${minimapView.width} ${minimapView.height}`"
                  @pointerdown.prevent="onMinimapPointerDown"
                  @pointermove.prevent="onMinimapPointerMove"
                  @pointerup.prevent="onMinimapPointerUp"
                  @pointercancel.prevent="onMinimapPointerUp"
                  @wheel.prevent="onMinimapWheel"
                >
                  <rect
                    :x="minimapBounds.x"
                    :y="minimapBounds.y"
                    :width="minimapBounds.width"
                    :height="minimapBounds.height"
                    fill="rgba(0,0,0,0.28)"
                    stroke="rgba(255,255,255,0.16)"
                    stroke-width="2"
                    rx="18"
                    ry="18"
                  />

                  <rect
                    :x="MAP_WORLD.x"
                    :y="MAP_WORLD.y"
                    :width="MAP_WORLD.width"
                    :height="MAP_WORLD.height"
                    fill="rgba(0,0,0,0)"
                    stroke="rgba(0,255,255,0.35)"
                    stroke-width="2"
                    stroke-dasharray="5 4"
                    vector-effect="non-scaling-stroke"
                    rx="10"
                    ry="10"
                  />

                  <rect
                    v-if="showBackground"
                    :x="bgRect.x"
                    :y="bgRect.y"
                    :width="bgRect.width"
                    :height="bgRect.height"
                    fill="rgba(255,255,255,0.03)"
                    stroke="rgba(255,255,255,0.06)"
                    stroke-width="2"
                  />

                  <g v-if="minimapPoints.length" opacity="0.85">
                    <circle
                      v-for="(p, i) in minimapPoints"
                      :key="i"
                      :cx="p.x"
                      :cy="p.y"
                      :r="p.r"
                      fill="rgba(255,255,255,0.35)"
                    />
                  </g>

                  <rect
                    class="minimap__viewport"
                    :x="viewWorld.x"
                    :y="viewWorld.y"
                    :width="viewWorld.width"
                    :height="viewWorld.height"
                    fill="rgba(0,255,255,0.10)"
                    stroke="rgba(0,255,255,0.75)"
                    stroke-width="3"
                    rx="10"
                    ry="10"
                  />

                  <circle
                    :cx="cursor.x"
                    :cy="cursor.y"
                    r="10"
                    fill="rgba(255,255,255,0.9)"
                    stroke="rgba(0,0,0,0.55)"
                    stroke-width="3"
                  />
                </svg>

                <div class="minimap__footer">
                  <div class="minimap__line">Cursor: <b>{{ Math.round(cursor.x) }}|{{ Math.round(-cursor.y) }}</b></div>
                  <div class="minimap__line">
                    Center: <b>{{ Math.round(viewCenter.x) }}|{{ Math.round(-viewCenter.y) }}</b>
                    <span class="minimap__muted">·</span>
                    <span class="minimap__muted">Zoom {{ zoomK.toFixed(2) }}×</span>
                  </div>
                </div>
              </div>

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
          </div>

          <div class="statusbar row items-center q-px-sm q-py-xs">
            <div class="col text-caption">Zoom: {{ zoomK.toFixed(2) }}×</div>
            <div class="col text-caption text-right">Cursor: {{ Math.round(cursor.x) }}|{{ Math.round(-cursor.y) }} <span class="statusbar__sep">·</span> Dist: {{ distanceTiles.toFixed(1) }}</div>
          </div>
        </div>
      </template>
    </q-splitter>

    <!-- Mobile -->
    <div v-else class="map-column">
      <div class="map-hud">
        <div class="map-hud__row">
          <q-input dense filled v-model="jumpInput" placeholder="Jump to x|y" class="map-hud__jump" @keyup.enter="jumpToInput">
            <template #prepend><q-icon name="pin_drop" /></template>
            <template #append><q-btn flat dense icon="near_me" @click="jumpToInput" /></template>
          </q-input>

          <q-space />

          <q-btn flat dense round icon="timelapse" class="map-hud__distbtn">
  <q-menu anchor="bottom right" self="top right" class="distance-menu">
    <q-card class="distance-card">
      <q-card-section class="distance-card__head">
        <div class="distance-card__title">
          <q-icon name="timelapse" size="18px" class="q-mr-sm" />
          Distance & travel time
        </div>
        <q-space />
        <q-btn dense flat round icon="my_location" @click="setRefToCursor" />
        <q-btn dense flat round icon="center_focus_strong" @click="setRefToViewCenter" />
        <q-btn dense flat round icon="pin_drop" :disable="!ctx.point" @click="setRefToContext" />
      </q-card-section>
      <q-separator />
      <q-card-section class="distance-card__body">
        <q-input dense filled v-model="refInput" label="Reference (x|y)" placeholder="e.g. 0|0" @keyup.enter="applyRefInput">
          <template #append>
            <q-btn flat dense icon="check" @click="applyRefInput" />
          </template>
        </q-input>

        <div class="row q-col-gutter-sm q-mt-sm">
          <div class="col-6">
            <q-select dense filled v-model="tribe" :options="tribeOptions" label="Tribe" emit-value map-options />
          </div>
          <div class="col-6">
            <q-toggle v-model="isSpeedServer" label="Speed ×2" dense />
          </div>
        </div>

        <div class="distance-card__meta q-mt-sm">
          <div>Cursor: <b>{{ Math.round(cursor.x) }}|{{ Math.round(-cursor.y) }}</b></div>
          <div>Ref: <b>{{ Math.round(refPoint.x) }}|{{ Math.round(-refPoint.y) }}</b></div>
          <div>Distance: <b>{{ distanceTiles.toFixed(2) }}</b> tiles</div>
        </div>

        <div class="q-mt-sm text-caption">Tournament Square level: <b>{{ tsLevel }}</b> (speedup {{ tsSpeedup.toFixed(1) }}×)</div>
        <q-slider dense v-model="tsLevel" :min="0" :max="20" :step="1" label label-always />

        <q-markup-table dense flat class="distance-card__table q-mt-sm">
          <thead>
            <tr>
              <th class="text-left">Unit</th>
              <th class="text-right">Time</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in travelRows" :key="row.key" :class="{ 'is-highlight': row.highlight }">
              <td class="text-left">{{ row.label }}</td>
              <td class="text-right"><b v-if="row.highlight">{{ row.time }}</b><span v-else>{{ row.time }}</span></td>
            </tr>
          </tbody>
        </q-markup-table>
      </q-card-section>
    </q-card>
  </q-menu>
</q-btn>

<q-btn flat dense round icon="square_foot" :class="{ 'is-active': showRulers }" @click="toggleRulers" />
          <q-btn flat dense round :icon="showGrid ? 'grid_on' : 'grid_off'" @click="showGrid = !showGrid" />
          <q-btn flat dense round :icon="showBackground ? 'wallpaper' : 'hide_image'" @click="showBackground = !showBackground" />
          <q-btn flat dense round icon="refresh" @click="resetView" />
          <q-btn flat dense round icon="help_outline" @click="helpOpen = true" />
        </div>
      </div>

      <div class="draw-panel draw-panel--mobile">
        <q-card class="draw-panel__card">
          <div class="draw-panel__head">
            <div class="draw-panel__title">
              <q-icon name="draw" size="18px" class="q-mr-sm" />
              Draw & Measure
            </div>

            <q-space />

            <q-btn dense flat round icon="more_vert" class="draw-panel__iconbtn">
              <q-menu anchor="bottom right" self="top right" class="draw-panel__menu">
                <q-list style="min-width: 220px">
                  <q-item-label header>Storage</q-item-label>

                  <q-item clickable v-close-popup @click="saveToLocal">
                    <q-item-section avatar><q-icon name="save" /></q-item-section>
                    <q-item-section>Save drawings (local)</q-item-section>
                  </q-item>

                  <q-item clickable v-close-popup @click="loadFromLocal">
                    <q-item-section avatar><q-icon name="restore" /></q-item-section>
                    <q-item-section>Load drawings (local)</q-item-section>
                  </q-item>

                  <q-separator />

                  <q-item clickable v-close-popup @click="exportDrawings">
                    <q-item-section avatar><q-icon name="download" /></q-item-section>
                    <q-item-section>Export drawings JSON</q-item-section>
                  </q-item>

                  <q-item clickable v-close-popup @click="importDrawings">
                    <q-item-section avatar><q-icon name="upload" /></q-item-section>
                    <q-item-section>Import drawings JSON</q-item-section>
                  </q-item>
                </q-list>
              </q-menu>
            </q-btn>

            <q-btn dense flat round :icon="drawPanelOpen ? 'expand_less' : 'expand_more'" class="draw-panel__iconbtn" @click="drawPanelOpen = !drawPanelOpen" />
          </div>

          <q-separator />

          <div v-show="drawPanelOpen" class="draw-panel__body">
            <div class="draw-panel__section">
              <div class="draw-panel__label">Mode</div>

              <div class="draw-panel__modes">
                <q-btn dense flat icon="block" class="draw-panel__modebtn" :class="{ 'is-active': !drawMode }" @click="setDrawMode(null)" />
                <q-btn dense flat icon="show_chart" class="draw-panel__modebtn" :class="{ 'is-active': drawMode === 'line' }" @click="setDrawMode('line')" />
                <q-btn dense flat icon="crop_square" class="draw-panel__modebtn" :class="{ 'is-active': drawMode === 'rect' }" @click="setDrawMode('rect')" />
                <q-btn dense flat icon="radio_button_unchecked" class="draw-panel__modebtn" :class="{ 'is-active': drawMode === 'circle' }" @click="setDrawMode('circle')" />
                <q-btn dense flat icon="gesture" class="draw-panel__modebtn" :class="{ 'is-active': drawMode === 'path' }" @click="setDrawMode('path')" />
                <q-btn dense flat icon="title" class="draw-panel__modebtn" :class="{ 'is-active': drawMode === 'text' }" @click="setDrawMode('text')" />
                <q-btn dense flat icon="straighten" class="draw-panel__modebtn" :class="{ 'is-active': drawMode === 'measure' }" @click="toggleMeasureMode" />
              </div>
            </div>

            <div class="draw-panel__section">
              <div class="draw-panel__row">
                <div class="draw-panel__label">Style</div>
                <q-space />
                <q-btn dense flat icon="tune" class="draw-panel__pill">
                  <q-menu anchor="bottom right" self="top right" class="draw-panel__menu">
                    <q-list style="min-width: 260px">
                      <q-item-label header>Color</q-item-label>
                      <q-item>
                        <q-item-section>
                          <q-input dense filled v-model="drawColor" label="Color (hex)" />
                        </q-item-section>
                      </q-item>
                      <q-separator />
                      <q-item-label header>Width</q-item-label>
                      <q-item>
                        <q-item-section>
                          <q-slider dense v-model="drawWidth" :min="1" :max="10" :step="1" label label-always />
                        </q-item-section>
                      </q-item>
                    </q-list>
                  </q-menu>
                </q-btn>
              </div>

              <div class="draw-panel__row">
                <div class="draw-panel__swatches">
                  <button
                    v-for="c in quickColors"
                    :key="c"
                    class="swatch"
                    :class="{ 'is-active': drawColor.toLowerCase() === c }"
                    :style="{ background: c }"
                    @click="setColor(c)"
                    type="button"
                  />
                </div>

                <q-space />

                <div class="draw-panel__widths">
                  <q-btn v-for="w in quickWidths" :key="w" dense flat class="draw-panel__pill" :class="{ 'is-active': drawWidth === w }" @click="drawWidth = w">
                    {{ w }}
                  </q-btn>
                </div>
              </div>
            </div>

            <div class="draw-panel__section">
              <div class="draw-panel__label">Actions</div>

              <div class="draw-panel__actions">
                <q-btn dense flat icon="undo" class="draw-panel__actionbtn" :disable="!canUndo" @click="undo" />
                <q-btn dense flat icon="redo" class="draw-panel__actionbtn" :disable="!canRedo" @click="redo" />
                <q-btn dense flat icon="grid_4x4" class="draw-panel__actionbtn" :class="{ 'is-active': snapToGrid }" @click="snapToGrid = !snapToGrid" />
                <q-btn dense flat icon="delete_sweep" class="draw-panel__actionbtn" @click="clearDrawings" />
              </div>
            </div>
          </div>
        </q-card>
      </div>

      <div class="map-stage" ref="stageEl">
        <div class="svg-square" ref="squareEl">
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

              <rect
                :x="MAP_CONTAINER.x"
                :y="MAP_CONTAINER.y"
                :width="MAP_CONTAINER.width"
                :height="MAP_CONTAINER.height"
                fill="rgba(255,255,255,0.02)"
                stroke="rgba(255,255,255,0.06)"
                stroke-width="0.6"
                vector-effect="non-scaling-stroke"
              />
              <rect
                :x="MAP_WORLD.x"
                :y="MAP_WORLD.y"
                :width="MAP_WORLD.width"
                :height="MAP_WORLD.height"
                fill="rgba(0,0,0,0)"
                stroke="rgba(0,255,255,0.18)"
                stroke-width="0.9"
                stroke-dasharray="3 3"
                vector-effect="non-scaling-stroke"
              />

              <image
                id="bgImage"
                :x="bgRect.x"
                :y="bgRect.y"
                :width="bgRect.width"
                :height="bgRect.height"
                :style="{ display: showBackground ? 'block' : 'none', opacity: bgOpacity }"
                href="/background.png"
                preserveAspectRatio="none"
              />

              <rect id="gridRect" x="-100000" y="-100000" width="200000" height="200000" :style="{ display: showGrid ? 'block' : 'none' }" fill="url(#grid)" />

              <line x1="-20000" y1="0" x2="20000" y2="0" stroke="white" stroke-width="0.1" opacity="0.12" />
              <line x1="0" y1="-20000" x2="0" y2="20000" stroke="white" stroke-width="0.1" opacity="0.12" />

              <g ref="markersGroup" id="markersLayer" v-html="markers"></g>

              <g id="drawLayer" style="pointer-events: none">
                <template v-for="(d, i) in drawings" :key="i">
                  <line v-if="d.type === 'line'" :x1="d.x1" :y1="d.y1" :x2="d.x2" :y2="d.y2" v-bind="d.style" />
                  <rect v-else-if="d.type === 'rect'" :x="d.x" :y="d.y" :width="d.width" :height="d.height" v-bind="d.style" />
                  <circle v-else-if="d.type === 'circle'" :cx="d.cx" :cy="d.cy" :r="d.r" v-bind="d.style" />
                  <path v-else-if="d.type === 'path'" :d="d.d" fill="none" v-bind="d.style" />
                  <g v-else-if="d.type === 'measure'">
                    <line :x1="d.x1" :y1="d.y1" :x2="d.x2" :y2="d.y2" v-bind="d.style" />
                    <text :x="(d.x1 + d.x2) / 2" :y="(d.y1 + d.y2) / 2 - 0.5" font-size="1.5" text-anchor="middle" class="measure-label">
                      {{ Number(d.distance).toFixed(1) }} tiles
                    </text>
                  </g>
                  <text v-else-if="d.type === 'text'" :x="d.x" :y="d.y" v-bind="d.style">{{ d.text }}</text>
                </template>
              </g>

              <g id="previewLayer" ref="previewLayer" style="pointer-events: none"></g>
            </g>

            <g v-if="showRulers" id="rulerOverlay" style="pointer-events: none">
              <rect :x="0" :y="0" :width="rulerW" :height="rulerThickness" fill="rgba(0,0,0,0.55)" />
              <rect :x="0" :y="0" :width="rulerThickness" :height="rulerH" fill="rgba(0,0,0,0.55)" />
              <g>
                <template v-for="t in rulerXTicks" :key="'mx' + t.value">
                  <line :x1="t.px" :y1="rulerThickness" :x2="t.px" :y2="rulerThickness - (t.major ? 10 : 6)" stroke="rgba(255,255,255,0.75)" stroke-width="1" />
                  <text v-if="t.major" :x="t.px" :y="12" fill="rgba(255,255,255,0.92)" font-size="10" text-anchor="middle">{{ t.label }}</text>
                </template>
              </g>
              <g>
                <template v-for="t in rulerYTicks" :key="'my' + t.value">
                  <line :x1="rulerThickness" :y1="t.py" :x2="rulerThickness - (t.major ? 10 : 6)" :y2="t.py" stroke="rgba(255,255,255,0.75)" stroke-width="1" />
                  <text v-if="t.major" :x="12" :y="t.py + 3" fill="rgba(255,255,255,0.92)" font-size="10" text-anchor="start">{{ t.label }}</text>
                </template>
              </g>
            </g>
          </svg>

          <div class="minimap" v-if="minimapReady">
            <div class="minimap__header">
              <div class="minimap__title">Minimap</div>
              <div class="minimap__actions">
                <q-btn dense flat round icon="remove" @click.stop="minimapZoomBy(0.85)" />
                <q-btn dense flat round icon="add" @click.stop="minimapZoomBy(1.18)" />
                <q-btn dense flat round icon="my_location" @click.stop="minimapRecenterToView()" />
                <q-btn dense flat round icon="crop_free" @click.stop="minimapFitAll()" />
              </div>
            </div>

            <svg
              ref="minimapSvg"
              class="minimap__svg"
              :viewBox="`${minimapView.x} ${minimapView.y} ${minimapView.width} ${minimapView.height}`"
              @pointerdown.prevent="onMinimapPointerDown"
              @pointermove.prevent="onMinimapPointerMove"
              @pointerup.prevent="onMinimapPointerUp"
              @pointercancel.prevent="onMinimapPointerUp"
              @wheel.prevent="onMinimapWheel"
            >
              <rect :x="minimapBounds.x" :y="minimapBounds.y" :width="minimapBounds.width" :height="minimapBounds.height" fill="rgba(0,0,0,0.28)" stroke="rgba(255,255,255,0.16)" stroke-width="2" rx="18" ry="18" />
              <rect
                :x="MAP_WORLD.x"
                :y="MAP_WORLD.y"
                :width="MAP_WORLD.width"
                :height="MAP_WORLD.height"
                fill="rgba(0,0,0,0)"
                stroke="rgba(0,255,255,0.35)"
                stroke-width="2"
                stroke-dasharray="5 4"
                vector-effect="non-scaling-stroke"
                rx="10"
                ry="10"
              />
              <rect v-if="showBackground" :x="bgRect.x" :y="bgRect.y" :width="bgRect.width" :height="bgRect.height" fill="rgba(255,255,255,0.03)" stroke="rgba(255,255,255,0.06)" stroke-width="2" />

              <g v-if="minimapPoints.length" opacity="0.85">
                <circle v-for="(p, i) in minimapPoints" :key="i" :cx="p.x" :cy="p.y" :r="p.r" fill="rgba(255,255,255,0.35)" />
              </g>

              <rect class="minimap__viewport" :x="viewWorld.x" :y="viewWorld.y" :width="viewWorld.width" :height="viewWorld.height" fill="rgba(0,255,255,0.10)" stroke="rgba(0,255,255,0.75)" stroke-width="3" rx="10" ry="10" />
              <circle :cx="cursor.x" :cy="cursor.y" r="10" fill="rgba(255,255,255,0.9)" stroke="rgba(0,0,0,0.55)" stroke-width="3" />
            </svg>

            <div class="minimap__footer">
              <div class="minimap__line">Cursor: <b>{{ Math.round(cursor.x) }}|{{ Math.round(-cursor.y) }}</b></div>
              <div class="minimap__line">
                Center: <b>{{ Math.round(viewCenter.x) }}|{{ Math.round(-viewCenter.y) }}</b>
                <span class="minimap__muted">·</span>
                <span class="minimap__muted">Zoom {{ zoomK.toFixed(2) }}×</span>
              </div>
            </div>
          </div>

          <q-inner-loading :showing="loading">
            <q-spinner color="primary" size="2em" />
          </q-inner-loading>

          <div v-if="tooltip.show" class="tooltip" :style="{ top: tooltip.y + 'px', left: tooltip.x + 'px' }" v-html="tooltip.content" />
        </div>
      </div>

      <div class="statusbar row items-center q-px-sm q-py-xs">
        <div class="col text-caption">Zoom: {{ zoomK.toFixed(2) }}×</div>
        <div class="col text-caption text-right">Cursor: {{ Math.round(cursor.x) }}|{{ Math.round(-cursor.y) }} <span class="statusbar__sep">·</span> Dist: {{ distanceTiles.toFixed(1) }}</div>
      </div>
    </div>

    <!-- Help dialog -->
    <q-dialog v-model="helpOpen">
      <q-card style="min-width: 420px; max-width: 720px">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Map shortcuts</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section class="q-pt-sm">
          <div class="text-body2">
            <div><b>Mouse</b></div>
            <div>• Wheel: zoom</div>
            <div>• Drag: pan</div>

            <div class="q-mt-md"><b>Keyboard</b></div>
            <div>• Ctrl/⌘+Z / Ctrl/⌘+Y: undo/redo drawings</div>
            <div>• Esc: cancel drawing</div>
            <div>• F: fullscreen</div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- Context menu -->
    <q-menu
      v-model="showContextMenu"
      context-menu
      touch-position
      :style="{ left: `${contextPosition.x}px`, top: `${contextPosition.y}px` }"
      class="context-menu"
      @before-show="onBeforeContextMenuShow"
      @hide="onContextMenuHide"
    >
      <q-list style="min-width: 240px">
        <q-item-label header>Village Actions</q-item-label>

        <q-item clickable v-close-popup @click="centerOnContext" :disable="!ctx.hasMarker">
          <q-item-section avatar><q-icon name="center_focus_strong" /></q-item-section>
          <q-item-section>Center on village</q-item-section>
        </q-item>

        <q-item clickable v-close-popup @click="copyCoordinates">
          <q-item-section avatar><q-icon name="content_copy" /></q-item-section>
          <q-item-section>Copy coordinates</q-item-section>
        </q-item>
<q-item clickable v-close-popup @click="setRefToContext" :disable="!ctx.point">
  <q-item-section avatar><q-icon name="timelapse" /></q-item-section>
  <q-item-section>Set as reference point</q-item-section>
</q-item>

        <q-separator />

        <q-item-label header>View</q-item-label>

        <q-item clickable v-close-popup @click="resetView">
          <q-item-section avatar><q-icon name="refresh" /></q-item-section>
          <q-item-section>Reset view</q-item-section>
        </q-item>

        <q-item clickable v-close-popup @click="exportPng">
          <q-item-section avatar><q-icon name="image" /></q-item-section>
          <q-item-section>Export PNG</q-item-section>
        </q-item>
      </q-list>
    </q-menu>
  </q-page>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount, computed, nextTick, watch } from 'vue'
import { useQuasar } from 'quasar'
import * as d3 from 'd3'
import { api } from 'boot/axios'
import MapSidebarContent from 'src/components/MapSidebarContent.vue'

/* =========================
   Authoritative world bounds
   ========================= */
const MAP_MIN = -200
const MAP_MAX = 200
const MAP_SIZE = MAP_MAX - MAP_MIN // 400
const MAP_PADDING = 30
const MAP_WORLD = Object.freeze({ x: MAP_MIN, y: MAP_MIN, width: MAP_SIZE, height: MAP_SIZE })
const MAP_CONTAINER = Object.freeze({
  x: MAP_MIN - MAP_PADDING,
  y: MAP_MIN - MAP_PADDING,
  width: MAP_SIZE + MAP_PADDING * 2,
  height: MAP_SIZE + MAP_PADDING * 2
})

/* === State === */
const $q = useQuasar()
const loading = ref(false)

const splitter = ref(320)
let handleCheckboxChange = null

/** DOM refs (resize fix) */
const stageEl = ref(null)
const squareEl = ref(null)
let resizeObserver = null
let resizeRaf = 0

/** Map & zoom */
const svg = ref(null)
const markersGroup = ref(null)
const previewLayer = ref(null)
let zoom
const zoomK = ref(1)
const cursor = ref({ x: 0, y: 0 })
const gotoX = ref(0)
const gotoY = ref(0)

/** === Zoom limits === */
const MAX_ZOOM_OUT_PERCENT = 50
const MIN_ZOOM_K = 1 / (MAX_ZOOM_OUT_PERCENT / 100) // ≈ 0.558
const MAX_ZOOM_K = 50

/** === World pan limits ===
 * IMPORTANT FIX:
 * translateExtent must be defined in WORLD coordinates (not screen coords),
 * otherwise d3 clamps translations and the view "jumps" when panning.
 */
const WORLD_MIN = MAP_CONTAINER.x
const WORLD_MAX = MAP_CONTAINER.x + MAP_CONTAINER.width

/** Initial centering requirement */
const initialCenteredDone = ref(false)
const INITIAL_CENTER = { x: 0, y: 0 }

/** HUD */
const jumpInput = ref('')
const zoomSlider = ref(100)
const helpOpen = ref(false)

/** Layers */
const showBackground = ref(true)
const bgOpacity = ref(0.6)
const showGrid = ref(true)
const gridOpacity = ref(0.35)
const gridSize = ref(2)

/** Markers & filters */
const markers = ref('')
const toggles = ref({ alliances: '', tribes: '' })
const groupFilters = ref({ alliances: '', tribes: '' })
let masterVisible = true

/** Background image */
const bgMeta = reactive({ w: 0, h: 0, loaded: false })
const bgRect = reactive({ x: MAP_WORLD.x, y: MAP_WORLD.y, width: MAP_WORLD.width, height: MAP_WORLD.height })

/** Tooltip */
const tooltip = ref({ show: false, x: 0, y: 0, content: '' })

/** Context menu */
const showContextMenu = ref(false)
const contextPosition = ref({ x: 0, y: 0 })
const ctx = reactive({ point: null, hasMarker: false, marker: null })

function onBeforeContextMenuShow() {
  document.addEventListener('click', handleClickOutside)
}
function onContextMenuHide() {
  document.removeEventListener('click', handleClickOutside)
}
function handleClickOutside(event) {
  if (showContextMenu.value && !event.target.closest('.q-menu')) showContextMenu.value = false
}

/** Drawing */
const drawMode = ref(null)
const drawOptions = [
  { label: 'Off', value: null },
  { label: 'Line', value: 'line' },
  { label: 'Rect', value: 'rect' },
  { label: 'Circle', value: 'circle' },
  { label: 'Freehand', value: 'path' },
  { label: 'Text', value: 'text' },
  { label: 'Measure', value: 'measure' }
]
const drawColor = ref('#ff0000')
const drawWidth = ref(2)
const snapToGrid = ref(false)
const drawings = ref([])
const history = ref([])
const historyIndex = ref(-1)
const canUndo = computed(() => historyIndex.value > 0)
const canRedo = computed(() => Boolean(history.value.length && historyIndex.value < history.value.length - 1))

/** Draw panel */
const drawPanelOpen = ref(true)
const quickColors = ['#ff1744', '#ff9100', '#ffd600', '#00e676', '#00bcd4', '#2979ff', '#7c4dff', '#ffffff']
const quickWidths = [1, 2, 3, 5]
function setColor(c) {
  drawColor.value = c
}

/** Rulers */
const showRulers = ref(true)
const rulerThickness = 26
const rulerW = ref(0)
const rulerH = ref(0)
const rulerXTicks = ref([])
const rulerYTicks = ref([])

/** Minimap */
const minimapSvg = ref(null)
const minimapBounds = reactive({ ...MAP_CONTAINER })
const minimapReady = ref(false)
const minimapView = reactive({ ...MAP_CONTAINER })
const minimapMinScale = 0.35
const minimapMaxScale = 3.5
const minimapPoints = ref([])

const viewWorld = reactive({ x: -50, y: -50, width: 100, height: 100 })
const viewCenter = computed(() => ({ x: viewWorld.x + viewWorld.width / 2, y: viewWorld.y + viewWorld.height / 2 }))

const minimapDrag = reactive({
  active: false,
  mode: null,
  startWorld: { x: 0, y: 0 },
  startViewBox: { x: 0, y: 0, width: 0, height: 0 },
  startCenter: { x: 0, y: 0 }
})

/* === Helpers === */
const capitalize = (s) => s.charAt(0).toUpperCase() + s.slice(1)
const clamp = (n, a, b) => Math.max(a, Math.min(b, n))

/** Distance & travel time calculator */
const refPoint = ref({ x: 0, y: 0 }) // world coords (y positive down)
const refInput = ref('0|0')

const tribeOptions = [
  { label: 'Romans', value: 'romans' },
  { label: 'Teutons', value: 'teutons' },
  { label: 'Gauls', value: 'gauls' },
  { label: 'Egyptians', value: 'egyptians' },
  { label: 'Huns', value: 'huns' },
  { label: 'Spartans', value: 'spartans' },
  { label: 'Vikings', value: 'vikings' }
];

const tribe = ref('romans')
const isSpeedServer = ref(false) // Travian "speed" servers (×2 unit speed)
const tsLevel = ref(0) // Tournament Square level 0..20
const tsSpeedup = computed(() => 1 + tsLevel.value / 10)

const TROOPS = Object.freeze({
  romans: [
    { key: 'legionnaire', label: 'Legionnaire', speed: 6 },
    { key: 'legionnaire_new', label: 'Legionnaire (new)', speed: 7 },
    { key: 'praetorian', label: 'Praetorian', speed: 5 },
    { key: 'imperian', label: 'Imperian', speed: 7 },
    { key: 'equites_legati', label: 'Equites Legati', speed: 16 },
    { key: 'equites_imperatoris', label: 'Equites Imperatoris', speed: 14 },
    { key: 'equites_caesaris', label: 'Equites Caesaris', speed: 10 },
    { key: 'ram', label: 'Battering Ram', speed: 4 },
    { key: 'catapult', label: 'Fire Catapult', speed: 3, highlight: true },
    { key: 'senator', label: 'Senator', speed: 4 },
    { key: 'settler', label: 'Settler', speed: 5 },
    { key: 'merchant', label: 'Merchant', speed: 18, bold: true }
  ],
  teutons: [
    { key: 'clubswinger', label: 'Clubswinger', speed: 7 },
    { key: 'spearman', label: 'Spearman', speed: 7 },
    { key: 'axeman', label: 'Axeman', speed: 6 },
    { key: 'scout', label: 'Scout', speed: 9 },
    { key: 'paladin', label: 'Paladin', speed: 10 },
    { key: 'teutonic_knight', label: 'Teutonic Knight', speed: 9 },
    { key: 'ram', label: 'Ram', speed: 4 },
    { key: 'catapult', label: 'Catapult', speed: 3, highlight: true },
    { key: 'chief', label: 'Chief', speed: 4 },
    { key: 'settler', label: 'Settler', speed: 5 },
    { key: 'merchant', label: 'Merchant', speed: 12, bold: true }
  ],
  gauls: [
    { key: 'phalanx', label: 'Phalanx', speed: 7 },
    { key: 'swordsman', label: 'Swordsman', speed: 6 },
    { key: 'pathfinder', label: 'Pathfinder', speed: 17 },
    { key: 'theutates_thunder', label: 'Theutates Thunder', speed: 19 },
    { key: 'druidrider', label: 'Druidrider', speed: 16 },
    { key: 'haeduan', label: 'Haeduan', speed: 13 },
    { key: 'ram', label: 'Ram', speed: 4 },
    { key: 'trebuchet', label: 'Trebuchet', speed: 3, highlight: true },
    { key: 'chieftain', label: 'Chieftain', speed: 5 },
    { key: 'settler', label: 'Settler', speed: 5 },
    { key: 'merchant', label: 'Merchant', speed: 24, bold: true }
  ],

  // added based on the troop tables you provided
  egyptians: [
    { key: 'slave_militia', label: 'Slave Militia', speed: 7 },
    { key: 'ash_warden', label: 'Ash Warden', speed: 6 },
    { key: 'khopesh_warrior', label: 'Khopesh Warrior', speed: 7 },
    { key: 'sopdu_explorer', label: 'Sopdu Explorer', speed: 16 },
    { key: 'anhur_guard', label: 'Anhur Guard', speed: 15 },
    { key: 'resheph_chariot', label: 'Resheph Chariot', speed: 10 }
  ],
  huns: [
    { key: 'mercenary', label: 'Mercenary', speed: 7 },
    { key: 'bowman', label: 'Bowman', speed: 6 },
    { key: 'spotter', label: 'Spotter', speed: 19 },
    { key: 'steppe_rider', label: 'Steppe Rider', speed: 16 },
    { key: 'marksman', label: 'Marksman', speed: 15 },
    { key: 'marauder', label: 'Marauder', speed: 14 }
  ],
  spartans: [
    { key: 'hoplite', label: 'Hoplite', speed: 6 },
    { key: 'sentinel', label: 'Sentinel', speed: 9 },
    { key: 'shieldsman', label: 'Shieldsman', speed: 8 },
    { key: 'twinsteel_therion', label: 'Twinsteel Therion', speed: 6 },
    { key: 'elpida_rider', label: 'Elpida Rider', speed: 16 },
    { key: 'corinthian_crusher', label: 'Corinthian Crusher', speed: 9 }
  ],
  vikings: [
    { key: 'thrall', label: 'Thrall', speed: 7 },
    { key: 'shield_maiden', label: 'Shield Maiden', speed: 7 },
    { key: 'berserker', label: 'Berserker', speed: 5 },
    { key: "heimdalls_eye", label: "Heimdall's Eye", speed: 9 },
    { key: 'huskarl_riders', label: 'Huskarl Riders', speed: 12 },
    { key: 'valkyrie', label: 'Valkyrie', speed: 9 }
  ]
});


function formatHours(totalHours) {
  const tot = Math.max(0, Number(totalHours) || 0)
  const days = Math.floor(tot / 24)
  const hours = tot % 24
  const h = Math.floor(hours)
  const min = Math.floor((hours * 60) % 60)
  const sec = Math.floor((((hours * 60) % 60) * 60) % 60)
  const pad2 = (n) => String(n).padStart(2, '0')
  return `${days ? `${days}d ` : ''}${h}:${pad2(min)}:${pad2(sec)}`
}

/** Travian TS speedup model (first 30 tiles at base speed, rest boosted) */
function calcTravelHours(dist, speed) {
  const d = Math.max(0, Number(dist) || 0)
  const s = Math.max(0.0001, Number(speed) || 0.0001)
  const multi = isSpeedServer.value ? 2 : 1
  const speedup = tsSpeedup.value

  if (d < 30 || !Number.isFinite(speedup) || speedup <= 1) return d / (s * multi)

  const sub30 = 30 / (s * multi)
  const super30 = (d - 30) / (s * speedup * multi)
  return sub30 + super30
}

function parseCoordString(input) {
  const s = String(input || '').trim().replace(/[()]/g, '')
  const m = s.match(/(-?\d+)\s*\|\s*(-?\d+)/)
  if (!m) return null
  const x = Number(m[1])
  const yTrav = Number(m[2]) // travian-style (y positive up)
  if (!Number.isFinite(x) || !Number.isFinite(yTrav)) return null
  return { x, y: -yTrav } // convert to world coords
}

function applyRefInput() {
  const p = parseCoordString(refInput.value)
  if (!p) {
    $q.notify({ message: 'Invalid reference coordinates. Use x|y.', color: 'negative', position: 'top', timeout: 1100 })
    return
  }
  refPoint.value = p
}

function setRefToCursor() {
  refPoint.value = { x: cursor.value.x, y: cursor.value.y }
  refInput.value = `${Math.round(refPoint.value.x)}|${Math.round(-refPoint.value.y)}`
}

function setRefToViewCenter() {
  refPoint.value = { x: viewCenter.value.x, y: viewCenter.value.y }
  refInput.value = `${Math.round(refPoint.value.x)}|${Math.round(-refPoint.value.y)}`
}

function setRefToContext() {
  if (!ctx.point) return
  refPoint.value = { x: ctx.point.x, y: ctx.point.y }
  refInput.value = `${Math.round(refPoint.value.x)}|${Math.round(-refPoint.value.y)}`
  $q.notify({ message: 'Reference point set.', color: 'positive', position: 'top', timeout: 800 })
}

const distanceTiles = computed(() => {
  const dx = cursor.value.x - refPoint.value.x
  const dy = cursor.value.y - refPoint.value.y
  return Math.sqrt(dx * dx + dy * dy)
})

const travelRows = computed(() => {
  const list = TROOPS[tribe.value] || TROOPS.romans
  const dist = distanceTiles.value
  return list.map((u) => {
    const hours = calcTravelHours(dist, u.speed)
    return {
      key: u.key,
      label: u.label,
      time: formatHours(hours),
      highlight: Boolean(u.highlight) || Boolean(u.bold && u.key === 'merchant')
    }
  })
})

watch(
  () => refPoint.value,
  (p) => {
    if (!p) return
    refInput.value = `${Math.round(p.x)}|${Math.round(-p.y)}`
  },
  { deep: true, immediate: true }
)


function pushHistory() {
  history.value = history.value.slice(0, historyIndex.value + 1)
  history.value.push(JSON.parse(JSON.stringify(drawings.value)))
  historyIndex.value = history.value.length - 1
}
function undo() {
  if (!canUndo.value) return
  historyIndex.value--
  drawings.value = JSON.parse(JSON.stringify(history.value[historyIndex.value]))
}
function redo() {
  if (!canRedo.value) return
  historyIndex.value++
  drawings.value = JSON.parse(JSON.stringify(history.value[historyIndex.value]))
}
function clearDrawings() {
  drawings.value = []
  pushHistory()
  saveToLocal()
}
function saveToLocal() {
  localStorage.setItem('drawings', JSON.stringify(drawings.value))
}
function loadFromLocal() {
  const raw = localStorage.getItem('drawings')
  if (raw) {
    drawings.value = JSON.parse(raw)
    pushHistory()
  }
}
function exportDrawings() {
  const dataStr = JSON.stringify(drawings.value, null, 2)
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  const link = document.createElement('a')
  link.href = url
  link.download = `drawings-${Date.now()}.json`
  link.click()
  URL.revokeObjectURL(url)
}
function importDrawings() {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'application/json'
  input.onchange = (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = (event) => {
      try {
        drawings.value = JSON.parse(String(event.target?.result || '[]'))
        pushHistory()
        saveToLocal()
      } catch (err) {
        console.error('Failed to import drawings:', err)
      }
    }
    reader.readAsText(file)
  }
  input.click()
}

/* === Disable page scroll ONLY while on map page === */
function lockPageScroll() {
  document.body.classList.add('map-no-scroll')
  document.documentElement.classList.add('map-no-scroll')
}
function unlockPageScroll() {
  document.body.classList.remove('map-no-scroll')
  document.documentElement.classList.remove('map-no-scroll')
}

/* === PNG export === */
async function exportPng() {
  if (!svg.value) return
  try {
    const s = svg.value
    const clone = s.cloneNode(true)
    const rect = s.getBoundingClientRect()
    clone.setAttribute('width', String(Math.max(1, Math.round(rect.width))))
    clone.setAttribute('height', String(Math.max(1, Math.round(rect.height))))
    clone.querySelectorAll('text').forEach((t) => t.setAttribute('font-family', 'sans-serif'))

    const xml = new XMLSerializer().serializeToString(clone)
    const svgBlob = new Blob([xml], { type: 'image/svg+xml;charset=utf-8' })
    const svgUrl = URL.createObjectURL(svgBlob)

    const img = new Image()
    img.onload = () => {
      const canvas = document.createElement('canvas')
      canvas.width = Math.round(rect.width)
      canvas.height = Math.round(rect.height)
      const ctx2d = canvas.getContext('2d')
      ctx2d.drawImage(img, 0, 0)

      URL.revokeObjectURL(svgUrl)
      canvas.toBlob((blob) => {
        if (!blob) return
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `map-${Date.now()}.png`
        a.click()
        URL.revokeObjectURL(url)
      }, 'image/png')
    }
    img.src = svgUrl
  } catch (e) {
    console.warn('PNG export failed:', e)
    $q.notify({ message: 'PNG export failed (check console).', color: 'negative', position: 'top', timeout: 1400 })
  }
}

/* === Minimap helpers (stable bounds) === */
function syncMinimapBounds() {
  Object.assign(minimapBounds, MAP_CONTAINER)
  minimapReady.value = true

  if (!Number.isFinite(minimapView.width) || minimapView.width <= 0) {
    Object.assign(minimapView, MAP_CONTAINER)
  }
  clampMinimapView()
}
function clampMinimapView() {
  const b = minimapBounds
  const v = minimapView
  const maxX = b.x + b.width - v.width
  const maxY = b.y + b.height - v.height
  v.x = Math.max(b.x, Math.min(v.x, maxX))
  v.y = Math.max(b.y, Math.min(v.y, maxY))
}
function minimapFitAll() {
  Object.assign(minimapView, minimapBounds)
  clampMinimapView()
}
function minimapRecenterToView() {
  const b = minimapBounds
  const cx = viewCenter.value.x
  const cy = viewCenter.value.y
  minimapView.x = cx - minimapView.width / 2
  minimapView.y = cy - minimapView.height / 2
  clampMinimapView()
  if (cx < b.x || cx > b.x + b.width || cy < b.y || cy > b.y + b.height) {
    minimapView.x = b.x + b.width / 2 - minimapView.width / 2
    minimapView.y = b.y + b.height / 2 - minimapView.height / 2
    clampMinimapView()
  }
}
function minimapZoomBy(factor) {
  const b = minimapBounds
  const cx = minimapView.x + minimapView.width / 2
  const cy = minimapView.y + minimapView.height / 2
  const newW = minimapView.width / factor
  const newH = minimapView.height / factor

  const minW = b.width * minimapMinScale
  const maxW = b.width * minimapMaxScale

  const w = Math.max(minW, Math.min(newW, maxW))
  const h = Math.max(b.height * minimapMinScale, Math.min(newH, b.height * minimapMaxScale))

  minimapView.width = w
  minimapView.height = h
  minimapView.x = cx - w / 2
  minimapView.y = cy - h / 2
  clampMinimapView()
}
function minimapToWorld(evt) {
  const el = minimapSvg.value
  if (!el) return { x: 0, y: 0 }
  const r = el.getBoundingClientRect()
  const px = evt.clientX - r.left
  const py = evt.clientY - r.top
  return {
    x: minimapView.x + (px / r.width) * minimapView.width,
    y: minimapView.y + (py / r.height) * minimapView.height
  }
}
function isInsideViewport(worldPt) {
  return (
    worldPt.x >= viewWorld.x &&
    worldPt.x <= viewWorld.x + viewWorld.width &&
    worldPt.y >= viewWorld.y &&
    worldPt.y <= viewWorld.y + viewWorld.height
  )
}
function onMinimapPointerDown(evt) {
  if (!minimapSvg.value) return
  minimapSvg.value.setPointerCapture?.(evt.pointerId)
  const wpt = minimapToWorld(evt)
  minimapDrag.active = true
  minimapDrag.startWorld = { ...wpt }
  minimapDrag.startViewBox = { x: minimapView.x, y: minimapView.y, width: minimapView.width, height: minimapView.height }
  minimapDrag.startCenter = { ...viewCenter.value }
  minimapDrag.mode = isInsideViewport(wpt) ? 'dragViewport' : 'pan'
  if (minimapDrag.mode === 'pan') {
    centerAt(
      clamp(wpt.x, WORLD_MIN, WORLD_MAX),
      clamp(wpt.y, WORLD_MIN, WORLD_MAX)
    )
  }
}
function onMinimapPointerMove(evt) {
  if (!minimapDrag.active) return
  const now = minimapToWorld(evt)
  const dx = now.x - minimapDrag.startWorld.x
  const dy = now.y - minimapDrag.startWorld.y
  if (minimapDrag.mode === 'pan') {
    minimapView.x = minimapDrag.startViewBox.x + dx
    minimapView.y = minimapDrag.startViewBox.y + dy
    clampMinimapView()
  } else {
    centerAt(
      clamp(minimapDrag.startCenter.x + dx, WORLD_MIN, WORLD_MAX),
      clamp(minimapDrag.startCenter.y + dy, WORLD_MIN, WORLD_MAX)
    )
  }
}
function onMinimapPointerUp(evt) {
  if (!minimapDrag.active) return
  minimapDrag.active = false
  minimapDrag.mode = null
  minimapSvg.value?.releasePointerCapture?.(evt.pointerId)
}
function onMinimapWheel(evt) {
  const factor = evt.deltaY < 0 ? 1.18 : 0.85
  const before = minimapToWorld(evt)
  minimapZoomBy(factor)
  const after = minimapToWorld(evt)
  minimapView.x += before.x - after.x
  minimapView.y += before.y - after.y
  clampMinimapView()
}
function rebuildMinimapPoints() {
  const g = markersGroup.value
  if (!g) {
    minimapPoints.value = []
    return
  }
  const nodes = Array.from(g.querySelectorAll('.marker'))
  const N = 500
  const step = Math.max(1, Math.floor(nodes.length / N))
  const pts = []
  for (let i = 0; i < nodes.length; i += step) {
    const el = nodes[i]
    try {
      const bb = el.getBBox()
      pts.push({ x: bb.x + bb.width / 2, y: bb.y + bb.height / 2, r: 6 })
    } catch {}
  }
  minimapPoints.value = pts
}

/* === Fit / position === */
function syncZoomExtents() {
  if (!svg.value || !zoom) return

  const r = svg.value.getBoundingClientRect()
  if (!r || r.width <= 0 || r.height <= 0) return

  zoom.extent([[0, 0], [r.width, r.height]])

  // === CRITICAL FIX (stops pan jump) ===
  // translateExtent is in WORLD coordinates, not screen coordinates.
  // Using screen-space numbers here makes d3 clamp translations unpredictably.
  zoom.translateExtent([
    [MAP_CONTAINER.x, MAP_CONTAINER.y],
    [MAP_CONTAINER.x + MAP_CONTAINER.width, MAP_CONTAINER.y + MAP_CONTAINER.height]
  ])

  rulerW.value = r.width
  rulerH.value = r.height
}

function forceReapplyTransformAfterResize() {
  if (!svg.value || !zoom) return
  const t = d3.zoomTransform(svg.value)
  d3.select(svg.value).call(zoom.transform, t)
}
function scheduleResizeRefresh() {
  cancelAnimationFrame(resizeRaf)
  resizeRaf = requestAnimationFrame(() => {
    syncZoomExtents()
    forceReapplyTransformAfterResize()
    updateViewWorldAndRulers()
  })
}

/** Initial centered view */
function setInitialCenteredViewIfPossible() {
  if (initialCenteredDone.value) return
  if (!svg.value || !zoom) return
  const r = svg.value.getBoundingClientRect()
  if (!r || r.width <= 0 || r.height <= 0) return

  syncZoomExtents()

  const k = clamp(1.25, MIN_ZOOM_K, MAX_ZOOM_K)
  const tx = r.width / 2 - k * INITIAL_CENTER.x
  const ty = r.height / 2 - k * INITIAL_CENTER.y
  const t = d3.zoomIdentity.translate(tx, ty).scale(k)

  d3.select(svg.value).call(zoom.transform, t)
  zoomSlider.value = Math.round(k * 100)
  initialCenteredDone.value = true
  updateViewWorldAndRulers()
}

function centerAt(x, y, k) {
  if (!svg.value || !zoom) return
  if (!Number.isFinite(k)) k = d3.zoomTransform(svg.value).k || 1

  x = clamp(x, WORLD_MIN, WORLD_MAX)
  y = clamp(y, WORLD_MIN, WORLD_MAX)

  syncZoomExtents()

  const rect = svg.value.getBoundingClientRect()
  const tx = rect.width / 2 - k * x
  const ty = rect.height / 2 - k * y
  const t = d3.zoomIdentity.translate(tx, ty).scale(k)

  d3.select(svg.value).transition().duration(220).call(zoom.transform, t)
}

function zoomBy(factor) {
  if (!svg.value || !zoom) return
  const t = d3.zoomTransform(svg.value)
  const nextK = clamp(t.k * factor, MIN_ZOOM_K, MAX_ZOOM_K)
  const rect = svg.value.getBoundingClientRect()
  const cx = (rect.width / 2 - t.x) / t.k
  const cy = (rect.height / 2 - t.y) / t.k
  centerAt(cx, cy, nextK)
}

function resetView() {
  centerAt(INITIAL_CENTER.x, INITIAL_CENTER.y, 1)
}
function centerOnCoords() {
  centerAt(Number(gotoX.value) || 0, Number(gotoY.value) || 0)
}

/* === Zoom slider === */
function syncSliderFromZoom() {
  zoomSlider.value = clamp(
    Math.round(zoomK.value * 100),
    Math.round(MIN_ZOOM_K * 100),
    500
  )
}
function applyZoomSlider() {
  if (!svg.value || !zoom) return
  const k = clamp(zoomSlider.value / 100, MIN_ZOOM_K, MAX_ZOOM_K)
  const t = d3.zoomTransform(svg.value)
  const rect = svg.value.getBoundingClientRect()
  const cx = (rect.width / 2 - t.x) / t.k
  const cy = (rect.height / 2 - t.y) / t.k
  centerAt(cx, cy, k)
}

function jumpToInput() {
  const raw = (jumpInput.value || '').trim()
  const m = raw.match(/^\s*(-?\d+)\s*[|, ]\s*(-?\d+)\s*$/)
  if (!m) {
    $q.notify({ message: 'Use format: x|y (example: -12|34)', color: 'warning', position: 'top', timeout: 1200 })
    return
  }
  const x = Number(m[1])
  const yTravian = Number(m[2])
  centerAt(
    clamp(x, WORLD_MIN, WORLD_MAX),
    clamp(-yTravian, WORLD_MIN, WORLD_MAX)
  )
}
async function toggleFullscreen() {
  const el = svg.value?.closest('.map-column') || svg.value
  if (!el) return
  try {
    if (!document.fullscreenElement) await el.requestFullscreen?.()
    else await document.exitFullscreen?.()
  } catch (e) {
    console.warn('Fullscreen failed:', e)
  }
}

/* === Rulers === */
function niceStep(worldPerPx) {
  const target = worldPerPx * 80
  const pow = Math.pow(10, Math.floor(Math.log10(Math.max(1e-9, target))))
  const n = target / pow
  if (n < 1.5) return 1 * pow
  if (n < 3.5) return 2 * pow
  if (n < 7.5) return 5 * pow
  return 10 * pow
}
function updateViewWorldAndRulers() {
  if (!svg.value || !zoom) return
  const rect = svg.value.getBoundingClientRect()
  if (!rect || rect.width <= 0 || rect.height <= 0) return
  const t = d3.zoomTransform(svg.value)

  const x0 = t.invertX(0)
  const y0 = t.invertY(0)
  const x1 = t.invertX(rect.width)
  const y1 = t.invertY(rect.height)

  viewWorld.x = Math.min(x0, x1)
  viewWorld.y = Math.min(y0, y1)
  viewWorld.width = Math.abs(x1 - x0)
  viewWorld.height = Math.abs(y1 - y0)

  if (!showRulers.value) {
    rulerXTicks.value = []
    rulerYTicks.value = []
    return
  }

  const worldPerPx = 1 / t.k
  const step = niceStep(worldPerPx)
  const minor = step / 5

  const xStart = Math.floor(viewWorld.x / minor) * minor
  const xEnd = viewWorld.x + viewWorld.width
  const xt = []
  for (let x = xStart; x <= xEnd + minor; x += minor) {
    const px = t.applyX(x)
    if (px < 0 || px > rect.width) continue
    const isMajor = Math.abs(x / step - Math.round(x / step)) < 1e-6
    xt.push({ value: x, px, major: isMajor, label: isMajor ? String(Math.round(x)) : '' })
  }

  const yStart = Math.floor(viewWorld.y / minor) * minor
  const yEnd = viewWorld.y + viewWorld.height
  const yt = []
  for (let y = yStart; y <= yEnd + minor; y += minor) {
    const py = t.applyY(y)
    if (py < 0 || py > rect.height) continue
    const isMajor = Math.abs(y / step - Math.round(y / step)) < 1e-6
    yt.push({ value: y, py, major: isMajor, label: isMajor ? String(Math.round(-y)) : '' })
  }

  rulerXTicks.value = xt
  rulerYTicks.value = yt
}
function toggleRulers() {
  showRulers.value = !showRulers.value
  updateViewWorldAndRulers()
}

/* === Marker loading === */
/* === Marker loading ===
   IMPORTANT:
   - localStorage has ~5MB quota and will explode for /api/markers payloads.
   - IndexedDB is designed for this (tens/hundreds of MB depending on browser).
*/
const CACHE_KEY = 'markersCache'              // legacy key (we will delete from localStorage)
const IDB_DB = 'travistat-cache'
const IDB_STORE = 'kv'
const IDB_KEY_MARKERS = 'markersCache:v1'
const CACHE_TTL = 15 * 60 * 1000
const NO_ALLIANCE_KEY = 'no-alliance'
const NO_ALLIANCE_LABEL = 'No Alliance'


function openIdb () {
  return new Promise((resolve, reject) => {
    if (!('indexedDB' in window)) return reject(new Error('IndexedDB not supported'))

    const req = indexedDB.open(IDB_DB, 1)
    req.onupgradeneeded = () => {
      const db = req.result
      if (!db.objectStoreNames.contains(IDB_STORE)) db.createObjectStore(IDB_STORE)
    }
    req.onsuccess = () => resolve(req.result)
    req.onerror = () => reject(req.error || new Error('IndexedDB open failed'))
  })
}

async function idbGet (key) {
  const db = await openIdb()
  try {
    return await new Promise((resolve, reject) => {
      const tx = db.transaction(IDB_STORE, 'readonly')
      const store = tx.objectStore(IDB_STORE)
      const req = store.get(key)
      req.onsuccess = () => resolve(req.result ?? null)
      req.onerror = () => reject(req.error || new Error('IndexedDB get failed'))
    })
  } finally {
    try { db.close() } catch {}
  }
}

async function idbSet (key, value) {
  const db = await openIdb()
  try {
    await new Promise((resolve, reject) => {
      const tx = db.transaction(IDB_STORE, 'readwrite')
      const store = tx.objectStore(IDB_STORE)
      const req = store.put(value, key)
      req.onsuccess = () => resolve()
      req.onerror = () => reject(req.error || new Error('IndexedDB put failed'))
    })
  } finally {
    try { db.close() } catch {}
  }
}

async function idbDel (key) {
  const db = await openIdb()
  try {
    await new Promise((resolve, reject) => {
      const tx = db.transaction(IDB_STORE, 'readwrite')
      const store = tx.objectStore(IDB_STORE)
      const req = store.delete(key)
      req.onsuccess = () => resolve()
      req.onerror = () => reject(req.error || new Error('IndexedDB delete failed'))
    })
  } finally {
    try { db.close() } catch {}
  }
}

/** Best-effort: remove the legacy localStorage cache so it never triggers quota again */
function purgeLegacyLocalStorageMarkersCache () {
  try {
    localStorage.removeItem(CACHE_KEY)
  } catch {
    // ignore
  }
}

async function reloadMarkers (force = false) {
  loading.value = true
  try {
    purgeLegacyLocalStorageMarkersCache()

    let payload = null

    // Try IndexedDB cache (unless force)
    if (!force) {
      try {
        const env = await idbGet(IDB_KEY_MARKERS)
        if (env?.data && typeof env.at === 'number') {
          if (Date.now() - env.at < CACHE_TTL) payload = env.data
        }
      } catch {
        // ignore and re-fetch
      }
    }

    // Fetch from API if needed
    if (!payload) {
      const { data } = await api.get('/api/markers')
      payload = data

      // Store big payload in IndexedDB (never localStorage)
      try {
        await idbSet(IDB_KEY_MARKERS, { at: Date.now(), data })
      } catch {
        // ignore (still works without cache)
      }
    }

    markers.value = payload?.markers || ''
    toggles.value = {
      alliances: payload?.alliance_checkboxes || '',
      tribes: payload?.tribe_checkboxes || ''
    }

    await nextTick()
    // Split "no alliance" players out of the Natars bucket (client-side) so they can be toggled separately.
    splitNoAllianceFromNatars()
    bindMarkerEvents()
    updateMarkersVisibility()

    rebuildMinimapPoints()
    syncMinimapBounds()
    setInitialCenteredViewIfPossible()
  } catch (error) {
    console.error('Error loading markers:', error)
    markers.value = ''
    toggles.value = { alliances: '', tribes: '' }

    // If cached data caused issues, nuke the cache key
    try { await idbDel(IDB_KEY_MARKERS) } catch {}
  } finally {
    loading.value = false
  }
}

function hasClassPrefix(el, prefix) {
  return Array.from(el.classList).some((c) => c.startsWith(prefix))
}

function extractTooltipValue(html, key) {
  // Tooltip is backend-provided HTML with <br> separators.
  // Keep parsing conservative to avoid brittle coupling to backend formatting.
  const s = String(html || '')
  const m = s.match(new RegExp(`${key}\\s*:\\s*([^<\\n]+)`, 'i'))
  return m ? String(m[1] || '').trim() : ''
}

function ensureNoAllianceToggle() {
  // Remove any previously injected no-alliance toggle (prevents duplicates if sidebar re-renders)
  document.querySelectorAll('.no-alliance-toggle').forEach((el) => el.remove())

  // If the sidebar already includes our id, do nothing
  if (document.getElementById(`toggleAlliance-${NO_ALLIANCE_KEY}`)) return

  const natarsInput = document.getElementById('toggleAlliance-natars')
  if (!natarsInput) return

  const natarsWrapper = natarsInput.closest('label') || natarsInput.parentElement
  if (!natarsWrapper || !natarsWrapper.parentElement) return

  const clone = natarsWrapper.cloneNode(true)
  clone.classList.add('no-alliance-toggle')

  // Update input id + keep checked
  const input = clone.querySelector('input')
  if (input) {
    input.id = `toggleAlliance-${NO_ALLIANCE_KEY}`
    input.checked = true
    input.classList.add('alliance-checkbox')
  }

  // Force label text to "No Alliance" (replace any occurrence of Natars inside the clone)
  // This is robust across different HTML structures.
  const allTextNodes = []
  const walker = document.createTreeWalker(clone, NodeFilter.SHOW_TEXT)
  while (walker.nextNode()) allTextNodes.push(walker.currentNode)

  let replaced = false
  for (const tn of allTextNodes) {
    if (String(tn.nodeValue || '').toLowerCase().includes('natars')) {
      tn.nodeValue = String(tn.nodeValue).replace(/natars/gi, NO_ALLIANCE_LABEL)
      replaced = true
    }
  }

  // If we didn’t find “Natars” text nodes at all, set a sensible fallback.
  if (!replaced) {
    const labelEl = clone.querySelector('.label, .q-item__label, span, div')
    if (labelEl) labelEl.textContent = NO_ALLIANCE_LABEL
  }

  // Insert after Natars entry
  natarsWrapper.parentElement.insertBefore(clone, natarsWrapper.nextSibling)
}

function splitNoAllianceFromNatars() {
  const root = markersGroup.value
  if (!root) return

  const nodes = root.querySelectorAll('.marker')
  nodes.forEach((node) => {
    const alliance = getClassValue(node, 'alliance-')
    const tribe = getClassValue(node, 'tribe-')
    const tip = node.getAttribute('data-tooltip') || ''

    const tooltipAlliance = extractTooltipValue(tip, 'Alliance')
    const tooltipTribe = extractTooltipValue(tip, 'Tribe')

    // "No alliance" heuristic:
    // - Backend grouped missing alliances under "Natars".
    // - True Natars villages have tribe "Natars".
    const looksLikeNatarsBucket =
      alliance === 'natars' || String(tooltipAlliance).toLowerCase() === 'natars'
    const isTribeNatars =
      tribe === 'natars' || String(tooltipTribe).toLowerCase() === 'natars'

    // If it's in the Natars bucket but NOT actually Natars tribe => treat as No Alliance.
    if (looksLikeNatarsBucket && !isTribeNatars) {
      // Remove existing alliance-* class
      Array.from(node.classList)
        .filter((c) => c.startsWith('alliance-'))
        .forEach((c) => node.classList.remove(c))

      node.classList.add(`alliance-${NO_ALLIANCE_KEY}`)

      // Keep tooltip readable
      if (tip) {
        const updated = tip.replace(/Alliance\s*:\s*Natars/gi, `Alliance: ${NO_ALLIANCE_LABEL}`)
        node.setAttribute('data-tooltip', updated)
      }
    }

    // If there is NO alliance class at all, treat as No Alliance as well.
    if (!hasClassPrefix(node, 'alliance-')) {
      node.classList.add(`alliance-${NO_ALLIANCE_KEY}`)
    }
  })

  // Ensure sidebar toggle exists so filtering works.
  ensureNoAllianceToggle()
}

/* === Marker filtering/visibility === */
const elementText = (el) => (el.textContent || '').toLowerCase()

async function filterGroup(group) {
  await nextTick()
  const containers = document.querySelectorAll('.section-scroll')
  let root = null
  for (const container of containers) {
    if (container.innerHTML.includes(`toggle${capitalize(group.slice(0, -1))}`)) {
      root = container
      break
    }
  }
  if (!root) return
  const term = (groupFilters.value[group] || '').toLowerCase().trim()
  Array.from(root.querySelectorAll('label, .q-checkbox, .q-option, div, span')).forEach((el) => {
    el.style.display = term === '' || elementText(el).includes(term) ? '' : 'none'
  })
}
async function selectGroup(group, mode) {
  await nextTick()
  const checkboxClass = `${group.slice(0, -1)}-checkbox`
  const boxes = document.querySelectorAll(`.${checkboxClass}`)
  boxes.forEach((cb) => {
    if (mode === 'all') cb.checked = true
    else if (mode === 'none') cb.checked = false
    else cb.checked = !cb.checked
  })
  updateMarkersVisibility()
}
function toggleAllMarkers() {
  masterVisible = !masterVisible
  updateMarkersVisibility()
}
function getClassValue(el, prefix) {
  const c = Array.from(el.classList).find((x) => x.startsWith(prefix))
  return c ? c.slice(prefix.length) : ''
}
function updateMarkersVisibility() {
  if (!markersGroup.value) return
  const groupCheck = (type, val) => {
    const checkbox = document.getElementById(`toggle${capitalize(type)}-${val}`)
    return checkbox ? checkbox.checked !== false : true
  }
  markersGroup.value.querySelectorAll('.marker').forEach((node) => {
    const alliance = getClassValue(node, 'alliance-')
    const region = getClassValue(node, 'region-')
    const tribe = getClassValue(node, 'tribe-')
    const on =
      masterVisible &&
      (alliance ? groupCheck('Alliance', alliance) : true) &&
      (region ? groupCheck('Region', region) : true) &&
      (tribe ? groupCheck('Tribe', tribe) : true)
    node.style.display = on ? 'block' : 'none'
  })
}
function sanitize(html) {
  try {
    if (window.DOMPurify?.sanitize) return window.DOMPurify.sanitize(html, { USE_PROFILES: { html: true, svg: true } })
  } catch {}
  return String(html).replace(/<script[\s\S]*?>[\s\S]*?<\/script>/gi, '')
}
function bindMarkerEvents() {
  const root = markersGroup.value
  if (!root) return

  root.onpointerover = (e) => {
    const el = e.target.closest('.marker')
    if (!el) return
    const tip = el.getAttribute('data-tooltip') || ''
    tooltip.value = { show: true, x: e.clientX + 8, y: e.clientY + 8, content: sanitize(tip.replace(/<br>/g, '<br/>')) }
  }
  root.onpointerout = (e) => {
    if (e.relatedTarget && e.currentTarget.contains(e.relatedTarget)) return
    hideTooltip()
  }
}

/* === Background sizing === */
function layoutBackground() {
  syncMinimapBounds()
}

/* === Context menu === */
function onContextMenu(e) {
  e.preventDefault()
  const el = e.target.closest('.marker')
  ctx.hasMarker = !!el
  ctx.marker = el

  if (el) {
    const bb = el.getBBox()
    ctx.point = { x: bb.x + bb.width / 2, y: bb.y + bb.height / 2 }
  } else {
    const rect = svg.value.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top
    const transform = d3.zoomTransform(svg.value)
    ctx.point = { x: (x - transform.x) / transform.k, y: (y - transform.y) / transform.k }
  }
  contextPosition.value = { x: e.clientX, y: e.clientY }
  showContextMenu.value = true
  return false
}
function copyCoordinates() {
  if (!ctx.point) return
  const x = Math.round(ctx.point.x)
  const y = Math.round(-ctx.point.y)
  navigator.clipboard.writeText(`${x}|${y}`).then(() => {
    $q.notify({ message: 'Coordinates copied!', color: 'positive', position: 'top', timeout: 900 })
  })
}
function centerOnContext() {
  if (!ctx.point) return
  centerAt(ctx.point.x, ctx.point.y)
}
function hideTooltip() {
  tooltip.value.show = false
}

/* === Draw controls === */
let previewElem = null
let anchor = null
let isDrawing = false

function setDrawMode(mode) {
  drawMode.value = mode
  if (drawMode.value !== 'measure') {
    anchor = null
    isDrawing = false
    if (previewElem) {
      try { previewElem.remove() } catch {}
      previewElem = null
    }
  }
}
function toggleMeasureMode() {
  drawMode.value = drawMode.value === 'measure' ? null : 'measure'
  if (drawMode.value !== 'measure') {
    anchor = null
    isDrawing = false
    if (previewElem) {
      try { previewElem.remove() } catch {}
      previewElem = null
    }
  }
}
function toMapCoords(evt) {
  if (!svg.value) return { x: 0, y: 0 }
  const [sx, sy] = d3.pointer(evt, svg.value)
  const t = d3.zoomTransform(svg.value)
  return { x: t.invertX(sx), y: t.invertY(sy) }
}
const snap = (v) => (snapToGrid.value ? Math.round(v / gridSize.value) * gridSize.value : v)
function applyPreviewStyle(el) {
  el.setAttribute('stroke', drawColor.value)
  el.setAttribute('stroke-width', drawWidth.value)
  if (['rect', 'circle'].includes(drawMode.value)) el.setAttribute('fill', drawColor.value + '33')
  else el.setAttribute('fill', 'none')
  if (el.tagName === 'path') {
    el.setAttribute('stroke-linecap', 'round')
    el.setAttribute('stroke-linejoin', 'round')
  }
}
function onPointerDown(evt) {
  const p = toMapCoords(evt)
  cursor.value = p
  if (!drawMode.value) return

  evt.preventDefault()
  const pt = { x: snap(p.x), y: snap(p.y) }

  if (drawMode.value === 'text') {
    const txt = prompt('Enter text:')
    if (txt) {
      drawings.value.push({ type: 'text', x: pt.x, y: pt.y, text: txt, style: { stroke: drawColor.value, 'stroke-width': drawWidth.value, fill: 'none' } })
      pushHistory()
      saveToLocal()
    }
    return
  }

  if (drawMode.value === 'measure') {
    if (!anchor) {
      anchor = pt
      isDrawing = true
    } else {
      const dist = Math.hypot(pt.x - anchor.x, pt.y - anchor.y)
      drawings.value.push({ type: 'measure', x1: anchor.x, y1: anchor.y, x2: pt.x, y2: pt.y, distance: dist, style: { stroke: '#00bcd4', 'stroke-width': 1.5, 'stroke-dasharray': '2 2', fill: 'none' } })
      pushHistory()
      saveToLocal()
      anchor = null
      isDrawing = false
      if (previewElem) {
        previewLayer.value.removeChild(previewElem)
        previewElem = null
      }
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
function onPointerMove(evt) {
  const p = toMapCoords(evt)
  cursor.value = p
  updateViewWorldAndRulers()

  if (!isDrawing || !previewElem) return
  evt.preventDefault()
  const pt = { x: snap(p.x), y: snap(p.y) }

  switch (drawMode.value) {
    case 'line':
      previewElem.setAttribute('x2', pt.x)
      previewElem.setAttribute('y2', pt.y)
      break
    case 'rect': {
      const x = Math.min(anchor.x, pt.x)
      const y = Math.min(anchor.y, pt.y)
      const w = Math.abs(pt.x - anchor.x)
      const h = Math.abs(pt.y - anchor.y)
      previewElem.setAttribute('x', x)
      previewElem.setAttribute('y', y)
      previewElem.setAttribute('width', w)
      previewElem.setAttribute('height', h)
      break
    }
    case 'circle': {
      const r = Math.hypot(pt.x - anchor.x, pt.y - anchor.y)
      previewElem.setAttribute('r', r)
      break
    }
    case 'path': {
      previewElem.setAttribute('d', previewElem.getAttribute('d') + ` L${pt.x},${pt.y}`)
      break
    }
  }
}
function onPointerUp(evt) {
  if (!isDrawing || !previewElem || drawMode.value === 'measure') return
  evt.preventDefault()

  const finalize = (shape) => {
    drawings.value.push(shape)
    pushHistory()
    saveToLocal()
  }
  const color = drawColor.value
  const width = drawWidth.value

  if (drawMode.value === 'line') {
    finalize({ type: 'line', x1: +previewElem.getAttribute('x1'), y1: +previewElem.getAttribute('y1'), x2: +previewElem.getAttribute('x2'), y2: +previewElem.getAttribute('y2'), style: { stroke: color, 'stroke-width': width, fill: 'none' } })
  } else if (drawMode.value === 'rect') {
    finalize({ type: 'rect', x: +previewElem.getAttribute('x'), y: +previewElem.getAttribute('y'), width: +previewElem.getAttribute('width'), height: +previewElem.getAttribute('height'), style: { stroke: color, 'stroke-width': width, fill: color + '33' } })
  } else if (drawMode.value === 'circle') {
    finalize({ type: 'circle', cx: +previewElem.getAttribute('cx'), cy: +previewElem.getAttribute('cy'), r: +previewElem.getAttribute('r'), style: { stroke: color, 'stroke-width': width, fill: color + '33' } })
  } else if (drawMode.value === 'path') {
    finalize({ type: 'path', d: previewElem.getAttribute('d'), style: { stroke: color, 'stroke-width': width, fill: 'none', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' } })
  }

  previewLayer.value.removeChild(previewElem)
  previewElem = null
  isDrawing = false
  anchor = null
}

/* === Keybinds === */
function onKeydown(evt) {
  if ((evt.ctrlKey || evt.metaKey) && !evt.shiftKey && evt.key === 'z') {
    undo()
    evt.preventDefault()
  } else if ((evt.ctrlKey || evt.metaKey) && (evt.key === 'y' || (evt.shiftKey && evt.key === 'Z'))) {
    redo()
    evt.preventDefault()
  } else if (evt.key === 'Escape') {
    drawMode.value = null
    previewElem?.remove()
    previewElem = null
    isDrawing = false
    anchor = null
  } else if (evt.key.toLowerCase() === 'f') {
    toggleFullscreen()
  }
}

/* === Resize handling === */
function setupResizeObservers() {
  window.addEventListener('resize', scheduleResizeRefresh)

  const target = squareEl.value || stageEl.value || svg.value
  if (!target || typeof ResizeObserver === 'undefined') return
  resizeObserver = new ResizeObserver(() => {
    scheduleResizeRefresh()
    setInitialCenteredViewIfPossible()
  })
  resizeObserver.observe(target)
}

/* === Lifecycle === */
onMounted(async () => {
  lockPageScroll()
  window.addEventListener('keydown', onKeydown)

  await nextTick()

  if (svg.value) {
    zoom = d3
      .zoom()
      .scaleExtent([MIN_ZOOM_K, MAX_ZOOM_K])
      .on('zoom', (event) => {
        const { transform } = event
        if (!Number.isFinite(transform.x) || !Number.isFinite(transform.y) || !Number.isFinite(transform.k)) return
        d3.select(svg.value).select('#viewport').attr('transform', transform)
        zoomK.value = transform.k
        syncSliderFromZoom()
        updateViewWorldAndRulers()
      })

    syncZoomExtents()
    d3.select(svg.value).call(zoom).on('dblclick.zoom', null)
  }

  setupResizeObservers()

  syncMinimapBounds()

  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      setInitialCenteredViewIfPossible()
      scheduleResizeRefresh()
    })
  })

  handleCheckboxChange = (e) => {
    const t = e.target
    if (!t) return
    if (t.classList.contains('alliance-checkbox') || t.classList.contains('tribe-checkbox') || t.classList.contains('region-checkbox')) {
      updateMarkersVisibility()
    }
  }
  document.addEventListener('change', handleCheckboxChange)

  loadFromLocal()
  if (history.value.length === 0) pushHistory()

  await reloadMarkers()
  await nextTick()

  const img = new Image()
  img.onload = () => {
    const w = img.naturalWidth
    const h = img.naturalHeight
    if (Number.isFinite(w) && Number.isFinite(h) && w > 0 && h > 0) {
      bgMeta.w = w
      bgMeta.h = h
      bgMeta.loaded = true
      bgRect.x = -w / 2
      bgRect.y = -h / 2
      bgRect.width = w
      bgRect.height = h
      layoutBackground()
      rebuildMinimapPoints()
      scheduleResizeRefresh()
    }
  }
  img.onerror = () => {
    bgMeta.w = MAP_WORLD.width
    bgMeta.h = MAP_WORLD.height
    bgMeta.loaded = true
    bgRect.x = MAP_WORLD.x
    bgRect.y = MAP_WORLD.y
    bgRect.width = MAP_WORLD.width
    bgRect.height = MAP_WORLD.height
    syncMinimapBounds()
    scheduleResizeRefresh()
  }
  img.src = '/background.png'
})

onBeforeUnmount(() => {
  unlockPageScroll()
  window.removeEventListener('keydown', onKeydown)
  window.removeEventListener('resize', scheduleResizeRefresh)
  if (handleCheckboxChange) document.removeEventListener('change', handleCheckboxChange)
  if (resizeObserver) {
    try { resizeObserver.disconnect() } catch {}
    resizeObserver = null
  }
  cancelAnimationFrame(resizeRaf)
})

watch(
  groupFilters,
  (v) => {
    Object.keys(v).forEach((grp) => filterGroup(grp))
  },
  { deep: true }
)
</script>

<style scoped>
.map-page {
  height: 100vh !important;
  overflow: hidden !important;
}
.map-splitter {
  height: 100vh !important;
  overflow: hidden !important;
}
.panel {
  height: 100%;
  overflow-y: auto;
  background: #0d0d0d;
  color: #eaeaea;
}
.map-column {
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
  background: #000;
}
.map-stage {
  flex: 1;
  min-height: 0;
  position: relative;
  display: flex;
  align-items: stretch;
  justify-content: stretch;
  padding: 0;
}
.svg-square {
  position: relative;
  width: 100%;
  height: 100%;
  aspect-ratio: 1 / 1;
  margin: auto;
  background: #000;
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.45);
}
#svgMap {
  width: 100%;
  height: 100%;
  display: block;
}

/* Top HUD */
.map-hud {
  position: absolute;
  left: 12px;
  right: 12px;
  top: 12px;
  z-index: 10001;
  pointer-events: none;
}
.map-hud__row {
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
.map-hud__row::-webkit-scrollbar { height: 8px; }
.map-hud__jump { width: 260px; max-width: 46vw; flex: 0 0 auto; }
.map-hud__zoom { display: flex; align-items: center; gap: 8px; min-width: 270px; flex: 0 0 auto; }
.map-hud__slider { width: 160px; }
.map-hud__zoomtext { width: 56px; text-align: right; font-size: 12px; opacity: 0.9; color: rgba(0, 0, 0, 0.85); }
.map-hud__row .is-active { background: rgba(0, 0, 0, 0.08); border-radius: 999px; }

/* Draw panel */
.draw-panel {
  position: absolute;
  right: 14px;
  top: 40%;
  transform: translateY(-50%);
  z-index: 10002;
  pointer-events: none;
}
.draw-panel--mobile {
  right: 12px;
  top: auto;
  bottom: 92px;
  transform: none;
}
.draw-panel__card {
  pointer-events: auto;
  width: 280px;
  background: rgba(15, 15, 15, 0.90);
  border: 1px solid rgba(255, 255, 255, 0.12);
  box-shadow: 0 16px 38px rgba(0, 0, 0, 0.6);
  border-radius: 14px;
  overflow: hidden;
}
.draw-panel__head { display: flex; align-items: center; gap: 8px; padding: 10px 10px 8px; }
.draw-panel__title { display: flex; align-items: center; color: rgba(255, 255, 255, 0.92); font-size: 13px; font-weight: 700; letter-spacing: 0.2px; }
.draw-panel__iconbtn { color: rgba(255, 255, 255, 0.9); background: rgba(255, 255, 255, 0.06); border-radius: 10px; }
.draw-panel__body { padding: 10px; display: grid; gap: 10px; }
.draw-panel__section { background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.07); border-radius: 12px; padding: 10px; }
.draw-panel__label { color: rgba(255, 255, 255, 0.78); font-size: 11px; font-weight: 700; letter-spacing: 0.25px; text-transform: uppercase; margin-bottom: 8px; }
.draw-panel__row { display: flex; align-items: center; gap: 10px; }
.draw-panel__modes { display: grid; grid-template-columns: repeat(7, 1fr); gap: 6px; }
.draw-panel__modebtn { height: 36px; border-radius: 12px; color: rgba(255, 255, 255, 0.92); background: rgba(255, 255, 255, 0.06); }
.draw-panel__modebtn.is-active { background: rgba(0, 188, 212, 0.22); outline: 1px solid rgba(0, 188, 212, 0.55); }
.draw-panel__actions { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
.draw-panel__actionbtn { height: 36px; border-radius: 12px; color: rgba(255, 255, 255, 0.92); background: rgba(255, 255, 255, 0.06); }
.draw-panel__actionbtn.is-active { background: rgba(0, 188, 212, 0.20); outline: 1px solid rgba(0, 188, 212, 0.45); }
.draw-panel__pill { height: 28px; border-radius: 999px; padding: 0 10px; color: rgba(255, 255, 255, 0.92); background: rgba(255, 255, 255, 0.06); }
.draw-panel__pill.is-active { background: rgba(255, 255, 255, 0.14); outline: 1px solid rgba(255, 255, 255, 0.18); }
.draw-panel__swatches { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; max-width: 150px; }
.swatch { width: 18px; height: 18px; border-radius: 999px; border: 1px solid rgba(255, 255, 255, 0.18); box-shadow: 0 2px 8px rgba(0, 0, 0, 0.35); cursor: pointer; }
.swatch.is-active { outline: 2px solid rgba(255, 255, 255, 0.75); outline-offset: 2px; }
.draw-panel__widths { display: flex; gap: 6px; }
.draw-panel__menu { background: #101010; color: #fff; }

/* Tooltip */
.tooltip {
  position: fixed;
  pointer-events: none;
  background: rgba(0, 0, 0, 0.9);
  color: #fff;
  padding: 6px 8px;
  border-radius: 6px;
  font-size: 0.8rem;
  white-space: nowrap;
  z-index: 1000;
  border: 1px solid rgba(255, 255, 255, 0.08);
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

/* Markers */
:deep(.marker) { cursor: pointer; transition: filter 120ms ease, opacity 120ms ease; }
:deep(.marker:hover) { filter: drop-shadow(0 0 8px rgba(255, 255, 255, 0.35)); }

/* Measure label */
.measure-label {
  paint-order: stroke;
  stroke: #000;
  stroke-width: 0.6;
  fill: #fff;
}

/* Minimap */
.minimap {
  position: absolute;
  right: 12px;
  bottom: 12px;
  width: 260px;
  border-radius: 14px;
  background: rgba(15, 15, 15, 0.88);
  border: 1px solid rgba(255, 255, 255, 0.12);
  box-shadow: 0 16px 36px rgba(0, 0, 0, 0.55);
  z-index: 10003;
  padding: 10px;
}
.minimap__header { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.minimap__title { font-size: 12px; color: rgba(255, 255, 255, 0.92); letter-spacing: 0.2px; font-weight: 600; }
.minimap__actions { margin-left: auto; display: flex; gap: 2px; }
.minimap__actions :deep(.q-btn) { color: rgba(255, 255, 255, 0.92); background: rgba(255, 255, 255, 0.06); border-radius: 10px; }
.minimap__svg {
  width: 100%;
  height: 170px;
  display: block;
  border-radius: 12px;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.25);
  outline: 1px solid rgba(255, 255, 255, 0.06);
  cursor: grab;
}
.minimap__svg:active { cursor: grabbing; }
.minimap__viewport { vector-effect: non-scaling-stroke; }
.minimap__footer { margin-top: 8px; display: grid; gap: 2px; }
.minimap__line { font-size: 12px; color: rgba(255, 255, 255, 0.9); }
.minimap__muted { color: rgba(255, 255, 255, 0.65); margin-left: 6px; }


/* Distance & travel time menu */
.distance-menu { border-radius: 14px; overflow: hidden; }
.distance-card { width: 360px; max-width: 88vw; background: rgba(20, 20, 20, 0.98); color: rgba(255, 255, 255, 0.92); }
.distance-card__head { padding: 10px 12px; }
.distance-card__title { display: flex; align-items: center; font-weight: 700; letter-spacing: 0.2px; }
.distance-card__body { padding: 12px; }
.distance-card__meta { display: grid; gap: 2px; font-size: 12px; color: rgba(255, 255, 255, 0.85); }
.distance-card__table :deep(th),
.distance-card__table :deep(td) { padding: 6px 8px; }
.distance-card__table :deep(thead tr) { background: rgba(255, 255, 255, 0.04); }
.distance-card__table :deep(tbody tr.is-highlight) { background: rgba(0, 255, 255, 0.08); }
.distance-card__table :deep(tbody tr.is-highlight td) { color: rgba(255, 255, 255, 0.98); }

.statusbar__sep { opacity: 0.6; margin: 0 6px; }

/* Mobile tweaks */
@media (max-width: 599px) {
  .map-hud__jump { width: 210px; max-width: 55vw; }
  .map-hud__zoom { display: none; }
  .minimap { width: 210px; }
  .minimap__svg { height: 140px; }
  .draw-panel__card { width: 260px; }
}

/* Global scroll lock class */
:global(html.map-no-scroll),
:global(body.map-no-scroll) {
  overflow: hidden !important;
}
</style>
