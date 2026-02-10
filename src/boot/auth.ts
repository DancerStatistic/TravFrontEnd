import { boot } from 'quasar/wrappers'
import { api } from './axios'
import { useAppStore } from 'src/stores/app'

export default boot(async () => {
  const appStore = useAppStore()
  
  // If we have stored auth state, verify it with the server
  if (appStore.isAuthenticated && appStore.userEmail) {
    try {
      const { data } = await api.get('/api/me')
      if (data?.status === 'success' && data?.user?.email) {
        // Session is valid, ensure store matches server
        appStore.setAuthenticated(data.user.email)
      } else {
        // Session invalid, clear stored state
        appStore.clearAuth()
      }
    } catch {
      // Session check failed, clear stored state
      appStore.clearAuth()
    }
  } else {
    // No stored state, check server anyway (in case of cookie-only session)
    try {
      const { data } = await api.get('/api/me')
      if (data?.status === 'success' && data?.user?.email) {
        appStore.setAuthenticated(data.user.email)
      }
    } catch {
      // Not authenticated - leave as-is
    }
  }
})
