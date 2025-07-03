<script setup>
import { ref, onMounted } from "vue";
import { LMap, LTileLayer, LMarker, LPopup } from "@vue-leaflet/vue-leaflet";
import axios from "axios";

const { showMarches, showChantiers, showDepots } = defineProps({
    showMarches: { type: Boolean, default: true },
    showChantiers: { type: Boolean, default: true },
    showDepots: { type: Boolean, default: true },
});

const url = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
const attribution = "&copy; OpenStreetMap contributors";

const marches = ref([]);
const chantiers = ref([]);
const depots = ref([]);

const violetIcon = ref(null);
const orangeIcon = ref(null);
const blueIcon = ref(null);

const fetchMarches = async () => {
    try {
        const response = await axios.get(
            "https://opendata.paris.fr/api/records/1.0/search/?dataset=marches-decouverts&rows=1000"
        );
        const today = new Date().toLocaleDateString("fr-FR", {
            weekday: "long",
        });
        const todayUpper =
            today.charAt(0).toUpperCase() + today.slice(1).toLowerCase();

        marches.value = response.data.records
            .filter((r) => {
                const jours = r.fields.jours_tenue || "";
                return r.fields.geo_point_2d && jours.includes(todayUpper);
            })
            .map((r) => ({
                nom: r.fields.nom || "Sans nom",
                produit: r.fields.produit || "Produit non précisé",
                jours: r.fields.jours_tenue || "Jours non précisés",
                lat: r.fields.geo_point_2d[0],
                lng: r.fields.geo_point_2d[1],
            }));
    } catch (error) {
        console.error("Erreur récupération marchés :", error);
    }
};

const fetchChantiers = async () => {
    try {
        const response = await axios.get(
            "https://opendata.paris.fr/api/records/1.0/search/?dataset=chantiers-a-paris&rows=1000"
        );
        const now = new Date();

        chantiers.value = response.data.records
            .filter((r) => {
                const debut = r.fields.date_debut
                    ? new Date(r.fields.date_debut)
                    : null;
                const fin = r.fields.date_fin
                    ? new Date(r.fields.date_fin)
                    : null;
                return (
                    r.fields.geo_point_2d &&
                    (!debut || now >= debut) &&
                    (!fin || now <= fin)
                );
            })
            .map((r) => ({
                ref: r.fields.num_emprise || "Réf. inconnue",
                responsable: r.fields.moa_principal || "Responsable inconnu",
                date_fin: r.fields.date_fin || "Date fin inconnue",
                lat: r.fields.geo_point_2d[0],
                lng: r.fields.geo_point_2d[1],
            }));
    } catch (error) {
        console.error("Erreur récupération chantiers :", error);
    }
};

const fetchDepots = async () => {
    try {
        const response = await axios.get(
            "http://127.0.0.1:8000/img/locations/"
        );
        depots.value = response.data.map((d) => ({
            id: d.id_image,
            lat: d.latitude,
            lng: d.longitude,
        }));
    } catch (error) {
        console.error("Erreur récupération dépôts :", error);
    }
};

function goToNavigation(id) {
    localStorage.setItem("currentId", id);
    window.location.href = "/navigation";
}

onMounted(async () => {
    const leaflet = await import("leaflet");

    violetIcon.value = leaflet.icon({
        iconUrl:
            "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-violet.png",
        shadowUrl:
            "https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png",
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41],
    });

    orangeIcon.value = leaflet.icon({
        iconUrl:
            "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-orange.png",
        shadowUrl:
            "https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png",
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41],
    });

    blueIcon.value = leaflet.icon({
        iconUrl:
            "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png",
        shadowUrl:
            "https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png",
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41],
    });

    await fetchMarches();
    await fetchChantiers();
    await fetchDepots();

    setInterval(fetchMarches, 24 * 60 * 60 * 1000);
    setInterval(fetchChantiers, 60 * 60 * 1000);
    setInterval(fetchDepots, 60 * 60 * 1000);
});
</script>

<template>
    <client-only>
        <div>
            <LMap :zoom="12" :center="[48.8566, 2.3522]" style="height: 500px">
                <LTileLayer :url="url" :attribution="attribution" />

                <!-- 🟣 Marchés -->
                <LMarker
                    v-if="showMarches && violetIcon"
                    v-for="(marche, index) in marches"
                    :key="'marche-' + index"
                    :lat-lng="[marche.lat, marche.lng]"
                    :icon="violetIcon"
                >
                    <LPopup>
                        <strong>{{ marche.nom }}</strong
                        ><br />
                        {{ marche.produit }}<br />
                        {{ marche.jours }}
                    </LPopup>
                </LMarker>

                <!-- 🟧 Chantiers -->
                <LMarker
                    v-if="showChantiers && orangeIcon"
                    v-for="(chantier, index) in chantiers"
                    :key="'chantier-' + index"
                    :lat-lng="[chantier.lat, chantier.lng]"
                    :icon="orangeIcon"
                >
                    <LPopup>
                        <strong>{{ chantier.ref }}</strong
                        ><br />
                        {{ chantier.responsable }}<br />
                        Fin : {{ chantier.date_fin }}
                    </LPopup>
                </LMarker>

                <!-- 🔵 Poubelles -->
                <LMarker
                    v-if="showDepots && blueIcon"
                    v-for="(depot, index) in depots"
                    :key="'depot-' + index"
                    :lat-lng="[depot.lat, depot.lng]"
                    :icon="blueIcon"
                >
                    <LPopup>
                        <strong>Dépôt ID {{ depot.id }}</strong
                        ><br />
                        <button @click="goToNavigation(depot.id)">
                            Voir l’image
                        </button>
                    </LPopup>
                </LMarker>

                <!-- 🔴🟡🟢Zones à risques -->
                <LMarker
                    v-if="showZones"
                    v-for="(depot, index) in depots"
                    :key="'depot-' + index"
                    :lat-lng="[depot.lat, depot.lng]"
                    :icon="blueIcon"
                >
                </LMarker>
            </LMap>
        </div>
    </client-only>
</template>
