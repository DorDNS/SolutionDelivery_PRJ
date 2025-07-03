<template>
  <div class="flex flex-col min-h-screen bg-white">
    <Header :changelanguage="changeLanguage" />
    <main class="flex-1">
      <slot />
    </main>
    <Footer />
  </div>
</template>

<script setup>
import { ref, provide } from 'vue'
import Header from '~/components/Header.vue'
import Footer from '~/components/Footer.vue'

const currentLanguage = ref('fr') // Langue par défaut
const translations = {
  fr: {
    //Header
    label: "Langue",
    headerup : "Uploader",
    headernav: "Navigation",
    headerconstraints: "Contraintes",
    //footer
    footerText: '2025 TrashMap. Tous droits réservés.',
    //Index
    slogan: "Aidez votre ville à rester propre. Uploadez des images de poubelles et contribuez à une meilleure gestion des déchets urbains grâce à l’IA.",
    uploadButton: 'Uploader une image',
    dashboardprev: 'Dashboard',
    dashboardDescription: 'Retrouvez ici les graphiques, les cartes interactives et les statistiques en temps réel.',
    // Realtimeindicators
    realtimetitle: "Indicateurs en temps réel",
    loc:"Localisation",
    pop:"Population",
    day: "Jour",
    meteo: "Météo",
    gettime: "Date d’acquisition",
    hab:"hab",
    //DashboardPreview
    filtre : "Filtres",
    allStates: "Tous",
    emptyState: "Vide",
    overflowState: "Débordée",
    allPeriods: "Toutes périodes",
    last7Days: "7 derniers jours",
    last30Days: "30 derniers jours",
    thisYear: "Cette année",
    loaddash: "Chargement des données du dashboard...",
    visu1title: "Nombre total d’images",
    visu2title: "Répartition des annotations",
    visu3title: "Couleur Moyenne globale",
    visu4title: "Histogramme global des tailles (px)",
    nbimg : "Nombre d'images",
    visu5title: "Histogramme des tons dominants",
    Red:"Rouge",
    Green:"Vert",
    Blue:"Bleu",
    visu6title: "Histogramme des contrastes",
    low: "Faible",
    medium: "Moyen",
    high: "Haut",
    visu7title: "Histogramme du nombre de contours",
    visu8title: "Contours moyen selon les labels",
    nbmoycontours: "Nombre moyen de contours",
    emptyLabel: "Vide",
    fullLabel: "Pleine",
    noLabel: "Sans label",
    annotationsLabel: "Annotations",
    cartetitle : "Carte des marchés, chantiers, poubelles et zones à risques",
    checkboxmarche : "Marchés actifs aujourd'hui",
    checkboxchantiers : "Chantiers en cours",
    checkboxdepots : "Poubelles",
    checkboxzones : "Zones à risques",
    dashboardDescription : "Visualisations interactives et statistiques en temps réel",
  },
  en: {
    //Header
    label: "Language",
    headerup: "Upload",
    headernav: "Navigation",
    headerconstraints: "Constraints",
    uploadButton: 'Upload an image',
    //Footer
    footerText: '2025 TrashMap. All rights reserved.',
    //Index
    slogan: "Help your city stay clean. Upload images of trash and contribute to better urban waste management with AI.",
    dashboardprev: 'Dashboard Overview',
    dashboardDescription: 'Soon, graphs, interactive maps, and collection statistics will be displayed here.',
    // Realtimeindicators
    realtimetitle: "Real-time indicators",
    loc: "Location",
    pop:"Population",
    day: "Day",
    meteo: "Weather",
    gettime: "Acquisition date",
    hab: "inhab",
    //DashboardPreview
    filtre : "Filters",
    allStates: "All",
    emptyState: "Empty",
    overflowState: "Overflowing",
    allPeriods: "All periods",
    last7Days: "Last 7 days",
    last30Days: "Last 30 days",
    thisYear: "This year",
    loaddash: "Loading dashboard data...",
    visu1title: "Total number of images",
    visu2title: "Distribution of annotations",
    visu3title: "Average global color",
    visu4title: "Global size histogram (px)",
    nbimg : "Number of images",
    visu5title: "Histogram of dominant tones",
    Red: "Red",
    Green: "Green",
    Blue: "Blue",
    visu6title: "Histogram of contrasts",
    low: "Low",
    medium: "Medium",
    high: "High",
    visu7title: "Histogram of number of edges",
    visu8title: "Average contours by labels",
    nbmoycontours: "Average number of edges",
    emptyLabel: "Empty",
    fullLabel: "Full",
    noLabel: "No label",
    annotationsLabel: "Annotations",
    cartetitle : "Map of markets, construction sites, trash bins, and risk zones",
    checkboxmarche : "Markets active today",
    checkboxchantiers : "Construction sites",
    checkboxdepots : "Trash bins",
    checkboxzones : "Risk zones",
    dashboardDescription : "Interactive visualizations and real-time statistics",
  },
}

// Fournir les données aux composants enfants
provide('currentLanguage', currentLanguage)
provide('translations', translations)
</script>