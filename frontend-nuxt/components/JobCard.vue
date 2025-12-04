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
  <div class="group bg-white rounded-xl shadow-sm border border-slate-200 p-5 hover:shadow-lg hover:border-primary-300 transition-all duration-300 flex flex-col gap-4 relative overflow-hidden">
    <div class="absolute top-0 left-0 w-1 h-full bg-primary-500 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
    
    <div class="border-b border-slate-100 pb-3">
      <div class="flex items-start justify-between gap-2 mb-2">
        <h3 class="text-lg font-bold text-slate-800 leading-tight group-hover:text-primary-600 transition-colors">
          <NuxtLink :to="`/job/${job.id}`" class="hover:underline decoration-2 underline-offset-2">
            {{ job.title }}
          </NuxtLink>
        </h3>
        <ChevronRightIcon class="w-5 h-5 text-slate-300 group-hover:text-primary-500 group-hover:translate-x-1 transition-all flex-shrink-0" />
      </div>
      <div class="flex items-center gap-1.5 text-slate-600 text-sm font-medium">
        <BuildingOfficeIcon class="w-4 h-4 text-slate-400" />
        <span>{{ job.org }}</span>
      </div>
    </div>
    
    <div class="grid grid-cols-2 gap-3 text-sm">
      <div class="flex items-center gap-2 col-span-2 sm:col-span-1">
        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-50 text-blue-700 border border-blue-100">
          {{ job.sysnam }}
        </span>
      </div>
      <div class="flex items-center gap-2 col-span-2 sm:col-span-1">
        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-600 border border-slate-200">
          {{ job.rank_display || job.rank }}
        </span>
      </div>
      <div class="flex items-center gap-2 text-slate-600 col-span-2">
        <MapPinIcon class="w-4 h-4 text-slate-400 flex-shrink-0" />
        <span class="truncate">{{ job.place }}</span>
      </div>
      <div class="flex items-center gap-2 text-slate-500 col-span-2 font-mono text-xs">
        <CalendarIcon class="w-4 h-4 text-slate-400 flex-shrink-0" />
        <span>{{ job.date_from }} ~ {{ job.date_to }}</span>
      </div>
    </div>

    <div class="mt-auto pt-4 border-t border-dashed border-slate-200 flex items-center justify-between">
      <div v-if="job.comment_count > 0" class="flex items-center gap-1.5 text-emerald-600 text-xs font-bold bg-emerald-50 px-2 py-1 rounded-md border border-emerald-100">
        <ChatBubbleLeftIcon class="w-3.5 h-3.5" />
        <span>{{ job.comment_count }} 則留言</span>
      </div>
      <div v-else class="text-xs text-slate-400 italic flex items-center gap-1">
        <ChatBubbleLeftIcon class="w-3.5 h-3.5" />
        尚無留言
      </div>
      
      <NuxtLink 
        :to="`/job/${job.id}`" 
        class="text-sm font-medium text-primary-600 hover:text-primary-700 hover:bg-primary-50 px-3 py-1.5 rounded-lg transition-colors"
      >
        查看詳情
      </NuxtLink>
    </div>
  </div>
</template>
