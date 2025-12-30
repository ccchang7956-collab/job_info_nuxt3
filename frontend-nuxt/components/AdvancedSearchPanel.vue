<script setup lang="ts">
import { 
  MagnifyingGlassIcon,
  XMarkIcon,
  ChevronDownIcon,
  Bars3Icon,
  AdjustmentsHorizontalIcon
} from '@heroicons/vue/24/outline'

interface Props {
  // Quick search
  quickSearchValue: string
  quickSearchPlaceholder?: string
  
  // Panel state
  isExpanded: boolean
  hasActiveFilters: boolean
  
  // Optional features
  showQuickSearch?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  quickSearchPlaceholder: '快速搜尋...',
  showQuickSearch: true
})

const emit = defineEmits<{
  (e: 'update:quickSearchValue', value: string): void
  (e: 'update:isExpanded', value: boolean): void
  (e: 'search'): void
  (e: 'clear'): void
}>()

const localQuickSearch = computed({
  get: () => props.quickSearchValue,
  set: (val) => emit('update:quickSearchValue', val)
})

const localIsExpanded = computed({
  get: () => props.isExpanded,
  set: (val) => emit('update:isExpanded', val)
})

const toggleExpanded = () => {
  localIsExpanded.value = !localIsExpanded.value
}

const handleSearch = () => {
  emit('search')
}

const handleClear = () => {
  emit('clear')
}
</script>

<template>
  <div class="mb-6">
    <!-- Quick Search Row -->
    <div class="flex flex-col sm:flex-row gap-3 items-stretch sm:items-center">
      <!-- Quick Search Input -->
      <div v-if="showQuickSearch" class="flex-1 relative">
        <MagnifyingGlassIcon class="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
        <input 
          v-model="localQuickSearch"
          type="text" 
          :placeholder="quickSearchPlaceholder" 
          class="w-full pl-10 pr-4 py-3 bg-white border border-slate-200 rounded-xl focus:ring-2 focus:ring-primary-100 focus:border-primary-500 outline-none transition-all text-base shadow-sm"
          @keyup.enter="handleSearch"
        >
      </div>
      
      <!-- Action Buttons -->
      <div class="flex gap-2">
        <button 
          type="button"
          @click="toggleExpanded" 
          class="flex items-center gap-2 px-4 py-3 bg-white border border-slate-200 text-slate-600 rounded-xl font-medium transition-all hover:bg-slate-50 shadow-sm"
          :class="{ 'bg-primary-50 border-primary-200 text-primary-700': hasActiveFilters || isExpanded }"
        >
          <AdjustmentsHorizontalIcon class="w-5 h-5" />
          <span>進階篩選</span>
          <ChevronDownIcon class="w-4 h-4 transition-transform" :class="{ 'rotate-180': isExpanded }" />
        </button>
        <button 
          type="button"
          @click="handleSearch" 
          class="flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white px-5 py-3 rounded-xl font-medium transition-colors shadow-sm"
        >
          <MagnifyingGlassIcon class="w-5 h-5" />
          <span class="hidden sm:inline">搜尋</span>
        </button>
      </div>
    </div>

    <!-- Active Filters Tags Slot -->
    <div v-if="hasActiveFilters && !isExpanded && $slots.activeTags" class="flex flex-wrap gap-2 mt-3">
      <slot name="activeTags" />
    </div>

    <!-- Advanced Filters Panel -->
    <div v-show="isExpanded" class="mt-4 p-5 bg-white border border-slate-200 rounded-xl shadow-sm">
      <!-- Filters Content Slot -->
      <slot name="filters" />
      
      <!-- Action Buttons Row -->
      <div class="flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-slate-100 mt-4">
        <!-- Extra Controls Slot (toggles, etc.) -->
        <div>
          <slot name="extraControls" />
        </div>
        
        <!-- Search & Clear Buttons -->
        <div class="flex items-center gap-3">
          <button 
            type="button"
            @click="handleClear" 
            class="flex items-center gap-2 bg-white hover:bg-slate-50 text-slate-600 border border-slate-200 px-4 py-2.5 rounded-lg font-medium transition-colors shadow-sm hover:shadow active:scale-95 transform duration-100"
          >
            <XMarkIcon class="w-5 h-5" />
            清空
          </button>
          <button 
            type="button"
            @click="handleSearch" 
            class="flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white px-6 py-2.5 rounded-lg font-medium transition-colors shadow-sm hover:shadow active:scale-95 transform duration-100"
          >
            <MagnifyingGlassIcon class="w-5 h-5" />
            搜尋
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
