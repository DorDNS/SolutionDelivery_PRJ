<template>
  <header class="bg-[#1b263b] text-white shadow-md">
    <UContainer class="flex justify-between items-center py-4">
      <h1 class="text-2xl font-bold tracking-tight">TrashMap</h1>
      <nav class="flex gap-4">
        <UButton to="/" variant="ghost" class="text-white hover:text-[#e0e1dd]">Accueil</UButton>
        <UButton to="/upload" color="primary">Uploader</UButton>
      </nav>
    </UContainer>
  </header>
</template>