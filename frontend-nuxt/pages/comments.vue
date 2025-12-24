<script setup>
import { 
  ChatBubbleLeftRightIcon, 
  FunnelIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  MagnifyingGlassIcon,
  XMarkIcon,
  TrashIcon,
  ClockIcon,
  CalendarIcon
} from '@heroicons/vue/24/outline'

const route = useRoute()
const router = useRouter()
const { addToast } = useToast()

const comments = ref([])
const loading = ref(true)
const error = ref(null)

// Filter Options
const sysnamAdminList = ref([])
const sysnamTechList = ref([])

// State
const pagination = ref({
  current_page: 1,
  total_pages: 1,
  total_count: 0,
  per_page: 10
})

const filters = ref({
  search_org: '',
  search_title: '',
  search_sysnam: '',
  search_message: '',
  show_deleted: false
})

// Search Bar State
const isSearchExpanded = ref(false)
const hasActiveFilters = computed(() => {
  return filters.value.search_org || 
         filters.value.search_title || 
         filters.value.search_sysnam || 
         filters.value.search_message || 
         filters.value.show_deleted
})

// Helper to build query params
const buildParams = () => {
  const params = {
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
  if (query.page) pagination.value.current_page = parseInt(query.page)
  if (query.search_org) filters.value.search_org = query.search_org
  if (query.search_title) filters.value.search_title = query.search_title
  if (query.search_sysnam) filters.value.search_sysnam = query.search_sysnam
  if (query.search_message) filters.value.search_message = query.search_message
  if (query.show_deleted) filters.value.show_deleted = query.show_deleted === 'true'
}

initFromUrl()

const { data: initialData, error: initialError } = await useFetch('/api/comments/list', {
  query: buildParams()
})

if (initialData.value) {
  comments.value = initialData.value.comments
  pagination.value = {
    current_page: initialData.value.current_page,
    total_pages: initialData.value.total_pages,
    total_count: initialData.value.total_count,
    per_page: initialData.value.per_page
  }
  sysnamAdminList.value = initialData.value.sysnam_admin_list
  sysnamTechList.value = initialData.value.sysnam_tech_list
  loading.value = false
} else if (initialError.value) {
  error.value = '無法載入留言資料，請稍後再試'
  loading.value = false
}

// Client-side Fetch
const fetchComments = async (isSearch = false) => {
  loading.value = true
  error.value = null
  try {
    const params = buildParams()
    const response = await $fetch('/api/comments/list', { params })
    
    comments.value = response.comments
    pagination.value = {
      current_page: response.current_page,
      total_pages: response.total_pages,
      total_count: response.total_count,
      per_page: response.per_page
    }
    sysnamAdminList.value = response.sysnam_admin_list
    sysnamTechList.value = response.sysnam_tech_list
    
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

const handleSearch = () => {
  pagination.value.current_page = 1
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
  updateUrl()
  fetchComments()
  addToast('已清空所有搜尋條件', 'info')
}

const changePage = (page) => {
  if (page < 1 || page > pagination.value.total_pages) return
  pagination.value.current_page = page
  updateUrl()
  fetchComments()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

watch(() => route.query, (newQuery, oldQuery) => {
  if (JSON.stringify(newQuery) === JSON.stringify(oldQuery)) return
  initFromUrl()
  fetchComments()
})

// SEO
useSeoMeta({
  title: '看留言 - 開放事求人',
  description: '瀏覽所有公務人員職缺的留言討論，分享職場心得與情報。',
  ogTitle: '看留言 - 開放事求人',
  ogDescription: '瀏覽所有公務人員職缺的留言討論，分享職場心得與情報。',
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

    <!-- Filters -->
    <CollapsibleSearchPanel 
      title="篩選條件" 
      v-model="isSearchExpanded" 
      :hasActiveFilters="hasActiveFilters"
    >
      <template #icon>
        <FunnelIcon class="w-5 h-5" />
      </template>

      <template #summary>
        <span v-if="filters.search_org" class="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full">機關: {{ filters.search_org }}</span>
        <span v-if="filters.search_title" class="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full">職稱: {{ filters.search_title }}</span>
        <span v-if="filters.search_sysnam" class="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full">職系: {{ filters.search_sysnam }}</span>
        <span v-if="filters.search_message" class="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full">留言: {{ filters.search_message }}</span>
        <span v-if="filters.show_deleted" class="text-xs bg-red-50 text-red-600 px-2 py-0.5 rounded-full">含刪除</span>
      </template>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
        <!-- Org -->
        <div>
          <label class="block text-base font-medium text-slate-700 mb-1">機關名稱</label>
          <input 
            v-model="filters.search_org" 
            type="text" 
            placeholder="搜尋機關..." 
            class="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary-100 focus:border-primary-500 outline-none text-base"
            @keyup.enter="handleSearch"
          >
        </div>

        <!-- Title -->
        <div>
          <label class="block text-base font-medium text-slate-700 mb-1">職稱</label>
          <input 
            v-model="filters.search_title" 
            type="text" 
            placeholder="搜尋職稱..." 
            class="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary-100 focus:border-primary-500 outline-none text-base"
            @keyup.enter="handleSearch"
          >
        </div>

        <!-- Sysnam -->
        <div>
          <label class="block text-base font-medium text-slate-700 mb-1">職系</label>
          <select 
            v-model="filters.search_sysnam" 
            class="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary-100 focus:border-primary-500 outline-none text-base"
            @change="handleSearch"
          >
            <option value="">全部職系</option>
            <optgroup label="行政類">
              <option v-for="sys in sysnamAdminList" :key="sys" :value="sys">{{ sys }}</option>
            </optgroup>
            <optgroup label="技術類">
              <option v-for="sys in sysnamTechList" :key="sys" :value="sys">{{ sys }}</option>
            </optgroup>
          </select>
        </div>

        <!-- Message -->
        <div>
          <label class="block text-base font-medium text-slate-700 mb-1">留言內容</label>
          <input 
            v-model="filters.search_message" 
            type="text" 
            placeholder="搜尋留言..." 
            class="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary-100 focus:border-primary-500 outline-none text-base"
            @keyup.enter="handleSearch"
          >
        </div>
      </div>

      <div class="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-slate-100">
        <label class="flex items-center gap-2 cursor-pointer group w-full sm:w-auto">
          <div class="relative inline-flex items-center">
            <input type="checkbox" v-model="filters.show_deleted" class="sr-only peer">
            <div class="w-11 h-6 bg-slate-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-100 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
          </div>
          <span class="text-sm font-medium text-slate-700 group-hover:text-slate-900">顯示已刪除留言</span>
        </label>

        <div class="flex items-center gap-3 w-full sm:w-auto">
          <button 
            @click="clearFilters" 
            class="flex-1 sm:flex-none flex items-center justify-center gap-2 px-4 py-2 bg-white border border-slate-200 text-slate-600 rounded-lg hover:bg-slate-50 transition-colors text-sm font-medium"
          >
            <XMarkIcon class="w-4 h-4" />
            清空
          </button>
          <button 
            @click="handleSearch" 
            class="flex-1 sm:flex-none flex items-center justify-center gap-2 px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium shadow-sm"
          >
            <MagnifyingGlassIcon class="w-4 h-4" />
            搜尋
          </button>
        </div>
      </div>
    </CollapsibleSearchPanel>

    <!-- Loading State -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-20 text-slate-400">
      <div class="w-10 h-10 border-4 border-slate-200 border-l-primary-500 rounded-full animate-spin mb-4"></div>
      <p class="font-medium">正在載入留言...</p>
    </div>

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
          class="group bg-white rounded-xl shadow-sm border border-slate-200 hover:border-primary-300 hover:shadow-md transition-all cursor-pointer block"
        >
          <!-- Blue Header Section - Org Name -->
          <div class="bg-primary-600 px-5 py-5 flex items-center justify-between gap-3 rounded-t-xl">
            <div class="flex items-center gap-2.5 min-w-0 flex-1">
              <span class="text-2xl font-bold text-white truncate">{{ comment.org_name }}</span>
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
                <span class="text-slate-800 text-lg font-mono">{{ comment.date_from }} ~ {{ comment.date_to }}</span>
              </div>
              
              <!-- 職系 -->
              <div class="flex items-start">
                <span class="w-24 flex-shrink-0 text-slate-500 text-lg">職系</span>
                <span class="text-slate-800 text-lg font-medium">{{ comment.sysnam }}</span>
              </div>
              
              <!-- 職稱 -->
              <div class="flex items-start">
                <span class="w-24 flex-shrink-0 text-slate-500 text-lg">職稱</span>
                <span class="text-slate-800 text-lg font-medium">{{ comment.title }}</span>
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
      <div class="flex items-center justify-center gap-4 mt-8" v-if="pagination.total_pages > 1">
        <button 
          @click="changePage(pagination.current_page - 1)"
          :disabled="pagination.current_page === 1"
          class="p-2 rounded-lg border border-slate-200 hover:bg-white hover:border-primary-300 hover:text-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all bg-white"
        >
          <ChevronLeftIcon class="w-5 h-5" />
        </button>
        
        <span class="text-sm font-medium text-slate-600 bg-white px-4 py-2 rounded-lg border border-slate-200 shadow-sm">
          第 {{ pagination.current_page }} 頁 / 共 {{ pagination.total_pages }} 頁
        </span>
        
        <button 
          @click="changePage(pagination.current_page + 1)"
          :disabled="pagination.current_page === pagination.total_pages"
          class="p-2 rounded-lg border border-slate-200 hover:bg-white hover:border-primary-300 hover:text-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all bg-white"
        >
          <ChevronRightIcon class="w-5 h-5" />
        </button>
      </div>
    </div>
  </div>
</template>
