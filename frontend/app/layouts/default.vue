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
    //Index
    slogan: "Aidez votre ville à rester propre. Uploadez des images de poubelles et contribuez à une meilleure gestion des déchets urbains grâce à l’IA.",
    uploadButton: 'Uploader une image',
    dashboardprev: 'Dashboard',
    dashboardDescription: 'Retrouvez ici les graphiques, les cartes interactives et les statistiques en temps réel.',
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
    emptyLabel: "Vide",
    fullLabel: "Pleine",
    noLabel: "Sans label",
    annotationsLabel: "Annotations",
  },
  en: {
    //Header
    label: "Language",
    headerup: "Upload",
    headernav: "Navigation",
    headerconstraints: "Constraints",
    uploadButton: 'Upload an image',
    //Index
    slogan: "Help your city stay clean. Upload images of trash and contribute to better urban waste management with AI.",
    dashboardprev: 'Dashboard Overview',
    dashboardDescription: 'Soon, graphs, interactive maps, and collection statistics will be displayed here.',
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
    emptyLabel: "Empty",
    fullLabel: "Full",
    noLabel: "No label",
    annotationsLabel: "Annotations",
  },
}

// Fournir les données aux composants enfants
provide('currentLanguage', currentLanguage)
provide('translations', translations)
</script>