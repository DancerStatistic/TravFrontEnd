<template>
    <div class="chart-fill">
        <!-- mixed series works with type="line" chart, Apex decides per-series type -->
        <apexchart type="line" height="100%" :options="options" :series="resolvedSeries" />
    </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
    categories: { type: Array, default: () => [] },
    series: { type: Array, default: () => [] }, // [{name,type:'column'|'line',data:[...]}]
    color: { type: String, default: '' },
    colors: { type: Array, default: null }
})

const resolvedSeries = computed(() => (Array.isArray(props.series) ? props.series : []))

const options = computed(() => {
    const palette = (props.colors && props.colors.length)
        ? props.colors
        : (props.color ? [props.color] : undefined)

    // Build a stroke width array that matches series count (columns get 0, lines get 3)
    const strokeWidths = resolvedSeries.value.map(s => (s?.type === 'column' ? 0 : 3))

    return {
        chart: { toolbar: { show: false } },
        colors: palette,
        stroke: { width: strokeWidths.length ? strokeWidths : [3] },
        dataLabels: { enabled: false },
        xaxis: { categories: props.categories || [] },
        plotOptions: { bar: { borderRadius: 4 } }
    }
})
</script>

<style scoped>
.chart-fill {
    height: 100%;
    width: 100%;
    min-height: 0;
}

.chart-fill :deep(.apexcharts-canvas),
.chart-fill :deep(svg) {
    height: 100% !important;
    width: 100% !important;
}
</style>
