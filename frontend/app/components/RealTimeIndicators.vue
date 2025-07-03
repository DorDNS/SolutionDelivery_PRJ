<template>
  <div class="space-y-6">
    <h2 class="text-2xl font-semibold text-[#1b263b]">Indicateurs en temps réel</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
      <UCard v-for="(item, index) in indicators" :key="index">
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

const apiKey = import.meta.env.VITE_OPENWEATHER_API_KEY

const indicators = ref([
  { label: "Localisation", value: "Chargement..." },
  { label: "Population", value: "—" },
  { label: "Jour", value: new Date().toLocaleDateString("fr-FR", { weekday: "long" }) },
  { label: "Météo", value: "Chargement..." },
  { label: "Date acquisition", value: new Date().toLocaleString("fr-FR") },
])

const updateIndicator = (label, value) => {
  const index = indicators.value.findIndex(i => i.label === label)
  if (index !== -1) {
    indicators.value[index].value = value
  }
}

// Nouvelle fonction pour récupérer la population via Wikidata
async function fetchPopulationFromWikidata(city) {
  try {
    // 1. Récupérer l’ID Wikidata via API MediaWiki
    const wikiIdRes = await axios.get(`https://fr.wikipedia.org/w/api.php`, {
      params: {
        action: 'query',
        prop: 'pageprops',
        titles: city,
        format: 'json',
        origin: '*'  // important pour CORS
      }
    });

    const pages = wikiIdRes.data.query.pages;
    const page = Object.values(pages)[0];
    if (!page || !page.pageprops || !page.pageprops.wikibase_item) {
      return null;
    }
    const wikidataId = page.pageprops.wikibase_item;

    // 2. Requête SPARQL pour récupérer la population la plus récente
    const sparqlQuery = `
      SELECT ?population WHERE {
        wd:${wikidataId} wdt:P1082 ?population .
      }
      ORDER BY DESC(?population)
      LIMIT 1
    `;

    const sparqlUrl = `https://query.wikidata.org/sparql?query=${encodeURIComponent(sparqlQuery)}&format=json`;
    const sparqlRes = await axios.get(sparqlUrl);

    const results = sparqlRes.data.results.bindings;
    if (results.length > 0) {
      return parseInt(results[0].population.value).toLocaleString('fr-FR') + ' hab';
    }
    return null;

  } catch (e) {
    console.error("Erreur récupération population Wikidata", e);
    return null;
  }
}

const fetchLocationAndWeather = async () => {
  if (!navigator.geolocation) {
    updateIndicator("Localisation", "Non supportée")
    updateIndicator("Population", "Non trouvée")
    updateIndicator("Météo", "Non trouvée")
    return
  }

  navigator.geolocation.getCurrentPosition(async (pos) => {
    const { latitude, longitude } = pos.coords
    let city = ""

    try {
      const res = await axios.get(
        `https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${latitude}&longitude=${longitude}&localityLanguage=fr`
      )
      city = res.data.city || res.data.locality || res.data.principalSubdivision || "Inconnue"
      city = city.replace(/(\d+e|Arrondissement|Arr\.)/gi, "").trim()
      updateIndicator("Localisation", city)
    } catch (err) {
      console.error("Erreur géolocalisation inverse :", err)
      updateIndicator("Localisation", "Erreur")
      updateIndicator("Population", "Erreur")
      updateIndicator("Météo", "Erreur")
      return
    }

    // Population via Wikidata
    const population = await fetchPopulationFromWikidata(city);
    if (population) {
      updateIndicator("Population", population);
    } else {
      updateIndicator("Population", "Non trouvée");
    }

    // Météo
    try {
      const weather = await axios.get(`https://api.openweathermap.org/data/2.5/weather`, {
        params: {
          lat: latitude,
          lon: longitude,
          units: 'metric',
          lang: 'fr',
          appid: apiKey
        }
      })
      const desc = weather.data.weather[0].description
      const temp = Math.round(weather.data.main.temp)
      updateIndicator("Météo", `${desc}, ${temp}°C`)
    } catch (err) {
      console.error("Erreur météo :", err)
      updateIndicator("Météo", "Erreur")
    }

  }, (err) => {
    console.error("Erreur géolocalisation navigateur :", err)
    updateIndicator("Localisation", "Refusée")
    updateIndicator("Population", "Inconnue")
    updateIndicator("Météo", "Inconnue")
  })
}

onMounted(() => {
  fetchLocationAndWeather()
  setInterval(fetchLocationAndWeather, 60 * 60 * 1000)
})
</script>
