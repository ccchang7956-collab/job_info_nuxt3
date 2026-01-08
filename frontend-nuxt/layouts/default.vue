<script setup>
import { ref, watch } from 'vue'
import { 
  CalendarIcon,
  InformationCircleIcon, 
  ChartBarIcon, 
  ChatBubbleLeftRightIcon,
  BriefcaseIcon,
  Bars3Icon,
  XMarkIcon
} from '@heroicons/vue/24/outline'

const route = useRoute()

const { data: updateDateData } = await useFetch('/api/metadata/last-update')
const updateDate = computed(() => updateDateData.value?.date || '無法取得')

// 動態年份
const currentYear = new Date().getFullYear()

// 手機版選單狀態
const isMobileMenuOpen = ref(false)

const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}

const closeMobileMenu = () => {
  isMobileMenuOpen.value = false
}

// 路由變更時自動關閉選單
watch(() => route.path, () => {
  closeMobileMenu()
})

// PWA Manifest + WebSite Schema
useHead({
  link: [
    { rel: 'manifest', href: '/manifest.webmanifest' },
    { rel: 'apple-touch-icon', href: '/apple-touch-icon.png' }
  ],
  meta: [
    { name: 'theme-color', content: '#337AB7' }
  ],
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'WebSite',
        'name': '開放事求人',
        'alternateName': '公務人員職缺查詢',
        'url': 'https://opendgpa.shibaalin.com'
      })
    }
  ]
})
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <header class="bg-primary-600 shadow-lg sticky top-0 z-50">
      <div class="container mx-auto px-4 h-16 flex items-center justify-between">
        <!-- Left Side: Logo + 網站名稱 -->
        <div class="logo flex-shrink-0">
          <NuxtLink to="/" class="flex items-center gap-2 text-2xl font-bold text-white hover:text-primary-100 transition-colors" @click="closeMobileMenu">
            <img src="/logo.png" alt="開放事求人 Logo" class="w-12 h-12 object-contain" />
            <span class="whitespace-nowrap">開放事求人</span>
          </NuxtLink>
        </div>
        
        <!-- Desktop Nav -->
        <nav class="hidden md:flex gap-1">
          <NuxtLink 
            to="/" 
            active-class="bg-primary-700 text-white shadow-inner"
            class="flex items-center gap-2 px-4 py-2 rounded-lg text-primary-100 hover:bg-primary-500 hover:text-white transition-all font-medium text-lg"
          >
            <BriefcaseIcon class="w-6 h-6" />
            <span>看職缺</span>
          </NuxtLink>
          <NuxtLink 
            to="/comments" 
            active-class="bg-primary-700 text-white shadow-inner"
            class="flex items-center gap-2 px-4 py-2 rounded-lg text-primary-100 hover:bg-primary-500 hover:text-white transition-all font-medium text-lg"
          >
            <ChatBubbleLeftRightIcon class="w-6 h-6" />
            <span>看留言</span>
          </NuxtLink>
          <NuxtLink 
            to="/charts" 
            active-class="bg-primary-700 text-white shadow-inner"
            class="flex items-center gap-2 px-4 py-2 rounded-lg text-primary-100 hover:bg-primary-500 hover:text-white transition-all font-medium text-lg"
          >
            <ChartBarIcon class="w-6 h-6" />
            <span>統計圖表</span>
          </NuxtLink>
          <NuxtLink 
            to="/about" 
            active-class="bg-primary-700 text-white shadow-inner"
            class="flex items-center gap-2 px-4 py-2 rounded-lg text-primary-100 hover:bg-primary-500 hover:text-white transition-all font-medium text-lg"
          >
            <InformationCircleIcon class="w-6 h-6" />
            <span>關於</span>
          </NuxtLink>
        </nav>
        
        <!-- Right Side: Data Date (Desktop) -->
        <div class="hidden lg:flex items-center gap-2 text-white/80 text-sm bg-primary-700/50 px-3 py-1.5 rounded-full border border-white/10">
          <CalendarIcon class="w-4 h-4" />
          <span>資料日期：{{ updateDate }}</span>
        </div>
        
        <!-- Mobile Menu Button -->
        <button 
          @click="toggleMobileMenu"
          class="md:hidden p-2 rounded-lg text-white hover:bg-primary-500 transition-colors"
          :aria-label="isMobileMenuOpen ? '關閉選單' : '開啟選單'"
        >
          <XMarkIcon v-if="isMobileMenuOpen" class="w-7 h-7" />
          <Bars3Icon v-else class="w-7 h-7" />
        </button>
      </div>
      
      <!-- Mobile Menu Dropdown -->
      <Transition
        enter-active-class="transition-all duration-200 ease-out"
        enter-from-class="opacity-0 -translate-y-2"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition-all duration-150 ease-in"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 -translate-y-2"
      >
        <nav v-if="isMobileMenuOpen" class="md:hidden bg-primary-700 border-t border-primary-500">
          <div class="container mx-auto px-4 py-3 flex flex-col gap-1">
            <NuxtLink 
              to="/" 
              active-class="bg-primary-800 text-white"
              class="flex items-center gap-3 px-4 py-3 rounded-lg text-primary-100 hover:bg-primary-600 hover:text-white transition-all font-medium text-lg"
              @click="closeMobileMenu"
            >
              <BriefcaseIcon class="w-6 h-6" />
              <span>看職缺</span>
            </NuxtLink>
            <NuxtLink 
              to="/comments" 
              active-class="bg-primary-800 text-white"
              class="flex items-center gap-3 px-4 py-3 rounded-lg text-primary-100 hover:bg-primary-600 hover:text-white transition-all font-medium text-lg"
              @click="closeMobileMenu"
            >
              <ChatBubbleLeftRightIcon class="w-6 h-6" />
              <span>看留言</span>
            </NuxtLink>
            <NuxtLink 
              to="/charts" 
              active-class="bg-primary-800 text-white"
              class="flex items-center gap-3 px-4 py-3 rounded-lg text-primary-100 hover:bg-primary-600 hover:text-white transition-all font-medium text-lg"
              @click="closeMobileMenu"
            >
              <ChartBarIcon class="w-6 h-6" />
              <span>統計圖表</span>
            </NuxtLink>
            <NuxtLink 
              to="/about" 
              active-class="bg-primary-800 text-white"
              class="flex items-center gap-3 px-4 py-3 rounded-lg text-primary-100 hover:bg-primary-600 hover:text-white transition-all font-medium text-lg"
              @click="closeMobileMenu"
            >
              <InformationCircleIcon class="w-6 h-6" />
              <span>關於</span>
            </NuxtLink>
            <!-- 資料日期 (Mobile) -->
            <div class="flex items-center gap-2 text-white/70 text-sm px-4 py-2 mt-2 border-t border-primary-500">
              <CalendarIcon class="w-4 h-4" />
              <span>資料日期：{{ updateDate }}</span>
            </div>
          </div>
        </nav>
      </Transition>
    </header>

    <main class="flex-grow">
      <slot />
    </main>
    
    
    <footer class="bg-white border-t border-slate-200 text-slate-600 py-8 mt-auto">
      <div class="container mx-auto px-4 text-center text-sm space-y-3 flex flex-col items-center">
        <p>
          © {{ currentYear }} 本網站使用
          <a href="https://data.gov.tw/" target="_blank" rel="noopener noreferrer" class="text-primary-600 hover:text-primary-700 underline">政府資料開放平臺</a>
          之
          <a href="https://data.gov.tw/dataset/7229" target="_blank" rel="noopener noreferrer" class="text-primary-600 hover:text-primary-700 underline">行政院人事行政總處事求人機關徵才資料</a>。
        </p>
        <p>
          與官方版本差別可以在「<NuxtLink to="/about" class="text-primary-600 hover:text-primary-700 underline">關於</NuxtLink>」中查看。
          ｜
          <NuxtLink to="/privacy-policy" class="text-primary-600 hover:text-primary-700 underline">隱私權政策</NuxtLink>
        </p>
      </div>
    </footer>

    <Toast />
    <DomainMigrationModal />
  </div>
</template>
