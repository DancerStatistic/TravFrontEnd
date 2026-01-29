/**
 * Application-wide state store
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Player, Alliance, Region } from '../types/api'

export const useAppStore = defineStore('app', () => {
  // User session state
  const isAuthenticated = ref(false)
  const userEmail = ref<string | null>(null)

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
    setSelectedRegion,
    setSelectedAlliance,
    setSelectedPlayer,
    clearFilters,
    setRegions,
    setAlliances,
    setPlayers
  }
})
