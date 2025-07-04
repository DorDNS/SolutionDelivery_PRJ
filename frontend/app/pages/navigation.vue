<template>
    <div class="min-h-[calc(100vh-64px-80px)] py-16 px-4 bg-white">
        <UContainer class="max-w-7xl mx-auto space-y-8">
            <!-- Titre -->
            <div class="text-center">
                <h1 class="text-3xl font-bold text-[#1b263b]">
                    {{ translations[currentLanguage].navtitle }}
                </h1>
                <div
                    class="mt-2 text-[#415a77] text-sm flex items-center justify-center gap-2"
                >
                    <UIcon
                        name="i-heroicons-eye"
                        class="w-4 h-4 text-[#778da9]"
                    />
                    <span
                        >{{ translations[currentLanguage].navtips }}</span
                    >
                </div>
            </div>

            <!-- Contenu -->
            <div
                v-if="meta && meta.Id_Image"
                class="flex flex-col lg:flex-row gap-10 items-start justify-center"
            >
                <!-- Colonne gauche : Image + Carte -->
                <div class="flex-1 flex flex-col gap-6">
                    <div class="text-center">
                        <img
                            :src="imageUrl"
                            alt="Image"
                            class="max-h-[32rem] mx-auto rounded-xl shadow-lg border object-contain"
                            loading="lazy"
                            @error="handleImageError"
                        />

                        <div class="flex justify-between mt-4 max-w-xs mx-auto">
                            <UButton
                                @click="precedente"
                                color="gray"
                                variant="ghost"
                                icon="i-heroicons-chevron-left"
                                >{{ translations[currentLanguage].prec }}</UButton
                            >
                            <UButton
                                @click="suivante"
                                color="gray"
                                variant="ghost"
                                icon="i-heroicons-chevron-right"
                                >{{ translations[currentLanguage].suiv }}</UButton
                            >
                        </div>
                    </div>

                    <!-- Carte de localisation -->
                    <div>
                        <UCard>
                            <template #header>
                                <h2 class="text-lg font-semibold">
                                    {{ translations[currentLanguage].loc }}
                                </h2>
                            </template>
                            <MapDepots :highlight-id="meta.Id_Location" />
                        </UCard>
                    </div>
                </div>

                <!-- Colonne droite : Fiche image complète sans la carte -->
                <UCard class="flex-1 text-sm text-[#1b263b]">
                    <!-- Header -->
                    <template #header>
                        <div class="flex justify-between items-center">
                            <h2 class="text-lg font-semibold">
                                {{ translations[currentLanguage].imginfo }}
                            </h2>
                            <UBadge
                                :color="meta.Status ? 'error' : 'success'"
                                variant="subtle"
                                size="md"
                                class="font-bold rounded-full"
                                :icon="
                                    meta.Status
                                        ? 'i-lucide-trash-2'
                                        : 'i-lucide-brush-cleaning'
                                "
                            >
                                {{ meta.Status ? translations[currentLanguage].fullLabel : translations[currentLanguage].emptyLabel }}
                            </UBadge>
                        </div>
                    </template>

                    <!-- Métadonnées -->
                    <div>
                        <h2 class="text-lg font-semibold mb-2 border-b pb-2">
                            {{ translations[currentLanguage].métadata }}
                        </h2>
                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <strong>{{ translations[currentLanguage].date }} :</strong> {{ meta.Date_taken }}
                            </div>
                            <div>
                                <strong>{{ translations[currentLanguage].size }} :</strong> {{ meta.Size }} ko
                            </div>
                            <div>
                                <strong>{{ translations[currentLanguage].dim }} :</strong> {{ meta.Width }} ×
                                {{ meta.Height }}
                            </div>
                            <div>
                                <strong>{{ translations[currentLanguage].contrast }} :</strong>
                                {{ meta.Contrast_level }}
                            </div>
                            <div>
                                <strong>{{ translations[currentLanguage].edges }} :</strong> {{ meta.Edges }}
                            </div>
                        </div>
                    </div>

                    <!-- Annotation -->
                    <div class="mt-6">
                        <h2 class="text-lg font-semibold mb-2 border-b pb-2">
                            {{ translations[currentLanguage].annotation }}
                        </h2>
                        <UButton
                            @click="openForm"
                            color="primary"
                            variant="soft"
                            >{{ translations[currentLanguage].annoter }}</UButton
                        >

                        <div v-if="showForm" class="space-y-4 mt-4">
                            <div>
                                <label class="block text-sm font-medium mb-1"
                                    >{{ translations[currentLanguage].date }}</label
                                >
                                <UInput
                                    v-model="formData.Date_taken"
                                    type="date"
                                />
                            </div>

                            <div class="grid grid-cols-2 gap-4">
                                <div>
                                    <label
                                        class="block text-sm font-medium mb-1"
                                        >{{ translations[currentLanguage].lat }}</label
                                    >
                                    <UInput
                                        v-model="formData.Latitude"
                                        type="number"
                                        step="any"
                                    />
                                </div>

                                <div>
                                    <label
                                        class="block text-sm font-medium mb-1"
                                        >{{ translations[currentLanguage].lon }}</label
                                    >
                                    <UInput
                                        v-model="formData.Longitude"
                                        type="number"
                                        step="any"
                                    />
                                </div>
                            </div>

                            <div>
                                <label class="block text-sm font-medium mb-1"
                                    >{{ translations[currentLanguage].statut }}</label
                                >
                                <USelect
                                    v-model="formData.Status"
                                    :items="statutOptions"
                                    placeholder="Sélectionnez le statut"
                                />
                            </div>

                            <div class="text-right">
                                <UButton
                                    @click="submitAnnotation"
                                    color="primary"
                                    variant="solid"
                                    >{{ translations[currentLanguage].val }}</UButton
                                >
                            </div>
                        </div>
                    </div>

                    <!-- Composition RGB PieChart -->
                    <div class="mt-6">
                        <h2 class="text-lg font-semibold mb-2 border-b pb-2">
                            {{ translations[currentLanguage].pietitle }}
                        </h2>
                        <div class="w-60 h-60 mx-auto">
                            <PieChart
                                :data="{
                                    labels: [
                                        translations[currentLanguage].Red,
                                        translations[currentLanguage].Green,
                                        translations[currentLanguage].Blue,
                                    ],
                                    datasets: [
                                        {
                                            label: translations[currentLanguage].moyrgb,
                                            data: [
                                                meta.Avg_R,
                                                meta.Avg_G,
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
                                :options="chartOptions"
                            />
                        </div>
                    </div>

                    <!-- Histogramme RGB -->
                    <div class="mt-6">
                        <h2 class="text-lg font-semibold mb-2 border-b pb-2">
                            {{ translations[currentLanguage].historgb }}
                        </h2>
                        <div class="w-full h-60">
                            <Bar
                                v-if="histogramRGB"
                                :data="histogramRGB"
                                :options="barOptions"
                            />
                        </div>
                    </div>

                    <!-- Histogramme luminance -->
                    <div class="mt-6">
                        <h2 class="text-lg font-semibold mb-2 border-b pb-2">
                            {{ translations[currentLanguage].histolum }}
                        </h2>
                        <div class="w-full h-60">
                            <Bar
                                v-if="histogramLuminance"
                                :data="histogramLuminance"
                                :options="barOptions"
                            />
                        </div>
                    </div>
                </UCard>
            </div>

            <div v-else class="text-center text-[#778da9] text-sm">
                {{ translations[currentLanguage].noimg }}
            </div>
        </UContainer>
    </div>
</template>

<script setup>
import { ref, inject, computed, watch, onMounted, onBeforeUnmount } from "vue";
import PieChart from "~/components/PieChart.vue";
import MapDepots from "../components/dashboard/MapDepots.vue";
import { Bar } from "vue-chartjs";
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
} from "chart.js";

ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend
);

const translations = inject("translations");
const currentLanguage = inject("currentLanguage");

const meta = ref(null);
const currentPage = ref(1);
const totalPages = ref(1);
const limit = 1;
const isSpecificImage = ref(false);

async function fetchImage() {
    try {
        const response = await fetch(
            `http://localhost:8000/img/list/?page=${currentPage.value}&limit=${limit}`
        );
        const data = await response.json();
        totalPages.value = Math.ceil(data.total / limit);

    if (data.images.length > 0) {
      const imageId = data.images[0].Id_Image;
      await fetchImageById(imageId);
    } else {
      meta.value = null;
    }
  } catch (error) {
    console.error("Erreur de chargement des images :", error);
  }
}

async function fetchImageById(id) {
  try {
    isSpecificImage.value = true;
    const metaResponse = await fetch(`http://localhost:8000/img/metadatas/${id}/`);
    meta.value = await metaResponse.json();

    showForm.value = false;
    formData.value = { Date_taken: "", Latitude: "", Longitude: "", Status: "false" };
  } catch (error) {
    console.error("Erreur de chargement de l'image par ID :", error);
  }
}

onMounted(() => {
  const idFromStorage = localStorage.getItem("currentId");
  if (idFromStorage) {
    fetchImageById(idFromStorage);
    localStorage.removeItem("currentId");
  } else {
    fetchImage();
  }
  window.addEventListener("keydown", handleKey);
});

onBeforeUnmount(() => {
    window.removeEventListener("keydown", handleKey);
});

watch(currentPage, fetchImage);

function suivante() {
    if (isSpecificImage.value) {
    isSpecificImage.value = false; // Désactiver l'état spécifique
    currentPage.value++; // Passer à la page suivante
    fetchImage(); // Charger les images via la pagination
  } else if (currentPage.value < totalPages.value) {
    currentPage.value++;
    fetchImage();
  }
}
function precedente() {
    if (isSpecificImage.value) {
    isSpecificImage.value = false; // Désactiver l'état spécifique
    currentPage.value--; // Passer à la page précédente
    fetchImage(); // Charger les images via la pagination
  } else if (currentPage.value > 1) {
    currentPage.value--;
    fetchImage();
  }
}
function handleKey(event) {
    if (event.key === "ArrowLeft") precedente();
    else if (event.key === "ArrowRight") suivante();
}

const imageUrl = computed(() => {
    if (!meta.value || !meta.value.File_path) return "";
    return `http://localhost:8000/media/Data/${meta.value.File_path}`;
});

function handleImageError(event) {
    if (meta.value?.File_path) {
        event.target.src = `http://localhost:8000/media/Data/${meta.value.File_path}`;
    }
}

// Chart.js
const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            display: true,
            position: "bottom",
            labels: {
                color: "#1b263b",
                padding: 8,
                boxWidth: 12,
                font: { size: 12 },
            },
        },
    },
};

const barOptions = {
    ...chartOptions,
    scales: {
        x: { ticks: { color: "#1b263b" } },
        y: { beginAtZero: true, ticks: { color: "#1b263b" } },
    },
};

const histogramRGB = computed(() => {
    if (!meta.value || !meta.value.RGB_Histogram) return null;
    const { red, green, blue } = meta.value.RGB_Histogram;
    const labels = Array.from({ length: red.length }, (_, i) => i.toString());
    return {
        labels,
        datasets: [
            {
                label: translations[currentLanguage.value]?.Red ?? "Rouge",
                data: red,
                backgroundColor: "rgba(217, 61, 61)",
            },
            {
                label: translations[currentLanguage.value]?.Green ?? "Vert",
                data: green,
                backgroundColor: "rgba(108, 224, 119)",
            },
            {
                label: translations[currentLanguage.value]?.Blue ?? "Bleu",
                data: blue,
                backgroundColor: "rgba(88, 148, 245)",
            },
        ],
    };
});

const histogramLuminance = computed(() => {
    if (!meta.value || !meta.value.Luminance_Histogram) return null;
    const luminance = meta.value.Luminance_Histogram;
    const labels = Array.from({ length: luminance.length }, (_, i) =>
        i.toString()
    );
    return {
        labels,
        datasets: [
            {
                label: translations[currentLanguage.value]?.lum ?? "Luminance",
                data: luminance,
                backgroundColor: "rgba(128,128,128,0.7)",
            },
        ],
    };
});

// Formulaire annotation
const showForm = ref(false);
const formData = ref({
    Date_taken: "",
    Latitude: "",
    Longitude: "",
    Status: "false",
});
const statutOptions = computed(() => [
    { label: translations[currentLanguage.value]?.fullLabel ?? "Pleine", value: "true" },
    { label: translations[currentLanguage.value]?.emptyLabel ?? "Vide", value: "false" },
]);

function openForm() {
    formData.value = {
        Date_taken: meta.value?.Date_taken || "",
        Latitude: meta.value?.Latitude || "",
        Longitude: meta.value?.Longitude || "",
        Status: meta.value?.Status ? "true" : "false",
    };
    showForm.value = true;
}

async function submitAnnotation() {
  try {
    const response = await fetch(`http://localhost:8000/img/${meta.value.Id_Image}/modify/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        Date_taken: formData.value.Date_taken,
        Latitude: parseFloat(formData.value.Latitude),
        Longitude: parseFloat(formData.value.Longitude),
        Status: formData.value.Status === "true",
      }),
    });
    if (!response.ok) throw new Error("Erreur lors de l'envoi");
    showForm.value = false;
    await fetchImageById(meta.value.Id_Image);
    alert("Annotation sauvegardée !");
  } catch (err) {
    console.error(err);
    alert("Erreur lors de l'envoi.");
  }
}
</script>
