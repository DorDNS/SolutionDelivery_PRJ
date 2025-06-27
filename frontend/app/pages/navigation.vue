<template>
  <div class="min-h-[calc(100vh-64px-80px)] py-16 px-4 bg-white">
    <UContainer class="max-w-xl mx-auto space-y-8">
      <!-- Titre -->
      <div class="text-center">
        <h1 class="text-3xl font-bold text-[#1b263b]">Navigation des images</h1>
        <div class="mt-2 text-[#415a77] text-sm flex items-center justify-center gap-2">
          <UIcon name="i-heroicons-eye" class="w-4 h-4 text-[#778da9]" />
          <span>Utilisez les flèches ou raccourcis clavier pour parcourir les images.</span>
        </div>
      </div>

      <!-- Filtre -->
      <div class="flex justify-center">
        <USelect
          v-model="filtre"
          :items="filtres"
          placeholder="Filtrer par statut"
          class="w-full max-w-xs"
          color="primary"
          size="lg"
        />
      </div>

      <!-- Image affichée -->
      <div v-if="images.length > 0" class="text-center space-y-6">
        <img
          :src="`/test/${images[index]}`"
          :alt="images[index]"
          class="max-h-[32rem] mx-auto rounded-xl shadow-lg border"
        />
        <div class="flex justify-between">
          <UButton
            @click="precedente"
            :disabled="index === 0"
            color="gray"
            variant="ghost"
          >
            ◀ Précédente
          </UButton>
          <UButton
            @click="suivante"
            :disabled="index === images.length - 1"
            color="gray"
            variant="ghost"
          >
            Suivante ▶
          </UButton>
        </div>
      </div>

      <div v-else class="text-center text-[#778da9] text-sm">
        Aucune image à afficher.
      </div>
    </UContainer>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const allImages = [
  '00569_03.jpg',
  '908.full.jpeg',
  '1080.full.jpeg',
  '1576.full.jpeg',
  '1794.full.jpeg',
  '02587_03.jpg',
  'dsc0132_4.jpg.png'
]

const filtre = ref('all')
const filtres = [
  { label: 'Toutes les images', value: 'all' },
  { label: 'Non annotées', value: 'non_annotated' },
  { label: 'Annotées', value: 'annotated' }
]

const images = ref([...allImages])
const index = ref(0)

function precedente() {
  if (index.value > 0) index.value--
}

function suivante() {
  if (index.value < images.value.length - 1) index.value++
}

function handleKey(event) {
  if (event.key === 'ArrowLeft') {
    precedente()
  } else if (event.key === 'ArrowRight') {
    suivante()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKey)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKey)
})
</script>