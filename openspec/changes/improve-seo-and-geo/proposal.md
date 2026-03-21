## Why

Google 搜尋流量是「開放事求人」網站的主要流量來源，但目前 SEO 設施尚有不足——缺少職缺頁結構化資料 (JobPosting Schema)、各頁面 canonical/meta 不完整、`llms.txt` 未包含完整版本。同時，AI 搜尋引擎（如 ChatGPT、Perplexity、Google AI Overview）日漸成為使用者獲取資訊的途徑，我們需要針對 Generative Engine Optimization (GEO) 進行優化，確保 AI 能正確理解並引用我們的內容。現在是優化的好時機，因為網站已具備 SSR、Sitemap、`robots.txt` 等基礎設施。

## What Changes

### SEO 改進
- 為職缺詳情頁加入 **JobPosting** JSON-LD 結構化資料，讓 Google 搜尋結果顯示 Rich Results
- 為每個頁面加入完整的 `useSeoMeta` 設定（title、description、canonical URL、OG tags）
- 新增 **WebSite** + **SearchAction** Schema，支援 Google Sitelinks Searchbox
- 新增 **BreadcrumbList** Schema 於職缺詳情頁
- 統一 OG image URL 為主域名（目前使用 `opendgpa.shibaalin.com`）
- 後端 Sitemap 加入 `<lastmod>`、`<changefreq>`、`<priority>` 等屬性
- 加入 `<meta name="theme-color">` 提升行動搜尋外觀

### GEO (AI 引擎優化) 改進
- 新增 `llms-full.txt`，提供 AI 爬蟲完整的網站功能描述與 API 結構
- 在 `robots.txt` 中加入 `llms.txt` 與 `llms-full.txt` 的連結
- 在各頁面 HTML 加入語義化 `<article>`、`<section>` 標籤，提升 AI 內容理解
- 後端 API 回應加入適當的 Cache-Control 標頭，方便 AI 爬蟲快取
- 在 `<head>` 加入 `<link rel="alternate" type="application/llms+txt">` 標記

## Capabilities

### New Capabilities
- `structured-data`: 為各頁面加入 JSON-LD 結構化資料（JobPosting、WebSite、BreadcrumbList、Organization）
- `geo-optimization`: AI 搜尋引擎優化，包含 llms-full.txt、語義化 HTML、AI 爬蟲友善標頭
- `page-level-seo`: 各頁面獨立的 SEO meta 設定（title、description、canonical、OG）

### Modified Capabilities
_無現有 spec 需要修改_

## Impact

- **前端** (`frontend-nuxt/`): 修改 `nuxt.config.ts`、各頁面 `.vue` 檔案的 `useSeoMeta`/`useHead`，新增 `llms-full.txt`
- **後端** (`backend/`): 增強 Sitemap 端點回應內容，API 回應加入 cache 標頭
- **公開資源** (`public/`): 更新 `robots.txt`，新增 `llms-full.txt`
- **無破壞性變更**: 所有改動皆為新增或增強，不影響現有功能
