<script setup lang="ts">
import { ref, computed } from 'vue'
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

// 客戶端導航時清除快取（僅當 SSR 資料可能過期時）
// 注意：cache: 'no-store' 會讓 useFetch 不使用瀏覽器快取
// 但 Nuxt 內部仍可能有快取，所以留言成功後需要手動 refresh

// SEO
useSeoMeta({
  title: () => job.value ? `${job.value.title} - ${job.value.org_name} - 開放事求人` : '職缺詳細資料 - 開放事求人',
  description: () => job.value ? `${job.value.org_name} ${job.value.title} 職缺詳情。工作地點：${job.value.work_place_type}。` : '公務人員職缺詳細資訊',
  ogTitle: () => job.value ? `${job.value.title} - ${job.value.org_name}` : '職缺詳細資料',
  ogDescription: () => job.value ? `${job.value.org_name} ${job.value.title} 職缺詳情。` : '公務人員職缺詳細資訊',
})

// Schema.org Structured Data
// Schema.org Structured Data
useHead(() => {
  if (!job.value) return {}

  const convertRocDate = (dateStr: string) => {
    if (!dateStr) return ''
    const parts = dateStr.split('/')
    if (parts.length !== 3) return dateStr
    const year = parseInt(parts[0]) + 1911
    return `${year}-${parts[1]}-${parts[2]}`
  }

  const schema = {
    '@context': 'https://schema.org',
    '@type': 'JobPosting',
    'title': job.value.title,
    'hiringOrganization': {
      '@type': 'Organization',
      'name': job.value.org_name || job.value.org,
      'logo': 'https://opendgpa.shibaalin.com/pwa-192x192.png'
    },
    'datePosted': convertRocDate(job.value.date_from),
    'validThrough': convertRocDate(job.value.date_to),
    'jobLocation': {
      '@type': 'Place',
      'address': {
        '@type': 'PostalAddress',
        'addressLocality': job.value.work_place_type,
        'streetAddress': job.value.work_address || job.value.work_place_type,
        'addressCountry': 'TW'
      }
    },
    'description': `
      <h3>工作項目</h3>
      <p>${job.value.work_item || '無'}</p>
      <h3>資格條件</h3>
      <p>${job.value.work_quality || '無'}</p>
      <p>機關：${job.value.org_name || job.value.org}</p>
      <p>職系：${job.value.sysnam}</p>
      <p>職等：${job.value.rank}</p>
    `,
    'employmentType': 'FULL_TIME',
    'identifier': {
      '@type': 'PropertyValue',
      'name': job.value.org_name || job.value.org,
      'value': job.value.id
    }
  }

  return {
    script: [
      {
        type: 'application/ld+json',
        innerHTML: JSON.stringify(schema)
      }
    ]
  }
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
