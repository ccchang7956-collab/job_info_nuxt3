<script setup lang="ts">
import { XMarkIcon } from '@heroicons/vue/24/outline'

interface Props {
  label: string
  value: string
  variant?: 'default' | 'info' | 'danger'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default'
})

const emit = defineEmits<{
  (e: 'remove'): void
}>()

const variantClasses = computed(() => {
  switch (props.variant) {
    case 'info':
      return 'bg-blue-50 text-blue-600'
    case 'danger':
      return 'bg-red-50 text-red-600'
    default:
      return 'bg-slate-100 text-slate-600'
  }
})
</script>

<template>
  <span 
    class="text-xs px-2 py-1 rounded-full flex items-center gap-1"
    :class="variantClasses"
  >
    <template v-if="label">{{ label }}: </template>{{ value }}
    <button 
      type="button"
      @click="emit('remove')" 
      class="hover:text-red-500 transition-colors"
    >
      <XMarkIcon class="w-3 h-3" />
    </button>
  </span>
</template>
