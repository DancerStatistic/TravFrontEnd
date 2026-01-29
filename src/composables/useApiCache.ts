/**
 * Composable for localStorage caching with daily TTL.
 * Provides a consistent caching pattern used across multiple pages.
 */
import { ref } from 'vue'

/**
 * Get today's date key in UTC (YYYY-MM-DD format)
 */
export function dayKeyUTC(): string {
  return new Date().toISOString().slice(0, 10)
}

/**
 * Generate a cache key with today's date suffix
 */
export function cacheKey(base: string): string {
  return `${base}:${dayKeyUTC()}`
}

/**
 * Read data from localStorage cache
 */
export function readCache<T>(key: string): T | null {
  try {
    const raw = localStorage.getItem(key)
    if (!raw) return null
    return JSON.parse(raw) as T
  } catch {
    return null
  }
}

/**
 * Write data to localStorage cache
 */
export function writeCache<T>(key: string, data: T): void {
  try {
    localStorage.setItem(key, JSON.stringify(data))
  } catch (error) {
    // Silently fail if localStorage is full or unavailable
    console.warn('Failed to write to cache:', error)
  }
}

/**
 * Remove a cache entry
 */
export function removeCache(key: string): void {
  try {
    localStorage.removeItem(key)
  } catch {
    // Silently fail
  }
}

/**
 * Composable for API caching with daily TTL
 */
export function useApiCache() {
  /**
   * Fetch data with caching - returns cached data if available for today, otherwise fetches fresh
   */
  async function fetchWithCache<T>(
    cacheKeyBase: string,
    fetchFn: () => Promise<T>,
    forceRefresh = false
  ): Promise<T> {
    const key = cacheKey(cacheKeyBase)
    
    // Return cached data if available and not forcing refresh
    if (!forceRefresh) {
      const cached = readCache<T>(key)
      if (cached !== null) {
        return cached
      }
    }
    
    // Fetch fresh data
    const data = await fetchFn()
    
    // Cache the result
    writeCache(key, data)
    
    return data
  }

  /**
   * Clear cache for a specific key base (removes today's cache)
   */
  function clearCache(cacheKeyBase: string): void {
    const key = cacheKey(cacheKeyBase)
    removeCache(key)
  }

  /**
   * Clear all caches for a specific key base pattern (useful for clearing all daily caches)
   */
  function clearAllCachesForBase(base: string): void {
    try {
      const keys = Object.keys(localStorage)
      const prefix = `${base}:`
      keys.forEach(key => {
        if (key.startsWith(prefix)) {
          localStorage.removeItem(key)
        }
      })
    } catch {
      // Silently fail
    }
  }

  return {
    dayKeyUTC,
    cacheKey,
    readCache,
    writeCache,
    removeCache,
    fetchWithCache,
    clearCache,
    clearAllCachesForBase
  }
}
