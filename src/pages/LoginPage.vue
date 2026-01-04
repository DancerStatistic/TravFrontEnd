<template>
  <q-page class="login-page">
    <div class="underlay-photo" />
    <div class="underlay-black" />
    <div class="login-form-container">
      <q-form @submit.prevent="onSubmit" class="login-form">
        <div class="login-text">
          <q-icon name="lock" size="64px" class="text-white" />
        </div>
        <q-input
          v-model="username"
          type="email"
          label="Email"
          class="login-input"
          outlined
          dense
          autofocus
          required
        />
        <q-input
          v-model="password"
          type="password"
          label="Password"
          class="login-input"
          outlined
          dense
          required
        />
        <q-btn
          label="Login"
          type="submit"
          class="login-submit"
          unelevated
          color="white"
          text-color="black"
          rounded
        />
        <div class="login-forgot-pass">
          <a href="https://blog.travian.com/2023/06/game-secrets-what-is-map-sql/" class="text-white">
            Travian Map Analysis – Based on the Official map.sql dump by Travian.
          </a>
        </div>
      </q-form>
    </div>
  </q-page>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { QForm, QInput, QBtn, QIcon } from 'quasar';

const username = ref('');
const password = ref('');
const router = useRouter();

function onSubmit() {
  // perform API login then navigate
  router.push('/');
}
</script>

<style scoped>
.login-page {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}
.underlay-photo {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: url('https://i.imgur.com/fUHXSao.png') center/cover no-repeat;
  filter: grayscale(30%);
  animation: hue-rotate 6s infinite linear;
  z-index: 1;
}
.underlay-black {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  z-index: 2;
}
.login-form-container {
  position: relative;
  z-index: 3;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}
.login-form {
  width: 100%;
  max-width: 400px;
  padding: 2rem;
  background: rgba(0, 0, 0, 0.75);
  border-radius: 8px;
  color: white;
}
.login-text {
  text-align: center;
  margin-bottom: 1rem;
}
.login-input {
  margin-bottom: 1rem;
}
  .q-field__control {
    color: white;
  }
  .q-field__label {
    color: rgba(255, 255, 255, 0.7);
  }

.login-submit {
  width: 100%;
  margin-top: 1rem;
  background: white !important;
  color: black !important;
}
.login-forgot-pass {
  margin-top: 1rem;
  text-align: center;
  font-size: 0.8rem;
}
@keyframes hue-rotate {
  0% { filter: grayscale(30%) hue-rotate(0deg); }
  100% { filter: grayscale(30%) hue-rotate(360deg); }
}
</style>
