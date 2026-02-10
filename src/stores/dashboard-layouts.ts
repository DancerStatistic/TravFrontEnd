import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const STORAGE_KEY = 'dashboard:layouts:v1'
const ACTIVE_KEY = 'dashboard:activeLayout:v1'

export interface DashboardLayout {
  id: string
  name: string
  widgets: unknown[]
  updatedAt: number
}

function loadFromStorage(): DashboardLayout[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

function saveToStorage(layouts: DashboardLayout[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(layouts))
}

function loadActiveId(): string | null {
  return localStorage.getItem(ACTIVE_KEY)
}

function saveActiveId(id: string | null) {
  if (id) localStorage.setItem(ACTIVE_KEY, id)
  else localStorage.removeItem(ACTIVE_KEY)
}

export const useDashboardLayoutsStore = defineStore('dashboard-layouts', () => {
  const layouts = ref<DashboardLayout[]>(loadFromStorage())
  const activeLayoutId = ref<string | null>(loadActiveId())

  const layoutsList = computed(() =>
    [...layouts.value].sort((a, b) => b.updatedAt - a.updatedAt)
  )

  function saveLayout(name: string, widgets: unknown[]) {
    const trimmed = name.trim()
    if (!trimmed) return null

    const existing = layouts.value.find((l) => l.name.toLowerCase() === trimmed.toLowerCase())
    const now = Date.now()

    if (existing) {
      existing.widgets = JSON.parse(JSON.stringify(widgets))
      existing.updatedAt = now
      saveToStorage(layouts.value)
      activeLayoutId.value = existing.id
      saveActiveId(existing.id)
      return existing.id
    }

    const id = `layout-${now}-${Math.random().toString(36).slice(2, 9)}`
    const layout: DashboardLayout = {
      id,
      name: trimmed,
      widgets: JSON.parse(JSON.stringify(widgets)),
      updatedAt: now
    }
    layouts.value = [...layouts.value, layout]
    saveToStorage(layouts.value)
    activeLayoutId.value = id
    saveActiveId(id)
    return id
  }

  function loadLayout(id: string): unknown[] | null {
    const layout = layouts.value.find((l) => l.id === id)
    if (!layout) return null
    activeLayoutId.value = id
    saveActiveId(id)
    return JSON.parse(JSON.stringify(layout.widgets))
  }

  function deleteLayout(id: string) {
    layouts.value = layouts.value.filter((l) => l.id !== id)
    saveToStorage(layouts.value)
    if (activeLayoutId.value === id) {
      activeLayoutId.value = layouts.value[0]?.id ?? null
      saveActiveId(activeLayoutId.value)
    }
  }

  function getLayout(id: string): DashboardLayout | undefined {
    return layouts.value.find((l) => l.id === id)
  }

  function setActiveLayout(id: string | null) {
    activeLayoutId.value = id
    saveActiveId(id)
  }

  return {
    layouts: layoutsList,
    activeLayoutId: computed(() => activeLayoutId.value),
    saveLayout,
    loadLayout,
    deleteLayout,
    getLayout,
    setActiveLayout
  }
})
