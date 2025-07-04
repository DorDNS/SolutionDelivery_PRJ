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
                    {{translations[currentLanguage].drag}}
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
                        {{ translations[currentLanguage].fromat }}<strong>JPG/JPEG/PNG/WEBP</strong> —
                        max <strong>5 Mo</strong> — min
                        <strong>500×500 px</strong>
                    </span>
                </div>
            </div>

            <!-- Upload -->
            <UCard>
                <div class="space-y-4">
                    <label class="block font-medium text-[#1b263b]"
                        >{{ translations[currentLanguage].img }}</label
                    >
                    <div class="relative">
                        <!-- Label personnalisé -->
                        <label
                            for="file-upload"
                            class="w-full rounded-md border-0 placeholder:text-gray-500 
                            focus:outline-none disabled:cursor-not-allowed disabled:opacity-75 
                            transition-colors px-3 py-2 text-sm gap-1.5 text-gray-600 
                            bg-default ring ring-inset ring-accented file:me-1.5 file:font-medium 
                            file:text-gray-400 file:outline-none focus-visible:ring-2 
                            focus-visible:ring-inset focus-visible:ring-primary"
                        >
                        <UIcon
                            name="i-heroicons-photo"
                            class="w-5 h-5 text-[#415a77] inline-block me-1 translate-y-1"
                        />
                        {{ (fileName) || (translations[currentLanguage]?.instruc ?? "Cliquez pour choisir un fichier à uploader") }}
                        </label>
                        <!-- Champ de type file caché -->
                        <UInput
                            id="file-upload"
                            type="file"
                            accept=".jpg,.jpeg,.png,.webp"
                            class="hidden"
                            icon="i-heroicons-photo"
                            @change="handleFileChange"
                        />
                    </div>
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
                        {{ translations[currentLanguage].selc }}
                    </p>

                    <!-- Sélecteur élégant -->
                    <USelect
                        v-model="annotation"
                        :items="annotationOptions"
                        value-key="value"
                        :icon="annotationIcon"
                        :placeholder="translations[currentLanguage].selc"
                        class="w-full max-w-xs"
                        size="lg"
                        color="primary"
                    />
                    <!-- Saisie du lieu -->
                    <UInput
                        v-model="locationInput"
                        :placeholder="translations[currentLanguage].lieu"
                        icon="i-heroicons-map-pin"
                        class="w-full max-w-xs"
                    />
                    <!-- Enregistrement -->
                    <UButton
                        color="primary"
                        :disabled="!annotation || annotationSaved || !locationInput"
                        @click="saveAnnotation"
                    >
                        {{ translations[currentLanguage].env }}
                    </UButton>

                    <div
                        v-if="annotationSaved"
                        class="text-sm text-[#415a77] font-semibold text-center"
                    >
                    <span class="text-green-600">{{ translations[currentLanguage].safe }}</span>
                        <div class="mt-2">
                            <UButton
                                color="primary"
                                variant="ghost"
                                @click="resetAnnotation"
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
import { ref, inject,  computed } from "vue";

const selectedFile = ref(null);
const preview = ref(null);
const error = ref("");
const annotation = ref("");
const annotationSaved = ref(false);
const dragging = ref(false);
const dragCounter = ref(0);
const locationInput = ref("");
const fileName = ref("");

const translations = inject("translations");
const currentLanguage = inject("currentLanguage");

const annotationOptions = computed(() => [
    { label: translations[currentLanguage.value]?.emptyLabel ?? "Vide", value: "vide", icon: "i-lucide-brush-cleaning" },
    { label: translations[currentLanguage.value]?.fullLabel ?? "Pleine", value: "pleine", icon: "i-lucide-trash-2" },
]);

const annotationIcon = computed(
    () => annotationOptions.value.find((opt) => opt.value === annotation.value)?.icon
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

function processFile(file) {
    error.value = "";
    preview.value = null;
    annotation.value = "";
    annotationSaved.value = false;
    selectedFile.value = file;

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
        img.onload = () => {
            if (img.width < 500 || img.height < 500) {
                error.value = translations[currentLanguage.value].err3;
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
        throw new Error(translations[currentLanguage.value].err4);
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
        error.value = translations[currentLanguage.value].err5;
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
        console.log(translations[currentLanguage.value].err6);
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
