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
                    Déposez votre image ici
                </p>
                <p class="text-sm text-[#778da9]">
                    JPG/JPEG/PNG/WEBP — 5 Mo max — min. 500×500 px
                </p>
            </div>
        </div>

        <UContainer class="max-w-xl mx-auto space-y-8">
            <!-- Titre -->
            <div class="text-center">
                <h1 class="text-3xl font-bold text-[#1b263b]">
                    Uploader une image
                </h1>
                <div
                    class="mt-2 text-[#415a77] text-sm flex items-center justify-center gap-2"
                >
                    <UIcon
                        name="i-heroicons-information-circle"
                        class="w-4 h-4 text-[#778da9]"
                    />
                    <span>
                        Formats : <strong>JPG/JPEG/PNG/WEBP</strong> —
                        max <strong>5 Mo</strong> — min
                        <strong>500×500 px</strong>
                    </span>
                </div>
            </div>

            <!-- Upload -->
            <UCard>
                <div class="space-y-4">
                    <label class="block font-medium text-[#1b263b]"
                        >Image</label
                    >
                    <UInput
                        type="file"
                        accept=".jpg,.jpeg,.png"
                        icon="i-heroicons-photo"
                        @change="handleFileChange"
                    />
                    <p v-if="error" class="text-red-600 text-sm">{{ error }}</p>
                </div>
            </UCard>

            <!-- Aperçu & annotation -->
            <div v-if="preview" class="text-center mt-8 space-y-6">
                <img
                    :src="preview"
                    alt="Aperçu"
                    class="max-h-[32rem] mx-auto rounded-xl shadow-lg border"
                    loading="lazy"
                />

                <div class="flex flex-col items-center space-y-6">
                    <p class="text-sm font-medium text-[#415a77]">
                        Sélectionnez l’état de la poubelle :
                    </p>

                    <!-- Sélecteur élégant -->
                    <USelect
                        v-model="annotation"
                        :items="annotationOptions"
                        value-key="value"
                        :icon="annotationIcon"
                        placeholder="Choisissez un état"
                        class="w-full max-w-xs"
                        size="lg"
                        color="primary"
                    />
                    <!-- Saisie du lieu -->
                    <UInput
                        v-model="locationInput"
                        placeholder="Entrez un lieu (ex: Paris)"
                        icon="i-heroicons-map-pin"
                        class="w-full max-w-xs"
                    />
                    <!-- Enregistrement -->
                    <UButton
                        color="primary"
                        :disabled="!annotation || annotationSaved || locationInput"
                        @click="saveAnnotation"
                    >
                        Envoyer
                    </UButton>

                    <div
                        v-if="annotationSaved"
                        class="text-sm text-[#415a77] font-semibold text-center"
                    >
                    <span class="text-green-600">Image et annotation enregistrée dans la base de données !!!</span>
                        <div class="mt-2">
                            <UButton
                                color="primary"
                                variant="ghost"
                                @click="resetAnnotation"
                            >
                                Modifier l'annotation
                            </UButton>
                        </div>
                    </div>
                </div>
            </div>
        </UContainer>
    </div>
</template>

<script setup>
import { ref, computed } from "vue";

const selectedFile = ref(null);
const preview = ref(null);
const error = ref("");
const annotation = ref("");
const annotationSaved = ref(false);
const dragging = ref(false);
const dragCounter = ref(0);
const locationInput = ref("");

const annotationOptions = [
    { label: "Vide", value: "vide", icon: "i-lucide-brush-cleaning" },
    { label: "Pleine", value: "pleine", icon: "i-lucide-trash-2" },
];

const annotationIcon = computed(
    () => annotationOptions.find((opt) => opt.value === annotation.value)?.icon
);

function handleFileChange(event) {
    const file = event.target.files[0];
    processFile(file);
}

function handleDrop(event) {
    dragCounter.value = 0;
    dragging.value = false;
    const file = event.dataTransfer.files[0];
    processFile(file);
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

function processFile(file) {
    error.value = "";
    preview.value = null;
    annotation.value = "";
    annotationSaved.value = false;
    selectedFile.value = file;

    if (!file) return;

    const validTypes = ["image/jpeg", "image/png", "image/webp", "image/jpg"];
    if (!validTypes.includes(file.type)) {
        error.value = "Format non supporté. JPG/JPEG/PNG/WEBP requis.";
        return;
    }

    if (file.size > 5 * 1024 * 1024) {
        error.value = "Fichier trop volumineux. 5 Mo max.";
        return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
            if (img.width < 500 || img.height < 500) {
                error.value = "Image trop petite. Minimum 500×500 px.";
            } else {
                preview.value = e.target.result;
            }
        };
        img.src = e.target.result;
    };
    reader.readAsDataURL(file);
}

async function geocodeLocation(place) {
    const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(place)}`;
    const response = await fetch(url);
    const results = await response.json();
    if (results.length === 0) {
        throw new Error("Lieu introuvable");
    }
    const result = results[0];
    return {
        lat: parseFloat(result.lat),
        lon: parseFloat(result.lon),
        city: result.display_name.split(',')[0]
    };
}


async function saveAnnotation() {
    if (!annotation.value || !selectedFile.value || !locationInput.value) {
        error.value = "Veuillez remplir tous les champs.";
        return;
    }

    annotationSaved.value = true;

    try {
        const location = await geocodeLocation(locationInput.value);

        const formData = new FormData();
        formData.append("image", selectedFile.value);
        formData.append("File_name", selectedFile.value.name);
        formData.append("Height", selectedFile.value.height);
        formData.append("Width", selectedFile.value.width);
        formData.append("Size", selectedFile.value.size);
        formData.append("Date_taken", new Date().toISOString().split("T")[0]);

        const annotationValue = annotation.value === "pleine" ? 1 : 0;
        formData.append("Annotation", annotationValue);

        formData.append("Latitude", location.lat);
        formData.append("Longitude", location.lon);
        formData.append("City", location.city);

        for (let [key, value] of formData.entries()) {
            console.log(`${key}: ${value}`);
        }


        const response = await fetch("http://localhost:8000/img/upload/", {
            method: "POST",
            body: formData,
        });

        if (!response.ok) throw new Error(`Erreur HTTP ${response.status}`);
        console.log("Upload réussi");
    } catch (err) {
        console.error("Erreur : ", err.message);
        annotationSaved.value = false;
    }
}


function resetAnnotation() {
    annotation.value = "";
    annotationSaved.value = false;
}
</script>
