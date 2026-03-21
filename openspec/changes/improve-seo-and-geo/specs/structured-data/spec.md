## ADDED Requirements

### Requirement: 職缺詳情頁 JobPosting Schema
每個職缺詳情頁 (`/job/[id]`) SHALL 包含符合 Google 規範的 `JobPosting` JSON-LD 結構化資料，包含以下欄位：`title`、`description`、`datePosted`、`validThrough`、`hiringOrganization`、`jobLocation`、`employmentType`。

#### Scenario: 正常顯示 JobPosting Schema
- **WHEN** 使用者瀏覽一個有效的職缺詳情頁 `/job/123`
- **THEN** HTML 中 MUST 包含一個 `<script type="application/ld+json">` 標籤，內含 `@type: "JobPosting"` 及所有必填欄位

#### Scenario: 缺少部分欄位時使用預設值
- **WHEN** 後端 API 回傳的職缺資料缺少 `validThrough` 欄位
- **THEN** 系統 SHALL 使用 `date_to` 欄位作為替代值

### Requirement: 首頁 WebSite + SearchAction Schema
首頁 (`/`) SHALL 包含 `WebSite` JSON-LD 結構化資料，並嵌入 `SearchAction`，讓 Google 搜尋結果可顯示 Sitelinks Searchbox。

#### Scenario: 首頁顯示 WebSite Schema
- **WHEN** 使用者瀏覽首頁
- **THEN** HTML 中 MUST 包含 `@type: "WebSite"` 的 JSON-LD，並包含 `potentialAction` 搭配 `SearchAction`

### Requirement: 職缺詳情頁 BreadcrumbList Schema
職缺詳情頁 SHALL 包含 `BreadcrumbList` JSON-LD，表示導覽路徑：首頁 → 職缺列表 → 當前職缺。

#### Scenario: 麵包屑顯示正確的導覽路徑
- **WHEN** 使用者瀏覽 `/job/123`（機關名稱為「內政部」、職稱為「科員」）
- **THEN** BreadcrumbList MUST 包含三層：「首頁」→「職缺列表」→「內政部 - 科員」

### Requirement: Organization Schema
首頁 SHALL 包含 `Organization` JSON-LD 結構化資料，包含網站名稱、URL、Logo。

#### Scenario: 首頁顯示 Organization 資訊
- **WHEN** 使用者瀏覽首頁
- **THEN** HTML 中 MUST 包含 `@type: "Organization"` 的 JSON-LD，含 `name`、`url`、`logo` 欄位
