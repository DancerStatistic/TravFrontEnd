<template>
    <div class="chart-fill">
        <apexchart type="radialBar" height="100%" :options="options" :series="resolvedSeries" />
    </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
    series: { type: Array, default: () => [] }, // [number] or [n1,n2]
    labels: { type: Array, default: () => [] },
    color: { type: String, default: '' },
    colors: { type: Array, default: null }
})

const resolvedSeries = computed(() => (Array.isArray(props.series) ? props.series : []))

const options = computed(() => {
    const palette = (props.colors && props.colors.length) ? props.colors : null

    return {
        chart: { toolbar: { show: false } },
        labels: props.labels || [],
        ...(palette ? { colors: palette } : {}),
        ...(!palette && props.color ? { theme: { monochrome: { enabled: true, color: props.color } } } : {}),
        plotOptions: {
            radialBar: {
                dataLabels: {
                    name: { show: true },
                    value: { show: true }
                }
            }
        }
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
