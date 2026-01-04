<template>
  <q-layout view="hHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>

        <!-- menu button / etc. -->

        <q-btn flat dense to="/"     label="Map"      icon="map"      />
        <q-btn flat dense to="/region"   label="Regions"   icon="terrain" />
        <q-btn flat dense to="/player"   label="Players"   icon="person"  />
        <q-btn flat dense to="/alliance" label="Alliance"  icon="groups"  />

      </q-toolbar>
    </q-header>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>
