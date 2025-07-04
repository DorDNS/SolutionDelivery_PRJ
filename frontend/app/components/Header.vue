<template>
  <header class="bg-[#1b263b] text-white shadow-md">
    <UContainer class="flex justify-between items-center py-4">
      <NuxtLink to="/" class="flex items-center gap-2">
        <img
          src="/images/icone-trashmap.svg"
          alt="Logo TrashMap"
          class="h-9 w-auto"
          loading="lazy"
        />
        <span class="text-2xl font-bold tracking-tight text-white">
          TrashMap
        </span>
      </NuxtLink>

      <nav class="flex gap-4">
        <UButton to="/upload" color="primary">
          {{ translations[currentLanguage].headerup }}
        </UButton>
        <UButton to="/navigation" variant="ghost" class="text-white hover:text-[#e0e1dd]">
          {{ translations[currentLanguage].headernav }}
        </UButton>
        <UButton to="/constraints" variant="ghost" class="text-white hover:text-[#e0e1dd]">
          {{ translations[currentLanguage].headerconstraints }}
        </UButton>
        <!-- Menu déroulant pour changer la langue -->
        <USelect v-model="value" :items="items" value-key="value" :avatar="avatar" class="custom-select" @update:model-value="changeLanguage" />
      </nav>
    </UContainer>
  </header>
</template>

<script setup lang="ts">
import { provide, inject, ref, computed } from 'vue'
import type { SelectItem } from '@nuxt/ui'

// Traduction
const currentLanguage = inject('currentLanguage')
const translations = inject('translations')

const items = ref([
  {
    label: 'Français',
    value: 'fr',
    avatar: {
      src: '/images/Flag_of_France.svg',
      alt: 'fr'
    }
  },
  {
    label: 'English',
    value: 'en',
    avatar: {
      src: '/images/Flag_of_the_UK.svg',
      alt: 'en'
    }
  },
  {
    label: 'اللغة العربية',
    value: 'ar',
    avatar: {
      src: '/images/Flag_of_Algeria.svg',
      alt: 'ar'
    }
  }
] satisfies SelectItem[])
const value = ref(items.value[0]?.value)

const avatar = computed(() => items.value.find(item => item.value === value.value)?.avatar)

function changeLanguage(lang) {
  currentLanguage.value = lang
}

// Fournir la langue et les traductions aux composants enfants
provide('currentLanguage', currentLanguage)
provide('translations', translations)
</script>

<style scoped>
.custom-select {
  width: 120px; /* Ajustez la largeur selon vos besoins */
}
</style>