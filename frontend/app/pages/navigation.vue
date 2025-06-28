<template>
    <div
        v-if="meta && meta.Id_Image"
        class="flex flex-col lg:flex-row gap-10 items-start justify-center"
    >
        <!-- Image -->
        <div class="flex-1 text-center">
            <img
                :src="imageUrl"
                alt="Image"
                class="max-h-[32rem] mx-auto rounded-xl shadow-lg border"
            />
            <div class="flex justify-between mt-4">
                <UButton
                    type="button"
                    @click="precedente"
                    color="gray"
                    variant="ghost"
                    >◀ Précédente</UButton
                >
                <UButton
                    type="button"
                    @click="suivante"
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
            <h2 class="text-lg font-semibold mb-2">Informations de l'image</h2>
            <p><strong>Taille :</strong> {{ meta.Size }} ko</p>
            <p>
                <strong>Dimensions :</strong> {{ meta.Width }} x
                {{ meta.Height }}
            </p>
            <p><strong>Date :</strong> {{ meta.Date_taken }}</p>
            <p><strong>Contraste :</strong> {{ meta.Contrast_level }}</p>
            <!-- Camembert RGB -->
            <h3 class="text-base font-semibold mb-4">Composition RGB :</h3>
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
            <MapDepots :highlight-id="meta.Id_Location" />
        </div>
    </div>

    <div v-else class="text-center text-[#778da9] text-sm">
        Aucune image à afficher.
    </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from "vue";
import { useFetch } from "#app";
import PieChart from "~/components/PieChart.vue";
import MapDepots from "../components/dashboard/MapDepots.vue";

// ✅ Super variable globale réactive
const currentId = ref(1);

// Si tu veux garder en localStorage (facultatif)
if (process.client && localStorage.getItem("currentId")) {
    currentId.value = parseInt(localStorage.getItem("currentId")) || 1;
}

// Fetch dynamique des métadonnées
const { data: meta, refresh } = useFetch(
    () => `http://localhost:8000/img/metadatas/${currentId.value}`
);

// URL de l'image
const imageUrl = computed(() =>
    meta.value ? `http://localhost:8000/img/img/${currentId.value}` : ""
);

// Navigation
function suivante() {
    currentId.value++;
}

function precedente() {
    if (currentId.value > 1) {
        currentId.value--;
    } else {
        currentId.value = 1;
    }
}

// Flèches clavier
function handleKey(event) {
    if (event.key === "ArrowLeft") precedente();
    else if (event.key === "ArrowRight") suivante();
}

// Quand currentId change, on refetch
watch(currentId, () => {
    if (process.client) {
        localStorage.setItem("currentId", currentId.value.toString());
    }
    refresh();
});

// Initialisation
onMounted(() => {
    refresh();
    window.addEventListener("keydown", handleKey);
});

onBeforeUnmount(() => {
    window.removeEventListener("keydown", handleKey);
});
</script>
