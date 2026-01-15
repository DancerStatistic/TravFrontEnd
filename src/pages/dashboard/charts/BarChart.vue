<template>
    <div class="chart-fill">
        <apexchart type="bar" height="100%" :options="options" :series="resolvedSeries" />
    </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
    categories: { type: Array, default: () => [] },
    series: { type: Array, default: () => [] },
    horizontal: { type: Boolean, default: true },
    color: { type: String, default: '' },
    colors: { type: Array, default: null }
})

const resolvedSeries = computed(() =>
    (Array.isArray(props.series) && props.series.length ? props.series : [{ name: 'Value', data: [] }])
)

const options = computed(() => {
    const palette = (props.colors && props.colors.length) ? props.colors : (props.color ? [props.color] : undefined)
    return {
        chart: { toolbar: { show: false }, animations: { enabled: true } },
        colors: palette,
        plotOptions: { bar: { horizontal: !!props.horizontal, borderRadius: 4 } },
        dataLabels: { enabled: false },
        xaxis: { categories: props.categories ?? [] }
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
