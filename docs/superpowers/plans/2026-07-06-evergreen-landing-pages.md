# 縣市與職系長青登陸頁面 (Evergreen Landing Pages) 實作計劃

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建立台灣 22 縣市與主要職系的長青登陸頁面，並透過內部連結與 Sitemap/IndexNow 整合，大幅提升網站的 GEO（地方搜尋）與分類 SEO 曝光度。

**Architecture:** 前端使用 Nuxt 3 新增動態 SSR 路由 `/places/[place]` 與 `/sysnams/[sysnam]`。頁面以 `useFetch` 發送篩選請求至 FastAPI 後端 `/api/jobs`，並嵌入在地化的 Meta 資訊與 JSON-LD（BreadcrumbList / ItemList）。後端動態擴展靜態 Sitemap 並在新職缺同步時一併推送分類 URL 至 IndexNow。

**Tech Stack:** Nuxt 3 (Vue 3, TypeScript), FastAPI (Python 3, SQLAlchemy), XML Sitemap, IndexNow API, pytest / test_seo.py 驗證腳本。

## Global Constraints
*   **語言格式**：所有頁面的 HTML lang 均為 `zh-TW`，SEO 標題與描述均為繁體中文。
*   **路由設計**：網址路徑格式必須為小寫與正確編碼，如 `/places/臺北市`。
*   **SSR 運作**：不可改為 client-only 渲染，搜尋引擎爬蟲必須在初次請求時即抓取到完整的職缺列表 HTML。

---

### Task 1: 後端 Sitemap 擴充

**Files:**
- Modify: `backend/app/Services/SeoService.py`

**Interfaces:**
- Produces: 更新後的 `/sitemap-static.xml`，內含 22 縣市與熱門職系的動態 URLs。

- [ ] **Step 1: 修改 Sitemap 靜態路由產生邏輯**
  在 `backend/app/Services/SeoService.py` 中更新 `get_sitemap_static`，加入縣市及熱門職系：
  ```python
      @staticmethod
      async def get_sitemap_static() -> str:
          """生成靜態及長青分類頁面的 Sitemap XML。"""
          cache_key = "sitemap_static"
          if cache_key in sitemap_cache:
              return sitemap_cache[cache_key]

          base_url = SITE_DOMAIN
          
          static_routes = [
              {"path": "/", "priority": "1.0", "changefreq": "daily"},
              {"path": "/comments", "priority": "0.7", "changefreq": "daily"},
              {"path": "/charts", "priority": "0.7", "changefreq": "daily"},
              {"path": "/about", "priority": "0.5", "changefreq": "monthly"},
              {"path": "/privacy-policy", "priority": "0.3", "changefreq": "yearly"},
          ]

          # 台灣 22 縣市
          places = [
              '臺北市', '新北市', '基隆市', '桃園市', '新竹縣', '新竹市', '苗栗縣',
              '臺中市', '彰化縣', '南投縣', '雲林縣', '嘉義縣', '嘉義市', '臺南市',
              '高雄市', '屏東縣', '宜蘭縣', '花蓮縣', '臺東縣', '澎湖縣', '金門縣', '連江縣'
          ]
          for p in places:
              static_routes.append({"path": f"/places/{p}", "priority": "0.9", "changefreq": "daily"})

          # 熱門職系
          sysnams = [
              '綜合行政', '人事行政', '經建行政', '會計審計', '地政', '社勞行政', '文教行政', '社會工作', '法制', '交通行政',
              '土木工程', '電機工程', '資訊處理', '農業技術', '測量製圖', '建築工程', '機械工程', '都市計畫'
          ]
          for s in sysnams:
              static_routes.append({"path": f"/sysnams/{s}", "priority": "0.9", "changefreq": "daily"})

          today_str = datetime.now().strftime("%Y-%m-%d")

          xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
          xml_parts.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

          for route in static_routes:
              lastmod = STATIC_PAGE_LASTMOD.get(route["path"], today_str)
              xml_parts.append('<url>')
              xml_parts.append(f'<loc>{escape(base_url + route["path"])}</loc>')
              xml_parts.append(f'<lastmod>{lastmod}</lastmod>')
              xml_parts.append(f'<changefreq>{route["changefreq"]}</changefreq>')
              xml_parts.append(f'<priority>{route["priority"]}</priority>')
              xml_parts.append('</url>')

          xml_parts.append('</urlset>')
          result = "\n".join(xml_parts)
          sitemap_cache[cache_key] = result
          return result
  ```

- [ ] **Step 2: 驗證 sitemap-static.xml 解析結果**
  啟動後端並請求 `/sitemap-static.xml`。
  Expected: 回傳 XML 且包含 `<loc>https://opendgpa.shibaalin.com/places/臺北市</loc>` 等項目。

- [ ] **Step 3: Commit**
  ```bash
  git add backend/app/Services/SeoService.py
  git commit -m "feat: add evergreen routes to static sitemap"
  ```

---

### Task 2: 前端地區與職系長青頁面建立

**Files:**
- Create: `frontend-nuxt/pages/places/[place].vue`
- Create: `frontend-nuxt/pages/sysnams/[sysnam].vue`

**Interfaces:**
- Consumes: 後端 `/api/jobs?places=[place]` 與 `/api/jobs?sysnam=[sysnam]`

- [ ] **Step 1: 建立 `frontend-nuxt/pages/places/[place].vue`**
  ```vue
  <script setup lang="ts">
  import { ref, computed } from 'vue'
  import { useRoute } from 'vue-router'
  import type { JobListResponse } from '@/types'

  const route = useRoute()
  const placeName = computed(() => String(route.params.place || '').trim())
  const siteUrl = useSiteUrl()
  const pageUrl = computed(() => `${siteUrl}/places/${placeName.value}`)

  const { data, error } = await useFetch<JobListResponse>('/api/jobs', {
    query: { places: placeName.value, per_page: 20 }
  })

  useSeoMeta({
    title: () => `最新 ${placeName.value} 公務人員職缺列表｜事求人職缺查詢 - 開放事求人`,
    description: () => `最即時的 ${placeName.value} 公務人員事求人職缺資訊。整理自人事行政總處開放資料，包含歷史開缺紀錄與討論，助您掌握 ${placeName.value} 最新的政府機關工作機會。`,
    keywords: () => `事求人, 公務員職缺, ${placeName.value}公務員, ${placeName.value}政府職缺, 開放事求人`,
    robots: 'index,follow',
    ogTitle: () => `最新 ${placeName.value} 公務人員職缺列表 - 開放事求人`,
    ogDescription: () => `即時同步 ${placeName.value} 各政府機關與學校之最新公務員職缺。`,
    ogUrl: pageUrl.value,
  })

  useHead({
    link: [{ rel: 'canonical', href: pageUrl.value }],
    script: [
      {
        type: 'application/ld+json',
        innerHTML: JSON.stringify({
          '@context': 'https://schema.org',
          '@type': 'BreadcrumbList',
          'itemListElement': [
            { '@type': 'ListItem', 'position': 1, 'name': '首頁', 'item': `${siteUrl}/` },
            { '@type': 'ListItem', 'position': 2, 'name': `${placeName.value} 職缺`, 'item': pageUrl.value }
          ]
        })
      }
    ]
  })
  </script>

  <template>
    <div class="container mx-auto px-4 py-8 max-w-5xl">
      <!-- 麵包屑導覽 -->
      <nav aria-label="breadcrumb" class="mb-6 text-sm text-slate-500">
        <ol class="flex items-center flex-wrap gap-1">
          <li><NuxtLink to="/" class="hover:text-primary-600 transition-colors">首頁</NuxtLink></li>
          <li class="text-slate-300">›</li>
          <li class="text-slate-600 font-medium truncate" aria-current="page">{{ placeName }}職缺專區</li>
        </ol>
      </nav>

      <div class="mb-8">
        <h1 class="text-3xl font-bold text-slate-800 mb-2">最新 {{ placeName }} 公務人員職缺</h1>
        <p class="text-slate-500 text-lg">
          歡迎瀏覽開放事求人 {{ placeName }} 專區。本頁面即時整理 {{ placeName }} 各級政府機關、學校及中央駐地機關的事求人職缺與徵才資訊。資料來源為人事行政總處事求人開放資料，每日自動同步更新。
        </p>
      </div>

      <div v-if="error" class="bg-red-50 p-6 rounded-xl text-center text-red-600">無法載入職缺資料，請稍後再試。</div>
      <div v-else-if="!data" class="text-center py-12 text-slate-400">讀取中...</div>
      <div v-else>
        <!-- 桌機版表格與手機版卡片列表 (共享 layouts/components 邏輯) -->
        <div class="hidden md:block bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden mb-8">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-primary-600 border-b border-primary-700 text-white text-base font-bold whitespace-nowrap">
                <th class="p-4 w-[180px]">機關名稱</th>
                <th class="p-4 w-[120px]">職稱</th>
                <th class="p-4 w-[120px]">職系</th>
                <th class="p-4 w-[90px]">職等</th>
                <th class="p-4 w-[100px]">工作地點</th>
                <th class="p-4 w-[130px]">期間</th>
                <th class="p-4 text-center w-[70px]">查看</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 text-sm">
              <tr v-for="job in data.jobs" :key="job.id" class="hover:bg-blue-50/50 transition-colors">
                <td class="p-4 font-bold text-slate-700">{{ job.org }}</td>
                <td class="p-4 font-bold text-slate-700">{{ job.title }}</td>
                <td class="p-4">{{ job.sysnam }}</td>
                <td class="p-4">{{ job.rank_display || job.rank }}</td>
                <td class="p-4">{{ job.place }}</td>
                <td class="p-4">{{ job.date_from }} ~ {{ job.date_to }}</td>
                <td class="p-4 text-center">
                  <NuxtLink :to="`/job/${job.id}`" class="px-3 py-1.5 bg-white border border-slate-300 text-slate-700 rounded-lg text-xs font-bold hover:bg-primary-600 hover:text-white transition-colors">查看</NuxtLink>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="md:hidden grid grid-cols-1 gap-4">
          <JobCard v-for="job in data.jobs" :key="job.id" :job="job" />
        </div>
      </div>
    </div>
  </template>
  ```

- [ ] **Step 2: 建立 `frontend-nuxt/pages/sysnams/[sysnam].vue`**
  與 places 結構類似，使用 `sysnamName` 作為核心：
  ```vue
  <script setup lang="ts">
  import { ref, computed } from 'vue'
  import { useRoute } from 'vue-router'
  import type { JobListResponse } from '@/types'

  const route = useRoute()
  const sysnamName = computed(() => String(route.params.sysnam || '').trim())
  const siteUrl = useSiteUrl()
  const pageUrl = computed(() => `${siteUrl}/sysnams/${sysnamName.value}`)

  const { data, error } = await useFetch<JobListResponse>('/api/jobs', {
    query: { sysnam: sysnamName.value, per_page: 20 }
  })

  useSeoMeta({
    title: () => `最新 ${sysnamName.value} 職系公務員職缺列表｜事求人職缺查詢 - 開放事求人`,
    description: () => `最即時的 ${sysnamName.value} 職系公務人員事求人職缺資訊。彙整全國各級政府機關招募${sysnamName.value}職系公務員最新開缺。`,
    keywords: () => `事求人, 公務員職缺, ${sysnamName.value}, ${sysnamName.value}職缺, 開放事求人`,
    robots: 'index,follow',
    ogTitle: () => `最新 ${sysnamName.value} 職系公務員職缺列表 - 開放事求人`,
    ogDescription: () => `即時同步全國各級政府機關最新 ${sysnamName.value} 職系公務員職缺。`,
    ogUrl: pageUrl.value,
  })

  useHead({
    link: [{ rel: 'canonical', href: pageUrl.value }],
    script: [
      {
        type: 'application/ld+json',
        innerHTML: JSON.stringify({
          '@context': 'https://schema.org',
          '@type': 'BreadcrumbList',
          'itemListElement': [
            { '@type': 'ListItem', 'position': 1, 'name': '首頁', 'item': `${siteUrl}/` },
            { '@type': 'ListItem', 'position': 2, 'name': `${sysnamName.value} 職缺`, 'item': pageUrl.value }
          ]
        })
      }
    ]
  })
  </script>

  <template>
    <div class="container mx-auto px-4 py-8 max-w-5xl">
      <nav aria-label="breadcrumb" class="mb-6 text-sm text-slate-500">
        <ol class="flex items-center flex-wrap gap-1">
          <li><NuxtLink to="/" class="hover:text-primary-600 transition-colors">首頁</NuxtLink></li>
          <li class="text-slate-300">›</li>
          <li class="text-slate-600 font-medium truncate" aria-current="page">{{ sysnamName }}職系專區</li>
        </ol>
      </nav>

      <div class="mb-8">
        <h1 class="text-3xl font-bold text-slate-800 mb-2">最新 {{ sysnamName }} 職系職缺</h1>
        <p class="text-slate-500 text-lg">
          歡迎瀏覽開放事求人 {{ sysnamName }} 職系專區。本頁面為您整理全國各機關招募 {{ sysnamName }} 職系之最新公務員缺額與開缺紀錄，每日自動同步更新。
        </p>
      </div>

      <div v-if="error" class="bg-red-50 p-6 rounded-xl text-center text-red-600">無法載入職缺資料，請稍後再試。</div>
      <div v-else-if="!data" class="text-center py-12 text-slate-400">讀取中...</div>
      <div v-else>
        <div class="hidden md:block bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden mb-8">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-primary-600 border-b border-primary-700 text-white text-base font-bold whitespace-nowrap">
                <th class="p-4 w-[180px]">機關名稱</th>
                <th class="p-4 w-[120px]">職稱</th>
                <th class="p-4 w-[120px]">職系</th>
                <th class="p-4 w-[90px]">職等</th>
                <th class="p-4 w-[100px]">工作地點</th>
                <th class="p-4 w-[130px]">期間</th>
                <th class="p-4 text-center w-[70px]">查看</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 text-sm">
              <tr v-for="job in data.jobs" :key="job.id" class="hover:bg-blue-50/50 transition-colors">
                <td class="p-4 font-bold text-slate-700">{{ job.org }}</td>
                <td class="p-4 font-bold text-slate-700">{{ job.title }}</td>
                <td class="p-4">{{ job.sysnam }}</td>
                <td class="p-4">{{ job.rank_display || job.rank }}</td>
                <td class="p-4">{{ job.place }}</td>
                <td class="p-4">{{ job.date_from }} ~ {{ job.date_to }}</td>
                <td class="p-4 text-center">
                  <NuxtLink :to="`/job/${job.id}`" class="px-3 py-1.5 bg-white border border-slate-300 text-slate-700 rounded-lg text-xs font-bold hover:bg-primary-600 hover:text-white transition-colors">查看</NuxtLink>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="md:hidden grid grid-cols-1 gap-4">
          <JobCard v-for="job in data.jobs" :key="job.id" :job="job" />
        </div>
      </div>
    </div>
  </template>
  ```

- [ ] **Step 3: 驗證 SSR 及 HTML 生成**
  啟動前端（`npm run dev`）並發送請求，檢查是否回傳完整 HTML：
  `curl -s http://localhost:3000/places/%E8%87%BA%E5%8C%97%E5%B8%82 | grep -q "臺北市公務人員職缺"`
  Expected: curl 回傳含有目標關鍵字，代表 SSR 成功。

- [ ] **Step 4: Commit**
  ```bash
  git add frontend-nuxt/pages/places/\[place\].vue frontend-nuxt/pages/sysnams/\[sysnam\].vue
  git commit -m "feat: implement places and sysnams evergreen pages with SSR"
  ```

---

### Task 3: 前端頁尾與首頁導覽連結

**Files:**
- Modify: `frontend-nuxt/layouts/default.vue`
- Modify: `frontend-nuxt/pages/index.vue`

- [ ] **Step 1: 修改全域 Layout 新增頁尾 SEO 連結**
  在 `frontend-nuxt/layouts/default.vue` 中的 `<footer>` 區塊最上方（版權聲明前）插入熱門分類：
  ```html
          <div class="border-b border-slate-200 pb-6 mb-6 w-full max-w-5xl text-left grid grid-cols-1 md:grid-cols-2 gap-6 text-xs text-slate-500">
            <div>
              <span class="font-bold text-slate-600 block mb-2">依熱門縣市瀏覽：</span>
              <div class="flex flex-wrap gap-x-3 gap-y-1.5">
                <NuxtLink to="/places/臺北市" class="hover:text-primary-600">臺北市</NuxtLink>
                <NuxtLink to="/places/新北市" class="hover:text-primary-600">新北市</NuxtLink>
                <NuxtLink to="/places/桃園市" class="hover:text-primary-600">桃園市</NuxtLink>
                <NuxtLink to="/places/臺中市" class="hover:text-primary-600">臺中市</NuxtLink>
                <NuxtLink to="/places/臺南市" class="hover:text-primary-600">臺南市</NuxtLink>
                <NuxtLink to="/places/高雄市" class="hover:text-primary-600">高雄市</NuxtLink>
              </div>
            </div>
            <div>
              <span class="font-bold text-slate-600 block mb-2">依熱門職系瀏覽：</span>
              <div class="flex flex-wrap gap-x-3 gap-y-1.5">
                <NuxtLink to="/sysnams/綜合行政" class="hover:text-primary-600">綜合行政</NuxtLink>
                <NuxtLink to="/sysnams/人事行政" class="hover:text-primary-600">人事行政</NuxtLink>
                <NuxtLink to="/sysnams/會計審計" class="hover:text-primary-600">會計審計</NuxtLink>
                <NuxtLink to="/sysnams/土木工程" class="hover:text-primary-600">土木工程</NuxtLink>
                <NuxtLink to="/sysnams/資訊處理" class="hover:text-primary-600">資訊處理</NuxtLink>
                <NuxtLink to="/sysnams/電機工程" class="hover:text-primary-600">電機工程</NuxtLink>
              </div>
            </div>
          </div>
  ```

- [ ] **Step 2: 修改首頁底部新增完整 22 縣市與熱門職系導覽**
  在 `frontend-nuxt/pages/index.vue` 職缺列表結束處，插入快速導覽區塊：
  ```vue
      <!-- 快速分類導覽 (SEO 內部連結) -->
      <div class="mt-8 bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <h3 class="text-lg font-bold text-slate-800 mb-4">快速分類導覽</h3>
        <div class="mb-4">
          <h4 class="text-sm font-bold text-slate-500 mb-2">依機關所在地（縣市）</h4>
          <div class="flex flex-wrap gap-2">
            <NuxtLink 
              v-for="place in ['臺北市', '新北市', '基隆市', '桃園市', '新竹縣', '新竹市', '苗栗縣', '臺中市', '彰化縣', '南投縣', '雲林縣', '嘉義縣', '嘉義市', '臺南市', '高雄市', '屏東縣', '宜蘭縣', '花蓮縣', '臺東縣', '澎湖縣', '金門縣', '連江縣']" 
              :key="place" 
              :to="`/places/${place}`" 
              class="px-2.5 py-1 bg-slate-50 hover:bg-primary-50 hover:text-primary-700 text-slate-600 text-sm rounded-lg border border-slate-100 transition-colors"
            >
              {{ place }}
            </NuxtLink>
          </div>
        </div>
        <div>
          <h4 class="text-sm font-bold text-slate-500 mb-2">依熱門職系</h4>
          <div class="flex flex-wrap gap-2">
            <NuxtLink 
              v-for="sys in ['綜合行政', '人事行政', '經建行政', '會計審計', '地政', '社勞行政', '文教行政', '社會工作', '法制', '交通行政', '土木工程', '電機工程', '資訊處理', '農業技術', '測量製圖', '建築工程', '機械工程', '都市計畫']" 
              :key="sys" 
              :to="`/sysnams/${sys}`" 
              class="px-2.5 py-1 bg-slate-50 hover:bg-primary-50 hover:text-primary-700 text-slate-600 text-sm rounded-lg border border-slate-100 transition-colors"
            >
              {{ sys }}
            </NuxtLink>
          </div>
        </div>
      </div>
  ```

- [ ] **Step 3: 驗證連結渲染**
  重啟前端，訪問 `http://localhost:3000/`，確認底部顯示 22 縣市標籤，點擊能正確導向。

- [ ] **Step 4: Commit**
  ```bash
  git add frontend-nuxt/layouts/default.vue frontend-nuxt/pages/index.vue
  git commit -m "feat: add evergreen internal links in layout footer and homepage"
  ```

---

### Task 4: 詳情頁內文連結化

**Files:**
- Modify: `frontend-nuxt/components/JobInfoCard.vue`

- [ ] **Step 1: 將職缺詳細資料內的地點與職系改為 Link 連結**
  尋找 `JobInfoCard.vue` 中的「工作地點」與「職系」展示處，使用 `<NuxtLink>` 取代純文字：
  *   工作地點：
      ```html
      <span class="text-slate-700 font-medium">
        <NuxtLink :to="`/places/${job.place || job.work_address || '臺北市'}`" class="text-primary-600 hover:underline">
          {{ job.place || job.work_address }}
        </NuxtLink>
      </span>
      ```
  *   職系：
      ```html
      <NuxtLink :to="`/sysnams/${job.sysnam}`" class="inline-flex items-center px-2.5 py-1 rounded text-sm font-bold bg-primary-50 text-primary-700 border border-primary-200 hover:bg-primary-100 transition-colors">
        {{ job.sysnam }}
      </NuxtLink>
      ```

- [ ] **Step 2: 驗證詳細頁跳轉**
  開啟前端，訪問 `http://localhost:3000/job/{某ID}`，確認工作地點與職系已變為可點擊的連結，且能正確跳轉。

- [ ] **Step 3: Commit**
  ```bash
  git add frontend-nuxt/components/JobInfoCard.vue
  git commit -m "feat: convert place and sysnam metadata into internal links in JobInfoCard"
  ```

---

### Task 5: 後端 IndexNow 推送擴充

**Files:**
- Modify: `backend/scripts/sync_jobs.py`

- [ ] **Step 1: 擴充 IndexNow 推送 URL 列表**
  修改 `backend/scripts/sync_jobs.py` 中的 `_push_indexnow_and_invalidate_cache` 函數，除了推送具體職缺頁面外，還需提取縣市及職系並推送：
  ```python
      # ── IndexNow 推送 ──────────────────────────────────────────────────────
      if not indexnow_key:
          logging.info("INDEXNOW_KEY not set, skipping IndexNow push.")
          return

      # 從已插入的職缺中提取 ID（從 view_url 取 id 或直接用 rowid）
      job_ids = []
      places_set = set()
      sysnams_set = set()
      from app.Utils.FormatUtils import format_place

      for job in new_jobs:
          view_url = job.get("view_url", "")
          job_id = job.get("id")
          if job_id:
              job_ids.append(job_id)
          elif view_url:
              match = re.search(r'[?&]id=(\d+)', view_url, re.IGNORECASE)
              if match:
                  job_ids.append(match.group(1))
          
          # 提取縣市
          place_type = job.get("work_place_type")
          if place_type:
              formatted_place = format_place(place_type)
              # 去除行政區保留縣市名 (例如: 臺北市信義區 -> 臺北市)
              match_place = re.match(r'^[^縣市]+[縣市]', formatted_place)
              if match_place:
                  places_set.add(match_place.group(0))

          # 提取職系
          sysnam = job.get("sysnam")
          if sysnam and sysnam != "無":
              sysnams_set.add(sysnam)

      if not job_ids:
          logging.info("No job IDs found for IndexNow push.")
          return

      # 構建 URL 列表
      urls = [f"{site_domain}/job/{job_id}" for job_id in job_ids[:400]]
      for p in places_set:
          urls.append(f"{site_domain}/places/{p}")
      for s in sysnams_set:
          urls.append(f"{site_domain}/sysnams/{s}")

      # 去重並限額 500 筆
      urls = list(set(urls))[:500]
  ```

- [ ] **Step 2: 驗證 IndexNow 推送函數**
  可以使用 `backend/scripts/test_seo.py` 檢查健康度 API，或利用 Mock 測試 `sync_jobs.py` 的推送是否順利生成合適的 payload。

- [ ] **Step 3: Commit**
  ```bash
  git add backend/scripts/sync_jobs.py
  git commit -m "feat: push related places and sysnams routes during IndexNow sync"
  ```

---

### Task 6: 完整自動化驗證測試

**Files:**
- Modify: `backend/scripts/test_seo.py`

- [ ] **Step 1: 新增長青頁面的整合測試函數**
  在 `backend/scripts/test_seo.py` 中新增 `test_evergreen_pages` 函數，用於驗證剛建立的長青路由與 Sitemap：
  ```python
  def test_evergreen_pages(base_url: str) -> bool:
      section("9. 地區與職系長青登陸頁面驗證")
      passed = True
      
      # 1. 驗證 sitemap-static.xml 是否包含對應路徑
      try:
          r = requests.get(f"{base_url}/sitemap-static.xml", timeout=10)
          if r.status_code == 200:
              content = r.text
              # 抽樣檢查幾個重要的縣市和職系
              samples = ["/places/臺北市", "/places/高雄市", "/sysnams/綜合行政", "/sysnams/資訊處理"]
              for path in samples:
                  if path in content:
                      ok(f"Sitemap 包含長青路徑: {path}")
                  else:
                      fail(f"Sitemap 缺少長青路徑: {path}")
                      passed = False
          else:
              fail(f"無法存取 sitemap-static.xml (HTTP {r.status_code})")
              passed = False
      except Exception as e:
          fail(f"Sitemap 驗證出錯: {e}")
          passed = False

      # 2. 驗證前端長青網頁 HTML 渲染 (SSR)
      frontend_url = base_url.replace(":8002", ":3000")
      test_routes = [
          ("/places/臺北市", "臺北市"),
          ("/sysnams/綜合行政", "綜合行政")
      ]
      
      for path, expected_text in test_routes:
          try:
              r = requests.get(f"{frontend_url}{path}", timeout=15)
              if r.status_code == 200:
                  ok(f"{path} 回傳 200")
                  # 驗證 Title 與主要 SEO 關鍵字
                  if expected_text in r.text:
                      ok(f"  包含主要關鍵字: {expected_text}")
                  else:
                      fail(f"  缺少關鍵字: {expected_text}")
                      passed = False
                  
                  # 驗證 Canonical
                  if f'rel="canonical" href="https://opendgpa.shibaalin.com{path}"' in r.text or f"rel='canonical' href='https://opendgpa.shibaalin.com{path}'" in r.text:
                      ok(f"  有正確的 canonical 指向: {path}")
                  else:
                      warn(f"  canonical 標記有異，請檢查 HTML")
                      
                  # 驗證 BreadcrumbList
                  if 'BreadcrumbList' in r.text:
                      ok(f"  包含 BreadcrumbList 結構化資料")
                  else:
                      fail(f"  缺少 BreadcrumbList 結構化資料")
                      passed = False
              else:
                  fail(f"{path} 回傳異常狀態碼: {r.status_code}")
                  passed = False
          except Exception as e:
              warn(f"無法連線至前端頁面 {path}，請確認前端 Nuxt 伺服器已開啟: {e}")
              passed = False

      return passed
  ```

- [ ] **Step 2: 將測試整合至 `main()`**
  在 `backend/scripts/test_seo.py` 的 `main()` 中，加入結果判定：
  ```python
      results = {
          "robots.txt": test_robots_txt(base_url),
          "sitemap_index": False,
          "sitemap_static": test_sitemap_static(base_url),
          "sitemap_jobs": test_sitemap_jobs(base_url),
          "seo_health_api": test_seo_health_api(base_url),
          "indexnow_key": test_indexnow_key_file(base_url),
          "page_meta": test_page_meta(base_url),
          "duplicate_schemas": test_duplicate_schemas(base_url),
          "evergreen_pages": test_evergreen_pages(base_url), # 新增此項
      }
  ```

- [ ] **Step 3: 執行完整 SEO 驗證腳本**
  啟動前端（`npm run dev` 在 localhost:3000）與後端（localhost:8002），執行驗證：
  Run: `python backend/scripts/test_seo.py`
  Expected: 所有 9 項測試皆輸出 `✓` 通過（如果前端或後端未正確啟用，腳本將輸出具體錯誤）。

- [ ] **Step 4: Commit**
  ```bash
  git add backend/scripts/test_seo.py
  git commit -m "test: add integration test cases for places and sysnams evergreen pages"
  ```
