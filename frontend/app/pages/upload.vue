<template>
    <div
        class="min-h-[calc(100vh-64px-80px)] py-16 px-4 bg-white relative"
        @dragenter.prevent="handleDragEnter"
        @dragleave.prevent="handleDragLeave"
        @dragover.prevent
        @drop.prevent="handleDrop"
    >
        <!-- Zone Drag & Drop -->
        <div
            v-if="dragging"
            class="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50"
        >
            <div
                class="bg-white px-6 py-10 rounded-xl shadow-xl border-2 border-dashed border-[#778da9] text-center space-y-4"
            >
                <UIcon
                    name="i-heroicons-arrow-down-tray"
                    class="text-[#415a77] w-12 h-12 mx-auto"
                />
                <p class="text-lg text-[#1b263b] font-semibold">
                    {{ translations[currentLanguage].drag }}
                </p>
                <p class="text-sm text-[#778da9]">
                    JPG/JPEG/PNG/WEBP — 5 Mo max — min. 500×500 px
                </p>
            </div>
        </div>

        <UContainer class="max-w-xl mx-auto space-y-8">
            <!-- Titre -->
            <div class="text-center">
                <h1 class="text-3xl font-bold text-[#1b263b]">
                    {{ translations[currentLanguage].upload }}
                </h1>
                <div
                    class="mt-2 text-[#415a77] text-sm flex items-center justify-center gap-2"
                >
                    <UIcon
                        name="i-heroicons-information-circle"
                        class="w-4 h-4 text-[#778da9]"
                    />
                    <span>
                        {{ translations[currentLanguage].fromat
                        }}<strong>JPG/JPEG/PNG/WEBP</strong> — max
                        <strong>5 Mo</strong> — min
                        <strong>500×500 px</strong>
                    </span>
                </div>
            </div>

            <!-- Upload -->
            <UCard>
                <div class="space-y-4">
                    <label class="block font-medium text-[#1b263b]">
                        {{ translations[currentLanguage].img }}
                    </label>
                    <div class="relative">
                        <!-- Label personnalisé -->
                        <label
                            for="file-upload"
                            class="w-full rounded-md border-0 placeholder:text-gray-500 focus:outline-none disabled:cursor-not-allowed disabled:opacity-75 transition-colors px-3 py-2 text-sm gap-1.5 text-gray-600 bg-default ring ring-inset ring-accented file:me-1.5 file:font-medium file:text-gray-400 file:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-primary"
                            :class="{
                                'opacity-50 cursor-not-allowed': loading,
                            }"
                        >
                            <UIcon
                                name="i-heroicons-photo"
                                class="w-5 h-5 text-[#415a77] inline-block me-1 translate-y-1"
                            />
                            {{
                                fileName ||
                                (translations[currentLanguage]?.instruc ??
                                    "Cliquez pour choisir un fichier à uploader")
                            }}
                        </label>
                        <!-- Champ de type file caché -->
                        <UInput
                            id="file-upload"
                            type="file"
                            accept=".jpg,.jpeg,.png,.webp"
                            class="hidden"
                            icon="i-heroicons-photo"
                            @change="handleFileChange"
                            :disabled="loading"
                        />
                    </div>
                    <p v-if="error" class="text-red-600 text-sm">{{ error }}</p>
                </div>
            </UCard>

            <!-- Barre de chargement Prédiction IA -->
            <div
                v-if="predicting"
                class="flex flex-col items-center justify-center mt-4 space-y-2"
            >
                <UProgress size="xl" />
                <p class="text-sm text-[#415a77]">Prédiction IA en cours...</p>
            </div>

            <!-- Aperçu & annotation -->
            <div
                v-if="preview && predictionDone"
                class="text-center mt-8 space-y-6"
            >
                <img
                    :src="preview"
                    alt="Aperçu"
                    class="max-h-[32rem] mx-auto rounded-xl shadow-lg border"
                    loading="lazy"
                />

                <div class="flex flex-col items-center space-y-6">
                    <p class="text-sm font-medium text-[#415a77]">
                        {{ translations[currentLanguage].selc }}
                    </p>

                    <!-- Sélecteur élégant -->
                    <UBadge
                        v-if="intelligentMode"
                        variant="solid"
                        size="md"
                        class="font-bold rounded-full bg-gradient-to-r from-purple-500 to-purple-300 text-white flex items-center gap-1"
                    >
                        <UIcon name="i-lucide-sparkles" class="w-4 h-4" />
                        {{ translations[currentLanguage].modelDeep }}
                    </UBadge>
                    <UBadge
                        v-if="!intelligentMode"
                        variant="solid"
                        size="md"
                        class="font-bold rounded-full bg-gradient-to-r from-gray-400 to-gray-300 text-white flex items-center gap-1"
                    >
                        <UIcon
                            name="i-lucide-sliders-horizontal"
                            class="w-4 h-4"
                        />
                        {{ translations[currentLanguage].modelCond }}
                    </UBadge>

                    <USelect
                        v-model="annotation"
                        :items="annotationOptions"
                        value-key="value"
                        :icon="annotationIcon"
                        :placeholder="translations[currentLanguage].selc"
                        class="w-full max-w-xs"
                        size="lg"
                        color="primary"
                        :disabled="loading"
                    />

                    <p class="text-sm font-medium text-[#415a77]">
                        {{ translations[currentLanguage].lieu }}
                    </p>

                    <!-- Carte Leaflet pour la localisation -->
                    <div
                        class="w-full max-w-md h-96 rounded-md overflow-hidden border shadow"
                    >
                        <div id="mapid" class="w-full h-full"></div>
                    </div>

                    <!-- Barre de chargement Upload -->
                    <div
                        v-if="loading"
                        class="flex flex-col items-center justify-center mt-4 space-y-2"
                    >
                        <UProgress size="xl" />
                        <p class="text-sm text-[#415a77]">Upload en cours...</p>
                    </div>

                    <!-- Enregistrement -->
                    <UButton
                        color="primary"
                        :disabled="!annotation || annotationSaved || loading"
                        @click="saveAnnotation"
                    >
                        {{ translations[currentLanguage].env }}
                    </UButton>

                    <div
                        v-if="annotationSaved"
                        class="text-sm text-[#415a77] font-semibold text-center"
                    >
                        <span class="text-green-600">{{
                            translations[currentLanguage].safe
                        }}</span>
                        <div class="mt-2">
                            <UButton
                                color="primary"
                                variant="ghost"
                                @click="resetAnnotation"
                                :disabled="loading"
                            >
                                {{ translations[currentLanguage].modano }}
                            </UButton>
                        </div>
                    </div>
                </div>
            </div>
        </UContainer>
    </div>
</template>

<script setup>
import { ref, inject, computed, watch, nextTick } from "vue";

const loading = ref(false);
const predicting = ref(false);
const predictionDone = ref(false);
const selectedFile = ref(null);
const preview = ref(null);
const error = ref("");
const annotation = ref("");
const annotationSaved = ref(false);
const dragging = ref(false);
const dragCounter = ref(0);
const fileName = ref("");
const intelligentMode = ref(false);
const predictionIAValue = ref(null); // 🔥 nouvelle variable

// 🔥 localisation via Leaflet
const lat = ref(48.8566); // Paris par défaut
const lon = ref(2.3522);
let L; // Leaflet instance
let map, marker;

const translations = inject("translations");
const currentLanguage = inject("currentLanguage");

async function initializeMap() {
    await nextTick(); // 🔥 attend que le DOM soit rendu

    if (!document.getElementById("mapid")) {
        console.error("Div #mapid introuvable pour Leaflet");
        return;
    }

    const leaflet = await import("leaflet");
    await import("leaflet/dist/leaflet.css");
    L = leaflet.default;

    // 🔄 Supprimer ancienne carte si elle existe (hot reload, navigation)
    if (map) {
        map.remove();
        map = null;
    }

    map = L.map("mapid").setView([lat.value, lon.value], 13);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: "&copy; OpenStreetMap contributors",
    }).addTo(map);

    marker = L.marker([lat.value, lon.value], { draggable: true }).addTo(map);
    marker.on("dragend", (e) => {
        const pos = e.target.getLatLng();
        lat.value = pos.lat;
        lon.value = pos.lng;
        console.log("Nouvelles coordonnées :", lat.value, lon.value);
    });

    map.on("click", function (e) {
        const { lat: newLat, lng: newLng } = e.latlng;
        marker.setLatLng(e.latlng);
        lat.value = newLat;
        lon.value = newLng;
        console.log("Coordonnées sélectionnées :", lat.value, lon.value);
    });
}

watch(predictionDone, async (newVal) => {
    if (newVal) {
        await initializeMap();
    }
});

onMounted(async () => {
    try {
        const res = await fetch("http://localhost:8000/api/config/");
        const data = await res.json();
        intelligentMode.value = data.intelligent_mode;
        console.log("Mode intelligent:", intelligentMode.value);
    } catch (err) {
        console.error("Erreur loadMode:", err);
    }
});

const annotationOptions = computed(() => [
    {
        label: translations[currentLanguage.value]?.emptyLabel ?? "Vide",
        value: "vide",
        icon: "i-lucide-brush-cleaning",
    },
    {
        label: translations[currentLanguage.value]?.fullLabel ?? "Pleine",
        value: "pleine",
        icon: "i-lucide-trash-2",
    },
]);

const annotationIcon = computed(
    () =>
        annotationOptions.value.find((opt) => opt.value === annotation.value)
            ?.icon
);

function handleFileChange(event) {
    const file = event.target.files[0];
    if (file) {
        fileName.value = file.name;
        processFile(file);
    }
}

function handleDrop(event) {
    dragCounter.value = 0;
    dragging.value = false;
    const file = event.dataTransfer.files[0];
    if (file) {
        fileName.value = file.name;
        processFile(file);
    }
}

function handleDragEnter() {
    dragCounter.value++;
    dragging.value = true;
}

function handleDragLeave() {
    dragCounter.value--;
    if (dragCounter.value <= 0) {
        dragging.value = false;
    }
}

async function processFile(file) {
    error.value = "";
    preview.value = null;
    annotation.value = "";
    annotationSaved.value = false;
    predictionDone.value = false;
    selectedFile.value = file;
    predictionIAValue.value = null; // 🔥 reset à chaque nouveau fichier

    if (!file) return;

    const validTypes = ["image/jpeg", "image/png", "image/webp", "image/jpg"];
    if (!validTypes.includes(file.type)) {
        error.value = translations[currentLanguage.value].err1;
        return;
    }

    if (file.size > 5 * 1024 * 1024) {
        error.value = translations[currentLanguage.value].err2;
        return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
        const img = new Image();
        img.onload = async () => {
            if (img.width < 500 || img.height < 500) {
                error.value = translations[currentLanguage.value].err3;
            } else {
                preview.value = e.target.result;

                if (intelligentMode.value) {
                    predicting.value = true;
                    try {
                        const formData = new FormData();
                        formData.append("image", file);

                        const res = await fetch(
                            "http://localhost:8000/img/predict_only/deep/",
                            {
                                method: "POST",
                                body: formData,
                            }
                        );

                        if (!res.ok) throw new Error(`HTTP ${res.status}`);
                        const data = await res.json();

                        console.log("Prédiction IA reçue :", data.prediction);

                        if (
                            data.prediction !== null &&
                            data.prediction !== undefined
                        ) {
                            annotation.value =
                                data.prediction === 1 ? "pleine" : "vide";
                            predictionIAValue.value = data.prediction; // 🔥 stocke la prédiction IA
                        }
                    } catch (err) {
                        console.error("Erreur prédiction IA :", err);
                    } finally {
                        predicting.value = false;
                        predictionDone.value = true;
                    }
                } else {
                    predicting.value = true;
                    try {
                        const formData = new FormData();
                        formData.append("image", file);

                        const res = await fetch(
                            "http://localhost:8000/img/predict_only/cond/",
                            {
                                method: "POST",
                                body: formData,
                            }
                        );

                        if (!res.ok) throw new Error(`HTTP ${res.status}`);
                        const data = await res.json();

                        console.log("Prédiction IA reçue :", data.prediction);

                        if (
                            data.prediction !== null &&
                            data.prediction !== undefined
                        ) {
                            annotation.value =
                                data.prediction === 1 ? "pleine" : "vide";
                            predictionIAValue.value = data.prediction; // 🔥 stocke la prédiction IA
                        }
                    } catch (err) {
                        console.error("Erreur prédiction IA :", err);
                    } finally {
                        predicting.value = false;
                        predictionDone.value = true;
                    }
                }
            }
        };
        img.src = e.target.result;
    };
    reader.readAsDataURL(file);
}

async function saveAnnotation() {
    if (!selectedFile.value || !annotation.value) {
        error.value = translations[currentLanguage.value].err5;
        return;
    }

    loading.value = true;
    annotationSaved.value = true;

    try {
        // 🔄 Reverse geocoding pour récupérer la ville
        let city = "Unknown";
        try {
            const url = `http://localhost:8000/api/reverse_geocode_proxy/?lat=${lat.value}&lon=${lon.value}`;
            const res = await fetch(url);
            const data = await res.json();
            city =
                data.address.city ||
                data.address.town ||
                data.address.village ||
                "Unknown";
        } catch (e) {
            console.error("Erreur reverse geocoding :", e);
        }

        const formData = new FormData();
        formData.append("image", selectedFile.value);
        formData.append("File_name", selectedFile.value.name);
        formData.append("Height", selectedFile.value.height);
        formData.append("Width", selectedFile.value.width);
        formData.append("Size", selectedFile.value.size);
        formData.append("Date_taken", new Date().toISOString().split("T")[0]);

        const annotationValue = annotation.value === "pleine" ? 1 : 0;
        formData.append("Annotation", annotationValue);
        formData.append("Latitude", lat.value);
        formData.append("Longitude", lon.value);
        formData.append("City", city);

        if (intelligentMode.value && predictionIAValue.value !== null) {
            formData.append("Prediction_IA", predictionIAValue.value); // 🔥 utilise la prédiction IA originale
        }

        const response = await fetch("http://localhost:8000/img/upload/", {
            method: "POST",
            body: formData,
        });

        if (!response.ok) throw new Error(`Erreur HTTP ${response.status}`);
        console.log(translations[currentLanguage.value].err6);
    } catch (err) {
        console.error("Erreur :", err.message);
        annotationSaved.value = false;
    } finally {
        loading.value = false;
    }
}

function resetAnnotation() {
    annotation.value = "";
    annotationSaved.value = false;
}
</script>
