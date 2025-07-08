<template>
  <header class="bg-[#1b263b] text-white shadow-md">
    <UContainer class="flex justify-between items-center py-4">

      <!-- Logo -->
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

      <!-- Menu desktop -->
      <nav class="hidden md:flex gap-4 items-center">
        <UButton to="/upload" color="primary">
          {{ translations[currentLanguage].headerup }}
        </UButton>
        <UButton to="/navigation" variant="ghost" class="text-white hover:text-[#e0e1dd]">
          {{ translations[currentLanguage].headernav }}
        </UButton>
        <UButton to="/constraints" variant="ghost" class="text-white hover:text-[#e0e1dd]">
          {{ translations[currentLanguage].headerconstraints }}
        </UButton>
        <USelect v-model="value" :items="items" value-key="value" :avatar="avatar" class="custom-select" @update:model-value="changeLanguage" />
      </nav>

      <!-- Bouton burger (mobile) -->
      <button
        @click="isOpen = !isOpen"
        class="md:hidden focus:outline-none"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2"
          viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round">
          <path v-if="!isOpen" d="M4 6h16M4 12h16M4 18h16"></path>
          <path v-else d="M6 18L18 6M6 6l12 12"></path>
        </svg>
      </button>
    </UContainer>

    <!-- Menu mobile déroulant -->
    <div v-if="isOpen" class="md:hidden bg-[#1b263b] px-4 pb-4 space-y-2">
      <UButton to="/upload" color="primary" block>
        {{ translations[currentLanguage].headerup }}
      </UButton>
      <UButton to="/navigation" variant="ghost" class="text-white hover:text-[#e0e1dd]" block>
        {{ translations[currentLanguage].headernav }}
      </UButton>
      <UButton to="/constraints" variant="ghost" class="text-white hover:text-[#e0e1dd]" block>
        {{ translations[currentLanguage].headerconstraints }}
      </UButton>
      <USelect v-model="value" :items="items" value-key="value" :avatar="avatar" class="custom-select" @update:model-value="changeLanguage" />
    </div>

  </header>
</template>

<script setup lang="ts">
import { provide, inject, ref, computed } from 'vue'
import type { SelectItem } from '@nuxt/ui'

const currentLanguage = inject('currentLanguage')
const translations = inject('translations')

// État du menu mobile
const isOpen = ref(false)

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

provide('currentLanguage', currentLanguage)
provide('translations', translations)
</script>

<style scoped>
.custom-select {
  width: 120px;
}
</style>