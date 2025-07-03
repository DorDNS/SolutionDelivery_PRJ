<template>
  <div class="space-y-6">
    <h2 class="text-2xl font-semibold text-[#1b263b]">{{ translations[currentLanguage].realtimetitle }}</h2>
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
import { ref, inject, onMounted } from 'vue'
import axios from 'axios'

const currentLanguage = inject('currentLanguage')
const translations = inject('translations')

const apiKey = import.meta.env.VITE_OPENWEATHER_API_KEY

// Structure réactive pour les valeurs des indicateurs
const indicatorValues = ref({
  Localisation: "...",
  Population: "—",
  Jour: new Date().toLocaleDateString(currentLanguage.value === "fr" ? "fr-FR" : "en-US", { weekday: "long" }),
  Météo: "...",
  Date: new Date().toLocaleString(currentLanguage.value === "fr" ? "fr-FR" : "en-US"),
});

// Labels dynamiques avec computed
const indicators = computed(() => [
  { label: translations[currentLanguage.value]?.loc ?? "Localisation", value: indicatorValues.value.Localisation },
  { label: translations[currentLanguage.value]?.pop ?? "Population", value: indicatorValues.value.Population },
  { label: translations[currentLanguage.value]?.day ?? "Jour", value: indicatorValues.value.Jour },
  { label: translations[currentLanguage.value]?.meteo ?? "Météo", value: indicatorValues.value.Météo },
  { label: translations[currentLanguage.value]?.gettime ?? "Date d’acquisition", value: indicatorValues.value.Date },
]);

// Fonction pour mettre à jour les valeurs des indicateurs
const updateIndicator = (key, value) => {
  if (Object.prototype.hasOwnProperty.call(indicatorValues.value, key)) {
    indicatorValues.value[key] = value;
  } else {
    console.warn(`Clé inconnue : ${key}`);
  }
};

// Watcher pour la langue courante
watch(currentLanguage, (newLang) => {
  updateIndicator("Jour", new Date().toLocaleDateString(newLang === "fr" ? "fr-FR" : "en-US", { weekday: "long" }));
  updateIndicator("Date", new Date().toLocaleString(newLang === "fr" ? "fr-FR" : "en-US"));
  fetchLocationAndWeather()
  setInterval(fetchLocationAndWeather, 60 * 60 * 1000)
});

// Récupérer la population via Wikidata
async function fetchPopulationFromWikidata(city) {
  try {
    // Récupère l’ID Wikidata via API MediaWiki
    const wikiIdRes = await axios.get(`https://fr.wikipedia.org/w/api.php`, {
      params: {
        action: 'query',
        prop: 'pageprops',
        titles: city,
        format: 'json',
        origin: '*'
      }
    });

    const pages = wikiIdRes.data.query.pages;
    const page = Object.values(pages)[0];
    if (!page || !page.pageprops || !page.pageprops.wikibase_item) {
      return null;
    }
    const wikidataId = page.pageprops.wikibase_item;

    //Requête SPARQL pour récupérer la population la plus récente
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
      return parseInt(results[0].population.value).toLocaleString('fr-FR') + " " + translations[currentLanguage.value].hab || " hab";
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

    try {
      const weather = await axios.get(`https://api.openweathermap.org/data/2.5/weather`, {
        params: {
          lat: latitude,
          lon: longitude,
          units: 'metric',
          lang: currentLanguage.value === "fr" ? 'fr' : 'en',
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
