<!-- src/pages/charts/RangeAreaChart.vue
FULL FIX: eliminates recursive updates by:
- never mutating props
- never "watch props -> set reactive options object -> causes apex to emit -> triggers watch again"
- using shallowRef + controlled watchers with string keys
- using markRaw for options (Apex mutates its options internally)
Also includes tooltip stability settings to stop the left/right “bounce”.
-->
<template>
    <div class="ra-wrap">
      <apexchart
        class="ra-chart"
        type="rangeArea"
        height="100%"
        :options="options"
        :series="seriesRef"
      />
    </div>
  </template>
  
  <script setup>
  import { computed, shallowRef, watch, markRaw } from 'vue'
  import ApexChart from 'vue3-apexcharts'
  
  const apexchart = ApexChart
  
  const props = defineProps({
    // Expected:
    // [
    //   { name: 'Min/Max', data: [ { x: '2026-01-01', y: [min, max] }, ... ] }
    // ]
    series: { type: Array, default: () => [] },
  
    // Optional cosmetics
    color: { type: String, default: '#3f51b5' },
    colors: { type: Array, default: null },
  
    // Optional axes labels
    xTitle: { type: String, default: '' },
    yTitle: { type: String, default: '' }
  })
  
  /**
   * ApexCharts internally mutates the options object.
   * If Vue treats options as reactive and Apex mutates it, Vue can re-render,
   * which can cause Apex to update again -> recursion.
   * Fix: keep options in a shallowRef and markRaw() the object.
   */
  const optionsRef = shallowRef(markRaw({}))
  const seriesRef = shallowRef([])
  
  /* ---------- Helpers ---------- */
  function safeNum (v) {
    const n = Number(v)
    return Number.isFinite(n) ? n : 0
  }
  
  function normalizeSeries (incoming) {
    const src = Array.isArray(incoming) ? incoming : []
    return src.map((s) => ({
      name: String(s?.name ?? 'Series'),
      data: (Array.isArray(s?.data) ? s.data : []).map((pt) => ({
        x: String(pt?.x ?? ''),
        y: Array.isArray(pt?.y) ? [safeNum(pt.y[0]), safeNum(pt.y[1])] : [0, 0]
      }))
    }))
  }
  
  function buildOptions () {
    const palette =
      Array.isArray(props.colors) && props.colors.length
        ? props.colors
        : [props.color || '#3f51b5']
  
    return markRaw({
      chart: {
        type: 'rangeArea',
        height: '100%',
        animations: { enabled: false }, // helps prevent hover jitter + feedback loops
        toolbar: { show: false },
        zoom: { enabled: false },
        foreColor: undefined
      },
  
      colors: palette,
  
      dataLabels: { enabled: false },
  
      stroke: {
        curve: 'smooth',
        width: 2
      },
  
      fill: {
        type: 'solid',
        opacity: 0.25
      },
  
      markers: { size: 0 },
  
      xaxis: {
        type: 'category',
        title: props.xTitle ? { text: props.xTitle } : undefined,
        labels: { rotate: -30, hideOverlappingLabels: true, trim: true }
      },
  
      yaxis: {
        title: props.yTitle ? { text: props.yTitle } : undefined,
        decimalsInFloat: 0
      },
  
      grid: {
        strokeDashArray: 4
      },
  
      tooltip: {
        // The “bounce left/right” typically comes from tooltip transform transitions or resizing.
        // These settings reduce layout thrash.
        followCursor: false,
        fixed: { enabled: false },
        intersect: false,
        shared: false
      },
  
      legend: { show: true },
  
      noData: { text: 'No data' }
    })
  }
  
  /* ---------- Stable update keys (prevents reactive recursion) ---------- */
  const seriesKey = computed(() => {
    // string key: only changes when the meaningful content changes
    try {
      return JSON.stringify(props.series || [])
    } catch {
      return String(Date.now())
    }
  })
  
  const paletteKey = computed(() => {
    const pal = (Array.isArray(props.colors) && props.colors.length ? props.colors : [props.color]).filter(Boolean)
    return pal.join('|')
  })
  
  const axisKey = computed(() => `${props.xTitle || ''}__${props.yTitle || ''}`)
  
  /* ---------- Watchers (controlled, no self-triggering) ---------- */
  watch(
    seriesKey,
    () => {
      seriesRef.value = normalizeSeries(props.series)
    },
    { immediate: true }
  )
  
  watch(
    [paletteKey, axisKey],
    () => {
      optionsRef.value = buildOptions()
    },
    { immediate: true }
  )
  
  const options = computed(() => optionsRef.value)
  </script>
  
  <style scoped>
  .ra-wrap {
    height: 100%;
    min-height: 0;
    position: relative;
  }
  
  /* Let tooltip escape without getting clipped */
  .ra-wrap :deep(.apexcharts-canvas),
  .ra-wrap :deep(.apexcharts-inner),
  .ra-wrap :deep(.apexcharts-graphical),
  .ra-wrap :deep(.apexcharts-svg) {
    overflow: visible !important;
  }
  
  /* Remove tooltip transitions that can look like bouncing */
  .ra-wrap :deep(.apexcharts-tooltip),
  .ra-wrap :deep(.apexcharts-xaxistooltip) {
    transition: none !important;
  }
  
  /* Ensure the chart fills the card */
  .ra-chart {
    height: 100%;
    width: 100%;
  }
  </style>
  