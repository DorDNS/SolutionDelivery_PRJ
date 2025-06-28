<template>
    <div ref="mapContainer" class="h-64 w-full rounded-lg shadow border" />
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import 'leaflet/dist/leaflet.css'
  
  const props = defineProps({
    lat: Number,
    lng: Number,
    city: String
  })
  
  const mapContainer = ref(null)
  
  onMounted(async () => {
    const L = await import('leaflet')
  
    const map = L.map(mapContainer.value).setView([props.lat, props.lng], 13)
  
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map)
  
    L.marker([props.lat, props.lng])
      .addTo(map)
      .bindPopup(`<strong>${props.city}</strong>`)
      .openPopup()
  })
  </script>
  