<template>
    <div class="min-h-[calc(100vh-64px-80px)] py-16 px-4 bg-white">
        <UContainer class="max-w-7xl mx-auto space-y-8">
            <!-- Titre -->
            <div class="text-center">
                <h1 class="text-3xl font-bold text-[#1b263b]">
                    Navigation des images
                </h1>
                <div
                    class="mt-2 text-[#415a77] text-sm flex items-center justify-center gap-2"
                >
                    <UIcon
                        name="i-heroicons-eye"
                        class="w-4 h-4 text-[#778da9]"
                    />
                    <span
                        >Utilisez les flèches ou raccourcis clavier pour
                        parcourir les images.</span
                    >
                </div>
            </div>

            <!-- Filtre -->
            <div class="flex justify-center">
                <USelect
                    v-model="filtre"
                    :items="filtres"
                    placeholder="Filtrer par statut"
                    class="w-full max-w-xs"
                    color="primary"
                    size="lg"
                />
            </div>

            <!-- Image + infos -->
            <div
                v-if="images.length > 0"
                class="flex flex-col lg:flex-row gap-10 items-start justify-center"
            >
                <!-- Image -->
                <div class="flex-1 text-center">
                    <img
                        :src="`/test/${images[index]}`"
                        :alt="images[index]"
                        class="max-h-[32rem] mx-auto rounded-xl shadow-lg border"
                    />
                    <div class="flex justify-between mt-4">
                        <UButton
                            type="button"
                            @click="precedente"
                            :disabled="index === 0"
                            color="gray"
                            variant="ghost"
                            >◀ Précédente</UButton
                        >
                        <UButton
                            type="button"
                            @click="suivante"
                            :disabled="index === images.length - 1"
                            color="gray"
                            variant="ghost"
                            >Suivante ▶</UButton
                        >
                    </div>
                </div>

                <!-- Fiche image -->
                <div
                    class="flex-1 space-y-2 bg-[#f8f9fa] p-6 rounded-xl shadow-sm border text-sm text-[#1b263b]"
                >
                    <h2 class="text-lg font-semibold mb-2">
                        Informations de l'image
                    </h2>
                    <p><strong>Taille :</strong> {{ meta.Size }} ko</p>
                    <p>
                        <strong>Dimensions :</strong> {{ meta.Width }} x
                        {{ meta.Height }}
                    </p>
                    <p><strong>Date :</strong> {{ meta.Date_taken }}</p>
                    <p>
                        <strong>Contraste :</strong> {{ meta.Contrast_level }}
                    </p>
                    <!-- Camembert RGB -->
                    <h3 class="text-base font-semibold mb-4">
                        Composition RGB :
                    </h3>
                    <div
                        class="w-full max-w-sm mx-auto bg-white p-4 rounded-xl shadow-sm border text-center text-sm text-[#1b263b]"
                    >
                        <div class="flex justify-center">
                            <div class="w-60 h-60">
                                <PieChart
                                    :data="{
                                        labels: ['Rouge', 'Vert', 'Bleu'],
                                        datasets: [
                                            {
                                                label: 'Moyenne RGB',
                                                data: [
                                                    meta.Avg_R,
                                                    meta.Avg_V,
                                                    meta.Avg_B,
                                                ],
                                                backgroundColor: [
                                                    '#e63946',
                                                    '#2a9d8f',
                                                    '#1d3557',
                                                ],
                                                borderColor: '#f8f9fa',
                                                borderWidth: 2,
                                            },
                                        ],
                                    }"
                                    :options="{
                                        responsive: true,
                                        maintainAspectRatio: false,
                                        plugins: {
                                            legend: {
                                                display: true,
                                                position: 'bottom',
                                                labels: {
                                                    color: '#1b263b',
                                                    padding: 8,
                                                    boxWidth: 12,
                                                    font: { size: 12 },
                                                },
                                            },
                                        },
                                    }"
                                />
                            </div>
                        </div>
                    </div>

                    <p><strong>Contours :</strong> {{ meta.Edges }}</p>
                    <p>
                        <strong>Statut :</strong>
                        {{ meta.Status === true ? "Pleine" : "Vide" }}
                    </p>
                    <div class="w-full max-w-sm mx-auto mt-6"></div>
                    <MapDepots :highlight-id="12" />
                </div>
            </div>

            <div v-else class="text-center text-[#778da9] text-sm">
                Aucune image à afficher.
            </div>
        </UContainer>
    </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from "vue";
import axios from "axios";
import PieChart from "~/components/PieChart.vue";
import MapDepots from "../components/dashboard/MapDepots.vue";

const location = ref({
    lat: 48.8566,
    lng: 2.3522,
    city: "Paris",
});

const allImages = [
    "00569_03.jpg",
    "908.full.jpeg",
    "1080.full.jpeg",
    "1576.full.jpeg",
    "1794.full.jpeg",
    "02587_03.jpg",
    "dsc0132_4.jpg.png",
];

const filtre = ref("all");
const filtres = [
    { label: "Toutes les images", value: "all" },
    { label: "Non annotées", value: "non_annotated" },
    { label: "Annotées", value: "annotated" },
];

const images = ref([...allImages]);
const index = ref(0);
const meta = ref({
    Size: 500,
    Width: 1920,
    Height: 1080,
    Date_taken: "2024-05-01",
    Contrast_level: 1.2,
    Avg_R: 0.2,
    Avg_V: 0.3,
    Avg_B: 0.5,
    Edges: 157,
    Status: true,
});

function precedente() {
    if (index.value > 0) index.value--;
}

function suivante() {
    if (index.value < images.value.length - 1) index.value++;
}

function handleKey(event) {
    if (event.key === "ArrowLeft") precedente();
    else if (event.key === "ArrowRight") suivante();
}

async function fetchImageData(filename) {
    try {
        const res = await axios.get(
            `http://localhost:8000/api/image/${filename}`
        );
        meta.value = res.data;
    } catch (err) {
        console.error("Erreur lors du chargement des métadonnées :", err);
        meta.value = null;
    }
}

watch(index, () => {
    fetchImageData(images.value[index.value]);
});

onMounted(() => {
    window.addEventListener("keydown", handleKey);
    fetchImageData(images.value[index.value]); // premier appel
});

onBeforeUnmount(() => {
    window.removeEventListener("keydown", handleKey);
});
</script>
