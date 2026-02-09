<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  ChatBubbleLeftRightIcon, 
  FunnelIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  ChevronDownIcon,
  MagnifyingGlassIcon,
  XMarkIcon,
  TrashIcon,
  ClockIcon,
  Bars3Icon,
  AdjustmentsHorizontalIcon
} from '@heroicons/vue/24/outline'
import type { Comment, CommentListResponse } from '@/types'

const route = useRoute()
const router = useRouter()
const { addToast } = useToast()

// Interfaces
interface PaginationState {
  current_page: number
  total_pages: number
  total_count: number
  per_page: number
}

interface FilterState {
  search_org: string
  search_title: string
  search_sysnam: string
  search_message: string
  show_deleted: boolean
}

// State
const comments = ref<Comment[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

const pagination = ref<PaginationState>({
  current_page: 1,
  total_pages: 1,
  total_count: 0,
  per_page: 10
})

const filters = ref<FilterState>({
  search_org: '',
  search_title: '',
  search_sysnam: '',
  search_message: '',
  show_deleted: false
})

// Search Bar State
const isSearchExpanded = ref(false)
const isSysnamModalOpen = ref(false)

// 標記：用於避免請求競爭
const skipNextWatch = ref(false)

// Trigger search when sysnam changes via modal
watch(() => filters.value.search_sysnam, () => {
  handleSearch()
})

const hasActiveFilters = computed(() => {
  return !!(filters.value.search_org || 
         filters.value.search_title || 
         filters.value.search_sysnam || 
         filters.value.search_message || 
         filters.value.show_deleted)
})

// Helper to build query params
const buildParams = () => {
  const params: Record<string, any> = {
    page: pagination.value.current_page,
    per_page: pagination.value.per_page,
    ...filters.value
  }
  // Filter out empty params
  Object.keys(params).forEach(key => {
    if (params[key] === '' || params[key] === null) {
      delete params[key]
    }
  })
  return params
}

const updateUrl = () => {
  const query = buildParams()
  router.push({ query })
}

// Initial Data Fetch (SSR)
const initFromUrl = () => {
  const query = route.query
  if (query.page) pagination.value.current_page = parseInt(query.page as string)
  if (query.search_org) filters.value.search_org = query.search_org as string
  if (query.search_title) filters.value.search_title = query.search_title as string
  if (query.search_sysnam) filters.value.search_sysnam = query.search_sysnam as string
  if (query.search_message) filters.value.search_message = query.search_message as string
  if (query.show_deleted) filters.value.show_deleted = query.show_deleted === 'true'
}

initFromUrl()

const { data: initialData, error: initialError } = await useFetch<CommentListResponse>('/api/comments/list', {
  query: buildParams(),
  // 完全禁用快取，確保每次都取得最新資料
  cache: 'no-store'
})

if (initialData.value) {
  comments.value = initialData.value.comments
  pagination.value = {
    current_page: initialData.value.current_page,
    total_pages: initialData.value.total_pages,
    total_count: initialData.value.total_count,
    per_page: initialData.value.per_page
  }

  loading.value = false
} else if (initialError.value) {
  error.value = '無法載入留言資料，請稍後再試'
  loading.value = false
}

// Client-side Fetch
const { fetchComments: apiFetchComments } = useJobApi()

const fetchComments = async (isSearch = false) => {
  loading.value = true
  error.value = null
  try {
    const params = buildParams()
    const response = await apiFetchComments(params)
    
    comments.value = response.comments
    pagination.value = {
      current_page: response.current_page,
      total_pages: response.total_pages,
      total_count: response.total_count,
      per_page: response.per_page
    }

    
    if (isSearch) {
      addToast(`搜尋完成，共找到 ${response.total_count} 筆留言`, 'success')
    }
  } catch (err) {
    console.error('Error fetching comments:', err)
    error.value = '無法載入留言資料，請稍後再試'
    addToast('無法載入留言資料', 'error')
  } finally {
    loading.value = false
  }
}

// 注意：cache: 'no-store' 已禁用瀏覽器快取
// 客戶端導航時 Nuxt 會自動重新執行 useFetch

const handleSearch = () => {
  pagination.value.current_page = 1
  // 設定標記，讓 watch 不要在 URL 更新後再次觸發搜尋
  skipNextWatch.value = true
  updateUrl()
  fetchComments(true)
}

const clearFilters = () => {
  filters.value = {
    search_org: '',
    search_title: '',
    search_sysnam: '',
    search_message: '',
    show_deleted: false
  }
  pagination.value.current_page = 1
  // 設定標記避免請求競爭
  skipNextWatch.value = true
  updateUrl()
  fetchComments()
  addToast('已清空所有搜尋條件', 'info')
}

const changePage = (page: number) => {
  if (page < 1 || page > pagination.value.total_pages) return
  pagination.value.current_page = page
  // 設定標記避免請求競爭
  skipNextWatch.value = true
  updateUrl()
  fetchComments()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

watch(() => route.query, (newQuery, oldQuery) => {
  if (JSON.stringify(newQuery) === JSON.stringify(oldQuery)) return
  // 如果是由 handleSearch/changePage 觸發的 URL 更新，跳過這次 watch
  if (skipNextWatch.value) {
    skipNextWatch.value = false
    return
  }
  initFromUrl()
  fetchComments()
})

// SEO
useSeoMeta({
  title: '職缺留言討論 - 開放事求人｜人事行政總處事求人',
  description: '瀏覽公務員職缺留言討論，分享職場心得與情報。人事行政總處事求人開放資料社群討論區。',
  keywords: '事求人, 職缺留言, 公務員心得, 人事行政總處事求人, 公務員討論, 開放事求人',
  robots: 'index,follow',
  ogTitle: '職缺留言討論 - 開放事求人｜人事行政總處事求人',
  ogDescription: '瀏覽公務員職缺留言討論，分享職場心得與情報。',
  ogUrl: 'https://opendgpa.shibaalin.com/comments',
  ogType: 'website',
})

// Canonical URL
useHead({
  link: [
    { rel: 'canonical', href: 'https://opendgpa.shibaalin.com/comments' }
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
            <ChatBubbleLeftRightIcon class="w-8 h-8 text-primary-600" />
          </div>
          看留言
        </h1>
        <p class="text-slate-500 text-lg">瀏覽所有職缺的留言討論</p>
      </div>
      <div class="inline-flex items-center gap-2 bg-white px-5 py-3 rounded-xl border border-slate-200 shadow-sm">
        <span class="text-slate-600 font-medium">總留言</span>
        <span class="text-emerald-600 font-bold text-2xl font-mono">{{ pagination.total_count }}</span>
        <span class="text-slate-400 text-sm">筆</span>
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
            v-model="filters.search_org"
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
        <span v-if="filters.search_org" class="text-xs bg-slate-100 text-slate-600 px-2 py-1 rounded-full flex items-center gap-1">
          機關: {{ filters.search_org }}
          <button @click="filters.search_org = ''; handleSearch()" class="hover:text-red-500"><XMarkIcon class="w-3 h-3" /></button>
        </span>
        <span v-if="filters.search_title" class="text-xs bg-slate-100 text-slate-600 px-2 py-1 rounded-full flex items-center gap-1">
          職稱: {{ filters.search_title }}
          <button @click="filters.search_title = ''; handleSearch()" class="hover:text-red-500"><XMarkIcon class="w-3 h-3" /></button>
        </span>
        <span v-if="filters.search_sysnam" class="text-xs bg-slate-100 text-slate-600 px-2 py-1 rounded-full flex items-center gap-1">
          職系: {{ filters.search_sysnam }}
          <button @click="filters.search_sysnam = ''; handleSearch()" class="hover:text-red-500"><XMarkIcon class="w-3 h-3" /></button>
        </span>
        <span v-if="filters.search_message" class="text-xs bg-slate-100 text-slate-600 px-2 py-1 rounded-full flex items-center gap-1">
          留言: {{ filters.search_message }}
          <button @click="filters.search_message = ''; handleSearch()" class="hover:text-red-500"><XMarkIcon class="w-3 h-3" /></button>
        </span>
        <span v-if="filters.show_deleted" class="text-xs bg-red-50 text-red-600 px-2 py-1 rounded-full flex items-center gap-1">
          含刪除
          <button @click="filters.show_deleted = false; handleSearch()" class="hover:text-red-500"><XMarkIcon class="w-3 h-3" /></button>
        </span>
      </div>

      <!-- Advanced Filters Panel -->
      <div v-show="isSearchExpanded" class="mt-4 p-5 bg-white border border-slate-200 rounded-xl shadow-sm">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
          <!-- Org -->
          <div class="space-y-1.5">
            <label class="text-base font-medium text-slate-700">機關名稱</label>
            <input 
              v-model="filters.search_org" 
              type="text" 
              placeholder="搜尋機關..." 
              class="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary-100 focus:border-primary-500 outline-none text-base"
              @keyup.enter="handleSearch"
            >
          </div>

          <!-- Title -->
          <div class="space-y-1.5">
            <label class="text-base font-medium text-slate-700">職稱</label>
            <input 
              v-model="filters.search_title" 
              type="text" 
              placeholder="搜尋職稱..." 
              class="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary-100 focus:border-primary-500 outline-none text-base"
              @keyup.enter="handleSearch"
            >
          </div>

          <!-- Sysnam -->
          <div class="space-y-1.5">
            <label class="text-base font-medium text-slate-700">職系</label>
            <div class="relative">
              <input 
                type="text" 
                readonly
                :value="filters.search_sysnam"
                placeholder="全部職系"
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

          <!-- Message -->
          <div class="space-y-1.5">
            <label class="text-base font-medium text-slate-700">留言內容</label>
            <input 
              v-model="filters.search_message" 
              type="text" 
              placeholder="搜尋留言..." 
              class="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary-100 focus:border-primary-500 outline-none text-base"
              @keyup.enter="handleSearch"
            >
          </div>
        </div>

        <!-- Toggles and Buttons Row -->
        <div class="flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-slate-100">
          <label class="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" v-model="filters.show_deleted" class="w-4 h-4 rounded border-slate-300 text-primary-600 focus:ring-primary-500">
            <span class="text-sm text-slate-700">顯示已刪除留言</span>
          </label>
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
              @click="handleSearch(); isSearchExpanded = false" 
              class="flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white px-6 py-2.5 rounded-lg font-medium transition-colors shadow-sm hover:shadow active:scale-95 transform duration-100"
            >
              <MagnifyingGlassIcon class="w-5 h-5" />
              搜尋
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <LoadingSpinner v-if="loading" message="正在載入留言..." />

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border border-red-100 text-red-600 p-8 rounded-xl text-center">
      <p class="font-medium">{{ error }}</p>
      <button @click="fetchComments(false)" class="mt-4 text-sm underline hover:text-red-700">重試</button>
    </div>

    <!-- Comments List -->
    <div v-else>
      <div v-if="comments.length === 0" class="text-center py-20 bg-slate-50 rounded-xl border border-dashed border-slate-200 text-slate-400">
        <ChatBubbleLeftRightIcon class="w-12 h-12 mx-auto mb-3 opacity-50" />
        <p class="text-lg font-medium">找不到符合條件的留言</p>
        <p class="text-sm mt-1">試著調整篩選條件看看</p>
      </div>

      <div v-else class="grid gap-6">
        <NuxtLink 
          v-for="comment in comments" 
          :key="comment.comment_id" 
          :to="`/job/${comment.job_all_data_id}`"
          class="group bg-white rounded-xl shadow-sm border border-slate-200 hover:border-primary-300 hover:shadow-md transition-all cursor-pointer block min-w-0"
        >
          <!-- Blue Header Section - Org Name -->
          <div class="bg-primary-600 px-5 py-5 flex items-center justify-between gap-3 rounded-t-xl">
            <div class="flex items-center gap-2.5 min-w-0 flex-1">
              <span class="text-2xl font-bold text-white break-words">{{ comment.org_name }}</span>
            </div>
            <svg class="w-8 h-8 text-blue-200 group-hover:text-white group-hover:translate-x-1 transition-all flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
            </svg>
          </div>
          
          <!-- Content Body - Table-like Layout -->
          <div class="p-5 flex flex-col gap-4">
            <!-- Info Rows -->
            <div class="space-y-3">
              <!-- 時間起迄 -->
              <div class="flex items-start">
                <span class="w-24 flex-shrink-0 text-slate-500 text-lg">時間起迄</span>
                <span class="text-slate-800 text-lg font-mono flex-1 min-w-0 break-words">{{ comment.date_from }} ~ {{ comment.date_to }}</span>
              </div>
              
              <!-- 職系 -->
              <div class="flex items-start">
                <span class="w-24 flex-shrink-0 text-slate-500 text-lg">職系</span>
                <span class="text-slate-800 text-lg font-medium flex-1 min-w-0 break-words">{{ comment.sysnam }}</span>
              </div>
              
              <!-- 職稱 -->
              <div class="flex items-start">
                <span class="w-24 flex-shrink-0 text-slate-500 text-lg">職稱</span>
                <span class="text-slate-800 text-lg font-medium flex-1 min-w-0 break-words">{{ comment.title }}</span>
              </div>
            </div>

            <!-- Comment Content -->
            <div class="pt-4 border-t border-slate-100">
              <div class="text-slate-500 text-lg mb-2">留言內容：</div>
              <div v-if="comment.is_deleted" class="bg-red-50 border border-red-100 rounded-lg p-4 mb-2">
                <div class="flex items-center gap-2 text-red-600 font-bold mb-1 text-sm">
                  <TrashIcon class="w-4 h-4" />
                  此留言已被刪除
                </div>
                <p class="text-red-700 text-sm" v-if="comment.deletion_reason">原因：{{ comment.deletion_reason }}</p>
              </div>
              
              <div class="text-slate-800 text-lg leading-relaxed whitespace-pre-wrap break-words" :class="{ 'opacity-50': comment.is_deleted }">
                {{ comment.message }}
              </div>
              
              <!-- Comment Time -->
              <div class="flex justify-end mt-3">
                <span class="inline-flex items-center gap-1.5 text-base text-slate-400">
                  <ClockIcon class="w-5 h-5 flex-shrink-0" />
                  <span class="font-mono">{{ comment.created_at }}</span>
                </span>
              </div>
            </div>
          </div>
        </NuxtLink>
      </div>

      <!-- Pagination -->
      <Pagination
        :currentPage="pagination.current_page"
        :totalPages="pagination.total_pages"
        :perPage="pagination.per_page"
        :showPerPage="false"
        :showJumpTo="false"
        @update:currentPage="changePage"
      />
    </div>
    <SysnamModal 
      v-model="filters.search_sysnam"
      :isOpen="isSysnamModalOpen"
      @close="isSysnamModalOpen = false" 
    />
  </div>
</template>
