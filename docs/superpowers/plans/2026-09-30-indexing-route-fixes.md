# 索引路由修正 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** 修正已實測的職缺 sitemap 404 及分類分頁重複第 1 頁問題。

**Architecture:** 採用既有 Nuxt／FastAPI 部署，不改 Nginx 設定。在 Nitro middleware 精確匹配職缺 sitemap，透過私人 runtimeConfig 的 backendUrl 轉送至後端並保留狀態碼。分類分頁從 URL 初始化及同步狀態，選頁與每頁筆數也更新 URL；純分頁具有自己的 canonical。

**Tech Stack:** Nuxt 4、Vue 3、Nitro／h3、Node 內建測試執行器。

## Global Constraints

- 使用者已批准修正先前診斷出的 sitemap 及分頁問題，實作於目前工作目錄；不部署或操作 Search Console。
- 不新增套件、不改資料庫、不將 Google Indexing API 或內容擴充混入本次修復。
- 保留 sitemap-jobs-N.xml 公開 URL，支援任意合法數字頁碼，後端不存在頁碼仍返回 404。
- 保留首頁任意篩選頁的既有 canonical 策略，只修正純列表分頁 canonical。

## Task 1: 可重現的 HTTP 回歸測試

- [x] 新增 frontend-nuxt/tests/seo.test.mjs，以測試後端 fixture 啟動真正的 Nuxt dev server，避免依賴正式站與資料庫。
- [x] 執行 `node --test tests/seo.test.mjs`，先確認職缺 sitemap 回 404、分類 page=2 職缺錯誤與 canonical 回第一頁的失敗。
- [x] 保留根 sitemap、static sitemap、普通頁面及後端 404 傳遞測試。

## Task 2: sitemap 轉送

- [x] 在 nuxt.config.ts 新增私人 runtimeConfig.backendUrl，移除無法匹配的 /sitemap-jobs-** 規則。
- [x] 新增 server/middleware/job-sitemap.ts，僅匹配 `/^\/sitemap-jobs-[1-9]\d*\.xml$/`；將 path 轉送至 backendUrl，非匹配請求交由正常路由。
- [x] 重跑 sitemap 測試，確認 200 XML 與不存在頁碼 404。

## Task 3: 分頁

- [x] 分類頁從 route.query.page/per_page 初始化並監聽網址改動；上下頁、跳頁、每頁筆數變更及上一頁歷史導航維持相同資料來源。
- [x] 每頁筆數變更回第 1 頁，canonical 保留不同 page/per_page 對應內容；預設第 1 頁使用無 query URL。
- [x] 首頁純 page 分頁 canonical 對應自身；不將任意篩選／排序 query 擴大開放索引。
- [x] 重跑 SSR 回歸測試並實測前端分頁導航。

## Task 4: 驗收與交付

- [x] `npm run build` 成功；以產出後的 production server 驗證主要 HTTP 測試。
- [x] GPT-6 Luna（max）唯讀檢查最終 diff，修正實質問題。
- [x] 更新診斷文件：本機修正已完成、正式站尚待部署，記錄 rebuild frontend 與 nginx reload 的指令。
- [x] 確認 git diff 無無關變更；不自行提交、推送或部署。
