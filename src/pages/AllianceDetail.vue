<template>
  <q-page class="column alliance-detail-page" :style-fn="(_, height) => ({ height: height + 'px' })">
    <!-- Toolbar -->
    <q-toolbar class="alliance-toolbar">
      <q-btn dense flat round icon="arrow_back" class="toolbar-btn" @click="$router.back()" />
      <q-toolbar-title class="toolbar-title">
        <div class="title-row">
          <div class="title-main">Alliance</div>
          <div class="title-tag">{{ tag }}</div>
        </div>
        <div class="title-sub">
          {{ stats.villages.toLocaleString() }} villages •
          {{ stats.totalPop.toLocaleString() }} pop •
          {{ stats.totalVP.toLocaleString() }} VP •
          Avg {{ stats.avgPop.toLocaleString() }} pop/village
        </div>
      </q-toolbar-title>

      <div class="row items-center q-gutter-sm on-right q-pr-sm toolbar-actions">
        <q-chip dense square class="kpi-chip" icon="groups">
          {{ stats.villages }} villages
        </q-chip>
        <q-chip dense square class="kpi-chip" icon="diversity_3">
          {{ stats.totalPop.toLocaleString() }} pop
        </q-chip>
        <q-chip dense square class="kpi-chip" icon="star">
          {{ stats.totalVP.toLocaleString() }} VP
        </q-chip>

        <q-separator vertical class="toolbar-sep" />

        <q-btn dense flat round icon="center_focus_strong" class="toolbar-btn" @click="fitToContent">
          <q-tooltip>Fit to alliance</q-tooltip>
        </q-btn>
        <q-btn
          dense flat round icon="open_in_new"
          class="toolbar-btn"
          :href="`https://nys.x1.europe.travian.com/karte.php?alliance=${encodeURIComponent(tag)}`"
          target="_blank"
        >
          <q-tooltip>Open in Travian map</q-tooltip>
        </q-btn>
      </div>
    </q-toolbar>

    <!-- Content -->
    <div class="content-wrap q-pa-md">
      <q-splitter v-model="split" :limits="[22, 72]" class="alliance-splitter">
        <!-- MAP PANEL -->
        <template #before>
          <div class="panel map-panel">
            <div class="panel-header">
              <div class="row items-center no-wrap q-gutter-sm">
                <q-icon name="public" size="18px" class="panel-icon" />
                <div class="panel-title">Alliance Map</div>
                <q-space />
                <q-chip dense square class="meta-chip" icon="gps_fixed">
                  Cursor: X {{ cursor.x.toFixed(0) }} / Y {{ cursor.y.toFixed(0) }}
                </q-chip>
                <q-chip dense square class="meta-chip" icon="zoom_in">
                  {{ zoomK.toFixed(2) }}×
                </q-chip>
              </div>

              <div class="row items-center q-gutter-sm q-mt-sm">
                <q-btn-group unelevated rounded class="toolgroup">
                  <q-btn
                    dense
                    icon="center_focus_strong"
                    label="Fit"
                    class="toolbtn"
                    @click="fitToContent"
                  />
                  <q-btn dense icon="restart_alt" label="Reset" class="toolbtn" @click="resetView" />
                </q-btn-group>

                <q-space />

                <q-btn dense flat icon="help_outline" class="hint-btn">
                  <q-tooltip>
                    Drag to pan • Wheel/trackpad to zoom • Hover markers for details • Click marker to open player
                  </q-tooltip>
                </q-btn>
              </div>
            </div>

            <div class="map-area" ref="mapAreaEl" @contextmenu.capture="onContextMenu">
              <svg
                ref="svg"
                viewBox="-200 -200 400 400"
                preserveAspectRatio="xMidYMid meet"
                @pointerdown="onPointerDown"
                @pointermove="onPointerMove"
                @pointerup="onPointerUp"
                @mouseleave="hideTooltip"
              >
                <g id="viewport">
                  <!-- Optional background image -->
                  <image
                    x="-200"
                    y="-200"
                    width="400"
                    height="400"
                    :href="bgUrl"
                    :xlink:href="bgUrl"
                    preserveAspectRatio="none"
                    opacity="0.75"
                  />

                  <!-- Fallback GRID -->
                  <g id="grid">
                    <template v-for="x in gridTicks" :key="'vx' + x">
                      <line
                        :x1="x"
                        y1="-200"
                        :x2="x"
                        y2="200"
                        stroke="#3f3f3f"
                        stroke-width="0.6"
                        vector-effect="non-scaling-stroke"
                      />
                    </template>
                    <template v-for="y in gridTicks" :key="'hz' + y">
                      <line
                        x1="-200"
                        :y1="y"
                        x2="200"
                        :y2="y"
                        stroke="#3f3f3f"
                        stroke-width="0.6"
                        vector-effect="non-scaling-stroke"
                      />
                    </template>
                  </g>

                  <!-- Axes -->
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

                  <!-- World border -->
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

                  <!-- Markers -->
                  <g ref="markersGroup" id="markersLayer" v-html="svgContent"></g>

                  <!-- Hover selection -->
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
                    <circle v-if="selection" :cx="selection.x" :cy="selection.y" :r="0.9" fill="#00e5ff" opacity="0.85" />
                  </g>

                  <!-- Debug center dot -->
                  <circle cx="0" cy="0" r="0.9" fill="#ff5252" opacity="0.9" />
                </g>

                <!-- Screen-fixed coord labels -->
                <g id="coordLabels">
                  <text id="labelLeft" text-anchor="end" alignment-baseline="middle" class="coord-label" />
                  <text id="labelRight" text-anchor="start" alignment-baseline="middle" class="coord-label" />
                  <text id="labelTop" text-anchor="middle" alignment-baseline="hanging" class="coord-label" />
                  <text id="labelBottom" text-anchor="middle" alignment-baseline="baseline" class="coord-label" />
                </g>
              </svg>

              <div v-if="!loading && !rawSvg" class="empty-hint">
                <div class="empty-card">
                  <q-icon name="info" size="18px" />
                  <div>No markers received from the server for this alliance.</div>
                </div>
              </div>

              <!-- Right-click context menu -->
              <q-menu context-menu touch-position>
                <q-list style="min-width: 220px">
                  <q-item-label header>Map</q-item-label>
                  <q-item clickable :disable="!ctx.hasMarker" v-close-popup @click="centerOnContext">
                    <q-item-section avatar><q-icon name="center_focus_strong" /></q-item-section>
                    <q-item-section>Center map on this village</q-item-section>
                  </q-item>
                  <q-separator />
                  <q-item clickable v-close-popup @click="fitToContent">
                    <q-item-section avatar><q-icon name="fit_screen" /></q-item-section>
                    <q-item-section>Fit to alliance</q-item-section>
                  </q-item>
                  <q-item clickable v-close-popup @click="resetView">
                    <q-item-section avatar><q-icon name="restart_alt" /></q-item-section>
                    <q-item-section>Reset view</q-item-section>
                  </q-item>
                </q-list>
              </q-menu>

              <q-inner-loading :showing="loading">
                <q-spinner color="primary" size="2em" />
              </q-inner-loading>

              <!-- Tooltip -->
              <div
                v-if="tooltip.show"
                class="tooltip"
                :style="{ top: tooltip.y + 'px', left: tooltip.x + 'px' }"
                v-html="tooltip.content"
              />
            </div>

            <div class="statusbar row items-center q-px-sm q-py-xs">
              <div class="col text-caption status-left">
                Drag to pan • Scroll to zoom • Right-click for actions
              </div>
              <div class="col text-caption text-right status-right">
                Markers: {{ villages.length.toLocaleString() }} • Filtered: {{ villagesFiltered.length.toLocaleString() }}
              </div>
            </div>
          </div>
        </template>

        <!-- TABLE PANEL -->
        <template #after>
          <div class="panel table-panel">
            <div class="panel-header">
              <div class="row items-center no-wrap q-gutter-sm">
                <q-icon name="table_view" size="18px" class="panel-icon" />
                <div class="panel-title">Villages</div>
                <q-chip dense square class="meta-chip">
                  {{ villagesFiltered.length.toLocaleString() }} / {{ villages.length.toLocaleString() }}
                </q-chip>
                <q-space />
                <q-btn dense flat round icon="download" class="toolbar-btn" @click="exportCsv">
                  <q-tooltip>Export filtered (CSV)</q-tooltip>
                </q-btn>
              </div>

              <div class="row items-center q-gutter-sm q-mt-sm">
                <q-input
                  v-model="filter"
                  dense
                  outlined
                  clearable
                  debounce="150"
                  placeholder="Filter villages / players / coords…"
                  class="filter-input"
                >
                  <template #prepend><q-icon name="search" /></template>
                  <template #append>
                    <q-btn
                      v-if="filter"
                      dense
                      flat
                      round
                      icon="close"
                      @click="filter = ''"
                    />
                  </template>
                </q-input>

                <q-btn dense outline icon="tune" label="Columns" class="colbtn">
                  <q-menu>
                    <q-list style="min-width: 240px">
                      <q-item-label header>Visible columns</q-item-label>
                      <q-item v-for="c in columns" :key="c.name" clickable>
                        <q-item-section>
                          <q-toggle
                            v-model="visibleColumnSet[c.name]"
                            :label="c.label"
                            dense
                          />
                        </q-item-section>
                      </q-item>
                    </q-list>
                  </q-menu>
                </q-btn>
              </div>
            </div>

            <div class="q-pa-md table-wrap">
              <q-table
                  style="height: 100%;"
                  class="villages-table"
                  :columns="columnsVisible"
                  :rows="villagesFiltered"
                  row-key="coords"
                  flat
                  :pagination.sync="pagination"
                  :rows-per-page-options="[10, 20, 50, 0]"
                  :filter="filter"
                  virtual-scroll
                  :virtual-scroll-sticky-size-start="44"
                  @row-click="(_, row) => centerFromCoords(row.coords)"
                >
                <template #body-cell-village="props">
                  <q-td :props="props" class="cell-strong">
                    <div class="ellipsis">{{ props.row.village }}</div>
                    <div class="cell-sub ellipsis">{{ props.row.coords }}</div>
                  </q-td>
                </template>

                <template #body-cell-player="props">
                  <q-td :props="props">
                    <RouterLink class="link" :to="{ name: 'player-detail', params: { name: props.row.player } }">
                      {{ props.row.player }}
                    </RouterLink>
                  </q-td>
                </template>

                <template #body-cell-coords="props">
                  <q-td :props="props">
                    <a
                      class="link"
                      :href="makeMapLink(props.row.coords)"
                      target="_blank"
                      rel="noopener"
                      @mouseenter="hoverCoords(props.row.coords)"
                      @mouseleave="selection = null"
                      @click.stop
                    >{{ props.row.coords }}</a>
                  </q-td>
                </template>

                <template #body-cell-population="props">
                  <q-td :props="props" class="text-right tabular">
                    {{ Number(props.row.population || 0).toLocaleString() }}
                  </q-td>
                </template>

                <template #body-cell-victoryPoints="props">
                  <q-td :props="props" class="text-right tabular">
                    {{ Number(props.row.victoryPoints || 0).toLocaleString() }}
                  </q-td>
                </template>
              </q-table>
            </div>
          </div>
        </template>
      </q-splitter>
    </div>

    <!-- Player Profile Dialog -->
    <q-dialog v-model="profileDialog">
      <q-card class="profile-card">
        <q-card-section class="row items-center">
          <div class="text-h6">Player: {{ profile.name }}</div>
          <q-space />
          <q-btn icon="close" flat round dense @click="profileDialog = false" />
        </q-card-section>
        <q-separator />
        <q-card-section v-if="profile.villages.length">
          <q-table
            :columns="profileColumns"
            :rows="profile.villages"
            row-key="coords"
            flat
            dense
            wrap-cells
            :rows-per-page-options="[10, 20, 50, 0]"
          />
        </q-card-section>
        <q-card-section v-else class="text-grey">
          No villages found for this player.
        </q-card-section>
        <q-card-actions align="right">
          <div class="text-subtitle2">
            Total population: {{ profile.totalPopulation.toLocaleString() }}
          </div>
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick, onBeforeUnmount, watch } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { api } from 'boot/axios'
import * as d3 from 'd3'
import bgUrl from 'assets/background.png' // optional; safe if missing

/* Route & layout */
const route = useRoute()
const tag = route.params.tag
const split = ref(35)

/* Refs */
const mapAreaEl = ref(null)
const svg = ref(null)
const markersGroup = ref(null)

/* Map state */
const rawSvg = ref('')
const svgContent = ref('')
const loading = ref(false)
const zoomK = ref(1)
const cursor = ref({ x: 0, y: 0 })

/* Marker visibility/size */
const markerSize = ref(2)

/* Fallback grid ticks every 10 units across -200..200 */
const gridTicks = Array.from({ length: 41 }, (_, i) => -200 + i * 10)

/* Tooltip & context menu */
const tooltip = ref({ show: false, x: 0, y: 0, content: '' })
const hideTooltip = () => { tooltip.value.show = false }
const ctx = reactive({ hasMarker: false, point: null })

/* Table data */
const villages = ref([])
const filter = ref('')
const pagination = ref({ page: 1, rowsPerPage: 20 })

/* Columns */
const columns = [
  { name: 'village', label: 'Village', field: 'village', align: 'left', sortable: true },
  { name: 'coords', label: 'Coords', field: 'coords', align: 'left', sortable: true },
  { name: 'population', label: 'Population', field: 'population', align: 'right', sortable: true },
  { name: 'victoryPoints', label: 'VP', field: 'victoryPoints', align: 'right', sortable: true },
  { name: 'player', label: 'Player', field: 'player', align: 'left', sortable: true },
  { name: 'tribe', label: 'Tribe', field: 'tribe', align: 'left', sortable: true }
]

/* Column visibility (UI only) */
const visibleColumnSet = reactive({
  village: true,
  coords: true,
  population: true,
  victoryPoints: true,
  player: true,
  tribe: true
})
const columnsVisible = computed(() => columns.filter(c => visibleColumnSet[c.name] !== false))

/* Summary stats */
const stats = computed(() => {
  const v = villages.value
  const villagesCount = v.length
  const totalPop = v.reduce((s, r) => s + (r.population || 0), 0)
  const totalVP = v.reduce((s, r) => s + (r.victoryPoints || 0), 0)
  return { villages: villagesCount, totalPop, avgPop: villagesCount ? Math.round(totalPop / villagesCount) : 0, totalVP }
})

/* Filtered rows */
const villagesFiltered = computed(() => {
  const q = filter.value.trim().toLowerCase()
  if (!q) return villages.value
  return villages.value.filter(r =>
    (r.village || '').toLowerCase().includes(q) ||
    (r.coords || '').toLowerCase().includes(q) ||
    (r.player || '').toLowerCase().includes(q) ||
    (r.tribe || '').toLowerCase().includes(q)
  )
})

/* Player dialog */
const profileDialog = ref(false)
const profile = ref({ name: '', villages: [], totalPopulation: 0 })
const profileColumns = [
  { name: 'village', label: 'Village', field: 'village' },
  { name: 'coords', label: 'Coords', field: 'coords' },
  { name: 'population', label: 'Population', field: 'population', align: 'right' },
  { name: 'victoryPoints', label: 'VP', field: 'victoryPoints', align: 'right' }
]
async function openProfile (owner) {
  try {
    const { data } = await api.get(`/api/player/${encodeURIComponent(owner)}/villages`)
    profile.value.name = data.player
    profile.value.villages = data.villages.map(r => ({
      village: r.village_name,
      coords: `(${r.x},${r.y})`,
      population: r.population,
      victoryPoints: r.victory_points,
      alliance: r.alliance_tag,
      tribe: r.tribe
    }))
    profile.value.totalPopulation = profile.value.villages.reduce((sum, v) => sum + (v.population || 0), 0)
  } catch {
    profile.value = { name: owner, villages: [], totalPopulation: 0 }
  }
  profileDialog.value = true
}

/* Helpers */
function makeMapLink (coords) {
  const m = coords.match(/\((-?\d+),\s*(-?\d+)\)/)
  return m ? `https://nys.x1.europe.travian.com/karte.php?x=${m[1]}&y=${m[2]}` : '#'
}
function parseCoords (coords) {
  const m = coords.match(/\((-?\d+),\s*(-?\d+)\)/)
  return m ? { x: Number(m[1]), y: Number(m[2]) } : null
}
function sanitizeHtml (html) {
  return String(html)
    .replace(/<script[\s\S]*?<\/script>/gi, '')
    .replace(/<style[\s\S]*?<\/style>/gi, '')
    .replace(/<\/?svg[^>]*>/gi, '')
}
function sanitizeTooltip (html) {
  try { if (window.DOMPurify?.sanitize) return window.DOMPurify.sanitize(html, { USE_PROFILES: { html: true, svg: true } }) } catch {}
  return String(html).replace(/<script[\s\S]*?<\/script>/gi, '')
}

/* Selection from table hover */
const selection = ref(null)
function hoverCoords (coords) {
  const pt = parseCoords(coords)
  selection.value = pt ? { x: pt.x, y: pt.y } : null
}
function centerFromCoords (coords) {
  const pt = parseCoords(coords)
  if (pt) centerAt(pt.x, pt.y)
}

/* D3 zoom */
let zoom

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
function centerAt (x, y, k = d3.zoomTransform(svg.value).k || 1) {
  const rect = getContainerRect()
  if (!rect || !Number.isFinite(x) || !Number.isFinite(y)) return
  k = Number.isFinite(k) && k > 0 ? k : 1
  const tx = rect.width / 2 - k * x
  const ty = rect.height / 2 - k * y
  if (!Number.isFinite(tx) || !Number.isFinite(ty)) return
  const t = d3.zoomIdentity.translate(tx, ty).scale(k)
  d3.select(svg.value).transition().duration(250).call(zoom.transform, t)
}
function fitToBBox (bbox, pad = 1.02) {
  const rect = getContainerRect()
  if (!rect || !bbox) return
  if (!(bbox.width > 0) || !(bbox.height > 0)) return
  const kCand = Math.min(rect.width / (bbox.width * pad), rect.height / (bbox.height * pad))
  const k = (Number.isFinite(kCand) && kCand > 0) ? kCand : 1
  const cx = bbox.x + bbox.width / 2
  const cy = bbox.y + bbox.height / 2
  if (!Number.isFinite(cx) || !Number.isFinite(cy)) return
  centerAt(cx, cy, k)
}
function unionBBox (a, b) {
  const ax2 = a.x + a.width, ay2 = a.y + a.height
  const bx2 = b.x + b.width, by2 = b.y + b.height
  const x = Math.min(a.x, b.x)
  const y = Math.min(a.y, b.y)
  const x2 = Math.max(ax2, bx2)
  const y2 = Math.max(ay2, by2)
  return { x, y, width: x2 - x, height: y2 - y }
}
function markersBBoxOrDefault () {
  const g = markersGroup.value || svg.value?.querySelector?.('#markersLayer')
  if (g?.getBBox) {
    const bb = g.getBBox()
    if (bb && bb.width > 0 && bb.height > 0) return bb
  }
  return { x: -200, y: -200, width: 400, height: 400 }
}

function fitToContent () {
  const all = unionBBox(markersBBoxOrDefault(), { x: -200, y: -200, width: 400, height: 400 })
  fitToBBox(all, 1.02)
}
function updateLabels () {
  const box = getContainerRect()
  if (!box) return
  const t = d3.zoomTransform(svg.value)
  d3.select('#labelLeft').text(t.invertX(0).toFixed(0)).attr('x', 8).attr('y', box.height / 2)
  d3.select('#labelRight').text(t.invertX(box.width).toFixed(0)).attr('x', box.width - 8).attr('y', box.height / 2)
  d3.select('#labelTop').text(t.invertY(0).toFixed(0)).attr('x', box.width / 2).attr('y', 8)
  d3.select('#labelBottom').text(t.invertY(box.height).toFixed(0)).attr('x', box.width / 2).attr('y', box.height - 8)
}

/* New: reset view */
function resetView () {
  const rect = getContainerRect()
  if (!rect) return
  const k = 1
  const tx = rect.width / 2 - k * 0
  const ty = rect.height / 2 - k * 0
  const t = d3.zoomIdentity.translate(tx, ty).scale(k)
  d3.select(svg.value).transition().duration(250).call(zoom.transform, t)
}

/* Normalize marker size/appearance after injection */
function normalizeMarkers () {
  const root = markersGroup.value
  if (!root) return
  root.querySelectorAll('.marker').forEach(el => {
    el.setAttribute('width', String(markerSize.value))
    el.setAttribute('height', String(markerSize.value))
    el.setAttribute('shape-rendering', 'crispEdges')
    el.setAttribute('opacity', '1')
    el.setAttribute('stroke', '#111')
    el.setAttribute('stroke-width', '0.25')
  })
}

/* Marker interactions (delegated) */
function bindMarkerDelegatedEvents () {
  const root = markersGroup.value
  if (!root) return
  root.onpointerover = (e) => {
    const el = e.target.closest('.marker')
    if (!el) return
    const tip = el.getAttribute('data-tooltip') || ''
    const content = sanitizeTooltip(tip.replace(/<br>/g, '<br/>'))
    tooltip.value = { show: true, x: e.clientX + 10, y: e.clientY + 10, content }
  }
  root.onpointerout = (e) => {
    if (e.relatedTarget && e.currentTarget.contains(e.relatedTarget)) return
    hideTooltip()
  }
  root.onclick = async (e) => {
    const el = e.target.closest('.marker')
    if (!el) return
    let owner = (el.getAttribute('data-player') || '').replace(/^'+|'+$/g, '')
    if (owner) await openProfile(owner)
  }
}

/* Context menu */
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
function centerOnContext () {
  if (!ctx.point) return
  centerAt(ctx.point.x, ctx.point.y)
}

/* Pointer handlers */
function onPointerDown (evt) { cursor.value = toMapCoords(evt) }
function onPointerMove (evt) { cursor.value = toMapCoords(evt) }
function onPointerUp (evt) { cursor.value = toMapCoords(evt) }

/* Export CSV (filtered) */
function exportCsv () {
  const rows = villagesFiltered.value
  const headers = ['village', 'coords', 'population', 'victoryPoints', 'player', 'tribe']
  const esc = (v) => `"${String(v ?? '').replaceAll('"', '""')}"`
  const csv = [
    headers.join(','),
    ...rows.map(r => headers.map(h => esc(r[h])).join(','))
  ].join('\n')

  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `alliance_${String(tag).replaceAll(' ', '_')}_villages.csv`
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

/* Mount & resize */
let ro = null
let didInitialFit = false

function scheduleSafeFit () {
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      const rect = getContainerRect()
      if (!rect) return

      if (!didInitialFit) {
        fitToContent()
        didInitialFit = true
      }

      updateLabels()
    })
  })
}
watch(split, scheduleSafeFit)

function fitWhenReady (tries = 20) {
  requestAnimationFrame(() => {
    const rect = getContainerRect()
    const g = markersGroup.value || svg.value?.querySelector?.('#markersLayer')
    const bb = g?.getBBox?.()

    const rectOk = !!rect
    const bboxOk = bb && bb.width > 0 && bb.height > 0

    if (rectOk && (bboxOk || tries <= 0)) {
      fitToContent()
      updateLabels()
      didInitialFit = true
      return
    }

    fitWhenReady(tries - 1)
  })
}




onMounted(async () => {
  loading.value = true
  try {
    zoom = d3.zoom()
      .scaleExtent([0.5, 50])
      .on('zoom', ({ transform }) => {
        d3.select('#viewport').attr('transform', transform)
        zoomK.value = transform.k
        updateLabels()
      })
    d3.select(svg.value).call(zoom)

    ro = new ResizeObserver(() => scheduleSafeFit())
    if (mapAreaEl.value) ro.observe(mapAreaEl.value)

    const mapRes = await api.get(`/api/alliance/${encodeURIComponent(tag)}/map`)
    rawSvg.value = mapRes.data?.markers || ''
    svgContent.value = sanitizeHtml(rawSvg.value)
    await nextTick()
    normalizeMarkers()
    bindMarkerDelegatedEvents()
    fitWhenReady()
    const listRes = await api.get(`/api/alliance/${encodeURIComponent(tag)}/villages`)
    villages.value = (listRes.data?.villages || []).map(r => ({
      village: r.village_name,
      coords: `(${r.x},${r.y})`,
      population: r.population,
      victoryPoints: r.victory_points,
      player: r.player_name,
      tribe: r.tribe
    }))
    await nextTick()
  } finally {
    loading.value = false
  }
})

onBeforeUnmount(() => {
  if (ro && mapAreaEl.value) ro.unobserve(mapAreaEl.value)
})
</script>

<style scoped>
.alliance-detail-page {
  height: 100%;
  min-height: 0;
  overflow: hidden;
  padding: 0;
  background: radial-gradient(1200px 800px at 20% 0%, rgba(0, 229, 255, 0.08), transparent 60%),
              radial-gradient(900px 600px at 90% 10%, rgba(123, 97, 255, 0.10), transparent 55%),
              #07090c;
}

/* Toolbar */
.alliance-toolbar {
  background: linear-gradient(90deg, rgba(0,229,255,0.14), rgba(123,97,255,0.12));
  border-bottom: 1px solid rgba(255,255,255,0.06);
  color: #eaf6ff;
}
.toolbar-title {
  padding-left: 6px;
}
.title-row {
  display: flex;
  align-items: baseline;
  gap: 10px;
}
.title-main {
  font-weight: 700;
  letter-spacing: 0.4px;
}
.title-tag {
  font-weight: 800;
  letter-spacing: 0.6px;
  color: #00e5ff;
  text-shadow: 0 0 18px rgba(0,229,255,0.15);
}
.title-sub {
  margin-top: 2px;
  font-size: 12px;
  color: rgba(234,246,255,0.76);
}
.kpi-chip {
  background: rgba(255,255,255,0.9);
  color: #0a0f14;
}
.toolbar-btn {
  border-radius: 10px;
  transition: transform 120ms ease, background 120ms ease;
}
.toolbar-btn:hover {
  transform: translateY(-1px);
  background: rgba(255,255,255,0.06);
}
.toolbar-sep {
  height: 26px;
  opacity: 0.35;
}

/* Layout */
.content-wrap {
  flex: 1;
  min-height: 0;
  overflow: hidden;   /* key: prevents content Y scrolling */
  height: auto;
  display: flex;          /* add */
  flex-direction: column; /* add */
}
.alliance-splitter {
  flex: 1;        /* add */
  min-height: 0;
  height: auto;   /* change from 100% */
}
.alliance-splitter :deep(.q-splitter__separator) {
  width: 10px;
  background: transparent;
}
.alliance-splitter :deep(.q-splitter__separator-area) {
  background: transparent;
}
.alliance-splitter :deep(.q-splitter__separator-area:hover) {
  background: rgba(255, 255, 255, 0.04);
  border-radius: 10px;
}

/* Panels */
.panel {
  height: 100%;
  min-height: 0;
  border-radius: 14px;
  overflow: hidden;
  background: rgba(10, 12, 16, 0.78);
  border: 1px solid rgba(255, 255, 255, 0.06);
  color: #eaeaea;
  backdrop-filter: blur(10px);
  box-shadow: 0 12px 30px rgba(0,0,0,0.35);
}
.panel-header {
  padding: 12px 12px 10px 12px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  background: linear-gradient(180deg, rgba(255,255,255,0.03), transparent);
}
.panel-title {
  font-weight: 700;
  letter-spacing: 0.35px;
}
.panel-icon {
  color: rgba(0,229,255,0.9);
  filter: drop-shadow(0 0 10px rgba(0,229,255,0.2));
}
.meta-chip {
  background: rgba(255,255,255,0.06);
  color: rgba(234,246,255,0.88);
  border: 1px solid rgba(255,255,255,0.06);
}
.toolgroup {
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(255,255,255,0.03);
}
.toolbtn {
  text-transform: none;
}
.hint-btn {
  opacity: 0.9;
}

/* Map */
.map-panel {
  display: flex;
  flex-direction: column;
  min-height: 0;
}
.map-area {
  position: relative;
  flex: 1;
  min-height: 0;
  background: #000;
}
.map-area svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(900px 600px at 40% 20%, rgba(0,229,255,0.06), transparent 55%),
              radial-gradient(900px 600px at 70% 40%, rgba(123,97,255,0.06), transparent 55%),
              #000;
}

/* Allow styling of injected SVG content */
.map-area :deep(#markersLayer .marker) {
  vector-effect: non-scaling-stroke;
  image-rendering: pixelated;
  transition: filter 120ms ease, transform 120ms ease, opacity 120ms ease;
  transform-origin: center;
}
.map-area :deep(#markersLayer .marker:hover) {
  filter: drop-shadow(0 0 10px rgba(0,229,255,0.35));
}

/* Coords labels */
.coord-label {
  fill: rgba(234,246,255,0.78);
  font-size: 11px;
  user-select: none;
  paint-order: stroke;
  stroke: rgba(0,0,0,0.65);
  stroke-width: 3px;
}

/* Tooltip */
.tooltip {
  position: fixed;
  pointer-events: none;
  background: rgba(8, 10, 14, 0.94);
  color: #fff;
  padding: 8px 10px;
  border-radius: 10px;
  font-size: 0.82rem;
  white-space: nowrap;
  z-index: 1000;
  border: 1px solid rgba(255, 255, 255, 0.10);
  box-shadow: 0 16px 40px rgba(0,0,0,0.55);
}

/* Empty hint */
.empty-hint {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 50px;
  display: flex;
  justify-content: center;
  pointer-events: none;
}
.empty-card {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 12px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.08);
  color: rgba(234,246,255,0.86);
}

/* Statusbar */
.statusbar {
  height: 34px;
  border-top: 1px solid rgba(255,255,255,0.06);
  background: rgba(10,12,16,0.88);
  color: rgba(234,246,255,0.80);
}
.status-left,
.status-right {
  opacity: 0.9;
}

/* Table */
.table-panel {
  display: flex;
  flex-direction: column;
}
.table-wrap {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}
.filter-input {
  flex: 1;
  min-width: 260px;
}
.colbtn {
  border-radius: 12px;
  text-transform: none;
}
.villages-table {
  flex: 1;
  min-height: 0;
  height: 100%;
}

.villages-table :deep(.q-table__middle) {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}

.villages-table :deep(.q-table__top),
.villages-table :deep(.q-table__bottom) {
  background: transparent;
}
.villages-table :deep(thead tr th) {
  position: sticky;
  top: 0;
  z-index: 2;
  background: rgba(10,12,16,0.92);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255,255,255,0.08);
  color: rgba(234,246,255,0.85);
}
.villages-table :deep(tbody tr:hover) {
  background: rgba(0,229,255,0.06);
}
.cell-strong {
  font-weight: 600;
}
.cell-sub {
  font-size: 12px;
  opacity: 0.72;
}
.tabular {
  font-variant-numeric: tabular-nums;
}
.link {
  color: #00e5ff;
  text-decoration: none;
}
.link:hover {
  text-decoration: underline;
}

/* Dialog */
.profile-card {
  min-width: 400px;
  max-width: 900px;
  width: min(900px, 92vw);
  border-radius: 14px;
}
</style>
