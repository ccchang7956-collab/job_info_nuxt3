<script setup>
import { 
  BuildingOfficeIcon,
  BriefcaseIcon,
  MapPinIcon,
  CalendarIcon,
  UserGroupIcon,
  ArrowTopRightOnSquareIcon,
  ClockIcon,
  InformationCircleIcon
} from '@heroicons/vue/24/outline'
import { computed } from 'vue'

const props = defineProps({
  job: {
    type: Object,
    required: true
  },
  duplicates: {
    type: Array,
    default: () => []
  }
})

// Filter and sort duplicates (legacy logic: date_from < current job's date_from)
const historyJobs = computed(() => {
  if (!props.duplicates || props.duplicates.length === 0) return []
  
  const currentJobDate = props.job.date_from
  return props.duplicates
    .filter(d => d.date_from < currentJobDate)
    .sort((a, b) => b.date_from.localeCompare(a.date_from))
})
</script>

<template>
  <div class="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden border-t-4 border-t-primary-500">
    <!-- Header -->
    <header class="p-6 sm:p-8 border-b border-slate-100 bg-gradient-to-b from-slate-50/80 to-white">
      <slot name="header-actions"></slot>
      
      <h1 class="text-2xl sm:text-3xl font-bold text-slate-900 mb-3">{{ job.title }}</h1>
      <div class="flex items-center gap-2 text-slate-600 font-medium text-lg">
        <BuildingOfficeIcon class="w-6 h-6 text-primary-500" />
        {{ job.org_name }}
      </div>
    </header>

    <div class="p-6 sm:p-8">
      <!-- Meta Grid -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-10">
        <!-- Job System -->
        <div class="flex items-start gap-4 p-4 rounded-xl bg-slate-50 border border-slate-100 hover:border-primary-200 hover:bg-primary-50/30 transition-colors group">
          <div class="p-2.5 bg-white rounded-lg shadow-sm text-slate-400 group-hover:text-primary-500 shrink-0 transition-colors">
            <BriefcaseIcon class="w-6 h-6" />
          </div>
          <div>
            <div class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">職系</div>
            <div class="font-bold text-slate-800 text-lg">{{ job.sysnam }}</div>
          </div>
        </div>

        <!-- Rank -->
        <div class="flex items-start gap-4 p-4 rounded-xl bg-slate-50 border border-slate-100 hover:border-primary-200 hover:bg-primary-50/30 transition-colors group">
          <div class="p-2.5 bg-white rounded-lg shadow-sm text-slate-400 group-hover:text-primary-500 shrink-0 transition-colors">
            <span class="w-6 h-6 flex items-center justify-center font-black text-sm border-2 border-current rounded">R</span>
          </div>
          <div>
            <div class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">職等</div>
            <div class="font-bold text-slate-800 text-lg">{{ job.rank }}</div>
          </div>
        </div>

        <!-- City -->
        <div class="flex items-start gap-4 p-4 rounded-xl bg-slate-50 border border-slate-100 hover:border-primary-200 hover:bg-primary-50/30 transition-colors group">
          <div class="p-2.5 bg-white rounded-lg shadow-sm text-slate-400 group-hover:text-primary-500 shrink-0 transition-colors">
            <MapPinIcon class="w-6 h-6" />
          </div>
          <div>
            <div class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">縣市</div>
            <div class="font-bold text-slate-800 text-lg">{{ job.work_place_type }}</div>
          </div>
        </div>

        <!-- Date From -->
        <div class="flex items-start gap-4 p-4 rounded-xl bg-slate-50 border border-slate-100 hover:border-primary-200 hover:bg-primary-50/30 transition-colors group">
          <div class="p-2.5 bg-white rounded-lg shadow-sm text-slate-400 group-hover:text-primary-500 shrink-0 transition-colors">
            <CalendarIcon class="w-6 h-6" />
          </div>
          <div>
            <div class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">發布日期</div>
            <div class="font-bold text-slate-800 text-lg">{{ job.date_from }}</div>
          </div>
        </div>

        <!-- Date To -->
        <div class="flex items-start gap-4 p-4 rounded-xl bg-slate-50 border border-slate-100 hover:border-primary-200 hover:bg-primary-50/30 transition-colors group">
          <div class="p-2.5 bg-white rounded-lg shadow-sm text-slate-400 group-hover:text-primary-500 shrink-0 transition-colors">
            <CalendarIcon class="w-6 h-6" />
          </div>
          <div>
            <div class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">截止日期</div>
            <div class="font-bold text-slate-800 text-lg">{{ job.date_to }}</div>
          </div>
        </div>

        <!-- Quota -->
        <div class="flex items-start gap-4 p-4 rounded-xl bg-slate-50 border border-slate-100 hover:border-primary-200 hover:bg-primary-50/30 transition-colors group">
          <div class="p-2.5 bg-white rounded-lg shadow-sm text-slate-400 group-hover:text-primary-500 shrink-0 transition-colors">
            <UserGroupIcon class="w-6 h-6" />
          </div>
          <div>
            <div class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">名額</div>
            <div class="font-bold text-slate-800 text-lg">{{ job.number_of || '詳見簡章' }}</div>
          </div>
        </div>
      </div>

      <!-- Content Sections -->
      <div class="space-y-8">
        <section>
          <h3 class="text-lg font-bold text-slate-900 mb-3 flex items-center gap-2">
            <span class="w-1.5 h-6 bg-primary-500 rounded-full shadow-sm shadow-primary-200"></span>
            工作地點
          </h3>
          <div class="text-slate-700 leading-relaxed whitespace-pre-wrap bg-slate-50/50 p-4 rounded-xl border border-slate-100">
            <a :href="`https://www.google.com/maps/search/?q=${job.work_address}`" target="_blank" class="flex items-center gap-2 hover:text-primary-600 hover:underline">
              <MapPinIcon class="w-5 h-5 text-slate-400" />
              {{ job.work_address }}
            </a>
          </div>
        </section>

        <section>
          <h3 class="text-lg font-bold text-slate-900 mb-3 flex items-center gap-2">
            <span class="w-1.5 h-6 bg-primary-500 rounded-full shadow-sm shadow-primary-200"></span>
            工作項目
          </h3>
          <div class="text-slate-700 leading-relaxed whitespace-pre-wrap bg-slate-50/50 p-4 rounded-xl border border-slate-100">
            {{ job.work_item }}
          </div>
        </section>

        <section>
          <h3 class="text-lg font-bold text-slate-900 mb-3 flex items-center gap-2">
            <span class="w-1.5 h-6 bg-primary-500 rounded-full shadow-sm shadow-primary-200"></span>
            資格條件
          </h3>
          <div class="text-slate-700 leading-relaxed whitespace-pre-wrap bg-slate-50/50 p-4 rounded-xl border border-slate-100">
            {{ job.work_quality || '詳見簡章' }}
          </div>
        </section>

        <section>
          <h3 class="text-lg font-bold text-slate-900 mb-3 flex items-center gap-2">
            <span class="w-1.5 h-6 bg-primary-500 rounded-full shadow-sm shadow-primary-200"></span>
            聯絡方式
          </h3>
          <div class="text-slate-700 leading-relaxed whitespace-pre-wrap bg-slate-50/50 p-4 rounded-xl border border-slate-100">
            {{ job.contact_method || '詳見簡章' }}
          </div>
        </section>

        <!-- History Job Openings -->
        <section>
          <h3 class="text-lg font-bold text-slate-900 mb-3 flex items-center gap-2">
            <span class="w-1.5 h-6 bg-primary-500 rounded-full shadow-sm shadow-primary-200"></span>
            歷史開缺
            <div class="group relative inline-block">
              <InformationCircleIcon class="w-5 h-5 text-slate-400 cursor-help" />
              <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 p-2 bg-slate-800 text-white text-xs rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10 text-center">
                判斷標準：相同機關且相同工作內容的過去職缺
                <div class="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-slate-800"></div>
              </div>
            </div>
          </h3>
          
          <div v-if="historyJobs.length > 0" class="space-y-3">
            <div v-for="historyJob in historyJobs" :key="historyJob.id" class="flex items-center justify-between p-4 bg-slate-50 border border-slate-100 rounded-xl hover:border-primary-200 hover:bg-primary-50/30 transition-all group">
              <div class="min-w-0">
                <div class="font-bold text-slate-800 mb-1 group-hover:text-primary-700 truncate">{{ historyJob.title }}</div>
                <div class="flex items-center gap-2 text-sm text-slate-500">
                  <ClockIcon class="w-4 h-4" />
                  <span>{{ historyJob.date_from }} ~ {{ historyJob.date_to }}</span>
                </div>
              </div>
              <router-link 
                :to="{ name: 'job-details', params: { id: historyJob.id } }"
                class="flex-shrink-0 ml-4 px-3 py-1.5 bg-white border border-primary-200 text-primary-600 text-sm font-medium rounded-lg hover:bg-primary-600 hover:text-white transition-colors"
              >
                檢視
              </router-link>
            </div>
          </div>
          <div v-else class="text-center py-8 bg-slate-50 rounded-xl border border-dashed border-slate-200 text-slate-400">
            <BriefcaseIcon class="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p>無歷史開缺資料</p>
          </div>
        </section>
      </div>

      <!-- Actions -->
      <div class="mt-12 pt-8 border-t border-slate-100 flex justify-center">
        <a 
          :href="job.view_url" 
          target="_blank" 
          class="inline-flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white px-8 py-3 rounded-xl font-bold text-lg shadow-lg shadow-primary-500/20 hover:shadow-primary-500/40 hover:-translate-y-0.5 transition-all duration-200"
        >
          前往事求人網站查看完整資訊
          <ArrowTopRightOnSquareIcon class="w-5 h-5" />
        </a>
      </div>
    </div>
  </div>
</template>
