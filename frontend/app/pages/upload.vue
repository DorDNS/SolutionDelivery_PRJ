<template>
  <div class="min-h-[calc(100vh-64px-80px)] py-16 px-4 bg-white">
    <UContainer class="max-w-xl mx-auto space-y-8">
      <div class="text-center">
        <h1 class="text-3xl font-bold text-[#1b263b]">Uploader une image</h1>
        <div class="mt-2 text-[#415a77] text-sm flex items-center justify-center gap-2">
            <UIcon name="i-heroicons-information-circle" class="w-4 h-4 text-[#778da9]" />
            <span>
                Formats acceptés : <strong>JPG</strong>, <strong>PNG</strong> — max <strong>5 Mo</strong> — min <strong>500×500 px</strong>
            </span>
        </div>

      </div>

      <UCard>
        <UForm :state="form" @submit="handleSubmit" class="space-y-6">
          <UFormGroup label="Fichier image" name="file" :error="error">
            <UInput
              type="file"
              accept=".jpg,.jpeg,.png"
              @change="handleFileChange"
              icon="i-heroicons-photo"
            />
          </UFormGroup>

          <div class="pt-2">
            <UButton type="submit" color="primary" block :disabled="!isValid">
              Envoyer l’image
            </UButton>
          </div>
        </UForm>
      </UCard>

      <div v-if="preview" class="text-center mt-8">
        <img :src="preview" alt="Aperçu" class="max-h-96 mx-auto rounded-xl shadow-lg border" />
      </div>
    </UContainer>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const form = ref({})
const preview = ref(null)
const error = ref('')
const isValid = ref(false)

function handleFileChange(event) {
  error.value = ''
  isValid.value = false
  preview.value = null

  const file = event.target.files[0]
  if (!file) return

  const validTypes = ['image/jpeg', 'image/png']
  if (!validTypes.includes(file.type)) {
    error.value = 'Format non supporté. Choisissez un fichier JPG ou PNG.'
    return
  }

  const maxSize = 5 * 1024 * 1024
  if (file.size > maxSize) {
    error.value = 'Fichier trop volumineux. 5 Mo maximum.'
    return
  }

  const reader = new FileReader()
  reader.onload = (e) => {
    const img = new Image()
    img.onload = () => {
      if (img.width < 500 || img.height < 500) {
        error.value = 'L’image doit faire au moins 500×500 pixels.'
      } else {
        isValid.value = true
        preview.value = e.target.result
      }
    }
    img.src = e.target.result
  }
  reader.readAsDataURL(file)
}

function handleSubmit() {
  alert('Image envoyée avec succès 🚀 (mock)')
}
</script>