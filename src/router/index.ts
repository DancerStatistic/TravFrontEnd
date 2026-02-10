// src/router/index.ts
import { route } from 'quasar/wrappers'
import {
  createRouter,
  createMemoryHistory,
  createWebHistory,
  createWebHashHistory
} from 'vue-router'

import routes from './routes'
import { useAppStore } from 'src/stores/app'

const PUBLIC_PATHS = ['/', '/login']
const PUBLIC_NAMES = ['landing', 'login']

function isPublicRoute(to: { path: string; name?: string }): boolean {
  if (PUBLIC_NAMES.includes(to.name as string)) return true
  if (PUBLIC_PATHS.includes(to.path)) return true
  return false
}

export default route(function (/* { store, ssrContext } */) {
  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : (process.env.VUE_ROUTER_MODE === 'history' ? createWebHistory : createWebHashHistory)

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,

    // leave this as is and make sure VUE_ROUTER_MODE matches quasar.config.js
    history: createHistory(process.env.VUE_ROUTER_BASE)
  })

  Router.beforeEach((to, _from, next) => {
    const appStore = useAppStore()
    if (to.name === 'login' && appStore.isAuthenticated) {
      next({ path: '/', replace: true })
      return
    }
    if (isPublicRoute(to)) return next()
    if (!appStore.isAuthenticated) {
      next({ path: '/login', query: { redirect: to.fullPath } })
    } else {
      next()
    }
  })

  return Router
})
