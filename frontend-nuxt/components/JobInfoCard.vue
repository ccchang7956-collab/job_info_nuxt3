<script setup lang="ts">
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
import type { Job } from '@/types'

const props = defineProps<{
  job: Job
  duplicates?: Job[]
}>()

// Filter and sort duplicates (legacy logic: date_from < current job's date_from)
const historyJobs = computed(() => {
  if (!props.duplicates || props.duplicates.length === 0) return []
  
  const currentJobDate = props.job.date_from
  return props.duplicates
    .filter(d => d.date_from < currentJobDate)
    .sort((a, b) => b.date_from.localeCompare(a.date_from))
})

// 職缺資訊欄位定義
const jobInfoFields = computed(() => {
  let cleanPlace = String(props.job.place || props.job.work_address || '臺北市')
    .replace(/^[\s,]*\d*-?/, '')
    .split(',')[0]
    .trim()
    .replace('台', '臺')

  const match = cleanPlace.match(/^[^縣市]+[縣市]/)
  if (match) {
    cleanPlace = match[0]
  }

  const sysnamValue = props.job.sysnam ? String(props.job.sysnam).trim() : ''

  return [
    { icon: CalendarIcon, label: '公告日期', value: props.job.date_from },
    { icon: CalendarDaysIcon, label: '有效期間', value: `${props.job.date_from} ~ ${props.job.date_to}` },
    { icon: BuildingOffice2Icon, label: '徵才機關', value: props.job.org_name },
    { icon: AcademicCapIcon, label: '職務列等', value: props.job.rank },
    { 
      icon: BriefcaseIcon, 
      label: '職系', 
      value: props.job.sysnam,
      isRouterLink: !!sysnamValue,
      linkUrl: sysnamValue ? `/sysnams/${encodeURIComponent(sysnamValue.toLowerCase())}` : '',
      customClass: 'inline-flex items-center px-2.5 py-1 rounded text-sm font-bold bg-primary-50 text-primary-700 border border-primary-200 hover:bg-primary-100 transition-colors'
    },
    { icon: UserIcon, label: '人員區分', value: props.job.person_kind || '-' },
    { icon: UserPlusIcon, label: '正取', value: props.job.number_of || '-' },
    { icon: UsersIcon, label: '候補', value: props.job.reserve_num || '-' },
    { 
      icon: MapPinIcon, 
      label: '工作地點', 
      value: cleanPlace || props.job.place || '臺北市',
      isRouterLink: !!cleanPlace,
      linkUrl: cleanPlace ? `/places/${encodeURIComponent(cleanPlace.toLowerCase())}` : '',
      customClass: 'text-primary-600 hover:underline hover:text-primary-700 font-medium'
    },
    { icon: HomeIcon, label: '地址', value: props.job.work_address, isLink: true, linkUrl: `https://www.google.com/maps/search/?q=${props.job.work_address}` },
  ]
})
</script>

<template>
  <div class="bg-transparent sm:bg-white rounded-xl shadow-none sm:shadow-sm border-0 sm:border border-slate-200 overflow-visible sm:overflow-hidden">
    <!-- Header Actions Slot -->
    <div class="p-0 pb-4 sm:p-6 sm:pb-0">
      <slot name="header-actions"></slot>
    </div>

    <!-- Job Title Header -->
    <header class="mb-4 sm:mb-0 px-0 sm:px-6 py-0 sm:py-5 border-0 sm:border-b border-slate-200 bg-transparent sm:bg-gradient-to-r sm:from-primary-600 sm:to-primary-700 text-center sm:text-left">
      <h2 class="block sm:hidden text-2xl sm:text-3xl font-bold text-slate-800 mb-2">{{ job.org_name }}</h2>
      <h1 class="text-2xl sm:text-3xl font-bold text-slate-800 sm:text-white">
        <span class="hidden sm:inline mr-2">{{ job.org_name }}</span>{{ job.title }}
      </h1>
    </header>

    <!-- Job Info Table -->
    <div class="flex flex-col gap-3 sm:gap-0 sm:block sm:divide-y sm:divide-slate-200">
      <div 
        v-for="(field, index) in jobInfoFields" 
        :key="index"
        class="flex flex-col sm:flex-row bg-white sm:bg-transparent rounded-lg sm:rounded-none border border-slate-200 sm:border-0 shadow-sm sm:shadow-none overflow-hidden sm:overflow-visible"
        v-show="!(index === 2)" 
      >
        <!-- Label Column -->
        <div class="w-full sm:w-36 sm:w-44 flex-shrink-0 bg-primary-600 text-white px-4 py-3 sm:py-4 flex items-center gap-2 border-b border-slate-100 sm:border-0">
          <component :is="field.icon" class="w-5 h-5 flex-shrink-0 text-white" />
          <span class="font-bold sm:font-medium text-lg sm:text-base">{{ field.label }}</span>
        </div>
        <!-- Value Column -->
        <div class="flex-1 px-4 py-3 sm:py-4 bg-white text-slate-700 text-base sm:text-base">
          <template v-if="field.isLink">
            <a 
              :href="field.linkUrl" 
              target="_blank" 
              class="text-primary-600 hover:underline hover:text-primary-700 break-words"
            >
              {{ field.value }}
            </a>
          </template>
          <template v-else-if="field.isRouterLink">
            <NuxtLink 
              :to="field.linkUrl" 
              :class="field.customClass || 'text-primary-600 hover:underline hover:text-primary-700 break-words'"
            >
              {{ field.value }}
            </NuxtLink>
          </template>
          <template v-else>
            {{ field.value || '-' }}
          </template>
        </div>
      </div>

      <!-- 條件資格 (Full Width Section) -->
      <div class="flex flex-col sm:flex-row bg-white sm:bg-transparent rounded-lg sm:rounded-none border border-slate-200 sm:border-0 shadow-sm sm:shadow-none overflow-hidden sm:overflow-visible">
        <div class="w-full sm:w-36 sm:w-44 flex-shrink-0 bg-primary-600 text-white px-4 py-3 sm:py-4 flex items-start gap-2 border-b border-slate-100 sm:border-0">
          <DocumentTextIcon class="w-5 h-5 flex-shrink-0 mt-1 sm:mt-0.5 text-white" />
          <span class="font-bold sm:font-medium text-lg sm:text-base">條件資格</span>
        </div>
        <div class="flex-1 px-4 py-3 sm:py-4 bg-white text-slate-700 whitespace-pre-wrap leading-relaxed text-base sm:text-base">
          {{ job.work_quality || '詳見簡章' }}
        </div>
      </div>
    
      <!-- Work Item -->
      <div class="flex flex-col sm:flex-row bg-white sm:bg-transparent rounded-lg sm:rounded-none border border-slate-200 sm:border-0 shadow-sm sm:shadow-none overflow-hidden sm:overflow-visible">
        <div class="w-full sm:w-36 sm:w-44 flex-shrink-0 bg-primary-600 text-white px-4 py-3 sm:py-4 flex items-start gap-2 border-b border-slate-100 sm:border-0">
          <BriefcaseIcon class="w-5 h-5 flex-shrink-0 mt-1 sm:mt-0.5 text-white" />
          <span class="font-bold sm:font-medium text-lg sm:text-base">工作項目</span>
        </div>
        <div class="flex-1 px-4 py-3 sm:py-4 bg-white text-slate-700 whitespace-pre-wrap leading-relaxed text-base sm:text-base">
          {{ job.work_item || '詳見簡章' }}
        </div>
      </div>

      <!-- Contact Method -->
      <div class="flex flex-col sm:flex-row bg-white sm:bg-transparent rounded-lg sm:rounded-none border border-slate-200 sm:border-0 shadow-sm sm:shadow-none overflow-hidden sm:overflow-visible">
        <div class="w-full sm:w-36 sm:w-44 flex-shrink-0 bg-primary-600 text-white px-4 py-3 sm:py-4 flex items-start gap-2 border-b border-slate-100 sm:border-0">
          <UserIcon class="w-5 h-5 flex-shrink-0 mt-1 sm:mt-0.5 text-white" />
          <span class="font-bold sm:font-medium text-lg sm:text-base">聯絡方式</span>
        </div>
        <div class="flex-1 px-4 py-3 sm:py-4 bg-white text-slate-700 whitespace-pre-wrap leading-relaxed text-base sm:text-base">
          {{ job.contact_method || '詳見簡章' }}
        </div>
      </div>

      <!-- History Job Openings -->
      <div class="flex flex-col sm:flex-row bg-white sm:bg-transparent rounded-lg sm:rounded-none border border-slate-200 sm:border-0 shadow-sm sm:shadow-none overflow-hidden sm:overflow-visible">
        <div class="w-full sm:w-36 sm:w-44 flex-shrink-0 bg-primary-600 text-white px-4 py-3 sm:py-4 flex items-start gap-2 border-b border-slate-100 sm:border-0">
          <ClockIcon class="w-5 h-5 flex-shrink-0 mt-1 sm:mt-0.5 text-white" />
          <div class="flex items-center gap-1">
            <span class="font-bold sm:font-medium text-lg sm:text-base">歷史開缺</span>
            <div class="group relative inline-block">
              <InformationCircleIcon class="w-4 h-4 text-slate-400 sm:text-white/70 cursor-help" />
              <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-56 p-2 bg-slate-800 text-white text-sm rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10 text-center">
                判斷標準：相同機關且相同工作內容的過去職缺
                <div class="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-slate-800"></div>
              </div>
            </div>
          </div>
        </div>
        <div class="flex-1 px-4 py-3 sm:py-4 bg-white text-slate-700">
          <div v-if="historyJobs.length > 0" class="space-y-2">
            <div 
              v-for="historyJob in historyJobs" 
              :key="historyJob.id" 
              class="flex items-center justify-between p-3 bg-slate-50 border border-slate-200 rounded hover:border-primary-300 transition-colors group"
            >
              <div class="min-w-0">
                <div class="font-medium text-slate-800 text-base group-hover:text-primary-700 truncate">{{ historyJob.title }}</div>
                <div class="flex items-center gap-1 text-sm text-slate-500 mt-0.5">
                  <CalendarIcon class="w-4 h-4" />
                  <span>{{ historyJob.date_from }} ~ {{ historyJob.date_to }}</span>
                </div>
              </div>
              <router-link 
                :to="`/job/${historyJob.id}`"
                class="flex-shrink-0 ml-3 px-3 py-1.5 bg-primary-50 border border-primary-200 text-primary-600 text-sm font-medium rounded hover:bg-primary-600 hover:text-white transition-colors"
              >
                檢視
              </router-link>
            </div>
          </div>
          <div v-else class="text-slate-400 text-base">
            無歷史開缺資料
          </div>
        </div>
      </div>

      <!-- Action: View Original Site -->
      <div class="flex flex-col sm:flex-row bg-white sm:bg-transparent rounded-lg sm:rounded-none border border-slate-200 sm:border-0 shadow-sm sm:shadow-none overflow-hidden sm:overflow-visible">
        <div class="w-full sm:w-36 sm:w-44 flex-shrink-0 bg-primary-600 text-white px-4 py-3 sm:py-4 flex items-center gap-2 border-b border-slate-100 sm:border-0">
          <ArrowTopRightOnSquareIcon class="w-5 h-5 flex-shrink-0 text-white" />
          <span class="font-bold sm:font-medium text-lg sm:text-base">原始連結</span>
        </div>
        <div class="flex-1 px-4 py-3 sm:py-4 bg-white flex items-center">
          <a 
            :href="job.view_url" 
            target="_blank" 
            class="text-primary-600 hover:underline hover:text-primary-700 text-base font-medium break-all"
          >
            前往事求人網站查看完整資訊 →
          </a>
        </div>
      </div>
    </div>
  </div>
</template>
