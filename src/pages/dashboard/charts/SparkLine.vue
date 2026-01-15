<template>
    <div class="chart-fill">
        <apexchart type="line" height="100%" :options="options" :series="resolvedSeries" />
    </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
    series: { type: Array, default: () => [] },
    color: { type: String, default: '' },
    colors: { type: Array, default: null }
})

const resolvedSeries = computed(() => (Array.isArray(props.series) && props.series.length ? props.series : [{ data: [] }]))

const options = computed(() => {
    const palette = (props.colors && props.colors.length) ? props.colors : null
    return {
        chart: { sparkline: { enabled: true }, toolbar: { show: false }, animations: { enabled: true } },
        ...(palette ? { colors: palette } : {}),
        ...(!palette && props.color ? { theme: { monochrome: { enabled: true, color: props.color } } } : {}),
        stroke: { width: 2 },
        dataLabels: { enabled: false }
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
