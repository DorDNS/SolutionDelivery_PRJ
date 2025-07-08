<template>
  <div id="map" class="h-[500px] rounded-lg" />
</template>

<script setup>
import { watch, onMounted, ref, inject } from "vue";
import "leaflet/dist/leaflet.css";

const translations = inject("translations");
const currentLanguage = inject("currentLanguage");

const props = defineProps({
  highlightId: Number,
});

const map = ref(null);
const markers = ref([]);

const { data } = await useFetch("http://127.0.0.1:8000/img/locations/1970-01-01");

onMounted(async () => {
  const L = await import("leaflet");

  const goldIcon = L.icon({
    iconUrl: "/leaflet/marker-icon-gold.png",
    shadowUrl: "/leaflet/marker-shadow.png",
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41],
  });

  map.value = L.map("map").setView([48.8566, 2.3522], 14);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors",
  }).addTo(map.value);

  // Ajouter tous les marqueurs
  addMarkers(data.value);

  updateHighlight();
});

// Fonction pour ajouter les marqueurs
function addMarkers(locations) {
  markers.value.forEach(({ marker }) => map.value.removeLayer(marker)); // Supprimer les anciens marqueurs
  markers.value = []; // Réinitialiser les marqueurs

  locations.forEach(({ latitude, longitude, id_image }) => {
    const marker = L.marker([latitude, longitude]).addTo(map.value);

    marker.bindPopup(
      `<strong>${translations[currentLanguage.value]?.depID ?? "ID Dépôt"} ${id_image}</strong><br>
      <button class="leaflet-popup-button" data-id="${id_image}">
      ${translations[currentLanguage.value]?.seeimg ?? "Voir l'image"}
      </button>`
    );

    marker.on("popupopen", (e) => {
      const popupContent = e.popup.getElement();
      const button = popupContent.querySelector(".leaflet-popup-button");

      if (button) {
        L.DomEvent.on(button, "click", () => {
          localStorage.setItem("currentId", button.dataset.id);
          window.location.href = "/navigation";
        });
      }
    });

    markers.value.push({ id: id_image, marker, latitude, longitude });
  });
}

// Watch pour détecter les changements de langue
watch(currentLanguage, () => {
  addMarkers(data.value); 
});

// Mettre en surbrillance le marqueur lié à l'image
watch([currentLanguage, () => props.highlightId], () => {
  updateHighlight(); 
});

async function updateHighlight() {
  if (!map.value || !props.highlightId) return;

  const L = await import("leaflet");

  const goldIcon = L.icon({
    iconUrl: "/leaflet/marker-icon-gold.png",
    shadowUrl: "/leaflet/marker-shadow.png",
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41],
  });

  markers.value.forEach(({ id, marker }) => {
    if (id === props.highlightId) {
      marker.setIcon(goldIcon);
      map.value.setView(marker.getLatLng(), 20);
      marker.openPopup();
    } else {
      marker.setIcon(L.Icon.Default.prototype);
    }
  });
}
</script>

<style>
#map {
  min-height: 500px;
}
</style>
