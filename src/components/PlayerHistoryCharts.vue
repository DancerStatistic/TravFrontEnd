<template>
  <div class="player-history-charts">
    <q-card flat>
      <q-tabs
        v-model="activeTab"
        dense
        class="text-grey"
        active-color="primary"
        indicator-color="primary"
        align="justify"
      >
        <q-tab name="population" label="Population" />
        <q-tab name="villages" label="Villages" />
        <q-tab name="growth" label="Growth" />
        <q-tab name="ranks" label="Rank" />
        <q-tab name="tribes" label="Tribes" />
      </q-tabs>

      <q-separator />

      <q-tab-panels v-model="activeTab" animated class="chart-tab-panels">
        <!-- Population Over Time -->
        <q-tab-panel name="population" class="q-pa-sm">
          <div class="chart-container">
            <apexchart
              type="area"
              height="350"
              :options="populationChartOptions"
              :series="populationSeries"
            />
          </div>
        </q-tab-panel>

        <!-- Villages Over Time -->
        <q-tab-panel name="villages" class="q-pa-sm">
          <div class="chart-container">
            <apexchart
              type="line"
              height="350"
              :options="villageChartOptions"
              :series="villageSeries"
            />
          </div>
        </q-tab-panel>

        <!-- Growth Rates -->
        <q-tab-panel name="growth" class="q-pa-sm">
          <div class="chart-container">
            <apexchart
              type="bar"
              height="350"
              :options="growthChartOptions"
              :series="growthSeries"
            />
          </div>
        </q-tab-panel>

        <!-- Rank History -->
        <q-tab-panel name="ranks" class="q-pa-sm">
          <div class="chart-container">
            <apexchart
              type="line"
              height="350"
              :options="rankChartOptions"
              :series="rankSeries"
            />
          </div>
        </q-tab-panel>

        <!-- Tribe Distribution Over Time -->
        <q-tab-panel name="tribes" class="q-pa-sm">
          <div class="chart-container">
            <apexchart
              type="line"
              height="350"
              :options="tribeChartOptions"
              :series="tribeSeries"
            />
          </div>
        </q-tab-panel>
      </q-tab-panels>
    </q-card>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { Notify } from 'quasar'
import { api } from 'boot/axios'
import VueApexCharts from 'vue3-apexcharts'
export default {
  name: 'PlayerHistoryCharts',
  components: {
     apexchart: VueApexCharts
   },
  props: {
    playerName: {
      type: String,
      required: true
    },
    historyData: {
      type: Array,
      default: () => []
    }
  },
  setup(props) {
    const $q = useQuasar()
    const activeTab = ref('population')
    const loading = ref(true)
    const history = ref([])

    // Fetch history data if not provided
    onMounted(async () => {
      if (props.historyData.length === 0) {
        try {
          loading.value = true
          const response = await api.get(`/api/player/${encodeURIComponent(props.playerName)}/history`)
          const payload = response.data?.data ?? response.data
          history.value = payload?.history || []
          playerHistory.value = history;
        } catch (error) {
          console.error('Error fetching player history:', error)
          Notify.create({
            type: 'negative',
            message: 'Failed to load player history'
          })
        } finally {
          loading.value = false
        }
      } else {
        history.value = props.historyData
        loading.value = false
      }
    })

    // Watch for prop changes
    watch(() => props.historyData, (newVal) => {
      if (newVal && newVal.length > 0) {
        history.value = newVal
      }
    })

    // Chart data computed properties
    const chartDates = computed(() => {
      return history.value.map(item => item.date)
    })

    // Population Chart
    const populationSeries = computed(() => [{
      name: 'Population',
      data: history.value.map(item => item.population)
    }])

    const populationChartOptions = computed(() => ({
      chart: {
        id: 'population-chart',
        type: 'area',
        height: '100%',
        zoom: { enabled: true },
        toolbar: { show: true },
        animations: { enabled: true }
      },
      dataLabels: { enabled: false },
      stroke: { curve: 'smooth' },
      xaxis: { categories: chartDates.value },
      yaxis: {
        title: { text: 'Population' },
        labels: {
          formatter: (val) => val.toLocaleString()
        }
      },
      tooltip: {
        y: {
          formatter: (val) => val.toLocaleString()
        }
      },
      colors: ['#1976D2'],
      fill: {
        type: 'gradient',
        gradient: {
          shadeIntensity: 1,
          opacityFrom: 0.7,
          opacityTo: 0.2,
        }
      }
    }))

    // Villages Chart
    const villageSeries = computed(() => [{
      name: 'Villages',
      data: history.value.map(item => item.villages)
    }])

    const villageChartOptions = computed(() => ({
      chart: {
        id: 'village-chart',
        type: 'line',
        height: '100%',
        zoom: { enabled: true },
        toolbar: { show: true }
      },
      dataLabels: { enabled: false },
      stroke: { curve: 'smooth' },
      xaxis: { categories: chartDates.value },
      yaxis: { title: { text: 'Villages' } },
      colors: ['#26A69A'],
      markers: { size: 4 }
    }))

    // Growth Chart
    const growthSeries = computed(() => [
      {
        name: 'Population Growth',
        data: history.value.map(item => item.pop_growth || 0)
      },
      {
        name: 'Village Growth',
        data: history.value.map(item => item.village_growth || 0)
      }
    ])

    const growthChartOptions = computed(() => ({
      chart: {
        id: 'growth-chart',
        type: 'bar',
        height: '100%',
        stacked: false,
        toolbar: { show: true }
      },
      plotOptions: {
        bar: {
          horizontal: false,
          columnWidth: '50%',
          endingShape: 'rounded'
        },
      },
      dataLabels: { enabled: false },
      stroke: { show: true, width: 2 },
      xaxis: { categories: chartDates.value },
      yaxis: { title: { text: 'Daily Growth' } },
      colors: ['#FFA726', '#66BB6A'],
      fill: { opacity: 1 }
    }))

    // Rank Chart
    const rankSeries = computed(() => [{
      name: 'Rank',
      data: history.value
        .filter(item => item.rank != null)
        .map(item => item.rank)
    }])

    const rankChartOptions = computed(() => {
      const rankData = history.value
        .filter(item => item.rank != null)
        .map(item => item.rank)
      
      return {
        chart: {
          id: 'rank-chart',
          type: 'line',
          height: '100%',
          zoom: { enabled: true },
          toolbar: { show: true }
        },
        dataLabels: { enabled: true },
        stroke: { curve: 'smooth' },
        xaxis: { 
          categories: chartDates.value.filter((_, i) => 
            history.value[i].rank != null
          )
        },
        yaxis: { 
          title: { text: 'Rank' },
          reversed: true,
          min: Math.max(1, Math.min(...rankData) - 10),
          max: Math.max(1, Math.max(...rankData) + 10)
        },
        colors: ['#EC407A'],
        markers: { size: 4 }
      }
    })

    // Tribe Distribution Chart
    const tribeSeries = computed(() => {
      // Get all unique tribes across all dates
      const allTribes = new Set()
      history.value.forEach(entry => {
        Object.keys(entry.tribes || {}).forEach(tribe => {
          allTribes.add(tribe)
        })
      })

      // Create series for each tribe
      return Array.from(allTribes).map(tribe => ({
        name: tribe || 'Unknown',
        data: history.value.map(entry => entry.tribes?.[tribe] || 0)
      }))
    })

    const tribeChartOptions = computed(() => ({
      chart: {
        id: 'tribe-chart',
        type: 'line',
        height: '100%',
        stacked: true,
        zoom: { enabled: true },
        toolbar: { show: true }
      },
      dataLabels: { enabled: false },
      stroke: { curve: 'smooth' },
      xaxis: { categories: chartDates.value },
      yaxis: { title: { text: 'Villages' } },
      colors: ['#8D6E63', '#5C6BC0', '#42A5F5', '#26A69A', '#66BB6A', '#FFEE58', '#FFA726', '#EF5350'],
      fill: { opacity: 1 }
    }))

    return {
      activeTab,
      loading,
      populationSeries,
      populationChartOptions,
      villageSeries,
      villageChartOptions,
      growthSeries,
      growthChartOptions,
      rankSeries,
      rankChartOptions,
      tribeSeries,
      tribeChartOptions
    }
  }
}
</script>

<style scoped>
.player-history-charts {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chart-tab-panels {
  flex: 1;
}

.chart-container {
  width: 100%;
}
</style>
