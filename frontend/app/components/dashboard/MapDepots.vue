<template>
  <UCard class="w-full">
    <template #header>
      <h3 class="text-lg font-semibold text-[#1b263b]">
        Carte des dépôts sauvages
      </h3>
    </template>
    <div id="map" class="h-[500px] rounded-lg" />
  </UCard>
</template>

<script setup>
import { watch, onMounted, ref } from "vue";
import "leaflet/dist/leaflet.css";

const props = defineProps({
  highlightId: Number,
});

const map = ref(null);
const markers = ref([]);
const highlightMarker = ref(null);

const { data } = await useFetch("http://127.0.0.1:8000/img/locations/");

onMounted(async () => {
  const L = await import("leaflet");
  map.value = L.map("map").setView([48.8566, 2.3522], 14);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors",
  }).addTo(map.value);

  // Ajouter tous les markers
  data.value.forEach(({ latitude, longitude, id_image }) => {
    const marker = L.marker([latitude, longitude]).addTo(map.value);

    marker.bindPopup(
      `<strong>Image n°${id_image}</strong><br>
      <button class="leaflet-popup-button" data-id="${id_image}">
        Voir cette image
      </button>`
    );

    marker.on("popupopen", (e) => {
      const button = e.target.getPopup().getContent().match(/data-id="(\d+)"/);
      if (button) {
        const id = button[1];
        document
          .querySelector(".leaflet-popup-button")
          .addEventListener("click", () => {
            localStorage.setItem("currentId", id);
            window.location.href = "/navigation";
          });
      }
    });

    markers.value.push({ id: id_image, marker, latitude, longitude });
  });

  updateHighlight(); // premier affichage
});

// 🔄 Watch highlightId pour déplacer le marker de highlight
watch(
  () => props.highlightId,
  () => {
    updateHighlight();
  }
);

function updateHighlight() {
  if (!map.value || !props.highlightId) return;

  // Supprimer la classe highlight de tous les markers
  markers.value.forEach(({ marker }) => {
    marker._icon?.classList.remove("huechange");
  });

  // Trouver le marker correspondant et ajouter la classe highlight
  const highlightData = markers.value.find(
    (m) => m.id === props.highlightId
  );
  if (highlightData) {
    highlightData.marker._icon?.classList.add("huechange");
    map.value.setView(
      [highlightData.latitude, highlightData.longitude],
      20
    );
  }
}
</script>

<style>
#map { min-height: 500px; }
</style>