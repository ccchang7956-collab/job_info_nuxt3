# SEO / GEO 修正與部署

本次使用者授權後已完成程式碼修改、本機驗證及正式部署。尚未操作 Search Console 或向 Google 發送通知。原始診斷與使用者提供的 20 筆樣本见 [稽核報告](SEO_GEO_AUDIT_2026-10-07.md)。

## 已完成正式部署

2026-10-07：程式碼 commit `539ea18` 已推送到 origin/main。使用正式 Compose 設定重建 frontend、backend、backend-cron，更新三個容器並重啟 nginx；四個服務均運行，驗收時重啟次數為 0。資料庫仍使用原來同一份掛載檔案，未執行 migration。

新後端映像的 6 項隔離測試通過，Google auth 依賴可匯入。本機 Nginx 入口與正式網域的首頁、SSR 統計、分類摘要及第二頁、歷史 index、無效分類與不存在職缺的 404／noindex、分類 API，以及 sitemap index 列出的所有子 sitemap 均通過 GET 驗收。

部署初期公開 robots.txt 曾交替取得新舊內容；源站始終提供新版，最後一次公開完整驗收也取得新版。若其他 CDN 節點仍提供旧版本，可針對 robots.txt 清除快取或等待快取更新；公開回應的 Cache-Control 為 max-age=14400。未使用 Cloudflare API 執行 purge。舊映像保留在各服務的 `pre-seo-539ea18` 標籤供回復。

## 已完成

- 統計頁改為 SSR 載入初始數據，HTML 包含月份、摘要、表格及來源；補充前十名、表內佔比、公告筆數與多地點重複計入等統計限制。保留圖表／月份／分類切換，避免較舊的請求覆寫新選擇。
- 縣市／職系分類驗證合法名稱。職系來源使用完整 job_sysnam 表及歷史公告的職系，不以熱門 sitemap 職系作為白名單。不存在分類 404／noindex，合法但暫時零職缺的分類保留 200／index。
- 分類頁加入由列表 API 實際總數生成的摘要、資料同步日期與來源，不把公告筆數當作招募人數。
- 首頁、分類、統計與職缺 API 暫時失敗回 5xx／no-store，避免 200 錯誤空頁或短暫故障 noindex。Nitro plugin 確保 SWR 不會覆寫錯誤回應的禁止快取標頭。
- 職缺真 404／無資料回 404／noindex，既有過期職缺仍可索引並顯示截止提示。
- 移除全站皆指向首頁的 hreflang；繁體中文 html lang 保留。
- 靜態／分類 sitemap 無可靠異動時間時省略 lastmod；職缺保留可得的公告日期。職缺 sitemap 包含今天截止的職缺，以台北日期判斷，同日起始公告以 ID 排序穩定分頁。
- sitemap 資料庫故障回錯誤，不再混同為不存在的 404。
- 移除所有機關共用的人事總處 sameAs 與未經證實的通用公務員福利。聘僱類型只依明確文字提供，不把約聘／約用一律當作獨立承攬人。
- robots.txt 允許抓取日誌，讓 Google 能讀取頁面既有 noindex。
- FAQ 與資料說明改為解釋歷史公告判定方式，不單憑再公告次數推斷流動率。
- 新增 Google Indexing API 手動預覽／通知工具，只選取仍未截止的既有職缺 ID，使用 URL_UPDATED；不處理一般分類，不刪除歷史網頁索引，預設不發送。

## 驗證

正式版本建置成功。38 項前端測試全部通過，包含 Chromium 分頁／歷史導航／頁面筆數／跳頁及統計頁互動；6 項後端 SQLite fixture 測試全部通過。測試未連接正式資料庫，也未呼叫 Google API。

前端沿用 `npm run test:seo`。正式版本的隔離建置與測試：

```bash
cd frontend-nuxt
BACKEND_URL=http://127.0.0.1:18002 npm run build
SEO_TEST_PRODUCTION=1 npm run test:seo
```

若已有 Playwright 與 Chromium，可設定 `SEO_TEST_PLAYWRIGHT_PATH`、`SEO_TEST_BROWSER_EXECUTABLE` 執行瀏覽器檢查。未設定時瀏覽器測試會跳過。本次驗證已啟用瀏覽器檢查。

後端在安裝專案依賴的環境執行：

```bash
cd backend
python -m unittest discover -s tests -v
```

## 部署與驗收

前後端必須一起更新，新前端會使用 `/api/metadata/categories`。不需資料庫 migration。測試建置含本機 fixture backend，不能直接拿測試 `.output` 部署；Docker Compose 會用正式內部 BACKEND_URL 重新建置。

於專案根目錄：

```bash
docker compose up -d --build --no-deps backend frontend
docker compose exec nginx nginx -s reload
```

重載 Nginx 是為了重新解析已重建容器的 IP。建置失敗或容器不健康時先修復，勿把建置成功當成網站已驗收。

部署後用 GET 確認：

- `/charts` HTML 有實際數據表與摘要。
- `/places/臺北市`、`/sysnams/綜合行政` 有真實公告總數，第 2 頁的內容與 canonical 正常。
- 不存在的分類回 404；有效但零職缺分類回 200。
- sitemap index 列出的每份子 sitemap 回 200／XML；靜態 sitemap 無捏造的 lastmod。
- `/job/81682` 與 `/job/81553` 回 200／index，過期提示正確；不存在職缺回 404／noindex。
- robots.txt 沒有禁止抓取 `/logs`，而日誌頁仍是 noindex。

Search Console：對歷史 noindex 樣本先「測試實際網址」，確認允許索引，再啟動該類別的修正驗證。分開追蹤首頁、有效職缺、分類及歷史頁；對少量有實質更新且重要的頁面要求索引。技術修復不保證 Google 收錄。

## Google Indexing API

工具為 `backend/scripts/notify_google_indexing.py`，依賴 google-auth。需要使用者完成 Google Cloud API 啟用、服務帳戶、Search Console 所有權及使用核准／配額設定；本次沒有取得或驗證這些設定，也未驗證真實通知發送。[Google 官方前置設定](https://developers.google.com/search/apis/indexing-api/v3/quickstart)。

部署後可先在容器中預覽指定職缺，預覽不需憑證、不連 Google：

```bash
docker compose exec backend python scripts/notify_google_indexing.py --job-id 138230
```

工具只準備當下仍未截止的 ID，因此上面的範例在截止後會得到空清單。可用多個 `--job-id` 指定不同職缺，一次最多 200 個，依實際配額控制總發送數。

先確認職缺內容及 JobPosting 符合規範，再以唯讀檔案掛載服務帳戶 JSON，設定 `GOOGLE_APPLICATION_CREDENTIALS`，加 `--publish` 才實際通知。JSON 私鑰不得加入 Git。本工具是手動試點，尚未接入同步排程，避免未設定帳戶／配額時自動發送。

Google 收到通知不等於已建立索引。[Indexing API 使用說明](https://developers.google.com/search/apis/indexing-api/v3/using-api)。

## 尚未包含的內容擴充

本次提供分類真實公告摘要，尚未新增機關頁、30／90 日歷史趨勢或完整職等分布。這些需要另外定義統計口徑與頁面設計；不使用泛用生成文字填補資料。Google Indexing API 的自動排程也需在帳戶與配額驗證後接入。
