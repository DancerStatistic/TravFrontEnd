<template>
  <q-layout view="hHh Lpr lFf">
    <q-header elevated class="bg-primary text-white">
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          @click="leftDrawerOpen = !leftDrawerOpen"
          class="q-mr-sm"
        />

        <q-toolbar-title class="toolbar-title">
          <router-link to="/" class="brand-link">
            <q-icon name="map" size="28px" class="q-mr-sm" />
            <span class="brand-text">Travian Status</span>
          </router-link>
        </q-toolbar-title>

        <q-space />

        <!-- Desktop Navigation -->
        <div class="desktop-nav gt-sm">
          <q-btn
            flat
            dense
            :to="{ name: 'landing' }"
            label="Home"
            icon="home"
            class="nav-btn"
            :class="{ 'nav-active': $route.name === 'landing' }"
          />
          <q-btn
            flat
            dense
            :to="{ name: 'global-map' }"
            label="Map"
            icon="map"
            class="nav-btn"
            :class="{ 'nav-active': $route.name === 'global-map' }"
          />
          <!-- Regions disabled for now -->
          <!--
          <q-btn
            flat
            dense
            :to="{ name: 'region-list' }"
            label="Regions"
            icon="terrain"
            class="nav-btn"
            :class="{ 'nav-active': $route.name === 'region-list' || $route.name === 'region-detail' }"
          />
          -->
          <q-btn
            flat
            dense
            :to="{ name: 'player-list' }"
            label="Players"
            icon="person"
            class="nav-btn"
            :class="{ 'nav-active': $route.name === 'player-list' || $route.name === 'player-detail' }"
          />
          <q-btn
            flat
            dense
            :to="{ name: 'alliance-list' }"
            label="Alliances"
            icon="groups"
            class="nav-btn"
            :class="{ 'nav-active': $route.name === 'alliance-list' || $route.name === 'alliance-detail' }"
          />
        </div>
      </q-toolbar>
    </q-header>

    <!-- Mobile Drawer -->
    <q-drawer
      v-model="leftDrawerOpen"
      show-if-above
      bordered
      class="bg-grey-1"
      :width="280"
      :breakpoint="1024"
    >
      <q-list>
        <q-item-label header class="text-grey-8">
          <div class="row items-center q-pa-sm">
            <q-icon name="map" size="24px" color="primary" class="q-mr-sm" />
            <span class="text-h6">Navigation</span>
          </div>
        </q-item-label>

        <q-item
          clickable
          v-ripple
          :to="{ name: 'landing' }"
          :active="$route.name === 'landing'"
          active-class="bg-primary text-white"
        >
          <q-item-section avatar>
            <q-icon name="home" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Home</q-item-label>
          </q-item-section>
        </q-item>

        <q-item
          clickable
          v-ripple
          :to="{ name: 'global-map' }"
          :active="$route.name === 'global-map'"
          active-class="bg-primary text-white"
        >
          <q-item-section avatar>
            <q-icon name="map" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Interactive Map</q-item-label>
          </q-item-section>
        </q-item>

        <q-item
  clickable
  v-ripple
  :to="{ name: 'trade-route' }"
  :active="['trade-route', 'trade-route-alias'].includes($route.name)"
  active-class="bg-primary text-white"
>
  <q-item-section avatar>
    <q-icon name="swap_horiz" />
  </q-item-section>
  <q-item-section>
    <q-item-label>Trade Routes</q-item-label>
  </q-item-section>
</q-item>

<q-item
  clickable
  v-ripple
  :to="{ name: 'dash-page' }"
  :active="['dash-page', 'dashboard-page'].includes($route.name)"
  active-class="bg-primary text-white"
>
  <q-item-section avatar>
    <q-icon name="swap_horiz" />
  </q-item-section>
  <q-item-section>
    <q-item-label>Dashboard</q-item-label>
  </q-item-section>
</q-item>

        <!-- Regions disabled for now -->
        <!--
        <q-item
          clickable
          v-ripple
          :to="{ name: 'region-list' }"
          :active="$route.name === 'region-list' || $route.name === 'region-detail'"
          active-class="bg-primary text-white"
        >
          <q-item-section avatar>
            <q-icon name="terrain" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Regions</q-item-label>
          </q-item-section>
        </q-item>
        -->

        <q-item
          clickable
          v-ripple
          :to="{ name: 'player-list' }"
          :active="$route.name === 'player-list' || $route.name === 'player-detail'"
          active-class="bg-primary text-white"
        >
          <q-item-section avatar>
            <q-icon name="person" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Players</q-item-label>
          </q-item-section>
        </q-item>

        <q-item
          clickable
          v-ripple
          :to="{ name: 'alliance-list' }"
          :active="$route.name === 'alliance-list' || $route.name === 'alliance-detail'"
          active-class="bg-primary text-white"
        >
          <q-item-section avatar>
            <q-icon name="groups" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Alliances</q-item-label>
          </q-item-section>
        </q-item>

        <q-separator class="q-mt-md q-mb-md" />

        <q-item-label header class="text-grey-8">
          <div class="text-caption">About</div>
        </q-item-label>

        <q-item clickable v-ripple>
          <q-item-section avatar>
            <q-icon name="info" />
          </q-item-section>
          <q-item-section>
            <q-item-label>About</q-item-label>
            <q-item-label caption>Travian Map Analysis</q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref } from 'vue'

const leftDrawerOpen = ref(false)
</script>

<style scoped lang="scss">
.toolbar-title {
  font-weight: 600;
}

.brand-link {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: inherit;
  transition: opacity 0.2s;
  
  &:hover {
    opacity: 0.8;
  }
}

.brand-text {
  font-size: 1.25rem;
}

.desktop-nav {
  display: flex;
  gap: 0.5rem;
}

.nav-btn {
  transition: background-color 0.2s;
  border-radius: 4px;
  
  &:hover {
    background-color: rgba(255, 255, 255, 0.1);
  }
}

.nav-active {
  background-color: rgba(255, 255, 255, 0.2);
  font-weight: 600;
}

@media (max-width: 1023px) {
  .desktop-nav {
    display: none;
  }
}
</style>
