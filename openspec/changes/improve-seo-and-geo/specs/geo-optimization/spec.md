## ADDED Requirements

### Requirement: 提供 llms-full.txt 完整版本
網站 SHALL 在 `/llms-full.txt` 路徑提供完整的 AI 可讀文件，包含：網站功能詳述、所有頁面路徑與用途、API 端點說明、資料欄位定義、常見問題解答。

#### Scenario: AI 爬蟲存取 llms-full.txt
- **WHEN** AI 爬蟲（如 GPTBot）請求 `/llms-full.txt`
- **THEN** 系統 MUST 回傳完整的純文字內容，包含網站完整描述與功能列表

### Requirement: robots.txt 指向 LLMs 檔案
`robots.txt` SHALL 包含指向 `llms.txt` 和 `llms-full.txt` 的引用連結。

#### Scenario: robots.txt 包含 LLMs 連結
- **WHEN** 爬蟲請求 `/robots.txt`
- **THEN** 檔案中 MUST 包含 `llms.txt` 和 `llms-full.txt` 的完整 URL

### Requirement: HTML head 包含 llms.txt 連結
每個頁面的 `<head>` SHALL 包含 `<link rel="alternate" type="text/plain" href="/llms.txt">` 標籤，方便 AI 爬蟲發現 LLMs 文件。

#### Scenario: 頁面 head 包含 llms.txt link tag
- **WHEN** 任何頁面被載入
- **THEN** HTML `<head>` 中 MUST 包含指向 `/llms.txt` 的 link 標籤

### Requirement: 語義化 HTML 結構
各主要頁面 SHALL 使用語義化 HTML 標籤（`<article>`、`<section>`、`<nav>`、`<main>`），提升 AI 爬蟲對內容結構的理解能力。

#### Scenario: 職缺詳情頁使用 article 標籤
- **WHEN** 使用者瀏覽職缺詳情頁
- **THEN** 職缺內容區域 MUST 使用 `<article>` 標籤包裹

#### Scenario: 首頁搜尋結果使用 section 標籤
- **WHEN** 使用者瀏覽首頁
- **THEN** 搜尋結果區域 MUST 使用 `<section>` 標籤包裹，並包含具描述性的 `aria-label`

### Requirement: API 回應加入 Cache-Control 標頭
後端 API 的公開端點 SHALL 在回應中加入適當的 `Cache-Control` 標頭，讓 AI 爬蟲能有效快取存取過的內容。

#### Scenario: 職缺列表 API 回應包含快取標頭
- **WHEN** 爬蟲請求 `/api/jobs`
- **THEN** 回應 MUST 包含 `Cache-Control: public, max-age=300` 標頭（5 分鐘快取）
