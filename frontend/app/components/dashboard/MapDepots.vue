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

<style>
img.huechange {
    filter: hue-rotate(120deg);
}

.leaflet-popup-button {
    cursor: pointer;
}

.leaflet-popup-button:hover {
    color: blue;
}
</style>

<script setup>
import { watch, onMounted } from "vue";
import "leaflet/dist/leaflet.css";

const props = defineProps({
    highlightId: {
        type: Number,
        default: null,
    },
});

const { data, pending, error } = await useFetch(
    "http://127.0.0.1:8000/img/locations/"
);

onMounted(async () => {
    const L = await import("leaflet");

    const map = L.map("map").setView([48.8566, 2.3522], 14);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap contributors",
    }).addTo(map);

    watch(
        data,
        (locations) => {
            if (!locations) return;

            locations.forEach(({ latitude, longitude, id_image }) => {
                const marker = L.marker([latitude, longitude]).addTo(map);

                marker.bindPopup(
                    `<strong>Image n°${id_image}</strong><br>
                    <button class="leaflet-popup-button" data-id="${id_image}">
                      Voir cette image
                    </button>`
                );

                map.on("popupopen", (e) => {
                    const button = e.popup._contentNode.querySelector(
                        ".leaflet-popup-button"
                    );
                    if (button) {
                        button.addEventListener("click", () => {
                            const id = button.dataset.id;
                            localStorage.setItem("currentId", id);
                            window.location.href = "/navigation";
                            // ou router.push("/navigation") si tu as injecté `const router = useRouter()`
                        });
                    }
                });

                // Ajoute la classe si c'est le point sélectionné
                if (props.highlightId === id_image) {
                    marker._icon.classList.add("huechange");
                    map.setView([latitude, longitude], 20);
                }
            });
        },
        { immediate: true }
    );
});
</script>
