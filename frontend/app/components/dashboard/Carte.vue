<script setup>
import { ref, onMounted } from "vue";
import { LMap, LTileLayer, LMarker, LPopup, LCircle } from "@vue-leaflet/vue-leaflet";
import axios from "axios";

// Props
const { showMarches, showChantiers, showDepots, showZones } = defineProps({
    showMarches: { type: Boolean, default: true },
    showChantiers: { type: Boolean, default: true },
    showDepots: { type: Boolean, default: true },
    showZones: { type: Boolean, default: false },
});

// Constantes Leaflet
const url = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
const attribution = "&copy; OpenStreetMap contributors";

// Références
const marches = ref([]);
const chantiers = ref([]);
const depots = ref([]);
const riskZones = ref([]);

const violetIcon = ref(null);
const orangeIcon = ref(null);
const blueIcon = ref(null);

// 🟣 Marchés
const fetchMarches = async () => {
    try {
        const response = await axios.get("https://opendata.paris.fr/api/records/1.0/search/?dataset=marches-decouverts&rows=1000");
        const now = new Date();
        const todayNum = now.getDay();
        const timeNow = now.toTimeString().slice(0,5);
        const joursMap = ["dimanche","lundi","mardi","mercredi","jeudi","vendredi","samedi"];

        marches.value = response.data.records.filter(r => {
            if (!r.fields.geo_point_2d) return false;
            let isToday = false, heureDebut = null, heureFin = null;
            if (todayNum >= 1 && todayNum <= 5) {
                isToday = r.fields[joursMap[todayNum]] === 1;
                heureDebut = r.fields.h_deb_sem_1;
                heureFin = r.fields.h_fin_sem_1;
            } else if (todayNum === 6) {
                isToday = r.fields.samedi === 1;
                heureDebut = r.fields.h_deb_sam;
                heureFin = r.fields.h_fin_sam;
            } else if (todayNum === 0) {
                isToday = r.fields.dimanche === 1;
                heureDebut = r.fields.h_deb_dim;
                heureFin = r.fields.h_fin_dim;
            }
            if (!isToday || !heureDebut || !heureFin) return false;
            return timeNow >= heureDebut && timeNow <= heureFin;
        }).map(r => ({
            nom: r.fields.nom_long || 'Sans nom',
            produit: r.fields.produit || 'Produit non précisé',
            jours: r.fields.jours_tenue || 'Jours non précisés',
            lat: r.fields.geo_point_2d[0],
            lng: r.fields.geo_point_2d[1],
        }));
    } catch (error) {
        console.error("Erreur récupération marchés :", error);
    }
};

// 🟧 Chantiers
const fetchChantiers = async () => {
    try {
        const response = await axios.get("https://opendata.paris.fr/api/records/1.0/search/?dataset=chantiers-a-paris&rows=1000");
        const now = new Date();
        chantiers.value = response.data.records.filter(r => {
            const debut = r.fields.date_debut ? new Date(r.fields.date_debut) : null;
            const fin = r.fields.date_fin ? new Date(r.fields.date_fin) : null;
            return r.fields.geo_point_2d && (!debut || now >= debut) && (!fin || now <= fin);
        }).map(r => ({
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
        const response = await axios.get("http://127.0.0.1:8000/img/locations/");
        console.log("Réponse API depots :", response.data);

        depots.value = response.data.map(d => {
            console.log("Depot brut :", d);
            let status = null;
            if (d.status === 1) status = "plein";
            else if (d.status === 0) status = "vide";
            // sinon null reste null

            console.log(`Depot ${d.id_image} -> status :`, status);

            return {
                id: d.id_image,
                lat: d.latitude,
                lng: d.longitude,
                status: status
            };
        });

        console.log("Depots transformés :", depots.value);

        generateRiskZones();
    } catch (error) {
        console.error("Erreur récupération dépôts :", error);
    }
};

function generateRiskZones() {
    console.log("Depots avant filter :", depots.value);

    const circles = depots.value
        .filter(d => d.status !== null)
        .map(d => ({
            lat: d.lat,
            lng: d.lng,
            radius: 150,
            status: d.status,
            color: d.status === "plein" ? "yellow" : "green" // plein = jaune, vide = vert
        }));

    console.log("Circles générés :", circles);

    // Détection chevauchements uniquement entre cercles jaunes
    const yellowCircles = circles
        .map((c, idx) => ({ ...c, index: idx }))
        .filter(c => c.color === "yellow");

    for (let i = 0; i < yellowCircles.length; i++) {
        const a = yellowCircles[i];
        for (let j = i + 1; j < yellowCircles.length; j++) {
            const b = yellowCircles[j];
            const dist = distanceBetween(a.lat, a.lng, b.lat, b.lng);
            if (dist < a.radius + b.radius) {
                circles[a.index].color = "red";
                circles[b.index].color = "red";
            }
        }
    }

    console.log("Circles après détection chevauchement :", circles);

    riskZones.value = circles;
}

// Calcul distance Haversine (approx m)
function distanceBetween(lat1, lon1, lat2, lon2) {
    const R = 6371e3;
    const φ1 = lat1 * Math.PI / 180;
    const φ2 = lat2 * Math.PI / 180;
    const Δφ = (lat2 - lat1) * Math.PI / 180;
    const Δλ = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(Δφ/2)**2 + Math.cos(φ1)*Math.cos(φ2)*Math.sin(Δλ/2)**2;
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
}

// Navigation image
function goToNavigation(id) {
    console.log("Redirection vers ID :", id);
    localStorage.setItem("currentId", id);
    window.location.href = "/navigation";
}

// onMounted initialisation
onMounted(async () => {
    const leaflet = await import("leaflet");

    violetIcon.value = leaflet.icon({
        iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-violet.png",
        shadowUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png",
        iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34], shadowSize: [41, 41],
    });

    orangeIcon.value = leaflet.icon({
        iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-orange.png",
        shadowUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png",
        iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34], shadowSize: [41, 41],
    });

    blueIcon.value = leaflet.icon({
        iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png",
        shadowUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png",
        iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34], shadowSize: [41, 41],
    });

    await fetchMarches();
    await fetchChantiers();
    await fetchDepots();

    setInterval(fetchMarches, 24*60*60*1000);
    setInterval(fetchChantiers, 60*60*1000);
    setInterval(fetchDepots, 60*60*1000);
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
            <strong>{{ marche.nom }}</strong><br />
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
            <strong>{{ chantier.ref }}</strong><br />
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
            <strong>Dépôt ID {{ depot.id }}</strong><br />
            <button @click="() => goToNavigation(depot.id)">
              Voir l’image
            </button>
          </LPopup>
        </LMarker>

        <!-- 🔴🟡🟢 Zones à risques -->
        <LCircle
          v-if="showZones"
          v-for="(zone, index) in riskZones"
          :key="'zone-' + index"
          :lat-lng="[zone.lat, zone.lng]"
          :radius="zone.radius"
          :color="zone.color"
          :fill-opacity="0.3"
          :stroke="false"
        />
      </LMap>
    </div>
  </client-only>
</template>