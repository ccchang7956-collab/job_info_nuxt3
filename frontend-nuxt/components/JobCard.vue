<script setup lang="ts">
import { 
  ChevronRightIcon
} from '@heroicons/vue/24/outline'
import type { Job } from '@/types'

defineProps<{
  job: Job
}>()

// Helper to check if job is new (announced today or yesterday)
const isNewJob = (announceDate: string | undefined): boolean => {
  if (!announceDate) return false
  try {
    let rocYear: number, month: number, day: number
    
    if (announceDate.includes('/')) {
      const parts = announceDate.split('/')
      if (parts.length !== 3) return false
      rocYear = parseInt(parts[0])
      month = parseInt(parts[1])
      day = parseInt(parts[2])
    } else {
      const str = announceDate.padStart(7, '0')
      rocYear = parseInt(str.slice(0, 3))
      month = parseInt(str.slice(3, 5))
      day = parseInt(str.slice(5, 7))
    }
    
    const westYear = rocYear + 1911
    const jobDate = new Date(westYear, month - 1, day)
    
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    const yesterday = new Date(today)
    yesterday.setDate(yesterday.getDate() - 1)
    
    return jobDate >= yesterday
  } catch (e) {
    return false
  }
}
</script>

<template>
  <NuxtLink 
    :to="`/job/${job.id}`" 
    class="group bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden hover:shadow-md hover:border-primary-300 transition-all duration-300 flex flex-col cursor-pointer"
  >
    <!-- Blue Header Section - Org Name -->
    <div class="bg-primary-600 px-5 py-5 flex items-center justify-between gap-3">
      <div class="flex items-center gap-2.5 min-w-0 flex-1">
        <span 
          v-if="isNewJob(job.announce_date)" 
          class="inline-flex items-center px-2 py-1 rounded text-sm font-bold bg-red-500 text-white animate-pulse flex-shrink-0"
        >
          NEW
        </span>
        <span class="text-2xl font-bold text-white truncate">{{ job.org }}</span>
      </div>
      <ChevronRightIcon class="w-8 h-8 text-blue-200 group-hover:text-white group-hover:translate-x-1 transition-all flex-shrink-0" />
    </div>
    
    <!-- Content Body - Table-like Layout -->
    <div class="p-5 flex flex-col gap-4 flex-1">
      <!-- Info Rows -->
      <div class="space-y-3">
        <!-- 時間起迄 -->
        <div class="flex items-start">
          <span class="w-24 flex-shrink-0 text-slate-500 text-lg">時間起迄</span>
          <span class="text-slate-800 text-lg font-mono">{{ job.date_from }} ~ {{ job.date_to }}</span>
        </div>
        
        <!-- 職系 -->
        <div class="flex items-start">
          <span class="w-24 flex-shrink-0 text-slate-500 text-lg">職系</span>
          <span class="text-slate-800 text-lg font-medium">{{ job.sysnam }}</span>
        </div>
        
        <!-- 職稱 -->
        <div class="flex items-start">
          <span class="w-24 flex-shrink-0 text-slate-500 text-lg">職稱</span>
          <span class="text-slate-800 text-lg font-medium">{{ job.title }}</span>
        </div>
        
        <!-- 職等 -->
        <div class="flex items-start">
          <span class="w-24 flex-shrink-0 text-slate-500 text-lg">職等</span>
          <span class="text-slate-800 text-lg">{{ job.rank_display || job.rank }}</span>
        </div>
        
        <!-- 地點 -->
        <div class="flex items-start">
          <span class="w-24 flex-shrink-0 text-slate-500 text-lg">地點</span>
          <span class="text-slate-800 text-lg">{{ job.place }}</span>
        </div>
      </div>

      <!-- Footer Status Badges -->
      <div class="mt-auto pt-4 border-t border-slate-100 flex items-center justify-start gap-2 flex-wrap">
        <span v-if="job.comment_count > 0" class="inline-flex items-center px-3 py-1.5 rounded text-base font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
          有留言
        </span>
        <span v-if="job.history_count > 0" class="inline-flex items-center px-3 py-1.5 rounded text-base font-bold bg-amber-50 text-amber-700 border border-amber-200">
          曾開缺
        </span>
        <span v-if="!job.comment_count && !job.history_count" class="text-slate-400 text-base">
          —
        </span>
      </div>
    </div>
  </NuxtLink>
</template>
