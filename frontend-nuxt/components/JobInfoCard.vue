<script setup>
import { 
  CalendarIcon,
  CalendarDaysIcon,
  BuildingOffice2Icon,
  AcademicCapIcon,
  BriefcaseIcon,
  UserIcon,
  UserPlusIcon,
  UsersIcon,
  MapPinIcon,
  HomeIcon,
  DocumentTextIcon,
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

// 職缺資訊欄位定義
const jobInfoFields = computed(() => [
  { icon: CalendarIcon, label: '公告日期', value: props.job.date_from },
  { icon: CalendarDaysIcon, label: '有效期間', value: `${props.job.date_from} ~ ${props.job.date_to}` },
  { icon: BuildingOffice2Icon, label: '徵才機關', value: props.job.org_name },
  { icon: AcademicCapIcon, label: '職務列等', value: props.job.rank },
  { icon: BriefcaseIcon, label: '職系', value: props.job.sysnam },
  { icon: UserIcon, label: '人員區分', value: props.job.work_kind || '-' },
  { icon: UserPlusIcon, label: '正取', value: props.job.quota_regular || '-' },
  { icon: UsersIcon, label: '候補', value: props.job.quota_backup || '-' },
  { icon: MapPinIcon, label: '工作地點', value: props.job.work_place_type },
  { icon: HomeIcon, label: '地址', value: props.job.work_address, isLink: true, linkUrl: `https://www.google.com/maps/search/?q=${props.job.work_address}` },
])
</script>

<template>
  <div class="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
    <!-- Header Actions Slot -->
    <div class="p-6 pb-0">
      <slot name="header-actions"></slot>
    </div>

    <!-- Job Title Header -->
    <header class="px-6 py-4 border-b border-slate-200 bg-gradient-to-r from-primary-600 to-primary-700">
      <h1 class="text-xl sm:text-2xl font-bold text-white">{{ job.title }}</h1>
    </header>

    <!-- Job Info Table -->
    <div class="divide-y divide-slate-200">
      <div 
        v-for="(field, index) in jobInfoFields" 
        :key="index"
        class="flex"
      >
        <!-- Label Column -->
        <div class="w-32 sm:w-40 flex-shrink-0 bg-primary-600 text-white px-4 py-3 flex items-center gap-2">
          <component :is="field.icon" class="w-5 h-5 flex-shrink-0" />
          <span class="font-medium text-sm">{{ field.label }}</span>
        </div>
        <!-- Value Column -->
        <div class="flex-1 px-4 py-3 bg-white text-slate-700">
          <template v-if="field.isLink">
            <a 
              :href="field.linkUrl" 
              target="_blank" 
              class="text-primary-600 hover:underline hover:text-primary-700"
            >
              {{ field.value }}
            </a>
          </template>
          <template v-else>
            {{ field.value || '-' }}
          </template>
        </div>
      </div>

      <!-- 條件資格 (Full Width Section) -->
      <div class="flex">
        <div class="w-32 sm:w-40 flex-shrink-0 bg-primary-600 text-white px-4 py-3 flex items-start gap-2">
          <DocumentTextIcon class="w-5 h-5 flex-shrink-0 mt-0.5" />
          <span class="font-medium text-sm">條件資格</span>
        </div>
        <div class="flex-1 px-4 py-3 bg-white text-slate-700 whitespace-pre-wrap leading-relaxed text-sm">
          {{ job.work_quality || '詳見簡章' }}
        </div>
      </div>
    </div>

    <!-- Additional Sections in Table Style -->
    <div class="divide-y divide-slate-200">
      <!-- Work Item -->
      <div class="flex">
        <div class="w-32 sm:w-40 flex-shrink-0 bg-primary-600 text-white px-4 py-3 flex items-start gap-2">
          <BriefcaseIcon class="w-5 h-5 flex-shrink-0 mt-0.5" />
          <span class="font-medium text-sm">工作項目</span>
        </div>
        <div class="flex-1 px-4 py-3 bg-white text-slate-700 whitespace-pre-wrap leading-relaxed text-sm">
          {{ job.work_item || '詳見簡章' }}
        </div>
      </div>

      <!-- Contact Method -->
      <div class="flex">
        <div class="w-32 sm:w-40 flex-shrink-0 bg-primary-600 text-white px-4 py-3 flex items-start gap-2">
          <UserIcon class="w-5 h-5 flex-shrink-0 mt-0.5" />
          <span class="font-medium text-sm">聯絡方式</span>
        </div>
        <div class="flex-1 px-4 py-3 bg-white text-slate-700 whitespace-pre-wrap leading-relaxed text-sm">
          {{ job.contact_method || '詳見簡章' }}
        </div>
      </div>

      <!-- History Job Openings -->
      <div class="flex">
        <div class="w-32 sm:w-40 flex-shrink-0 bg-primary-600 text-white px-4 py-3 flex items-start gap-2">
          <ClockIcon class="w-5 h-5 flex-shrink-0 mt-0.5" />
          <div class="flex items-center gap-1">
            <span class="font-medium text-sm">歷史開缺</span>
            <div class="group relative inline-block">
              <InformationCircleIcon class="w-4 h-4 text-white/70 cursor-help" />
              <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-56 p-2 bg-slate-800 text-white text-xs rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10 text-center">
                判斷標準：相同機關且相同工作內容的過去職缺
                <div class="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-slate-800"></div>
              </div>
            </div>
          </div>
        </div>
        <div class="flex-1 px-4 py-3 bg-white text-slate-700">
          <div v-if="historyJobs.length > 0" class="space-y-2">
            <div 
              v-for="historyJob in historyJobs" 
              :key="historyJob.id" 
              class="flex items-center justify-between p-2 bg-slate-50 border border-slate-200 rounded hover:border-primary-300 transition-colors group"
            >
              <div class="min-w-0">
                <div class="font-medium text-slate-800 text-sm group-hover:text-primary-700 truncate">{{ historyJob.title }}</div>
                <div class="flex items-center gap-1 text-xs text-slate-500 mt-0.5">
                  <CalendarIcon class="w-3 h-3" />
                  <span>{{ historyJob.date_from }} ~ {{ historyJob.date_to }}</span>
                </div>
              </div>
              <router-link 
                :to="{ name: 'job-details', params: { id: historyJob.id } }"
                class="flex-shrink-0 ml-3 px-2 py-1 bg-primary-50 border border-primary-200 text-primary-600 text-xs font-medium rounded hover:bg-primary-600 hover:text-white transition-colors"
              >
                檢視
              </router-link>
            </div>
          </div>
          <div v-else class="text-slate-400 text-sm">
            無歷史開缺資料
          </div>
        </div>
      </div>

      <!-- Action: View Original Site -->
      <div class="flex">
        <div class="w-32 sm:w-40 flex-shrink-0 bg-primary-600 text-white px-4 py-3 flex items-center gap-2">
          <ArrowTopRightOnSquareIcon class="w-5 h-5 flex-shrink-0" />
          <span class="font-medium text-sm">原始連結</span>
        </div>
        <div class="flex-1 px-4 py-3 bg-white flex items-center">
          <a 
            :href="job.view_url" 
            target="_blank" 
            class="text-primary-600 hover:underline hover:text-primary-700 text-sm font-medium"
          >
            前往事求人網站查看完整資訊 →
          </a>
        </div>
      </div>
    </div>
  </div>
</template>
