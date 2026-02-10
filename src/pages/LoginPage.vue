<template>
  <q-page class="login-page" @mousemove="onMouseMove" @mouseleave="onMouseLeave">
    <!-- Animated background layers -->
    <div class="bg-layer bg-photo" />
    <div class="bg-layer bg-vignette" />
    <div class="bg-layer bg-gradient" />
    <div class="bg-layer bg-noise" />
    <div class="bg-layer bg-grid" />

    <!-- NEW: subtle “cursor glow” + parallax highlight -->
    <div
      class="bg-layer bg-cursorGlow"
      :class="{ 'bg-cursorGlow--active': glowActive }"
      :style="cursorGlowStyle"
    />

    <div class="bg-layer bg-orbs">
      <span class="orb orb-1" />
      <span class="orb orb-2" />
      <span class="orb orb-3" />
    </div>

    <!-- Centered card -->
    <div class="login-form-container">
      <!-- NEW: gentle 3D tilt on pointer move -->
      <q-card
        class="login-card"
        flat
        :style="cardTiltStyle"
        @mousemove="onCardMove"
        @mouseleave="onCardLeave"
      >
        <!-- Top glow line -->
        <div class="card-top-glow" />

        <!-- NEW: inner highlight “specular” -->
        <div class="card-specular" :style="specularStyle" />

        <q-card-section class="text-center q-pb-none">
          <div class="login-header">
            <div class="icon-badge">
              <q-icon name="map" size="58px" class="login-icon" />
            </div>

            <h1 class="login-title">
              <span class="title-shine">Travian Status</span>
            </h1>

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
              :type="showPassword ? 'text' : 'password'"
              label="Password"
              class="login-input"
              outlined
              required
              :error="!!error"
            >
              <template #prepend>
                <q-icon name="lock" />
              </template>
              <template #append>
                <q-btn
                  flat
                  round
                  dense
                  class="pw-toggle"
                  :icon="showPassword ? 'visibility_off' : 'visibility'"
                  @click="showPassword = !showPassword"
                  :aria-label="showPassword ? 'Hide password' : 'Show password'"
                />
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
              :disable="loading"
            >
              <template #loading>
                <div class="row items-center no-wrap q-gutter-sm">
                  <q-spinner-dots />
                  <span>Signing in…</span>
                </div>
              </template>
            </q-btn>

            <!-- NEW: tiny “status” dot that animates while loading -->
            <div class="login-status row items-center justify-center q-mt-md">
              <span class="status-dot" :class="{ 'status-dot--loading': loading }" />
              <span class="status-text">
                {{ loading ? 'Authenticating…' : 'Secure session' }}
              </span>
            </div>
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
import { computed, ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { api } from 'boot/axios';
import { useAppStore } from 'src/stores/app';

const username = ref('');
const password = ref('');
const rememberMe = ref(false);
const loading = ref(false);
const error = ref('');
const showPassword = ref(false);

const router = useRouter();
const route = useRoute();
const appStore = useAppStore();

/* =========================
   NEW: cursor glow layer
   ========================= */
const glowX = ref(50);
const glowY = ref(45);
const glowActive = ref(false);

function onMouseMove(e) {
  // page-relative, normalized to %
  const rect = e.currentTarget?.getBoundingClientRect?.();
  if (!rect) return;
  const x = ((e.clientX - rect.left) / rect.width) * 100;
  const y = ((e.clientY - rect.top) / rect.height) * 100;
  glowX.value = Math.max(0, Math.min(100, x));
  glowY.value = Math.max(0, Math.min(100, y));
  glowActive.value = true;
}

function onMouseLeave() {
  glowActive.value = false;
}

/* =========================
   NEW: card tilt + specular
   ========================= */
const tiltX = ref(0);
const tiltY = ref(0);
const specX = ref(50);
const specY = ref(30);

function onCardMove(e) {
  // keep this cheap: only on card hover
  const el = e.currentTarget;
  if (!el) return;
  const rect = el.getBoundingClientRect();
  const px = (e.clientX - rect.left) / rect.width; // 0..1
  const py = (e.clientY - rect.top) / rect.height; // 0..1

  // tilt range
  const max = 6; // degrees
  tiltY.value = (px - 0.5) * max * 2; // left/right
  tiltX.value = -(py - 0.5) * max * 2; // up/down

  // specular follows pointer
  specX.value = px * 100;
  specY.value = py * 100;
}

function onCardLeave() {
  tiltX.value = 0;
  tiltY.value = 0;
  specX.value = 50;
  specY.value = 30;
}

const cursorGlowStyle = computed(() => ({
  '--glow-x': `${glowX.value}%`,
  '--glow-y': `${glowY.value}%`,
}));

const cardTiltStyle = computed(() => ({
  transform: `perspective(900px) rotateX(${tiltX.value}deg) rotateY(${tiltY.value}deg) translateZ(0)`,
}));

const specularStyle = computed(() => ({
  '--spec-x': `${specX.value}%`,
  '--spec-y': `${specY.value}%`,
}));

async function onSubmit() {
  error.value = '';

  // Basic validation
  if (!username.value || !password.value) {
    error.value = 'Please enter both email and password';
    // NEW: a tiny shake when invalid
    bumpShake();
    return;
  }

  // Email validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(username.value)) {
    error.value = 'Please enter a valid email address';
    bumpShake();
    return;
  }

  loading.value = true;

  try {
    const response = await api.post('/api/login', {
      email: username.value.trim(),
      password: password.value
    });
    
    console.log('Login response:', response);
    console.log('Response status:', response.status);
    console.log('Response data:', response.data);
    
    // If we get a 200 response, login was successful
    if (response.status === 200) {
      const data = response.data || {};
      const userEmail = data?.user?.email || username.value.trim();
      
      console.log('Login successful, userEmail:', userEmail);
      
      // Store auth state (persisted to localStorage)
      appStore.setAuthenticated(userEmail);
      
      // Get redirect path from query, default to home
      const redirectParam = route.query.redirect;
      const targetPath = typeof redirectParam === 'string' && redirectParam 
        ? decodeURIComponent(redirectParam) 
        : '/';
      
      // Simple redirect - use window.location for reliability
      window.location.href = targetPath;
      return; // Exit early to prevent any further execution
    } else {
      console.error('Unexpected status:', response.status);
      error.value = 'Invalid credentials. Please try again.';
      bumpShake();
    }
  } catch (err) {
    console.error('Login error:', err);
    console.error('Error response:', err?.response);
    error.value = err?.response?.data?.message || 'Invalid credentials. Please try again.';
    bumpShake();
  } finally {
    loading.value = false;
  }
}

/* NEW: shake helper (pure DOM class toggle, short + cheap) */
function bumpShake() {
  const el = document.querySelector('.login-card');
  if (!el) return;
  el.classList.remove('is-shaking');
  // force reflow so animation re-triggers
  // eslint-disable-next-line no-unused-expressions
  el.offsetHeight;
  el.classList.add('is-shaking');
  window.setTimeout(() => el.classList.remove('is-shaking'), 380);
}
</script>

<style scoped lang="scss">
/* =========================
   Page / background effects
   ========================= */
.login-page {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;

  display: flex;
  align-items: center;
  justify-content: center;
}

.bg-layer {
  position: absolute;
  inset: 0;
  z-index: 1;
}

.bg-photo {
  // background: url('https://i.imgur.com/fUHXSao.png') center/cover no-repeat;
  filter: saturate(115%) contrast(105%);
  transform: scale(1.06);
  animation: bg-kenburns 18s ease-in-out infinite alternate, hue-rotate 10s linear infinite;
}

.bg-vignette {
  background: radial-gradient(
    ellipse at center,
    rgba(0, 0, 0, 0.35) 0%,
    rgba(0, 0, 0, 0.82) 70%,
    rgba(0, 0, 0, 0.92) 100%
  );
  z-index: 2;
}

.bg-gradient {
  background:
    radial-gradient(800px 500px at 15% 20%, rgba(0, 170, 255, 0.18), transparent 60%),
    radial-gradient(900px 600px at 85% 75%, rgba(123, 92, 255, 0.18), transparent 60%);
  mix-blend-mode: screen;
  z-index: 3;
  animation: gradient-drift 12s ease-in-out infinite alternate;
}

.bg-noise {
  z-index: 4;
  pointer-events: none;
  opacity: 0.12;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='160' height='160' filter='url(%23n)' opacity='.55'/%3E%3C/svg%3E");
  animation: noise-shift 2.8s steps(2) infinite;
}

.bg-grid {
  z-index: 5;
  pointer-events: none;
  opacity: 0.12;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.10) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.10) 1px, transparent 1px);
  background-size: 52px 52px;
  mask-image: radial-gradient(circle at 50% 45%, rgba(0, 0, 0, 1) 0%, rgba(0, 0, 0, .8) 35%, rgba(0, 0, 0, 0) 70%);
  animation: grid-slide 16s linear infinite;
}

/* NEW: cursor-follow glow (very modern, very subtle) */
.bg-cursorGlow {
  z-index: 5; /* between grid + orbs */
  pointer-events: none;
  opacity: 0;
  transition: opacity 220ms ease;
  background:
    radial-gradient(
      520px 420px at var(--glow-x, 50%) var(--glow-y, 45%),
      rgba(255, 255, 255, 0.08),
      rgba(255, 255, 255, 0.00) 60%
    ),
    radial-gradient(
      760px 560px at calc(var(--glow-x, 50%) + 6%) calc(var(--glow-y, 45%) + 8%),
      rgba(0, 170, 255, 0.09),
      rgba(0, 170, 255, 0.00) 62%
    );
  mix-blend-mode: screen;
}

.bg-cursorGlow--active {
  opacity: 1;
}

.bg-orbs {
  z-index: 6;
  pointer-events: none;
}

.orb {
  position: absolute;
  width: 520px;
  height: 520px;
  border-radius: 999px;
  filter: blur(28px);
  opacity: 0.25;
  transform: translate3d(0,0,0);
  background: radial-gradient(circle at 30% 30%, rgba(255,255,255,0.25), rgba(255,255,255,0) 55%),
              radial-gradient(circle at 70% 70%, rgba(255,255,255,0.10), rgba(255,255,255,0) 60%);
}

.orb-1 {
  top: -180px;
  left: -140px;
  background: radial-gradient(circle at 30% 30%, rgba(0, 170, 255, 0.45), rgba(0, 170, 255, 0) 55%),
              radial-gradient(circle at 70% 70%, rgba(123, 92, 255, 0.25), rgba(123, 92, 255, 0) 60%);
  animation: orb-float-1 10s ease-in-out infinite alternate;
}
.orb-2 {
  bottom: -220px;
  right: -160px;
  background: radial-gradient(circle at 30% 30%, rgba(123, 92, 255, 0.45), rgba(123, 92, 255, 0) 55%),
              radial-gradient(circle at 70% 70%, rgba(0, 170, 255, 0.22), rgba(0, 170, 255, 0) 60%);
  animation: orb-float-2 12s ease-in-out infinite alternate;
}
.orb-3 {
  top: 35%;
  left: 55%;
  width: 360px;
  height: 360px;
  opacity: 0.18;
  background: radial-gradient(circle at 35% 35%, rgba(255, 180, 60, 0.35), rgba(255, 180, 60, 0) 58%),
              radial-gradient(circle at 70% 70%, rgba(255, 80, 120, 0.18), rgba(255, 80, 120, 0) 62%);
  animation: orb-float-3 9s ease-in-out infinite alternate;
}

/* =========================
   Layout / card animation
   ========================= */
.login-form-container {
  position: relative;
  z-index: 10;
  width: 100%;
  padding: 1rem;
  display: flex;
  justify-content: center;
  align-items: center;
}

.login-card {
  width: 100%;
  max-width: 460px;

  background: rgba(10, 12, 18, 0.72) !important;
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);

  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  box-shadow:
    0 24px 70px rgba(0, 0, 0, 0.55),
    0 0 0 1px rgba(255, 255, 255, 0.06) inset;

  position: relative;
  overflow: hidden;

  /* Entry animation */
  animation: card-in 700ms cubic-bezier(.2,.9,.2,1) both;

  /* NEW: help make tilt look crisp */
  transform-style: preserve-3d;
  will-change: transform;
}

/* NEW: invalid shake */
.login-card.is-shaking {
  animation: card-shake 360ms ease both;
}

.card-top-glow {
  position: absolute;
  left: -40%;
  top: 0;
  width: 180%;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.35), transparent);
  opacity: 0.7;
  animation: shine-sweep 3.2s ease-in-out infinite;
}

/* NEW: pointer-follow “specular highlight” inside the card */
.card-specular {
  position: absolute;
  inset: -1px;
  pointer-events: none;
  z-index: 0;
  background:
    radial-gradient(
      420px 320px at var(--spec-x, 50%) var(--spec-y, 30%),
      rgba(255, 255, 255, 0.08),
      rgba(255, 255, 255, 0.00) 60%
    );
  opacity: 0.75;
  mix-blend-mode: screen;
}

.login-header {
  padding: 2rem 0 1rem;
  animation: fade-up 650ms ease both;
  animation-delay: 120ms;
  position: relative;
  z-index: 1;
}

.icon-badge {
  width: 88px;
  height: 88px;
  margin: 0 auto 0.75rem;
  border-radius: 999px;
  display: grid;
  place-items: center;

  background: radial-gradient(circle at 30% 30%, rgba(255,255,255,0.12), rgba(255,255,255,0.02));
  border: 1px solid rgba(255, 255, 255, 0.10);
  box-shadow: 0 18px 40px rgba(0,0,0,0.35);
}

.login-icon {
  color: $primary;
  animation: icon-float 2.6s ease-in-out infinite;
}

.login-title {
  font-size: 2rem;
  font-weight: 800;
  color: white;
  margin: 0.5rem 0 0.25rem;
  letter-spacing: 0.2px;
}

.title-shine {
  position: relative;
  display: inline-block;
}

.title-shine::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(110deg, transparent 0%, rgba(255,255,255,0.35) 30%, transparent 60%);
  transform: translateX(-120%);
  animation: title-shimmer 3.8s ease-in-out infinite;
  pointer-events: none;
  mix-blend-mode: screen;
}

.login-subtitle {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.72);
  margin: 0;
}

.login-form {
  padding: 0;
  animation: fade-up 700ms ease both;
  animation-delay: 170ms;
  position: relative;
  z-index: 1;
}

/* =========================
   Inputs: animated focus ring
   ========================= */
.login-input {
  margin-bottom: 1rem;

  :deep(.q-field__control) {
    color: white;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 10px;
    transition: transform 180ms ease, box-shadow 180ms ease, background 180ms ease;
  }

  :deep(.q-field__label) {
    color: rgba(255, 255, 255, 0.72);
  }

  :deep(.q-field__native) {
    color: white;
  }

  :deep(.q-field--outlined .q-field__control:before) {
    border-color: rgba(255, 255, 255, 0.25);
  }

  :deep(.q-field--focused .q-field__control) {
    transform: translateY(-1px);
    background: rgba(255, 255, 255, 0.07);
    box-shadow:
      0 10px 26px rgba(0, 0, 0, 0.35),
      0 0 0 2px rgba($primary, 0.35);
  }

  /* subtle icon pulse on focus */
  :deep(.q-field--focused .q-icon) {
    animation: icon-pop 240ms ease-out both;
  }
}

.pw-toggle {
  color: rgba(255,255,255,0.85);
}

/* =========================
   Links + button glow
   ========================= */
.forgot-link {
  text-decoration: none;
  transition: opacity 0.2s, transform 0.2s;

  &:hover {
    opacity: 0.85;
    text-decoration: underline;
    transform: translateY(-1px);
  }
}

.login-submit {
  margin-top: 1rem;
  border-radius: 10px;
  font-weight: 700;
  text-transform: none;
  position: relative;
  overflow: hidden;

  transition: transform 0.2s, box-shadow 0.2s;

  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 12px 26px rgba(0, 0, 0, 0.35);
  }

  /* animated sheen */
  &::after {
    content: "";
    position: absolute;
    top: -40%;
    left: -60%;
    width: 60%;
    height: 220%;
    transform: rotate(18deg);
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.28), transparent);
    opacity: 0;
    transition: opacity 220ms ease;
  }

  &:hover::after {
    opacity: 1;
    animation: button-sheen 900ms ease;
  }
}

/* NEW: tiny status row */
.login-status {
  gap: 10px;
  opacity: 0.9;
  user-select: none;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 99px;
  background: rgba(255, 255, 255, 0.55);
  box-shadow: 0 0 0 3px rgba(255,255,255,0.10);
  transform: translateZ(0);
}

.status-dot--loading {
  animation: dot-pulse 900ms ease-in-out infinite;
  background: rgba($primary, 0.9);
  box-shadow: 0 0 0 3px rgba($primary, 0.18), 0 0 18px rgba($primary, 0.35);
}

.status-text {
  font-size: 12px;
  color: rgba(255,255,255,0.70);
}

.login-info {
  padding: 1rem 0;
  animation: fade-up 750ms ease both;
  animation-delay: 220ms;
  position: relative;
  z-index: 1;
}

.info-link {
  text-decoration: none;
  transition: opacity 0.2s, transform 0.2s;
  display: inline-block;
  margin-top: 0.5rem;

  &:hover {
    opacity: 0.85;
    text-decoration: underline;
    transform: translateY(-1px);
  }
}

/* =========================
   Motion accessibility
   ========================= */
@media (prefers-reduced-motion: reduce) {
  .bg-photo,
  .bg-gradient,
  .bg-grid,
  .bg-noise,
  .bg-cursorGlow,
  .orb,
  .card-top-glow,
  .login-card,
  .login-header,
  .login-form,
  .login-info,
  .login-icon,
  .title-shine::after,
  .login-submit::after,
  .status-dot--loading {
    animation: none !important;
    transition: none !important;
  }

  .login-card {
    transform: none !important;
  }
}

/* =========================
   Keyframes
   ========================= */
@keyframes hue-rotate {
  0% { filter: saturate(115%) contrast(105%) hue-rotate(0deg); }
  100% { filter: saturate(115%) contrast(105%) hue-rotate(360deg); }
}

@keyframes bg-kenburns {
  0% { transform: scale(1.06) translate3d(0, 0, 0); }
  100% { transform: scale(1.12) translate3d(-1.5%, -1%, 0); }
}

@keyframes gradient-drift {
  0% { transform: translate3d(0, 0, 0); opacity: 0.9; }
  100% { transform: translate3d(1.5%, -1.2%, 0); opacity: 1; }
}

@keyframes noise-shift {
  0% { transform: translate3d(0,0,0); }
  50% { transform: translate3d(-1.5%, 1%, 0); }
  100% { transform: translate3d(1%, -1.2%, 0); }
}

@keyframes grid-slide {
  0% { background-position: 0 0, 0 0; }
  100% { background-position: 260px 260px, 260px 260px; }
}

@keyframes orb-float-1 {
  0% { transform: translate3d(0, 0, 0) scale(1); }
  100% { transform: translate3d(40px, 22px, 0) scale(1.05); }
}
@keyframes orb-float-2 {
  0% { transform: translate3d(0, 0, 0) scale(1); }
  100% { transform: translate3d(-36px, -26px, 0) scale(1.06); }
}
@keyframes orb-float-3 {
  0% { transform: translate3d(0, 0, 0) scale(1); }
  100% { transform: translate3d(20px, -18px, 0) scale(1.08); }
}

@keyframes card-in {
  0% {
    opacity: 0;
    transform: translate3d(0, 14px, 0) scale(0.985);
    filter: blur(2px);
  }
  100% {
    opacity: 1;
    transform: translate3d(0, 0, 0) scale(1);
    filter: blur(0);
  }
}

@keyframes card-shake {
  0% { transform: translate3d(0, 0, 0); }
  20% { transform: translate3d(-8px, 0, 0); }
  40% { transform: translate3d(7px, 0, 0); }
  60% { transform: translate3d(-6px, 0, 0); }
  80% { transform: translate3d(5px, 0, 0); }
  100% { transform: translate3d(0, 0, 0); }
}

@keyframes fade-up {
  0% { opacity: 0; transform: translate3d(0, 10px, 0); }
  100% { opacity: 1; transform: translate3d(0, 0, 0); }
}

@keyframes icon-float {
  0%, 100% { transform: translate3d(0, 0, 0); }
  50% { transform: translate3d(0, -4px, 0); }
}

@keyframes icon-pop {
  0% { transform: scale(1); }
  60% { transform: scale(1.08); }
  100% { transform: scale(1); }
}

@keyframes shine-sweep {
  0% { transform: translateX(-25%); opacity: 0.25; }
  50% { transform: translateX(0%); opacity: 0.75; }
  100% { transform: translateX(25%); opacity: 0.25; }
}

@keyframes title-shimmer {
  0% { transform: translateX(-120%); opacity: 0; }
  15% { opacity: 0.65; }
  55% { opacity: 0.45; }
  100% { transform: translateX(120%); opacity: 0; }
}

@keyframes button-sheen {
  0% { transform: translateX(0) rotate(18deg); }
  100% { transform: translateX(320%) rotate(18deg); }
}

@keyframes dot-pulse {
  0% { transform: scale(1); opacity: 0.9; }
  50% { transform: scale(1.35); opacity: 1; }
  100% { transform: scale(1); opacity: 0.9; }
}

/* =========================
   Responsive tweaks
   ========================= */
@media (max-width: 600px) {
  .login-card {
    max-width: 100%;
    margin: 1rem;
    transform: none !important; /* avoid tilt weirdness on small screens */
  }

  .login-title {
    font-size: 1.55rem;
  }

  .icon-badge {
    width: 78px;
    height: 78px;
  }
}
</style>
