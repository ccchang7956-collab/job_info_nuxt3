<script setup>
import { ref, watch } from 'vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  isOpen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'close'])

const selectedPlaces = ref(new Set())

// Initialize selected places from props
watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    selectedPlaces.value = new Set(
      props.modelValue ? props.modelValue.split(',').map(s => s.trim()) : []
    )
  }
})

const togglePlace = (place) => {
  const newSet = new Set(selectedPlaces.value)
  if (newSet.has(place)) {
    newSet.delete(place)
  } else {
    newSet.add(place)
  }
  selectedPlaces.value = newSet
}

const toggleRegion = (places) => {
  const placesArr = places.split(',')
  const newSet = new Set(selectedPlaces.value)
  const allSelected = placesArr.every(p => newSet.has(p))
  
  if (allSelected) {
    placesArr.forEach(p => newSet.delete(p))
  } else {
    placesArr.forEach(p => newSet.add(p))
  }
  selectedPlaces.value = newSet
}

const clearSelection = () => {
  selectedPlaces.value = new Set()
}

const confirmSelection = () => {
  emit('update:modelValue', Array.from(selectedPlaces.value).join(', '))
  emit('close')
}

const regions = [
  {
    name: '北北基地區',
    places: ['臺北市', '新北市', '基隆市']
  },
  {
    name: '桃竹苗地區',
    places: ['桃園市', '新竹縣', '新竹市', '苗栗縣']
  },
  {
    name: '中彰投地區',
    places: ['臺中市', '彰化縣', '南投縣']
  },
  {
    name: '雲嘉南地區',
    places: ['雲林縣', '嘉義縣', '嘉義市', '臺南市']
  },
  {
    name: '高屏地區',
    places: ['高雄市', '屏東縣']
  },
  {
    name: '宜花東地區',
    places: ['宜蘭縣', '花蓮縣', '臺東縣']
  },
  {
    name: '離島地區',
    places: ['澎湖縣', '金門縣', '連江縣']
  }
]
</script>

<template>
  <Teleport to="body">
    <div v-if="isOpen" class="relative z-[9999]" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <!-- Backdrop -->
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>

      <!-- Modal Container -->
      <div class="fixed inset-0 z-10 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4 text-center sm:p-0">
          <!-- Modal Panel -->
          <div class="relative flex flex-col transform overflow-hidden rounded-xl bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-2xl max-h-[85vh]" @click.stop>
            
            <!-- Header -->
            <div class="bg-white px-4 py-3 border-b border-slate-100 flex-shrink-0">
              <div class="flex justify-between items-center">
                <h3 class="text-lg font-bold text-slate-800" id="modal-title">選擇地點</h3>
                <button type="button" @click="$emit('close')" class="text-slate-400 hover:text-slate-600 transition-colors p-1 rounded-full hover:bg-slate-100">
                  <XMarkIcon class="h-5 w-5" />
                </button>
              </div>
            </div>

            <!-- Scrollable Content -->
            <div class="flex-1 overflow-y-auto bg-white px-4 py-4">
              <div class="space-y-5">
                <div v-for="(region, index) in regions" :key="index">
                  <div class="flex items-center justify-between mb-2 sticky top-0 bg-white/95 backdrop-blur-sm z-10 py-1">
                    <h6 class="text-sm font-bold text-slate-700 flex items-center gap-2">
                      <span class="w-1 h-4 bg-primary-500 rounded-full"></span>
                      {{ region.name }}
                    </h6>
                    <button 
                      type="button"
                      @click="toggleRegion(region.places.join(','))"
                      class="text-xs font-medium px-2 py-0.5 rounded border border-primary-200 text-primary-600 hover:bg-primary-50 transition-colors"
                    >
                      全選
                    </button>
                  </div>
                  <div class="grid grid-cols-3 sm:grid-cols-4 gap-2">
                    <button 
                      type="button"
                      v-for="place in region.places" 
                      :key="place"
                      @click="togglePlace(place)"
                      class="px-2 py-1.5 rounded text-xs font-medium transition-all border"
                      :class="selectedPlaces.has(place) 
                        ? 'bg-primary-50 text-primary-700 border-primary-200 shadow-sm ring-1 ring-primary-200' 
                        : 'bg-white text-slate-600 border-slate-200 hover:border-primary-300 hover:bg-slate-50'"
                    >
                      {{ place }}
                    </button>
                  </div>
                  <hr v-if="index < regions.length - 1" class="mt-4 border-slate-100">
                </div>
              </div>
            </div>

            <!-- Footer -->
            <div class="bg-slate-50 px-4 py-3 sm:px-6 flex flex-col-reverse sm:flex-row sm:justify-end gap-2 flex-shrink-0 border-t border-slate-100">
              <button 
                type="button" 
                class="w-full sm:w-auto inline-flex justify-center rounded-lg border border-slate-300 shadow-sm px-4 py-2 bg-white text-sm font-medium text-slate-700 hover:bg-slate-50 focus:outline-none transition-colors"
                @click="$emit('close')"
              >
                關閉
              </button>
              <button 
                type="button" 
                class="w-full sm:w-auto inline-flex justify-center rounded-lg border border-red-200 shadow-sm px-4 py-2 bg-white text-sm font-medium text-red-600 hover:bg-red-50 focus:outline-none transition-colors"
                @click="clearSelection"
              >
                清空
              </button>
              <button 
                type="button" 
                class="w-full sm:w-auto inline-flex justify-center rounded-lg border border-transparent shadow-sm px-6 py-2 bg-primary-600 text-sm font-bold text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-all shadow-primary-500/20"
                @click="confirmSelection"
              >
                確定選取
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
/* Styles removed as Transition is removed */
</style>
