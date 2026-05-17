<script setup lang="ts">
import { ref } from 'vue'
import { 
  InformationCircleIcon, 
  WrenchScrewdriverIcon, 
  CommandLineIcon, 
  PaperAirplaneIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  CheckCircleIcon,
  ExclamationCircleIcon
} from '@heroicons/vue/24/outline'

// Types
interface FormData {
  name: string
  email: string
  message: string
}

interface SubmitStatus {
  type: '' | 'success' | 'error'
  message: string
}

// Dev Log State
const isDevLogOpen = ref(false)
const toggleDevLog = () => {
  isDevLogOpen.value = !isDevLogOpen.value
}

// Contact Form State
const formData = ref<FormData>({
  name: '',
  email: '',
  message: ''
})
const errors = ref<Partial<FormData>>({})
const loading = ref(false)
const submitStatus = ref<SubmitStatus>({
  type: '', 
  message: ''
})

const validateForm = (): boolean => {
  const newErrors: Partial<FormData> = {}
  let isValid = true

  if (!formData.value.name.trim()) {
    newErrors.name = '請輸入您的稱呼。'
    isValid = false
  }

  if (!formData.value.email.trim()) {
    newErrors.email = '請輸入您的電子郵件。'
    isValid = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.value.email.trim())) {
    newErrors.email = '請輸入有效的電子郵件地址。'
    isValid = false
  }

  if (!formData.value.message.trim()) {
    newErrors.message = '請輸入您的訊息。'
    isValid = false
  }

  errors.value = newErrors
  return isValid
}

const submitForm = async () => {
  submitStatus.value = { type: '', message: '' }
  
  if (!validateForm()) {
    return
  }

  loading.value = true
  
  try {
    const response = await fetch('https://formspree.io/f/xzzdqbyk', {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData.value)
    })

    const data = await response.json()

    if (response.ok) {
      submitStatus.value = {
        type: 'success',
        message: '訊息提交成功！感謝您的聯繫。'
      }
      formData.value = { name: '', email: '', message: '' }
      errors.value = {}
    } else {
      let errorMsg = '訊息提交失敗，請稍後再試。'
      if (data && data.errors && data.errors.length > 0) {
        errorMsg = data.errors.map((err: any) => err.message).join(', ')
      }
      throw new Error(errorMsg)
    }
  } catch (error: any) {
    submitStatus.value = {
      type: 'error',
      message: '訊息提交失敗。錯誤：' + error.message
    }
  } finally {
    loading.value = false
  }
}

const pageUrl = useAbsoluteUrl('/about')

// SEO
useSeoMeta({
  title: '關於本站 - 開放事求人｜人事行政總處事求人開放資料',
  description: '了解開放事求人網站的緣起與特色功能。人事行政總處事求人開放資料查詢平台。',
  keywords: '事求人, 人事行政總處事求人, 開放資料, 關於, 開放事求人',
  robots: 'index,follow',
  ogTitle: '關於本站 - 開放事求人｜人事行政總處事求人開放資料',
  ogDescription: '了解開放事求人網站的緣起與特色功能。',
  ogUrl: pageUrl,
  ogType: 'website',
})

// Canonical URL + FAQ Schema
useHead({
  link: [
    { rel: 'canonical', href: pageUrl }
  ],
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        'mainEntity': [
          {
            '@type': 'Question',
            'name': '開放事求人是什麼？',
            'acceptedAnswer': {
              '@type': 'Answer',
              'text': '開放事求人是一個人事行政總處事求人開放資料查詢平台，提供公務員職缺搜尋、歷史開缺追蹤、留言討論、統計圖表等功能。'
            }
          },
          {
            '@type': 'Question',
            'name': '與官方事求人網站有什麼不同？',
            'acceptedAnswer': {
              '@type': 'Answer',
              'text': '開放事求人提供歷史開缺紀錄追蹤、重複開缺提醒、職缺留言討論、統計圖表分析等官方網站沒有的功能，並支援 PWA 安裝到手機。'
            }
          },
          {
            '@type': 'Question',
            'name': '資料來源是什麼？',
            'acceptedAnswer': {
              '@type': 'Answer',
              'text': '本站資料來源為政府資料開放平臺之「行政院人事行政總處事求人機關徵才資料」，每日自動同步更新。'
            }
          },
          {
            '@type': 'Question',
            'name': '可以在手機上使用嗎？',
            'acceptedAnswer': {
              '@type': 'Answer',
              'text': '是的，開放事求人支援 PWA（漸進式網頁應用程式），可以安裝到手機桌面像 App 一樣使用，並支援離線瀏覽。'
            }
          }
        ]
      })
    }
  ]
})
</script>

<template>
  <div class="page-container">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-8">
      <div>
        <h1 class="text-3xl font-bold text-slate-800 flex items-center gap-3 mb-2">
          <div class="p-2 bg-primary-100 rounded-lg">
            <InformationCircleIcon class="w-8 h-8 text-primary-600" />
          </div>
          關於本站與聯絡方式
        </h1>
        <p class="text-slate-500 text-lg">了解本站的緣起、特色功能，或隨時與我們聯繫。</p>
      </div>
    </div>

    <!-- About Card -->
    <div class="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden mb-8">
      <div class="bg-primary-50 px-6 py-4 border-b border-primary-100 flex items-center gap-2">
        <InformationCircleIcon class="w-6 h-6 text-primary-600" />
        <h5 class="font-bold text-primary-900 m-0">關於本站</h5>
      </div>
      <div class="p-6">
        <ul class="space-y-4 text-slate-600 leading-relaxed">
          <li class="flex gap-3">
            <span class="text-primary-500 mt-1">📢</span>
            <span>因為113年勞動部公務員事件，想要讓大家能分享職缺趨吉避凶，所以有了這個網站。</span>
          </li>
          <li class="flex gap-3">
            <span class="text-primary-500 mt-1">📅</span>
            <span>目前職缺資料從113年11月11日開始至今。(配合人事行政總處開放資料更新頻率，每日12:30左右和00:30左右更新)</span>
          </li>
          <li class="flex gap-3">
            <span class="text-primary-500 mt-1">👥</span>
            <span>有前輩做出一個人事行政總處事求人開放資料版，相當好用，但後來很可惜因為被人洗版導致留言功能關掉，希望能提供給大家一個能查詢職缺（包含歷史開缺）並且評論的平台，也參考了前面網站的很多功能，目前留言區開放可以訪客留言，若還是被人洗版可能會改成需要登入。另外有什麼功能上的想法或建議都可以提供！</span>
          </li>
          <li class="flex gap-3">
            <span class="text-primary-500 mt-1">📱</span>
            <span>本站支援 PWA（漸進式網頁應用程式），您可以使用「加入主畫面」功能，讓網站像 APP 一樣使用，享受更佳的瀏覽體驗！</span>
          </li>
        </ul>
      </div>
    </div>

    <!-- Features Card -->
    <div class="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden mb-8">
      <div class="bg-primary-50 px-6 py-4 border-b border-primary-100 flex items-center gap-2">
        <WrenchScrewdriverIcon class="w-6 h-6 text-primary-600" />
        <h5 class="font-bold text-primary-900 m-0">本站特色功能</h5>
      </div>
      <div class="p-6">
        <ul class="space-y-4 text-slate-600 leading-relaxed">
          <li class="flex gap-3">
            <span class="text-primary-500 mt-1">🔖</span>
            <div>
              <strong class="text-slate-800">記憶搜尋狀態：</strong>
              在「看職缺」頁面搜尋到自己設定的條件後，可以將網址存成書籤（我的最愛），方便每次都是跑出預設的條件。
            </div>
          </li>
          <li class="flex gap-3">
            <span class="text-primary-500 mt-1">🕰️</span>
            <div>
              <strong class="text-slate-800">歷史職缺搜尋：</strong>
              在「看職缺」頁面可以設定"包含歷史職缺"後搜尋，方便查找機關過去開缺情形(目前資料日期從113/11月中旬開始)。
            </div>
          </li>
          <li class="flex gap-3">
            <span class="text-primary-500 mt-1">📋</span>
            <div>
              <strong class="text-slate-800">歷史重複開缺：</strong>
              職缺詳細資料裡面有這個欄位，判斷標準為相同機關且相同工作內容，過去開過的職缺就會顯示出來。
            </div>
          </li>
          <li class="flex gap-3">
            <span class="text-primary-500 mt-1">💬</span>
            <div>
              <strong class="text-slate-800">留言區：</strong>
              職缺詳細資料下面可以留言，目前可以匿名。
            </div>
          </li>
          <li class="flex gap-3">
            <span class="text-primary-500 mt-1">📊</span>
            <div>
              <strong class="text-slate-800">其他：</strong>
              一些統計資料和排行榜等等。
            </div>
          </li>
        </ul>
      </div>
    </div>

    <!-- Dev Log Card -->
    <div class="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden mb-8">
      <div 
        class="bg-primary-50 px-6 py-4 border-b border-primary-100 flex items-center justify-between cursor-pointer hover:bg-primary-100 transition-colors"
        @click="toggleDevLog"
      >
        <div class="flex items-center gap-2">
          <CommandLineIcon class="w-6 h-6 text-primary-600" />
          <h5 class="font-bold text-primary-900 m-0">開發日誌</h5>
        </div>
        <component :is="isDevLogOpen ? ChevronUpIcon : ChevronDownIcon" class="w-5 h-5 text-slate-500" />
      </div>
      
      <div v-show="isDevLogOpen" class="p-6 bg-slate-50/50">
        <ul class="space-y-3 text-slate-600 text-sm">
          <li class="flex gap-3">
            <span class="text-slate-400 font-mono">2026-01-05</span>
            <span>[新增]網站改版成可用PWA版本，可以用“加入主畫面”變成一個偽APP</span>
          </li>
          <li class="flex gap-3">
            <span class="text-slate-400 font-mono">2026-01-05</span>
            <span>[新增]增加每個職缺的「狀態」標籤，例如：曾開缺、有留言等等。</span>
          </li>
          <li class="flex gap-3">
            <span class="text-slate-400 font-mono">2025-7-26</span>
            <span>[異動]統計排行調整</span>
          </li>
          <li class="flex gap-3">
            <span class="text-slate-400 font-mono">2025-7-19</span>
            <span>[新增]增加非正式公務人員查詢</span>
          </li>
          <li class="flex gap-3">
            <span class="text-slate-400 font-mono">2025-6-05</span>
            <span>[新增]留言區可以搜尋</span>
          </li>
          <li class="flex gap-3">
            <span class="text-slate-400 font-mono">2025-5-28</span>
            <span>[新增]Google廣告審核通過了。</span>
          </li>
          <li class="flex gap-3">
            <span class="text-slate-400 font-mono">2025-5-27</span>
            <span>[修改]修改關於頁面呈現，整合聯絡我</span>
          </li>
          <li class="flex gap-3">
            <span class="text-slate-400 font-mono">2025-5-22</span>
            <span>[新增]LINE機器人改成用AI進行語意判斷，應該會比較好用。</span>
          </li>
          <li class="flex gap-3">
            <span class="text-slate-400 font-mono">2025-4-28</span>
            <span>[新增]LINE機器人，大家玩玩看。</span>
          </li>
          <li class="flex gap-3">
            <span class="text-slate-400 font-mono">2025-3-28</span>
            <span>[新增]職缺詳細資料的標頭icon。</span>
          </li>
          <li class="flex gap-3">
            <span class="text-slate-400 font-mono">2025-3-11</span>
            <span>[新增]看職缺頁面增加可以輸入分頁筆數和下拉式選單跳頁功能（使用者提議）。</span>
          </li>
          <li class="flex gap-3">
            <span class="text-slate-400 font-mono">2025-2-27</span>
            <span>[新增]看留言頁面增加已刪除留言分頁。</span>
          </li>
          <li class="flex gap-3">
            <span class="text-slate-400 font-mono">2025-2-23</span>
            <span>[新增]增加模態框選擇後的提示(Toast)。</span>
          </li>
          <li class="flex gap-3">
            <span class="text-slate-400 font-mono">2025-2-22</span>
            <span>[新增]增加聯絡我頁面。</span>
          </li>
          <li class="flex gap-3">
            <span class="text-slate-400 font-mono">2025-2-22</span>
            <span>[修改]更新職缺列表的工作地顯示方式、增加一張統計圖每月工作地開缺、上方選單區增加資料日期。</span>
          </li>
          <li class="flex gap-3">
            <span class="text-slate-400 font-mono">2025-2-21</span>
            <span>[修改]更新表格顯示職等方式（ex:6等 - 7等）、日期顯示和一些小地方。</span>
          </li>
          <li class="flex gap-3">
            <span class="text-slate-400 font-mono">2025-2-14</span>
            <span>[刪除]暫時移除排行榜-職缺點擊數。</span>
          </li>
          <li class="flex gap-3">
            <span class="text-slate-400 font-mono">2025-2-12</span>
            <span>[新增]增加工作地點連結google maps。</span>
          </li>
          <li class="flex gap-3">
            <span class="text-slate-400 font-mono">2025-2-10</span>
            <span>[新增]增加手機版顯示工作地點，PTT網友需求。</span>
          </li>
          <li class="flex gap-3">
            <span class="text-slate-400 font-mono">2025-2-08</span>
            <span>[新增]增加職等的搜尋條件，PTT網友需求。</span>
          </li>
          <li class="flex gap-3">
            <span class="text-slate-400 font-mono">2025-2-06</span>
            <span>[修改]修正職系選單(增加新聞傳播)，謝謝網友反映。</span>
          </li>
          <li class="flex gap-3">
            <span class="text-slate-400 font-mono">2025-2-05</span>
            <span>[修改]修正地點選單(臺東市改為臺東縣)，謝謝網友反映。</span>
          </li>
          <li class="flex gap-3">
            <span class="text-slate-400 font-mono">2025-1-26</span>
            <span>[新增]增加按表頭欄位可以排序功能。</span>
          </li>
          <li class="flex gap-3">
            <span class="text-slate-400 font-mono">2025-1-23</span>
            <span>[修改]因為有程式爬網站，造成某些職缺點閱數衝高，做一些修改。</span>
          </li>
          <li class="flex gap-3">
            <span class="text-slate-400 font-mono">2025-1-17</span>
            <span>初步搞定留言區而且申請好domain和ssl。</span>
          </li>
          <li class="flex gap-3">
            <span class="text-slate-400 font-mono">2025-1月上旬</span>
            <span>決定來自幹一個簡單的留言區，而且要有驗證防止機器人，但年底太忙了進度牛步。</span>
          </li>
          <li class="flex gap-3">
            <span class="text-slate-400 font-mono">2024-12月下旬</span>
            <span>留言區改成用commento，還又多開了一台VM，最後發現它的註冊功能用的e-mail沒有驗證，所以隨便輸入也可以通過，果斷放棄..。</span>
          </li>
          <li class="flex gap-3">
            <span class="text-slate-400 font-mono">2024-12月中旬</span>
            <span>繼續調整前台，導入留言區，一開始用disqus，這個抓留言數有提供API，但每小時還有限制連線次數，已經都弄得差不多才發現網友說它很會插入廣告XD</span>
          </li>
          <li class="flex gap-3">
            <span class="text-slate-400 font-mono">2024-12月上旬</span>
            <span>開始慢慢實現功能(從開放資料抓下來資料庫，資料如何呈現)。</span>
          </li>
          <li class="flex gap-3">
            <span class="text-slate-400 font-mono">2024-11的某天</span>
            <span>因為勞動部的事件，萌生了想做這個網站的想法。</span>
          </li>
        </ul>
      </div>
    </div>

    <!-- Contact Form Card -->
    <div id="contact-section" class="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
      <div class="bg-primary-50 px-6 py-4 border-b border-primary-100">
        <div class="flex items-center gap-2 mb-1">
          <PaperAirplaneIcon class="w-6 h-6 text-primary-600" />
          <h5 class="font-bold text-primary-900 m-0">與我們聯繫</h5>
        </div>
        <p class="text-sm text-slate-500 m-0">有任何問題、建議或錯誤報告？請填寫下方表單，您的意見對改進網站非常重要！</p>
      </div>
      <div class="p-6">
        <form @submit.prevent="submitForm" class="space-y-4">
          <div>
            <input 
              v-model="formData.name"
              type="text" 
              class="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary-100 focus:border-primary-500 outline-none transition-all"
              :class="{ 'border-red-300 focus:border-red-500 focus:ring-red-100': errors.name }"
              placeholder="您的稱呼 (必填)"
            >
            <p v-if="errors.name" class="mt-1 text-sm text-red-500">{{ errors.name }}</p>
          </div>
          
          <div>
            <input 
              v-model="formData.email"
              type="email" 
              class="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary-100 focus:border-primary-500 outline-none transition-all"
              :class="{ 'border-red-300 focus:border-red-500 focus:ring-red-100': errors.email }"
              placeholder="您的電子郵件 (必填，例如: name@example.com)"
            >
            <p v-if="errors.email" class="mt-1 text-sm text-red-500">{{ errors.email }}</p>
          </div>
          
          <div>
            <textarea 
              v-model="formData.message"
              rows="5" 
              class="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary-100 focus:border-primary-500 outline-none transition-all"
              :class="{ 'border-red-300 focus:border-red-500 focus:ring-red-100': errors.message }"
              placeholder="您的訊息 (必填)"
            ></textarea>
            <p v-if="errors.message" class="mt-1 text-sm text-red-500">{{ errors.message }}</p>
          </div>

          <div class="flex justify-end">
            <button 
              type="submit" 
              class="flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white px-6 py-2.5 rounded-lg font-medium transition-all shadow-sm hover:shadow disabled:opacity-70 disabled:cursor-not-allowed"
              :disabled="loading"
            >
              <PaperAirplaneIcon v-if="!loading" class="w-5 h-5" />
              <svg v-else class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ loading ? '發送中...' : '發送' }}
            </button>
          </div>
        </form>

        <!-- Status Message -->
        <div v-if="submitStatus.message" class="mt-6 p-4 rounded-lg flex items-start gap-3"
          :class="submitStatus.type === 'success' ? 'bg-green-50 text-green-700 border border-green-100' : 'bg-red-50 text-red-700 border border-red-100'"
        >
          <CheckCircleIcon v-if="submitStatus.type === 'success'" class="w-5 h-5 mt-0.5 flex-shrink-0" />
          <ExclamationCircleIcon v-else class="w-5 h-5 mt-0.5 flex-shrink-0" />
          <p>{{ submitStatus.message }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
