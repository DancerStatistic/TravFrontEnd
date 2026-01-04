<template>
  <q-list padding class="sidebar-content">
    <!-- GENERAL CONTROLS -->
    <div class="menu-section">
      <div class="section-header">
        <q-icon name="settings" class="q-mr-sm" />
        General Controls
      </div>
      <div class="section-scroll q-gutter-sm q-pa-sm">
        <q-toggle v-model="showBackgroundModel" label="Background Image" dense dark @update:model-value="$emit('update:showBackground', $event)" />
        <q-slider v-model="bgOpacityModel" :min="0" :max="1" :step="0.05" label label-always dark @update:model-value="$emit('update:bgOpacity', $event)">
          <template #label>BG Opacity: {{ bgOpacityModel.toFixed(2) }}</template>
        </q-slider>

        <q-toggle v-model="showGridModel" label="Grid" dense dark @update:model-value="$emit('update:showGrid', $event)" />
        <q-slider v-model="gridOpacityModel" :min="0" :max="1" :step="0.05" label label-always dark @update:model-value="$emit('update:gridOpacity', $event)">
          <template #label>Grid Opacity: {{ gridOpacityModel.toFixed(2) }}</template>
        </q-slider>
        <q-slider v-model="gridSizeModel" :min="0.5" :max="10" :step="0.5" label label-always dark @update:model-value="$emit('update:gridSize', $event)">
          <template #label>Grid Size: {{ gridSizeModel }}u</template>
        </q-slider>

        <q-separator spaced dark />
        <div class="row q-col-gutter-sm">
          <div class="col">
            <q-input v-model.number="gotoXModel" type="number" label="Goto X" dense outlined dark @update:model-value="$emit('update:gotoX', $event)" />
          </div>
          <div class="col">
            <q-input v-model.number="gotoYModel" type="number" label="Goto Y" dense outlined dark @update:model-value="$emit('update:gotoY', $event)" />
          </div>
        </div>
        <q-btn
          class="full-width q-mt-sm"
          color="primary"
          icon="my_location"
          label="Center on coords"
          @click="$emit('center-on-coords')"
        />
      </div>

      <div class="section-actions">
        <q-btn class="full-width" color="primary" label="Toggle All Markers" @click="$emit('toggle-all-markers')" />
      </div>
    </div>

    <!-- GROUP FILTERS - Excluding regions -->
    <div class="menu-section" v-for="grp in ['alliances','tribes']" :key="grp">
      <div class="section-header">
        <q-icon name="filter_list" class="q-mr-sm" />
        {{ capitalize(grp) }}
      </div>

      <div class="q-pa-sm">
        <q-input
          dense outlined clearable
          :model-value="groupFilters[grp]"
          :label="`Filter ${capitalize(grp)}...`"
          @update:model-value="$emit('filter-group', grp, $event)"
          dark
        >
          <template #append><q-icon name="search" /></template>
        </q-input>
        <div class="row q-col-gutter-sm q-mt-sm">
          <div class="col-4"><q-btn size="sm" color="primary" outline label="All" @click="$emit('select-group', grp, 'all')" /></div>
          <div class="col-4"><q-btn size="sm" color="primary" outline label="None" @click="$emit('select-group', grp, 'none')" /></div>
          <div class="col-4"><q-btn size="sm" color="primary" outline label="Invert" @click="$emit('select-group', grp, 'invert')" /></div>
        </div>
      </div>

      <div class="section-scroll">
        <div :ref="el => (groupRefs[grp] = el)" v-html="toggles[grp]" class="q-pa-sm" />
      </div>
    </div>

    <!-- DRAWING & MEASURE -->
    <div class="menu-section">
      <div class="section-header">
        <q-icon name="brush" class="q-mr-sm" />
        Drawing / Measure
      </div>

      <div class="section-scroll q-pa-sm q-gutter-sm">
        <q-select
          dense outlined
          :model-value="drawMode"
          :options="drawOptions"
          label="Mode"
          emit-value map-options
          dark
          @update:model-value="$emit('update:drawMode', $event)"
        />
        <div class="row q-col-gutter-sm">
          <div class="col-6">
            <q-input :model-value="drawColor" label="Color" type="color" dense outlined dark @update:model-value="$emit('update:drawColor', $event)" />
          </div>
          <div class="col-6">
            <q-slider :model-value="drawWidth" :min="1" :max="10" :step="1" label label-always dark @update:model-value="$emit('update:drawWidth', $event)" />
          </div>
        </div>
        <q-toggle :model-value="snapToGrid" label="Snap to grid" dense dark @update:model-value="$emit('update:snapToGrid', $event)" />
        <div class="row q-col-gutter-sm">
          <div class="col-6"><q-btn class="full-width" color="info" label="Undo" :disable="!canUndo" @click="$emit('undo')" /></div>
          <div class="col-6"><q-btn class="full-width" color="info" label="Redo" :disable="!canRedo" @click="$emit('redo')" /></div>
        </div>
        <div class="row q-col-gutter-sm q-mt-sm">
          <div class="col-6"><q-btn class="full-width" color="negative" label="Clear" @click="$emit('clear-drawings')" /></div>
          <div class="col-6">
            <q-btn-dropdown class="full-width" color="secondary" label="Save / Load">
              <q-list>
                <q-item clickable v-close-popup @click="$emit('export-drawings')">
                  <q-item-section>Export JSON</q-item-section>
                </q-item>
                <q-item clickable v-close-popup @click="$emit('import-drawings')">
                  <q-item-section>Import JSON</q-item-section>
                </q-item>
                <q-separator />
                <q-item clickable v-close-popup @click="$emit('save-to-local')">
                  <q-item-section>Save to LocalStorage</q-item-section>
                </q-item>
                <q-item clickable v-close-popup @click="$emit('load-from-local')">
                  <q-item-section>Load from LocalStorage</q-item-section>
                </q-item>
              </q-list>
            </q-btn-dropdown>
          </div>
        </div>
      </div>
    </div>
  </q-list>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  showBackground: { type: Boolean, default: true },
  bgOpacity: { type: Number, default: 0.6 },
  showGrid: { type: Boolean, default: true },
  gridOpacity: { type: Number, default: 0.35 },
  gridSize: { type: Number, default: 2 },
  gotoX: { type: Number, default: 0 },
  gotoY: { type: Number, default: 0 },
  groupFilters: { type: Object, default: () => ({ alliances: '', tribes: '' }) },
  toggles: { type: Object, default: () => ({ alliances: '', tribes: '' }) },
  drawMode: { type: String, default: null },
  drawOptions: { type: Array, default: () => [] },
  drawColor: { type: String, default: '#ff0000' },
  drawWidth: { type: Number, default: 2 },
  snapToGrid: { type: Boolean, default: false },
  canUndo: { type: Boolean, default: false },
  canRedo: { type: Boolean, default: false },
});

// Create local refs for v-model bindings
const showBackgroundModel = ref(props.showBackground);
const bgOpacityModel = ref(props.bgOpacity);
const showGridModel = ref(props.showGrid);
const gridOpacityModel = ref(props.gridOpacity);
const gridSizeModel = ref(props.gridSize);
const gotoXModel = ref(props.gotoX);
const gotoYModel = ref(props.gotoY);

// Watch for prop changes and update local refs
watch(() => props.showBackground, (val) => { showBackgroundModel.value = val; });
watch(() => props.bgOpacity, (val) => { bgOpacityModel.value = val; });
watch(() => props.showGrid, (val) => { showGridModel.value = val; });
watch(() => props.gridOpacity, (val) => { gridOpacityModel.value = val; });
watch(() => props.gridSize, (val) => { gridSizeModel.value = val; });
watch(() => props.gotoX, (val) => { gotoXModel.value = val; });
watch(() => props.gotoY, (val) => { gotoYModel.value = val; });

const groupRefs = { alliances: null, tribes: null };

const capitalize = (s) => s.charAt(0).toUpperCase() + s.slice(1);
</script>

<style scoped>
.panel {
  height: 100%;
  overflow: auto;
  background: #0d0d0d;
  color: #eaeaea;
}

.menu-section {
  margin-bottom: 1rem;
  border-bottom: 1px solid #1f1f1f;
}

.section-header {
  padding: 0.5rem 1rem;
  display: flex;
  align-items: center;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.05);
}

.section-scroll {
  max-height: 180px;
  overflow-y: auto;
  padding: 0 0.5rem 0.5rem 0.5rem;
}

.section-actions {
  padding: 0.5rem 1rem 1rem 1rem;
}

/* Scrollbar styling */
.section-scroll::-webkit-scrollbar {
  width: 6px;
}

.section-scroll::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
}

.section-scroll::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

.section-scroll::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}
</style>
