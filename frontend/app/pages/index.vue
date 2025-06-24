<template>
  <div class="flex flex-col min-h-screen bg-white">
    <!-- Hero Section -->
    <section
      class="relative bg-cover bg-center h-[600px] text-center text-gray-800"
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
            Aidez votre ville à rester propre. Uploadez des images de poubelles et contribuez à une meilleure gestion des déchets urbains grâce à l’IA.
          </p>
        </Motion>

        <Motion
          :initial="{ opacity: 0, scale: 0.9 }"
          :enter="{ opacity: 1, scale: 1, delay: 0.4, transition: { duration: 0.5 } }"
        >
          <div class="flex justify-center gap-4">
            <UButton to="/upload" icon="i-heroicons-arrow-up-tray" size="lg" color="primary">
              Uploader une image
            </UButton>
          </div>
        </Motion>
      </UContainer>
    </section>

    <!-- Dashboard Preview Section -->
    <section class="py-20 bg-[#e0e1dd] text-center text-[#1b263b]">
      <UContainer class="space-y-6">
        <h2 class="text-3xl font-bold">Aperçu du Dashboard</h2>
        <p class="max-w-2xl mx-auto text-[#415a77]">
          Ici s’afficheront bientôt les graphiques, les cartes interactives et les statistiques de collecte.
        </p>
        <div class="flex justify-center">
          <UCard class="w-full max-w-md opacity-60 pointer-events-none">
            <div class="text-center py-8 italic">Dashboard en construction…</div>
          </UCard>
        </div>
      </UContainer>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const gradientStyle = ref('color: transparent; background-image: linear-gradient(90deg, #415a77, #778da9); background-clip: text;')

function updateGradient(event) {
  const el = event.currentTarget
  const rect = el.getBoundingClientRect()
  const x = ((event.clientX - rect.left) / rect.width) * 100
  gradientStyle.value = `
    color: transparent;
    background-image: radial-gradient(circle at ${x}%, #ffffff, #415a77, #778da9);
    background-clip: text;
  `
}

function resetGradient() {
  gradientStyle.value = `
    color: transparent;
    background-image: linear-gradient(90deg, #415a77, #778da9);
    background-clip: text;
  `
}
</script>

<style scoped>
@keyframes lightShift {
  0% {
    background-position: 0% 50%;
  }
  100% {
    background-position: 100% 50%;
  }
}
.group-hover\:animate-lightShift:hover {
  animation: lightShift 2s ease-in-out infinite alternate;
  background-size: 200% 200%;
}
</style>