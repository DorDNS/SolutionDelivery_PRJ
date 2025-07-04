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
          {{ translations[currentLanguage].cartetitle }}
        </h3>
      </template>

      <div class="flex flex-wrap gap-4 mb-4">
        <UCheckbox v-model="showDepots" :label="translations[currentLanguage].checkboxdepots" />
        <UCheckbox v-model="showChantiers" :label="translations[currentLanguage].checkboxchantiers" />
        <UCheckbox v-model="showMarches" :label="translations[currentLanguage].checkboxmarche" />
        <UCheckbox v-model="showZones" :label="translations[currentLanguage].checkboxzones" />
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
      {{ translations[currentLanguage].dashboardDescription }}
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

      <!-- Histogramme global des tailles -->
      <ChartCard :title="translations[currentLanguage].visu4title">
        <Bar :data="globalSizeHistogram" :options="chartOptions" />
      </ChartCard>

      <!-- Histogramme des couleurs dominantes -->
      <ChartCard :title="translations[currentLanguage].visu5title">
        <Bar :data="barCouleurs" :options="chartOptions" />
      </ChartCard>

      <!-- Histogramme des contrastes -->
      <ChartCard :title="translations[currentLanguage].visu6title">
        <Bar :data="barContrastes" :options="chartOptions" />
      </ChartCard>

      <!-- Histogramme des contours -->
      <ChartCard :title="translations[currentLanguage].visu7title">
        <Bar :data="barContours" :options="chartOptions" />
      </ChartCard>
      
      <!-- Histogramme des tons dominants par label -->
      <ChartCard :title="translations[currentLanguage].visu9title">
        <Bar :data="barTonsDominants" :options="chartOptions" />
      </ChartCard>

      <!-- Histogramme des contrastes par label -->
      <ChartCard :title="translations[currentLanguage].visu10title">
        <Bar :data="barContrastesLabel" :options="chartOptions" />
      </ChartCard>

      <!-- Histogramme des contours moyens -->
      <ChartCard :title="translations[currentLanguage].visu8title">
        <Bar :data="barContoursMoy" :options="chartOptions" />
      </ChartCard>

      <!-- Couleur moyenne globale -->
      <ChartCard :title="translations[currentLanguage].visu3title">
        <div class="relative flex items-center justify-center" style="height: 200px; width: 200px;">
          <Doughnut :data="rgbDoughnutData" :options="doughnutOptions" class="relative z-10" />
          <div
            class="absolute rounded-full border border-[#1b263b] shadow-md"
            :style="{ backgroundColor: avgRGBColor, width: '80px', height: '80px', zIndex: 0 }"
          />
        </div>
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

//Déclarations des switches
const showMarches = ref(false)
const showChantiers = ref(false)
const showDepots = ref(true)
const showZones = ref(false) 

// ChartJS register
ChartJS.register(Title, Tooltip, Legend, ArcElement, BarElement, CategoryScale, LinearScale);

// WebSocket temps réel
const { data: realtimeIndicators } = useWebSocket()

//Traduction
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
    label: translations[currentLanguage.value].nbimg,
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
  labels: [
    translations[currentLanguage.value]?.Red ?? "Rouge",
    translations[currentLanguage.value]?.Green ?? "Vert",
    translations[currentLanguage.value]?.Blue ?? "Bleu",
  ],
  datasets: [{
    label: translations[currentLanguage.value].nbimg,
    data: [
      histoData.value?.Dominant_Colors?.Rouge ?? 0,
      histoData.value?.Dominant_Colors?.Vert ?? 0,
      histoData.value?.Dominant_Colors?.Bleu ?? 0,
    ],
    backgroundColor: ["#FF4C4C", "#4CAF50", "#2196F3"],
    borderRadius: 8,
  }],
}));

//Histogramme des tons dominants pour les labels
const barTonsDominants = computed(() => ({
  labels: [
  translations[currentLanguage.value]?.fullLabel ?? "Pleine",
    translations[currentLanguage.value]?.emptyLabel ?? "Vide",
  ],
  datasets: [
    {
      label: translations[currentLanguage.value]?.Red ?? "Rouge",
      data: [
        histoData.value?.Dominant_Colors_Label?.Vide?.Rouge ?? 0,
        histoData.value?.Dominant_Colors_Label?.Pleine?.Rouge ?? 0,
      ],
      backgroundColor: "#FF4C4C",
    },
    {
      label: translations[currentLanguage.value]?.Green ?? "Vert",
      data: [
        histoData.value?.Dominant_Colors_Label?.Vide?.Vert ?? 0,
        histoData.value?.Dominant_Colors_Label?.Pleine?.Vert ?? 0,
      ],
      backgroundColor: "#4CAF50",
    },
    {
      label: translations[currentLanguage.value]?.Blue ?? "Bleu",
      data: [
        histoData.value?.Dominant_Colors_Label?.Vide?.Bleu ?? 0,
        histoData.value?.Dominant_Colors_Label?.Pleine?.Bleu ?? 0,
      ],
      backgroundColor: "#2196F3",
    },
  ],
}));

// Histogramme contrastes global
const barContrastes = computed(() => ({
  labels: [
    translations[currentLanguage.value]?.low ?? "Faible",
    translations[currentLanguage.value]?.medium ?? "Moyen",
    translations[currentLanguage.value]?.high ?? "Haut",
  ],
  datasets: [{
    label: translations[currentLanguage.value].nbimg,
    data: [
      histoData.value?.Contrast_Histogram?.Faible ?? 0,
      histoData.value?.Contrast_Histogram?.Moyen ?? 0,
      histoData.value?.Contrast_Histogram?.Élevé ?? 0,
    ],
    backgroundColor: ["#FF7F27", "#006FFF", "#000000"],
    borderRadius: 8,
  }],
}));

// Histogramme contrastes moyen par label
const barContrastesLabel = computed(() => ({
  labels: [
    translations[currentLanguage.value]?.fullLabel ?? "Pleine",
    translations[currentLanguage.value]?.emptyLabel ?? "Vide",
  ],
  datasets: [
    {
      label: translations[currentLanguage.value]?.low ?? "Faible",
      data: [
        histoData.value?.Contrast_Level_Label?.Vide?.Faible ?? 0,
        histoData.value?.Contrast_Level_Label?.Pleine?.Faible ?? 0,
      ],
      backgroundColor: "#FF7F27",
    },
    {
      label: translations[currentLanguage.value]?.medium ?? "Moyen",
      data: [
        histoData.value?.Contrast_Level_Label?.Vide?.Moyen ?? 0,
        histoData.value?.Contrast_Level_Label?.Pleine?.Moyen ?? 0,
      ],
      backgroundColor: "#006FFF",
    },
    {
      label: translations[currentLanguage.value]?.high ?? "Élevé",
      data: [
        histoData.value?.Contrast_Level_Label?.Vide?.Élevé ?? 0,
        histoData.value?.Contrast_Level_Label?.Pleine?.Élevé ?? 0,
      ],
      backgroundColor: "#000000",
    },
  ],
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

// Histogramme contours global
const barContours = computed(() => ({
  labels: ["<5000", "5000-10000", "10000-50000", ">50000"],
  datasets: [{
    label: translations[currentLanguage.value].nbimg,
    data: [
      histoData.value?.Edges_Histogram?.["<5000"] ?? 0,
      histoData.value?.Edges_Histogram?.["5000-10000"] ?? 0,
      histoData.value?.Edges_Histogram?.["10000-50000"] ?? 0,
      histoData.value?.Edges_Histogram?.[">50000"] ?? 0,
    ],
    backgroundColor: ["#58508d", "#bc5090", "#ff6361", "#ffa600"],
    borderRadius: 8,
  }],
}));

// Histogramme contours moyen par label
const barContoursMoy = computed(() => ({
  labels: [
    translations[currentLanguage.value]?.fullLabel ?? "Pleine",
    translations[currentLanguage.value]?.emptyLabel ?? "Vide",
  ],
  datasets: [{
    label: translations[currentLanguage.value].nbmoycontours,
    data: [
      histoData.value?.Edges_Average?.["Pleine"] ?? 0,
      histoData.value?.Edges_Average?.["Vide"] ?? 0,
    ],
    backgroundColor: ["#FB8C00", "#4CAF50"],
    borderRadius: 8,
  }],
}));

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
  scales: {
    x: {
      stacked: true,
    },
    y: {
      stacked: true,
      beginAtZero: true,
    },
  },
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