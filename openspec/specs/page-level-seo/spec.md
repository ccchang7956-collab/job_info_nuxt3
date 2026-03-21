## ADDED Requirements

### Requirement: 每個頁面有獨立的 title 和 description
每個頁面 SHALL 使用 `useSeoMeta` 設定獨立的 `title`、`description`、`ogTitle`、`ogDescription`，不可使用相同的預設值。

#### Scenario: 職缺詳情頁顯示動態 title
- **WHEN** 使用者瀏覽職缺詳情頁，該職缺為「內政部 - 科員」
- **THEN** 頁面 title MUST 包含「內政部」和「科員」關鍵字（例如：`內政部 科員 - 開放事求人`）

#### Scenario: 統計圖表頁有獨立 meta
- **WHEN** 使用者瀏覽 `/charts` 頁面
- **THEN** 頁面 MUST 有獨立的 title 和 description，描述該頁面的功能（統計圖表分析）

### Requirement: 每個頁面有 canonical URL
每個頁面 SHALL 包含 `<link rel="canonical">` 標籤，指向該頁面的標準 URL。

#### Scenario: 首頁 canonical URL
- **WHEN** 使用者瀏覽首頁
- **THEN** HTML MUST 包含 `<link rel="canonical" href="https://opendgpa.shibaalin.com/">` 

#### Scenario: 職缺詳情頁 canonical URL
- **WHEN** 使用者瀏覽 `/job/123`
- **THEN** HTML MUST 包含 `<link rel="canonical" href="https://opendgpa.shibaalin.com/job/123">`

### Requirement: Open Graph 完整設定
每個頁面 SHALL 包含完整的 Open Graph meta 標籤（`og:title`、`og:description`、`og:url`、`og:type`、`og:image`），確保社群分享時顯示正確的預覽。

#### Scenario: 職缺詳情頁社群分享預覽
- **WHEN** 使用者在 Facebook/LINE 分享一個職缺連結
- **THEN** 分享預覽 MUST 顯示該職缺的機關名稱、職稱，以及網站 OG 圖片

### Requirement: Sitemap 包含完整資訊
`sitemap.xml` SHALL 為每個 URL 包含 `<lastmod>`、`<changefreq>`、`<priority>` 屬性，幫助搜尋引擎判斷頁面更新頻率與重要性。

#### Scenario: Sitemap 職缺頁面有正確的 lastmod
- **WHEN** 搜尋引擎爬蟲請求 `/sitemap.xml`
- **THEN** 每個職缺 URL MUST 包含 `<lastmod>` 設為該職缺的公告日期
- **THEN** 首頁 MUST 設定 `<priority>1.0</priority>` 和 `<changefreq>daily</changefreq>`
