/**
 * Application-wide state store
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Player, Alliance, Region } from '../types/api'

const AUTH_STORAGE_KEY = 'app:auth'
const EMAIL_STORAGE_KEY = 'app:userEmail'

function loadFromStorage<T>(key: string, defaultValue: T): T {
  if (typeof window === 'undefined') return defaultValue
  try {
    const stored = localStorage.getItem(key)
    return stored ? JSON.parse(stored) : defaultValue
  } catch {
    return defaultValue
  }
}

function saveToStorage(key: string, value: any) {
  if (typeof window === 'undefined') return
  try {
    localStorage.setItem(key, JSON.stringify(value))
  } catch {
    // Ignore storage errors
  }
}

export const useAppStore = defineStore('app', () => {
  // User session state - load from localStorage initially
  const isAuthenticated = ref(loadFromStorage(AUTH_STORAGE_KEY, false))
  const userEmail = ref<string | null>(loadFromStorage(EMAIL_STORAGE_KEY, null))

  // Global filters (can be shared across pages)
  const selectedRegion = ref<string | null>(null)
  const selectedAlliance = ref<string | null>(null)
  const selectedPlayer = ref<string | null>(null)

  // Cached metadata (fetched once, shared across pages)
  const regions = ref<Region[]>([])
  const alliances = ref<Alliance[]>([])
  const players = ref<Player[]>([])

  // Loading states
  const loadingRegions = ref(false)
  const loadingAlliances = ref(false)
  const loadingPlayers = ref(false)

  // Computed
  const hasFilters = computed(() => {
    return !!(selectedRegion.value || selectedAlliance.value || selectedPlayer.value)
  })

  // Actions
  function setAuthenticated(email: string | null) {
    isAuthenticated.value = !!email
    userEmail.value = email
    // Persist to localStorage
    saveToStorage(AUTH_STORAGE_KEY, isAuthenticated.value)
    saveToStorage(EMAIL_STORAGE_KEY, userEmail.value)
  }
  
  function clearAuth() {
    isAuthenticated.value = false
    userEmail.value = null
    localStorage.removeItem(AUTH_STORAGE_KEY)
    localStorage.removeItem(EMAIL_STORAGE_KEY)
  }

  function setSelectedRegion(region: string | null) {
    selectedRegion.value = region
  }

  function setSelectedAlliance(alliance: string | null) {
    selectedAlliance.value = alliance
  }

  function setSelectedPlayer(player: string | null) {
    selectedPlayer.value = player
  }

  function clearFilters() {
    selectedRegion.value = null
    selectedAlliance.value = null
    selectedPlayer.value = null
  }

  function setRegions(data: Region[]) {
    regions.value = data
  }

  function setAlliances(data: Alliance[]) {
    alliances.value = data
  }

  function setPlayers(data: Player[]) {
    players.value = data
  }

  return {
    // State
    isAuthenticated,
    userEmail,
    selectedRegion,
    selectedAlliance,
    selectedPlayer,
    regions,
    alliances,
    players,
    loadingRegions,
    loadingAlliances,
    loadingPlayers,
    // Computed
    hasFilters,
    // Actions
    setAuthenticated,
    clearAuth,
    setSelectedRegion,
    setSelectedAlliance,
    setSelectedPlayer,
    clearFilters,
    setRegions,
    setAlliances,
    setPlayers
  }
})
