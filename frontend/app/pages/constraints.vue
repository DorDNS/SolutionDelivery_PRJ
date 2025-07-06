<template>
    <div class="min-h-[calc(100vh-64px-80px)] py-16 px-4 bg-white">
        <UContainer class="max-w-7xl mx-auto space-y-8">
            <!-- Titre -->
            <div class="text-center">
                <h1 class="text-3xl font-bold text-[#1b263b]">
                    {{ translations[currentLanguage].constraintsTitle }}
                </h1>
                <div
                    class="mt-2 text-[#415a77] text-sm flex items-center justify-center gap-2"
                >
                    <UIcon
                        name="i-lucide-sliders-horizontal"
                        class="w-4 h-4 text-[#778da9]"
                    />
                    <span>
                        {{
                            translations[currentLanguage].constraintsDescription
                        }}
                    </span>
                </div>
            </div>

            <!-- Switch mode intelligent -->
            <div class="flex items-center justify-center gap-1 mb-6">
                <USwitch
                    v-model="intelligentMode"
                    checked-icon="i-lucide-brain-cog"
                    unchecked-icon="i-lucide-cpu"
                    color="primary"
                    size="lg"
                />
                <span class="text-sm text-[#415a77] min-w-[180px] text-center">
                    {{
                        intelligentMode
                            ? translations[currentLanguage]?.modeint ??
                              "Mode intelligent activé"
                            : translations[currentLanguage]?.modeman ??
                              "Mode manuel activé"
                    }}
                </span>
            </div>

            <!-- Bouton relancer prédiction IA -->
            <div v-if="intelligentMode" class="text-center mt-6">
                <UButton
                    color="primary"
                    variant="solid"
                    size="md"
                    icon="i-lucide-sparkles"
                    @click="confirmRelance"
                >
                    {{
                        translations[currentLanguage]?.relanceIA ??
                        "Relancer prédiction IA sur toutes les images"
                    }}
                </UButton>
            </div>

            <!-- Formulaire de contraintes -->
            <div v-if="!intelligentMode">
                <form
                    @submit.prevent="submitConstraints"
                    class="grid gap-4 max-w-4xl mx-auto"
                >
                    <div
                        v-for="field in Object.keys(constraints)"
                        :key="field"
                        class="grid grid-cols-2 gap-2"
                    >
                        <label class="font-semibold capitalize text-[#1b263b]">
                            {{ field.replaceAll("_", " ") }}
                        </label>
                        <input
                            v-model="constraints[field]"
                            :type="getInputType(constraints[field])"
                            class="border border-gray-300 rounded px-2 py-1"
                        />
                    </div>
                    <button
                        type="submit"
                        class="mt-4 bg-blue-600 text-white px-4 py-2 rounded"
                    >
                        {{ translations[currentLanguage].save }}
                    </button>
                </form>
            </div>

            <div v-if="message" class="mt-4 text-green-600 text-center">
                {{ message }}
            </div>
        </UContainer>
    </div>
</template>

<script setup>
import { ref, inject, onMounted, watch } from "vue";
import axios from "axios";

const constraints = ref({});
const intelligentMode = ref(true);
const isInitializing = ref(true); // ✅ ajouter l'initialisation
const message = ref("");

const currentLanguage = inject("currentLanguage");
const translations = inject("translations");

// 🍀 Charger l'état du switch
async function loadMode() {
    try {
        const res = await axios.get("http://localhost:8000/api/config/");
        console.log("Mode intelligent récupéré :", res.data.intelligent_mode);
        intelligentMode.value = res.data.intelligent_mode;
    } catch (err) {
        console.error("Erreur loadMode:", err);
    } finally {
        isInitializing.value = false; // ✅ terminer l'initialisation après le chargement
    }
}

// 📦 Charger les contraintes existantes
async function getConstraints() {
    try {
        const res = await axios.get("http://localhost:8000/api/constraints/");
        constraints.value = res.data;
    } catch (err) {
        console.error("Erreur getConstraints:", err);
    }
}

// 💾 Enregistrer les contraintes modifiées
async function submitConstraints() {
    try {
        await axios.post(
            "http://localhost:8000/api/constraints/update/",
            constraints.value
        );
        message.value = translations[currentLanguage].savedSuccess;
    } catch (err) {
        console.error("Erreur submitConstraints:", err);
        message.value = translations[currentLanguage].savedError;
    }
}

// 🎯 Détecter un changement de switch et persister
watch(intelligentMode, async (newVal) => {
    if (isInitializing.value) return; // 🔥 ignore le set initial
    console.log("Sauvegarde mode intelligent :", newVal);
    try {
        await axios.post("http://localhost:8000/api/config/update/", {
            intelligent_mode: newVal,
        });
    } catch (err) {
        console.error("Erreur saveMode:", err);
    }
});

// 🛠 pour déterminer le type d’input
function getInputType(value) {
    if (typeof value === "number" && Number.isInteger(value)) return "number";
    else if (typeof value === "number") return "number";
    else if (typeof value === "string" && /^\d{4}-\d{2}-\d{2}$/.test(value))
        return "date";
    else return "text";
}

// ✅ Relancer prédiction IA sur toutes les images avec confirmation
async function relancerPredictionIA() {
    try {
        const res = await axios.post(
            "http://localhost:8000/img/predict_crops_all/"
        );
        alert("✅ Prédictions IA relancées avec succès.");
    } catch (err) {
        console.error("Erreur relancerPredictionIA:", err);
        alert("❌ Erreur lors de la relance des prédictions IA.");
    }
}

function confirmRelance() {
    if (
        confirm(
            "⚠️ Cette action va relancer la prédiction IA sur toutes les images.\nContinuer ?"
        )
    ) {
        relancerPredictionIA();
    }
}

onMounted(() => {
    loadMode();
    getConstraints();
});
</script>

<style scoped>
input[type="number"] {
    width: 100%;
}
</style>
