<template>
  <q-page class="login-page">
    <div class="underlay-photo" />
    <div class="underlay-black" />
    <div class="login-form-container">
      <q-card class="login-card" flat>
        <q-card-section class="text-center q-pb-none">
          <div class="login-header">
            <q-icon name="map" size="64px" class="login-icon" />
            <h1 class="login-title">Travian Status</h1>
            <p class="login-subtitle">Sign in to access the analytics dashboard</p>
          </div>
        </q-card-section>
        
        <q-card-section>
          <q-form @submit.prevent="onSubmit" class="login-form">
            <q-input
              v-model="username"
              type="email"
              label="Email"
              class="login-input"
              outlined
              autofocus
              required
              :error="!!error"
              :error-message="error"
            >
              <template #prepend>
                <q-icon name="email" />
              </template>
            </q-input>
            
            <q-input
              v-model="password"
              type="password"
              label="Password"
              class="login-input"
              outlined
              required
              :error="!!error"
            >
              <template #prepend>
                <q-icon name="lock" />
              </template>
            </q-input>
            
            <div class="row items-center q-mb-md">
              <q-checkbox v-model="rememberMe" label="Remember me" class="text-white" />
              <q-space />
              <a href="#" class="text-white text-caption forgot-link">Forgot password?</a>
            </div>
            
            <q-btn
              label="Sign In"
              type="submit"
              class="login-submit full-width"
              unelevated
              color="primary"
              size="lg"
              :loading="loading"
            />
          </q-form>
        </q-card-section>
        
        <q-separator dark />
        
        <q-card-section class="text-center">
          <div class="login-info">
            <p class="text-caption text-white q-mb-none">
              Travian Map Analysis – Based on the Official map.sql dump by Travian.
            </p>
            <a
              href="https://blog.travian.com/2023/06/game-secrets-what-is-map-sql/"
              target="_blank"
              rel="noopener"
              class="text-white text-caption info-link"
            >
              Learn more
            </a>
          </div>
        </q-card-section>
      </q-card>
    </div>
  </q-page>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useQuasar } from 'quasar';

const username = ref('');
const password = ref('');
const rememberMe = ref(false);
const loading = ref(false);
const error = ref('');
const router = useRouter();
const $q = useQuasar();

async function onSubmit() {
  error.value = '';
  
  // Basic validation
  if (!username.value || !password.value) {
    error.value = 'Please enter both email and password';
    return;
  }
  
  // Email validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(username.value)) {
    error.value = 'Please enter a valid email address';
    return;
  }
  
  loading.value = true;
  
  try {
    // TODO: Implement actual API login
    // For now, simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // On success, navigate to home
    $q.notify({
      type: 'positive',
      message: 'Login successful',
      position: 'top'
    });
    
    router.push('/');
  } catch (err) {
    error.value = 'Invalid credentials. Please try again.';
    $q.notify({
      type: 'negative',
      message: error.value,
      position: 'top'
    });
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped lang="scss">
.login-page {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
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
  background: rgba(0, 0, 0, 0.75);
  z-index: 2;
}

.login-form-container {
  position: relative;
  z-index: 3;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  padding: 1rem;
}

.login-card {
  width: 100%;
  max-width: 450px;
  background: rgba(0, 0, 0, 0.85) !important;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.login-header {
  padding: 2rem 0 1rem;
}

.login-icon {
  color: $primary;
  margin-bottom: 1rem;
  animation: pulse 2s ease-in-out infinite;
}

.login-title {
  font-size: 2rem;
  font-weight: 700;
  color: white;
  margin: 0.5rem 0;
}

.login-subtitle {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}

.login-form {
  padding: 0;
}

.login-input {
  margin-bottom: 1rem;
  
  :deep(.q-field__control) {
    color: white;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
  }
  
  :deep(.q-field__label) {
    color: rgba(255, 255, 255, 0.7);
  }
  
  :deep(.q-field__native) {
    color: white;
  }
  
  :deep(.q-field--outlined .q-field__control) {
    border-color: rgba(255, 255, 255, 0.3);
  }
  
  :deep(.q-field--focused .q-field__control) {
    border-color: $primary;
  }
}

.forgot-link {
  text-decoration: none;
  transition: opacity 0.2s;
  
  &:hover {
    opacity: 0.8;
    text-decoration: underline;
  }
}

.login-submit {
  margin-top: 1rem;
  border-radius: 8px;
  font-weight: 600;
  text-transform: none;
  transition: transform 0.2s, box-shadow 0.2s;
  
  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
  }
}

.login-info {
  padding: 1rem 0;
}

.info-link {
  text-decoration: none;
  transition: opacity 0.2s;
  display: inline-block;
  margin-top: 0.5rem;
  
  &:hover {
    opacity: 0.8;
    text-decoration: underline;
  }
}

@keyframes hue-rotate {
  0% {
    filter: grayscale(30%) hue-rotate(0deg);
  }
  100% {
    filter: grayscale(30%) hue-rotate(360deg);
  }
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.05);
    opacity: 0.9;
  }
}

@media (max-width: 600px) {
  .login-card {
    max-width: 100%;
    margin: 1rem;
  }
  
  .login-title {
    font-size: 1.5rem;
  }
}
</style>
