<script setup>
import { useToast } from '../composables/useToast'
import { XMarkIcon, CheckCircleIcon, ExclamationCircleIcon, InformationCircleIcon } from '@heroicons/vue/24/outline'

const { toasts, removeToast } = useToast()

const getIcon = (type) => {
  switch (type) {
    case 'success': return CheckCircleIcon
    case 'error': return ExclamationCircleIcon
    default: return InformationCircleIcon
  }
}

const getClasses = (type) => {
  switch (type) {
    case 'success': return 'bg-emerald-50 text-emerald-800 border-emerald-200'
    case 'error': return 'bg-red-50 text-red-800 border-red-200'
    default: return 'bg-blue-50 text-blue-800 border-blue-200'
  }
}
</script>

<template>
  <Teleport to="body">
    <div class="fixed top-4 left-1/2 -translate-x-1/2 z-[10000] flex flex-col gap-2 pointer-events-none items-center w-full max-w-md px-4">
      <TransitionGroup 
        enter-active-class="transform ease-out duration-300 transition" 
        enter-from-class="-translate-y-2 opacity-0" 
        enter-to-class="translate-y-0 opacity-100" 
        leave-active-class="transition ease-in duration-100" 
        leave-from-class="opacity-100" 
        leave-to-class="opacity-0"
      >
        <div 
          v-for="toast in toasts" 
          :key="toast.id" 
          class="pointer-events-auto w-full overflow-hidden rounded-lg border shadow-lg ring-1 ring-black ring-opacity-5"
          :class="getClasses(toast.type)"
        >
          <div class="p-4">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <component :is="getIcon(toast.type)" class="h-6 w-6" aria-hidden="true" />
              </div>
              <div class="ml-3 flex-1 pt-0.5">
                <p class="text-sm font-medium whitespace-nowrap">{{ toast.message }}</p>
              </div>
              <div class="ml-4 flex flex-shrink-0">
                <button 
                  type="button" 
                  @click="removeToast(toast.id)"
                  class="inline-flex rounded-md p-1.5 focus:outline-none focus:ring-2 focus:ring-offset-2"
                  :class="[
                    toast.type === 'success' ? 'text-emerald-500 hover:bg-emerald-100 focus:ring-emerald-600' : 
                    toast.type === 'error' ? 'text-red-500 hover:bg-red-100 focus:ring-red-600' : 
                    'text-blue-500 hover:bg-blue-100 focus:ring-blue-600'
                  ]"
                >
                  <span class="sr-only">Close</span>
                  <XMarkIcon class="h-5 w-5" aria-hidden="true" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>
