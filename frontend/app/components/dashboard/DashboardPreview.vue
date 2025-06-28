<template>
    <div class="space-y-10">
        <!-- Filtres -->
        <UCard>
            <template #header>
                <h3 class="text-lg font-semibold text-[#1b263b]">Filtres</h3>
            </template>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <USelect
                    v-model="selectedEtat"
                    :items="etats"
                    placeholder="Filtrer par état"
                />
                <USelect
                    v-model="selectedPeriod"
                    :items="periodes"
                    placeholder="Filtrer par période"
                />
            </div>
        </UCard>

        <!-- Visualisations -->
        <div v-if="pending" class="text-center py-10">
            <span class="text-[#1b263b]"
                >Chargement des données du dashboard...</span
            >
        </div>

        <div
            v-else
            class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6"
        >
            <ChartCard title="Nombre total d’images">
                <Bar :data="barImages" :options="chartOptions" />
            </ChartCard>

            <ChartCard title="Répartition des annotations">
                <Pie :data="pieAnnotations" :options="pieOptions" />
            </ChartCard>

            <ChartCard title="Couleur moyenne globale">
                <div
                    class="relative flex items-center justify-center"
                    style="height: 200px; width: 200px"
                >
                    <!-- Doughnut Chart -->
                    <Doughnut
                        :data="rgbDoughnutData"
                        :options="doughnutOptions"
                    />

                    <!-- Couleur moyenne au centre -->
                    <div
                        class="absolute rounded-full border border-[#1b263b] shadow-md"
                        :style="{
                            backgroundColor: avgRGBColor,
                            width: '80px',
                            height: '80px',
                        }"
                    />
                </div>
            </ChartCard>

            <ChartCard title="Histogramme global des tailles (px)">
                <Bar :data="globalSizeHistogram" :options="chartOptions" />
            </ChartCard>

            <ChartCard title="Histogramme des couleurs (tons dominants)">
                <Bar :data="barCouleurs" :options="chartOptions" />
            </ChartCard>

            <ChartCard title="Histogramme des contrastes">
                <Bar :data="barContrastes" :options="chartOptions" />
            </ChartCard>
        </div>

        <MapDepots />
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
    LinearScale,
} from "chart.js";
import { Bar, Pie, Doughnut } from "vue-chartjs";
import ChartCard from "./ChartCard.vue";
import MapDepots from "./MapDepots.vue";
import { ref, computed } from "vue";

ChartJS.register(
    Title,
    Tooltip,
    Legend,
    ArcElement,
    BarElement,
    CategoryScale,
    LinearScale
);

// États & périodes (filtres simulés)
const etats = [
    { label: "Tous", value: "all" },
    { label: "Vide", value: "vide" },
    { label: "Débordée", value: "debordee" },
];

const periodes = [
    { label: "Toutes périodes", value: "all" },
    { label: "7 derniers jours", value: "7days" },
    { label: "30 derniers jours", value: "30days" },
    { label: "Cette année", value: "year" },
];

const selectedEtat = ref(etats[0].value);
const selectedPeriod = ref(periodes[0].value);

const {
    data: histoData,
    pending: histoPending,
    error: histoError,
} = await useFetch("http://127.0.0.1:8000/img/global_histograms/");

const globalSizeHistogram = computed(() => ({
    labels: ["<500px", "500-800px", "800-1200px", ">1200px"],
    datasets: [
        {
            label: "Nombre d’images",
            data: [
                histoData.value?.Size_Histogram?.["<500px"] ?? 0,
                histoData.value?.Size_Histogram?.["500-800px"] ?? 0,
                histoData.value?.Size_Histogram?.["800-1200px"] ?? 0,
                histoData.value?.Size_Histogram?.[">1200px"] ?? 0,
            ],
            backgroundColor: ["#4CAF50", "#FFCA28", "#FB8C00", "#E53935"],
            borderRadius: 8,
        },
    ],
}));

// 🔗 API call
const { data, pending, error } = await useFetch(
    "http://127.0.0.1:8000/dashboard/"
);

// 📊 Graphes dynamiques
const barImages = computed(() => ({
    labels: ["Images"],
    datasets: [
        {
            label: "Total",
            data: [data.value?.total_images ?? 0],
            backgroundColor: "hsl(217, 91%, 60%)",
            borderRadius: 12,
        },
    ],
}));

const pieAnnotations = computed(() => ({
    labels: ["Vide", "Pleine", "Sans label"],
    datasets: [
        {
            label: "Annotations",
            data: [
                data.value?.anotations_balance.empty_count ?? 0,
                data.value?.anotations_balance.full_count ?? 0,
                data.value?.anotations_balance.no_labeled_count ?? 0,
            ],
            backgroundColor: ["#4CAF50", "#FB8C00", "#9E9E9E"],
            borderColor: "#fff",
            borderWidth: 2,
        },
    ],
}));

const barCouleurs = computed(() => ({
    labels: ["Gris", "Vert", "Bleu", "Jaune", "Autre"],
    datasets: [
        {
            label: "Occurrences",
            data: [
                data.value?.histogram_couleurs?.Gris ?? 0,
                data.value?.histogram_couleurs?.Vert ?? 0,
                data.value?.histogram_couleurs?.Bleu ?? 0,
                data.value?.histogram_couleurs?.Jaune ?? 0,
                data.value?.histogram_couleurs?.Autre ?? 0,
            ],
            backgroundColor: "hsl(190, 85%, 65%)",
            borderRadius: 8,
        },
    ],
}));

const barContrastes = computed(() => ({
    labels: ["Faible", "Moyen", "Élevé"],
    datasets: [
        {
            label: "Images",
            data: [
                data.value?.histogram_contrastes?.Faible ?? 0,
                data.value?.histogram_contrastes?.Moyen ?? 0,
                data.value?.histogram_contrastes?.Élevé ?? 0,
            ],
            backgroundColor: "hsl(40, 90%, 65%)",
            borderRadius: 8,
        },
    ],
}));

// 🎨 Couleur moyenne et doughnut RGB
const avgRGB = computed(() => {
    const avg = data.value?.anotations_balance?.Avg_RGB;
    if (!avg) {
        return { R: 0, G: 0, B: 0 };
    }
    return {
        R: Math.round(avg.Avg_R),
        G: Math.round(avg.Avg_G),
        B: Math.round(avg.Avg_B),
    };
});

const avgRGBColor = computed(
    () => `rgb(${avgRGB.value.R}, ${avgRGB.value.G}, ${avgRGB.value.B})`
);

const rgbDoughnutData = computed(() => ({
    labels: ["R", "G", "B"],
    datasets: [
        {
            data: [avgRGB.value.R, avgRGB.value.G, avgRGB.value.B],
            backgroundColor: ["#FF4C4C", "#4CAF50", "#2196F3"],
            borderWidth: 0,
        },
    ],
}));

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
                    const percentage = total
                        ? ((value / total) * 100).toFixed(1)
                        : 0;
                    return `${label}: ${value} (${percentage}%)`;
                },
            },
        },
        legend: { display: false },
    },
};

// Chart options
const chartOptions = {
    responsive: true,
    plugins: {
        legend: { display: false },
    },
    scales: {
        y: { beginAtZero: true },
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
                    const percentage = total
                        ? ((value / total) * 100).toFixed(1)
                        : 0;
                    return `${label}: ${value} (${percentage}%)`;
                },
            },
        },
        legend: {
            position: "bottom",
            labels: {
                color: "#1b263b",
                boxWidth: 16,
                padding: 12,
            },
        },
    },
};

console.log("Dashboard data", data.value);
</script>
