<template>
  <div class="min-h-[calc(100vh-64px-80px)] py-16 px-4 bg-white">
    <UContainer class="max-w-7xl mx-auto space-y-8">
      <!-- Titre -->
      <div class="text-center">
        <h1 class="text-3xl font-bold text-[#1b263b]">
          {{ translations[currentLanguage].constraintsTitle}}
        </h1>
        <div
          class="mt-2 text-[#415a77] text-sm flex items-center justify-center gap-2"
        >
          <UIcon
            name="i-lucide-sliders-horizontal"
            class="w-4 h-4 text-[#778da9]"
          />
          <span>
            {{ translations[currentLanguage].constraintsDescription }}
          </span>
        </div>
      </div>

      <!-- Switch mode intelligent -->
      <div class="flex items-center justify-center gap-1 mb-6">
        <USwitch
          v-model="intelligentMode"
          checked-icon="i-lucide-brain-cog"
          unchecked-icon="i-lucide-cpu"
          color="primary"
          size="lg"
        />
        <span class="text-sm text-[#415a77] min-w-[180px] text-center">
          {{ intelligentMode ? translations[currentLanguage.value]?.modeint ?? "Mode intelligent activé" : translations[currentLanguage.value]?.modeman ?? "Mode manuel activé" }}
        </span>
      </div>

      <!-- Formulaire -->
      <form @submit.prevent="submitConstraints" class="grid gap-4 max-w-4xl mx-auto">
        <div v-for="field in Object.keys(constraints)" :key="field" class="grid grid-cols-2 gap-2">
          <label class="font-semibold capitalize text-[#1b263b]">{{ field.replaceAll('_', ' ') }}</label>
          <input
            v-model="constraints[field]"
            :type="getInputType(constraints[field])"
            class="border border-gray-300 rounded px-2 py-1"
          />
        </div>
        <button type="submit" class="mt-4 bg-blue-600 text-white px-4 py-2 rounded">
          {{ translations[currentLanguage].save }}
        </button>
      </form>

      <div v-if="message" class="mt-4 text-green-600 text-center">{{ message }}</div>
    </UContainer>
  </div>
</template>

<script setup>
import { ref, inject,  onMounted } from 'vue'
import axios from 'axios'

const constraints = ref({})
const message = ref('')

const currentLanguage = inject('currentLanguage')
const translations = inject('translations')

// Switch intelligent mode
const intelligentMode = ref(false)

const getConstraints = async () => {
  const res = await axios.get('http://localhost:8000/api/constraints/')
  constraints.value = res.data
}

const submitConstraints = async () => {
  await axios.post('http://localhost:8000/api/constraints/update/', constraints.value)
  message.value = 'Contraintes mises à jour avec succès.'
}

const getInputType = (value) => {
  return typeof value === 'number' && Number.isInteger(value) ? 'number' :
         typeof value === 'number' ? 'number' :
         typeof value === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(value) ? 'date' : 'text'
}

onMounted(() => {
  getConstraints()
})
</script>

<style scoped>
input[type="number"] {
  width: 100%;
}
</style>