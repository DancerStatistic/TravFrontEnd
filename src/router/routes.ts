// src/router/routes.ts
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  // 1. Public login (no layout)
  {
    path: '/login',
    name: 'login',
    component: () => import('pages/LoginPage.vue')
  },

  // 2. All other routes use MainLayout
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', name: 'landing', component: () => import('pages/LandingPage.vue') },
      { path: 'map', name: 'global-map', component: () => import('pages/GlobalMap.vue') },

      // Player list + detail
      { path: 'player', name: 'player-list', component: () => import('pages/PlayerPage.vue') },
      {
        path: 'player/:name',
        name: 'player-detail',
        component: () => import('pages/PlayerDetail.vue'),
        props: true
      },

      // Alliance list + detail
      { path: 'alliance', name: 'alliance-list', component: () => import('pages/AlliancePage.vue') },
      {
        path: 'alliance/:tag',
        name: 'alliance-detail',
        component: () => import('pages/AllianceDetail.vue'),
        props: true
      },

      // Region list + detail
      { path: 'region', name: 'region-list', component: () => import('pages/RegionPage.vue') },
      {
        path: 'region/:name',
        name: 'region-detail',
        component: () => import('pages/RegionDetail.vue'),
        props: true
      },

      // Trade routes (consolidated - removed duplicate alias)
      { path: 'trade', name: 'trade-route', component: () => import('pages/TradeRoutes.vue') },

      // Dashboard (consolidated - removed duplicate alias)
      { path: 'dashboard', name: 'dashboard-page', component: () => import('pages/dashboard/MainDashboard.vue') }
    ]
  },

  // 3. Catch-all → landing
  {
    path: '/:catchAll(.*)*',
    redirect: { name: 'landing' }
  }
]

export default routes
