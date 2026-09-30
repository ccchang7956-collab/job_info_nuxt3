# Google Search Console 索引診斷

檢查日期：2026-09-30（Asia/Taipei）。正式站：https://opendgpa.shibaalin.com 。

初次完成程式碼唯讀審查及正式站 HTTP GET / HTML / XML 抽查；GPT-6 Luna（max）協助程式碼審查。使用者後續批准修正，現在已完成本機的 sitemap 轉送、分類分頁及純列表分頁 canonical 修復。正式站尚未部署，沒有操作 Search Console；下方正式站實測表記錄的是部署前結果。

## 已完成的修復與部署

- 新增 `frontend-nuxt/server/middleware/job-sitemap.ts`，精確轉送合法職缺子 sitemap；支援任意數字頁碼，保留後端 XML 與 404，移除失效的 Nitro 檔名萬用字元規則。
- 新增私人 runtimeConfig.backendUrl，預設沿用既有 BACKEND_URL；前端 Docker 建置參數可以沿用。
- 分類頁從網址初始化並同步 page/per_page，直接開第二頁、下一頁、上一頁歷史導航、跳頁及每頁筆數變更都有一致結果。
- 分類與首頁純列表分頁使用對應 URL 的 canonical；首頁任意篩選／排序仍維持既有首頁 canonical 策略。
- 超出實際分類頁數時回 404、noindex，並提供返回第一頁連結；有效分類暫時零職缺的第一頁仍保留 200。
- 本機正式建置成功；21 項正式版本的 HTTP／SSR／瀏覽器測試通過，Luna 最終程式碼審查無阻擋問題。瀏覽器測試使用獨立無頭 Chrome，阻擋非本機網路，不連接正式資料庫。

本次採用 Nuxt 方案，**nginx/default.conf 不需要修改**。現有 Nginx 的 `location /` 會把職缺子 sitemap 送到 Nuxt，交由新 middleware 處理。

在正式環境套用程式碼後，於專案根目錄重建前端：

```bash
docker compose up -d --build --no-deps frontend
```

如果重建後出現 Nginx 502，可能是 Nginx 仍保留原前端容器 IP，此時重新載入即可，不需變更設定：

```bash
docker compose exec nginx nginx -s reload
```

部署後以 GET 驗收（不要只使用 HEAD）：

```bash
curl -fsS -o /dev/null -w '%{http_code}\n' https://opendgpa.shibaalin.com/sitemap-jobs-1.xml
curl -fsS -o /dev/null -w '%{http_code}\n' https://opendgpa.shibaalin.com/sitemap-jobs-2.xml
```

兩者應回 200；再依 sitemap index 列出的完整子 sitemap 清單檢查。確認分類 page=2 顯示第二頁且職缺清單與第一頁不同，然後按下文 Search Console 操作順序重新提交 sitemap 與抽查重要網址。

## 結論與證據範圍

網站不是整站被 robots.txt 阻擋，也不是只有 JavaScript 空殼。首頁及抽查職缺、分類頁都有 SSR 內容、index,follow 及目前正式網域的 canonical。不存在的職缺 ID 正確回傳 HTTP 404。

有兩個已證實、應優先修正的缺陷：職缺子 sitemap 對外 404，以及分類分頁永遠輸出第 1 頁。兩者影響 URL 發現與抓取，不能單獨證明使用者提供的「已檢索－目前尚未建立索引」案例的原因。

使用者進一步回報「首頁或有效職缺也未收錄」。因此診斷範圍包括主要入口與有效職缺，不能將整體問題歸因於歷史職缺過期。首頁及有效職缺各自的精確排除原因與上次檢索時間尚未取得；/job/82417 的排除原因不能直接套用到全站。

目前沒有 Search Console 帳戶、Google 實際抓取的歷史 HTML、Google 選取的 canonical 或伺服器 Googlebot 歷史日誌。這些資料仍是確定 Google 當次不收錄原因所需的證據。

補充以 Googlebot 手機 user-agent 抽查首頁、/job/82417、有效職缺 /job/136788，也都回 200 並提供完整 HTML。這只排除了本次測試來源下單純依 user-agent 封鎖的情況，不能代替來自 Google 真實 IP 的 URL Inspection 或 Cloudflare 事件查核。

## 使用者提供的 /job/82417

網址：https://opendgpa.shibaalin.com/job/82417 。使用者回報狀態為「已檢索－目前尚未建立索引」。

| 項目 | 正式站抽查結果 |
| --- | --- |
| HTTP GET | 200 |
| robots meta | index,follow |
| canonical | https://opendgpa.shibaalin.com/job/82417 |
| SSR | 有完整機關、職稱、資格、工作項目、報名方式及歷史開缺 |
| 職缺 | 臺北市內湖區南湖國民小學／幹事 |
| 截止日期 | 2026-01-16；頁面明確顯示已截止 |
| JobPosting validThrough | 2026-01-16T23:59:59+08:00 |
| 職缺 sitemap | 後端兩份有效職缺 sitemap 都不含此歷史 URL |

這頁現在具備技術上的可索引條件；不能據此保證 Google 會收錄。它是已截止八個多月的歷史公告，其搜尋需求、與其他公告的內容相似性、站內可發現性及獨有價值都是需考慮的方向，並非已證明的 Google 排除原因。內容有完整長文，不宜僅因為未收錄就稱為「內容太短」。

Google 將「已檢索－目前尚未建立索引」定義為已抓取但未收錄，未來可能收錄也可能不收錄；此狀態本身無法指出內容品質或 canonical 的具體根因。[Search Console 官方說明](https://support.google.com/webmasters/answer/7440203)。

過期的 JobPosting 不再適合作為有效職缺顯示；目前 validThrough 已在過去，是 Google 官方列出的過期處理方式之一。這不等於禁止該歷史頁進入一般網頁搜尋。[JobPosting 官方文件](https://developers.google.com/search/docs/appearance/structured-data/job-posting)。

## 優先修正 1：職缺子 sitemap 的對外路由

| 正式站 GET 路徑 | HTTP | 內容 |
| --- | --- | --- |
| /robots.txt | 200 | 允許一般搜尋爬蟲，指向 /sitemap.xml |
| /sitemap.xml | 200 | index，列出 static、jobs-1、jobs-2 |
| /sitemap-static.xml | 200 | 45 筆 URL，包含 22 縣市與 18 職系 |
| /sitemap-jobs-1.xml | 404 | Nuxt Page not found JSON |
| /sitemap-jobs-2.xml | 404 | Nuxt Page not found JSON |
| /api/sitemap-jobs-1.xml | 200 | 後端正常生成 1,000 筆職缺 URL |
| /api/sitemap-jobs-2.xml | 200 | 後端正常生成 599 筆職缺 URL |

兩份後端 sitemap 合計 1,599 個不重複的職缺 URL；它們被 index 列出的兩個對外 404 路徑阻斷。這會影響 sitemap 發現途徑，不代表 Google 無法透過其他內部連結找到職缺。

原因已定位：frontend-nuxt/nuxt.config.ts:148 的 `/sitemap-jobs-**` 不會匹配 `/sitemap-jobs-1.xml`。本機使用專案已安裝、Nitro 實際使用的 radix3 route matcher 重現，兩個職缺路徑的 matchAll 都是空陣列，static 路徑則正常匹配。nginx/default.conf:35 只直接轉送 `/sitemap.xml`，沒有涵蓋職缺子 sitemap，所以請求落入前端的 404。

以下保留原診斷中的 Nginx 備選作法供參考；本次已採用上方 Nuxt middleware 修復，不需要套用這段設定。若另選 Nginx 直接轉送，可將原本的 sitemap location 改為明確匹配整組 sitemap，proxy_pass 不帶 URI 以保留原始路徑：

```nginx
location ~ ^/sitemap(?:-static|-jobs-[1-9][0-9]*)?\.xml$ {
    proxy_pass http://backend:8002;
    proxy_set_header Host $host;
}
```

這段 Nginx 備選設定尚未執行或驗證。本次新增的 Nitro middleware 讓 Nuxt 本身可以直接服務子 sitemap，並移除現有失效規則；頁碼未硬編碼為只支援 1、2 頁。

部署驗收：對 sitemap index 的每個 loc 執行 GET，確認 HTTP 200、application/xml、可解析 urlset、URL 使用同一正式網域；不存在的頁碼應回 404。不要只測根 index 或 HEAD。backend/app/Routers/SeoRouter.py 的子 sitemap HEAD 目前會固定回 200，無法用來證明 GET 是否真的成功。

## 優先修正 2：分類分頁及 canonical

正式站已重現：

- `/places/臺北市` 與其 `?page=2` 的職缺連結清單完全相同，兩頁都顯示「第 1 頁 / 共 10 頁」。
- `/sysnams/綜合行政` 與其 `?page=2` 的職缺連結清單完全相同，兩頁都顯示「第 1 頁 / 共 8 頁」。
- 上述 page=2 的 canonical 都指向沒有 query 的第 1 頁。

原因：frontend-nuxt/components/Pagination.vue:69-97 的上一頁／下一頁 NuxtLink 只更新 route.query；兩個分類頁的 currentPage 固定從 1 開始，未讀取或監聽 query.page。首頁已有 query 同步處理，可以作為行為參考。

修正要求：將分類頁頁碼以 URL 為資料來源，在 SSR 與前端導航都解析、驗證 page，讓 useFetch 隨頁碼更新；每頁輸出不同的職缺連結。可索引的純分頁 URL 應有各自 canonical（第 1 頁保留無 query URL）。首頁純分頁也需要與任意篩選／排序頁分開設定策略，避免直接把所有搜尋組合開放索引。

Google 明確建議分頁各自使用獨立 URL 與 canonical，不應全部 canonical 到第一頁。[Google 分頁指南](https://developers.google.com/search/docs/specialty/ecommerce/pagination-and-incremental-page-loading)。

驗收：page=2 應顯示第 2 頁、職缺 ID 清單與 page=1 不同；直接開網址與點下一頁結果一致；上一頁／下一頁都保持可抓取的 a href；invalid/out-of-range page 具備一致的錯誤或轉址處理。

## 優先改善 3：有效職缺的 Google Indexing API

backend/scripts/sync_jobs.py:562-566,594 目前有 IndexNow 推送及 sitemap 快取失效，未看到 Google Indexing API 的整合。IndexNow 的參與引擎清單未包含 Google，不應把 IndexNow 成功當成通知了 Google。[IndexNow 官方參與端點](https://www.indexnow.org/faq)。

Google 對職缺站建議使用 Indexing API 通知新職缺及更新，以加快爬取；它只適用於帶有 JobPosting 的職缺頁及符合條件的直播頁，不可拿來批量推送一般分類、首頁或所有歷史網頁。需要 Google Cloud API、服務帳戶與 Search Console 權限，現有憑證與啟用情況尚未查驗。[Google JobPosting 指南](https://developers.google.com/search/docs/appearance/structured-data/job-posting)、[Indexing API 使用方法](https://developers.google.com/search/apis/indexing-api/v3/using-api)。

先以一批正在招募、完整而可存取的職缺做試點。API 的 HTTP 200 只表示通知已接受、Google 可能很快重抓，不等於已建立索引。保留全站 sitemap。對仍要保留在一般搜尋中的歷史頁，不應為了移除職缺搜尋顯示而直接要求刪除一般索引。

## 長期改善：以穩定頁與歷史分析建立搜尋價值

已有縣市及職系 URL，應先把分頁修好，再增加真正能解決需求的內容，例如職系任用條件說明、機關與地區職缺統計、近期趨勢，以及機關歷史徵才時間線。資料應由網站既有資料庫計算，標明期間、來源與限制，避免為了文字量填入泛用段落。

歷史頁如 /job/82417 可保留，但應清楚呈現「歷史公告／已截止」，提供同機關後續公告、目前相關職缺，以及實際的重複開缺時間線與分析。本站本來已有歷史連結，這是可繼續強化的差異。保留資料不代表每一筆歷史公告都需要成為 SEO 主力。

優先追蹤首頁、有效職缺、縣市頁、職系頁的索引及曝光；歷史職缺分開追蹤。不要用全部 URL 的未收錄比例直接推論全站 SEO 很差。

## 次要修正與需查證項目

1. 正式站 `/places/seo-audit-invalid-county` 會回 200、index,follow 及「目前無最新職缺」。無效縣市應回 404；有效縣市暫時沒有職缺仍可保留有用內容。職系需使用完整合法分類資料，不能直接把 sitemap 的 18 個「熱門職系」當完整白名單。
2. backend/app/Services/SeoService.py:137-145 每天替所有縣市與職系頁填今天的 lastmod。列表有實質變更時可以更新；無變更時不應只因跨日刷新。首頁／charts 的固定 2025-12-30 也不反映實際動態資料更新。可採真實資料變更時間，無可靠時間時省略。Google 會驗證 lastmod 的可信度，忽略 priority/changefreq。[Sitemap 官方文件](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)。
3. nuxt.config.ts:107-108 把所有頁面的 hreflang 都指向首頁；單一繁體中文網站通常可移除這組不對應的 alternate，或逐頁提供對應 URL。這不是已證明的 /job/82417 排除原因。
4. 詳情頁的真 404 目前仍輸出 index,follow，但 HTTP 404 正確，沒有形成 200 soft 404；robots 註解與實作可另行整理，不是本次高優先根因。
5. 之前 docs/superpowers/specs/2026-07-06-seo-optimization-design.md 宣稱「過期頁 noindex 拖累整站」不應繼續作為根據。Google 官方明確說大量 noindex 不會因此影響其他頁的抓取與索引；是否保留歷史索引應依內容價值決定。[Google 官方 SEO office hours](https://developers.google.com/search/blog/2022/11/november-office-hours)。
6. 本次抽查舊網域 opendgpa.site、www.opendgpa.site、job.ccchang.tw 的 DNS 無法解析；不能據此判定它們曾經或現在是 Google 選取的 canonical。需讀 Search Console 的實際 canonical 欄位，不應只沿用舊稽核的網域分裂結論。

## Search Console 操作順序

1. 技術修正部署後，確認所有子 sitemap 的 GET 正常，再提交或重新讀取 `https://opendgpa.shibaalin.com/sitemap.xml`；檢查子 sitemap 的讀取狀態與發現 URL 數。
2. 抽查首頁、1 筆有效職缺、1 個縣市、1 個職系，以及 /job/82417。記錄上次檢索時間、頁面擷取狀態、是否允許建立索引、使用者宣告與 Google 選取的標準網址。
3. 用「測試實際網址」檢查當前 HTML 是否有完整內容；把目前 live 測試與 Google 上次抓取的結果區分。live 正常不代表歷史抓取也正常。
4. 對有實質更新的少數重要頁要求建立索引；有效 JobPosting 以 Indexing API 處理批次通知。不要一直對同一頁重複提交。
5. 依頁面類型觀察後續數週的索引／曝光／點擊，並檢查 Googlebot 的 429、5xx、抓取延遲與過期前抓取比例。

要求爬取可能需數天到數週，且不保證收錄；對同一 URL 重複要求不會加快。[Google 重新檢索官方說明](https://developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl)。
