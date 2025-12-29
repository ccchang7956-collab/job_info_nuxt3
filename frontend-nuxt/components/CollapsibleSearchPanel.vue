<script setup lang="ts">
import { ChevronDownIcon } from '@heroicons/vue/24/outline'

defineProps<{
  title: string
  modelValue: boolean
  hasActiveFilters?: boolean
}>()

defineEmits<{
  (e: 'update:modelValue', value: boolean): void
}>()
</script>

<template>
  <section 
    class="bg-white rounded-2xl shadow-sm border border-slate-200 mb-8 overflow-hidden transition-all duration-300 hover:shadow-md"
    :class="modelValue ? 'ring-2 ring-primary-100 border-primary-200' : ''"
  >
    <!-- Header / Toggle -->
    <div 
      @click="$emit('update:modelValue', !modelValue)"
      class="p-4 flex items-center justify-between cursor-pointer hover:bg-slate-50 transition-colors select-none"
    >
      <div class="flex items-center gap-3">
        <div class="bg-primary-50 p-2 rounded-lg text-primary-600">
          <slot name="icon"></slot>
        </div>
        <div>
          <h2 class="font-bold text-slate-800 text-lg">{{ title }}</h2>
          <!-- Active Filters Summary (Mobile/Collapsed) -->
          <div v-if="!modelValue && hasActiveFilters" class="flex flex-wrap gap-2 mt-1">
            <slot name="summary"></slot>
          </div>
          <div v-else-if="!modelValue" class="text-xs text-slate-400 mt-1">
            點擊展開{{ title }}...
          </div>
        </div>
      </div>
      <div class="text-slate-400">
        <ChevronDownIcon 
          class="w-5 h-5 transition-transform duration-300"
          :class="{ 'rotate-180': modelValue }"
        />
      </div>
    </div>
    
    <!-- Collapsible Content -->
    <div 
      v-show="modelValue" 
      class="border-t border-slate-100 p-6 bg-slate-50/50"
    >
      <slot></slot>
    </div>
  </section>
</template>
