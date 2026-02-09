<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  MagnifyingGlassIcon, 
  FunnelIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  ChevronDownIcon,
  ArrowsUpDownIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  Bars3Icon,
  XMarkIcon,
  InboxIcon,
  BriefcaseIcon,
  AdjustmentsHorizontalIcon
} from '@heroicons/vue/24/outline'
import type { Job, JobListResponse } from '@/types'

const router = useRouter()
const route = useRoute()
const { addToast } = useToast()

// Fetch update date for display
const { data: updateDateData } = await useFetch('/api/metadata/last-update')
const updateDate = computed(() => updateDateData.value?.date || '無法取得')

// Interfaces
interface PaginationState {
  current_page: number
  total_pages: number
  total_count: number
}

interface FilterState {
  org: string
  title: string
  sysnam: string
  places: string
  min_rank: string
  max_rank: string
  include_history: boolean
  include_parttime: boolean
}

// State
const jobs = ref<Job[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const pagination = ref<PaginationState>({
  current_page: 1,
  total_pages: 1,
  total_count: 0
})

const perPage = ref(15)
const jumpPage = ref('')

// Filters
const filters = ref<FilterState>({
  org: '',
  title: '',
  sysnam: '',
  places: '',
  min_rank: '',
  max_rank: '',
  include_history: false,
  include_parttime: false
})

const isSysnamModalOpen = ref(false)
const isPlaceModalOpen = ref(false)
const isRankModalOpen = ref(false)
const isSearchExpanded = ref(false)

// 標記：用於避免 handleSearch 和 watch 同時觸發請求競爭
const skipNextWatch = ref(false)

// Use shared date formatting utilities
const { isNewJob, isExpired } = useFormatDate()

// Use job constants for sysnam categorization
const { getSysnamType } = useJobConstants()


// Computed
const hasActiveFilters = computed(() => {
  return !!(filters.value.org || 
         filters.value.title || 
         filters.value.sysnam || 
         filters.value.places || 
         filters.value.min_rank || 
         filters.value.max_rank || 
         filters.value.include_history || 
         filters.value.include_parttime)
})

// Sorting
const sortField = ref('date_from')
const sortOrder = ref('desc')

// Helper to build query params
const buildParams = () => {
  const params: Record<string, any> = {
    page: pagination.value.current_page,
    per_page: perPage.value,
    sort: sortField.value,
    order: sortOrder.value,
    ...filters.value
  }
  // Filter out empty params
  Object.keys(params).forEach(key => {
    if (params[key] === '' || params[key] === null || params[key] === false) {
      delete params[key]
    }
  })
  return params
}

const updateUrl = () => {
  const query = buildParams()
  // Remove defaults for URL cleanliness
  if (query.page === 1) delete query.page
  if (query.per_page === 15) delete query.per_page
  if (query.sort === 'date_from') delete query.sort
  if (query.order === 'desc') delete query.order

  router.replace({ query })
}

// Initial Data Fetch (SSR)
const initFromUrl = () => {
  const query = route.query
  if (query.page) pagination.value.current_page = parseInt(query.page as string)
  if (query.per_page) perPage.value = parseInt(query.per_page as string)
  if (query.sort) sortField.value = query.sort as string
  if (query.order) sortOrder.value = query.order as string
  
  const filterKeys: (keyof FilterState)[] = ['org', 'title', 'sysnam', 'places', 'min_rank', 'max_rank']
  filterKeys.forEach(key => {
    if (query[key]) filters.value[key] = query[key] as any // Simplified casting
  })
  
  if (query.include_history) filters.value.include_history = query.include_history === 'true'
  if (query.include_parttime) filters.value.include_parttime = query.include_parttime === 'true'
}

initFromUrl()

// Use useFetch for SSR
const { data: initialData, error: initialError } = await useFetch<JobListResponse>('/api/jobs', {
  query: buildParams()
})

if (initialData.value) {
  jobs.value = initialData.value.jobs
  pagination.value = {
    current_page: initialData.value.current_page,
    total_pages: initialData.value.total_pages,
    total_count: initialData.value.total_count
  }
  loading.value = false
} else if (initialError.value) {
  error.value = '無法取得職缺資料，請稍後再試。'
  loading.value = false
}

// Client-side Fetch
const { fetchJobs: apiFetchJobs } = useJobApi()

const fetchJobs = async (isSearch = false) => {
  loading.value = true
  error.value = null
  updateUrl()

  try {
    const params = buildParams()
    const response = await apiFetchJobs(params)
    
    jobs.value = response.jobs
    pagination.value = {
      current_page: response.current_page,
      total_pages: response.total_pages,
      total_count: response.total_count
    }
    
    if (isSearch) {
      addToast(`搜尋完成，共找到 ${response.total_count} 筆職缺`, 'success')
    }
  } catch (err: any) {
    // 忽略被取消的請求（請求競爭導致）
    if (err?.name === 'AbortError' || err?.message?.includes('aborted') || err?.message?.includes('取消')) {
      console.debug('請求已被取消（可能是新搜尋觸發）')
      return
    }
    error.value = '無法取得職缺資料，請稍後再試。'
    console.error(err)
    addToast('無法取得職缺資料，請稍後再試', 'error')
  } finally {
    loading.value = false
  }
}

// Actions
const handleSearch = () => {
  pagination.value.current_page = 1
  // 設定標記，讓 watch 不要在 URL 更新後再次觸發搜尋
  skipNextWatch.value = true
  fetchJobs(true)
}

const clearFilters = () => {
  filters.value = {
    org: '',
    title: '',
    sysnam: '',
    places: '',
    min_rank: '',
    max_rank: '',
    include_history: false,
    include_parttime: false
  }
  sortField.value = 'date_from'
  sortOrder.value = 'desc'
  perPage.value = 15
  pagination.value.current_page = 1
  
  fetchJobs()
  addToast('已清空所有搜尋條件', 'info')
}

const changePage = (page: number) => {
  if (page >= 1 && page <= pagination.value.total_pages) {
    pagination.value.current_page = page
    fetchJobs()
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const handleSort = (field: string) => {
  if (sortField.value === field) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortOrder.value = 'desc'
  }
  fetchJobs()
}

const handleJumpPage = () => {
  const page = parseInt(jumpPage.value)
  if (page && page >= 1 && page <= pagination.value.total_pages) {
    changePage(page)
    jumpPage.value = ''
  } else {
    addToast('請輸入有效的頁碼', 'error')
  }
}

const handlePerPageChange = () => {
  pagination.value.current_page = 1
  fetchJobs()
}

// Watchers
watch(() => route.query, (newQuery, oldQuery) => {
  if (JSON.stringify(newQuery) === JSON.stringify(oldQuery)) return
  // 如果是由 handleSearch 觸發的 URL 更新，跳過這次 watch
  if (skipNextWatch.value) {
    skipNextWatch.value = false
    return
  }
  initFromUrl()
  fetchJobs()
})

// SEO
useSeoMeta({
  title: '開放事求人 - 人事行政總處事求人開放資料｜公務員職缺查詢',
  description: '最即時的人事行政總處事求人開放資料查詢平台。提供公務員職缺搜尋、歷史開缺、留言討論、統計圖表。支援 PWA 安裝。',
  keywords: '事求人, 人事行政總處事求人, 公務員職缺, 政府職缺, 開放資料, 公務人員, 職缺查詢, 開放事求人',
  robots: 'index,follow',
  ogTitle: '開放事求人 - 人事行政總處事求人開放資料｜公務員職缺查詢',
  ogDescription: '最即時的人事行政總處事求人開放資料查詢平台。提供公務員職缺搜尋、歷史開缺、留言討論、統計圖表。',
  ogUrl: 'https://opendgpa.shibaalin.com/',
  ogType: 'website',
})

// Canonical URL + FAQ Schema
useHead({
  link: [
    { rel: 'canonical', href: 'https://opendgpa.shibaalin.com/' }
  ],
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        'mainEntity': [
          {
            '@type': 'Question',
            'name': '如何搜尋公務員職缺？',
            'acceptedAnswer': {
              '@type': 'Answer',
              'text': '在開放事求人首頁使用關鍵字搜尋，可依機關、職系、職稱、地點等條件篩選，快速找到適合的公務員職缺。'
            }
          },
          {
            '@type': 'Question',
            'name': '開放事求人的資料來源是什麼？',
            'acceptedAnswer': {
              '@type': 'Answer',
              'text': '資料來源為政府資料開放平臺之「行政院人事行政總處事求人機關徵才資料」，每日自動同步更新，確保資料即時性。'
            }
          },
          {
            '@type': 'Question',
            'name': '什麼是重複開缺？',
            'acceptedAnswer': {
              '@type': 'Answer',
              'text': '當相同機關、相同職稱的職缺重複出現時，系統會標示為「重複開缺」，幫助您判斷該職位可能較不穩定或流動率較高。'
            }
          },
          {
            '@type': 'Question',
            'name': '可以在手機上使用嗎？',
            'acceptedAnswer': {
              '@type': 'Answer',
              'text': '是的，開放事求人支援 PWA（漸進式網頁應用程式），可以安裝到手機桌面像 App 一樣使用，並支援離線瀏覽已查看過的職缺。'
            }
          }
        ]
      })
    }
  ]
})
</script>

<template>
  <div class="page-container">
    <!-- Header -->
    <div class="mb-8 flex flex-col sm:flex-row sm:items-end justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold text-slate-800 flex items-center gap-3 mb-2">
          <div class="p-2 bg-primary-100 rounded-lg">
            <BriefcaseIcon class="w-8 h-8 text-primary-600" />
          </div>
          看職缺
        </h1>
        <p class="text-slate-500 text-lg">瀏覽全台最新公務人員職缺資訊</p>
      </div>
      <div class="inline-flex items-center gap-2 bg-white px-5 py-3 rounded-xl border border-slate-200 shadow-sm">
        <span class="text-slate-600 font-medium">總職缺：</span>
        <span class="text-emerald-600 font-bold text-2xl font-mono">{{ pagination.total_count }}</span>
        <span class="text-slate-400 text-sm">筆</span>
        <span class="text-slate-400 text-sm lg:hidden">（資料日期：{{ updateDate }}）</span>
      </div>
    </div>

    <!-- Compact Search Bar -->
    <div class="mb-6">
      <!-- Quick Search Row -->
      <div class="flex flex-col sm:flex-row gap-3 items-stretch sm:items-center">
        <!-- Quick Search Input -->
        <div class="flex-1 relative">
          <MagnifyingGlassIcon class="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input 
            v-model="filters.org"
            type="text" 
            placeholder="快速搜尋機關名稱..." 
            class="w-full pl-10 pr-4 py-3 bg-white border border-slate-200 rounded-xl focus:ring-2 focus:ring-primary-100 focus:border-primary-500 outline-none transition-all text-base shadow-sm"
            @keyup.enter="handleSearch"
          >
        </div>
        
        <!-- Action Buttons -->
        <div class="flex gap-2 justify-end">
          <button 
            type="button"
            @click="isSearchExpanded = !isSearchExpanded" 
            class="flex items-center gap-2 px-4 py-3 bg-white border border-slate-200 text-slate-600 rounded-xl font-medium transition-all hover:bg-slate-50 shadow-sm"
            :class="{ 'bg-primary-50 border-primary-200 text-primary-700': hasActiveFilters || isSearchExpanded }"
          >
            <AdjustmentsHorizontalIcon class="w-5 h-5" />
            <span>進階篩選</span>
            <ChevronDownIcon class="w-4 h-4 transition-transform" :class="{ 'rotate-180': isSearchExpanded }" />
          </button>
          <button 
            type="button"
            @click="handleSearch" 
            class="flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white px-5 py-3 rounded-xl font-medium transition-colors shadow-sm"
          >
            <MagnifyingGlassIcon class="w-5 h-5" />
            <span class="hidden sm:inline">搜尋</span>
          </button>
        </div>
      </div>

      <!-- Active Filters Summary -->
      <div v-if="hasActiveFilters && !isSearchExpanded" class="flex flex-wrap gap-2 mt-3">
        <span v-if="filters.org" class="text-xs bg-slate-100 text-slate-600 px-2 py-1 rounded-full flex items-center gap-1">
          機關: {{ filters.org }}
          <button @click="filters.org = ''; handleSearch()" class="hover:text-red-500"><XMarkIcon class="w-3 h-3" /></button>
        </span>
        <span v-if="filters.title" class="text-xs bg-slate-100 text-slate-600 px-2 py-1 rounded-full flex items-center gap-1">
          職稱: {{ filters.title }}
          <button @click="filters.title = ''; handleSearch()" class="hover:text-red-500"><XMarkIcon class="w-3 h-3" /></button>
        </span>
        <span v-if="filters.sysnam" class="text-xs bg-slate-100 text-slate-600 px-2 py-1 rounded-full flex items-center gap-1">
          職系: {{ filters.sysnam }}
          <button @click="filters.sysnam = ''; handleSearch()" class="hover:text-red-500"><XMarkIcon class="w-3 h-3" /></button>
        </span>
        <span v-if="filters.places" class="text-xs bg-slate-100 text-slate-600 px-2 py-1 rounded-full flex items-center gap-1">
          地點: {{ filters.places }}
          <button @click="filters.places = ''; handleSearch()" class="hover:text-red-500"><XMarkIcon class="w-3 h-3" /></button>
        </span>
        <span v-if="filters.min_rank || filters.max_rank" class="text-xs bg-slate-100 text-slate-600 px-2 py-1 rounded-full flex items-center gap-1">
          職等: {{ filters.min_rank || 1 }}~{{ filters.max_rank || 14 }}
          <button @click="filters.min_rank = ''; filters.max_rank = ''; handleSearch()" class="hover:text-red-500"><XMarkIcon class="w-3 h-3" /></button>
        </span>
        <span v-if="filters.include_history" class="text-xs bg-blue-50 text-blue-600 px-2 py-1 rounded-full flex items-center gap-1">
          含歷史
          <button @click="filters.include_history = false; handleSearch()" class="hover:text-red-500"><XMarkIcon class="w-3 h-3" /></button>
        </span>
        <span v-if="filters.include_parttime" class="text-xs bg-blue-50 text-blue-600 px-2 py-1 rounded-full flex items-center gap-1">
          含非正式
          <button @click="filters.include_parttime = false; handleSearch()" class="hover:text-red-500"><XMarkIcon class="w-3 h-3" /></button>
        </span>
      </div>

      <!-- Advanced Filters Panel -->
      <div v-show="isSearchExpanded" class="mt-4 p-5 bg-white border border-slate-200 rounded-xl shadow-sm">

      <!-- Unified Filter Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
        <!-- 1. Organization -->
        <div class="space-y-1.5">
          <label class="text-base font-medium text-slate-700">機關名稱</label>
          <div class="relative">
            <input 
              v-model="filters.org" 
              type="text" 
              placeholder="例如：內政部" 
              class="w-full pl-3 pr-3 py-2 bg-white border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary-100 focus:border-primary-500 outline-none transition-all text-base"
              @keyup.enter="handleSearch"
            >
          </div>
        </div>

        <!-- 2. Title -->
        <div class="space-y-1.5">
          <label class="text-base font-medium text-slate-700">職稱</label>
          <input 
            v-model="filters.title" 
            type="text" 
            placeholder="例如：科員" 
            class="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary-100 focus:border-primary-500 outline-none transition-all text-base"
            @keyup.enter="handleSearch"
          >
        </div>

        <!-- 3. Sysnam -->
        <div class="space-y-1.5">
          <label class="text-base font-medium text-slate-700">職系</label>
          <div class="relative">
            <input 
              type="text" 
              readonly
              :value="filters.sysnam"
              placeholder="例如：綜合行政" 
              class="w-full pl-3 pr-10 py-2 bg-white border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary-100 focus:border-primary-500 outline-none transition-all text-base cursor-pointer hover:bg-slate-50"
              @click="isSysnamModalOpen = true"
            >
            <button 
              type="button"
              @click.stop="isSysnamModalOpen = true"
              class="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-slate-400 hover:text-slate-600"
            >
              <Bars3Icon class="w-5 h-5" />
            </button>
          </div>
        </div>

        <!-- 4. Place -->
        <div class="space-y-1.5">
          <label class="text-base font-medium text-slate-700">地點</label>
          <div class="relative">
            <input 
              type="text" 
              readonly
              :value="filters.places"
              placeholder="例如：臺北市" 
              class="w-full pl-3 pr-10 py-2 bg-white border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary-100 focus:border-primary-500 outline-none transition-all text-base cursor-pointer hover:bg-slate-50"
              @click="isPlaceModalOpen = true"
            >
            <button 
              type="button"
              @click.stop="isPlaceModalOpen = true"
              class="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-slate-400 hover:text-slate-600"
            >
              <Bars3Icon class="w-5 h-5" />
            </button>
          </div>
        </div>

        <!-- 5. Rank Range -->
        <div class="space-y-1.5">
          <label class="text-base font-medium text-slate-700">職等範圍</label>
          <div class="relative">
            <input 
              type="text" 
              readonly
              :value="filters.min_rank || filters.max_rank ? `${filters.min_rank || 1} ~ ${filters.max_rank || 14} 職等` : ''"
              placeholder="請選擇職等範圍" 
              class="w-full pl-3 pr-10 py-2 bg-white border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary-100 focus:border-primary-500 outline-none transition-all text-base cursor-pointer hover:bg-slate-50"
              @click="isRankModalOpen = true"
            >
            <button 
              type="button"
              @click.stop="isRankModalOpen = true"
              class="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-slate-400 hover:text-slate-600"
            >
              <Bars3Icon class="w-5 h-5" />
            </button>
          </div>
        </div>

        <!-- 6. Actions & Toggles (Spans remaining columns) -->
        <div class="flex flex-col sm:flex-row sm:items-end justify-between gap-4 lg:col-span-3">
          <!-- Toggles -->
          <div class="flex flex-wrap items-center gap-4 py-2">
            <label class="flex items-center gap-2 cursor-pointer group">
              <div class="relative inline-flex items-center">
                <input type="checkbox" v-model="filters.include_history" class="sr-only peer">
                <div class="w-11 h-6 bg-slate-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-100 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
              </div>
              <span class="text-base font-medium text-slate-700 group-hover:text-slate-900">包含歷史職缺</span>
            </label>

            <label class="flex items-center gap-2 cursor-pointer group">
              <div class="relative inline-flex items-center">
                <input type="checkbox" v-model="filters.include_parttime" class="sr-only peer">
                <div class="w-11 h-6 bg-slate-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-100 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
              </div>
              <span class="text-base font-medium text-slate-700 group-hover:text-slate-900">包含非正式人員</span>
            </label>
          </div>
          
          <!-- Buttons -->
          <div class="flex items-center gap-3">
            <button 
              type="button"
              @click="clearFilters" 
              class="flex items-center gap-2 bg-white hover:bg-slate-50 text-slate-600 border border-slate-200 px-4 py-2.5 rounded-lg font-medium transition-colors shadow-sm hover:shadow active:scale-95 transform duration-100"
            >
              <XMarkIcon class="w-5 h-5" />
              清空
            </button>
            <button 
              type="button"
              @click="handleSearch" 
              class="flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white px-6 py-2.5 rounded-lg font-medium transition-colors shadow-sm hover:shadow active:scale-95 transform duration-100"
            >
              <MagnifyingGlassIcon class="w-5 h-5" />
              搜尋
            </button>
          </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Results Section -->
    <section>
      <!-- Loading State -->
      <LoadingSpinner v-if="loading" message="正在載入職缺資料..." />
      
      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 border border-red-100 text-red-600 p-8 rounded-2xl text-center shadow-sm">
        <div class="flex justify-center mb-3">
          <XMarkIcon class="w-12 h-12 text-red-400" />
        </div>
        <h3 class="text-lg font-bold mb-2">發生錯誤</h3>
        <p>{{ error }}</p>
        <button @click="fetchJobs(false)" class="mt-4 text-sm font-medium text-red-600 hover:text-red-700 underline">
          重試
        </button>
      </div>

      <div v-else>
        <!-- Empty State -->
        <div v-if="jobs.length === 0" class="flex flex-col items-center justify-center py-24 text-center">
          <div class="bg-slate-50 p-6 rounded-full mb-4">
            <InboxIcon class="w-12 h-12 text-slate-300" />
          </div>
          <h3 class="text-lg font-bold text-slate-900 mb-2">找不到符合條件的職缺</h3>
          <p class="text-slate-500 max-w-sm mx-auto mb-6">
            試著調整搜尋條件，或是移除部分篩選項目來查看更多結果。
          </p>
          <button 
            @click="clearFilters"
            class="inline-flex items-center gap-2 px-4 py-2 bg-white border border-slate-300 rounded-lg text-slate-700 font-medium hover:bg-slate-50 hover:border-slate-400 transition-all shadow-sm"
          >
            <XMarkIcon class="w-4 h-4" />
            清空所有條件
          </button>
        </div>

        <div v-else>

        <!-- Desktop View (Table) -->
        <div class="hidden md:block bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden mb-8">
          <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse">
              <thead>
                <tr class="bg-primary-600 border-b border-primary-700 text-white text-base font-bold tracking-wide whitespace-nowrap">
                  <th class="p-4 cursor-pointer hover:bg-primary-700 transition-colors group w-[180px]" @click="handleSort('org')">
                    <div class="flex items-center gap-1">
                      機關名稱
                      <component :is="sortField === 'org' ? (sortOrder === 'asc' ? ArrowUpIcon : ArrowDownIcon) : ArrowsUpDownIcon" class="w-4 h-4 text-blue-200 group-hover:text-white" />
                    </div>
                  </th>
                  <th class="p-4 cursor-pointer hover:bg-primary-700 transition-colors group w-[120px]" @click="handleSort('title')">
                    <div class="flex items-center gap-1">
                      職稱
                      <component :is="sortField === 'title' ? (sortOrder === 'asc' ? ArrowUpIcon : ArrowDownIcon) : ArrowsUpDownIcon" class="w-4 h-4 text-blue-200 group-hover:text-white" />
                    </div>
                  </th>
                  <th class="p-4 cursor-pointer hover:bg-primary-700 transition-colors group w-[120px]" @click="handleSort('sysnam')">
                    <div class="flex items-center gap-1">
                      職系
                      <component :is="sortField === 'sysnam' ? (sortOrder === 'asc' ? ArrowUpIcon : ArrowDownIcon) : ArrowsUpDownIcon" class="w-4 h-4 text-blue-200 group-hover:text-white" />
                    </div>
                  </th>
                  <th class="p-4 cursor-pointer hover:bg-primary-700 transition-colors group w-[90px]" @click="handleSort('rank')">
                    <div class="flex items-center gap-1">
                      職等
                      <component :is="sortField === 'rank' ? (sortOrder === 'asc' ? ArrowUpIcon : ArrowDownIcon) : ArrowsUpDownIcon" class="w-4 h-4 text-blue-200 group-hover:text-white" />
                    </div>
                  </th>
                  <th class="p-4 cursor-pointer hover:bg-primary-700 transition-colors group w-[100px]" @click="handleSort('place')">
                    <div class="flex items-center gap-1">
                      工作地點
                      <component :is="sortField === 'place' ? (sortOrder === 'asc' ? ArrowUpIcon : ArrowDownIcon) : ArrowsUpDownIcon" class="w-4 h-4 text-blue-200 group-hover:text-white" />
                    </div>
                  </th>
                  <th class="p-4 cursor-pointer hover:bg-primary-700 transition-colors group w-[130px]" @click="handleSort('date_from')">
                    <div class="flex items-center gap-1">
                      期間
                      <component :is="sortField === 'date_from' ? (sortOrder === 'asc' ? ArrowUpIcon : ArrowDownIcon) : ArrowsUpDownIcon" class="w-4 h-4 text-blue-200 group-hover:text-white" />
                    </div>
                  </th>
                  <th class="p-4 text-left w-[80px]">狀態</th>
                  <th class="p-4 text-center w-[70px]">查看</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100 text-sm">
                <tr v-for="job in jobs" :key="job.id" class="hover:bg-blue-50/50 transition-colors duration-200 border-b border-slate-50 last:border-0 group">
                  <td class="p-4 align-top">
                    <div class="font-bold text-slate-700 text-base break-words leading-tight">{{ job.org }}</div>
                  </td>
                  <td class="p-4 align-top">
                    <span 
                      class="font-bold text-slate-700 text-base truncate max-w-[200px] block"
                      :title="job.title"
                    >
                      {{ job.title }}
                    </span>
                  </td>
                  <td class="p-4 align-top">
                    <div class="flex flex-col gap-1.5 items-start">
                      <span 
                        class="inline-flex items-center px-2.5 py-1 rounded text-sm font-bold whitespace-nowrap"
                        :class="{
                          'bg-blue-50 text-blue-700 border border-blue-200': getSysnamType(job.sysnam) === 'admin',
                          'bg-emerald-50 text-emerald-700 border border-emerald-200': getSysnamType(job.sysnam) === 'tech',
                          'bg-slate-100 text-slate-600 border border-slate-200': getSysnamType(job.sysnam) === 'unknown'
                        }"
                      >
                        {{ job.sysnam }}
                      </span>
                    </div>
                  </td>
                  <td class="p-4 align-top">
                    <span class="text-slate-700 text-sm font-bold whitespace-nowrap">
                      {{ job.rank_display || job.rank }}
                    </span>
                  </td>
                  <td class="p-4 align-top">
                    <span class="text-slate-700 text-base font-bold truncate block max-w-[120px]" :title="job.place">
                      {{ job.place }}
                    </span>
                  </td>
                  <td class="p-4 align-top">
                    <div class="flex flex-col">
                      <div class="flex items-center gap-1.5">
                        <span class="text-xs font-mono text-slate-700 font-bold leading-tight">{{ job.date_from }}</span>
                        <span 
                          v-if="isNewJob(job.announce_date)" 
                          class="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-bold bg-red-500 text-white animate-pulse"
                        >
                          NEW
                        </span>
                      </div>
                      <span class="text-xs font-mono text-slate-500 leading-tight mt-1">~ {{ job.date_to }}</span>
                    </div>
                  </td>
                  <td class="p-4 align-top">
                    <div class="flex flex-wrap gap-1">
                      <span 
                        v-if="isExpired(job.date_to)" 
                        class="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-bold bg-slate-200 text-slate-500"
                      >
                        已逾期
                      </span>
                      <span v-if="job.comment_count > 0" class="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                        有留言
                      </span>
                      <span v-if="job.history_count > 0" class="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-bold bg-amber-50 text-amber-700 border border-amber-200">
                        曾開缺
                      </span>
                      <span v-if="!isExpired(job.date_to) && !job.comment_count && !job.history_count" class="text-slate-400 text-sm">
                        —
                      </span>
                    </div>
                  </td>
                  <td class="p-4 align-top text-center">
                    <NuxtLink 
                      :to="`/job/${job.id}`"
                      class="inline-flex items-center justify-center px-3 py-1.5 bg-white border border-slate-300 text-slate-700 rounded-lg text-xs font-bold hover:bg-primary-600 hover:text-white hover:border-primary-600 transition-all shadow-sm whitespace-nowrap"
                    >
                      查看
                    </NuxtLink>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Mobile View (Cards) -->
        <div class="md:hidden grid grid-cols-1 gap-4 mb-8">
          <JobCard 
            v-for="job in jobs" 
            :key="job.id" 
            :job="job" 
          />
        </div>


        <!-- Pagination -->
        <Pagination
          :currentPage="pagination.current_page"
          :totalPages="pagination.total_pages"
          :perPage="perPage"
          @update:currentPage="changePage"
          @update:perPage="(val) => { perPage = val; handlePerPageChange() }"
        />
        </div>
      </div>
    </section>

    <!-- Modals -->
    <SysnamModal 
      v-model="filters.sysnam" 
      :isOpen="isSysnamModalOpen" 
      @close="isSysnamModalOpen = false" 
    />
    <PlaceModal 
      v-model="filters.places" 
      :isOpen="isPlaceModalOpen" 
      @close="isPlaceModalOpen = false" 
    />
    <RankModal 
      v-model:minRank="filters.min_rank"
      v-model:maxRank="filters.max_rank"
      :isOpen="isRankModalOpen" 
      @close="isRankModalOpen = false" 
    />
  </div>
</template>
