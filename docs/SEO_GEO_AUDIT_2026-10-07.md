# SEO / GEO 與 Google 索引複查

日期：2026-10-07（Asia/Taipei）。範圍：專案程式碼、正式站公開 HTTP GET / HTML / XML，以及使用者提供的 Search Console 樣本。本次未修改應用程式或部署，也未登入 Search Console。

更新：使用者後續授權修正、提交、推送及重啟 Docker，已完成本機修改、44 項測試及正式部署驗收。下文保留修改前稽核結果，實作與部署狀態見 [修正紀錄](SEO_GEO_CHANGES_2026-10-07.md)。

## 結論與證據限制

使用者確認下列 10 筆屬於「已檢索－目前尚未建立索引」，最近檢索日期為 10 月 2～6 日。逐筆 GET 都回 HTTP 200、robots meta `index,follow`、自我 canonical，沒有 X-Robots-Tag，也包含 SSR 職缺內容。全部在 2026 年 1 月截止，頁面都有已截止提示。

這批樣本目前沒有技術上的 noindex 阻擋。歷史公告的需求、與官方公告的相似內容及獨有資訊價值，應列為主要調查方向；這是根據頁面特徵的推論，不能當成 Google 已證實的排除原因，也不能推論首頁或有效職缺都未收錄。內容並非空殼，不能直接歸因於文字太短。

Google 官方對此狀態的定義是已檢索但未收錄，未來可能收錄也可能不收錄；状态本身不提供根因。[網頁索引報表](https://support.google.com/webmasters/answer/7440203?hl=zh-Hant)。

尚缺：Google 當次抓取的 HTML、Google 選取的 canonical、首頁與有效職缺的 Search Console 狀態，以及真實 Googlebot 的 Cloudflare／伺服器事件。使用者後續提供 noindex 類別的 10 筆樣本，結果見下方。

## 使用者提供的樣本

所有列出的職缺目前都符合上述 HTTP／robots／canonical 結果。

| 職缺 ID | 機關／職稱 | 截止日期 | Search Console 上次檢索 |
| --- | --- | --- | --- |
| 81571 | 新竹市殯葬管理所／約用人員（三班） | 2026-01-08 | 2026-10-06 |
| 81962 | 臺中市政府政風處／職代約僱人員 | 2026-01-12 | 2026-10-06 |
| 81647 | 新竹市政府／約用人員 | 2026-01-16 | 2026-10-05 |
| 82359 | 彰化縣北斗鎮公所／約僱職務代理人 | 2026-01-23 | 2026-10-05 |
| 79603 | 苗栗縣政府衛生局／藥師 | 2026-01-08 | 2026-10-05 |
| 80995 | 新北市政府衛生局／股長 | 2026-01-19 | 2026-10-04 |
| 82248 | 高雄市立民生醫院／醫師 | 2026-01-31 | 2026-10-04 |
| 82435 | 臺北市立啟聰學校／幹事 | 2026-01-20 | 2026-10-03 |
| 81424 | 南投縣政府／約僱職務代理人 | 2026-01-09 | 2026-10-03 |
| 82492 | 嘉義縣義竹鄉公所／約僱人員 | 2026-01-16 | 2026-10-02 |

三份職缺 sitemap 合計 2,103 個不重複 URL，均不含這 10 筆。後端目前只列出截止日期在明天以後的職缺；缺少 sitemap entry 不等於禁止索引，使用者提供的檢索紀錄也已證明 Google 知道這些 URL。

## 正式站複查：舊問題已修復

| 項目 | 本次結果 |
| --- | --- |
| `/robots.txt` | 200，允許一般搜尋抓取，僅一般爬蟲群組禁止 `/logs`；本次沒有看到 5 月報告中的 AI Disallow 注入 |
| `/sitemap.xml` | 200、可解析的 sitemap index，列出 static 與 jobs 1～3 |
| `/sitemap-static.xml` | 200、45 個 URL |
| `/sitemap-jobs-1.xml` | 200、1,000 個 URL |
| `/sitemap-jobs-2.xml` | 200、1,000 個 URL |
| `/sitemap-jobs-3.xml` | 200、103 個 URL |
| 臺北市及綜合行政第 2 頁 | 正確顯示第 2 頁、清單與第 1 頁不同，canonical 包含 `?page=2` |
| 首頁 | 200、index、自我 canonical，初始 HTML 有職缺與內部連結 |
| 有效職缺 `/job/138230` | 200、index、自我 canonical，JobPosting 截止 2026-10-30 |
| 不存在的 `/job/999999999` | 正確回 404，meta 仍是 index；HTTP 404 本身不符合一般索引條件 |
| `/logs` | 200、noindex,follow，屬目前程式刻意排除 |
| `/places/臺北市?page=999` | 404、noindex,follow，屬超出實際頁數的預期排除 |
| `/places/seo-audit-invalid-county` | 200、index、空列表，應修正不存在分類的處理 |
| `/charts` | 200、index，但 SSR 沒有統計表；數據在 onMounted 後載入 |

9 月 30 日報告中的子 sitemap 404 和分類分頁問題，這次正式站已無法重現；不要再把當時部署前結果當作現在的缺陷。

以 Googlebot user-agent 抽查首頁、有效職缺及歷史職缺 81571，均回 200。這只是模擬 user-agent，不能代替 Google 真實 IP 的抓取。一個未設定 user-agent 的 Python sitemap 請求回 403，改用 `Mozilla/5.0` 後成功；尚不確定是 CDN、來源 IP、user-agent 或其他規則造成，不能據此宣稱 Googlebot 被封鎖。應核對 Cloudflare 事件及 Search Console 實際網址測試。

## 如何診斷 noindex 類別

### 使用者提供的 noindex 樣本與歷史根因

| 職缺 ID | 截止日期 | Search Console 上次檢索 |
| --- | --- | --- |
| 81682 | 2026-01-08 | 2026-07-06 |
| 81684 | 2026-01-09 | 2026-07-06 |
| 81373 | 2026-01-09 | 2026-07-05 |
| 81398 | 2026-01-13 | 2026-07-04 |
| 81553 | 2026-02-28 | 2026-07-04 |
| 80990 | 2026-01-09 | 2026-07-04 |
| 79080 | 2026-01-16 | 2026-07-03 |
| 80302 | 2026-01-13 | 2026-07-02 |
| 82209 | 2026-01-19 | 2026-07-02 |
| 80073 | 2026-01-21 | 2026-07-01 |

逐筆實測全部回 200、index,follow、自我 canonical，沒有 X-Robots-Tag，有完整 SSR 職缺內容。

Git commit `6b2f28a`（2026-07-06 22:43:57 +08:00）將舊規則 `(job.value && isJobExpired.value) ? 'noindex,follow' : 'index,follow'` 改為允許過期職缺索引。隨後 `a943003`（同日 22:46:24）補上 API 錯誤處理。

這組樣本在 Google 上次抓取時均已過期，且檢索日期落在修正當日或之前。因此，**舊版過期職缺 noindex 規則是高度吻合的歷史原因**；報表很可能尚未反映修正後內容。當年的實際部署時間、Google 精確抓取時間與歷史 HTML 尚未取得，故不把 Git 提交時間當成正式站部署證明。

處理順序：先在 Search Console 用 81682 及 81553 執行「測試實際網址」，確認是否允許索引及 HTML 內容；再針對 noindex 問題啟動修正驗證。可對少量有搜尋價值且確實更新的歷史頁要求索引，不需反覆提交所有歷史 URL。解除 noindex 後仍可能成為「已檢索－目前尚未建立索引」，因為允許索引不等於 Google 決定收錄。[Search Console 驗證與排除原因說明](https://support.google.com/webmasters/answer/7440203?hl=zh-Hant)。

### 目前程式規則

程式來源：

- `frontend-nuxt/pages/logs.vue:128`：固定 noindex。
- `frontend-nuxt/pages/places/[place].vue:34` 與 `pages/sysnams/[sysnam].vue:34`：超出實際分頁範圍才 noindex。
- `frontend-nuxt/pages/job/[id].vue:152`：API 無錯誤、但沒有 job 時才 noindex；有效及過期 job 都 index。API 真 404 走 fetchError，目前 meta 仍 index，但 HTTP 回 404。
- `frontend-nuxt/nuxt.config.ts:89`：全域 index,follow。

若其他 noindex 報表樣本是日誌或無效分頁，可以保留排除。若是有效職缺，對照上次檢索 HTML 與即時 HTML，確認舊版、快取、API 空結果或 CDN 標頭，不能把這組歷史職缺的結論直接套用到全站。

`noindex` 與 robots.txt 禁止抓取是不同機制；Google 必須能抓到頁面才能讀取 noindex。目前 `/logs` 同時禁止抓取及 noindex，若目標是讓 Google 穩定讀到 noindex，應允許其抓取此頁。[Google noindex 說明](https://developers.google.com/search/docs/crawling-indexing/block-indexing)。

## 改善優先順序

### 1. 先確認重要頁的實際索引結果

在 Search Console 分別檢查首頁、有效職缺 138230、臺北市分類與綜合行政分類，再與歷史公告 81571 比較。記錄索引原因、上次檢索、擷取狀態、是否允許索引，以及使用者宣告／Google 選取的 canonical。檢查已抓取 HTML 和「測試實際網址」結果，兩者代表不同時間。

技術正常仍不代表保證收錄。追蹤有效職缺在截止前的索引率、穩定分類頁的曝光／點擊，歷史頁分開統計，避免用全部歷史 URL 的未索引比例代表全站表現。

### 2. 用既有資料建立獨有的 SEO / GEO 內容

- 強化既有 `/places/…`、`/sysnams/…`：顯示實際目前職缺数、職等分布、機關分布、近 30／90 日變化，以及更新時間。應由資料庫計算，讓數據在 SSR HTML 可讀，避免只換分類名稱的制式介紹。
- 增加穩定機關頁：機關目前職缺、歷史徵才時間線、同職稱再公告次數、可驗證的趨勢及相關分類連結。
- 歷史詳情頁保留明確截止提示，增加正在招募的相關職缺連結與可驗證的歷史分析。若只想保留檔案、沒有搜尋需求，也可依產品策略選擇 noindex；不必全站一律刪除或一律索引。
- 「重複開缺」只代表再公告的觀測結果，不能單憑公告次數斷言流動率高或工作不穩定；說明判定方式與資料限制，提升引用可信度。
- 用自然語言解答使用者的實際問題，附上資料來源、統計期間及官方公告連結；不要大量生成僅替換機關／地名的泛用段落。

對 Google 的生成式搜尋，先建立索引是基本條件。Google 明確說不使用 llms.txt 作為特殊優化，也沒有專用 GEO schema；應把投入集中在可抓取、可讀、獨有且可信的內容。[Google 生成式搜尋最佳化指南](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)。其他 AI 平台需個別驗證爬蟲規則與 CDN 放行，不能把允許訓練爬蟲等同搜尋引用保證。

### 3. 補齊可直接修正的技術項目

| 優先度 | 項目 | 建議與驗收 |
| --- | --- | --- |
| 高 | `/charts` 數據僅 client fetch | 用 await useFetch／useAsyncData 提供初始統計；SSR HTML 有摘要、期間、數據表，圖表仍可互動 |
| 高 | 不存在的分類回 200 空內容 | 縣市依完整合法集合驗證，職系依完整來源資料驗證；不存在者 404，有效但零職缺者保留有用內容 |
| 高 | 首頁／分類 API 錯誤仍可能回 200 | 暫時取不到資料回適當 5xx，避免把錯誤空頁當成正常內容；不要以 noindex 處理暫時故障 |
| 中 | sitemap lastmod 失真 | `SeoService.py:137–151` 分類每天填今天，首頁／charts 卻固定 2025-12-30；採實際內容異動時間，無可靠時間可省略。index 的 static 子檔 lastmod 也應同步 |
| 中 | 所有頁面 hreflang 指向首頁 | `nuxt.config.ts:107–108`；單語網站可移除，或提供正確逐頁對應 |
| 中 | JobPosting 資料可信度 | `job/[id].vue:191` 所有機關 sameAs 指向同一事求人入口，應改機關官方網址或省略；福利、聘僱類型也應依實際公告，不要對所有工作填同一公務員福利 |

過期職缺目前都有過去的 validThrough，這是官方允許的過期處理方式之一。可另考慮移除過期頁的 JobPosting、保留歷史網頁，但不是這批未索引問題的已證實修復。[Google JobPosting 文件](https://developers.google.com/search/docs/appearance/structured-data/job-posting)。

Google 建議 sitemap lastmod 反映重要內容的實際更新，priority／changefreq 不作為 Google 判斷依據。[Sitemap 官方文件](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)。

### 4. 有效職缺導入 Google Indexing API

目前 `backend/scripts/sync_jobs.py:569` 整合的是 IndexNow，未找到 Google Indexing API。不能把 IndexNow 推送成功當作 Google 已收到職缺更新。

針對符合 JobPosting 規範的有效職缺，新公告與實質更新時送 URL_UPDATED，保留 sitemap。需設定 Google Cloud API、服務帳戶及 Search Console 權限。API 接受通知不等於建立索引，不應批量推送一般首頁／分類頁。[Google Indexing API](https://developers.google.com/search/apis/indexing-api/v3/using-api)。

歷史頁若要繼續一般網頁索引，不應僅因職缺到期就送 URL_DELETED；移除一般索引與移除職缺展示是不同目標。

## 本次建議的完成標準

先確認有效職缺及穩定入口的 Search Console 結果，再修 SSR 統計、分類合法性與失敗狀態；接著改善真實 lastmod／hreflang／結構化資料並接入職缺通知，最後把歷史資料轉成有用的機關與分類分析。用頁面類型追蹤結果，避免反覆提交沒有變更的歷史 URL。
