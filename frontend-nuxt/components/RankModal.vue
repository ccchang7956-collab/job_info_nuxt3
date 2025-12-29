<script setup lang="ts">
import { ref, watch } from 'vue'
import BaseModal from './BaseModal.vue'

const props = defineProps<{
  minRank: number | string | null
  maxRank: number | string | null
  isOpen: boolean
}>()

const emit = defineEmits<{
  (e: 'update:minRank', value: number | null): void
  (e: 'update:maxRank', value: number | null): void
  (e: 'close'): void
}>()

const localMin = ref<number | null>(null)
const localMax = ref<number | null>(null)

// Initialize from props
watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    localMin.value = props.minRank ? parseInt(String(props.minRank)) : null
    localMax.value = props.maxRank ? parseInt(String(props.maxRank)) : null
  }
})

const ranks = Array.from({ length: 14 }, (_, i) => i + 1)

const selectRank = (rank: number) => {
  if (localMin.value === null && localMax.value === null) {
    // First selection
    localMin.value = rank
    localMax.value = rank
  } else if (localMin.value !== null && localMax.value !== null && localMin.value === localMax.value) {
    // Second selection
    if (rank < localMin.value) {
      localMin.value = rank
    } else {
      localMax.value = rank
    }
  } else {
    // Reset and start new selection
    localMin.value = rank
    localMax.value = rank
  }
}

const isSelected = (rank: number) => {
  if (localMin.value === null || localMax.value === null) return false
  return rank >= localMin.value && rank <= localMax.value
}

const isEndpoint = (rank: number) => {
  return rank === localMin.value || rank === localMax.value
}

const confirmSelection = () => {
  emit('update:minRank', localMin.value)
  emit('update:maxRank', localMax.value)
  emit('close')
}

const clearSelection = () => {
  localMin.value = null
  localMax.value = null
}
</script>

<template>
  <BaseModal
    :is-open="isOpen"
    title="選擇職等範圍"
    @close="$emit('close')"
  >
    <div class="px-4 py-4 sm:p-6">
      <div class="space-y-4">
        <p class="text-base text-slate-500">請點選起始與結束職等（可單選）</p>
        
        <div class="grid grid-cols-5 gap-3">
          <button 
            type="button"
            v-for="rank in ranks" 
            :key="rank"
            @click="selectRank(rank)"
            class="aspect-square flex items-center justify-center rounded-lg text-xl font-bold transition-all border-2"
            :class="[
              isEndpoint(rank) 
                ? 'bg-primary-600 text-white border-primary-600 scale-105 shadow-md z-10' 
                : isSelected(rank)
                  ? 'bg-primary-50 text-primary-700 border-primary-200'
                  : 'bg-white text-slate-600 border-slate-200 hover:border-primary-300 hover:bg-slate-50'
            ]"
          >
            {{ rank }}
          </button>
        </div>
        
        <div class="mt-2 text-center h-6">
          <span v-if="localMin && localMax" class="text-primary-700 font-bold bg-primary-50 px-3 py-1 rounded-full text-base">
            已選擇：{{ localMin }} ~ {{ localMax }} 職等
          </span>
        </div>
      </div>
    </div>

    <!-- Footer Slot -->
    <template #footer>
      <button 
        type="button" 
        class="w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:ml-3 sm:w-auto sm:text-sm"
        @click="$emit('close')"
      >
        取消
      </button>
      <button 
        type="button" 
        class="mt-3 w-full inline-flex justify-center rounded-md border border-red-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-red-700 hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:mt-0 sm:ml-3 sm:w-auto"
        @click="clearSelection"
      >
        清空
      </button>
      <button 
        type="button" 
        class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-primary-600 text-base font-medium text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:ml-3 sm:w-auto"
        @click="confirmSelection"
      >
        確定
      </button>
    </template>
  </BaseModal>
</template>
