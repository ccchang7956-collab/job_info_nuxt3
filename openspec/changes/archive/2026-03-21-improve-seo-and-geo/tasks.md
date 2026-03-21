## 1. 頁面層級 SEO Meta 設定

- [x] 1.1 為職缺詳情頁 (`pages/job/[id].vue`) 加入動態的 `useSeoMeta`（title 含機關+職稱、description 含關鍵資訊、ogUrl 含完整 URL）
- [x] 1.2 為統計圖表頁 (`pages/charts.vue`) 加入獨立的 `useSeoMeta` 設定
- [x] 1.3 為留言頁 (`pages/comments.vue`) 加入獨立的 `useSeoMeta` 設定
- [x] 1.4 為更新日誌頁 (`pages/logs.vue`) 加入獨立的 `useSeoMeta` 設定
- [x] 1.5 為關於頁 (`pages/about.vue`) 加入獨立的 `useSeoMeta` 設定
- [x] 1.6 為隱私權政策頁 (`pages/privacy-policy.vue`) 加入獨立的 `useSeoMeta` 設定
- [x] 1.7 為每個頁面加入 `<link rel="canonical">` 標籤

## 2. JSON-LD 結構化資料

- [x] 2.1 在首頁加入 `WebSite` + `SearchAction` JSON-LD Schema
- [x] 2.2 在首頁加入 `Organization` JSON-LD Schema
- [x] 2.3 在職缺詳情頁加入 `JobPosting` JSON-LD Schema（使用 API 回傳的職缺資料動態生成）
- [x] 2.4 在職缺詳情頁加入 `BreadcrumbList` JSON-LD Schema

## 3. GEO 優化（AI 搜尋引擎）

- [x] 3.1 建立 `public/llms-full.txt`，包含完整的網站功能描述、頁面路徑、API 結構、資料欄位定義
- [x] 3.2 更新 `public/robots.txt`，加入 `llms.txt` 和 `llms-full.txt` 的完整 URL
- [x] 3.3 在 `nuxt.config.ts` 的 `app.head.link` 中加入 `<link rel="alternate">` 指向 `llms.txt`
- [x] 3.4 在職缺詳情頁加入語義化 HTML 標籤（`<article>` 包裹職缺內容）
- [x] 3.5 在首頁加入語義化 HTML 標籤（`<section>` 包裹搜尋結果，加 `aria-label`）

## 4. Sitemap 增強

- [x] 4.1 修改後端 Sitemap 端點，為每個 URL 加入 `<lastmod>`、`<changefreq>`、`<priority>` 屬性
- [x] 4.2 首頁設定 `priority=1.0`、`changefreq=daily`；職缺頁設定 `priority=0.8`、使用公告日期為 `lastmod`

## 5. 後端 API 增強

- [x] 5.1 為公開 API 端點加入 `Cache-Control: public, max-age=300` 回應標頭

## 6. 驗證

- [x] 6.1 使用 Google Rich Results Test 驗證 JobPosting Schema
- [x] 6.2 使用 Google Rich Results Test 驗證 FAQPage Schema
- [x] 6.3 確認所有頁面的 meta tags 正確輸出
- [x] 6.4 確認 `robots.txt` 和 `llms-full.txt` 可正常存取
- [x] 6.5 確認 `sitemap.xml` 包含完整的 lastmod/priority 資訊
