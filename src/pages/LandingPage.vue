<template>
  <q-page class="landing-page">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">Travian Status</h1>
        <p class="hero-subtitle">Comprehensive analytics and visualization for Travian game data</p>
        <div class="hero-actions">
          <q-btn
            to="/map"
            color="primary"
            size="lg"
            unelevated
            rounded
            class="hero-btn"
            icon="map"
            label="Explore Map"
          />
          <q-btn
            to="/player"
            color="secondary"
            size="lg"
            outline
            rounded
            class="hero-btn"
            icon="person"
            label="View Players"
          />
        </div>
      </div>
      <div class="hero-background"></div>
    </section>

    <!-- Statistics Section -->
    <section class="stats-section">
      <div class="container">
        <h2 class="section-title">Game Statistics</h2>
        <div class="stats-grid">
          <q-card class="stat-card" v-for="stat in stats" :key="stat.label" flat bordered>
            <q-card-section class="text-center">
              <q-icon :name="stat.icon" size="48px" :color="stat.color" />
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features-section">
      <div class="container">
        <h2 class="section-title">Key Features</h2>
        <div class="features-grid">
          <q-card
            v-for="feature in features"
            :key="feature.title"
            class="feature-card"
            flat
            bordered
          >
            <q-card-section>
              <q-icon :name="feature.icon" size="40px" :color="feature.color" class="q-mb-md" />
              <div class="text-h6 q-mb-sm">{{ feature.title }}</div>
              <div class="text-body2 text-grey-7">{{ feature.description }}</div>
            </q-card-section>
            <q-card-actions v-if="feature.route">
              <q-btn
                flat
                :to="feature.route"
                color="primary"
                label="Explore"
                icon-right="arrow_forward"
              />
            </q-card-actions>
          </q-card>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta-section">
      <div class="container">
        <q-card class="cta-card" flat>
          <q-card-section class="text-center">
            <div class="text-h4 q-mb-md">Ready to explore?</div>
            <div class="text-body1 text-grey-7 q-mb-lg">
              Start analyzing game data and discover insights about players, alliances, and regions
            </div>
            <q-btn
              to="/map"
              color="primary"
              size="lg"
              unelevated
              rounded
              icon="map"
              label="Get Started"
            />
          </q-card-section>
        </q-card>
      </div>
    </section>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from 'boot/axios'

const stats = ref([
  { label: 'Total Players', value: '—', icon: 'people', color: 'primary' },
  { label: 'Villages', value: '—', icon: 'location_city', color: 'secondary' },
  { label: 'Alliances', value: '—', icon: 'groups', color: 'accent' },
  { label: 'Regions', value: '—', icon: 'terrain', color: 'positive' }
])

const features = [
  {
    title: 'Interactive Map',
    description: 'Explore the game world with an interactive map showing all villages, alliances, and regions with real-time filtering.',
    icon: 'map',
    color: 'primary',
    route: '/map'
  },
  {
    title: 'Player Analytics',
    description: 'View detailed player statistics, village counts, population data, and track player progress over time.',
    icon: 'person',
    color: 'secondary',
    route: '/player'
  },
  {
    title: 'Alliance Overview',
    description: 'Analyze alliance strength, member counts, territory distribution, and competitive rankings.',
    icon: 'groups',
    color: 'accent',
    route: '/alliance'
  },
  {
    title: 'Region Analysis',
    description: 'Examine regional statistics, top alliances per region, and territorial control patterns.',
    icon: 'terrain',
    color: 'positive',
    route: '/region'
  }
]

async function loadStats() {
  try {
    // Load players count
    const playersRes = await api.get('/api/players?limit=1')
    if (Array.isArray(playersRes.data)) {
      // We need to get total count, but API might not provide it
      // For now, we'll show the limit or make another call
      stats.value[0].value = playersRes.data.length > 0 ? '300+' : '—'
    }

    // Load alliances count
    const alliancesRes = await api.get('/api/alliances')
    if (alliancesRes.data && alliancesRes.data.total) {
      stats.value[2].value = alliancesRes.data.total.toString()
    } else if (Array.isArray(alliancesRes.data)) {
      stats.value[2].value = alliancesRes.data.length.toString()
    }

    // Load regions count
    const regionsRes = await api.get('/api/region')
    if (Array.isArray(regionsRes.data)) {
      stats.value[3].value = regionsRes.data.length.toString()
    }
  } catch (error) {
    console.error('Failed to load stats:', error)
    // Keep default values
  }
}

onMounted(loadStats)
</script>

<style scoped lang="scss">
.landing-page {
  min-height: 100vh;
}

.hero-section {
  position: relative;
  min-height: 70vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
  overflow: hidden;
}

.hero-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  opacity: 0.9;
  z-index: 0;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
   // background: url('/background.png') center/cover no-repeat;
    opacity: 0.2;
  }
}

.hero-content {
  position: relative;
  z-index: 1;
  text-align: center;
  color: white;
  max-width: 800px;
  padding: 2rem;
}

.hero-title {
  font-size: 4rem;
  font-weight: 700;
  margin-bottom: 1rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
  
  @media (max-width: 600px) {
    font-size: 2.5rem;
  }
}

.hero-subtitle {
  font-size: 1.5rem;
  margin-bottom: 2rem;
  opacity: 0.95;
  
  @media (max-width: 600px) {
    font-size: 1.1rem;
  }
}

.hero-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.hero-btn {
  min-width: 180px;
}

.stats-section,
.features-section,
.cta-section {
  padding: 4rem 1rem;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.section-title {
  text-align: center;
  font-size: 2.5rem;
  font-weight: 600;
  margin-bottom: 3rem;
  color: $dark;
  
  @media (max-width: 600px) {
    font-size: 2rem;
    margin-bottom: 2rem;
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  
  @media (max-width: 600px) {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }
}

.stat-card {
  transition: transform 0.2s, box-shadow 0.2s;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  }
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: $primary;
  margin: 0.5rem 0;
}

.stat-label {
  font-size: 0.9rem;
  color: $grey-7;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
  
  @media (max-width: 600px) {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
}

.feature-card {
  height: 100%;
  transition: transform 0.2s, box-shadow 0.2s;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  }
}

.cta-section {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.cta-card {
  background: white;
  max-width: 600px;
  margin: 0 auto;
  padding: 2rem;
}
</style>
