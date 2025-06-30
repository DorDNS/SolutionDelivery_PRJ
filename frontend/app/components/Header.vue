<template>
  <header class="bg-[#1b263b] text-white shadow-md">
    <UContainer class="flex justify-between items-center py-4">
      <NuxtLink to="/" class="flex items-center gap-2">
        <img
          src="/images/icone-trashmap.svg"
          alt="Logo TrashMap"
          class="h-9 w-auto"
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
        <!-- Menu déroulant pour changer la langue -->
        <USelect v-model="value" :items="items" value-key="value" :avatar="avatar" class="w-48" @update:modelValue="changeLanguage" />
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
      alt: 'rn'
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
.lang-switch {
  display: flex;
  align-items: center;
  gap: 8px;
}

.lang-button {
  background-color: transparent;
  border: none;
  cursor: pointer;
}

.lang-button img {
  display: block;
  border-radius: 50%;
}

.lang-dropdown {
  padding: 8px 16px;
  background-color: #415a77;
  color: #ffffff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
}

.lang-dropdown:hover {
  background-color: #778da9;
}
</style>