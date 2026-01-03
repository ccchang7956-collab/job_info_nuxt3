<script setup>
import '~/assets/main.css'
</script>

<template>
  <NuxtLayout>
    <!-- 頁面切換時顯示頂部進度條 -->
    <NuxtLoadingIndicator color="#3b82f6" :height="3" />
    <NuxtPage />
  </NuxtLayout>
</template>
