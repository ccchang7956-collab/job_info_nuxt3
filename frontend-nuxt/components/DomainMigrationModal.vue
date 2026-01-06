<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'

const isVisible = ref(false)

const STORAGE_KEY_LAST_SHOWN = 'domainMigrationModalLastShown'
const STORAGE_KEY_NEVER_SHOW = 'domainMigrationModalNeverShow'
const EXPIRY_DATE = new Date('2026-01-17')

onMounted(() => {
  // 只在客戶端執行
  if (typeof window === 'undefined') return

  const now = new Date()
  const today = now.toDateString()

  // 檢查是否已過期
  if (now > EXPIRY_DATE) return

  // 檢查是否永久關閉
  if (localStorage.getItem(STORAGE_KEY_NEVER_SHOW) === 'true') return

  // 檢查今日是否已顯示
  if (localStorage.getItem(STORAGE_KEY_LAST_SHOWN) === today) return

  // 顯示模態框
  isVisible.value = true
})

const closeModal = () => {
  const today = new Date().toDateString()
  localStorage.setItem(STORAGE_KEY_LAST_SHOWN, today)
  isVisible.value = false
}

const neverShowAgain = () => {
  localStorage.setItem(STORAGE_KEY_NEVER_SHOW, 'true')
  isVisible.value = false
}
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="isVisible"
        class="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
        @click.self="closeModal"
      >
        <Transition
          enter-active-class="transition duration-300 ease-out"
          enter-from-class="opacity-0 scale-95"
          enter-to-class="opacity-100 scale-100"
          leave-active-class="transition duration-200 ease-in"
          leave-from-class="opacity-100 scale-100"
          leave-to-class="opacity-0 scale-95"
        >
          <div
            v-if="isVisible"
            class="relative w-full max-w-md bg-white rounded-2xl shadow-2xl overflow-hidden"
          >
            <!-- Header -->
            <div class="bg-gradient-to-r from-primary-600 to-primary-700 px-6 py-4">
              <div class="flex items-center justify-between">
                <h2 class="text-xl font-bold text-white flex items-center gap-2">
                  📢 重要通知
                </h2>
                <button
                  @click="closeModal"
                  class="text-white/80 hover:text-white transition-colors"
                >
                  <XMarkIcon class="w-6 h-6" />
                </button>
              </div>
            </div>

            <!-- Content -->
            <div class="px-6 py-5 space-y-5 max-h-[60vh] overflow-y-auto">
              <!-- 網址更新 -->
              <div class="space-y-2">
                <h3 class="font-bold text-slate-800 flex items-center gap-2">
                  🔗 網址已更新
                </h3>
                <div class="text-slate-600 text-sm space-y-1">
                  <p>本站已遷移至新網址：</p>
                  <p class="font-bold text-primary-600 text-base">opendgpa.shibaalin.com</p>
                  <p class="text-amber-600">
                    舊網址 <code class="bg-amber-50 px-1 rounded">opendgpa.site</code> 將於 <strong>2026/01/17</strong> 停止服務。
                  </p>
                  <p>請將新網址加入書籤！</p>
                </div>
              </div>

              <hr class="border-slate-200" />

              <!-- PWA -->
              <div class="space-y-2">
                <h3 class="font-bold text-slate-800 flex items-center gap-2">
                  📱 支援 PWA
                </h3>
                <p class="text-slate-600 text-sm">
                  本站支援 PWA（漸進式網頁應用程式），您可以使用「加入主畫面」功能，讓網站像 APP 一樣使用，享受更佳的瀏覽體驗！
                </p>
              </div>

              <hr class="border-slate-200" />

              <!-- 新功能 -->
              <div class="space-y-2">
                <h3 class="font-bold text-slate-800 flex items-center gap-2">
                  ✨ 新功能：職缺狀態顯示
                </h3>
                <ul class="text-slate-600 text-sm space-y-1.5">
                  <li class="flex items-center gap-2">
                    <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-700">
                      🔄 曾開缺
                    </span>
                    <span>過去曾刊登過此職缺</span>
                  </li>
                  <li class="flex items-center gap-2">
                    <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-700">
                      💬 有留言
                    </span>
                    <span>該職缺有用戶留言討論</span>
                  </li>
                </ul>
              </div>
            </div>

            <!-- Footer -->
            <div class="px-6 py-4 bg-slate-50 border-t border-slate-200 flex justify-end gap-3">
              <button
                @click="neverShowAgain"
                class="px-4 py-2 text-sm font-medium text-slate-600 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition-colors"
              >
                不再顯示
              </button>
              <button
                @click="closeModal"
                class="px-5 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-lg shadow-sm transition-colors flex items-center gap-1.5"
              >
                我知道了 ✓
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>
