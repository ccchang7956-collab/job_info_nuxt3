# SEO/GEO 優化：建立縣市與職系長青登陸頁面 (Evergreen Landing Pages)

## 1. 上下文與背景 (Context)
「開放事求人」系統中的具體公務員職缺（如：某科員職位）生命週期很短（通常僅公告 7~14 天），導致大量被 Google 索引的職缺頁面很快變為逾期或 404，不利於累積長期的搜尋引擎權重（PageRank）。
為了解決此問題，本設計提案建立一組**網址永久固定且持續更新**的「地區縣市」與「職能職系」長青登陸頁面。這些頁面能作為搜尋引擎穩定的流量入口，並大幅強化地方搜尋（GEO）和職類關鍵字的 SEO 排名。

## 2. 功能需求與場景 (Requirements & Scenarios)

### 前端長青頁面路由
*   **縣市職缺頁面**：新增路由 `/places/[place]`，例如 `/places/臺北市`、`/places/高雄市`。
*   **職系職缺頁面**：新增路由 `/sysnams/[sysnam]`，例如 `/sysnams/綜合行政`、`/sysnams/資訊處理`。
*   **SSR 渲染與效能**：所有頁面必須在 Nuxt 3 伺服器端（SSR）完成渲染，確保搜尋爬蟲抓取到的是完整的 HTML，並繼承現有的 Cache-Control（5 分鐘）快取機制。
*   **SEO 優化文本**：每個分類頁面必須呈現專屬的分類介紹文字段落，避免被搜尋引擎判定為「內容薄弱的搜尋結果頁」。

### 頁面層級 SEO Meta 與結構化資料 (JSON-LD)
*   **縣市頁 Meta 範例 (臺北市)**：
    *   **Title**：`最新 臺北市 公務人員職缺列表｜事求人職缺查詢 - 開放事求人`
    *   **Description**：`即時同步行政院人事行政總處事求人開放資料，提供臺北市最完整的公務人員職缺搜尋、歷史開缺次數與留言討論。`
*   **職系頁 Meta 範例 (綜合行政)**：
    *   **Title**：`最新 綜合行政 職系公務員職缺列表｜事求人職缺查詢 - 開放事求人`
    *   **Description**：`為您整理全國綜合行政職系最新公務人員事求人開缺，並包含同職位歷史開缺次數、重複開缺警示與網友留言討論。`
*   **結構化資料 (JSON-LD)**：
    *   每個長青頁面皆必須嵌入 `BreadcrumbList` 結構，引導爬蟲辨識網站階層（首頁 -> 地區 -> 縣市職缺）。
    *   嵌入 `ItemList` 結構，列出該分類前幾名熱門的職缺連結與名稱。

### 全站內部連結網絡佈局
*   **全域頁尾 (Footer)**：新增「熱門快速導覽」區，列出六都（臺北市、新北市、桃園市、臺中市、臺南市、高雄市）與六大熱門職系（綜合行政、人事行政、會計審計、土木工程、資訊處理、電機工程）的長青頁網址。
*   **首頁底部**：新增「依縣市或職系快速查找職缺」導覽卡片，列出完整 22 個台灣縣市（分組顯示）與前 15 大熱門職系的長青網址連結。
*   **職缺詳情頁**：將原有的「工作地點」與「職系」欄位文字轉化為動態連結（NuxtLink），點擊分別引導回對應的地區長青頁與職系長青頁。

### 後端 Sitemap 與 IndexNow 推送整合
*   **Sitemap 擴充**：更新 FastAPI `SeoService.py` 中的 `sitemap-static.xml`，將 22 個縣市與所有職系的長青網址併入靜態 Sitemap。
    *   將這批網址的優先級（Priority）設為 `0.9`，更新頻率（Changefreq）設為 `daily`。
    *   其 `<lastmod>` 應動態設為最新職缺同步日期。
*   **IndexNow 關聯推送**：在後端 `sync_jobs.py` 同步新職缺時，除了推送新職缺 URL，也應解析新職缺的「地區」與「職系」，並將對應的 `/places/[place]` 與 `/sysnams/[sysnam]` 網址一併推送給 IndexNow，加速 Bing 等搜尋引擎重新收錄分類頁。

---

## 3. 詳細設計與程式碼修改說明

### 前端 (Nuxt 3) 修改

#### 1. 新增地區長青頁：`frontend-nuxt/pages/places/[place].vue`
此頁面會透過 `route.params.place` 獲取地區名稱，向 `/api/jobs?places=[縣市名稱]` 請求數據。設計與 `pages/index.vue` 共享元件，包括分頁、表格與卡片，但特別配置 SEO 首屏文本。

#### 2. 新增職系長青頁：`frontend-nuxt/pages/sysnams/[sysnam].vue`
此頁面會透過 `route.params.sysnam` 獲取職系名稱，向 `/api/jobs?sysnam=[職系名稱]` 請求數據。

#### 3. 修改全域版面（`frontend-nuxt/layouts/default.vue`）
在 `<footer>` 標籤中，添加六都與六大熱門職系的分類連結，實現全站的 PageRank 自動輸送。

#### 4. 修改首頁底部（`frontend-nuxt/pages/index.vue`）
在職缺列表展示結束處，增設 22 縣市與熱門職系的快速導覽，建立一個淺層級的連結網格。

#### 5. 修改詳細頁卡片（`frontend-nuxt/components/JobInfoCard.vue`）
在卡片中將地區與職系字段轉化為 `<NuxtLink>`。

---

### 後端 (FastAPI) 修改

#### 1. 更新 sitemap-static.xml（`backend/app/Services/SeoService.py`）
擴充 `SeoService.get_sitemap_static()`，將 22 個縣市與熱門職系的路徑拼裝進 `sitemap-static.xml`。
`<lastmod>` 使用最新職缺同步日期。

#### 2. 更新 IndexNow 推送邏輯（`backend/scripts/sync_jobs.py`）
在 `_push_indexnow_and_invalidate_cache()` 中，從新入庫的職缺列表提取不重複的縣市與職系，並拼裝成對應的長青頁網址，與具體職缺頁一併推送給 IndexNow。

---

## 4. 驗證與風險評估 (Verification & Risks)
*   **路由快取效能**：確保 SWR 快取運作正常，限制快取總體記憶體。
*   **Google 結構化檢測**：上線後需進行 Rich Results Test 檢測 JSON-LD 麵包屑導航。
