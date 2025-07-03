<template>
    <div id="map" class="h-[500px] rounded-lg" />
    <div class="flex">
        <USwitch
            class="p-5"
            v-if="highlightId == null"
            v-model="toggleValueZones"
            label="Zones à risque"
        />
        <USwitch
            class="p-5"
            v-if="highlightId == null"
            v-model="toggleValueMarker"
            label="Poubelles"
        />
    </div>
</template>

<script setup>
import { watch, onMounted, ref } from "vue";
import { USwitch } from "#components";
import "leaflet/dist/leaflet.css";

const props = defineProps({
    highlightId: Number,
});

const toggleValueZones = ref(false);
const toggleValueMarker = ref(true);

const map = ref(null);
const riskZoneCircles = ref([]);
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
            const button = e.target
                .getPopup()
                .getContent()
                .match(/data-id="(\d+)"/);
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

    // Ajout de toutes le szones
    const newCircles = data.value
        .filter((item) => item.status !== null)
        .map((item) => {
            const color = item.status ? "yellow" : "green";
            return L.circle([item.latitude, item.longitude], {
                radius: 150,
                color,
                fillOpacity: 0.3,
                stroke: false,
            });
        });

    // Détection des intersections
    newCircles.forEach((circleA, i) => {
        const centerA = circleA.getLatLng();
        const radiusA = circleA.getRadius();

        newCircles.forEach((circleB, j) => {
            if (i >= j) return; // éviter les doublons et la même instance
            const centerB = circleB.getLatLng();
            const radiusB = circleB.getRadius();

            const distance = centerA.distanceTo(centerB);
            if (distance < radiusA + radiusB) {
                // chevauchement → rouge
                circleA.setStyle({ color: "red" });
                circleB.setStyle({ color: "red" });
            }
        });
    });

    // Stocker dans le ref
    riskZoneCircles.value = newCircles;
    updateHighlight();
});

watch(
    () => props.highlightId,
    () => {
        updateHighlight();
    }
);

watch(toggleValueZones, async (newVal) => {
    if (newVal === true) {
        riskZoneCircles.value.forEach((circle) => {
            circle.addTo(map.value);
        });
    }
    if (newVal === false) {
        riskZoneCircles.value.forEach((circle) => {
            map.value.removeLayer(circle);
        });
    }
});

watch(toggleValueMarker, (newVal) => {
    if (newVal) {
        markers.value.forEach(({ marker }) => {
            marker.addTo(map.value);
        });
    } else {
        markers.value.forEach(({ marker }) => {
            map.value.removeLayer(marker);
        });
    }
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

.leaflet-popup-button {
    background: none;
    border: none;
    cursor: pointer;
    font-weight: 500;
    padding: 0;
}

.leaflet-popup-button:hover {
    color: #007bff;
}
</style>
