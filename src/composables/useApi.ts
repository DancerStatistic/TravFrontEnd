/**
 * Composable for API calls with error handling and loading state.
 */
import { ref } from 'vue'
import { api } from 'boot/axios'
import type { AxiosResponse } from 'axios'

export interface ApiError {
  message: string
  status?: number
  data?: unknown
}

/**
 * Composable for making API calls with loading and error state
 */
export function useApi() {
  const loading = ref(false)
  const error = ref<ApiError | null>(null)

  /**
   * Make a GET request
   */
  async function get<T = unknown>(url: string, config?: unknown): Promise<T> {
    loading.value = true
    error.value = null
    try {
      const response: AxiosResponse<T> = await api.get(url, config)
      return response.data
    } catch (err: unknown) {
      const axiosError = err as { response?: { status: number; data: unknown }; message: string }
      error.value = {
        message: axiosError.message || 'An error occurred',
        status: axiosError.response?.status,
        data: axiosError.response?.data
      }
      throw error.value
    } finally {
      loading.value = false
    }
  }

  /**
   * Make a POST request
   */
  async function post<T = unknown>(url: string, data?: unknown, config?: unknown): Promise<T> {
    loading.value = true
    error.value = null
    try {
      const response: AxiosResponse<T> = await api.post(url, data, config)
      return response.data
    } catch (err: unknown) {
      const axiosError = err as { response?: { status: number; data: unknown }; message: string }
      error.value = {
        message: axiosError.message || 'An error occurred',
        status: axiosError.response?.status,
        data: axiosError.response?.data
      }
      throw error.value
    } finally {
      loading.value = false
    }
  }

  /**
   * Make a PUT request
   */
  async function put<T = unknown>(url: string, data?: unknown, config?: unknown): Promise<T> {
    loading.value = true
    error.value = null
    try {
      const response: AxiosResponse<T> = await api.put(url, data, config)
      return response.data
    } catch (err: unknown) {
      const axiosError = err as { response?: { status: number; data: unknown }; message: string }
      error.value = {
        message: axiosError.message || 'An error occurred',
        status: axiosError.response?.status,
        data: axiosError.response?.data
      }
      throw error.value
    } finally {
      loading.value = false
    }
  }

  /**
   * Make a DELETE request
   */
  async function del<T = unknown>(url: string, config?: unknown): Promise<T> {
    loading.value = true
    error.value = null
    try {
      const response: AxiosResponse<T> = await api.delete(url, config)
      return response.data
    } catch (err: unknown) {
      const axiosError = err as { response?: { status: number; data: unknown }; message: string }
      error.value = {
        message: axiosError.message || 'An error occurred',
        status: axiosError.response?.status,
        data: axiosError.response?.data
      }
      throw error.value
    } finally {
      loading.value = false
    }
  }

  /**
   * Clear error state
   */
  function clearError(): void {
    error.value = null
  }

  return {
    loading,
    error,
    get,
    post,
    put,
    del,
    clearError
  }
}

/**
 * Specific API composables for common endpoints
 */
export function usePlayerApi() {
  const { get, loading, error } = useApi()
  const { fetchWithCache } = useApiCache()

  async function fetchPlayers(limit?: number) {
    const url = limit ? `/api/players?limit=${limit}` : '/api/players'
    return fetchWithCache('players:list', () => get(url))
  }

  async function fetchPlayerDetail(playerName: string) {
    return get(`/api/player/${encodeURIComponent(playerName)}/villages`)
  }

  async function fetchPlayerHistory(playerName: string) {
    return get(`/api/player/${encodeURIComponent(playerName)}/history`)
  }

  return {
    fetchPlayers,
    fetchPlayerDetail,
    fetchPlayerHistory,
    loading,
    error
  }
}

export function useAllianceApi() {
  const { get, loading, error } = useApi()
  const { fetchWithCache } = useApiCache()

  async function fetchAlliances() {
    return fetchWithCache('alliances:list', () => get('/api/alliances'))
  }

  async function fetchAllianceTags() {
    return fetchWithCache('alliances:tags', () => get('/api/alliance'))
  }

  async function fetchAllianceDetail(tag: string) {
    return get(`/api/alliance/${encodeURIComponent(tag)}/villages`)
  }

  return {
    fetchAlliances,
    fetchAllianceTags,
    fetchAllianceDetail,
    loading,
    error
  }
}

export function useRegionApi() {
  const { get, loading, error } = useApi()
  const { fetchWithCache } = useApiCache()

  async function fetchRegions() {
    return fetchWithCache('regions:list', () => get('/api/region'))
  }

  async function fetchRegionDetail(regionName: string) {
    return get(`/api/region/${encodeURIComponent(regionName)}/villages`)
  }

  return {
    fetchRegions,
    fetchRegionDetail,
    loading,
    error
  }
}
