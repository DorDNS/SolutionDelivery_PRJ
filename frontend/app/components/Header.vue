<template>
  <header class="bg-[#1b263b] text-white shadow-md">
    <UContainer class="flex justify-between items-center py-4">
      <NuxtLink to="/" class="flex items-center gap-2">
        <img
          src="/images/icone-trashmap.svg"
          alt="Logo TrashMap"
          class="h-9 w-auto"
        />
        <span class="text-2xl font-bold tracking-tight text-white">
          TrashMap
        </span>
      </NuxtLink>
      <nav class="flex gap-4">
        <UButton to="/" variant="ghost" class="text-white hover:text-[#e0e1dd]">Accueil</UButton>
        <UButton to="/upload" color="primary">Uploader</UButton>
      </nav>
    </UContainer>
  </header>
</template>