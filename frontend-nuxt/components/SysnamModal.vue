<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import BaseModal from './BaseModal.vue'
import { useJobConstants } from '@/composables/useJobConstants'

const props = defineProps<{
  modelValue: string
  isOpen: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'close'): void
}>()

const selectedSysnams = ref<Set<string>>(new Set())

// Initialize selected sysnams from props
watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    selectedSysnams.value = new Set(
      props.modelValue ? props.modelValue.split(',').map(s => s.trim()) : []
    )
  }
})

const toggleSysnam = (sysnam: string) => {
  const newSet = new Set(selectedSysnams.value)
  if (newSet.has(sysnam)) {
    newSet.delete(sysnam)
  } else {
    newSet.add(sysnam)
  }
  selectedSysnams.value = newSet
}

const clearSelection = () => {
  selectedSysnams.value = new Set()
}

const confirmSelection = () => {
  emit('update:modelValue', Array.from(selectedSysnams.value).join(', '))
  emit('close')
}

const { adminSysnams, techSysnams } = useJobConstants()

onMounted(() => {
})
</script>

<template>
  <BaseModal
    :is-open="isOpen"
    title="選擇職系"
    @close="$emit('close')"
  >
    <div class="space-y-6">
      <!-- Admin Sysnams -->
      <div>
        <h4 class="text-base font-bold text-slate-700 mb-3 flex items-center gap-2 sticky top-0 bg-white/95 backdrop-blur-sm z-10 py-1">
          <span class="w-1 h-5 bg-blue-500 rounded-full"></span>
          行政職系
        </h4>
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
          <button 
            type="button"
            v-for="sysnam in adminSysnams" 
            :key="sysnam"
            @click="toggleSysnam(sysnam)"
            class="px-3 py-2.5 rounded-lg text-base font-medium transition-all border"
            :class="selectedSysnams.has(sysnam) 
              ? 'bg-blue-50 text-blue-700 border-blue-200 shadow-sm ring-1 ring-blue-200' 
              : 'bg-white text-slate-600 border-slate-200 hover:border-blue-300 hover:bg-slate-50'"
          >
            {{ sysnam }}
          </button>
        </div>
      </div>

      <hr class="border-slate-100">

      <!-- Tech Sysnams -->
      <div>
        <h4 class="text-base font-bold text-slate-700 mb-3 flex items-center gap-2 sticky top-0 bg-white/95 backdrop-blur-sm z-10 py-1">
          <span class="w-1 h-5 bg-emerald-500 rounded-full"></span>
          技術職系
        </h4>
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
          <button 
            type="button"
            v-for="sysnam in techSysnams" 
            :key="sysnam"
            @click="toggleSysnam(sysnam)"
            class="px-3 py-2.5 rounded-lg text-base font-medium transition-all border"
            :class="selectedSysnams.has(sysnam) 
              ? 'bg-emerald-50 text-emerald-700 border-emerald-200 shadow-sm ring-1 ring-emerald-200' 
              : 'bg-white text-slate-600 border-slate-200 hover:border-emerald-300 hover:bg-slate-50'"
          >
            {{ sysnam }}
          </button>
        </div>
      </div>
    </div>

    <!-- Footer Slot -->
    <template #footer>
      <button 
        type="button" 
        class="w-full sm:w-auto inline-flex justify-center rounded-lg border border-slate-300 shadow-sm px-4 py-2.5 bg-white text-base font-medium text-slate-700 hover:bg-slate-50 focus:outline-none transition-colors"
        @click="$emit('close')"
      >
        關閉
      </button>
      <button 
        type="button" 
        class="w-full sm:w-auto inline-flex justify-center rounded-lg border border-red-200 shadow-sm px-4 py-2.5 bg-white text-base font-medium text-red-600 hover:bg-red-50 focus:outline-none transition-colors"
        @click="clearSelection"
      >
        清空
      </button>
      <button 
        type="button" 
        class="w-full sm:w-auto inline-flex justify-center rounded-lg border border-transparent shadow-sm px-6 py-2.5 bg-primary-600 text-base font-bold text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-all shadow-primary-500/20"
        @click="confirmSelection"
      >
        確定選取
      </button>
    </template>
  </BaseModal>
</template>

<style scoped>
/* Dummy style block to reset parser state */
</style>
