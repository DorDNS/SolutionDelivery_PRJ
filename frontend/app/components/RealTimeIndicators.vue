<template>
  <div class="p-6">
    <h2 class="text-2xl font-semibold text-gray-800 mb-6">Indicateurs temps réel</h2>
    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
      <UCard
        v-for="(item, index) in indicators"
        :key="index"
        class="flex flex-col justify-between p-4"
        elevation="2"
        rounded="xl"
      >
        <h3 class="text-sm font-medium text-gray-500 uppercase tracking-wide">{{ item.label }}</h3>
        <p class="text-xl font-semibold text-gray-900 mt-2">
          {{ item.value || '—' }}
        </p>
      </UCard>
    </div>
  </div>
</template>

<script setup>
const indicators = [
  { label: "Localisation", value: "Paris" },
  { label: "Population", value: Math.floor(3_800_000 + Math.random() * 100_000) + " hab" },
  { label: "Jour", value: new Date().toLocaleDateString("fr-FR", { weekday: "long" }) },
  { label: "Météo", value: ["Soleil", "Pluie", "Nuageux", "Orage"][Math.floor(Math.random() * 4)] }, //METTRE LA METEO A JOUR
  { label: "Date acquisition", value: new Date().toLocaleString("fr-FR") },
];
</script>
