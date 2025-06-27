<template>
  <UCard class="w-full">
    <template #header>
      <h3 class="text-lg font-semibold text-[#1b263b]">Carte des dépôts sauvages</h3>
    </template>
    <div id="map" class="h-[500px] rounded-lg" />
  </UCard>
</template>

<script setup>
import { onMounted } from 'vue'
import 'leaflet/dist/leaflet.css'

onMounted(async () => {
  const L = await import('leaflet')

  const map = L.map('map').setView([48.8566, 2.3522], 12)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map)

  const fakeMarkers = [
    { lat: 48.8584, lng: 2.2945, label: 'Tour Eiffel' },
    { lat: 48.8606, lng: 2.3376, label: 'Louvre' },
    { lat: 48.8738, lng: 2.2950, label: 'Arc de Triomphe' }
  ]

  fakeMarkers.forEach(({ lat, lng, label }) => {
    L.marker([lat, lng])
      .addTo(map)
      .bindPopup(`<strong>${label}</strong><br>Dépôt sauvage détecté`)
  })
})
</script>