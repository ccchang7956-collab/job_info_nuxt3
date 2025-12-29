<script setup lang="ts">
import { XMarkIcon } from '@heroicons/vue/24/outline'

defineProps<{
  isOpen: boolean
  title: string
}>()

defineEmits<{
  (e: 'close'): void
}>()
</script>

<template>
  <Teleport to="body">
    <div v-if="isOpen" class="relative z-[9999]" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <!-- Backdrop -->
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="$emit('close')"></div>

      <!-- Modal Container -->
      <div class="fixed inset-0 z-10 overflow-y-auto pointer-events-none">
        <div class="flex min-h-full items-center justify-center p-4 text-center sm:p-0 pointer-events-auto">
          <!-- Modal Panel -->
          <div class="relative flex flex-col transform overflow-hidden rounded-xl bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-4xl max-h-[85vh]">
            
            <!-- Header -->
            <div class="bg-primary-600 px-4 py-3 border-b border-primary-700 flex-shrink-0">
              <div class="flex justify-between items-center">
                <slot name="header-title">
                  <h3 class="text-xl font-bold text-white" id="modal-title">{{ title }}</h3>
                </slot>
                <button type="button" @click="$emit('close')" class="text-blue-100 hover:text-white transition-colors p-1 rounded-full hover:bg-primary-500">
                  <span class="sr-only">Close</span>
                  <XMarkIcon class="h-6 w-6" />
                </button>
              </div>
            </div>

            <!-- Scrollable Content -->
            <div class="flex-1 overflow-y-auto bg-white px-4 py-4">
              <slot />
            </div>

            <!-- Footer -->
            <div class="bg-slate-50 px-4 py-3 sm:px-6 flex flex-col-reverse sm:flex-row sm:justify-end gap-2 flex-shrink-0 border-t border-slate-100">
              <slot name="footer" />
            </div>
            
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>
