<script setup>
// Auto-imports: ref, computed, watch, onMounted, useRoute, useRouter, useNuxtApp
import { 
  MagnifyingGlassIcon, 
  FunnelIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  ArrowPathIcon,
  ChatBubbleLeftIcon,
  ArrowsUpDownIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  Bars3Icon,
  XMarkIcon,
  InboxIcon,
  BriefcaseIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const route = useRoute()
const { addToast } = useToast()

// State
const jobs = ref([])
const loading = ref(true)
const error = ref(null)
const pagination = ref({
  current_page: 1,
  total_pages: 1,
  total_count: 0
})

const perPage = ref(15)
const jumpPage = ref('')

// Filters
const filters = ref({
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

// Computed
const hasActiveFilters = computed(() => {
  return filters.value.org || 
         filters.value.title || 
         filters.value.sysnam || 
         filters.value.places || 
         filters.value.min_rank || 
         filters.value.max_rank || 
         filters.value.include_history || 
         filters.value.include_parttime
})

// Sorting
const sortField = ref('date_from')
const sortOrder = ref('desc')

// Helper to build query params
const buildParams = () => {
  const params = {
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
  if (query.page) pagination.value.current_page = parseInt(query.page)
  if (query.per_page) perPage.value = parseInt(query.per_page)
  if (query.sort) sortField.value = query.sort
  if (query.order) sortOrder.value = query.order
  
  const filterKeys = ['org', 'title', 'sysnam', 'places', 'min_rank', 'max_rank']
  filterKeys.forEach(key => {
    if (query[key]) filters.value[key] = query[key]
  })
  
  if (query.include_history) filters.value.include_history = query.include_history === 'true'
  if (query.include_parttime) filters.value.include_parttime = query.include_parttime === 'true'
}

initFromUrl()

// Use useFetch for SSR
const { data: initialData, error: initialError } = await useFetch('/api/jobs', {
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
const fetchJobs = async (isSearch = false) => {
  loading.value = true
  error.value = null
  updateUrl()

  try {
    const params = buildParams()
    const response = await $fetch('/api/jobs', { params })
    
    jobs.value = response.jobs
    pagination.value = {
      current_page: response.current_page,
      total_pages: response.total_pages,
      total_count: response.total_count
    }
    
    if (isSearch) {
      addToast(`搜尋完成，共找到 ${response.total_count} 筆職缺`, 'success')
    }
  } catch (err) {
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

const changePage = (page) => {
  if (page >= 1 && page <= pagination.value.total_pages) {
    pagination.value.current_page = page
    fetchJobs()
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const handleSort = (field) => {
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
  initFromUrl()
  fetchJobs()
})

// SEO
useSeoMeta({
  title: '開放事求人 - 公務人員職缺查詢',
  description: '查詢最新公務人員職缺，提供機關、職稱、職系、地點等多種篩選條件。',
  ogTitle: '開放事求人 - 公務人員職缺查詢',
  ogDescription: '查詢最新公務人員職缺，提供機關、職稱、職系、地點等多種篩選條件。',
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
        <span class="text-slate-600 font-medium">總職缺</span>
        <span class="text-primary-600 font-bold text-2xl font-mono">{{ pagination.total_count }}</span>
        <span class="text-slate-400 text-sm">筆</span>
      </div>
    </div>

    <!-- Search Section -->
    <CollapsibleSearchPanel 
      title="搜尋職缺" 
      v-model="isSearchExpanded" 
      :hasActiveFilters="hasActiveFilters"
    >
      <template #icon>
        <MagnifyingGlassIcon class="w-5 h-5" />
      </template>

      <template #summary>
        <span v-if="filters.org" class="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full">機關: {{ filters.org }}</span>
        <span v-if="filters.title" class="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full">職稱: {{ filters.title }}</span>
        <span v-if="filters.sysnam" class="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full">職系: {{ filters.sysnam }}</span>
        <span v-if="filters.places" class="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full">地點: {{ filters.places }}</span>
        <span v-if="filters.min_rank || filters.max_rank" class="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full">職等: {{ filters.min_rank || 1 }}~{{ filters.max_rank || 14 }}</span>
        <span v-if="filters.include_history" class="text-xs bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full">含歷史</span>
        <span v-if="filters.include_parttime" class="text-xs bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full">含非正式</span>
      </template>

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
    </CollapsibleSearchPanel>

    <!-- Results Section -->
    <section>
      <!-- Loading State -->
      <div v-if="loading" class="flex flex-col items-center justify-center py-32 text-slate-400">
        <div class="relative">
          <div class="w-16 h-16 border-4 border-slate-100 border-t-primary-500 rounded-full animate-spin"></div>
          <div class="absolute inset-0 flex items-center justify-center">
            <div class="w-8 h-8 bg-white rounded-full"></div>
          </div>
        </div>
        <p class="mt-4 font-medium text-slate-500 animate-pulse">正在載入職缺資料...</p>
      </div>
      
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
                  <th class="p-4 cursor-pointer hover:bg-primary-700 transition-colors group w-[150px]" @click="handleSort('title')">
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
                  <th class="p-4 cursor-pointer hover:bg-primary-700 transition-colors group w-[170px]" @click="handleSort('date_from')">
                    <div class="flex items-center gap-1">
                      期間
                      <component :is="sortField === 'date_from' ? (sortOrder === 'asc' ? ArrowUpIcon : ArrowDownIcon) : ArrowsUpDownIcon" class="w-4 h-4 text-blue-200 group-hover:text-white" />
                    </div>
                  </th>
                  <th class="p-4 text-center w-[100px]">狀態</th>
                  <th class="p-4 text-center w-[70px]">查看</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100 text-sm">
                <tr v-for="job in jobs" :key="job.id" class="hover:bg-blue-50/50 transition-colors duration-200 border-b border-slate-50 last:border-0 group">
                  <td class="p-4 align-top">
                    <div class="font-bold text-slate-700 text-base mb-0.5 truncate max-w-[180px]" :title="job.org">{{ job.org }}</div>
                  </td>
                  <td class="p-4 align-top">
                    <NuxtLink :to="`/job/${job.id}`" class="block font-bold text-slate-900 text-base hover:text-primary-600 hover:underline truncate max-w-[200px]" :title="job.title">
                      {{ job.title }}
                    </NuxtLink>
                  </td>
                  <td class="p-4 align-top">
                    <div class="flex flex-col gap-1.5 items-start">
                      <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-bold bg-blue-50 text-blue-700 border border-blue-100 whitespace-nowrap">
                        {{ job.sysnam }}
                      </span>
                    </div>
                  </td>
                  <td class="p-4 align-top">
                    <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-bold bg-slate-100 text-slate-600 border border-slate-200 whitespace-nowrap">
                      {{ job.rank_display || job.rank }}
                    </span>
                  </td>
                  <td class="p-4 align-top">
                    <div class="flex items-center gap-1.5 text-slate-700 text-base font-bold max-w-[120px]" :title="job.place">
                      <MapPinIcon class="w-4 h-4 text-slate-400 flex-shrink-0" />
                      <span class="truncate">{{ job.place }}</span>
                    </div>
                  </td>
                  <td class="p-4 align-top">
                    <div class="flex flex-col">
                      <span class="text-xs font-mono text-slate-700 font-bold leading-tight">{{ job.date_from }}</span>
                      <span class="text-xs font-mono text-slate-500 leading-tight mt-1">~ {{ job.date_to }}</span>
                    </div>
                  </td>
                  <td class="p-4 align-top text-center">
                    <div class="flex justify-center gap-1">
                      <div v-show="job.comment_count > 0" class="group/icon relative">
                        <ChatBubbleLeftIcon class="w-5 h-5 text-emerald-500" />
                        <span class="absolute -top-1 -right-1 flex h-2.5 w-2.5">
                          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                          <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
                        </span>
                      </div>
                      <div v-show="job.history_count > 0" title="曾開缺">
                         <ArrowPathIcon class="w-5 h-5 text-amber-500" />
                      </div>
                      <span v-if="!job.comment_count && !job.history_count" class="text-slate-200 text-xl leading-none">&middot;</span>
                    </div>
                  </td>
                  <td class="p-4 align-top text-right">
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
        <div class="flex flex-col sm:flex-row justify-center items-center gap-4 mt-8" v-if="pagination.total_pages > 1">
          <!-- Page Controls -->
          <div class="flex items-center gap-2">
            <button 
              type="button"
              :disabled="pagination.current_page === 1" 
              @click="changePage(pagination.current_page - 1)"
              class="p-2 rounded-lg border border-slate-200 hover:bg-white hover:border-primary-300 hover:text-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all bg-white"
            >
              <ChevronLeftIcon class="w-5 h-5" />
            </button>
            
            <span class="text-sm font-medium text-slate-600 bg-white px-4 py-2 rounded-lg border border-slate-200 shadow-sm whitespace-nowrap">
              第 {{ pagination.current_page }} 頁 / 共 {{ pagination.total_pages }} 頁
            </span>
            
            <button 
              type="button"
              :disabled="pagination.current_page === pagination.total_pages" 
              @click="changePage(pagination.current_page + 1)"
              class="p-2 rounded-lg border border-slate-200 hover:bg-white hover:border-primary-300 hover:text-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all bg-white"
            >
              <ChevronRightIcon class="w-5 h-5" />
            </button>
          </div>

          <!-- Settings -->
          <div class="flex items-center gap-4">
            <div class="flex items-center gap-2">
              <span class="text-sm text-slate-500">每頁顯示</span>
              <select 
                v-model="perPage" 
                @change="handlePerPageChange"
                class="bg-white border border-slate-200 text-slate-700 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block p-2 outline-none"
              >
                <option :value="15">15</option>
                <option :value="30">30</option>
                <option :value="50">50</option>
                <option :value="100">100</option>
              </select>
              <span class="text-sm text-slate-500">筆</span>
            </div>

            <div class="flex items-center gap-2">
              <span class="text-sm text-slate-500">跳至</span>
              <input 
                v-model="jumpPage" 
                type="number" 
                min="1" 
                :max="pagination.total_pages"
                class="w-16 bg-white border border-slate-200 text-slate-700 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block p-2 outline-none text-center"
                @keyup.enter="handleJumpPage"
              >
              <span class="text-sm text-slate-500">頁</span>
              <button 
                type="button"
                @click="handleJumpPage"
                class="px-3 py-2 text-sm font-medium text-primary-600 bg-primary-50 rounded-lg hover:bg-primary-100 transition-colors"
              >
                GO
              </button>
            </div>
          </div>
        </div>
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
