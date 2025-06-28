<template>
    <div
        v-if="meta && meta.Id_Image"
        class="flex flex-col gap-10 items-start justify-center"
    >
        <div
            class="flex flex-col lg:flex-row gap-10 items-start justify-center w-full"
        >
            <!-- Image -->
            <div class="flex flex-col items-center space-y-4 lg:w-1/2">
                <h2 class="text-3xl font-bold text-[#1b263b]">
                    Image n°{{ meta.Id_Image }}
                </h2>
                <img
                    :src="imageUrl"
                    alt="Image"
                    class="max-h-80 max-w-xs w-full mx-auto rounded-xl shadow-lg border object-contain"
                />
                <div class="flex justify-between w-full max-w-xs">
                    <UButton
                        type="button"
                        @click="precedente"
                        color="gray"
                        variant="soft"
                        icon="i-heroicons-chevron-left"
                    >
                        Précédente
                    </UButton>
                    <UButton
                        type="button"
                        @click="suivante"
                        color="gray"
                        variant="soft"
                        icon="i-heroicons-chevron-right"
                    >
                        Suivante
                    </UButton>
                </div>
            </div>

            <!-- Infos générales + bouton Annoter -->
            <div
                class="flex flex-col w-full lg:w-1/2 space-y-4 bg-[#f8f9fa] p-6 rounded-xl shadow border text-[#1b263b]"
            >
                <div class="flex justify-between items-center border-b pb-2">
                    <h3 class="text-lg font-semibold">
                        Informations générales
                    </h3>
                    <span
                        class="inline-flex items-center rounded-full bg-gray-200 px-2 py-0.5 text-xs font-medium"
                    >
                        {{ meta.Status ? "Pleine" : "Vide" }}
                    </span>
                </div>
                <div class="grid grid-cols-2 gap-2 text-sm">
                    <div>
                        <strong>Date :</strong>
                        <div>{{ meta.Date_taken }}</div>
                    </div>
                    <div>
                        <strong>Taille :</strong>
                        <div>{{ meta.Size }} ko</div>
                    </div>
                    <div>
                        <strong>Dimensions :</strong>
                        <div>{{ meta.Width }} × {{ meta.Height }}</div>
                    </div>
                    <div>
                        <strong>Contraste :</strong>
                        <div>{{ meta.Contrast_level }}</div>
                    </div>
                    <div>
                        <strong>Contours :</strong>
                        <div>{{ meta.Edges }}</div>
                    </div>
                </div>

                <UButton
                    type="button"
                    color="primary"
                    variant="soft"
                    class="mt-2"
                    @click="openForm"
                >
                    Annoter
                </UButton>

                <!-- Formulaire Annotation -->
                <form
                    v-if="showForm"
                    @submit.prevent="submitAnnotation"
                    class="space-y-3 mt-3"
                >
                    <div>
                        <label class="block text-sm font-medium mb-1"
                            >Date</label
                        >
                        <input
                            v-model="formData.Date_taken"
                            type="date"
                            class="border rounded w-full p-2"
                        />
                    </div>
                    <div>
                        <label class="block text-sm font-medium mb-1"
                            >Latitude</label
                        >
                        <input
                            v-model="formData.Latitude"
                            type="number"
                            step="any"
                            class="border rounded w-full p-2"
                        />
                    </div>
                    <div>
                        <label class="block text-sm font-medium mb-1"
                            >Longitude</label
                        >
                        <input
                            v-model="formData.Longitude"
                            type="number"
                            step="any"
                            class="border rounded w-full p-2"
                        />
                    </div>
                    <div>
                        <label class="block text-sm font-medium mb-1"
                            >Statut</label
                        >
                        <select
                            v-model="formData.Status"
                            class="border rounded w-full p-2"
                        >
                            <option value="true">Pleine</option>
                            <option value="false">Vide</option>
                        </select>
                    </div>
                    <UButton type="submit" color="primary" variant="solid"
                        >Valider</UButton
                    >
                </form>
            </div>
        </div>

        <!-- Composition RGB -->
        <div class="w-full flex flex-col items-center space-y-4">
            <div
                class="w-full max-w-sm bg-[#f8f9fa] p-4 rounded-xl shadow border text-center"
            >
                <h3 class="text-lg font-semibold mb-2">Composition RGB</h3>
                <div class="w-60 h-60 mx-auto">
                    <PieChart
                        :data="{
                            labels: ['Rouge', 'Vert', 'Bleu'],
                            datasets: [
                                {
                                    label: 'Moyenne RGB',
                                    data: [meta.Avg_R, meta.Avg_G, meta.Avg_B],
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

            <!-- Carte -->
            <div class="w-full max-w-2xl">
                <MapDepots :highlight-id="meta.Id_Location" />
            </div>
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

const currentId = ref(1);

if (process.client && localStorage.getItem("currentId")) {
    currentId.value = parseInt(localStorage.getItem("currentId")) || 1;
}

const { data: meta, refresh } = useFetch(
    () => `http://localhost:8000/img/metadatas/${currentId.value}`
);

const imageUrl = computed(() =>
    meta.value ? `http://localhost:8000/img/img/${currentId.value}` : ""
);

function suivante() {
    currentId.value++;
}
function precedente() {
    if (currentId.value > 1) {
        currentId.value--;
    }
}

function handleKey(event) {
    if (event.key === "ArrowLeft") precedente();
    else if (event.key === "ArrowRight") suivante();
}

function openForm() {
    formData.value = {
        Date_taken: meta.value.Date_taken || "",
        Latitude: meta.value.Latitude || "",
        Longitude: meta.value.Longitude || "",
        Status: meta.value?.Status ? "true" : "false",
    };
    showForm.value = true;
}

watch(currentId, async () => {
    if (process.client) {
        localStorage.setItem("currentId", currentId.value.toString());
    }
    // Recharge les métadonnées
    await refresh();
    // Ferme le formulaire si ouvert
    showForm.value = false;
    // Vide le contenu du formData
    formData.value = {
        Date_taken: "",
        Latitude: "",
        Longitude: "",
        Status: "false",
    };
});

onMounted(() => {
    refresh();
    window.addEventListener("keydown", handleKey);
});
onBeforeUnmount(() => {
    window.removeEventListener("keydown", handleKey);
});

// Formulaire annotation
const showForm = ref(false);
const formData = ref({
    Date_taken: "",
    Longitude: "",
    Latitude: "",
    Status: "false",
});

async function submitAnnotation() {
    try {
        const response = await fetch(
            `http://localhost:8000/img/${currentId.value}/modify/`,
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    Date_taken: formData.value.Date_taken,
                    Latitude: parseFloat(formData.value.Latitude),
                    Longitude: parseFloat(formData.value.Longitude),
                    Status: formData.value.Status === "true",
                }),
            }
        );
        if (!response.ok) throw new Error("Erreur lors de l'envoi");
        showForm.value = false;
        refresh();
        alert("Annotation sauvegardée !");
    } catch (err) {
        console.error(err);
        alert("Erreur lors de l'envoi.");
    }
}
</script>
