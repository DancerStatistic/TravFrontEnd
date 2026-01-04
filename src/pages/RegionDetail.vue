<!-- RegionDetail.vue -->
<template>
  <q-page padding class="column region-detail-page">

    <!-- Toolbar -->
    <q-toolbar class="bg-primary text-white">
      <q-btn dense flat round icon="arrow_back" @click="$router.back()" />
      <q-toolbar-title>Region: {{ regionName }}</q-toolbar-title>
      <q-btn dense flat round icon="open_in_new"
             :href="`https://nys.x1.europe.travian.com/karte.php?region=${encodeURIComponent(regionName)}`"
             target="_blank"
      />
    </q-toolbar>

    <!-- Region-only Map -->
    <div class="map-area">
      <svg
        ref="svg"
        :viewBox="regionViewBox"
        preserveAspectRatio="xMidYMid meet"
        @mousemove="onMouseMove"
        @mouseleave="hideTooltip"
      >
        <!-- Background PNG -->
        <image
          x="-200" y="-200" width="400" height="400"
          href="/background.png"
          preserveAspectRatio="xMidYMid slice"
        />

        <!-- Grid -->
        <defs>
          <pattern id="grid" width="1" height="1" patternUnits="userSpaceOnUse">
            <path d="M1 0 L0 0 L0 1" stroke="gray" stroke-width="0.05" fill="none"/>
          </pattern>
        </defs>
        <rect x="-200" y="-200" width="400" height="400" fill="url(#grid)" />

        <!-- Axes -->
        <line x1="-200" y1="0" x2="200" y2="0" stroke="black" stroke-width="0.1"/>
        <line x1="0" y1="-200" x2="0" y2="200" stroke="black" stroke-width="0.1"/>

        <!-- Villages -->
        <g id="mapContent">
          <circle
            v-for="m in markers"
            :key="m.id"
            :cx="m.x" :cy="m.y"
            r="0.6"
            :fill="m.color"
            stroke="black"
            stroke-width="0.05"
            style="cursor:pointer"
            @mouseover="showTooltip($event, m.tooltip)"
            @mouseout="hideTooltip"
            @click="openProfile(m.player)"
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

    <!-- Villages Table -->
    <div class="table-area q-pa-md">
      <q-table
        :columns="columns"
        :rows="villages"
        row-key="coords"
        flat bordered separator="cell"
        :pagination.sync="pagination"
        :rows-per-page-options="[10, 20, 50]"
      >
        <template #body-cell-coords="props">
          <q-td :props="props">
            <a
              :href="makeMapLink(props.row.coords)"
              target="_blank"
              rel="noopener"
            >{{ props.row.coords }}</a>
          </q-td>
        </template>
      </q-table>
    </div>

    <!-- Player Profile Dialog -->
    <q-dialog v-model="profileDialog">
      <q-card style="min-width:400px; max-width:600px">
        <q-card-section class="row items-center">
          <div class="text-h6">Player: {{ profile.name }}</div>
          <q-space/>
          <q-btn icon="close" flat round dense @click="profileDialog = false"/>
        </q-card-section>
        <q-separator/>
        <q-card-section v-if="profile.villages.length">
          <q-table
            :columns="profileColumns"
            :rows="profile.villages"
            row-key="coords"
            flat dense wrap-cells
          />
        </q-card-section>
        <q-card-section v-else class="text-grey">
          No villages found for this player.
        </q-card-section>
        <q-card-actions align="right">
          <div class="text-subtitle2">
            Total population: {{ profile.totalPopulation }}
          </div>
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { api } from 'boot/axios'
import * as d3 from 'd3'

// route & reactive state
const route      = useRoute()
const regionName = route.params.name
const villages   = ref([])
const markers    = ref([])
const pagination = ref({ page: 1, rowsPerPage: 10 })

// table columns
const columns = [
  { name: 'village',       label: 'Village',    field: 'village' },
  { name: 'coords',        label: 'Coords',     field: 'coords'  },
  { name: 'population',    label: 'Population', field: 'population', align:'right' },
  { name: 'victoryPoints', label: 'VP',         field: 'victoryPoints', align:'right' },
  { name: 'alliance',      label: 'Alliance',   field: 'alliance' },
  { name: 'tribe',         label: 'Tribe',      field: 'tribe'    }
]

// tooltip state
const tooltip = ref({ show:false, x:0, y:0, content:'' })
function showTooltip(evt, html){
  tooltip.value = {
    show: true,
    x:    evt.clientX + 8,
    y:    evt.clientY + 8,
    content: html
  }
}
function hideTooltip(){ tooltip.value.show = false }
function onMouseMove(){}  // no‐op

// map link helper
function makeMapLink(coords){
  const m = coords.match(/\((-?\d+),\s*(-?\d+)\)/)
  return m
    ? `https://nys.x1.europe.travian.com/karte.php?x=${m[1]}&y=${m[2]}`
    : '#'
}

// player profile popup
const profileDialog = ref(false)
const profile       = ref({ name:'', villages:[], totalPopulation:0 })
const profileColumns = [
  { name:'village',       label:'Village',    field:'village' },
  { name:'coords',        label:'Coords',     field:'coords' },
  { name:'population',    label:'Population', field:'population', align:'right' },
  { name:'victoryPoints', label:'VP',         field:'victoryPoints', align:'right' }
]
async function openProfile(owner){
  try {
    const { data } = await api.get(`/api/player/${encodeURIComponent(owner)}/villages`)
    profile.value.name            = data.player
    profile.value.villages        = data.villages
    profile.value.totalPopulation = data.villages.reduce((s,v)=>s+(v.population||0),0)
  } catch {
    profile.value = { name: owner, villages: [], totalPopulation:0 }
  }
  profileDialog.value = true
}

// compute dynamic viewBox to zoom into region
const regionViewBox = computed(() => {
  if (!markers.value.length) return '-200 -200 400 400'
  const xs = markers.value.map(m=>m.x)
  const ys = markers.value.map(m=>m.y)
  const minX = Math.min(...xs), maxX = Math.max(...xs)
  const minY = Math.min(...ys), maxY = Math.max(...ys)
  const pad = 5
  const w = (maxX - minX) + pad*2
  const h = (maxY - minY) + pad*2
  return `${minX - pad} ${minY - pad} ${w} ${h}`
})

// setup map & data on mount
const svg = ref(null)
onMounted(async () => {
  // fetch region villages
  const { data } = await api.get(`/api/region/${encodeURIComponent(regionName)}/villages`)
  villages.value = data.villages

  // assign each player a distinct HSL color
  const players = [...new Set(data.villages.map(v=>v.player))]
  const colorMap = {}
  players.forEach((p,i) => {
    colorMap[p] = `hsl(${(i*137)%360},70%,50%)`
  })

  // build marker array
  markers.value = data.villages.map(v => {
    const m = v.coords.match(/\((-?\d+),\s*(-?\d+)\)/)
    const x = +m[1], y = -m[2]
    return {
      id:      `${v.village}-${x}-${y}`,
      x, y,
      tooltip: `Village: ${v.village}<br>Population: ${v.population}<br>Alliance: ${v.alliance}`,
      player:  v.player,
      color:   colorMap[v.player]||'gray'
    }
  })

  // D3 zoom on your region map
  const sel = d3.select(svg.value)
  const g   = d3.select('#mapContent')
  sel.call(
    d3.zoom()
      .scaleExtent([1,20])
      .on('zoom', ({transform}) => g.attr('transform', transform))
  )
})
</script>

<style scoped>
.region-detail-page {
  min-height: calc(100vh - var(--q-header-height));
  padding: 0;
}
.map-area {
  position: relative;
  height: 300px;
  border-bottom: 1px solid #e0e0e0;
  width: 100%;
}
.map-area svg {
  width: 100%;
  height: 100%;
}
.table-area {
  flex: 1;
}
.tooltip {
  position: fixed;
  pointer-events: none;
  background: rgba(0,0,0,0.8);
  color: #fff;
  padding: 6px 8px;
  border-radius: 4px;
  font-size: .8rem;
  white-space: nowrap;
  z-index: 1000;
}
</style>
