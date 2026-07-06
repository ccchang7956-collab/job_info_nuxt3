<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeftIcon, ExclamationTriangleIcon } from '@heroicons/vue/24/outline'
import type { JobDetailResponse } from '@/types'

const route = useRoute()
const router = useRouter()
const { isExpired } = useFormatDate()

const jobId = route.params.id as string
const siteUrl = useSiteUrl()
const jobUrl = `${siteUrl}/job/${jobId}`

// SSR Data Fetching
// 注意：不設 cache: 'no-store'，讓 nuxt.config 的 swr: 120 快取生效
// swr: 120 讓後端有足夠時間暖好快取，Googlebot 第一次抓取時能得到完整 HTML
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
    setResponseStatus(err.statusCode)
    error.value = `無法取得職缺詳細資料 (${err.statusCode}): ${err.statusMessage || err.message}`
  } else {
    error.value = `無法取得職缺詳細資料: ${err.message}`
  }
}

// 留言提交成功後呼叫 refresh() 強制重取最新資料（包含新留言）

const normalizeText = (value?: string | null) => String(value || '').replace(/\s+/g, ' ').trim()
const normalizeMultilineText = (value?: string | null) => String(value || '').replace(/\r\n/g, '\n').replace(/\n{3,}/g, '\n\n').trim()
const cleanValue = (value?: string | null) => normalizeText(value).replace(/^[,，\s-]+/, '')
const hasMeaningfulValue = (value?: string | null) => {
  const text = cleanValue(value)
  return !!text && text !== '無' && text !== '-'
}

const truncateText = (value: string, maxLength = 115) => (
  value.length > maxLength ? `${value.slice(0, maxLength - 3)}...` : value
)

const escapeHtml = (value: string) => value
  .replace(/&/g, '&amp;')
  .replace(/</g, '&lt;')
  .replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;')
  .replace(/'/g, '&#39;')

const toJsonLd = (value: Record<string, any>) => JSON.stringify(value).replace(/</g, '\\u003c')

const convertRocDate = (dateStr?: string | null) => {
  const normalized = String(dateStr || '').replace(/[/-]/g, '').trim()
  if (!normalized) return ''

  if (/^\d{7}$/.test(normalized)) {
    const year = parseInt(normalized.slice(0, 3), 10) + 1911
    return `${year}-${normalized.slice(3, 5)}-${normalized.slice(5, 7)}`
  }

  if (/^\d{8}$/.test(normalized)) {
    return `${normalized.slice(0, 4)}-${normalized.slice(4, 6)}-${normalized.slice(6, 8)}`
  }

  const parts = String(dateStr || '').split('/')
  if (parts.length === 3) {
    const year = parseInt(parts[0], 10) + 1911
    return `${year}-${parts[1].padStart(2, '0')}-${parts[2].padStart(2, '0')}`
  }

  return ''
}

const convertRocDateEndOfDay = (dateStr?: string | null) => {
  const date = convertRocDate(dateStr)
  return date ? `${date}T23:59:59+08:00` : ''
}

const jobOrganizationName = computed(() => cleanValue(job.value?.org_name || job.value?.org))
const jobTitleText = computed(() => cleanValue(job.value?.title) || '公務人員職缺')
const jobLocationText = computed(() => cleanValue(job.value?.work_address || job.value?.work_place_type || job.value?.place))
const isJobExpired = computed(() => job.value ? isExpired(job.value.date_to) : true)

const jobMetaDescription = computed(() => {
  if (!job.value) return '公務人員職缺詳細資訊'

  const details = [
    `${jobOrganizationName.value}${jobTitleText.value ? `招募${jobTitleText.value}` : ''}`,
    hasMeaningfulValue(job.value.sysnam) ? `職系：${cleanValue(job.value.sysnam)}` : '',
    hasMeaningfulValue(job.value.rank) ? `職等：${cleanValue(job.value.rank)}` : '',
    jobLocationText.value ? `地點：${jobLocationText.value}` : '',
    hasMeaningfulValue(job.value.date_to) ? `報名至：${job.value.date_to}` : ''
  ].filter(Boolean).join('，')

  return truncateText(`${details}。資料來源：行政院人事行政總處事求人開放資料。`)
})

const buildHtmlSection = (label: string, value?: string | null) => {
  const text = normalizeMultilineText(value)
  if (!text) return ''
  return `<p>${label}：${escapeHtml(text).replace(/\n/g, '<br>')}</p>`
}

const jobPostingDescription = computed(() => {
  if (!job.value) return ''

  const introParts = [
    `${jobOrganizationName.value}招募${jobTitleText.value}`,
    hasMeaningfulValue(job.value.sysnam) ? `職系${cleanValue(job.value.sysnam)}` : '',
    hasMeaningfulValue(job.value.rank) ? `職等${cleanValue(job.value.rank)}` : '',
    jobLocationText.value ? `工作地點${jobLocationText.value}` : '',
    hasMeaningfulValue(job.value.date_from) && hasMeaningfulValue(job.value.date_to)
      ? `公告期間${job.value.date_from}至${job.value.date_to}`
      : ''
  ].filter(Boolean).join('，')

  return [
    `<p>${escapeHtml(introParts)}。</p>`,
    buildHtmlSection('條件資格', job.value.work_quality),
    buildHtmlSection('工作項目', job.value.work_item),
    buildHtmlSection('報名與聯絡方式', job.value.contact_method)
  ].join('')
})

const employmentType = computed(() => {
  const source = normalizeText(`${job.value?.type || ''} ${job.value?.person_kind || ''} ${job.value?.title || ''}`)
  if (/兼職|兼任|部分工時|工讀/.test(source)) return 'PART_TIME'
  if (/臨時|代理/.test(source)) return 'TEMPORARY'
  if (/約僱|約用|約聘|聘用|聘僱|僱用/.test(source)) return 'CONTRACTOR'
  return 'FULL_TIME'
})

// SEO
useSeoMeta({
  title: () => job.value 
    ? `開放事求人｜${jobOrganizationName.value}(${jobTitleText.value})｜職缺詳情 - 人事行政總處事求人開放資料` 
    : '職缺詳細資料 - 開放事求人',
  description: () => jobMetaDescription.value,
  keywords: () => job.value 
    ? ['事求人', '人事行政總處事求人', '公務員職缺', '政府職缺', jobOrganizationName.value, jobTitleText.value, cleanValue(job.value.sysnam), '開放事求人'].filter(Boolean).join(', ')
    : '事求人, 公務員職缺, 政府職缺',
  // 只有確認職缺已過期才設 noindex；API 失敗（job.value=null）時保持 index
  // 避免後端短暫錯誤導致 Googlebot 看到 noindex 而永久拒絕收錄
  robots: () => job.value ? 'index,follow' : 'noindex,follow',
  ogTitle: () => job.value 
    ? `開放事求人｜${jobOrganizationName.value}(${jobTitleText.value})｜職缺詳情`
    : '職缺詳細資料',
  ogDescription: () => jobMetaDescription.value,
  ogUrl: jobUrl,
  ogType: 'article',
  // 文章更新時間 - 與對手同等規格
  articleModifiedTime: () => convertRocDate(job.value?.announce_date || job.value?.date_from) || undefined,
})

// Canonical URL + Schema.org Structured Data (JobPosting + BreadcrumbList)
useHead(() => {
  const baseHead = {
    link: [
      { rel: 'canonical', href: jobUrl }
    ]
  }
  
  if (!job.value) return baseHead

  // JobPosting Schema
  const jobPostingSchema = {
    '@context': 'https://schema.org',
    '@type': 'JobPosting',
    'title': jobTitleText.value,
    'url': jobUrl,
    'description': jobPostingDescription.value,
    'identifier': {
      '@type': 'PropertyValue',
      'name': jobOrganizationName.value || '開放事求人',
      'value': String(job.value.id)
    },
    'datePosted': convertRocDate(job.value.announce_date || job.value.date_from),
    'validThrough': convertRocDateEndOfDay(job.value.date_to),
    'employmentType': employmentType.value,
    'hiringOrganization': {
      '@type': 'Organization',
      'name': jobOrganizationName.value || '未提供機關名稱',
      'sameAs': 'https://web3.dgpa.gov.tw/want03front/AP/WANTF00001.ASPX'
    },
    'jobLocation': {
      '@type': 'Place',
      'address': {
        '@type': 'PostalAddress',
        'addressLocality': cleanValue(job.value.work_place_type || job.value.place) || '台灣',
        'streetAddress': jobLocationText.value || '台灣',
        'addressRegion': cleanValue(job.value.work_place_type || job.value.place) || '台灣',
        'addressCountry': 'TW'
      }
    },
    'jobBenefits': '政府機關公務員職位，享有公務人員保障與福利',
    'industry': '政府機關',
    'occupationalCategory': cleanValue(job.value.sysnam) || '公務人員',
    'responsibilities': normalizeMultilineText(job.value.work_item) || undefined,
    'qualifications': normalizeMultilineText(job.value.work_quality) || undefined,
    'directApply': false
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
        'name': `${jobOrganizationName.value}(${jobTitleText.value})`,
        'item': jobUrl
      }
    ]
  }

  return {
    ...baseHead,
    script: [
      {
        type: 'application/ld+json',
        innerHTML: toJsonLd(jobPostingSchema)
      },
      {
        type: 'application/ld+json',
        innerHTML: toJsonLd(breadcrumbSchema)
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
    <!-- SEO 麵包屑導覽列（HTML nav，讓 Google 看到真實導覽結構）-->
    <nav aria-label="breadcrumb" class="mb-4 text-sm text-slate-500">
      <ol class="flex items-center flex-wrap gap-1">
        <li>
          <NuxtLink to="/" class="hover:text-primary-600 transition-colors">首頁</NuxtLink>
        </li>
        <li class="text-slate-300">›</li>
        <li>
          <NuxtLink to="/" class="hover:text-primary-600 transition-colors">職缺列表</NuxtLink>
        </li>
        <li v-if="job" class="text-slate-300">›</li>
        <li v-if="job" class="text-slate-600 font-medium truncate max-w-xs" aria-current="page">
          {{ jobOrganizationName }}（{{ jobTitleText }}）
        </li>
      </ol>
    </nav>

    <!-- Expired Warning Banner -->
    <div v-if="job && isJobExpired" class="mb-6 bg-amber-50 border border-amber-200 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-sm animate-fade-in">
      <div class="flex items-center gap-3 text-amber-800">
        <ExclamationTriangleIcon class="w-6 h-6 flex-shrink-0" />
        <div>
          <p class="font-bold">此職缺已截止報名</p>
          <p class="text-sm text-amber-700 mt-0.5">本職缺已於 {{ job.date_to }} 截止收件，僅保留歷史資料供參考。</p>
        </div>
      </div>
      <NuxtLink 
        to="/" 
        class="inline-flex items-center justify-center px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-sm font-medium transition-colors shadow-sm whitespace-nowrap"
      >
        查看最新職缺列表
      </NuxtLink>
    </div>

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

      <!-- 同機關相關職缺區塊（增加內部連結，提升 SEO 深度）-->
      <aside
        v-if="duplicates && duplicates.length > 0"
        class="mt-6 bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden"
        aria-label="同機關相關職缺"
      >
        <div class="px-6 py-4 border-b border-slate-100 bg-slate-50">
          <h2 class="text-base font-semibold text-slate-700">
            {{ jobOrganizationName }} 的其他職缺
          </h2>
        </div>
        <ul class="divide-y divide-slate-100">
          <li
            v-for="dup in duplicates.slice(0, 6)"
            :key="dup.id"
            class="px-6 py-3 flex items-center justify-between hover:bg-slate-50 transition-colors"
          >
            <div class="min-w-0">
              <NuxtLink
                :to="`/job/${dup.id}`"
                class="text-primary-600 hover:underline font-medium text-sm truncate block"
              >
                {{ dup.title || dup.org_name }}
              </NuxtLink>
              <p class="text-xs text-slate-400 mt-0.5">{{ dup.date_from }} ~ {{ dup.date_to }}</p>
            </div>
          </li>
        </ul>
      </aside>

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
