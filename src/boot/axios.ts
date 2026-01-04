// src/boot/axios.js
import { boot } from 'quasar/wrappers'
import axios from 'axios'

const api = axios.create({
  baseURL:'http://localhost:5000',
  withCredentials: true,
  timeout: 6000
})

// Optional: attach auth token if you use one
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Centralized 401 handling
api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err?.response?.status === 401) {
      // preserve redirect
      const target = encodeURIComponent(window.location.pathname + window.location.search)
      window.location.href = `/login?redirect=${target}`
    }
    return Promise.reject(err)
  }
)

export default boot(({ app }) => {
  app.config.globalProperties.$api = api
})

export { api }
