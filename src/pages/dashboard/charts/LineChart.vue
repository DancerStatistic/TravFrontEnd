<template>
    <div class="chart-fill">
        <apexchart type="line" height="100%" :options="options" :series="series" />
    </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
    data: { type: Array, default: () => [] },
    color: { type: String, default: '' },
    colors: { type: Array, default: null }
})

const categories = computed(() =>
    props.data.map((x, i) => (typeof x === 'number' ? `#${i + 1}` : (x.label ?? `#${i + 1}`)))
)

const values = computed(() => props.data.map((x) => (typeof x === 'number' ? x : x.value)))
const series = computed(() => [{ name: 'Value', data: values.value }])

const options = computed(() => {
    const palette = (props.colors && props.colors.length) ? props.colors : (props.color ? [props.color] : undefined)
    return {
        chart: { toolbar: { show: false }, animations: { enabled: true } },
        colors: palette,
        stroke: { curve: 'smooth', width: 3 },
        dataLabels: { enabled: false },
        xaxis: { categories: categories.value },
        yaxis: { decimalsInFloat: 0 }
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
