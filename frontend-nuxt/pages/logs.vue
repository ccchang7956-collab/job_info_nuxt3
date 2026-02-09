<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  ClipboardDocumentListIcon, 
  FunnelIcon,
  ChevronLeftIcon,
  ChevronRightIcon
} from '@heroicons/vue/24/outline'
import type { Log, LogListResponse } from '@/types'

const route = useRoute()
const router = useRouter()

const logs = ref<Log[]>([])
const actions = ref<string[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

// Pagination & Filter state
const currentPage = ref(parseInt(route.query.page as string) || 1)
const selectedAction = ref((route.query.action as string) || '')
const totalPages = ref(0)
const totalCount = ref(0)
const pageRange = ref<number[]>([])

// 標記：用於避免請求競爭
const skipNextWatch = ref(false)

// Helper to build query params
const buildParams = () => {
  return {
    page: currentPage.value,
    action: selectedAction.value || undefined
  }
}

const updateUrl = () => {
  const query: Record<string, any> = { page: currentPage.value }
  if (selectedAction.value) {
    query.action = selectedAction.value
  }
  router.push({ query })
}

// Initial Data Fetch (SSR)
const { data: initialData, error: initialError } = await useFetch<LogListResponse>('/api/logs', {
  query: buildParams()
})

if (initialData.value) {
  logs.value = initialData.value.logs
  actions.value = initialData.value.actions
  totalPages.value = initialData.value.total_pages
  totalCount.value = initialData.value.total_count
  pageRange.value = initialData.value.page_range
  loading.value = false
} else if (initialError.value) {
  error.value = '無法載入日誌資料，請稍後再試'
  loading.value = false
}

// Client-side Fetch
const { fetchLogs: apiFetchLogs } = useJobApi()

const fetchLogs = async () => {
  loading.value = true
  error.value = null
  try {
    const params = buildParams()
    const response = await apiFetchLogs(params)
    logs.value = response.logs
    actions.value = response.actions
    totalPages.value = response.total_pages
    totalCount.value = response.total_count
    pageRange.value = response.page_range
  } catch (err) {
    console.error('Error fetching logs:', err)
    error.value = '無法載入日誌資料，請稍後再試'
  } finally {
    loading.value = false
  }
}

const changePage = (page: number) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  // 設定標記避免請求競爭
  skipNextWatch.value = true
  updateUrl()
  fetchLogs()
}

const handleFilterChange = () => {
  currentPage.value = 1
  // 設定標記避免請求競爭
  skipNextWatch.value = true
  updateUrl()
  fetchLogs()
}

// Watch for URL changes (e.g. back button)
watch(() => route.query, (newQuery, oldQuery) => {
  // 如果 query 沒有變化，不做任何事
  if (JSON.stringify(newQuery) === JSON.stringify(oldQuery)) return
  
  // 如果是由 changePage/handleFilterChange 觸發的 URL 更新，跳過這次 watch
  if (skipNextWatch.value) {
    skipNextWatch.value = false
    return
  }
  
  const newPage = parseInt(newQuery.page as string) || 1
  const newAction = (newQuery.action as string) || ''
  
  currentPage.value = newPage
  selectedAction.value = newAction
  fetchLogs()
})

// SEO
useSeoMeta({
  title: '更新日誌 - 開放事求人｜資料更新紀錄',
  description: '查看開放事求人網站的資料更新紀錄，追蹤人事行政總處事求人開放資料同步狀態。',
  keywords: '事求人, 更新日誌, 資料更新, 開放事求人',
  robots: 'index,follow',
  ogTitle: '更新日誌 - 開放事求人',
  ogDescription: '查看開放事求人網站的資料更新紀錄。',
  ogUrl: 'https://opendgpa.shibaalin.com/logs',
  ogType: 'website',
})

// Canonical URL
useHead({
  link: [
    { rel: 'canonical', href: 'https://opendgpa.shibaalin.com/logs' }
  ]
})
</script>

<template>
  <div class="container mx-auto px-4 py-8 max-w-5xl">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
      <h1 class="text-2xl font-bold text-slate-800 flex items-center gap-2">
        <ClipboardDocumentListIcon class="w-8 h-8 text-primary-600" />
        更新日誌
      </h1>
      
      <!-- Filter -->
      <div class="flex items-center gap-2">
        <FunnelIcon class="w-5 h-5 text-slate-400" />
        <select 
          v-model="selectedAction" 
          @change="handleFilterChange"
          class="bg-white border border-slate-200 text-slate-700 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 min-w-[200px]"
        >
          <option value="">全部動作</option>
          <option v-for="action in actions" :key="action" :value="action">
            {{ action }}
          </option>
        </select>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-20 text-slate-400">
      <div class="w-10 h-10 border-4 border-slate-200 border-l-primary-500 rounded-full animate-spin mb-4"></div>
      <p class="font-medium">正在載入日誌...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border border-red-100 text-red-600 p-8 rounded-xl text-center">
      <p class="font-medium">{{ error }}</p>
      <button @click="fetchLogs" class="mt-4 text-sm underline hover:text-red-700">重試</button>
    </div>

    <!-- Data Table -->
    <div v-else class="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm text-left text-slate-600">
          <thead class="text-xs text-slate-700 uppercase bg-slate-50 border-b border-slate-200">
            <tr>
              <th scope="col" class="px-6 py-3 whitespace-nowrap">ID</th>
              <th scope="col" class="px-6 py-3 whitespace-nowrap">動作</th>
              <th scope="col" class="px-6 py-3 whitespace-nowrap">開始時間</th>
              <th scope="col" class="px-6 py-3 whitespace-nowrap">結束時間</th>
              <th scope="col" class="px-6 py-3 whitespace-nowrap text-right">新增筆數</th>
              <th scope="col" class="px-6 py-3 whitespace-nowrap text-right">更新筆數</th>
              <th scope="col" class="px-6 py-3 whitespace-nowrap">狀態</th>
              <th scope="col" class="px-6 py-3 min-w-[200px]">備註</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in logs" :key="log.id" class="bg-white border-b hover:bg-slate-50 transition-colors">
              <td class="px-6 py-4 font-mono text-xs">{{ log.id }}</td>
              <td class="px-6 py-4 font-medium text-slate-900">{{ log.action }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ log.start_time }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ log.end_time }}</td>
              <td class="px-6 py-4 text-right font-mono">{{ log.new_records }}</td>
              <td class="px-6 py-4 text-right font-mono">{{ log.updated_records }}</td>
              <td class="px-6 py-4">
                <span 
                  class="px-2.5 py-0.5 rounded-full text-xs font-medium border"
                  :class="{
                    'bg-emerald-50 text-emerald-700 border-emerald-100': log.status === '成功',
                    'bg-red-50 text-red-700 border-red-100': log.status !== '成功'
                  }"
                >
                  {{ log.status }}
                </span>
              </td>
              <td class="px-6 py-4 text-xs text-slate-500 break-words max-w-xs">{{ log.remarks }}</td>
            </tr>
            <tr v-if="logs.length === 0">
              <td colspan="8" class="px-6 py-12 text-center text-slate-400">
                無符合條件的日誌資料
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="flex items-center justify-between border-t border-slate-200 bg-white px-4 py-3 sm:px-6">
        <div class="hidden sm:flex flex-1 justify-between sm:hidden">
          <button 
            @click="changePage(currentPage - 1)" 
            :disabled="currentPage === 1"
            class="relative inline-flex items-center rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            上一頁
          </button>
          <button 
            @click="changePage(currentPage + 1)" 
            :disabled="currentPage === totalPages"
            class="relative ml-3 inline-flex items-center rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            下一頁
          </button>
        </div>
        <div class="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
          <div>
            <p class="text-sm text-slate-700">
              顯示第 <span class="font-medium">{{ (currentPage - 1) * 20 + 1 }}</span> 到 <span class="font-medium">{{ Math.min(currentPage * 20, totalCount) }}</span> 筆，共 <span class="font-medium">{{ totalCount }}</span> 筆
            </p>
          </div>
          <div>
            <nav class="isolate inline-flex -space-x-px rounded-md shadow-sm" aria-label="Pagination">
              <button 
                @click="changePage(currentPage - 1)"
                :disabled="currentPage === 1"
                class="relative inline-flex items-center rounded-l-md px-2 py-2 text-slate-400 ring-1 ring-inset ring-slate-300 hover:bg-slate-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span class="sr-only">Previous</span>
                <ChevronLeftIcon class="h-5 w-5" aria-hidden="true" />
              </button>
              
              <button 
                v-for="page in pageRange" 
                :key="page"
                @click="changePage(page)"
                :class="[
                  page === currentPage ? 'z-10 bg-primary-600 text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600' : 'text-slate-900 ring-1 ring-inset ring-slate-300 hover:bg-slate-50 focus:outline-offset-0',
                  'relative inline-flex items-center px-4 py-2 text-sm font-semibold focus:z-20'
                ]"
              >
                {{ page }}
              </button>
              
              <button 
                @click="changePage(currentPage + 1)"
                :disabled="currentPage === totalPages"
                class="relative inline-flex items-center rounded-r-md px-2 py-2 text-slate-400 ring-1 ring-inset ring-slate-300 hover:bg-slate-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span class="sr-only">Next</span>
                <ChevronRightIcon class="h-5 w-5" aria-hidden="true" />
              </button>
            </nav>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
