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
                      <div class="text-subtitle2">Real-time updates</div>
                      <div class="text-caption text-grey-6">Fresh data synced every hour from game servers</div>
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
                  {{ loading ? 'Syncing' : 'Live' }}
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
                            <q-icon name="shield" size="12px" class="q-mr-xs" />
                            {{ scope.opt.alliance || 'No alliance' }}
                            • {{ (scope.opt.villages || 0).toLocaleString() }} villages
                            • {{ (scope.opt.population || 0).toLocaleString() }} pop
                          </q-item-label>
                        </q-item-section>
                      </q-item>
                    </template>
                  </q-select>

                  <div class="text-caption text-grey-6 q-mt-xs">
                    <q-icon name="info" size="14px" class="q-mr-xs" />
                    Type to filter, then select from dropdown
                  </div>
                </div>

                <div class="q-mt-md row q-col-gutter-sm">
                  <div class="col-12 col-sm-6">
                    <q-btn
                      to="/player"
                      color="primary"
                      unelevated
                      icon="leaderboard"
                      label="Player Rankings"
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
            <div class="section-kicker">
              <q-icon name="insights" size="14px" class="q-mr-xs" />
              Game Intelligence
            </div>
            <h2 class="section-title">Power dynamics at your fingertips</h2>
            <div class="section-subtitle">
              Real-time leaderboards, population distribution analysis, and expansion velocity metrics. See who's rising,
              who's stagnating, and where opportunities lie.
            </div>
          </div>

          <div class="row items-center q-gutter-sm">
            <q-btn to="/map" color="primary" outline rounded icon="map" label="Open Map" />
            <q-btn to="/region" color="primary" flat rounded icon="terrain" label="Regions" />
          </div>
        </div>

        <div class="row q-col-gutter-lg q-mt-md">
          <!-- LEFT: Top Players -->
          <div class="col-12 col-md-5">
            <q-card flat bordered class="panel">
              <q-card-section class="row items-center justify-between">
                <div class="text-subtitle1 text-weight-bold">
                  <q-icon name="emoji_events" size="20px" class="q-mr-xs text-amber-7" />
                  Top Players
                </div>
                <q-chip dense square color="grey-2" text-color="grey-8" icon="sort">by population</q-chip>
              </q-card-section>

              <q-separator />

              <q-card-section>
                <div v-if="loading">
                  <q-item v-for="i in 6" :key="i" class="q-mb-sm">
                    <q-item-section avatar><q-skeleton type="circle" size="30px" /></q-item-section>
                    <q-item-section>
                      <q-item-label><q-skeleton type="text" width="65%" /></q-item-label>
                      <q-item-label caption><q-skeleton type="text" width="45%" /></q-item-label>
                    </q-item-section>
                    <q-item-section side class="text-right">
                      <q-skeleton type="text" width="52px" />
                      <div class="q-mt-xs"><q-skeleton type="text" width="28px" /></div>
                    </q-item-section>
                  </q-item>
                </div>

                <q-list v-else dense padding class="top-list">
                  <q-item v-for="(p, idx) in topPlayers" :key="p.name" clickable @click="goPlayer(p.name)">
                    <q-item-section avatar>
                      <q-avatar
                        size="32px"
                        :color="idx < 3 ? 'amber-7' : 'grey-3'"
                        :text-color="idx < 3 ? 'white' : 'grey-8'"
                      >
                        <q-icon v-if="idx === 0" name="military_tech" size="18px" />
                        <span v-else>{{ idx + 1 }}</span>
                      </q-avatar>
                    </q-item-section>

                    <q-item-section>
                      <q-item-label class="text-weight-medium">{{ p.name }}</q-item-label>
                      <q-item-label caption>
                        <q-icon name="shield" size="12px" class="q-mr-xs" />
                        {{ p.alliance || 'No alliance' }}
                        <span class="q-mx-xs">•</span>
                        <q-icon name="location_city" size="12px" class="q-mr-xs" />
                        {{ (p.villages || 0).toLocaleString() }} villages
                      </q-item-label>
                    </q-item-section>

                    <q-item-section side class="text-right">
                      <div class="text-weight-bold text-primary">{{ (p.population || 0).toLocaleString() }}</div>
                      <div class="text-caption text-grey-6">population</div>
                    </q-item-section>
                  </q-item>
                </q-list>

                <q-separator class="q-my-sm" />
                <q-btn
                  to="/player"
                  color="primary"
                  flat
                  icon-right="arrow_forward"
                  label="View full rankings & analytics"
                  class="full-width"
                />
              </q-card-section>
            </q-card>
          </div>

          <!-- RIGHT -->
          <div class="col-12 col-md-7">
            <div class="row q-col-gutter-lg">
              <!-- Population Distribution -->

              <!-- Top Alliances -->
              <div class="col-12">
                <q-card flat bordered class="panel">
                  <q-card-section class="row items-center justify-between">
                    <div class="text-subtitle1 text-weight-bold">
                      <q-icon name="groups" size="20px" class="q-mr-xs text-purple-7" />
                      Top Alliances
                    </div>
                    <q-chip dense square color="grey-2" text-color="grey-8" icon="sort">by total pop</q-chip>
                  </q-card-section>

                  <q-separator />

                  <q-card-section>
                    <div v-if="loading">
                      <q-item v-for="i in 6" :key="i" class="q-mb-sm">
                        <q-item-section avatar><q-skeleton type="circle" size="30px" /></q-item-section>
                        <q-item-section>
                          <q-item-label><q-skeleton type="text" width="55%" /></q-item-label>
                          <q-item-label caption><q-skeleton type="text" width="40%" /></q-item-label>
                        </q-item-section>
                        <q-item-section side class="text-right">
                          <q-skeleton type="text" width="62px" />
                          <div class="q-mt-xs"><q-skeleton type="text" width="34px" /></div>
                        </q-item-section>
                      </q-item>
                    </div>

                    <q-list v-else dense padding class="top-list">
                      <q-item v-for="(a, idx) in topAlliances" :key="a.tag" clickable @click="goAlliance(a.tag)">
                        <q-item-section avatar>
                          <q-avatar
                            size="32px"
                            :color="idx < 3 ? 'purple-7' : 'grey-3'"
                            :text-color="idx < 3 ? 'white' : 'grey-8'"
                          >
                            <q-icon v-if="idx === 0" name="workspace_premium" size="18px" />
                            <span v-else>{{ idx + 1 }}</span>
                          </q-avatar>
                        </q-item-section>

                        <q-item-section>
                          <q-item-label class="text-weight-medium">
                            {{ a.tag }}
                            <span v-if="a.name" class="text-caption text-grey-6"> — {{ a.name }}</span>
                          </q-item-label>
                          <q-item-label caption>
                            <q-icon name="people" size="12px" class="q-mr-xs" />
                            {{ (a.players || 0).toLocaleString() }} members
                            <span class="q-mx-xs">•</span>
                            <q-icon name="location_city" size="12px" class="q-mr-xs" />
                            {{ (a.villages || 0).toLocaleString() }} villages
                          </q-item-label>
                        </q-item-section>

                        <q-item-section side class="text-right">
                          <div class="text-weight-bold text-primary">{{ (a.population || 0).toLocaleString() }}</div>
                          <div class="text-caption text-grey-6">population</div>
                        </q-item-section>
                      </q-item>
                    </q-list>

                    <q-separator class="q-my-sm" />
                    <q-btn
                      to="/alliance"
                      color="primary"
                      flat
                      icon-right="arrow_forward"
                      label="View all alliances"
                      class="full-width"
                    />
                  </q-card-section>
                </q-card>
              </div>

              <div class="col-12">
                <q-card flat bordered class="panel">
                  <q-card-section class="row items-center justify-between">
                    <div>
                      <div class="text-subtitle1 text-weight-bold">
                        <q-icon name="bar_chart" size="20px" class="q-mr-xs text-blue-7" />
                        Population Distribution
                      </div>
                      <div class="text-caption text-grey-6">Player power tiers across the server</div>
                    </div>

                    <q-chip dense square color="grey-2" text-color="grey-8" icon="analytics">by range</q-chip>
                  </q-card-section>

                  <q-separator />

                  <q-card-section>
                    <div v-if="loading" class="row q-col-gutter-sm">
                      <div class="col-12"><q-skeleton type="rect" height="160px" /></div>
                    </div>

                    <div v-else class="bars">
                      <div
                        v-for="b in popBuckets"
                        :key="b.label"
                        class="bar"
                        :title="`${b.label}: ${b.count.toLocaleString()} players (${Math.round((b.count / Math.max(1, totals.players)) * 100)}% of total)`"
                      >
                        <div class="bar__head">
                          <div class="bar__label">
                            <q-icon name="group" size="14px" class="q-mr-xs" />
                            {{ b.label }}
                          </div>
                          <div class="bar__value">
                            {{ b.count.toLocaleString() }}
                            <span class="text-caption text-grey-6 q-ml-xs">
                              ({{ Math.round((b.count / Math.max(1, totals.players)) * 100) }}%)
                            </span>
                          </div>
                        </div>
                        <div class="bar__track">
                          <div class="bar__fill" :style="{ width: `${b.pct}%` }"></div>
                        </div>
                      </div>
                    </div>

                    <div v-if="!loading" class="q-mt-md">
                      <q-banner dense rounded class="bg-blue-1 text-blue-9">
                        <template #avatar>
                          <q-icon name="lightbulb" color="blue-7" />
                        </template>
                        <span class="text-caption">
                          Most players ({{ mostPopBucketPct }}%) are in the {{ mostPopBucketLabel }} range
                        </span>
                      </q-banner>
                    </div>
                  </q-card-section>
                </q-card>
              </div>

              <!-- Expansion Metrics -->
              <div class="col-12">
                <q-card flat bordered class="panel">
                  <q-card-section class="row items-center justify-between">
                    <div>
                      <div class="text-subtitle1 text-weight-bold">
                        <q-icon name="timeline" size="20px" class="q-mr-xs text-green-7" />
                        Expansion Metrics
                      </div>
                      <div class="text-caption text-grey-6">Village count distribution reveals expansion patterns</div>
                    </div>

                    <q-chip dense square color="grey-2" text-color="grey-8" icon="insights">statistics</q-chip>
                  </q-card-section>

                  <q-separator />

                  <q-card-section>
                    <div v-if="loading">
                      <q-skeleton type="rect" height="140px" />
                    </div>

                    <div v-else class="mini-grid">
                      <div class="mini">
                        <div class="mini__label">
                          <q-icon name="show_chart" size="12px" class="q-mr-xs" />
                          Median
                        </div>
                        <div class="mini__value">{{ villagesStats.median.toLocaleString() }}</div>
                        <div class="text-caption text-grey-6 q-mt-xs">villages</div>
                      </div>
                      <div class="mini">
                        <div class="mini__label">
                          <q-icon name="functions" size="12px" class="q-mr-xs" />
                          Average
                        </div>
                        <div class="mini__value">{{ villagesStats.avg.toLocaleString() }}</div>
                        <div class="text-caption text-grey-6 q-mt-xs">villages</div>
                      </div>
                      <div class="mini">
                        <div class="mini__label">
                          <q-icon name="trending_up" size="12px" class="q-mr-xs" />
                          90th %
                        </div>
                        <div class="mini__value">{{ villagesStats.p90.toLocaleString() }}</div>
                        <div class="text-caption text-grey-6 q-mt-xs">elite tier</div>
                      </div>
                      <div class="mini">
                        <div class="mini__label">
                          <q-icon name="workspace_premium" size="12px" class="q-mr-xs" />
                          Maximum
                        </div>
                        <div class="mini__value">{{ villagesStats.max.toLocaleString() }}</div>
                        <div class="text-caption text-grey-6 q-mt-xs">top player</div>
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
                        <q-icon name="info" size="14px" class="q-mr-xs" />
                        Distribution: {{ villagesHistogram.map((h) => h.label).join(' • ') }}
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
            <div class="section-kicker">
              <q-icon name="extension" size="14px" class="q-mr-xs" />
              Platform Features
            </div>
            <h2 class="section-title">Everything you need to dominate</h2>
            <div class="section-subtitle">
              Comprehensive tools for scouting, planning, and executing your strategy. From macro-level alliance warfare
              to micro village management.
            </div>
          </div>
        </div>

        <div class="features-grid q-mt-md">
          <q-card v-for="f in features" :key="f.title" flat bordered class="feature">
            <q-card-section>
              <div class="row items-start no-wrap">
                <q-avatar size="48px" :color="f.color" text-color="white" class="q-mr-md">
                  <q-icon :name="f.icon" size="28px" />
                </q-avatar>
                <div class="col">
                  <div class="text-h6 q-mb-xs">{{ f.title }}</div>
                  <div class="text-body2 text-grey-7">{{ f.description }}</div>
                  <div class="q-mt-sm">
                    <q-chip
                      v-for="tag in f.tags"
                      :key="tag"
                      dense
                      size="sm"
                      color="grey-2"
                      text-color="grey-8"
                      class="q-mr-xs q-mb-xs"
                    >
                      {{ tag }}
                    </q-chip>
                  </div>
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
                :label="f.actionLabel || 'Explore'"
              />
            </q-card-actions>
          </q-card>
        </div>
      </div>
    </section>

    <!-- WHY CHOOSE US -->
    <section class="section section--light">
      <div class="container">
        <div class="section-head">
          <div>
            <div class="section-kicker">
              <q-icon name="verified" size="14px" class="q-mr-xs" />
              Why Our Platform
            </div>
            <h2 class="section-title">Built by players, for players</h2>
            <div class="section-subtitle">
              We understand the game because we play it. Every feature is designed to solve real strategic challenges.
            </div>
          </div>
        </div>

        <div class="row q-col-gutter-lg q-mt-md">
          <div class="col-12 col-md-4" v-for="benefit in benefits" :key="benefit.title">
            <q-card flat bordered class="benefit-card">
              <q-card-section>
                <q-icon :name="benefit.icon" size="42px" :color="benefit.color" />
                <div class="text-h6 q-mt-md q-mb-sm">{{ benefit.title }}</div>
                <div class="text-body2 text-grey-7">{{ benefit.description }}</div>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="cta">
      <div class="container">
        <q-card flat bordered class="cta-card">
          <q-card-section class="text-center">
            <q-icon name="rocket_launch" size="48px" color="primary" class="q-mb-md" />
            <div class="text-h4 text-weight-bold">Ready to gain the edge?</div>
            <div class="text-body1 text-grey-7 q-mt-sm q-mb-md">
              Join thousands of players using our analytics platform to make smarter decisions, spot threats early, and
              identify opportunities before your competitors.
            </div>

            <div class="row justify-center q-gutter-md q-mt-lg">
              <q-btn to="/map" color="primary" unelevated rounded size="lg" icon="map" label="Start Exploring" />
              <q-btn to="/player" color="secondary" outline rounded size="lg" icon="person" label="View Rankings" />
            </div>

            <div class="q-mt-lg text-caption text-grey-6">
              <q-icon name="update" size="14px" class="q-mr-xs" />
              Data updates hourly • Free to use • No registration required
            </div>
          </q-card-section>
        </q-card>
      </div>
    </section>
  </q-page>
</template>
<script setup lang="ts">
  import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
  import { useRouter } from 'vue-router'
  import { api } from 'boot/axios'
  
  type PlayerRow = {
    name: string
  
    // common variants we might get from backend
    alliance?: string | null
    alliance_tag?: string | null
    allianceTag?: string | null
    alliance_id?: number | string | null
    allianceId?: number | string | null
    tag?: string | null
  
    villages?: number | null
    population?: number | null
  }
  
  type PlayerOption = {
    label: string
    value: string
    alliance?: string | null
    villages?: number | null
    population?: number | null
  }
  
  type AllianceRow = {
    // common variants
    id?: number | string | null
    alliance_id?: number | string | null
  
    tag: string
    name?: string | null
  
    players?: number | null
    villages?: number | null
    population?: number | null
  
    member_count?: number | null
    villages_count?: number | null
    total_population?: number | null
    total_pop?: number | null
  }
  
  const router = useRouter()
  
  const loading = ref(false)
  const players = ref<PlayerRow[]>([])
  const alliances = ref<AllianceRow[]>([])
  const allianceTagById = ref<Record<string, string>>({})
  
  const alliancesCount = ref<number | null>(null)
  const regionsCount = ref<number | null>(null)
  
  const selectedPlayer = ref<PlayerOption | null>(null)
  const playerOptions = ref<PlayerOption[]>([])
  const optionsLoading = ref(false)
  
  const playerAllianceByName = ref<Record<string, string>>({})

  function toKey(v: unknown): string {
    return (v ?? '').toString().trim()
  }
  
  function normalizeAllianceTag(p: PlayerRow): string | null {
  const direct =
    p.alliance_tag ??
    p.allianceTag ??
    p.tag ??
    (typeof p.alliance === 'string' ? p.alliance : null) ??
    null

  const d = toKey(direct)
  if (d) return d

  // fallback: hydrated from /api/player/:name/villages for top players
  const byName = playerAllianceByName.value[toKey(p.name)]
  if (byName) return byName

  // optional: id->tag fallback if you have it
  const aid = toKey(p.alliance_id ?? p.allianceId ?? '')
  if (aid && allianceTagById.value[aid]) return allianceTagById.value[aid]

  return null
}

  
  function goPlayer(name: string) {
    const n = (name || '').trim()
    if (!n) return
    router.push({ name: 'player-detail', params: { name: n } })
  }
  
  function goAlliance(tag: string) {
    const t = (tag || '').trim()
    if (!t) return
    router.push({ name: 'alliance-detail', params: { tag: t } })
  }
  
  function onSelectedPlayer(val: PlayerOption | null) {
    if (!val?.value) return
    goPlayer(val.value)
  }
  
  function filterPlayers(needle: string, update: (cb: () => void) => void) {
    update(() => {
      optionsLoading.value = true
      const n = (needle || '').trim().toLowerCase()
  
      let list: PlayerOption[] = (players.value || []).map((p) => ({
        label: p.name,
        value: p.name,
        alliance: normalizeAllianceTag(p),
        villages: p.villages ?? 0,
        population: p.population ?? 0
      }))
  
      if (n) list = list.filter((o) => (o.label || '').toLowerCase().includes(n))
      list.sort((a, b) => Number(b.population || 0) - Number(a.population || 0))
  
      playerOptions.value = list.slice(0, 50)
      optionsLoading.value = false
    })
  }
  
  function buildAllianceIdTagIndex(list: AllianceRow[]) {
    const idx: Record<string, string> = {}
    for (const a of list || []) {
      const tag = toKey(a.tag)
      if (!tag) continue
  
      const id1 = toKey(a.id)
      const id2 = toKey(a.alliance_id)
      if (id1) idx[id1] = tag
      if (id2) idx[id2] = tag
    }
    allianceTagById.value = idx
  }
  
  async function loadLandingData() {
    loading.value = true
    try {
      // 1) Alliances (first) -> build id->tag mapping before we normalize player alliance tags
      try {
        const aListRes = await api.get('/api/alliances?limit=2000')
        const list = Array.isArray(aListRes.data)
          ? (aListRes.data as AllianceRow[])
          : Array.isArray((aListRes.data as any)?.data)
            ? ((aListRes.data as any).data as AllianceRow[])
            : []
  
        alliances.value = list
        buildAllianceIdTagIndex(list)
      } catch {
        alliances.value = []
        allianceTagById.value = {}
      }
  
      // 2) Players
      const playersRes = await api.get('/api/players?limit=2000')
      players.value = Array.isArray(playersRes.data) ? (playersRes.data as PlayerRow[]) : []
      const topNames = [...players.value]
  .sort((a, b) => Number(b?.population || 0) - Number(a?.population || 0))
  .slice(0, 12)
  .map((p) => p.name)

await hydrateTopPlayerAlliances(topNames)
      // 3) Quick select options
      playerOptions.value = [...players.value]
        .sort((a, b) => Number(b?.population || 0) - Number(a?.population || 0))
        .slice(0, 50)
        .map((p) => ({
          label: p.name,
          value: p.name,
          alliance: normalizeAllianceTag(p),
          villages: p.villages ?? 0,
          population: p.population ?? 0
        }))
  
      // 4) Alliances count (supports {total} or list)
      try {
        const aRes = await api.get('/api/alliances')
        if ((aRes as any)?.data && typeof (aRes as any).data.total === 'number') alliancesCount.value = (aRes as any).data.total
        else if (Array.isArray((aRes as any).data)) alliancesCount.value = (aRes as any).data.length
        else alliancesCount.value = null
      } catch {
        alliancesCount.value = null
      }
  
      // 5) Regions count
      try {
        const rRes = await api.get('/api/region')
        if (Array.isArray((rRes as any).data)) regionsCount.value = (rRes as any).data.length
        else if ((rRes as any)?.data && typeof (rRes as any).data.total === 'number') regionsCount.value = (rRes as any).data.total
        else regionsCount.value = null
      } catch {
        regionsCount.value = null
      }
    } finally {
      loading.value = false
    }
  }
  
  async function hydrateTopPlayerAlliances(names: string[]) {
  const out: Record<string, string> = { ...playerAllianceByName.value }

  await Promise.allSettled(
    names.map(async (name) => {
      const n = (name || '').trim()
      if (!n || out[n]) return

      try {
        const res = await api.get(`/api/player/${encodeURIComponent(n)}/villages`)
        const vs = res.data?.villages || []
        const tag = (vs?.[0]?.alliance_tag ?? vs?.[0]?.alliance ?? '').toString().trim()
        if (tag) out[n] = tag
      } catch {
        // ignore; we'll just show "No alliance"
      }
    })
  )

  playerAllianceByName.value = out
}


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
    return { players: playersCount, villages, population, avgPop }
  })
  
  const snapshotCaption = computed(() => {
    const a = alliancesCount.value
    const r = regionsCount.value
    const parts: string[] = []
    if (typeof a === 'number') parts.push(`${a.toLocaleString()} alliances`)
    if (typeof r === 'number') parts.push(`${r.toLocaleString()} regions`)
    if (!parts.length) return 'Updated hourly from live servers'
    return `${parts.join(' • ')} tracked`
  })
  
  const topPlayers = computed(() => {
    return [...(players.value || [])]
      .sort((a, b) => Number(b?.population || 0) - Number(a?.population || 0))
      .slice(0, 8)
      .map((p) => ({
        ...p,
        alliance: normalizeAllianceTag(p)
      }))
  })
  
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
    return buckets.map((b) => ({ ...b, pct: Math.round((b.count / maxCount) * 100) }))
  })
  
  const mostPopBucket = computed(() => {
    const list = popBuckets.value
    if (!list.length) return { label: '—', count: 0 }
    return list.reduce((best, cur) => (cur.count > best.count ? cur : best), list[0])
  })
  const mostPopBucketLabel = computed(() => mostPopBucket.value.label)
  const mostPopBucketPct = computed(() => {
    const total = Math.max(1, totals.value.players)
    return Math.round((mostPopBucket.value.count / total) * 100)
  })
  
  function percentile(sorted: number[], p: number) {
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
    return buckets.map((b) => ({ ...b, pct: Math.round((b.count / maxCount) * 100) }))
  })
  
  const topAlliances = computed(() => {
  const fromEndpoint = (alliances.value || [])
    .map((a) => ({
      tag: toKey(a.tag),
      name: a.name ?? null,
      players: Number(a.players ?? a.member_count ?? 0),
      villages: Number(a.villages ?? a.villages_count ?? 0),
      population: Number(a.population ?? a.total_population ?? a.total_pop ?? 0)
    }))
    .filter((a) => !!a.tag)

  const usable = fromEndpoint.filter((a) => a.population > 0 || a.players > 0 || a.villages > 0)
  if (usable.length) return usable.sort((a, b) => b.population - a.population).slice(0, 8)

  // fallback: aggregate from players by alliance tag
  const m = new Map<
    string,
    { tag: string; name: string | null; players: number; villages: number; population: number }
  >()

  for (const p of players.value || []) {
    const tag = normalizeAllianceTag(p)
    if (!tag) continue
    const cur = m.get(tag) || { tag, name: null, players: 0, villages: 0, population: 0 }
    cur.players += 1
    cur.villages += Number(p.villages || 0)
    cur.population += Number(p.population || 0)
    m.set(tag, cur)
  }

  return [...m.values()].sort((a, b) => b.population - a.population).slice(0, 8)
})

  
  const features = [
    {
      title: 'Interactive World Map',
      description:
        'Visualize the entire game world with real-time village positions, alliance territories, and strategic chokepoints. Filter by player, alliance, or region.',
      icon: 'map',
      color: 'primary',
      route: '/map',
      actionLabel: 'Open Map',
      tags: ['Real-time', 'Filters', 'Territory view']
    },
    {
      title: 'Player Intelligence',
      description:
        'Deep-dive analytics on any player: growth trends, village distribution, alliance history, and comparative rankings. Track rivals and allies.',
      icon: 'person_search',
      color: 'secondary',
      route: '/player',
      actionLabel: 'View Players',
      tags: ['Rankings', 'Trends', 'Comparisons']
    },
    {
      title: 'Alliance Power Index',
      description:
        'Comprehensive alliance metrics: total strength, member activity, territorial control, and growth velocity. Identify dominant coalitions.',
      icon: 'groups',
      color: 'accent',
      route: '/alliance',
      actionLabel: 'Browse Alliances',
      tags: ['Strength metrics', 'Members', 'Territory']
    },
    {
      title: 'Regional Analysis',
      description:
        'Break down the map by regions to identify power vacuums, contested zones, and expansion opportunities. See who controls what.',
      icon: 'terrain',
      color: 'positive',
      route: '/region',
      actionLabel: 'View Regions',
      tags: ['Control maps', 'Opportunities', 'Hotspots']
    }
  ] as const
  
  const benefits = [
    {
      title: 'Always Up-to-Date',
      description:
        'Our scraper pulls fresh data from game servers every hour, ensuring you always have the latest intelligence for critical decisions.',
      icon: 'update',
      color: 'blue-7'
    },
    {
      title: 'Lightning Fast Search',
      description:
        'Find any player, alliance, or village in milliseconds. Optimized database queries mean zero lag, even with massive datasets.',
      icon: 'bolt',
      color: 'amber-7'
    },
    {
      title: 'Strategic Edge',
      description:
        'Spot expansion patterns, identify weakening players, track alliance shifts, and discover undefended territories before anyone else.',
      icon: 'psychology',
      color: 'purple-7'
    }
  ] as const
  
  // Hero canvas particles
  const heroCanvas = ref<HTMLCanvasElement | null>(null)
  
  let raf = 0
  let ctx: CanvasRenderingContext2D | null = null
  let w = 0
  let h = 0
  let particles: Array<{ x: number; y: number; r: number; vx: number; vy: number; a: number }> = []
  let lastT = 0
  let ro: ResizeObserver | null = null
  
  function rand(min: number, max: number) {
    return Math.random() * (max - min) + min
  }
  
  function resizeCanvas() {
    const c = heroCanvas.value
    if (!c) return
    const parent = c.parentElement
    if (!parent) return
  
    const rect = parent.getBoundingClientRect()
    w = Math.max(1, Math.floor(rect.width))
    h = Math.max(1, Math.floor(rect.height))
  
    const dpr = Math.max(1, window.devicePixelRatio || 1)
    c.width = Math.floor(w * dpr)
    c.height = Math.floor(h * dpr)
    c.style.width = `${w}px`
    c.style.height = `${h}px`
  
    if (ctx) ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  }
  
  function initParticles() {
    const count = Math.min(120, Math.max(70, Math.floor((w * h) / 16000)))
    particles = Array.from({ length: count }).map(() => ({
      x: rand(0, w),
      y: rand(0, h),
      r: rand(0.9, 2.4),
      vx: rand(-0.14, 0.14),
      vy: rand(-0.09, 0.09),
      a: rand(0.2, 0.6)
    }))
  }
  
  function tick(t: number) {
    raf = window.requestAnimationFrame(tick)
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
  
    ctx.globalAlpha = 0.13
    ctx.strokeStyle = '#ffffff'
  
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const a = particles[i]
        const b = particles[j]
        const dx = a.x - b.x
        const dy = a.y - b.y
        const d2 = dx * dx + dy * dy
        if (d2 < 90 * 90) {
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
  
  function setupCanvas() {
    const c = heroCanvas.value
    if (!c) return
    ctx = c.getContext('2d', { alpha: true })
    if (!ctx) return
    resizeCanvas()
    initParticles()
    lastT = performance.now()
    tick(lastT)
  }
  
  function cleanupCanvas() {
    if (raf) window.cancelAnimationFrame(raf)
    raf = 0
    ctx = null
    particles = []
  }
  
  function onWinResize() {
    resizeCanvas()
    initParticles()
  }
  
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

    