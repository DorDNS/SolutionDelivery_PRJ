<template>
  <footer class="bg-[#415a77] text-white py-6 text-center">
    <p class="text-sm">&copy; {{ translations[currentLanguage].footerText }}</p>
    <form @submit.prevent="subscribeEmail" class="flex justify-center gap-2 flex-wrap">
      <input
        v-model="email"
        type="email"
        placeholder="Entrez votre email"
        required
        class="text-black px-2 py-1 rounded bg-white"
      />
      <button
        type="submit"
        class="bg-[#1b263b] hover:bg-[#0d1b2a] text-white px-3 py-1 rounded"
      >
        S’abonner
      </button>
    </form>

    <p v-if="message" class="mt-2 text-sm">{{ message }}</p>
  </footer>
</template>

<script setup>
import {inject } from 'vue'
import axios from 'axios'

const currentLanguage = inject('currentLanguage')
const translations = inject('translations')

const email = ref('')
const message = ref('')

const subscribeEmail = async () => {
  try {
    await axios.post('http://localhost:8000/subscribe/', { email: email.value })
    message.value = 'Inscription réussie ! Un rapport vous a été envoyé.'
    email.value = ''
  } catch (error) {
    message.value = 'Erreur lors de l’inscription.'
    console.error(error)
  }
}
</script>