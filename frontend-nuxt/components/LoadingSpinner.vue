<script setup lang="ts">
interface Props {
  message?: string
  size?: 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  message: '正在載入...',
  size: 'md'
})

const sizeClasses = {
  sm: {
    outer: 'w-10 h-10',
    inner: 'w-5 h-5',
    border: 'border-[3px]'
  },
  md: {
    outer: 'w-16 h-16',
    inner: 'w-8 h-8',
    border: 'border-4'
  },
  lg: {
    outer: 'w-20 h-20',
    inner: 'w-10 h-10',
    border: 'border-[5px]'
  }
}

const currentSize = computed(() => sizeClasses[props.size])
</script>

<template>
  <div 
    role="status" 
    :aria-label="message"
    class="flex flex-col items-center justify-center py-32 text-slate-400"
  >
    <div class="relative">
      <!-- 外環 - 旋轉動畫 -->
      <div 
        class="rounded-full animate-spin border-slate-100 border-t-primary-500"
        :class="[currentSize.outer, currentSize.border]"
      ></div>
      <!-- 內圓 - 靜態白色圓心 -->
      <div class="absolute inset-0 flex items-center justify-center">
        <div 
          class="bg-white rounded-full"
          :class="currentSize.inner"
        ></div>
      </div>
    </div>
    <!-- 訊息文字 - 脈動動畫 -->
    <p class="mt-4 font-medium text-slate-500 animate-pulse">{{ message }}</p>
  </div>
</template>
