<template>
  <q-page padding class="column">
    <q-toolbar class="bg-primary text-white">
      <q-toolbar-title>Alliances</q-toolbar-title>
    </q-toolbar>

    <div class="q-pa-md">
      <q-table
        :columns="columns"
        :rows="filteredRows"
        row-key="alliance"
        flat bordered separator="cell"
        :loading="loading"
        :pagination.sync="pagination"
        :rows-per-page-options="[20, 50, 100]"
        @row-click="goToDetail"
      >
        <template v-slot:no-data>
          <q-spinner-dots size="2em" color="primary"/>
          <div class="text-center q-mt-md">No alliances found.</div>
        </template>
      </q-table>
    </div>
  </q-page>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from 'boot/axios'

const CACHE_KEY   = 'alliancesCache'
const CACHE_TTL   = 1000 * 60 * 60 * 24  // 24h

const router     = useRouter()
const loading    = ref(false)
const rows       = ref([])
const pagination = ref({ page: 1, rowsPerPage: 20 })

const columns = [
  { name: 'alliance',   label: 'Alliance',   field: 'alliance',   sortable: true },
  { name: 'players',    label: '# Players',  field: 'players',    sortable: true, align: 'right' },
  { name: 'population', label: 'Population', field: 'population', sortable: true, align: 'right' },
  { name: 'topRegion',  label: 'Top Region', field: 'topRegion',  sortable: true }
]

const filters = reactive({
  alliance: '',
  players: '',
  population: '',
  topRegion: ''
})

function goToDetail(evt, row) {
  router.push({ name: 'alliance-detail', params: { tag: row.alliance } })
}

function loadFromCache() {
  try {
    const raw = localStorage.getItem(CACHE_KEY)
    if (!raw) return null
    const { ts, data } = JSON.parse(raw)
    if ((Date.now() - ts) < CACHE_TTL) {
      return data
    }
  }
  catch {}
  return null
}

function saveToCache(data) {
  localStorage.setItem(CACHE_KEY, JSON.stringify({ ts: Date.now(), data }))
}

async function loadAlliances() {
  const cached = loadFromCache()
  if (cached) {
    rows.value = cached
    return
  }

  loading.value = true
  try {
    // 1) fetch all alliance tags directly
    const { data: tags } = await api.get('/api/alliance')
    
    // Validate response
    if (!Array.isArray(tags)) {
      console.error('Expected array of tags, got:', tags)
      return
    }
    
    if (tags.length === 0) {
      console.warn('No alliance tags found')
      rows.value = []
      return
    }

    // 2) for each tag, fetch its villages & compute stats
    const statsPromises = tags.map(async tag => {
      try {
        const { data } = await api.get(
          `/api/alliance/${encodeURIComponent(tag)}/villages`
        )
        
        if (!data || !data.villages) {
          console.error(`No villages data for alliance ${tag}:`, data)
          return {
            alliance: tag,
            players: 0,
            population: 0,
            topRegion: ''
          }
        }
        
        const vs = data.villages

        // count unique players
        const playerSet = new Set(vs.map(v => v.player_name || v.player || '').filter(Boolean))
        const totalPop  = vs.reduce((sum, v) => sum + (Number(v.population)||0), 0)

        // find top region by population
        const regionTotals = {}
        vs.forEach(v => {
          const region = v.region || ''
          if (region) {
            regionTotals[region] = (regionTotals[region]||0) + (Number(v.population)||0)
          }
        })
        let topR = '', topVal = -1
        Object.entries(regionTotals).forEach(([r,val]) => {
          if (val > topVal) {
            topVal = val
            topR   = r
          }
        })

        return {
          alliance:   tag,
          players:    playerSet.size,
          population: totalPop,
          topRegion:  topR
        }
      } catch (err) {
        console.error(`Error fetching villages for alliance ${tag}:`, err)
        return {
          alliance: tag,
          players: 0,
          population: 0,
          topRegion: ''
        }
      }
    })

    const result = await Promise.all(statsPromises)
    rows.value = result.filter(r => r) // Filter out any null/undefined results
    saveToCache(result)
  } catch (err) {
    console.error('Error loading alliances:', err)
    rows.value = []
  } finally {
    loading.value = false
  }
}

const filteredRows = computed(() => {
  return rows.value.filter(r =>
    Object.entries(filters).every(([k, v]) => {
      if (!v) return true
      return String(r[k]).toLowerCase().includes(v.toLowerCase())
    })
  )
})

onMounted(loadAlliances)
</script>

<style scoped>
.q-table__container {
  max-height: calc(100vh - var(--q-header-height) - 64px);
}
</style>
