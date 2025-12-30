<script setup lang="ts">
import { 
  ChevronRightIcon
} from '@heroicons/vue/24/outline'
import type { Job } from '@/types'

defineProps<{
  job: Job
}>()

// Use shared date formatting utilities
const { isNewJob, isExpired } = useFormatDate()

// Use job constants for sysnam categorization
const { getSysnamType } = useJobConstants()
</script>

<template>
  <NuxtLink 
    :to="`/job/${job.id}`" 
    class="group bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden hover:shadow-md hover:border-primary-300 transition-all duration-300 flex flex-col cursor-pointer"
  >
    <!-- Blue Header Section - Org Name -->
    <div class="bg-primary-600 px-5 py-5 flex items-center justify-between gap-3">
      <div class="flex items-center gap-2.5 min-w-0 flex-1">
        <span class="text-2xl font-bold text-white break-words leading-tight">{{ job.org }}</span>
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
          <div class="flex items-center gap-2">
            <span class="text-slate-800 text-lg font-mono">{{ job.date_from }} ~ {{ job.date_to }}</span>
            <span 
              v-if="isNewJob(job.announce_date)" 
              class="inline-flex items-center px-2 py-1 rounded text-sm font-bold bg-red-500 text-white animate-pulse"
            >
              NEW
            </span>
          </div>
        </div>
        
        <!-- 職稱 -->
        <div class="flex items-start">
          <span class="w-24 flex-shrink-0 text-slate-500 text-lg">職稱</span>
          <span class="text-slate-800 text-lg font-medium">{{ job.title }}</span>
        </div>

        <!-- 職系 -->
        <div class="flex items-start">
          <span class="w-24 flex-shrink-0 text-slate-500 text-lg">職系</span>
          <span 
            class="text-lg font-medium px-2 py-0.5 rounded"
            :class="{
              'bg-blue-50 text-blue-700': getSysnamType(job.sysnam) === 'admin',
              'bg-emerald-50 text-emerald-700': getSysnamType(job.sysnam) === 'tech',
              'text-slate-800': getSysnamType(job.sysnam) === 'unknown'
            }"
          >
            {{ job.sysnam }}
          </span>
        </div>
        
        <!-- 職等 -->
        <div class="flex items-start">
          <span class="w-24 flex-shrink-0 text-slate-500 text-lg">職等</span>
          <span class="inline-flex items-center px-2.5 py-1 rounded text-base font-bold bg-slate-100 text-slate-600 border border-slate-200">
            {{ job.rank_display || job.rank }}
          </span>
        </div>
        
        <!-- 地點 -->
        <div class="flex items-start">
          <span class="w-24 flex-shrink-0 text-slate-500 text-lg">地點</span>
          <span class="text-slate-800 text-lg">{{ job.place }}</span>
        </div>
      </div>


      <!-- Footer Status Badges -->
      <div class="mt-auto pt-4 border-t border-slate-100 flex items-center justify-start gap-2 flex-wrap">
        <span 
          v-if="isExpired(job.date_to)" 
          class="inline-flex items-center px-2 py-1 rounded text-sm font-bold bg-slate-200 text-slate-500"
        >
          已逾期
        </span>
        <span v-if="job.comment_count > 0" class="inline-flex items-center px-2 py-1 rounded text-sm font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
          有留言
        </span>
        <span v-if="job.history_count > 0" class="inline-flex items-center px-2 py-1 rounded text-sm font-bold bg-amber-50 text-amber-700 border border-amber-200">
          曾開缺
        </span>
        <span v-if="!isExpired(job.date_to) && !job.comment_count && !job.history_count" class="text-slate-400 text-base">
          —
        </span>
      </div>
    </div>
  </NuxtLink>
</template>
