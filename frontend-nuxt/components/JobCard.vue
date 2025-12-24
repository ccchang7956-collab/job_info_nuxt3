<script setup>
import { 
  BuildingOfficeIcon, 
  ChevronRightIcon
} from '@heroicons/vue/24/outline'

defineProps({
  job: {
    type: Object,
    required: true
  }
})
</script>

<template>
  <NuxtLink 
    :to="`/job/${job.id}`" 
    class="group bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden hover:shadow-md hover:border-primary-300 transition-all duration-300 flex flex-col cursor-pointer"
  >
    <!-- Blue Header Section - Org Name -->
    <div class="bg-primary-600 px-4 py-4 flex items-center justify-between gap-3">
      <div class="flex items-center gap-2 min-w-0 flex-1">
        <BuildingOfficeIcon class="w-6 h-6 text-blue-200 flex-shrink-0" />
        <span class="text-xl font-bold text-white truncate">{{ job.org }}</span>
      </div>
      <ChevronRightIcon class="w-7 h-7 text-blue-200 group-hover:text-white group-hover:translate-x-1 transition-all flex-shrink-0" />
    </div>
    
    <!-- Content Body - Table-like Layout -->
    <div class="p-4 flex flex-col gap-3 flex-1">
      <!-- Info Rows -->
      <div class="space-y-2.5">
        <!-- 時間起迄 -->
        <div class="flex items-start">
          <span class="w-20 flex-shrink-0 text-slate-500 text-base">時間起迄</span>
          <span class="text-slate-800 text-base font-mono">{{ job.date_from }} ~ {{ job.date_to }}</span>
        </div>
        
        <!-- 職系 -->
        <div class="flex items-start">
          <span class="w-20 flex-shrink-0 text-slate-500 text-base">職系</span>
          <span class="text-slate-800 text-base font-medium">{{ job.sysnam }}</span>
        </div>
        
        <!-- 職稱 -->
        <div class="flex items-start">
          <span class="w-20 flex-shrink-0 text-slate-500 text-base">職稱</span>
          <span class="text-slate-800 text-base font-medium">{{ job.title }}</span>
        </div>
        
        <!-- 職等 -->
        <div class="flex items-start">
          <span class="w-20 flex-shrink-0 text-slate-500 text-base">職等</span>
          <span class="text-slate-800 text-base">{{ job.rank_display || job.rank }}</span>
        </div>
        
        <!-- 地點 -->
        <div class="flex items-start">
          <span class="w-20 flex-shrink-0 text-slate-500 text-base">地點</span>
          <span class="text-slate-800 text-base">{{ job.place }}</span>
        </div>
      </div>

      <!-- Footer Status Badges -->
      <div class="mt-auto pt-3 border-t border-slate-100 flex items-center justify-start gap-2 flex-wrap">
        <span v-if="job.comment_count > 0" class="inline-flex items-center px-2.5 py-1 rounded text-sm font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
          有留言
        </span>
        <span v-if="job.history_count > 0" class="inline-flex items-center px-2.5 py-1 rounded text-sm font-bold bg-amber-50 text-amber-700 border border-amber-200">
          曾開缺
        </span>
        <span v-if="!job.comment_count && !job.history_count" class="text-slate-400 text-sm">
          —
        </span>
      </div>
    </div>
  </NuxtLink>
</template>
