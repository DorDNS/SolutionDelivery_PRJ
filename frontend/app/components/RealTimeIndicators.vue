<template>
  <div class="space-y-6">
    <h2 class="text-2xl font-semibold text-[#1b263b]">Indicateurs en temps réel</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
      <UCard
        v-for="(item, index) in indicators"
        :key="index"
      >
        <template #header>
          <h3 class="text-base font-semibold text-[#1b263b]">{{ item.label }}</h3>
        </template>
        <div class="h-[120px] flex items-center justify-center"> <!-- Hauteur réduite -->
          <p class="text-xl font-medium text-[#1b263b]"> <!-- Texte plus petit -->
            {{ item.value || '—' }}
          </p>
        </div>
      </UCard>
    </div>
  </div>
</template>

<script setup>
const indicators = [
  { label: "Localisation", value: "Paris" },
  { label: "Population", value: Math.floor(3_800_000 + Math.random() * 100_000) + " hab" },
  { label: "Jour", value: new Date().toLocaleDateString("fr-FR", { weekday: "long" }) },
  { label: "Météo", value: ["Soleil", "Pluie", "Nuageux", "Orage"][Math.floor(Math.random() * 4)] },
  { label: "Date acquisition", value: new Date().toLocaleString("fr-FR") },
];
</script>