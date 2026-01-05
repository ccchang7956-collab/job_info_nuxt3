# Google Analytics 4 (GA4) 引入教學

本文說明如何在此 Nuxt 4 專案中引入 Google Analytics 4。

---

## 步驟一：建立 GA4 資源並取得測量 ID

### 1. 登入 Google Analytics

前往 [analytics.google.com](https://analytics.google.com/) 並使用 Google 帳號登入。

### 2. 建立帳戶（首次使用）

如果是首次使用，點擊「**開始測量**」，然後：

1. **帳戶名稱**：輸入你的組織或專案名稱（例如：`開放事求人`）
2. 勾選資料分享選項（可全選或依需求）
3. 點擊「**下一步**」

### 3. 建立資源（Property）

1. **資源名稱**：輸入網站名稱（例如：`開放事求人網站`）
2. **報表時區**：選擇 `(GMT+08:00) 台北`
3. **貨幣**：選擇 `新台幣 (TWD)`
4. 點擊「**下一步**」

### 4. 填寫商家資訊

1. **行業類別**：選擇最接近的（例如：`就業`）
2. **商家規模**：選擇適當的
3. 點擊「**下一步**」

### 5. 選擇業務目標（可多選）

- ✅ 產生待開發客戶
- ✅ 提高品牌知名度
- ✅ 檢查使用者行為

點擊「**建立**」

### 6. 設定資料串流

1. 選擇平台：點擊「**網頁**」
2. 輸入網站網址：`https://nuxt3.opendgpa.site`（或你的網域）
3. 輸入串流名稱：`主網站`
4. 點擊「**建立串流**」

### 7. 取得測量 ID

建立完成後會看到：

```
測量 ID: G-XXXXXXXXXX
```

**複製這個 ID**，後續步驟會用到。

> 💡 也可以從：**管理** (齒輪圖示) → **資料串流** → 點擊你的串流 → 查看「測量 ID」

---

## 步驟二：安裝 Nuxt GA4 模組

```bash
cd frontend-nuxt
npm install nuxt-gtag
```

---

## 步驟三：設定 nuxt.config.ts

在 `frontend-nuxt/nuxt.config.ts` 中添加以下設定：

```typescript
export default defineNuxtConfig({
  // ... 其他設定

  modules: [
    // ... 其他模組
    'nuxt-gtag'
  ],

  gtag: {
    id: process.env.NUXT_PUBLIC_GTAG_ID || 'G-XXXXXXXXXX',
    config: {
      // 關閉 IP 匿名化（預設已匿名）
      anonymize_ip: true,
      // 發送頁面瀏覽事件
      send_page_view: true
    }
  }
})
```

---

## 步驟四：設定環境變數

### 開發環境 (frontend-nuxt/.env)

```bash
NUXT_PUBLIC_GTAG_ID=G-XXXXXXXXXX
```

### 生產環境 (伺服器)

在伺服器的 `.env` 或 systemd 服務中設定：

```bash
NUXT_PUBLIC_GTAG_ID=G-XXXXXXXXXX
```

---

## 步驟五：更新 CSP 設定

在 `nuxt.config.ts` 的 `security.headers.contentSecurityPolicy` 中添加 Google Analytics 網域：

```typescript
'script-src': [
  "'self'",
  "'unsafe-inline'",
  "https://challenges.cloudflare.com",
  "https://static.cloudflareinsights.com",
  "https://www.googletagmanager.com",  // 新增
  "https://www.google-analytics.com"    // 新增
],
'connect-src': [
  "'self'",
  "https://www.google-analytics.com",   // 新增
  "https://analytics.google.com"         // 新增
],
'img-src': [
  "'self'",
  "data:",
  "https://www.google-analytics.com"     // 新增
]
```

---

## 步驟六：追蹤自訂事件（可選）

在任何 Vue 元件中追蹤自訂事件：

```vue
<script setup>
const { gtag } = useGtag()

const trackClick = () => {
  gtag('event', 'button_click', {
    event_category: 'engagement',
    event_label: 'Apply Job Button'
  })
}
</script>

<template>
  <button @click="trackClick">應徵工作</button>
</template>
```

---

## 步驟七：驗證安裝

1. 部署後開啟網站
2. 在 Google Analytics 的 **即時報表** 中應該能看到活動
3. 使用瀏覽器開發者工具 → Network → 搜尋 `google-analytics` 確認請求

---

## 注意事項

- **GDPR/隱私**: 如果有歐洲用戶，考慮加入 Cookie 同意機制
- **測試環境**: 可設定不同的測量 ID 避免污染生產數據
- **Adblocker**: 部分用戶使用廣告阻擋器，GA 追蹤可能被阻擋

---

## 參考資源

- [nuxt-gtag 官方文件](https://nuxt.com/modules/gtag)
- [Google Analytics 4 說明](https://support.google.com/analytics/answer/9304153)
