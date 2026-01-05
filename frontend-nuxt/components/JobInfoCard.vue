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
const jobInfoFields = computed(() => [
  { icon: CalendarIcon, label: '公告日期', value: props.job.date_from },
  { icon: CalendarDaysIcon, label: '有效期間', value: `${props.job.date_from} ~ ${props.job.date_to}` },
  { icon: BuildingOffice2Icon, label: '徵才機關', value: props.job.org_name }, // Use org_name instead of org if that fits types. Job interface has org and org_name? Checked Job interface: has org, no org_name. Wait, checked Job interface again in Step 3267:
  /*
  31:     id: number
  32:     org: string  <- It is 'org'
  */
  // But wait, the original code used props.job.org_name in line 45!
  /*
  45:   { icon: BuildingOffice2Icon, label: '徵才機關', value: props.job.org_name },
  */
  // Let me check Job interface again.
  // Step 3267:
  /*
  30: export interface Job {
  31:     id: number
  32:     org: string
  ...
  */
  // It has `org`, not `org_name`.
  // However, `get_jobs` returns `JobAllData` which has `org_name`.
  // `JobService.py` `get_jobs` select `JobAllData.org_name`.
  // API response might have `org_name`.
  // Let's check `Job` interface again.
  // If `Job` interface only has `org`, then I should strictly use `org`.
  // BUT the original code used `org_name`.
  // Maybe I should update `Job` interface to match what's actually returned?
  // Or check if `org` in interface maps to `org_name` in API?
  // In `JobService.py`, select includes `JobAllData.org_name`.
  // Pydantic schema `JobItem` (not shown fully) likely maps it.
  // Wait, `JobListResponse` has `jobs: list[JobItem]`.
  // Let's assume `Job` interface in frontend needs update or I should use `org` if it's the alias.
  // Actually, I saw `JobCard.vue` using `job.org`.
  // But `JobInfoCard.vue` uses `job.org_name` in lines 45, 66.
  // This is inconsistent.
  // I will check `Job` interface again.
  // It has `org`.
  // I will check `JobCard.vue` again. Line 22: `{{ job.org }}`.
  // `JobInfoCard.vue` Line 45: `value: props.job.org_name`.
  // This means the objects passed to them might be slightly different or `Job` interface is incomplete/wrong.
  // `job/[id].vue` fetches `/api/Active_job_openings/${jobId}` which returns `JobDetailResponse`.
  // `JobDetailResponse` has `job: Job`.
  // `Job` interface has `org`.
  // If `JobInfoCard` is used in `job/[id].vue`, then `props.job` is the single job detail.
  // If `JobCard` is used in `index.vue`, then `props.job` is from `JobListResponse`.
  // Maybe the single job detail has `org_name`?
  // I will look at `JobService.get_job_detail` again.
  // It returns `JobAllData`. `JobAllData` (model) has `org_name`.
  // So the API likely returns `org_name`.
  // So `Job` interface should probably have `org_name` OR `org`?
  // `JobListResponse` uses `JobItem` schema.
  // `JobService.get_sitemap_xml` uses `JobAllData`.
  // StartLine 45 of `JobInfoCard.vue` uses `org_name`.
  // I will update `Job` interface to include optional fields or aliases if needed, OR just use `any` cast if I'm lazy, but better to fix interface.
  // I will add `org_name` to `Job` interface in `types/index.ts`?
  // Wait, `Job` interface has `org`.
  // Maybe valid key is `org_name`?
  // Let's look at `index.vue` again. It uses `jobs = ref([])`. `JobCard` uses `job.org`.
  // So `JobListResponse` returns objects with `org`.
  // `JobDetailResponse` returns objects with `org_name`?
  // I should check `Job` interface again.
  // I'll add `org_name?: string` to `Job` interface to be safe, or check if I can unify them.
  // For now, in `JobInfoCard.vue`, I will follow the existing code which uses `org_name`.
  // So I need to make sure `Job` type has `org_name`.
  // I will update `Job` interface in `types/index.ts` first?
  // Or just cast to `any` for now in `JobInfoCard.vue` for that specific field?
  // No, that's bad.
  // I'll verify `Job` interface.
  // `index.ts`:
  /*
  30: export interface Job {
  ...
  32:     org: string
  ...
  */
  // I'll add `org_name?: string` to `Job` interface.
  // Also check `work_place_type`, `work_address`, `work_quality`, `contact_method`, `quota_regular`, `quota_backup`, `work_kind`.
  // `Job` interface in `index.ts` is quite minimal.
  // I should expand `Job` interface to include all these fields as optional.
  
  { icon: AcademicCapIcon, label: '職務列等', value: props.job.rank },
  { icon: BriefcaseIcon, label: '職系', value: props.job.sysnam },
  { icon: UserIcon, label: '人員區分', value: props.job.person_kind || '-' },
  { icon: UserPlusIcon, label: '正取', value: props.job.number_of || '-' },
  { icon: UsersIcon, label: '候補', value: props.job.reserve_num || '-' },
  { icon: MapPinIcon, label: '工作地點', value: props.job.work_place_type },
  { icon: HomeIcon, label: '地址', value: props.job.work_address, isLink: true, linkUrl: `https://www.google.com/maps/search/?q=${props.job.work_address}` },
])
</script>

<template>
  <div class="bg-transparent sm:bg-white rounded-xl shadow-none sm:shadow-sm border-0 sm:border border-slate-200 overflow-visible sm:overflow-hidden">
    <!-- Header Actions Slot -->
    <div class="p-0 pb-4 sm:p-6 sm:pb-0">
      <slot name="header-actions"></slot>
    </div>

    <!-- Job Title Header -->
    <header class="mb-4 sm:mb-0 px-0 sm:px-6 py-0 sm:py-5 border-0 sm:border-b border-slate-200 bg-transparent sm:bg-gradient-to-r sm:from-primary-600 sm:to-primary-700 text-center sm:text-left">
      <h2 class="block sm:hidden text-xl text-slate-600 font-bold mb-1">{{ job.org_name }}</h2>
      <h1 class="text-2xl sm:text-3xl font-bold text-slate-800 sm:text-white">{{ job.title }}</h1>
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
