<template>
  <q-page class="landing-page">
    <!-- HERO -->
    <section class="hero">
      <canvas ref="heroCanvas" class="hero__canvas" aria-hidden="true"></canvas>
      <div class="hero__overlay"></div>

      <div class="hero__content container">
        <div class="row items-center q-col-gutter-xl">
          <div class="col-12 col-md-7">
            <div class="hero__kicker">
              <q-icon name="analytics" size="14px" class="q-mr-xs" />
              Travian Intelligence Platform
            </div>

            <h1 class="hero__title">Master your Travian game with real-time analytics</h1>

            <p class="hero__subtitle">
              Track every player, alliance, and village across the map. Get actionable insights with live data updates,
              power rankings, growth trends, and strategic intelligence tools built for competitive players.
            </p>

            <div class="hero__actions q-mt-lg">
              <q-btn
                to="/map"
                color="primary"
                size="lg"
                unelevated
                rounded
                icon="map"
                label="Explore Interactive Map"
                class="hero__btn"
              />
              <q-btn
                to="/player"
                color="white"
                text-color="primary"
                size="lg"
                outline
                rounded
                icon="person"
                label="Player Rankings"
                class="hero__btn"
              />
            </div>

            <div class="hero__quick row q-col-gutter-md q-mt-xl">
              <div class="col-12 col-sm-6">
                <q-card flat bordered class="quick-card">
                  <q-card-section class="row items-center no-wrap">
                    <q-icon name="bolt" size="22px" class="text-amber-7 q-mr-sm" />
                    <div>
                      <div class="text-subtitle2">Daily updates</div>
                      <div class="text-caption text-grey-6">Fresh data synced once per day</div>
                    </div>
                  </q-card-section>
                </q-card>
              </div>
              <div class="col-12 col-sm-6">
                <q-card flat bordered class="quick-card">
                  <q-card-section class="row items-center no-wrap">
                    <q-icon name="psychology" size="22px" class="text-purple-7 q-mr-sm" />
                    <div>
                      <div class="text-subtitle2">Strategic insights</div>
                      <div class="text-caption text-grey-6">Growth tracking, expansion patterns, and threat analysis</div>
                    </div>
                  </q-card-section>
                </q-card>
              </div>
            </div>

            <div class="hero__stats row q-col-gutter-sm q-mt-lg">
              <div class="col-auto">
                <div class="stat-pill">
                  <q-icon name="speed" size="16px" class="q-mr-xs" />
                  <span>Sub-second search</span>
                </div>
              </div>
              <div class="col-auto">
                <div class="stat-pill">
                  <q-icon name="public" size="16px" class="q-mr-xs" />
                  <span>Full map coverage</span>
                </div>
              </div>
              <div class="col-auto">
                <div class="stat-pill">
                  <q-icon name="trending_up" size="16px" class="q-mr-xs" />
                  <span>Historical tracking</span>
                </div>
              </div>
            </div>
          </div>

          <div class="col-12 col-md-5">
            <q-card class="hero-panel" flat bordered>
              <q-card-section class="row items-start justify-between">
                <div>
                  <div class="text-subtitle1 text-weight-bold">Live Game Snapshot</div>
                  <div class="text-caption text-grey-6">
                    {{ loading ? 'Loading latest data…' : snapshotCaption }}
                  </div>
                </div>

                <q-chip
                  dense
                  square
                  :color="loading ? 'grey-4' : 'positive'"
                  :text-color="loading ? 'grey-8' : 'white'"
                  :icon="loading ? 'hourglass_empty' : 'check_circle'"
                >
                  {{ loading ? 'Syncing' : 'Cached' }}
                </q-chip>
              </q-card-section>

              <q-separator />

              <q-card-section class="q-pt-md">
                <div class="kpi-grid">
                  <div class="kpi">
                    <div class="kpi__label">
                      <q-icon name="people" size="12px" class="q-mr-xs" />
                      Active Players
                    </div>
                    <div class="kpi__value">
                      <q-skeleton v-if="loading" type="text" width="70px" />
                      <span v-else>{{ totals.players.toLocaleString() }}</span>
                    </div>
                  </div>

                  <div class="kpi">
                    <div class="kpi__label">
                      <q-icon name="location_city" size="12px" class="q-mr-xs" />
                      Total Villages
                    </div>
                    <div class="kpi__value">
                      <q-skeleton v-if="loading" type="text" width="90px" />
                      <span v-else>{{ totals.villages.toLocaleString() }}</span>
                    </div>
                  </div>

                  <div class="kpi">
                    <div class="kpi__label">
                      <q-icon name="groups" size="12px" class="q-mr-xs" />
                      Population
                    </div>
                    <div class="kpi__value">
                      <q-skeleton v-if="loading" type="text" width="120px" />
                      <span v-else>{{ totals.population.toLocaleString() }}</span>
                    </div>
                  </div>

                  <div class="kpi">
                    <div class="kpi__label">
                      <q-icon name="trending_up" size="12px" class="q-mr-xs" />
                      Avg / Player
                    </div>
                    <div class="kpi__value">
                      <q-skeleton v-if="loading" type="text" width="90px" />
                      <span v-else>{{ totals.avgPop.toLocaleString() }}</span>
                    </div>
                  </div>
                </div>

                <div class="q-mt-md">
                  <q-select
                    v-model="selectedPlayer"
                    :options="playerOptions"
                    use-input
                    fill-input
                    hide-selected
                    clearable
                    outlined
                    dense
                    label="Quick player search…"
                    :input-debounce="0"
                    behavior="menu"
                    :loading="loading || optionsLoading"
                    @filter="filterPlayers"
                    @update:model-value="onSelectedPlayer"
                  >
                    <template #prepend>
                      <q-icon name="search" />
                    </template>

                    <template #no-option>
                      <q-item>
                        <q-item-section class="text-grey-7">No matching players found</q-item-section>
                      </q-item>
                    </template>

                    <template #option="scope">
                      <q-item v-bind="scope.itemProps">
                        <q-item-section avatar>
                          <q-avatar size="32px" color="primary" text-color="white">
                            {{ (scope.opt.label || '?').charAt(0).toUpperCase() }}
                          </q-avatar>
                        </q-item-section>
                        <q-item-section>
                          <q-item-label class="text-weight-medium">{{ scope.opt.label }}</q-item-label>
                          <q-item-label caption>
                            {{ (scope.opt.alliance || '—') }} • {{ (scope.opt.villages || 0).toLocaleString() }} villages
                          </q-item-label>
                        </q-item-section>
                        <q-item-section side class="text-right">
                          <div class="text-weight-bold text-primary">
                            {{ (scope.opt.population || 0).toLocaleString() }}
                          </div>
                          <div class="text-caption text-grey-6">pop</div>
                        </q-item-section>
                      </q-item>
                    </template>
                  </q-select>

                  <div class="row q-col-gutter-sm q-mt-sm">
                    <div class="col-12 col-sm-6">
                      <q-btn
                        outline
                        rounded
                        icon="person"
                        label="Players"
                        class="full-width"
                        to="/player"
                      />
                    </div>
                    <div class="col-12 col-sm-6">
                      <q-btn
                        outline
                        rounded
                        icon="groups"
                        label="Alliances"
                        class="full-width"
                        to="/alliance"
                      />
                    </div>
                  </div>
                </div>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </div>

      <div class="hero__fade"></div>
    </section>

    <!-- AT A GLANCE -->
    <section class="section section--light">
      <div class="container">
        <div class="section-head">
          <div>
            <div class="section-kicker">At a glance</div>
            <h2 class="section-title">Useful signals, not just counts</h2>
            <div class="section-subtitle">
              Top players right now + population distribution + villages-per-player spread.
            </div>
          </div>

          <div class="row items-center q-gutter-sm">
            <q-btn
              to="/map"
              color="primary"
              outline
              rounded
              icon="map"
              label="Open Map"
            />
            <q-btn
              to="/region"
              color="primary"
              flat
              rounded
              icon="terrain"
              label="Regions"
            />
          </div>
        </div>

        <div class="row q-col-gutter-lg q-mt-md">
          <!-- Top players -->
          <div class="col-12 col-md-5">
            <q-card flat bordered class="panel">
              <q-card-section class="row items-center justify-between">
                <div class="text-subtitle1 text-weight-bold">Top players</div>
                <q-chip dense square color="grey-2" text-color="grey-8" icon="sort">
                  by population
                </q-chip>
              </q-card-section>
              <q-separator />

              <q-card-section>
                <div v-if="loading">
                  <q-skeleton v-for="i in 6" :key="i" type="QItem" class="q-mb-sm" />
                </div>

                <q-list v-else dense padding class="top-list">
                  <q-item
                    v-for="(p, idx) in topPlayers"
                    :key="p.name"
                    clickable
                    @click="goPlayer(p.name)"
                  >
                    <q-item-section avatar>
                      <q-avatar size="30px" color="grey-2" text-color="grey-8">
                        {{ idx + 1 }}
                      </q-avatar>
                    </q-item-section>

                    <q-item-section>
                      <q-item-label class="text-weight-medium">{{ p.name }}</q-item-label>
                      <q-item-label caption>
                        {{ (p.alliance || '—') }} • {{ (p.villages || 0).toLocaleString() }} villages
                      </q-item-label>
                    </q-item-section>

                    <q-item-section side class="text-right">
                      <div class="text-weight-bold text-primary">
                        {{ (p.population || 0).toLocaleString() }}
                      </div>
                      <div class="text-caption text-grey-6">pop</div>
                    </q-item-section>
                  </q-item>
                </q-list>

                <q-separator class="q-my-sm" />
                <q-btn
                  to="/player"
                  color="primary"
                  flat
                  icon-right="arrow_forward"
                  label="See full player table"
                  class="full-width"
                />
              </q-card-section>
            </q-card>
          </div>

          <!-- Distribution charts -->
          <div class="col-12 col-md-7">
            <div class="row q-col-gutter-lg">
              <!-- Population buckets -->
              <div class="col-12">
                <q-card flat bordered class="panel">
                  <q-card-section class="row items-center justify-between">
                    <div>
                      <div class="text-subtitle1 text-weight-bold">Population distribution</div>
                      <div class="text-caption text-grey-6">
                        Players grouped by population buckets
                      </div>
                    </div>

                    <q-chip dense square color="grey-2" text-color="grey-8" icon="bar_chart">
                      buckets
                    </q-chip>
                  </q-card-section>

                  <q-separator />

                  <q-card-section>
                    <div v-if="loading" class="row q-col-gutter-sm">
                      <div class="col-12">
                        <q-skeleton type="rect" height="140px" />
                      </div>
                    </div>

                    <div v-else class="bars">
                      <div
                        v-for="b in popBuckets"
                        :key="b.label"
                        class="bar"
                        :title="`${b.label}: ${b.count.toLocaleString()} players`"
                      >
                        <div class="bar__head">
                          <div class="bar__label">{{ b.label }}</div>
                          <div class="bar__value">{{ b.count.toLocaleString() }}</div>
                        </div>
                        <div class="bar__track">
                          <div class="bar__fill" :style="{ width: `${b.pct}%` }"></div>
                        </div>
                      </div>
                    </div>
                  </q-card-section>
                </q-card>
              </div>

              <!-- Villages per player -->
              <div class="col-12">
                <q-card flat bordered class="panel">
                  <q-card-section class="row items-center justify-between">
                    <div>
                      <div class="text-subtitle1 text-weight-bold">Villages per player</div>
                      <div class="text-caption text-grey-6">
                        Shows how concentrated expansion is
                      </div>
                    </div>

                    <q-chip dense square color="grey-2" text-color="grey-8" icon="insights">
                      spread
                    </q-chip>
                  </q-card-section>

                  <q-separator />

                  <q-card-section>
                    <div v-if="loading">
                      <q-skeleton type="rect" height="120px" />
                    </div>

                    <div v-else class="mini-grid">
                      <div class="mini">
                        <div class="mini__label">Median</div>
                        <div class="mini__value">{{ villagesStats.median.toLocaleString() }}</div>
                      </div>
                      <div class="mini">
                        <div class="mini__label">Average</div>
                        <div class="mini__value">{{ villagesStats.avg.toLocaleString() }}</div>
                      </div>
                      <div class="mini">
                        <div class="mini__label">90th pct</div>
                        <div class="mini__value">{{ villagesStats.p90.toLocaleString() }}</div>
                      </div>
                      <div class="mini">
                        <div class="mini__label">Max</div>
                        <div class="mini__value">{{ villagesStats.max.toLocaleString() }}</div>
                      </div>
                    </div>

                    <div v-if="!loading" class="spark q-mt-md" aria-hidden="true">
                      <div
                        v-for="(v, i) in villagesHistogram"
                        :key="i"
                        class="spark__bar"
                        :style="{ height: `${v.pct}%` }"
                        :title="`${v.label}: ${v.count.toLocaleString()} players`"
                      />
                    </div>

                    <div v-if="!loading" class="row q-mt-sm">
                      <div class="col text-caption text-grey-6">
                        Histogram buckets: {{ villagesHistogram.map(h => h.label).join(' • ') }}
                      </div>
                    </div>
                  </q-card-section>
                </q-card>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- FEATURES -->
    <section class="section">
      <div class="container">
        <div class="section-head">
          <div>
            <div class="section-kicker">Tools</div>
            <h2 class="section-title">Explore the world from multiple angles</h2>
            <div class="section-subtitle">
              Jump into what you need — map, players, alliances, regions.
            </div>
          </div>
        </div>

        <div class="features-grid q-mt-md">
          <q-card v-for="f in features" :key="f.title" flat bordered class="feature">
            <q-card-section>
              <div class="row items-start no-wrap">
                <q-icon :name="f.icon" size="34px" :color="f.color" class="q-mr-md" />
                <div>
                  <div class="text-h6">{{ f.title }}</div>
                  <div class="text-body2 text-grey-7 q-mt-xs">{{ f.description }}</div>
                </div>
              </div>
            </q-card-section>
            <q-separator />
            <q-card-actions align="right">
              <q-btn
                v-if="f.route"
                flat
                color="primary"
                :to="f.route"
                icon-right="arrow_forward"
                label="Open"
              />
            </q-card-actions>
          </q-card>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="cta">
      <div class="container">
        <q-card flat bordered class="cta-card">
          <q-card-section class="text-center">
            <div class="text-h4 text-weight-bold">Ready to explore?</div>
            <div class="text-body1 text-grey-7 q-mt-sm">
              Start with the interactive map, or jump straight to a player page.
            </div>

            <div class="row justify-center q-gutter-md q-mt-lg">
              <q-btn to="/map" color="primary" unelevated rounded icon="map" label="Open Map" />
              <q-btn to="/player" color="secondary" outline rounded icon="person" label="Players" />
            </div>
          </q-card-section>
        </q-card>
      </div>
    </section>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { api } from 'boot/axios'

const router = useRouter()

/* =========================================================
 * Client-side request throttling (daily-updated data)
 * - Caches GET responses in localStorage for a TTL
 * - Dedupes in-flight requests to avoid bursts
 * ========================================================= */
const CACHE_NS = 'travstat:api_cache:v1'
const DEFAULT_TTL_MS = 6 * 60 * 60 * 1000 // 6h (tune as desired)

const inflight = new Map()

function cacheKey(url) {
  return `${CACHE_NS}:${url}`
}

function safeJsonParse(s) {
  try {
    return JSON.parse(s)
  } catch {
    return null
  }
}

function readCache(url) {
  try {
    const raw = localStorage.getItem(cacheKey(url))
    if (!raw) return null
    const obj = safeJsonParse(raw)
    if (!obj || typeof obj.ts !== 'number') return null
    return obj
  } catch {
    return null
  }
}

function writeCache(url, data) {
  try {
    localStorage.setItem(cacheKey(url), JSON.stringify({ ts: Date.now(), data }))
  } catch {
    // ignore quota / private-mode failures
  }
}

async function cachedGet(url, { ttlMs = DEFAULT_TTL_MS } = {}) {
  const cached = readCache(url)
  if (cached && Date.now() - cached.ts < ttlMs) return cached.data

  if (inflight.has(url)) return inflight.get(url)

  const p = api
    .get(url)
    .then((res) => {
      const data = res?.data
      writeCache(url, data)
      return data
    })
    .finally(() => inflight.delete(url))

  inflight.set(url, p)
  return p
}

/* -----------------------------
 * Data loading
 * ----------------------------- */
const loading = ref(false)
const players = ref([])

const alliancesCount = ref(null)
const regionsCount = ref(null)

/**
 * Autocomplete state (q-select)
 * - selectedPlayer: the chosen option object (or null)
 * - playerOptions: the filtered list shown in the dropdown
 * - optionsLoading: small loading flag for filter work
 */
const selectedPlayer = ref(null)
const playerOptions = ref([])
const optionsLoading = ref(false)

function goPlayer(name) {
  const n = (name || '').trim()
  if (!n) return
  router.push({ name: 'player-detail', params: { name: n } })
}

function onSelectedPlayer(val) {
  // Only navigate when the user selects a real option from the list
  if (!val || !val.value) return
  goPlayer(val.value)
}

/**
 * Filter callback for QSelect
 * - Ensures user can type to narrow options,
 *   but cannot submit an arbitrary name (only selectable options navigate).
 */
function filterPlayers(needle, update) {
  update(() => {
    optionsLoading.value = true
    const n = (needle || '').trim().toLowerCase()

    // base list: all players mapped to option objects
    // keep it small in the dropdown: cap results
    let list = (players.value || []).map((p) => ({
      label: p.name,
      value: p.name,
      alliance: p.alliance,
      villages: p.villages,
      population: p.population
    }))

    if (n) {
      list = list.filter((o) => (o.label || '').toLowerCase().includes(n))
    }

    // Sort by population desc so best matches feel useful
    list.sort((a, b) => Number(b.population || 0) - Number(a.population || 0))

    // cap to avoid huge menus
    playerOptions.value = list.slice(0, 30)
    optionsLoading.value = false
  })
}

async function loadLandingData() {
  loading.value = true
  try {
    // Players (for totals + charts + top list + autocomplete list)
    // Cached to avoid refetching constantly across navigation/reloads.
    const playersData = await cachedGet('/api/players?limit=1000', { ttlMs: DEFAULT_TTL_MS })
    players.value = Array.isArray(playersData) ? playersData : []

    // initialize options with top-population players (useful before typing)
    playerOptions.value = [...players.value]
      .sort((a, b) => Number(b?.population || 0) - Number(a?.population || 0))
      .slice(0, 30)
      .map((p) => ({
        label: p.name,
        value: p.name,
        alliance: p.alliance,
        villages: p.villages,
        population: p.population
      }))

    // Alliances count (best-effort; supports {total} or array) - cached too
    try {
      const aData = await cachedGet('/api/alliances', { ttlMs: DEFAULT_TTL_MS })
      if (aData && typeof aData.total === 'number') alliancesCount.value = aData.total
      else if (Array.isArray(aData)) alliancesCount.value = aData.length
    } catch {
      alliancesCount.value = null
    }

    // Regions count (best-effort; supports array or {total}) - cached too
    try {
      const rData = await cachedGet('/api/region', { ttlMs: DEFAULT_TTL_MS })
      if (Array.isArray(rData)) regionsCount.value = rData.length
      else if (rData && typeof rData.total === 'number') regionsCount.value = rData.total
    } catch {
      regionsCount.value = null
    }
  } finally {
    loading.value = false
  }
}

/* -----------------------------
 * Derived stats
 * ----------------------------- */
const totals = computed(() => {
  const ps = players.value || []
  const playersCount = ps.length

  let villages = 0
  let population = 0

  for (const p of ps) {
    villages += Number(p?.villages || 0)
    population += Number(p?.population || 0)
  }

  const avgPop = playersCount ? Math.round(population / playersCount) : 0

  return {
    players: playersCount,
    villages,
    population,
    avgPop
  }
})

const snapshotCaption = computed(() => {
  const a = alliancesCount.value
  const r = regionsCount.value
  const parts = []
  if (typeof a === 'number') parts.push(`${a.toLocaleString()} alliances`)
  if (typeof r === 'number') parts.push(`${r.toLocaleString()} regions`)
  if (!parts.length) return 'Aggregated from the latest daily scrape'
  return parts.join(' • ')
})

const topPlayers = computed(() => {
  return [...(players.value || [])]
    .sort((a, b) => Number(b?.population || 0) - Number(a?.population || 0))
    .slice(0, 8)
})

/**
 * Population buckets:
 * - < 1k
 * - 1k–5k
 * - 5k–10k
 * - 10k–25k
 * - 25k–50k
 * - 50k+
 */
const popBuckets = computed(() => {
  const ps = players.value || []
  const buckets = [
    { label: '< 1k', min: 0, max: 999, count: 0 },
    { label: '1k–5k', min: 1000, max: 4999, count: 0 },
    { label: '5k–10k', min: 5000, max: 9999, count: 0 },
    { label: '10k–25k', min: 10000, max: 24999, count: 0 },
    { label: '25k–50k', min: 25000, max: 49999, count: 0 },
    { label: '50k+', min: 50000, max: Infinity, count: 0 }
  ]

  for (const p of ps) {
    const pop = Number(p?.population || 0)
    const b = buckets.find((x) => pop >= x.min && pop <= x.max)
    if (b) b.count += 1
  }

  const maxCount = Math.max(1, ...buckets.map((b) => b.count))
  return buckets.map((b) => ({
    ...b,
    pct: Math.round((b.count / maxCount) * 100)
  }))
})

/**
 * Villages stats (median, avg, p90, max) + histogram
 */
function percentile(sorted, p) {
  if (!sorted.length) return 0
  const idx = Math.min(sorted.length - 1, Math.max(0, Math.floor((p / 100) * (sorted.length - 1))))
  return sorted[idx]
}

const villagesStats = computed(() => {
  const vs = (players.value || []).map((p) => Number(p?.villages || 0)).sort((a, b) => a - b)
  if (!vs.length) return { median: 0, avg: 0, p90: 0, max: 0 }

  const sum = vs.reduce((s, n) => s + n, 0)
  return {
    median: percentile(vs, 50),
    avg: Math.round(sum / vs.length),
    p90: percentile(vs, 90),
    max: vs[vs.length - 1]
  }
})

/**
 * Histogram buckets (villages):
 * 1 • 2 • 3–4 • 5–7 • 8–12 • 13+
 */
const villagesHistogram = computed(() => {
  const ps = players.value || []
  const buckets = [
    { label: '1', min: 1, max: 1, count: 0 },
    { label: '2', min: 2, max: 2, count: 0 },
    { label: '3–4', min: 3, max: 4, count: 0 },
    { label: '5–7', min: 5, max: 7, count: 0 },
    { label: '8–12', min: 8, max: 12, count: 0 },
    { label: '13+', min: 13, max: Infinity, count: 0 }
  ]

  for (const p of ps) {
    const v = Number(p?.villages || 0)
    const b = buckets.find((x) => v >= x.min && v <= x.max)
    if (b) b.count += 1
  }

  const maxCount = Math.max(1, ...buckets.map((b) => b.count))
  return buckets.map((b) => ({
    ...b,
    pct: Math.round((b.count / maxCount) * 100)
  }))
})

/* -----------------------------
 * Features cards
 * ----------------------------- */
const features = [
  {
    title: 'Interactive Map',
    description: 'Explore villages, alliances, and regions with filtering and quick navigation.',
    icon: 'map',
    color: 'primary',
    route: '/map'
  },
  {
    title: 'Player Analytics',
    description: 'Rankings, village counts, population totals, and quick access to detail pages.',
    icon: 'person',
    color: 'secondary',
    route: '/player'
  },
  {
    title: 'Alliance Overview',
    description: 'Strength, members, and comparative performance across the world.',
    icon: 'groups',
    color: 'accent',
    route: '/alliance'
  },
  {
    title: 'Region Analysis',
    description: 'Regional snapshots: control patterns, top entities, and distribution.',
    icon: 'terrain',
    color: 'positive',
    route: '/region'
  }
]

/* -----------------------------
 * Fancy hero animation (canvas particles)
 * ----------------------------- */
const heroCanvas = ref(null)

let raf = 0
let ctx = null
let w = 0
let h = 0
let particles = []
let lastT = 0

function rand(min, max) {
  return Math.random() * (max - min) + min
}

function setupCanvas() {
  const c = heroCanvas.value
  if (!c) return
  ctx = c.getContext('2d', { alpha: true })
  resizeCanvas()
  initParticles()
  lastT = performance.now()
  tick(lastT)
}

function resizeCanvas() {
  const c = heroCanvas.value
  if (!c) return
  const parent = c.parentElement
  if (!parent) return
  const rect = parent.getBoundingClientRect()
  w = Math.max(1, Math.floor(rect.width))
  h = Math.max(1, Math.floor(rect.height))
  c.width = w * devicePixelRatio
  c.height = h * devicePixelRatio
  c.style.width = `${w}px`
  c.style.height = `${h}px`
  if (ctx) ctx.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0)
}

function initParticles() {
  const count = Math.min(110, Math.max(60, Math.floor((w * h) / 18000)))
  particles = Array.from({ length: count }).map(() => ({
    x: rand(0, w),
    y: rand(0, h),
    vx: rand(-0.18, 0.18),
    vy: rand(-0.12, 0.12),
    r: rand(0.8, 2.2),
    a: rand(0.12, 0.35)
  }))
}

function tick(t) {
  raf = requestAnimationFrame(tick)
  const dt = Math.min(32, t - lastT)
  lastT = t
  if (!ctx) return

  ctx.clearRect(0, 0, w, h)

  for (const p of particles) {
    p.x += p.vx * dt
    p.y += p.vy * dt

    if (p.x < -20) p.x = w + 20
    if (p.x > w + 20) p.x = -20
    if (p.y < -20) p.y = h + 20
    if (p.y > h + 20) p.y = -20

    ctx.globalAlpha = p.a
    ctx.beginPath()
    ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2)
    ctx.fillStyle = '#ffffff'
    ctx.fill()
  }

  // light connections
  ctx.globalAlpha = 0.08
  ctx.strokeStyle = '#ffffff'
  for (let i = 0; i < particles.length; i++) {
    for (let j = i + 1; j < particles.length; j++) {
      const a = particles[i]
      const b = particles[j]
      const dx = a.x - b.x
      const dy = a.y - b.y
      const d2 = dx * dx + dy * dy
      if (d2 < 130 * 130) {
        ctx.lineWidth = 1
        ctx.beginPath()
        ctx.moveTo(a.x, a.y)
        ctx.lineTo(b.x, b.y)
        ctx.stroke()
      }
    }
  }
}

/* -----------------------------
 * Lifecycle
 * ----------------------------- */
function onResize() {
  resizeCanvas()
  initParticles()
}

onMounted(() => {
  loadLandingData()
  setupCanvas()
  window.addEventListener('resize', onResize, { passive: true })
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
  if (raf) cancelAnimationFrame(raf)
})
</script>
  <style scoped lang="scss">
    .landing-page {
      min-height: 100vh;
    }
    
    .hero {
      position: relative;
      min-height: 82vh;
      display: flex;
      align-items: center;
      overflow: hidden;
      background: radial-gradient(1300px 650px at 18% 12%, rgba(255, 255, 255, 0.22), transparent 62%),
        radial-gradient(1100px 650px at 88% 38%, rgba(255, 255, 255, 0.16), transparent 60%),
        linear-gradient(135deg, #1e40af 0%, #7c3aed 48%, #f59e0b 125%);
    }
    
    .hero__canvas {
      position: absolute;
      inset: 0;
      z-index: 0;
      opacity: 0.7;
    }
    
    .hero__overlay {
      position: absolute;
      inset: 0;
      z-index: 1;
      background: linear-gradient(
        180deg,
        rgba(0, 0, 0, 0.16) 0%,
        rgba(0, 0, 0, 0.24) 58%,
        rgba(0, 0, 0, 0.12) 100%
      );
    }
    
    .hero__fade {
      position: absolute;
      left: 0;
      right: 0;
      bottom: 0;
      height: 140px;
      z-index: 2;
      background: linear-gradient(180deg, transparent, rgba(255, 255, 255, 1));
    }
    
    .hero__content {
      position: relative;
      z-index: 2;
      padding: 4.5rem 1rem 3.5rem;
    }
    
    .container {
      max-width: 1320px;
      margin: 0 auto;
      padding: 0 1rem;
    }
    
    .hero__kicker {
      display: inline-flex;
      align-items: center;
      padding: 0.4rem 0.75rem;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.18);
      border: 1px solid rgba(255, 255, 255, 0.25);
      color: rgba(255, 255, 255, 0.98);
      font-weight: 700;
      letter-spacing: 0.7px;
      font-size: 0.82rem;
      text-transform: uppercase;
    }
    
    .hero__title {
      color: white;
      font-weight: 900;
      font-size: 3.5rem;
      line-height: 1.08;
      margin: 1rem 0 0.9rem;
      letter-spacing: -0.02em;
    
      @media (max-width: 600px) {
        font-size: 2.4rem;
      }
    }
    
    .hero__subtitle {
      color: rgba(255, 255, 255, 0.94);
      font-size: 1.25rem;
      line-height: 1.6;
      margin: 0;
      max-width: 56ch;
    
      @media (max-width: 600px) {
        font-size: 1.08rem;
      }
    }
    
    .hero__actions {
      display: flex;
      gap: 0.85rem;
      flex-wrap: wrap;
    }
    
    .hero__btn {
      min-width: 200px;
      font-weight: 600;
    }
    
    .hero__stats {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
    }
    
    .stat-pill {
      display: inline-flex;
      align-items: center;
      padding: 0.4rem 0.85rem;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.15);
      border: 1px solid rgba(255, 255, 255, 0.2);
      color: rgba(255, 255, 255, 0.95);
      font-size: 0.8rem;
      font-weight: 600;
      backdrop-filter: blur(8px);
    }
    
    .hero-panel {
      backdrop-filter: blur(12px);
      background: rgba(255, 255, 255, 0.94);
      border-radius: 18px;
      overflow: hidden;
      box-shadow: 0 20px 48px rgba(0, 0, 0, 0.24);
    }
    
    .quick-card {
      background: rgba(255, 255, 255, 0.94);
      border-radius: 16px;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .quick-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
    }
    
    .kpi-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1rem;
    }
    
    .kpi {
      padding: 0.85rem 0.95rem;
      border-radius: 14px;
      background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
      border: 1px solid rgba(0, 0, 0, 0.05);
    }
    .kpi__label {
      font-size: 0.75rem;
      letter-spacing: 0.6px;
      color: #64748b;
      text-transform: uppercase;
      font-weight: 700;
      display: flex;
      align-items: center;
    }
    .kpi__value {
      font-size: 1.45rem;
      font-weight: 900;
      margin-top: 0.3rem;
      color: #0f172a;
    }
    
    .section {
      padding: 4rem 1rem;
      background: white;
    }
    .section--light {
      background: #f8f9fc;
    }
    
    .section-head {
      display: flex;
      gap: 1.5rem;
      align-items: flex-end;
      justify-content: space-between;
      flex-wrap: wrap;
    }
    .section-kicker {
      color: #64748b;
      font-weight: 800;
      letter-spacing: 0.8px;
      text-transform: uppercase;
      font-size: 0.78rem;
      display: inline-flex;
      align-items: center;
    }
    .section-title {
      margin: 0.3rem 0 0;
      font-size: 2.4rem;
      font-weight: 900;
      color: #0f172a;
      letter-spacing: -0.01em;
    
      @media (max-width: 600px) {
        font-size: 1.85rem;
      }
    }
    .section-subtitle {
      margin-top: 0.5rem;
      color: #64748b;
      font-size: 1.05rem;
      line-height: 1.6;
      max-width: 70ch;
    }
    
    .panel {
      border-radius: 18px;
      background: white;
      box-shadow: 0 12px 32px rgba(15, 23, 42, 0.07);
      border: 1px solid rgba(0, 0, 0, 0.04);
    }
    
    .top-list :deep(.q-item) {
      border-radius: 14px;
      transition: all 0.18s ease;
    }
    .top-list :deep(.q-item:hover) {
      background: #f1f5f9;
      transform: translateX(4px);
    }
    
    .bars {
      display: flex;
      flex-direction: column;
      gap: 0.85rem;
    }
    
    .bar__head {
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      gap: 0.85rem;
      margin-bottom: 0.4rem;
    }
    .bar__label {
      font-weight: 700;
      color: #0f172a;
      font-size: 0.9rem;
      display: flex;
      align-items: center;
    }
    .bar__value {
      font-weight: 800;
      color: #475569;
      font-size: 0.9rem;
    }
    .bar__track {
      height: 12px;
      border-radius: 999px;
      background: #e2e8f0;
      overflow: hidden;
    }
    .bar__fill {
      height: 100%;
      border-radius: 999px;
      background: linear-gradient(90deg, rgba(30, 64, 175, 0.92), rgba(245, 158, 11, 0.92));
      transition: width 0.4s ease;
    }
    
    .mini-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 0.85rem;
    
      @media (max-width: 900px) {
        grid-template-columns: repeat(2, 1fr);
      }
    }
    .mini {
      padding: 0.85rem 0.95rem;
      border-radius: 14px;
      background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
      border: 1px solid rgba(0, 0, 0, 0.05);
    }
    .mini__label {
      font-size: 0.74rem;
      color: #64748b;
      text-transform: uppercase;
      letter-spacing: 0.6px;
      font-weight: 700;
      display: flex;
      align-items: center;
    }
    .mini__value {
      font-size: 1.35rem;
      font-weight: 900;
      margin-top: 0.3rem;
      color: #0f172a;
    }
    
    .spark {
      display: flex;
      align-items: flex-end;
      gap: 10px;
      height: 70px;
      padding: 12px 14px;
      border-radius: 14px;
      background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
      border: 1px solid rgba(0, 0, 0, 0.05);
      overflow: hidden;
    }
    .spark__bar {
      flex: 1;
      border-radius: 12px 12px 4px 4px;
      background: linear-gradient(180deg, rgba(124, 58, 237, 0.92), rgba(30, 64, 175, 0.8));
      transition: transform 0.18s ease;
      cursor: pointer;
    }
    .spark__bar:hover {
      transform: translateY(-3px);
    }
    
    .features-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 1.5rem;
    
      @media (max-width: 900px) {
        grid-template-columns: 1fr;
      }
    }
    
    .feature {
      border-radius: 18px;
      background: white;
      box-shadow: 0 12px 32px rgba(15, 23, 42, 0.07);
  border: 1px solid rgba(0, 0, 0, 0.04);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.feature:hover {
  transform: translateY(-6px);
  box-shadow: 0 20px 48px rgba(15, 23, 42, 0.12);
}

.benefit-card {
  border-radius: 18px;
  background: white;
  box-shadow: 0 12px 32px rgba(15, 23, 42, 0.07);
  border: 1px solid rgba(0, 0, 0, 0.04);
  height: 100%;
  transition: transform 0.2s ease;
}
.benefit-card:hover {
  transform: translateY(-4px);
}

.cta {
  padding: 5rem 1rem;
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 50%, #e0e7ff 100%);
}

.cta-card {
  border-radius: 24px;
  max-width: 900px;
  margin: 0 auto;
  padding: 2.5rem 1.5rem;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 24px 56px rgba(0, 0, 0, 0.12);
  border: 1px solid rgba(0, 0, 0, 0.04);
}

/* Small polish for the list rows (both top players + top alliances) */
.top-list :deep(.q-item__section--side) {
  min-width: 88px;
}
.top-list :deep(.q-item) {
  cursor: pointer;
}

/* Make the feature tiles evenly tall and tidy */
.feature :deep(.q-card__section) {
  min-height: 140px;
}

/* Mobile spacing tweaks */
@media (max-width: 600px) {
  .hero__content {
    padding: 3.75rem 1rem 3rem;
  }

  .hero__btn {
    min-width: 100%;
  }

  .kpi-grid {
    grid-template-columns: 1fr;
  }

  .section {
    padding: 3.25rem 1rem;
  }

  .cta {
    padding: 4rem 1rem;
  }

  .cta-card {
    padding: 2rem 1.25rem;
  }
}
</style>

    