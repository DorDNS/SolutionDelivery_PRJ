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
            <div v-if="!intelligentMode" class="space-y-4">
                <div
                    v-for="(rule, index) in constraints"
                    :key="rule.id"
                    class="border border-gray-200 rounded-xl p-4 shadow-sm bg-gray-50"
                >
                    <div class="flex justify-between items-center mb-2">
                        <p>
                            SI {{ rule.feature }} {{ rule.operator }}
                            {{ rule.threshold }} → la poubelle est pleine. Score
                            :
                            <span class="font-bold text-blue-700">{{
                                rule.score
                            }}</span>
                        </p>
                        <UButton
                            :label="openForm === index ? 'Fermer' : 'Modifier'"
                            color="gray"
                            variant="ghost"
                            size="sm"
                            @click="toggleForm(index)"
                            style="cursor: pointer"
                            icon="i-lucide-edit"
                        />
                    </div>

                    <div
                        v-if="openForm === index"
                        class="grid grid-cols-1 md:grid-cols-4 gap-4 items-center mt-4"
                    >
                        <!-- Operator -->
                        <USelect
                            v-model="rule.operator"
                            :options="operators"
                            label="Opérateur"
                            :aria-hidden="false"
                        />

                        <!-- Threshold -->
                        <UInput
                            v-model.number="rule.threshold"
                            type="number"
                            label="Seuil"
                            icon="i-lucide-sliders"
                        />

                        <!-- Score -->
                        <UInput
                            v-model.number="rule.score"
                            type="number"
                            step="0.01"
                            label="Score"
                            icon="i-lucide-percent"
                        />

                        <UButton
                            color="primary"
                            icon="i-lucide-check-circle"
                            size="md"
                            class="mt-1"
                            @click="submitConstraint(rule)"
                        >
                            {{ translations[currentLanguage].save }}
                        </UButton>
                    </div>
                </div>
                <span>
                    {{
                        translations[currentLanguage].constraintsFormDesctiption
                    }}
                </span>
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
const operators = [">", "<", ">=", "<=", "=="];
const intelligentMode = ref(true);
const isInitializing = ref(true);
const message = ref("");

const currentLanguage = inject("currentLanguage");
const translations = inject("translations");

const openForm = ref(null);
const toggleForm = (index) => {
    openForm.value = openForm.value === index ? null : index;
};

async function loadMode() {
    try {
        const res = await axios.get("http://localhost:8000/api/config/");
        console.log("Mode intelligent récupéré :", res.data.intelligent_mode);
        intelligentMode.value = res.data.intelligent_mode;
    } catch (err) {
        console.error("Erreur loadMode:", err);
    } finally {
        isInitializing.value = false;
    }
}

async function getConstraints() {
    try {
        const res = await axios.get("http://localhost:8000/api/constraints/");
        constraints.value = res.data;
    } catch (err) {
        console.error("Erreur getConstraints:", err);
    }
}

async function submitConstraint(constraint) {
    try {
        console.log(constraint);
        await axios.post(
            "http://localhost:8000/api/constraints/update/",
            constraint
        );
        message.value = translations[currentLanguage].savedSuccess;
    } catch (err) {
        console.error("Erreur submitConstraints:", err);
        message.value = translations[currentLanguage].savedError;
    }
}

watch(intelligentMode, async (newVal) => {
    if (isInitializing.value) return;
    console.log("Sauvegarde mode intelligent :", newVal);
    try {
        await axios.post("http://localhost:8000/api/config/update/", {
            intelligent_mode: newVal,
        });
    } catch (err) {
        console.error("Erreur saveMode:", err);
    }
});

function getInputType(value) {
    if (typeof value === "number" && Number.isInteger(value)) return "number";
    else if (typeof value === "number") return "number";
    else if (typeof value === "string" && /^\d{4}-\d{2}-\d{2}$/.test(value))
        return "date";
    else return "text";
}

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
