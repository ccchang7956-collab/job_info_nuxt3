<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeftIcon } from '@heroicons/vue/24/outline'
import type { JobDetailResponse } from '@/types'

const route = useRoute()
const router = useRouter()

const jobId = route.params.id as string
const siteUrl = useSiteUrl()
const jobUrl = `${siteUrl}/job/${jobId}`

// SSR Data Fetching
// 注意：不設 cache: 'no-store'，讓 nuxt.config 的 swr: 60 快取生效
// 加速 Googlebot 爬取（避免每次都等後端即時回應消耗爬取配額）
// 留言刷新時使用 refresh() 強制更新即可
const { data, error: fetchError, refresh } = await useFetch<JobDetailResponse>(`/api/Active_job_openings/${jobId}`)

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

// 留言提交成功後呼叫 refresh() 強制重取最新資料（包含新留言）

// SEO
useSeoMeta({
  title: () => job.value 
    ? `開放事求人｜${job.value.org_name}(${job.value.title})｜職缺詳情 - 人事行政總處事求人開放資料` 
    : '職缺詳細資料 - 開放事求人',
  description: () => {
    if (!job.value) return '公務人員職缺詳細資訊'
    const desc = `${job.value.org_name}(${job.value.title}) - ${job.value.sysnam}(${job.value.rank})，地點：${job.value.work_address || job.value.work_place_type}。資料來源：行政院人事行政總處事求人開放資料。`
    // 限制 description 長度 <= 80 個中文字（約 160 bytes），避免 Google 截斷
    return desc.length > 80 ? desc.slice(0, 77) + '...' : desc
  },
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
  ogUrl: jobUrl,
  ogType: 'article',
  // 文章更新時間 - 與對手同等規格
  articleModifiedTime: () => {
    if (!job.value?.date_from) return undefined
    const parts = job.value.date_from.split('/')
    if (parts.length !== 3) return undefined
    const year = parseInt(parts[0]) + 1911
    return `${year}-${parts[1]}-${parts[2]}`
  },
})

// Canonical URL + Schema.org Structured Data (JobPosting + BreadcrumbList)
useHead(() => {
  const baseHead = {
    link: [
      { rel: 'canonical', href: jobUrl }
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
    'url': jobUrl,
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
        'addressRegion': '台灣',
        'addressCountry': 'TW'
      }
    },
    // 地理限制 — 提升 Google Jobs 豐富摘要出現機率
    'applicantLocationRequirements': {
      '@type': 'Country',
      'name': 'TW'
    },
    'jobBenefits': '政府機關公務員職位，享有公務人員保障與福利',
    'industry': '政府機關',
    'occupationalCategory': job.value.sysnam || '公務人員'
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
        'item': `${siteUrl}/`
      },
      {
        '@type': 'ListItem',
        'position': 2,
        'name': '職缺列表',
        'item': `${siteUrl}/`
      },
      {
        '@type': 'ListItem',
        'position': 3,
        'name': `${job.value.org_name}(${job.value.title})`,
        'item': jobUrl
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

// 浮動返回按鈕 - 捲動超過 200px 後顯示
const showFloatingBack = ref(false)
const handleScroll = () => {
  showFloatingBack.value = window.scrollY > 200
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
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

    <article v-else-if="job">
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
    </article>

    <!-- 浮動返回按鈕（手機版，捲動後顯示）-->
    <Transition name="fade">
      <button
        v-if="showFloatingBack"
        @click="router.back()"
        class="md:hidden fixed bottom-6 left-4 z-50 flex items-center gap-2 px-4 py-3 bg-primary-600 text-white rounded-full shadow-lg hover:bg-primary-700 active:scale-95 transition-all"
      >
        <ArrowLeftIcon class="w-5 h-5" />
        <span class="text-sm font-medium">返回</span>
      </button>
    </Transition>
  </div>
</template>
