<template>
  <div class="flex flex-col min-h-screen bg-white">
    <!-- Hero Section -->
    <section
      class="relative bg-cover bg-center h-[420px] text-center text-gray-800"
      style="
        background-image:
          linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3)),
          url('/images/hero-fond.png');
      "
    >
      <UContainer class="relative z-10 space-y-10 flex flex-col justify-center h-full">
        <Motion
          :initial="{ opacity: 0, y: -20 }"
          :enter="{ opacity: 1, y: 0, transition: { duration: 0.7, ease: 'easeOut' } }"
        >
          <h1
            class="text-6xl font-extrabold tracking-tight relative inline-block"
            @mousemove="updateGradient"
            @mouseleave="resetGradient"
            :style="gradientStyle"
          >
            TrashMap
          </h1>
        </Motion>

        <Motion
          :initial="{ opacity: 0, y: 20 }"
          :enter="{ opacity: 1, y: 0, delay: 0.2, transition: { duration: 0.6 } }"
        >
          <p class="text-lg text-[#e0e1dd] max-w-2xl mx-auto">
            {{ translations[currentLanguage].slogan }}
          </p>
        </Motion>

        <Motion
          :initial="{ opacity: 0, scale: 0.9 }"
          :enter="{ opacity: 1, scale: 1, delay: 0.4, transition: { duration: 0.5 } }"
        >
          <div class="flex justify-center gap-4">
            <UButton to="/upload" icon="i-heroicons-arrow-up-tray" size="lg" color="primary">
              {{ translations[currentLanguage].uploadButton }}
            </UButton>
          </div>
        </Motion>
      </UContainer>
    </section>

    <!-- Dashboard Preview Section -->
    <section class="flex-1 py-20 bg-[#e0e1dd] text-center text-[#1b263b]">
      <UContainer class="space-y-6">
        <h2 class="text-3xl font-bold">{{ translations[currentLanguage].dashboardprev }}</h2>
        <p class="max-w-2xl mx-auto text-[#415a77]">
          {{ translations[currentLanguage].dashboardDescription }}
        </p>
        <DashboardPreview />
      </UContainer>
    </section>
  </div>
</template>

<script setup>
import { ref, inject } from 'vue'
import DashboardPreview from '@/components/dashboard/DashboardPreview.vue'

const currentLanguage = inject('currentLanguage')
const translations    = inject('translations')

// Couleurs
const gradientStyle = ref(`
  color: transparent;
  background-image: linear-gradient(90deg, rgba(11,178,246,1) 0%, #415a77 100%);
  background-clip: text;
`)

function updateGradient(event) {
  const el   = event.currentTarget
  const rect = el.getBoundingClientRect()
  const x    = ((event.clientX - rect.left) / rect.width) * 100

  gradientStyle.value = `
    color: transparent;
    background-image: radial-gradient(
      circle at ${x}%,
      rgba(160,231,245,0.8),
      rgba(11,178,246,1),
      #415a77
    );
    background-clip: text;
  `
}

function resetGradient() {
  gradientStyle.value = `
    color: transparent;
    background-image: linear-gradient(90deg, rgba(11,178,246,1) 0%, #415a77 100%);
    background-clip: text;
  `
}
</script>

<style scoped>
@keyframes lightShift {
  0% { background-position: 0% 50%; }
  100% { background-position: 100% 50%; }
}
.group-hover\:animate-lightShift:hover {
  animation: lightShift 2s ease-in-out infinite alternate;
  background-size: 200% 200%;
}
</style>
