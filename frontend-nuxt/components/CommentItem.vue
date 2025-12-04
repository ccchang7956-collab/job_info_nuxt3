<script setup>
import { formatDistanceToNow } from 'date-fns'
import { zhTW } from 'date-fns/locale'

const props = defineProps({
  comment: {
    type: Object,
    required: true
  }
})

defineEmits(['reply'])

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  try {
    const date = new Date(dateStr)
    return formatDistanceToNow(date, { addSuffix: true, locale: zhTW })
  } catch (e) {
    return dateStr
  }
}
</script>

<template>
  <div class="flex gap-3 mb-6">
    <!-- Avatar -->
    <div 
      class="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold shrink-0 shadow-sm"
      :style="{ backgroundColor: comment.color || '#3b82f6' }"
    >
      {{ comment.initial }}
    </div>
    
    <div class="flex-1 min-w-0">
      <div class="bg-slate-50 p-4 rounded-2xl rounded-tl-none border border-slate-100 hover:border-slate-200 transition-colors">
        <div class="flex justify-between items-center mb-2">
          <div class="font-bold text-slate-800 text-sm">{{ comment.username }}</div>
          <div class="text-xs text-slate-400">{{ formatDate(comment.created_at) }}</div>
        </div>
        <p class="text-slate-700 whitespace-pre-wrap text-sm leading-relaxed break-words">{{ comment.message }}</p>
        
        <button 
          @click="$emit('reply', comment)" 
          class="text-xs font-medium text-primary-600 hover:text-primary-700 mt-3 flex items-center gap-1 hover:underline decoration-2 underline-offset-2"
        >
          回覆
        </button>
      </div>

      <!-- Recursive Children -->
      <div v-if="comment.children && comment.children.length > 0" class="mt-4 pl-4 sm:pl-6 border-l-2 border-slate-100 space-y-4">
        <CommentItem 
          v-for="child in comment.children" 
          :key="child.id" 
          :comment="child" 
          @reply="$emit('reply', $event)"
        />
      </div>
    </div>
  </div>
</template>
