<script setup>
import '~/assets/main.css'
</script>

<template>
  <NuxtLayout>
    <!-- 頁面切換時顯示頂部進度條 -->
    <NuxtLoadingIndicator color="#22c55e" :height="4" :throttle="0" />
    <NuxtPage />
  </NuxtLayout>
</template>
