<template>
  <div class="space-y-10">
    <!-- Filtres -->
    <UCard>
      <template #header>
        <h3 class="text-lg font-semibold text-[#1b263b]">
          {{ translations[currentLanguage].filtre }}
        </h3>
      </template>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <USelect v-model="selectedEtat" :items="etats" placeholder="Filtrer par état" />
        <USelect v-model="selectedPeriod" :items="periodes" placeholder="Filtrer par période" />
      </div>
    </UCard>

    <!-- Indicateurs en temps réel -->
    <RealTimeIndicators :indicators="realtimeIndicators || {}" />

    <!-- Carte -->
    <UCard class="mt-12">
      <template #header>
        <h3 class="text-lg font-semibold text-[#1b263b]">
          Carte des marchés, chantiers, poubelles et zones à risques
        </h3>
      </template>

      <div class="flex flex-wrap gap-4 mb-4">
        <UCheckbox v-model="showMarches" label="Marchés actifs aujourd'hui" />
        <UCheckbox v-model="showChantiers" label="Chantiers en cours" />
        <UCheckbox v-model="showDepots" label="Poubelles" />
        <UCheckbox v-model="showZones" label="Zones à risques" />
      </div>

      <CarteMarchesChantiers
        :showMarches="showMarches"
        :showChantiers="showChantiers"
        :showDepots="showDepots"
        :showZones="showZones"
      />
    </UCard>

    <!-- Titre section visualisations -->
    <h2 class="text-2xl font-semibold text-[#1b263b]">
      Visualisations interactives
    </h2>

    <!-- Visualisations -->
    <div v-if="pending || histoPending" class="text-center py-10">
      <span class="text-[#1b263b]">{{ translations[currentLanguage].loaddash }}</span>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
      <!-- Nombre total d'images -->
      <ChartCard :title="translations[currentLanguage].visu1title">
        <Bar :data="barImages" :options="chartOptions" />
      </ChartCard>

      <!-- Répartition des annotations -->
      <ChartCard :title="translations[currentLanguage].visu2title">
        <Pie :data="pieAnnotations" :options="pieOptions" />
      </ChartCard>

      <!-- Couleur moyenne globale -->
      <ChartCard title="Couleur moyenne globale">
        <div class="relative flex items-center justify-center" style="height: 200px; width: 200px;">
          <Doughnut :data="rgbDoughnutData" :options="doughnutOptions" class="relative z-10" />
          <div
            class="absolute rounded-full border border-[#1b263b] shadow-md"
            :style="{ backgroundColor: avgRGBColor, width: '80px', height: '80px', zIndex: 0 }"
          />
        </div>
      </ChartCard>

      <!-- Histogramme global des tailles -->
      <ChartCard title="Histogramme global des tailles (px)">
        <Bar :data="globalSizeHistogram" :options="chartOptions" />
      </ChartCard>

      <!-- Histogramme des couleurs dominantes -->
      <ChartCard title="Histogramme des couleurs (tons dominants)">
        <Bar :data="barCouleurs" :options="chartOptions" />
      </ChartCard>

      <!-- Histogramme des contrastes -->
      <ChartCard title="Histogramme des contrastes">
        <Bar :data="barContrastes" :options="chartOptions" />
      </ChartCard>
    </div>
  </div>
</template>

<script setup>
import { useWebSocket } from '~/composables/useWebSocket'
import RealTimeIndicators from '~/components/RealTimeIndicators.vue'
import { ref, computed, inject } from "vue";
import { Bar, Pie, Doughnut } from "vue-chartjs";
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement,
  CategoryScale,
  LinearScale,
} from "chart.js";
import ChartCard from "./ChartCard.vue";
import CarteMarchesChantiers from './Carte.vue'

// ✅ Déclarations des switches
const showMarches = ref(true)
const showChantiers = ref(true)
const showDepots = ref(true)
const showZones = ref(true) 

// ChartJS register
ChartJS.register(Title, Tooltip, Legend, ArcElement, BarElement, CategoryScale, LinearScale);

// WebSocket temps réel
const { data: realtimeIndicators } = useWebSocket()

// Traduction
const currentLanguage = inject('currentLanguage')
const translations = inject('translations')

// Filtres
const etats = computed(() => [
  { label: translations[currentLanguage.value]?.allStates ?? "Tous", value: "all" },
  { label: translations[currentLanguage.value]?.emptyState ?? "Vide", value: "vide" },
  { label: translations[currentLanguage.value]?.overflowState ?? "Débordée", value: "debordee" },
]);

const periodes = computed(() => [
  { label: translations[currentLanguage.value]?.allPeriods ?? "Toutes périodes", value: "all" },
  { label: translations[currentLanguage.value]?.last7Days ?? "7 derniers jours", value: "7days" },
  { label: translations[currentLanguage.value]?.last30Days ?? "30 derniers jours", value: "30days" },
  { label: translations[currentLanguage.value]?.thisYear ?? "Cette année", value: "year" },
]);

const selectedEtat = ref(etats.value[0].value);
const selectedPeriod = ref(periodes.value[0].value);

// API dashboard
const { data, pending, error } = await useFetch("http://127.0.0.1:8000/dashboard/");

// API histograms globaux
const { data: histoData, pending: histoPending, error: histoError } = await useFetch("http://127.0.0.1:8000/img/global_histograms/");

// Graphes dashboard
const barImages = computed(() => ({
  labels: ["Images"],
  datasets: [{
    label: "Total",
    data: [data.value?.total_images ?? 0],
    backgroundColor: "hsl(217, 91%, 60%)",
    borderRadius: 12,
  }],
}));

const pieAnnotations = computed(() => ({
  labels: [
    translations[currentLanguage.value]?.emptyLabel ?? "Vide",
    translations[currentLanguage.value]?.fullLabel ?? "Pleine",
    translations[currentLanguage.value]?.noLabel ?? "Sans label",
  ],
  datasets: [{
    label: "Annotations",
    data: [
      data.value?.anotations_balance.empty_count ?? 0,
      data.value?.anotations_balance.full_count ?? 0,
      data.value?.anotations_balance.no_labeled_count ?? 0,
    ],
    backgroundColor: ["#4CAF50", "#FB8C00", "#9E9E9E"],
    borderColor: "#fff",
    borderWidth: 2,
  }],
}));

// Histogramme tailles global
const globalSizeHistogram = computed(() => ({
  labels: ["<500px", "500-800px", "800-1200px", ">1200px"],
  datasets: [{
    label: "Nombre d’images",
    data: [
      histoData.value?.Size_Histogram?.["<500px"] ?? 0,
      histoData.value?.Size_Histogram?.["500-800px"] ?? 0,
      histoData.value?.Size_Histogram?.["800-1200px"] ?? 0,
      histoData.value?.Size_Histogram?.[">1200px"] ?? 0,
    ],
    backgroundColor: ["#4CAF50", "#FFCA28", "#FB8C00", "#E53935"],
    borderRadius: 8,
  }],
}));

// Histogramme couleurs dominantes global
const barCouleurs = computed(() => ({
  labels: ["Rouge", "Vert", "Bleu"],
  datasets: [{
    label: "Couleur dominante",
    data: [
      histoData.value?.Dominant_Colors?.Rouge ?? 0,
      histoData.value?.Dominant_Colors?.Vert ?? 0,
      histoData.value?.Dominant_Colors?.Bleu ?? 0,
    ],
    backgroundColor: ["#FF4C4C", "#4CAF50", "#2196F3"],
    borderRadius: 8,
  }],
}));

// Histogramme contrastes global
const barContrastes = computed(() => ({
  labels: ["Faible", "Moyen", "Élevé"],
  datasets: [{
    label: "Contrastes",
    data: [
      histoData.value?.Contrast_Histogram?.Faible ?? 0,
      histoData.value?.Contrast_Histogram?.Moyen ?? 0,
      histoData.value?.Contrast_Histogram?.Élevé ?? 0,
    ],
    backgroundColor: ["#9E9E9E", "#FFC107", "#FF5722"],
    borderRadius: 8,
  }],
}));

// Couleur moyenne et doughnut RGB
const avgRGB = computed(() => {
  const avg = data.value?.anotations_balance?.Avg_RGB;
  if (!avg) return { R: 0, G: 0, B: 0 };
  return {
    R: Math.round(avg.Avg_R),
    G: Math.round(avg.Avg_G),
    B: Math.round(avg.Avg_B),
  };
});

const avgRGBColor = computed(() => `rgb(${avgRGB.value.R}, ${avgRGB.value.G}, ${avgRGB.value.B})`);

const rgbDoughnutData = computed(() => ({
  labels: ["R", "G", "B"],
  datasets: [{
    data: [avgRGB.value.R, avgRGB.value.G, avgRGB.value.B],
    backgroundColor: ["#FF4C4C", "#4CAF50", "#2196F3"],
    borderWidth: 0,
  }],
}));

// Chart options
const chartOptions = {
  responsive: true,
  plugins: { legend: { display: false } },
  scales: { y: { beginAtZero: true } },
};

const doughnutOptions = {
  responsive: true,
  cutout: "60%",
  plugins: {
    tooltip: {
      callbacks: {
        label: function (context) {
          const label = context.label || "";
          const value = context.parsed;
          const data = context.chart.data.datasets[0].data;
          const total = data.reduce((a, b) => a + b, 0);
          const percentage = total ? ((value / total) * 100).toFixed(1) : 0;
          return `${label}: ${value} (${percentage}%)`;
        },
      },
    },
    legend: { display: false },
  },
};

const pieOptions = {
  responsive: true,
  plugins: {
    tooltip: {
      callbacks: {
        label: function (context) {
          const label = context.label || "";
          const value = context.parsed;
          const data = context.chart.data.datasets[0].data;
          const total = data.reduce((a, b) => a + b, 0);
          const percentage = total ? ((value / total) * 100).toFixed(1) : 0;
          return `${label}: ${value} (${percentage}%)`;
        },
      },
    },
    legend: {
      position: "bottom",
      labels: { color: "#1b263b", boxWidth: 16, padding: 12 },
    },
  },
};

console.log("Dashboard data", data.value);
console.log("Histogram data", histoData.value);
</script>