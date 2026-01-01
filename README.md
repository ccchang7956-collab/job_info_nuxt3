# 開放事求人 - 公務人員職缺查詢系統

本專案是一個現代化的網頁應用程式，用於查詢與瀏覽台灣公務人員職缺。專案採用 **Nuxt 3** 前端框架搭配 **FastAPI** 後端，提供優異的效能、SEO 及開發體驗。

🔗 **線上版本**: [開放事求人](https://job.ccchang.tw)

## ✨ 功能特色

- **職缺搜尋**: 瀏覽與搜尋政府公務人員職缺，支援多條件篩選
- **職缺詳情**: 查看特定職缺的詳細資訊與歷史記錄
- **留言系統**: 使用者可對職缺進行留言討論，整合 Cloudflare Turnstile 防護
- **資料視覺化**: 互動式圖表展示職缺統計數據
- **LINE AI Bot**: 透過 LINE 機器人查詢職缺資訊
- **PWA 支援**: 可安裝為應用程式，支援離線瀏覽
- **響應式設計**: 針對手機與桌面裝置最佳化

## 🛠️ 技術堆疊

### 前端 (`frontend-nuxt`)
| 技術 | 說明 |
|------|------|
| [Nuxt 3](https://nuxt.com/) | Vue 3 框架，支援 SSR |
| [Tailwind CSS](https://tailwindcss.com/) | 實用優先的 CSS 框架 |
| [Pinia](https://pinia.vuejs.org/) | 狀態管理 |
| `nuxt-security` | CSP、安全標頭 |
| `@vite-pwa/nuxt` | 漸進式網頁應用 |
| `@heroicons/vue` | 圖示庫 |

### 後端 (`backend`)
| 技術 | 說明 |
|------|------|
| [FastAPI](https://fastapi.tiangolo.com/) | 高效能 Python API 框架 |
| MySQL + SQLAlchemy (Async) | 資料庫與 ORM |
| `fastapi-csrf-protect` | CSRF 防護 |
| Cloudflare Turnstile | 防機器人驗證 |
| APScheduler | 排程任務 |

## 📁 專案結構

```
job_info_nuxt3/
├── backend/                  # FastAPI 後端
│   ├── app/
│   │   ├── Core/             # 設定檔
│   │   ├── Models/           # 資料庫模型
│   │   ├── Routers/          # API 路由
│   │   ├── Services/         # 商業邏輯
│   │   └── Utils/            # 工具函式
│   ├── db_optimization.sql   # 資料庫索引優化
│   └── requirements.txt
├── frontend-nuxt/            # Nuxt 3 前端
│   ├── components/           # Vue 元件
│   ├── composables/          # 共用邏輯
│   ├── layouts/              # 版面配置
│   ├── pages/                # 頁面路由
│   └── nuxt.config.ts
└── README.md
```

## 🚀 快速啟動

### 環境需求
- Node.js 18+
- Python 3.10+
- MySQL 8.0+

### 1. 啟動後端

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
./venv/bin/python run.py
```
> 後端服務：`http://localhost:8000`

### 2. 啟動前端

```bash
cd frontend-nuxt
npm install
npm run dev
```
> 前端應用：`http://localhost:3000`

### 3. 環境變數設定

建立 `.env` 檔案：

```env
# 後端
CLOUDFLARE_TURNSTILE_SECRET_KEY=your_secret_key

# 前端
NUXT_PUBLIC_TURNSTILE_SITE_KEY=your_site_key
```

## 📊 資料庫優化

執行索引優化以提升查詢效能：

```bash
mysql -u root -p job_info < backend/db_optimization.sql
```

## 🔐 安全特性

- **CSP (Content Security Policy)**: 嚴格的內容安全政策
- **CSRF Token**: 防止跨站請求偽造
- **Cloudflare Turnstile**: 智慧型機器人防護
- **XSS 防護**: 輸入消毒與輸出編碼
- **Rate Limiting**: API 請求限流

## 📱 PWA 支援

本應用支援 Progressive Web App：
- 可安裝至手機主畫面
- 離線快取靜態資源
- 推送通知（未來功能）

## 🤖 LINE AI Bot

整合 LINE Messaging API，可透過 LINE 查詢職缺：
- 傳送關鍵字搜尋職缺
- 查看職缺詳情
- 取得最新職缺通知

## 📝 近期更新 (2025-12-30)

### 效能優化
- ✅ 日期計算快取機制
- ✅ 職等篩選使用 REGEXP 優化
- ✅ 啟用第一頁查詢快取
- ✅ API 請求加入 Retry 機制

### 安全強化
- ✅ CSP unsafe-eval 僅限開發環境
- ✅ 移除硬編碼敏感金鑰

### 程式碼品質
- ✅ 抽取共用元件 (Pagination, FilterTag)
- ✅ 結構化 JSON 日誌格式
- ✅ TypeScript 型別強化

---

## 📄 授權

本專案使用政府資料開放平臺之 [行政院人事行政總處事求人機關徵才資料](https://data.gov.tw/dataset/7229)。

---

*最後更新: 2025-12-30*

