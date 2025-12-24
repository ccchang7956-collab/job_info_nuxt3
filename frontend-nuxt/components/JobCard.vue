<script setup>
import { 
  BuildingOfficeIcon, 
  BriefcaseIcon, 
  MapPinIcon, 
  CalendarIcon,
  ChatBubbleLeftIcon,
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
  <div class="group bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden hover:shadow-md transition-all duration-300 flex flex-col">
    <!-- Blue Header Section -->
    <div class="bg-primary-600 px-4 py-3 flex items-start justify-between gap-3">
      <div class="min-w-0 flex-1">
        <h3 class="text-lg font-bold text-white leading-tight mb-1 truncate">
          <NuxtLink :to="`/job/${job.id}`" class="hover:underline decoration-2 underline-offset-2">
            {{ job.title }}
          </NuxtLink>
        </h3>
        <div class="flex items-center gap-1.5 text-blue-100 text-sm font-medium">
          <BuildingOfficeIcon class="w-4 h-4 text-blue-200" />
          <span class="truncate">{{ job.org }}</span>
        </div>
      </div>
      <ChevronRightIcon class="w-5 h-5 text-blue-200 group-hover:text-white group-hover:translate-x-1 transition-all flex-shrink-0 mt-1" />
    </div>
    
    <!-- Content Body -->
    <div class="p-4 flex flex-col gap-3 flex-1">
      <!-- Badges Row -->
      <div class="flex flex-wrap items-center gap-2">
        <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-bold bg-blue-50 text-blue-700 border border-blue-100 whitespace-nowrap">
          {{ job.sysnam }}
        </span>
        <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-bold bg-slate-100 text-slate-600 border border-slate-200 whitespace-nowrap">
          {{ job.rank_display || job.rank }}
        </span>
      </div>

      <!-- Info Grid -->
      <div class="grid grid-cols-1 gap-2 text-sm text-slate-600">
        <div class="flex items-center gap-2">
          <MapPinIcon class="w-4 h-4 text-slate-400 flex-shrink-0" />
          <span class="truncate">{{ job.place }}</span>
        </div>
        <div class="flex items-center gap-2 font-mono text-xs text-slate-500">
          <CalendarIcon class="w-4 h-4 text-slate-400 flex-shrink-0" />
          <span>{{ job.date_from }} ~ {{ job.date_to }}</span>
        </div>
      </div>

      <!-- Footer Actions -->
      <div class="mt-auto pt-3 border-t border-slate-100 flex items-center justify-between">
        <div v-if="job.comment_count > 0" class="flex items-center gap-1.5 text-emerald-600 text-xs font-bold bg-emerald-50 px-2 py-1 rounded border border-emerald-100">
          <ChatBubbleLeftIcon class="w-3.5 h-3.5" />
          <span>{{ job.comment_count }} 則留言</span>
        </div>
        <div v-else class="text-xs text-slate-300 flex items-center gap-1">
          <ChatBubbleLeftIcon class="w-3.5 h-3.5" />
          尚無留言
        </div>
        
        <NuxtLink 
          :to="`/job/${job.id}`" 
          class="text-sm font-bold text-primary-600 hover:text-primary-700 hover:bg-primary-50 px-3 py-1.5 rounded transition-colors"
        >
          查看詳情
        </NuxtLink>
      </div>
    </div>
  </div>
</template>
