<template>
  <div class="p-6 max-w-4xl mx-auto">
    <h1 class="text-2xl font-bold mb-4">Configuration des règles de classification</h1>
    <form @submit.prevent="submitConstraints" class="grid gap-4">
      <div v-for="field in Object.keys(constraints)" :key="field" class="grid grid-cols-2 gap-2">
        <label class="font-semibold capitalize">{{ field.replaceAll('_', ' ') }}</label>
        <input
          v-model="constraints[field]"
          :type="getInputType(constraints[field])"
          class="border border-gray-300 rounded px-2 py-1"
        />
      </div>
      <button type="submit" class="mt-4 bg-blue-600 text-white px-4 py-2 rounded">Enregistrer</button>
    </form>
    <div v-if="message" class="mt-4 text-green-600">{{ message }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const constraints = ref({})
const message = ref('')

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
