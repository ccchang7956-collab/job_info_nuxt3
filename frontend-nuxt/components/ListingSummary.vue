<script setup lang="ts">
import type { JobListResponse } from '@/types'

defineProps<{ data: JobListResponse; name: string }>()
const { data: update } = await useFetch<{ date: string }>('/api/metadata/last-update')
</script>

<template>
  <section class="mb-6 rounded-xl border border-slate-200 bg-slate-50 p-5" aria-label="職缺資料摘要">
    <h2 class="font-bold text-slate-800 mb-2">{{ name }}職缺資料摘要</h2>
    <p class="text-slate-600">
      目前共有 <strong>{{ data.total_count }}</strong> 筆未截止的職缺公告，
      本頁顯示 {{ data.jobs.length }} 筆。公告筆數不等於招募人數，預設不包含無職系職缺。
    </p>
    <p v-if="update?.date && update.date !== '無資料'" class="mt-2 text-sm text-slate-500">
      資料同步日期：{{ update.date }}。截止日期與報名資格請以各機關公告為準。
    </p>
    <p class="mt-2 text-sm text-slate-500">
      資料來源：<a href="https://data.gov.tw/dataset/7229" target="_blank" rel="noopener noreferrer" class="text-primary-600 underline">行政院人事行政總處事求人機關徵才資料</a>。
      <NuxtLink to="/charts" class="text-primary-600 underline">查看每月開缺統計</NuxtLink>
    </p>
  </section>
</template>
