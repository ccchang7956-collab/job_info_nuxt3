<script setup lang="ts">
import { 
  ChevronLeftIcon,
  ChevronRightIcon
} from '@heroicons/vue/24/outline'

interface Props {
  currentPage: number
  totalPages: number
  perPage?: number
  showPerPage?: boolean
  showJumpTo?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  perPage: 15,
  showPerPage: true,
  showJumpTo: true
})

const emit = defineEmits<{
  (e: 'update:currentPage', page: number): void
  (e: 'update:perPage', perPage: number): void
}>()

const { addToast } = useToast()

// Local state for jump input
const jumpPage = ref('')
const localPerPage = ref(props.perPage)

// Sync local perPage with prop
watch(() => props.perPage, (val) => {
  localPerPage.value = val
})

const changePage = (page: number) => {
  if (page >= 1 && page <= props.totalPages) {
    emit('update:currentPage', page)
  }
}

const handleJumpPage = () => {
  const page = parseInt(jumpPage.value)
  if (page && page >= 1 && page <= props.totalPages) {
    changePage(page)
    jumpPage.value = ''
  } else {
    addToast('請輸入有效的頁碼', 'error')
  }
}

const handlePerPageChange = () => {
  emit('update:perPage', localPerPage.value)
  emit('update:currentPage', 1) // Reset to first page
}

// Computed for per-page options
const perPageOptions = [15, 30, 50, 100]
</script>

<template>
  <div 
    v-if="totalPages > 1"
    class="flex flex-col sm:flex-row justify-center items-center gap-4"
  >
    <!-- Page Controls -->
    <div class="flex items-center gap-2">
      <NuxtLink 
        v-if="currentPage > 1"
        :to="{ query: { ...$route.query, page: currentPage - 1 } }"
        @click.prevent="changePage(currentPage - 1)"
        class="p-2 flex items-center justify-center rounded-lg border border-slate-200 hover:bg-white hover:border-primary-300 hover:text-primary-600 transition-all bg-white"
        aria-label="上一頁"
      >
        <ChevronLeftIcon class="w-5 h-5" />
      </NuxtLink>
      <button 
        v-else
        type="button"
        disabled 
        class="p-2 flex items-center justify-center rounded-lg border border-slate-200 disabled:opacity-50 disabled:cursor-not-allowed transition-all bg-white"
      >
        <ChevronLeftIcon class="w-5 h-5" />
      </button>
      
      <span class="text-sm font-medium text-slate-600 bg-white px-4 py-2 rounded-lg border border-slate-200 shadow-sm whitespace-nowrap">
        第 {{ currentPage }} 頁 / 共 {{ totalPages }} 頁
      </span>
      
      <NuxtLink 
        v-if="currentPage < totalPages"
        :to="{ query: { ...$route.query, page: currentPage + 1 } }"
        @click.prevent="changePage(currentPage + 1)"
        class="p-2 flex items-center justify-center rounded-lg border border-slate-200 hover:bg-white hover:border-primary-300 hover:text-primary-600 transition-all bg-white"
        aria-label="下一頁"
      >
        <ChevronRightIcon class="w-5 h-5" />
      </NuxtLink>
      <button 
        v-else
        type="button"
        disabled 
        class="p-2 flex items-center justify-center rounded-lg border border-slate-200 disabled:opacity-50 disabled:cursor-not-allowed transition-all bg-white"
      >
        <ChevronRightIcon class="w-5 h-5" />
      </button>
    </div>

    <!-- Settings -->
    <div class="flex items-center gap-4">
      <!-- Per Page -->
      <div v-if="showPerPage" class="flex items-center gap-2">
        <span class="text-sm text-slate-500">每頁顯示</span>
        <select 
          v-model="localPerPage" 
          @change="handlePerPageChange"
          class="bg-white border border-slate-200 text-slate-700 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block p-2 outline-none"
        >
          <option v-for="opt in perPageOptions" :key="opt" :value="opt">{{ opt }}</option>
        </select>
        <span class="text-sm text-slate-500">筆</span>
      </div>

      <!-- Jump To -->
      <div v-if="showJumpTo" class="flex items-center gap-2">
        <span class="text-sm text-slate-500">跳至</span>
        <input 
          v-model="jumpPage" 
          type="number" 
          min="1" 
          :max="totalPages"
          class="w-16 bg-white border border-slate-200 text-slate-700 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block p-2 outline-none text-center"
          @keyup.enter="handleJumpPage"
        >
        <span class="text-sm text-slate-500">頁</span>
        <button 
          type="button"
          @click="handleJumpPage"
          class="px-3 py-2 text-sm font-medium text-primary-600 bg-primary-50 rounded-lg hover:bg-primary-100 transition-colors"
        >
          GO
        </button>
      </div>
    </div>
  </div>
</template>
