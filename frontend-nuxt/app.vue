<script setup>
import '~/assets/main.css'
</script>

<template>
  <NuxtLayout>
    <!-- 頁面切換時顯示頂部進度條 -->
    <NuxtLoadingIndicator color="#f97316" :height="4" :throttle="0" />
    <NuxtPage />
  </NuxtLayout>
</template>
