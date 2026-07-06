<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import type { JobListResponse } from '@/types'

const route = useRoute()
const sysnamName = computed(() => String(route.params.sysnam || '').trim())
const siteUrl = useSiteUrl()
const pageUrl = computed(() => `${siteUrl}/sysnams/${encodeURIComponent(sysnamName.value)}`)

const { data, error } = await useFetch<JobListResponse>('/api/jobs', {
  query: { sysnam: sysnamName.value, per_page: 20 }
})

useSeoMeta({
  title: () => `最新 ${sysnamName.value} 職系公務員職缺列表｜事求人職缺查詢 - 開放事求人`,
  description: () => `最即時的 ${sysnamName.value} 職系公務人員事求人職缺資訊。彙整全國各級政府機關招募${sysnamName.value}職系公務員最新開缺。`,
  keywords: () => `事求人, 公務員職缺, ${sysnamName.value}, ${sysnamName.value}職缺, 開放事求人`,
  robots: 'index,follow',
  ogTitle: () => `最新 ${sysnamName.value} 職系公務員職缺列表 - 開放事求人`,
  ogDescription: () => `即時同步全國各級政府機關最新 ${sysnamName.value} 職系公務員職缺。`,
  ogUrl: () => pageUrl.value,
})

useHead(() => ({
  link: [{ rel: 'canonical', href: pageUrl.value }],
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': [
          { '@type': 'ListItem', 'position': 1, 'name': '首頁', 'item': `${siteUrl}/` },
          { '@type': 'ListItem', 'position': 2, 'name': `${sysnamName.value} 職缺`, 'item': pageUrl.value }
        ]
      })
    }
  ]
}))
</script>

<template>
  <div class="container mx-auto px-4 py-8 max-w-5xl">
    <nav aria-label="breadcrumb" class="mb-6 text-sm text-slate-500">
      <ol class="flex items-center flex-wrap gap-1">
        <li><NuxtLink to="/" class="hover:text-primary-600 transition-colors">首頁</NuxtLink></li>
        <li class="text-slate-300">›</li>
        <li class="text-slate-600 font-medium truncate" aria-current="page">{{ sysnamName }}職系專區</li>
      </ol>
    </nav>

    <div class="mb-8">
      <h1 class="text-3xl font-bold text-slate-800 mb-2">最新 {{ sysnamName }} 職系職缺</h1>
      <p class="text-slate-500 text-lg">
        歡迎瀏覽開放事求人 {{ sysnamName }} 職系專區。本頁面為您整理全國各機關招募 {{ sysnamName }} 職系之最新公務員缺額與開缺紀錄，每日自動同步更新。
      </p>
    </div>

    <div v-if="error" class="bg-red-50 p-6 rounded-xl text-center text-red-600">無法載入職缺資料，請稍後再試。</div>
    <div v-else-if="!data" class="text-center py-12 text-slate-400">讀取中...</div>
    <div v-else-if="!data.jobs || data.jobs.length === 0" class="text-center py-12 text-slate-500 bg-white rounded-xl border border-slate-200">
      目前無最新職缺
    </div>
    <div v-else>
      <div class="hidden md:block bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden mb-8">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-primary-600 border-b border-primary-700 text-white text-base font-bold whitespace-nowrap">
              <th class="p-4 w-[180px]">機關名稱</th>
              <th class="p-4 w-[120px]">職稱</th>
              <th class="p-4 w-[120px]">職系</th>
              <th class="p-4 w-[90px]">職等</th>
              <th class="p-4 w-[100px]">工作地點</th>
              <th class="p-4 w-[130px]">期間</th>
              <th class="p-4 text-center w-[70px]">查看</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            <tr v-for="job in data.jobs" :key="job.id" class="hover:bg-blue-50/50 transition-colors">
              <td class="p-4 font-bold text-slate-700">{{ job.org }}</td>
              <td class="p-4 font-bold text-slate-700">{{ job.title }}</td>
              <td class="p-4">{{ job.sysnam }}</td>
              <td class="p-4">{{ job.rank_display || job.rank }}</td>
              <td class="p-4">{{ job.place }}</td>
              <td class="p-4">{{ job.date_from }} ~ {{ job.date_to }}</td>
              <td class="p-4 text-center">
                <NuxtLink :to="`/job/${job.id}`" class="px-3 py-1.5 bg-white border border-slate-300 text-slate-700 rounded-lg text-xs font-bold hover:bg-primary-600 hover:text-white transition-colors">查看</NuxtLink>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="md:hidden grid grid-cols-1 gap-4">
        <JobCard v-for="job in data.jobs" :key="job.id" :job="job" />
      </div>
    </div>
  </div>
</template>
