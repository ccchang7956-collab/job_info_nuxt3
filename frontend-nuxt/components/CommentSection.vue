<script setup lang="ts">
// Nuxt 3 auto-imports ref and nextTick
import CommentItem from './CommentItem.vue'
import { XMarkIcon, PaperAirplaneIcon } from '@heroicons/vue/24/outline'
import { useComments } from '../composables/useComments'
import type { Comment } from '@/types'

const props = defineProps<{
  comments: Comment[]
  jobId: number
}>()

const emit = defineEmits<{
  (e: 'refresh'): void
}>()

const username = ref('')
const message = ref('')
const replyTo = ref<Comment | null>(null)

const commentFormRef = ref<HTMLElement | null>(null)
const messageTextareaRef = ref<HTMLTextAreaElement | null>(null)

const { submitting, error, submitComment } = useComments(props.jobId, () => emit('refresh'))

const handleReply = (comment: Comment) => {
  replyTo.value = comment
  // Scroll to form
  if (commentFormRef.value) {
    commentFormRef.value.scrollIntoView({ behavior: 'smooth' })
    // Focus textarea
    nextTick(() => {
      if (messageTextareaRef.value) messageTextareaRef.value.focus()
    })
  }
}

const cancelReply = () => {
  replyTo.value = null
}

const handleSubmit = async () => {
  const success = await submitComment(
    username.value, 
    message.value, 
    replyTo.value ? replyTo.value.id : null
  )

  if (success) {
    // Reset form
    message.value = ''
    replyTo.value = null
  }
}
</script>

<template>
  <div class="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden mt-8">
    <div class="p-6 sm:p-8 border-b border-slate-100 bg-slate-50/50">
      <h2 class="text-xl font-bold text-slate-900 flex items-center gap-2">
        <span class="w-1.5 h-6 bg-emerald-500 rounded-full"></span>
        留言討論區
        <span class="text-sm font-normal text-slate-500 ml-2">({{ comments.length }} 則留言)</span>
      </h2>
    </div>

    <div class="p-6 sm:p-8">
      <!-- Comments List -->
      <div v-if="comments.length > 0" class="mb-12">
        <CommentItem 
          v-for="comment in comments" 
          :key="comment.id" 
          :comment="comment" 
          @reply="handleReply"
        />
      </div>
      <div v-else class="text-center py-12 text-slate-400 bg-slate-50 rounded-xl border border-dashed border-slate-200 mb-12">
        <p>目前尚無留言，成為第一個留言的人吧！</p>
      </div>

      <!-- Comment Form -->
      <div ref="commentFormRef" class="bg-slate-50 p-6 rounded-xl border border-slate-200">
        <div class="flex justify-between items-center mb-4">
          <h3 class="font-bold text-slate-800">發表留言</h3>
          <button 
            v-if="replyTo" 
            @click="cancelReply" 
            class="text-xs flex items-center gap-1 bg-slate-200 hover:bg-slate-300 text-slate-600 px-2 py-1 rounded-full transition-colors"
          >
            回覆給: {{ replyTo.username }}
            <XMarkIcon class="w-3 h-3" />
          </button>
        </div>

        <div class="mb-4">
          <label class="block text-xs font-medium text-slate-500 mb-1">暱稱 *</label>
          <input 
            v-model="username" 
            type="text" 
            placeholder="您的暱稱" 
            class="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary-100 focus:border-primary-500 outline-none transition-all text-sm"
          >
        </div>

        <div class="mb-4">
          <label class="block text-xs font-medium text-slate-500 mb-1">留言內容 *</label>
          <textarea 
            ref="messageTextareaRef"
            v-model="message" 
            rows="4" 
            placeholder="請輸入您的留言..." 
            class="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary-100 focus:border-primary-500 outline-none transition-all text-sm resize-none"
          ></textarea>
        </div>

        <div class="mb-6 flex justify-center">
          <div id="recaptcha-container"></div>
        </div>

        <div v-if="error" class="mb-4 text-center text-sm text-red-600 bg-red-50 py-2 rounded-lg">
          {{ error }}
        </div>

        <button 
          @click="handleSubmit" 
          :disabled="submitting"
          class="w-full sm:w-auto px-6 py-2.5 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg shadow-sm hover:shadow transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 mx-auto"
        >
          <span v-if="submitting" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
          <PaperAirplaneIcon v-else class="w-4 h-4" />
          {{ submitting ? '發送中...' : '送出留言' }}
        </button>
      </div>
    </div>
  </div>
</template>
