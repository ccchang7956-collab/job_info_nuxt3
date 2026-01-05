<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeftIcon } from '@heroicons/vue/24/outline'
import type { JobDetailResponse } from '@/types'

const route = useRoute()
const router = useRouter()

const jobId = route.params.id as string

// SSR Data Fetching（禁用快取）
const { data, error: fetchError, refresh } = await useFetch<JobDetailResponse>(`/api/Active_job_openings/${jobId}`, {
  cache: 'no-store'
})

const job = computed(() => data.value?.job)
const comments = computed(() => data.value?.comments || [])
const duplicates = computed(() => data.value?.duplicates || [])

// Error Handling
const error = ref<string | null>(null)
if (fetchError.value) {
  const err = fetchError.value
  if (err.statusCode) {
    error.value = `無法取得職缺詳細資料 (${err.statusCode}): ${err.statusMessage || err.message}`
  } else {
    error.value = `無法取得職缺詳細資料: ${err.message}`
  }
}

// 客戶端導航時清除快取並重新載入
onMounted(async () => {
  if (import.meta.client) {
    clearNuxtData()
    await refresh()
  }
})

// SEO
useSeoMeta({
  title: () => job.value ? `${job.value.title} - ${job.value.org_name} - 開放事求人` : '職缺詳細資料 - 開放事求人',
  description: () => job.value ? `${job.value.org_name} ${job.value.title} 職缺詳情。工作地點：${job.value.work_place_type}。` : '公務人員職缺詳細資訊',
  ogTitle: () => job.value ? `${job.value.title} - ${job.value.org_name}` : '職缺詳細資料',
  ogDescription: () => job.value ? `${job.value.org_name} ${job.value.title} 職缺詳情。` : '公務人員職缺詳細資訊',
})

// Refresh function for comments - 留言成功後呼叫
const refreshJobDetails = async () => {
  clearNuxtData()
  await refresh()
}
</script>

<template>
  <div class="container mx-auto px-4 py-8 max-w-5xl">
    <!-- Loading State -->
    <LoadingSpinner v-if="!job && !error" message="正在載入職缺詳細資料..." />
    
    <div v-else-if="error" class="bg-red-50 border border-red-100 text-red-600 p-8 rounded-xl text-center">
      <p class="mb-4 text-lg font-medium">{{ error }}</p>
      <button 
        @click="router.back()" 
        class="inline-flex items-center gap-2 px-4 py-2 bg-white border border-red-200 text-red-600 rounded-lg hover:bg-red-50 transition-colors"
      >
        <ArrowLeftIcon class="w-4 h-4" />
        返回列表
      </button>
    </div>

    <div v-else-if="job">
      <JobInfoCard :job="job" :duplicates="duplicates">
        <template #header-actions>
          <button 
            @click="router.back()" 
            class="inline-flex items-center gap-1.5 text-slate-500 hover:text-primary-600 transition-colors text-sm font-medium mb-6 group"
          >
            <ArrowLeftIcon class="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
            返回列表
          </button>
        </template>
      </JobInfoCard>

      <!-- Comment Section -->
      <CommentSection 
        :comments="comments" 
        :job-id="job.id" 
        @refresh="refreshJobDetails" 
      />
    </div>
  </div>
</template>
