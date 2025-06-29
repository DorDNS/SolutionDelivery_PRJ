<template>
  <div class="min-h-[calc(100vh-64px-80px)] py-16 px-4 bg-white">
    <UContainer class="max-w-7xl mx-auto space-y-8">
      <!-- Titre -->
      <div class="text-center">
        <h1 class="text-3xl font-bold text-[#1b263b]">Navigation des images</h1>
        <div class="mt-2 text-[#415a77] text-sm flex items-center justify-center gap-2">
          <UIcon name="i-heroicons-eye" class="w-4 h-4 text-[#778da9]" />
          <span>Utilisez les flèches ou raccourcis clavier pour parcourir les images.</span>
        </div>
      </div>

      <!-- Image + infos -->
      <div v-if="meta && meta.Id_Image" class="flex flex-col lg:flex-row gap-10 items-start justify-center">
        <!-- Image -->
        <div class="flex-1 text-center">
          <img :src="imageUrl" alt="Image" class="max-h-[32rem] mx-auto rounded-xl shadow-lg border object-contain" />
          <div class="flex justify-between mt-4 max-w-xs mx-auto">
            <UButton @click="precedente" color="gray" variant="ghost" icon="i-heroicons-chevron-left">Précédente</UButton>
            <UButton @click="suivante" color="gray" variant="ghost" icon="i-heroicons-chevron-right">Suivante</UButton>
          </div>
        </div>

        <!-- Fiche image complète -->
        <UCard class="flex-1 text-sm text-[#1b263b]">
          <!-- Header carte -->
          <template #header>
            <div class="flex justify-between items-center">
              <h2 class="text-lg font-semibold">Informations de l'image</h2>
              <UBadge
                :color="meta.Status ? 'error' : 'success'"
                variant="subtle"
                size="md"
                class="font-bold rounded-full"
                :icon="meta.Status ? 'i-lucide-trash-2' : 'i-lucide-brush-cleaning'"
                >
                {{ meta.Status ? "Pleine" : "Vide" }}
              </UBadge>
            </div>
          </template>

          <!-- Métadonnées -->
          <div>
            <h2 class="text-lg font-semibold mb-2 border-b pb-2">Métadonnées</h2>
            <div class="grid grid-cols-2 gap-2">
              <div><strong>Date :</strong> {{ meta.Date_taken }}</div>
              <div><strong>Taille :</strong> {{ meta.Size }} ko</div>
              <div><strong>Dimensions :</strong> {{ meta.Width }} × {{ meta.Height }}</div>
              <div><strong>Contraste :</strong> {{ meta.Contrast_level }}</div>
              <div><strong>Contours :</strong> {{ meta.Edges }}</div>
            </div>
          </div>

          <!-- Annotation -->
          <div class="mt-6">
            <h2 class="text-lg font-semibold mb-2 border-b pb-2">Annotation</h2>
            <UButton @click="openForm" color="primary" variant="soft">Annoter</UButton>

            <div v-if="showForm" class="space-y-4 mt-4">
              <div>
                <label class="block text-sm font-medium mb-1">Date</label>
                <UInput v-model="formData.Date_taken" type="date" />
              </div>

              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium mb-1">Latitude</label>
                  <UInput v-model="formData.Latitude" type="number" step="any" />
                </div>

                <div>
                  <label class="block text-sm font-medium mb-1">Longitude</label>
                  <UInput v-model="formData.Longitude" type="number" step="any" />
                </div>
              </div>

              <div>
                <label class="block text-sm font-medium mb-1">Statut</label>
                <USelect v-model="formData.Status" :items="statutOptions" placeholder="Sélectionnez le statut" />
              </div>

              <div class="text-right">
                <UButton @click="submitAnnotation" color="primary" variant="solid">Valider</UButton>
              </div>
            </div>
          </div>

          <!-- Composition RGB -->
          <div class="mt-6">
            <h2 class="text-lg font-semibold mb-2 border-b pb-2">Composition RGB</h2>
            <div class="w-60 h-60 mx-auto">
              <PieChart
                :data="{
                  labels: ['Rouge', 'Vert', 'Bleu'],
                  datasets: [{
                    label: 'Moyenne RGB',
                    data: [meta.Avg_R, meta.Avg_G, meta.Avg_B],
                    backgroundColor: ['#e63946', '#2a9d8f', '#1d3557'],
                    borderColor: '#f8f9fa',
                    borderWidth: 2,
                  }]
                }"
                :options="{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      display: true,
                      position: 'bottom',
                      labels: { color: '#1b263b', padding: 8, boxWidth: 12, font: { size: 12 } }
                    }
                  }
                }"
              />
            </div>
          </div>

          <!-- Localisation -->
          <div class="mt-6">
            <h2 class="text-lg font-semibold mb-2 border-b pb-2">Localisation</h2>
            <MapDepots :highlight-id="meta.Id_Location" />
          </div>
        </UCard>
      </div>

      <div v-else class="text-center text-[#778da9] text-sm">Aucune image à afficher.</div>
    </UContainer>
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
  () => `http://localhost:8000/img/metadatas/${currentId.value}`,
  { key: `image-meta-${currentId.value}` }
);
const imageUrl = computed(() => meta.value ? `http://localhost:8000/img/img/${currentId.value}` : "");

function suivante() { currentId.value++; }
function precedente() { if (currentId.value > 1) currentId.value--; }

function handleKey(event) {
  if (event.key === "ArrowLeft") precedente();
  else if (event.key === "ArrowRight") suivante();
}

watch(currentId, async () => {
  if (process.client) localStorage.setItem("currentId", currentId.value.toString());
  await refresh();
  showForm.value = false;
  formData.value = { Date_taken: "", Latitude: "", Longitude: "", Status: "false" };
});

onMounted(() => {
  refresh();
  window.addEventListener("keydown", handleKey);
});
onBeforeUnmount(() => { window.removeEventListener("keydown", handleKey); });

// Formulaire annotation
const showForm = ref(false);
const formData = ref({ Date_taken: "", Latitude: "", Longitude: "", Status: "false" });
const statutOptions = [{ label: "Pleine", value: "true" }, { label: "Vide", value: "false" }];

function openForm() {
  formData.value = {
    Date_taken: meta.value.Date_taken || "",
    Latitude: meta.value.Latitude || "",
    Longitude: meta.value.Longitude || "",
    Status: meta.value?.Status ? "true" : "false",
  };
  showForm.value = true;
}

async function submitAnnotation() {
  try {
    const response = await fetch(`http://localhost:8000/img/${currentId.value}/modify/`, {
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
    await refresh(); // Refresh to update badge immediately
    alert("Annotation sauvegardée !");
  } catch (err) {
    console.error(err);
    alert("Erreur lors de l'envoi.");
  }
}
</script>