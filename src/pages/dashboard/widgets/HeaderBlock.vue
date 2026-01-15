<!-- widgets/TextBlock.vue -->
<template>
    <div class="textBlock">
        <q-input v-if="edit" :model-value="text" type="textarea" autogrow dense outlined placeholder="Write something…"
            @update:model-value="onUpdateText" />

        <div v-else class="textBlock__read">
            <div v-if="text" class="q-pa-xs">
                {{ text }}
            </div>
            <div v-else class="text-grey-6 q-pa-xs">
                No text
            </div>
        </div>
    </div>
</template>

<script setup>
defineProps({
    edit: {
        type: Boolean,
        default: false
    },
    text: {
        type: String,
        default: ''
    },
    onUpdateText: {
        type: Function,
        required: true
    }
})
</script>

<style scoped>
.textBlock {
    height: 100%;
    width: 100%;
}

.textBlock__read {
    white-space: pre-wrap;
    word-break: break-word;
}
</style>
