<template>
  <div class="space-y-6">
    <h2 class="text-2xl font-semibold text-[#1b263b]">Indicateurs en temps réel</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
      <UCard
        v-for="(item, index) in indicators"
        :key="index"
      >
        <template #header>
          <h3 class="text-base font-semibold text-[#1b263b]">{{ item.label }}</h3>
        </template>
        <div class="py-6 flex items-center justify-center">
          <p class="text-xl font-medium text-[#1b263b]">
            {{ item.value || '—' }}
          </p>
        </div>
      </UCard>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

// 🔑 Récupération de la clé API depuis .env
const apiKey = import.meta.env.VITE_OPENWEATHER_API_KEY;

const indicators = ref([
  { label: "Localisation", value: "Paris" },
  { label: "Population", value: "2 161 000 hab" },
  { label: "Jour", value: new Date().toLocaleDateString("fr-FR", { weekday: "long" }) },
  { label: "Météo", value: "Chargement..." },
  { label: "Date acquisition", value: new Date().toLocaleString("fr-FR") },
])

const fetchWeather = async () => {
  const url = `https://api.openweathermap.org/data/2.5/weather?q=Paris&units=metric&lang=fr&appid=${apiKey}`;

  try {
    const response = await axios.get(url);
    const data = response.data;
    const weatherDesc = data.weather[0].description; // ex: 'partiellement nuageux'
    const temperature = Math.round(data.main.temp);
    const meteo = `${weatherDesc}, ${temperature}°C`;

    const meteoIndex = indicators.value.findIndex(i => i.label === "Météo");
    if (meteoIndex !== -1) {
      indicators.value[meteoIndex].value = meteo;
    }
  } catch (error) {
    console.error("Erreur récupération météo :", error.response?.data || error.message);
    const meteoIndex = indicators.value.findIndex(i => i.label === "Météo");
    if (meteoIndex !== -1) {
      indicators.value[meteoIndex].value = "Erreur";
    }
  }
}

onMounted(() => {
  fetchWeather();
  setInterval(fetchWeather, 60 * 60 * 1000); // actualisation toutes les 1h
});
</script>
