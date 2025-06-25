<template>
  <div class="space-y-10">
    <!-- Filtres -->
    <UCard>
      <template #header>
        <h3 class="text-lg font-semibold text-[#1b263b]">Filtres</h3>
      </template>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <USelect v-model="selectedEtat" :items="etats" placeholder="Filtrer par état" />
        <USelect v-model="selectedPeriod" :items="periodes" placeholder="Filtrer par période" />
      </div>
    </UCard>

    <!-- Visualisations -->
    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
      <ChartCard title="Nombre total d’images">
        <Bar :data="barImages" :options="chartOptions" />
      </ChartCard>

      <ChartCard title="Répartition des annotations">
        <Pie :data="pieAnnotations" :options="pieOptions" />
      </ChartCard>

      <ChartCard title="Histogramme des tailles (px)">
        <Bar :data="barTailles" :options="chartOptions" />
      </ChartCard>

      <ChartCard title="Histogramme des couleurs (tons dominants)">
        <Bar :data="barCouleurs" :options="chartOptions" />
      </ChartCard>

      <ChartCard title="Histogramme des contrastes">
        <Bar :data="barContrastes" :options="chartOptions" />
      </ChartCard>
    </div>
  </div>
</template>

<script setup>
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement,
  CategoryScale,
  LinearScale
} from 'chart.js'
import { Bar, Pie } from 'vue-chartjs'
import ChartCard from './ChartCard.vue' // Carte modulaire avec centrement

ChartJS.register(Title, Tooltip, Legend, ArcElement, BarElement, CategoryScale, LinearScale)

// États & périodes (filtres simulés)
const etats = [
  { label: 'Tous', value: 'all' },
  { label: 'Vide', value: 'vide' },
  { label: 'Moitié pleine', value: 'moitie' },
  { label: 'Pleine', value: 'pleine' },
  { label: 'Débordée', value: 'debordee' }
]

const periodes = [
  { label: 'Toutes périodes', value: 'all' },
  { label: '7 derniers jours', value: '7days' },
  { label: '30 derniers jours', value: '30days' },
  { label: 'Cette année', value: 'year' }
]

const selectedEtat = ref(etats[0].value)
const selectedPeriod = ref(periodes[0].value)

// Données simulées
const barImages = {
  labels: ['Images'],
  datasets: [{
    label: 'Total',
    data: [72],
    backgroundColor: 'hsl(217, 91%, 60%)',
    borderRadius: 12
  }]
}

const pieAnnotations = {
  labels: ['Vide', 'Moitié pleine', 'Pleine', 'Débordée'],
  datasets: [{
    label: 'Annotations',
    data: [10, 20, 30, 12],
    backgroundColor: [
      'hsl(217, 91%, 60%)',
      'hsl(190, 85%, 65%)',
      'hsl(160, 80%, 55%)',
      'hsl(40, 90%, 65%)'
    ],
    borderColor: '#fff',
    borderWidth: 2
  }]
}

const barTailles = {
  labels: ['<500px', '500-800px', '800-1200px', '>1200px'],
  datasets: [{
    label: 'Nombre',
    data: [5, 18, 35, 14],
    backgroundColor: 'hsl(160, 80%, 55%)',
    borderRadius: 8
  }]
}

const barCouleurs = {
  labels: ['Gris', 'Vert', 'Bleu', 'Jaune', 'Autre'],
  datasets: [{
    label: 'Occurrences',
    data: [12, 8, 25, 14, 7],
    backgroundColor: 'hsl(190, 85%, 65%)',
    borderRadius: 8
  }]
}

const barContrastes = {
  labels: ['Faible', 'Moyen', 'Élevé'],
  datasets: [{
    label: 'Images',
    data: [10, 32, 28],
    backgroundColor: 'hsl(40, 90%, 65%)',
    borderRadius: 8
  }]
}

const chartOptions = {
  responsive: true,
  plugins: {
    legend: { display: false }
  },
  scales: {
    y: { beginAtZero: true }
  }
}

const pieOptions = {
  responsive: true,
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        color: '#1b263b',
        boxWidth: 16,
        padding: 12
      }
    }
  }
}
</script>