<script setup>
import { 
  BuildingOfficeIcon, 
  BriefcaseIcon, 
  MapPinIcon, 
  CalendarIcon,
  ChatBubbleLeftIcon,
  ChevronRightIcon,
  ArrowPathIcon
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
    <!-- Blue Header Section - Only Org Name -->
    <div class="bg-primary-600 px-4 py-5 flex items-center justify-between gap-3">
      <div class="flex items-center gap-2 min-w-0 flex-1">
        <BuildingOfficeIcon class="w-7 h-7 text-blue-200 flex-shrink-0" />
        <span class="text-2xl font-bold text-white truncate">{{ job.org }}</span>
      </div>
      <ChevronRightIcon class="w-8 h-8 text-blue-200 group-hover:text-white group-hover:translate-x-1 transition-all flex-shrink-0" />
    </div>
    
    <!-- Content Body -->
    <div class="p-5 flex flex-col gap-4 flex-1">
      <!-- Title + Badges Row -->
      <div class="flex flex-wrap items-center gap-2.5">
        <span class="inline-flex items-center px-3.5 py-2 rounded text-lg font-bold bg-primary-50 text-primary-700 border border-primary-200">
          {{ job.title }}
        </span>
        <span class="inline-flex items-center px-3.5 py-2 rounded text-lg font-bold bg-blue-50 text-blue-700 border border-blue-100 whitespace-nowrap">
          {{ job.sysnam }}
        </span>
        <span class="inline-flex items-center px-3.5 py-2 rounded text-lg font-bold bg-slate-100 text-slate-600 border border-slate-200 whitespace-nowrap">
          {{ job.rank_display || job.rank }}
        </span>
      </div>

      <!-- Info Grid -->
      <div class="grid grid-cols-1 gap-3 text-lg text-slate-700">
        <div class="flex items-center gap-2">
          <MapPinIcon class="w-6 h-6 text-slate-400 flex-shrink-0" />
          <span class="truncate">{{ job.place }}</span>
        </div>
        <div class="flex items-center gap-2 font-mono text-base text-slate-600">
          <CalendarIcon class="w-6 h-6 text-slate-400 flex-shrink-0" />
          <span>{{ job.date_from }} ~ {{ job.date_to }}</span>
        </div>
      </div>

      <!-- Footer Status (Desktop Table Style) -->
      <div class="mt-auto pt-3 border-t border-slate-100 flex items-center justify-start gap-3">
        <div v-show="job.comment_count > 0" class="relative">
          <ChatBubbleLeftIcon class="w-6 h-6 text-emerald-500" />
          <span class="absolute -top-1 -right-1 flex h-2.5 w-2.5">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
          </span>
        </div>
        <div v-show="job.history_count > 0" title="曾開缺">
          <ArrowPathIcon class="w-6 h-6 text-amber-500" />
        </div>
        <span v-if="!job.comment_count && !job.history_count" class="text-slate-300 text-2xl leading-none">&middot;</span>
      </div>
    </div>
  </NuxtLink>
</template>
