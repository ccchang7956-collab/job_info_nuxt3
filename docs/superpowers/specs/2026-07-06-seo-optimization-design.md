# 開放事求人 SEO 優化設計說明書 (SEO Optimization Design Spec)

- **日期**: 2026-07-06
- **狀態**: 待評審 (Pending Review)
- **作者**: Antigravity

---

## 1. 背景與問題診斷

目前「開放事求人」網站在 Google Search Console (GSC) 中的索引狀態為 **「已檢索 - 目前未建立索引 (Crawled - currently not indexed)」**。這代表 Google 爬蟲能夠正常抓取 HTML，但因內容合規性與結構問題而拒絕建立索引。

經診斷，本專案存在以下兩個主要的 SEO 致命障礙：
1. **FAQPage 結構化資料隱藏違規**：首頁宣告了 `FAQPage` JSON-LD 結構化資料，但首頁畫面上完全沒有這些問答內容，違反 Google「結構化資料內容必須可視」的政策。
2. **過期職缺主動 Noindex 拖累整站評級**：過期職缺被標記為 `noindex`。由於職缺時效短，導致網站 90% 以上的頁面都主動要求不索引，這嚴重降低了 Googlebot 對整站質量的評估，且失去了歷史職缺的長尾搜尋流量。

---

## 2. 設計方案與實作細節

本設計採用 **「優化內容合規性與開放歷史職缺索引」** 的策略來解決上述問題。

### 2.1. 首頁 FAQ 實體渲染 (pages/index.vue)
在首頁底部新增一個視覺美觀的常見問題（FAQ）摺疊元件，與 JSON-LD 中的問答完全對齊。

* **功能規格**：
  * 使用 HTML5 原生語意標籤 `<details>` 與 `<summary>`，即使在爬蟲不執行 JS 的情況下也能完美解析。
  * 摺疊狀態的切換使用簡單的 CSS 轉動動畫。
  * 引入 `@heroicons/vue/24/outline` 中的 `ChevronDownIcon`。
* **文字內容對齊**：
  1. **如何搜尋公務員職缺？** ➔ 在開放事求人首頁使用關鍵字搜尋，可依機關、職系、職稱、地點等條件篩選...
  2. **開放事求人的資料來源是什麼？** ➔ 資料來源為政府資料開放平臺之「行政院人事行政總處事求人機關徵才資料」...
  3. **什麼是重複開缺？** ➔ 當相同機關、相同職稱的職缺重複出現時，系統會標示為「重複開缺」...
  4. **可以在手機上使用嗎？** ➔ 是的，開放事求人支援 PWA，可以安裝到手機桌面...

### 2.2. 職缺詳細頁 SEO 與 UI 調整 (pages/job/[id].vue)
開放歷史職缺的索引，並增加過期警告與引導。

* **SEO 規格**：
  * 修改 `useSeoMeta`，將 `robots` 統一調整為 `'index,follow'`，不再對已過期職缺進行 `noindex`。
  * 保持 `JobPosting` Schema 的 `validThrough` 設定。
* **UI 防呆導流橫幅**：
  * 當 `isJobExpired` 為 `true` 時，在頁面頂部顯示琥珀色（Amber）的警告橫幅。
  * 引入 `ExclamationTriangleIcon` 作為警告圖示。
  * 橫幅包含提示文字：`此職缺已截止報名` 與 `本職缺已於 {job.date_to} 截止收件，僅保留歷史資料供參考。`
  * 橫幅右側提供「查看最新職缺列表」按鈕，點擊導向回首頁 `/`。

---

## 3. 變更影響檔案列表

* [frontend-nuxt/pages/index.vue](file:///Users/ccchang/Project/job_info_nuxt3/frontend-nuxt/pages/index.vue)
* [frontend-nuxt/pages/job/\[id\].vue](file:///Users/ccchang/Project/job_info_nuxt3/frontend-nuxt/pages/job/%5Bid%5D.vue)

---

## 4. 自審檢查表 (Self-Review Checklist)

- [x] **無預留預留欄位**：無 any TODO, TBD 或未決定細節。
- [x] **前後一致性**：首頁 FAQ 元件中的文字與現有 JSON-LD 完全一致。
- [x] **範疇控制**：僅限於首頁 FAQ 渲染與詳細頁面的 SEO/UI 警告，不涉及其他無關邏輯。
