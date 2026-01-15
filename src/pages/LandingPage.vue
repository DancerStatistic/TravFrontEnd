<template>
  <q-page class="landing-page">
    <!-- HERO -->
    <section class="hero">
      <!-- animated canvas background -->
      <canvas ref="heroCanvas" class="hero__canvas" aria-hidden="true"></canvas>

      <div class="hero__overlay"></div>

      <div class="hero__content container">
        <div class="row items-center q-col-gutter-xl">
          <div class="col-12 col-md-7">
            <div class="hero__kicker">Travian Status</div>
            <h1 class="hero__title">
              Game analytics that actually helps you make decisions.
            </h1>
            <p class="hero__subtitle">
              Players, alliances, regions, and an interactive map — summarized into clear signals, not noise.
            </p>

            <div class="hero__actions q-mt-lg">
              <q-btn
                to="/map"
                color="primary"
                size="lg"
                unelevated
                rounded
                icon="map"
                label="Explore Map"
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
                label="View Players"
                class="hero__btn"
              />
            </div>

            <div class="hero__quick row q-col-gutter-md q-mt-xl">
              <div class="col-12 col-sm-6">
                <q-card flat bordered class="quick-card">
                  <q-card-section class="row items-center no-wrap">
                    <q-icon name="bolt" size="22px" class="q-mr-sm" />
                    <div>
                      <div class="text-subtitle2">Fast insights</div>
                      <div class="text-caption text-grey-6">
                        Top players, distributions, and totals at a glance
                      </div>
                    </div>
                  </q-card-section>
                </q-card>
              </div>
              <div class="col-12 col-sm-6">
                <q-card flat bordered class="quick-card">
                  <q-card-section class="row items-center no-wrap">
                    <q-icon name="tune" size="22px" class="q-mr-sm" />
                    <div>
                      <div class="text-subtitle2">Practical tools</div>
                      <div class="text-caption text-grey-6">
                        Jump straight into map filters and player detail pages
                      </div>
                    </div>
                  </q-card-section>
                </q-card>
              </div>
            </div>
          </div>

          <div class="col-12 col-md-5">
            <q-card class="hero-panel" flat bordered>
              <q-card-section class="row items-start justify-between">
                <div>
                  <div class="text-subtitle1 text-weight-bold">Snapshot</div>
                  <div class="text-caption text-grey-6">
                    {{ loading ? 'Loading latest data…' : snapshotCaption }}
                  </div>
                </div>

                <q-chip
                  dense
                  square
                  :color="loading ? 'grey-4' : 'positive'"
                  :text-color="loading ? 'grey-8' : 'white'"
                  icon="check_circle"
                >
                  {{ loading ? 'Fetching' : 'Ready' }}
                </q-chip>
              </q-card-section>

              <q-separator />

              <q-card-section class="q-pt-md">
                <div class="kpi-grid">
                  <div class="kpi">
                    <div class="kpi__label">Players</div>
                    <div class="kpi__value">
                      <q-skeleton v-if="loading" type="text" width="70px" />
                      <span v-else>{{ totals.players.toLocaleString() }}</span>
                    </div>
                  </div>

                  <div class="kpi">
                    <div class="kpi__label">Villages</div>
                    <div class="kpi__value">
                      <q-skeleton v-if="loading" type="text" width="90px" />
                      <span v-else>{{ totals.villages.toLocaleString() }}</span>
                    </div>
                  </div>

                  <div class="kpi">
                    <div class="kpi__label">Population</div>
                    <div class="kpi__value">
                      <q-skeleton v-if="loading" type="text" width="120px" />
                      <span v-else>{{ totals.population.toLocaleString() }}</span>
                    </div>
                  </div>

                  <div class="kpi">
                    <div class="kpi__label">Avg / player</div>
                    <div class="kpi__value">
                      <q-skeleton v-if="loading" type="text" width="90px" />
                      <span v-else>{{ totals.avgPop.toLocaleString() }}</span>
                    </div>
                  </div>
                </div>

                <!-- AUTOCOMPLETE PLAYER JUMP -->
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
                    label="Jump to player…"
                    input-debounce="0"
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
                        <q-item-section class="text-grey-7">
                          No matching players
                        </q-item-section>
                      </q-item>
                    </template>

                    <template #option="scope">
                      <q-item v-bind="scope.itemProps">
                        <q-item-section>
                          <q-item-label class="text-weight-medium">
                            {{ scope.opt.label }}
                          </q-item-label>
                          <q-item-label caption>
                            {{ scope.opt.alliance || '—' }}
                            • {{ (scope.opt.villages || 0).toLocaleString() }} villages
                            • {{ (scope.opt.population || 0).toLocaleString() }} pop
                          </q-item-label>
                        </q-item-section>
                      </q-item>
                    </template>
                  </q-select>

                  <div class="text-caption text-grey-6 q-mt-xs">
                    Select from the list — free-typed names are not accepted.
                  </div>
                </div>

                <div class="q-mt-sm row q-col-gutter-sm">
                  <div class="col-12 col-sm-6">
                    <q-btn
                      to="/player"
                      color="primary"
                      unelevated
                      icon="leaderboard"
                      label="Player Analytics"
                      class="full-width"
                    />
                  </div>
                  <div class="col-12 col-sm-6">
                    <q-btn
                      to="/alliance"
                      color="secondary"
                      outline
                      icon="groups"
                      label="Alliances"
                      class="full-width"
                    />
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
  <q-item v-for="i in 6" :key="i" class="q-mb-sm">
    <q-item-section avatar>
      <q-skeleton type="circle" size="30px" />
    </q-item-section>

    <q-item-section>
      <q-item-label>
        <q-skeleton type="text" width="65%" />
      </q-item-label>
      <q-item-label caption>
        <q-skeleton type="text" width="45%" />
      </q-item-label>
    </q-item-section>

    <q-item-section side class="text-right">
      <q-skeleton type="text" width="52px" />
      <div class="q-mt-xs">
        <q-skeleton type="text" width="28px" />
      </div>
    </q-item-section>
  </q-item>
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
    let list = (players.value || []).map(p => ({
      label: p.name,
      value: p.name,
      alliance: p.alliance,
      villages: p.villages,
      population: p.population
    }))

    if (n) {
      list = list.filter(o => (o.label || '').toLowerCase().includes(n))
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
    const playersRes = await api.get('/api/players?limit=1000')
    players.value = Array.isArray(playersRes.data) ? playersRes.data : []

    // initialize options with top-population players (useful before typing)
    playerOptions.value = [...players.value]
      .sort((a, b) => Number(b?.population || 0) - Number(a?.population || 0))
      .slice(0, 30)
      .map(p => ({
        label: p.name,
        value: p.name,
        alliance: p.alliance,
        villages: p.villages,
        population: p.population
      }))

    // Alliances count (best-effort; supports {total} or array)
    try {
      const aRes = await api.get('/api/alliances')
      if (aRes?.data && typeof aRes.data.total === 'number') alliancesCount.value = aRes.data.total
      else if (Array.isArray(aRes.data)) alliancesCount.value = aRes.data.length
    } catch (e) {
      alliancesCount.value = null
    }

    // Regions count (best-effort; supports array or {total})
    try {
      const rRes = await api.get('/api/region')
      if (Array.isArray(rRes.data)) regionsCount.value = rRes.data.length
      else if (rRes?.data && typeof rRes.data.total === 'number') regionsCount.value = rRes.data.total
    } catch (e) {
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
  if (!parts.length) return 'Aggregated from the latest scrape'
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
    const b = buckets.find(x => pop >= x.min && pop <= x.max)
    if (b) b.count += 1
  }

  const maxCount = Math.max(1, ...buckets.map(b => b.count))
  return buckets.map(b => ({
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
  const vs = (players.value || []).map(p => Number(p?.villages || 0)).sort((a, b) => a - b)
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
    const b = buckets.find(x => v >= x.min && v <= x.max)
    if (b) b.count += 1
  }

  const maxCount = Math.max(1, ...buckets.map(b => b.count))
  return buckets.map(b => ({
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
    description:
      'Explore villages, alliances, and regions with filtering and quick navigation.',
    icon: 'map',
    color: 'primary',
    route: '/map'
  },
  {
    title: 'Player Analytics',
    description:
      'Rankings, village counts, population totals, and quick access to detail pages.',
    icon: 'person',
    color: 'secondary',
    route: '/player'
  },
  {
    title: 'Alliance Overview',
    description:
      'Strength, members, and comparative performance across the world.',
    icon: 'groups',
    color: 'accent',
    route: '/alliance'
  },
  {
    title: 'Region Analysis',
    description:
      'Regional snapshots: control patterns, top entities, and distribution.',
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
    r: rand(0.8, 2.2),
    vx: rand(-0.12, 0.12),
    vy: rand(-0.08, 0.08),
    a: rand(0.18, 0.55)
  }))
}

function tick(t) {
  raf = requestAnimationFrame(tick)
  const dt = Math.min(40, t - lastT)
  lastT = t
  if (!ctx) return

  ctx.clearRect(0, 0, w, h)

  for (const p of particles) {
    p.x += p.vx * dt
    p.y += p.vy * dt

    if (p.x < -10) p.x = w + 10
    if (p.x > w + 10) p.x = -10
    if (p.y < -10) p.y = h + 10
    if (p.y > h + 10) p.y = -10

    ctx.globalAlpha = p.a
    ctx.beginPath()
    ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2)
    ctx.fillStyle = '#ffffff'
    ctx.fill()
  }

  ctx.globalAlpha = 0.12
  ctx.strokeStyle = '#ffffff'
  for (let i = 0; i < particles.length; i++) {
    for (let j = i + 1; j < particles.length; j++) {
      const a = particles[i]
      const b = particles[j]
      const dx = a.x - b.x
      const dy = a.y - b.y
      const d2 = dx * dx + dy * dy
      if (d2 < 85 * 85) {
        ctx.lineWidth = 1
        ctx.beginPath()
        ctx.moveTo(a.x, a.y)
        ctx.lineTo(b.x, b.y)
        ctx.stroke()
      }
    }
  }
  ctx.globalAlpha = 1
}

function cleanupCanvas() {
  if (raf) cancelAnimationFrame(raf)
  raf = 0
  ctx = null
  particles = []
}

let ro = null
function installResizeObserver() {
  const c = heroCanvas.value
  if (!c) return
  const parent = c.parentElement
  if (!parent) return

  ro = new ResizeObserver(() => {
    resizeCanvas()
    initParticles()
  })
  ro.observe(parent)

  window.addEventListener('resize', onWinResize, { passive: true })
}

function onWinResize() {
  resizeCanvas()
  initParticles()
}

function uninstallResizeObserver() {
  if (ro) ro.disconnect()
  ro = null
  window.removeEventListener('resize', onWinResize)
}

onMounted(async () => {
  await loadLandingData()
  setupCanvas()
  installResizeObserver()
})

onBeforeUnmount(() => {
  uninstallResizeObserver()
  cleanupCanvas()
})
</script>

<style scoped lang="scss">
.landing-page {
  min-height: 100vh;
}

/* -----------------------------
 * HERO
 * ----------------------------- */
.hero {
  position: relative;
  min-height: 78vh;
  display: flex;
  align-items: center;
  overflow: hidden;
  background: radial-gradient(1200px 600px at 20% 10%, rgba(255, 255, 255, 0.20), transparent 60%),
              radial-gradient(1000px 600px at 85% 35%, rgba(255, 255, 255, 0.14), transparent 58%),
              linear-gradient(135deg, #2b59ff 0%, #7b2ff7 45%, #ffb300 120%);
}

.hero__canvas {
  position: absolute;
  inset: 0;
  z-index: 0;
  opacity: 0.65;
}

.hero__overlay {
  position: absolute;
  inset: 0;
  z-index: 1;
  background: linear-gradient(
    180deg,
    rgba(0, 0, 0, 0.14) 0%,
    rgba(0, 0, 0, 0.22) 55%,
    rgba(0, 0, 0, 0.10) 100%
  );
}

.hero__fade {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 120px;
  z-index: 2;
  background: linear-gradient(180deg, transparent, rgba(255, 255, 255, 1));
}

.hero__content {
  position: relative;
  z-index: 2;
  padding: 4rem 1rem 3rem;
}

.container {
  max-width: 1280px;
  margin: 0 auto;
}

.hero__kicker {
  display: inline-block;
  padding: 0.35rem 0.65rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.16);
  border: 1px solid rgba(255, 255, 255, 0.20);
  color: rgba(255, 255, 255, 0.95);
  font-weight: 600;
  letter-spacing: 0.6px;
  font-size: 0.85rem;
}

.hero__title {
  color: white;
  font-weight: 800;
  font-size: 3.2rem;
  line-height: 1.05;
  margin: 0.9rem 0 0.8rem;

  @media (max-width: 600px) {
    font-size: 2.25rem;
  }
}

.hero__subtitle {
  color: rgba(255, 255, 255, 0.92);
  font-size: 1.2rem;
  line-height: 1.55;
  margin: 0;
  max-width: 52ch;

  @media (max-width: 600px) {
    font-size: 1.05rem;
  }
}

.hero__actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.hero__btn {
  min-width: 190px;
}

.hero-panel {
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.92);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 18px 42px rgba(0, 0, 0, 0.22);
}

.quick-card {
  background: rgba(255, 255, 255, 0.92);
  border-radius: 14px;
}

/* KPI grid inside hero panel */
.kpi-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.9rem;
}

.kpi {
  padding: 0.75rem 0.8rem;
  border-radius: 12px;
  background: #f7f7fb;
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.kpi__label {
  font-size: 0.78rem;
  letter-spacing: 0.5px;
  color: #6b7280;
  text-transform: uppercase;
}

.kpi__value {
  font-size: 1.35rem;
  font-weight: 800;
  margin-top: 0.2rem;
  color: #111827;
}

/* -----------------------------
 * SECTIONS
 * ----------------------------- */
.section {
  padding: 3.5rem 1rem;
  background: white;
}

.section--light {
  background: #f7f8fb;
}

.section-head {
  display: flex;
  gap: 1rem;
  align-items: flex-end;
  justify-content: space-between;
  flex-wrap: wrap;
}

.section-kicker {
  color: #6b7280;
  font-weight: 700;
  letter-spacing: 0.7px;
  text-transform: uppercase;
  font-size: 0.8rem;
}

.section-title {
  margin: 0.25rem 0 0;
  font-size: 2.2rem;
  font-weight: 800;
  color: #0f172a;

  @media (max-width: 600px) {
    font-size: 1.75rem;
  }
}

.section-subtitle {
  margin-top: 0.4rem;
  color: #64748b;
}

/* panels */
.panel {
  border-radius: 16px;
  background: white;
  box-shadow: 0 10px 28px rgba(15, 23, 42, 0.06);
}

/* top list style */
.top-list :deep(.q-item) {
  border-radius: 12px;
}
.top-list :deep(.q-item:hover) {
  background: #f3f4f6;
}

/* bars chart */
.bars {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.bar__head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 0.75rem;
  margin-bottom: 0.35rem;
}

.bar__label {
  font-weight: 700;
  color: #0f172a;
}

.bar__value {
  font-weight: 700;
  color: #64748b;
}

.bar__track {
  height: 10px;
  border-radius: 999px;
  background: #eef0f6;
  overflow: hidden;
}

.bar__fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, rgba(43, 89, 255, 0.9), rgba(255, 179, 0, 0.9));
}

/* mini stats */
.mini-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;

  @media (max-width: 900px) {
    grid-template-columns: repeat(2, 1fr);
  }
}

.mini {
  padding: 0.75rem;
  border-radius: 12px;
  background: #f7f8fb;
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.mini__label {
  font-size: 0.78rem;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 700;
}

.mini__value {
  font-size: 1.25rem;
  font-weight: 800;
  margin-top: 0.25rem;
  color: #0f172a;
}

/* tiny histogram */
.spark {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  height: 60px;
  padding: 10px 12px;
  border-radius: 12px;
  background: #f7f8fb;
  border: 1px solid rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.spark__bar {
  width: 14px;
  border-radius: 10px 10px 3px 3px;
  background: linear-gradient(180deg, rgba(123, 47, 247, 0.9), rgba(43, 89, 255, 0.75));
  transition: transform 0.15s ease;
}

.spark__bar:hover {
  transform: translateY(-2px);
}

/* features grid */
.features-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.25rem;

  @media (max-width: 1100px) {
    grid-template-columns: repeat(2, 1fr);
  }

  @media (max-width: 700px) {
    grid-template-columns: 1fr;
  }
}

.feature {
  border-radius: 16px;
  background: white;
  box-shadow: 0 10px 28px rgba(15, 23, 42, 0.06);
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.feature:hover {
  transform: translateY(-4px);
  box-shadow: 0 18px 36px rgba(15, 23, 42, 0.10);
}

/* CTA */
.cta {
  padding: 4rem 1rem;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.cta-card {
  border-radius: 18px;
  max-width: 820px;
  margin: 0 auto;
  padding: 1.2rem 1rem;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 18px 42px rgba(0, 0, 0, 0.10);
}
</style>
