<template>
  <footer class="bg-[#415a77] text-white py-6 text-center">
    <p class="text-sm">&copy; {{ translations[currentLanguage].footerText }}</p>
  </footer>
</template>

<script setup>
import {inject } from 'vue'

const currentLanguage = inject('currentLanguage')
const translations = inject('translations')

</script>