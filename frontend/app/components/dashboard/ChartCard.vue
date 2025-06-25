<template>
  <UCard>
    <template #header>
      <h3 class="text-lg font-semibold text-[#1b263b]">{{ title }}</h3>
    </template>
    <div class="h-[240px] flex items-center justify-center">
      <slot />
    </div>
  </UCard>
</template>

<script setup>
defineProps({ title: String })
</script>