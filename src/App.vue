<template>
  <q-layout view="lHh Lpr lFf">


    <q-page-container class="app-page-container">
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { QLayout, QHeader, QToolbar, QToolbarTitle, QPageContainer } from 'quasar'
</script>
