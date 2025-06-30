<template>
  <div id="map" class="h-[500px] rounded-lg" />
</template>

<script setup>
import { watch, onMounted, ref } from "vue";
import "leaflet/dist/leaflet.css";

const props = defineProps({
  highlightId: Number,
});

const map = ref(null);
const markers = ref([]);

const { data } = await useFetch("http://127.0.0.1:8000/img/locations/");

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
  data.value.forEach(({ latitude, longitude, id_image }) => {
    const marker = L.marker([latitude, longitude]).addTo(map.value); // icône par défaut

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

  updateHighlight();
});

watch(
  () => props.highlightId,
  () => {
    updateHighlight();
  }
);

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
