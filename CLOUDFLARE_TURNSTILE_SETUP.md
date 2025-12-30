# Cloudflare Turnstile 設定教學

本文件說明如何取得並設定 Cloudflare Turnstile 金鑰，用於取代 Google reCAPTCHA 進行機器人驗證。

## 什麼是 Cloudflare Turnstile？

Cloudflare Turnstile 是一個免費的 CAPTCHA 替代方案，具有以下優點：

- ✅ **完全免費**，無使用次數限制
- ✅ **隱私友善**，不追蹤使用者
- ✅ **使用者體驗佳**，通常不需要點選圖片
- ✅ **快速驗證**，大多數情況下無需使用者互動

---

## 步驟一：註冊/登入 Cloudflare

1. 前往 [Cloudflare Dashboard](https://dash.cloudflare.com)
2. 使用現有帳號登入，或註冊新帳號（免費）

---

## 步驟二：前往 Turnstile 頁面

1. 登入後，在左側選單找到並點擊 **「Turnstile」**
2. 或直接前往：https://dash.cloudflare.com/?to=/:account/turnstile

---

## 步驟三：建立 Widget

1. 點擊 **「Add Widget」** 按鈕

2. 填寫表單：

   | 欄位 | 說明 | 範例 |
   |------|------|------|
   | Widget name | 自訂名稱 | `job-portal-comments` |
   | Hostname | 網站網域 | `localhost`, `your-domain.com` |
   | Widget Mode | 驗證模式 | 選擇 **Managed**（推薦） |

3. 點擊 **「Create」** 建立

---

## 步驟四：取得金鑰

建立完成後，你會看到兩個金鑰：

### Site Key（網站金鑰）
- 用於**前端**
- 可以公開
- 格式：`0x4AAAAAAA...`

### Secret Key（密鑰）
- 用於**後端**
- ⚠️ **不可公開**
- 格式：`0x4AAAAAAA...`

---

## 步驟五：設定環境變數

### 前端 (Nuxt)

在 `frontend-nuxt/.env` 或 `nuxt.config.ts` 的 `runtimeConfig` 中設定：

```env
NUXT_PUBLIC_TURNSTILE_SITE_KEY=你的_Site_Key
```

### 後端 (FastAPI)

在 `backend/.env` 中設定：

```env
CLOUDFLARE_TURNSTILE_SECRET_KEY=你的_Secret_Key
```

---

## Widget 模式說明

| 模式 | 說明 | 適用場景 |
|------|------|----------|
| **Managed** | 自動決定是否需要挑戰 | 一般網站（推薦） |
| **Non-interactive** | 完全隱形，無需互動 | 低風險操作 |
| **Invisible** | 在需要時才顯示挑戰 | 表單提交 |

---

## 相關連結

- [Cloudflare Turnstile 官方文件](https://developers.cloudflare.com/turnstile/)
- [Turnstile Dashboard](https://dash.cloudflare.com/?to=/:account/turnstile)
- [Client-side API 參考](https://developers.cloudflare.com/turnstile/get-started/client-side-rendering/)
- [Server-side 驗證 API](https://developers.cloudflare.com/turnstile/get-started/server-side-validation/)

---

## 下一步

取得金鑰後，需要修改以下檔案來整合 Turnstile：

1. `nuxt.config.ts` - 載入 Turnstile 腳本
2. `composables/useComments.ts` - 替換 reCAPTCHA 邏輯
3. `components/CommentSection.vue` - 替換 widget 容器
4. `backend/app/Services/CommentService.py` - 替換驗證 API
