/**
 * TypeScript type definitions for API responses and data models.
 */

export interface Player {
  id: number
  name: string
  alliance?: string
  villages: number
  population: number
  tribe?: string
  tribe_id?: number
  tribeId?: number
}

export interface Alliance {
  alliance: string
  players?: number
  population?: number
  villages?: number
  topRegion?: string
}

export interface Region {
  region: string
  villages?: number
  population?: number
}

export interface Village {
  field_id: number
  x: number
  y: number
  tribe: string
  village_id: number
  village_name: string
  player_id: number
  player_name: string
  alliance_id: number
  alliance_tag: string
  population: number
  region: string
  capital: boolean
  city: boolean
  harbor: boolean
  victory_points: number
  dump_date?: string
}

export interface Marker {
  x: number
  y: number
  tribe?: string
  alliance?: string
  player?: string
  population?: number
}

export interface MarkerResponse {
  markers: string // SVG string
  alliance_checkboxes?: string // HTML string
  tribe_checkboxes?: string // HTML string
}

export interface PlayerHistory {
  dump_date: string
  villages: number
  population: number
  victory_points: number
}

export interface PaginatedResponse<T> {
  status: string
  data: T[]
  pagination: {
    page: number
    per_page: number
    total: number
    total_pages: number
    has_next: boolean
    has_prev: boolean
  }
  timestamp: string
}

export interface ApiErrorResponse {
  status: 'error'
  message: string
  code: number
  timestamp: string
  payload?: Record<string, unknown>
}

export interface ApiSuccessResponse<T = unknown> {
  status: 'success'
  message: string
  timestamp: string
  data?: T
}
