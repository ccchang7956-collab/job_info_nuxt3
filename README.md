# 公務人員職缺查詢系統 (重構版)

本專案是一個現代化的網頁應用程式，用於查詢與瀏覽台灣公務人員職缺。專案已從 Vue 3 SPA 重構為 **Nuxt 3** 應用程式，以提升效能、SEO 及開發體驗，並搭配 **FastAPI** 後端。

## 技術堆疊 (Tech Stack)

### 前端 (`frontend-nuxt`)
- **框架**: [Nuxt 3](https://nuxt.com/) (Vue 3)
- **樣式**: [Tailwind CSS](https://tailwindcss.com/)
- **狀態管理**: [Pinia](https://pinia.vuejs.org/)
- **HTTP 客戶端**: Nuxt `$fetch` / `useFetch`
- **資安**: `nuxt-security` 模組 (CSP, 安全標頭)
- **PWA**: `@vite-pwa/nuxt` (漸進式網頁應用)
- **圖表**: `vue-chartjs` / `chart.js`
- **圖示**: `@heroicons/vue`

### 後端 (`backend`)
- **框架**: [FastAPI](https://fastapi.tiangolo.com/)
- **資料庫**: MySQL
- **ORM**: SQLAlchemy (Async)
- **資安**: `fastapi-csrf-protect` (CSRF Token), Google reCAPTCHA
- **排程任務**: APScheduler (用於資料更新)

## 功能特色

- **職缺搜尋**: 瀏覽與搜尋政府公務人員職缺。
- **職缺詳情**: 查看特定職缺的詳細資訊。
- **留言系統**:
    - 使用者可對職缺進行留言討論。
    - 整合 **Google reCAPTCHA v3** 防止機器人。
    - 使用 **CSRF Token** 保護提交安全。
    - 支援即時 Toast 訊息回饋。
- **資料視覺化**: 互動式圖表展示職缺統計數據。
- **PWA 支援**: 可安裝為應用程式，支援離線瀏覽體驗。
- **響應式設計**: 針對手機與桌面裝置最佳化。

## 專案結構

```
job_info_vue_refactor/
├── backend/                # FastAPI 後端
│   ├── app/                # 應用程式邏輯 (路由, 模型, 架構)
│   ├── venv/               # Python 虛擬環境
│   ├── run.py              # 啟動入口
│   └── requirements.txt    # Python 相依套件
├── frontend-nuxt/          # Nuxt 3 前端
│   ├── components/         # Vue 元件
│   ├── composables/        # 共用邏輯 (useComments, useToast)
│   ├── pages/              # 應用程式路由
│   ├── server/             # 伺服器端邏輯 (如有)
│   ├── types/              # TypeScript 型別定義
│   └── nuxt.config.ts      # Nuxt 設定檔
└── README.md               # 本文件
```

## 安裝與執行

### 後端 (Backend)

1.  進入後端目錄：
    ```bash
    cd backend
    ```
2.  建立並啟用虛擬環境 (若尚未建立)：
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  安裝相依套件：
    ```bash
    pip install -r requirements.txt
    ```
4.  啟動伺服器：
    ```bash
    ./venv/bin/python run.py
    ```
    後端服務將於 `http://localhost:8000` 啟動。

### 前端 (Frontend)

1.  進入前端目錄：
    ```bash
    cd frontend-nuxt
    ```
2.  安裝相依套件：
    ```bash
    npm install
    ```
3.  啟動開發伺服器：
    ```bash
    npm run dev
    ```
    應用程式將於 `http://localhost:3000` 啟動。

## 近期重構亮點

- **遷移至 Nuxt 3**: 將完整的 Vue 3 SPA 移植到 Nuxt 3，實現 SSR (伺服器端渲染) 與更佳的路由管理。
- **資安增強**:
    - 引入 `nuxt-security` 實作嚴格的 CSP 與安全標頭。
    - 修復 Nuxt 與 FastAPI 之間的 CSRF Token 驗證流程。
    - 強制留言功能需通過 reCAPTCHA 驗證。
- **程式碼優化**:
    - 重構 API 呼叫，全面改用 `useFetch` 並設定 Proxy 規則。
    - 抽離邏輯至 Composables (`useComments`, `useToast`)。
    - 加入 TypeScript 介面定義，提升型別安全。
    - 優化後端 Pydantic Schema 驗證邏輯。

---
*最後更新: 2025-12-04*
