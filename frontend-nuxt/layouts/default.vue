<script setup>
import { 
  InformationCircleIcon, 
  ChartBarIcon, 
  ChatBubbleLeftRightIcon,
  BriefcaseIcon
} from '@heroicons/vue/24/outline'

const { data: updateDateData } = await useFetch('/api/metadata/last-update')
const updateDate = computed(() => updateDateData.value?.date || '無法取得')

// PWA Manifest
useHead({
  link: [
    { rel: 'manifest', href: '/manifest.webmanifest' },
    { rel: 'apple-touch-icon', href: '/pwa-192x192.png' }
  ],
  meta: [
    { name: 'theme-color', content: '#337AB7' }
  ]
})
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <header class="bg-primary-600 shadow-lg sticky top-0 z-50">
      <div class="container mx-auto px-4 h-16 flex items-center justify-between">
        <!-- Left Side: Logo + Nav -->
        <div class="flex items-center gap-6">
          <div class="logo">
            <NuxtLink to="/" class="flex items-center gap-2 text-xl font-bold text-white hover:text-primary-100 transition-colors">
              <img src="/logo.png" alt="Logo" class="w-10 h-10 object-contain" />
              <span>開放事求人</span>
            </NuxtLink>
          </div>
          <nav class="flex gap-1">
            <NuxtLink 
              to="/" 
              active-class="bg-primary-700 text-white shadow-inner"
              class="flex items-center gap-2 px-4 py-2 rounded-lg text-primary-100 hover:bg-primary-500 hover:text-white transition-all font-medium text-lg"
            >
              <BriefcaseIcon class="w-6 h-6" />
              <span class="hidden sm:inline">看職缺</span>
            </NuxtLink>
            <NuxtLink 
              to="/comments" 
              active-class="bg-primary-700 text-white shadow-inner"
              class="flex items-center gap-2 px-4 py-2 rounded-lg text-primary-100 hover:bg-primary-500 hover:text-white transition-all font-medium text-lg"
            >
              <ChatBubbleLeftRightIcon class="w-6 h-6" />
              <span class="hidden sm:inline">看留言</span>
            </NuxtLink>
            <NuxtLink 
              to="/charts" 
              active-class="bg-primary-700 text-white shadow-inner"
              class="flex items-center gap-2 px-4 py-2 rounded-lg text-primary-100 hover:bg-primary-500 hover:text-white transition-all font-medium text-lg"
            >
              <ChartBarIcon class="w-6 h-6" />
              <span class="hidden sm:inline">統計圖表</span>
            </NuxtLink>
            <NuxtLink 
              to="/about" 
              active-class="bg-primary-700 text-white shadow-inner"
              class="flex items-center gap-2 px-4 py-2 rounded-lg text-primary-100 hover:bg-primary-500 hover:text-white transition-all font-medium text-lg"
            >
              <InformationCircleIcon class="w-6 h-6" />
              <span class="hidden sm:inline">關於</span>
            </NuxtLink>
          </nav>
        </div>
        
        <!-- Right Side: Data Date -->
        <div class="hidden lg:flex items-center gap-2 text-white/80 text-sm bg-primary-700/50 px-3 py-1.5 rounded-full border border-white/10">
          <CalendarIcon class="w-4 h-4" />
          <span>資料日期：{{ updateDate }}</span>
        </div>
      </div>
    </header>

    <main class="flex-grow">
      <slot />
    </main>
    
    <footer class="bg-white border-t border-slate-200 py-8 mt-auto">
      <div class="footer-container">
        <p>&copy; 2024 Job Info. All rights reserved.</p>
      </div>
    </footer>

    <Toast />
  </div>
</template>
