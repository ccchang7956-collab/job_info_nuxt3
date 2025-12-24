<script setup>
import { 
  InformationCircleIcon, 
  ChartBarIcon, 
  ChatBubbleLeftRightIcon,
  BriefcaseIcon,
  CalendarIcon
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
        <!-- Left Side: Logo -->
        <div class="logo flex-shrink-0">
          <NuxtLink to="/" class="flex items-center gap-2 text-xl font-bold text-white hover:text-primary-100 transition-colors">
            <img src="/logo.png" alt="Logo" class="w-10 h-10 object-contain" />
            <span class="hidden sm:inline whitespace-nowrap">開放事求人</span>
          </NuxtLink>
        </div>
        
        <!-- Right Side: Nav -->
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
    
    
    <footer class="bg-slate-800 text-slate-300 py-6 mt-auto">
      <div class="container mx-auto px-4 text-center text-sm space-y-2">
        <p>
          © 2024 本網站使用
          <a href="https://data.gov.tw/" target="_blank" class="text-primary-300 hover:text-primary-200 underline">政府資料開放平臺</a>
          之
          <a href="https://data.gov.tw/dataset/7229" target="_blank" class="text-primary-300 hover:text-primary-200 underline">行政院人事行政總處事求人機關徵才資料</a>。
        </p>
        <p class="text-slate-400">
          與官方版本差別可以在「<NuxtLink to="/about" class="text-primary-300 hover:text-primary-200 underline">關於</NuxtLink>」中查看。
          ｜
          <NuxtLink to="/privacy-policy" class="text-primary-300 hover:text-primary-200 underline">隱私權政策</NuxtLink>
        </p>
      </div>
    </footer>

    <Toast />
  </div>
</template>
