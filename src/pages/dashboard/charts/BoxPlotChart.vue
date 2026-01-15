<template>
    <div class="chart-fill">
        <apexchart type="boxPlot" height="100%" :options="options" :series="resolvedSeries" />
    </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
    series: { type: Array, default: () => [] }, // [{name, data:[{x, y:[min,q1,median,q3,max]}]}]
    color: { type: String, default: '' },
    colors: { type: Array, default: null }
})

const resolvedSeries = computed(() => (Array.isArray(props.series) ? props.series : []))

const options = computed(() => {
    const palette = (props.colors && props.colors.length)
        ? props.colors
        : (props.color ? [props.color] : undefined)

    return {
        chart: { toolbar: { show: false } },
        colors: palette
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
