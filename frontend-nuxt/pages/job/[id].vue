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
  title: () => job.value 
    ? `開放事求人｜${job.value.org_name}(${job.value.title})｜職缺詳情 - 人事行政總處事求人開放資料` 
    : '職缺詳細資料 - 開放事求人',
  description: () => job.value 
    ? `${job.value.org_name}(${job.value.title}) - ${job.value.sysnam}(${job.value.rank})，地點：${job.value.work_address || job.value.work_place_type}。資料來源：行政院人事行政總處事求人開放資料。`
    : '公務人員職缺詳細資訊',
  keywords: () => job.value 
    ? `事求人, 人事行政總處事求人, 公務員職缺, 政府職缺, ${job.value.org_name}, ${job.value.title}, ${job.value.sysnam}, 開放事求人`
    : '事求人, 公務員職缺, 政府職缺',
  robots: 'index,follow',
  ogTitle: () => job.value 
    ? `開放事求人｜${job.value.org_name}(${job.value.title})｜職缺詳情`
    : '職缺詳細資料',
  ogDescription: () => job.value 
    ? `${job.value.org_name}(${job.value.title}) - ${job.value.sysnam}(${job.value.rank})，地點：${job.value.work_address || job.value.work_place_type}。`
    : '公務人員職缺詳細資訊',
  ogUrl: `https://opendgpa.shibaalin.com/job/${jobId}`,
  ogType: 'article',
})

// Canonical URL + Schema.org Structured Data (JobPosting + BreadcrumbList)
useHead(() => {
  const baseHead = {
    link: [
      { rel: 'canonical', href: `https://opendgpa.shibaalin.com/job/${jobId}` }
    ]
  }
  
  if (!job.value) return baseHead

  const convertRocDate = (dateStr: string) => {
    if (!dateStr) return ''
    const parts = dateStr.split('/')
    if (parts.length !== 3) return dateStr
    const year = parseInt(parts[0]) + 1911
    return `${year}-${parts[1]}-${parts[2]}`
  }

  // JobPosting Schema
  const jobPostingSchema = {
    '@context': 'https://schema.org',
    '@type': 'JobPosting',
    'title': `${job.value.org_name}(${job.value.title})`,
    'description': `${job.value.org_name}(${job.value.title}) - ${job.value.sysnam}(${job.value.rank})，地點：${job.value.work_address || job.value.work_place_type}。資料來源：行政院人事行政總處事求人開放資料。`,
    'identifier': {
      '@type': 'PropertyValue',
      'name': '開放事求人',
      'value': String(job.value.id)
    },
    'datePosted': convertRocDate(job.value.date_from),
    'validThrough': convertRocDate(job.value.date_to),
    'employmentType': 'FULL_TIME',
    'hiringOrganization': {
      '@type': 'Organization',
      'name': job.value.org_name || job.value.org,
      'sameAs': 'https://web3.dgpa.gov.tw/want03front/AP/WANTF00001.ASPX'
    },
    'jobLocation': {
      '@type': 'Place',
      'address': {
        '@type': 'PostalAddress',
        'addressLocality': job.value.work_place_type,
        'streetAddress': job.value.work_address || job.value.work_place_type,
        'addressRegion': '台灣'
      }
    }
  }

  // BreadcrumbList Schema - 讓 Google 顯示階層導航
  const breadcrumbSchema = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    'itemListElement': [
      {
        '@type': 'ListItem',
        'position': 1,
        'name': '首頁',
        'item': 'https://opendgpa.shibaalin.com/'
      },
      {
        '@type': 'ListItem',
        'position': 2,
        'name': '職缺列表',
        'item': 'https://opendgpa.shibaalin.com/'
      },
      {
        '@type': 'ListItem',
        'position': 3,
        'name': `${job.value.org_name}(${job.value.title})`,
        'item': `https://opendgpa.shibaalin.com/job/${jobId}`
      }
    ]
  }

  return {
    ...baseHead,
    script: [
      {
        type: 'application/ld+json',
        innerHTML: JSON.stringify(jobPostingSchema)
      },
      {
        type: 'application/ld+json',
        innerHTML: JSON.stringify(breadcrumbSchema)
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
