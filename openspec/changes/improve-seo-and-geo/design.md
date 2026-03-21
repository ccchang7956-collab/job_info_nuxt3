## Context

「開放事求人」(opendgpa.shibaalin.com / job.ccchang.tw) 是一個 Nuxt 3 SSR + FastAPI 的全端網站，提供台灣公務人員職缺查詢。目前已具備基礎 SEO 設施：`robots.txt`（已允許 AI 爬蟲）、`llms.txt`、`sitemap.xml`（後端代理）、Google Analytics (nuxt-gtag)、首頁 FAQ Schema、OG meta tags。但各頁面的結構化資料與 AI 可讀性仍有大幅改善空間。

## Goals / Non-Goals

**Goals:**
- 每個職缺詳情頁顯示 Google Rich Results（JobPosting Schema）
- 每個頁面有完整且獨立的 SEO meta（title、description、canonical、OG）
- AI 搜尋引擎能正確理解並引用網站內容（GEO 優化）
- Sitemap 包含完整的 lastmod/priority 資訊

**Non-Goals:**
- 不做付費 SEO 工具整合（如 Ahrefs、SEMrush）
- 不做多語系 (i18n) SEO（目前僅繁體中文）
- 不做 AMP 頁面
- 不重構現有前端元件架構

## Decisions

### 1. 結構化資料使用 JSON-LD（非 Microdata）
- **選擇**: 使用 `<script type="application/ld+json">` 方式嵌入
- **原因**: Google 官方推薦 JSON-LD；Nuxt 3 的 `useHead` 可直接注入 script 標籤
- **替代方案**: Microdata（嵌入 HTML 屬性中），但維護成本高且與 Vue template 混合不佳

### 2. 使用 Nuxt 內建 `useSeoMeta` + `useHead` composable
- **選擇**: 不安裝第三方 SEO 模組（如 `nuxt-seo`）
- **原因**: 專案需求明確，`useSeoMeta` 已涵蓋所有需求；減少依賴
- **替代方案**: `@nuxtjs/seo` 套件，但引入不必要的複雜度

### 3. `llms-full.txt` 放在 `public/` 目錄作為靜態檔
- **選擇**: 靜態檔案而非動態 API 端點
- **原因**: 內容變動頻率低（功能描述為主），靜態檔更簡單且效能最佳
- **替代方案**: 後端動態生成含最新資料統計，但增加不必要的複雜度

### 4. 結構化資料在各頁面的 `<script setup>` 中定義
- **選擇**: 不建立共用 composable
- **原因**: 每個頁面的 Schema 類型不同（JobPosting vs FAQPage vs WebSite），共用的效益有限
- **替代方案**: 建立 `useSchemaOrg` composable，但增加間接層

### 5. Sitemap 增強在後端處理
- **選擇**: 修改現有的後端 sitemap 端點
- **原因**: Sitemap 已由後端 FastAPI 生成並透過 Nuxt proxy 提供，在原處增強最自然
- **替代方案**: 改用 `nuxt-simple-sitemap` 模組在前端生成，但需大幅重構

## Risks / Trade-offs

- **JobPosting Schema 資料完整性** → Schema 需要 `datePosted`、`validThrough` 等欄位，需確認後端 API 已提供這些資料。若欄位缺失則使用合理預設值
- **OG Image 域名一致性** → 目前 OG image 指向 `opendgpa.shibaalin.com`，需確認這是否為主要使用的域名。若有域名遷移計畫需同步更新
- **AI 爬蟲流量增加** → 開放 AI 爬蟲可能增加伺服器負載。現有 rate limiting 應足以應對
- **結構化資料驗證** → 需使用 Google Rich Results Test 工具驗證 Schema 正確性
