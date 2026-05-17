<script setup lang="ts">
import { ShieldCheckIcon, ArrowLeftIcon } from '@heroicons/vue/24/outline'

const pageUrl = useAbsoluteUrl('/privacy-policy')

useSeoMeta({
  title: '隱私權政策 - 開放事求人',
  description: '開放事求人網站的隱私權政策說明，包含個人資料蒐集方式、Google Analytics 使用，以及 Cookie 政策。',
  robots: 'index,follow',
  ogTitle: '隱私權政策 - 開放事求人',
  ogDescription: '開放事求人網站的隱私權政策說明。',
  ogUrl: pageUrl,
  ogType: 'website',
})

useHead({
  link: [
    { rel: 'canonical', href: pageUrl }
  ]
})
</script>

<template>
  <div class="bg-gradient-to-b from-slate-50 to-white min-h-screen py-8 px-4">
    <div class="container mx-auto max-w-4xl">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-slate-800 flex items-center gap-3 mb-2">
          <div class="p-2 bg-primary-100 rounded-lg">
            <ShieldCheckIcon class="w-8 h-8 text-primary-600" />
          </div>
          隱私權政策
        </h1>
        <p class="text-slate-500 text-lg">了解本網站如何保護您的個人資訊</p>
      </div>

      <!-- Content -->
      <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-6 sm:p-8">
        <div class="prose prose-slate max-w-none">
          <p class="text-lg text-slate-700 leading-relaxed">
            感謝您光臨「開放事求人」（以下簡稱本網站），為了幫助您瞭解本網站如何蒐集、應用及保護您所提供的個人資訊，請您務必詳細閱讀下列資訊：
          </p>

          <h2 class="text-xl font-bold text-slate-800 mt-8 mb-4 flex items-center gap-2">
            <span class="w-8 h-8 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center text-sm font-bold">1</span>
            政策適用範圍
          </h2>
          <p class="text-slate-600 leading-relaxed">
            本隱私權政策適用於您在本網站活動時，所涉及的個人資料蒐集、運用與保護，但不適用於與本網站以外的相關連結網站，也不適用於非本網站所管理的人員。
          </p>

          <h2 class="text-xl font-bold text-slate-800 mt-8 mb-4 flex items-center gap-2">
            <span class="w-8 h-8 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center text-sm font-bold">2</span>
            個人資料之蒐集、處理及利用方式
          </h2>
          <ul class="text-slate-600 space-y-3 list-none pl-0">
            <li class="flex items-start gap-3">
              <span class="w-6 h-6 bg-slate-100 text-slate-600 rounded-full flex items-center justify-center text-xs font-medium flex-shrink-0 mt-0.5">1</span>
              <span>本網站為單純瀏覽性質，不會蒐集任何個人資料。（除非於留言輸入可辨識個人資料之資訊）</span>
            </li>
            <li class="flex items-start gap-3">
              <span class="w-6 h-6 bg-slate-100 text-slate-600 rounded-full flex items-center justify-center text-xs font-medium flex-shrink-0 mt-0.5">2</span>
              <span>本網站有導入 Google GA，會記錄使用者的 IP 位址、上網時間及瀏覽網頁資料，以供內部分析網站流量及行為。（IP 位址本網站的管理者也看不到）</span>
            </li>
          </ul>

          <h2 class="text-xl font-bold text-slate-800 mt-8 mb-4 flex items-center gap-2">
            <span class="w-8 h-8 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center text-sm font-bold">3</span>
            個人應盡義務
          </h2>
          <p class="text-slate-600 leading-relaxed">
            若提供錯誤或不實資料，本網站有權拒絕提供服務。
          </p>

          <h2 class="text-xl font-bold text-slate-800 mt-8 mb-4 flex items-center gap-2">
            <span class="w-8 h-8 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center text-sm font-bold">4</span>
            資料保護
          </h2>
          <p class="text-slate-600 leading-relaxed">
            本網站架設於 Google Cloud Platform，設有防火牆，並採嚴格保護措施，確保個人資料安全。
          </p>

          <h2 class="text-xl font-bold text-slate-800 mt-8 mb-4 flex items-center gap-2">
            <span class="w-8 h-8 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center text-sm font-bold">5</span>
            網站對外連結
          </h2>
          <p class="text-slate-600 leading-relaxed">
            本網站提供其他網站連結，但該網站不適用本隱私權政策，使用者需自行參閱該網站的隱私權保護政策。
          </p>

          <h2 class="text-xl font-bold text-slate-800 mt-8 mb-4 flex items-center gap-2">
            <span class="w-8 h-8 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center text-sm font-bold">6</span>
            Cookie 使用
          </h2>
          <p class="text-slate-600 leading-relaxed">
            本網站會使用 Cookie，若不願接受，可在瀏覽器中設定隱私權等級為高，但部分功能可能無法使用。
          </p>

          <h2 class="text-xl font-bold text-slate-800 mt-8 mb-4 flex items-center gap-2">
            <span class="w-8 h-8 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center text-sm font-bold">7</span>
            意見反饋
          </h2>
          <p class="text-slate-600 leading-relaxed">
            若對隱私權或安全政策有任何意見，歡迎隨時聯絡我們。本網站之政策將隨需求修正，並於網站上公告最新條款。
          </p>
        </div>

        <!-- Back Link -->
        <div class="mt-10 pt-6 border-t border-slate-100">
          <NuxtLink to="/" class="inline-flex items-center gap-2 text-primary-600 hover:text-primary-700 font-medium">
            <ArrowLeftIcon class="w-4 h-4" />
            返回首頁
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>
