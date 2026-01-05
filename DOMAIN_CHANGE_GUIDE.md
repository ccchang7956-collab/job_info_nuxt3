# 網域變更指南：nuxt3.opendgpa.site → opendgpa.shibaalin.com

本文說明如何將此專案的網域從 `nuxt3.opendgpa.site` 變更為 `opendgpa.shibaalin.com`。

---

## 概覽：需要修改的地方

| 項目 | 說明 |
|------|------|
| Cloudflare DNS | 在新網域添加 CNAME 記錄 |
| Cloudflared Tunnel | 添加新 hostname 到 config.yml |
| Nginx | 修改或添加 server_name |
| 後端 .env | 更新 SITE_DOMAIN |
| 前端（可選） | 如有硬編碼網域需修改 |

---

## 步驟一：Cloudflare DNS 設定

### 1. 登入 Cloudflare Dashboard

前往 [dash.cloudflare.com](https://dash.cloudflare.com) 並選擇 `shibaalin.com` 網域。

### 2. 添加 DNS 記錄

- **類型**：`CNAME`
- **名稱**：`opendgpa`
- **目標**：`e81dbb08-e43f-4783-ad6b-02eea6388e45.cfargotunnel.com`（你的 Tunnel ID）
- **Proxy 狀態**：**已代理**（橘色雲朵）

---

## 步驟二：修改 Cloudflared Tunnel 設定

```bash
sudo nano /etc/cloudflared/config.yml
```

在 `ingress` 區塊添加新的 hostname：

```yaml
tunnel: e81dbb08-e43f-4783-ad6b-02eea6388e45
credentials-file: /etc/cloudflared/e81dbb08-e43f-4783-ad6b-02eea6388e45.json

ingress:
  # 新網域
  - hostname: opendgpa.shibaalin.com
    service: http://127.0.0.1:80
  
  # 舊網域（可保留一段時間做重定向）
  - hostname: nuxt3.opendgpa.site
    service: http://127.0.0.1:80
  
  # 其他網域...
  - hostname: autovoucher.opendgpa.site
    service: http://127.0.0.1:80
  - hostname: vego2.opendgpa.site
    service: http://127.0.0.1:80
  - hostname: www.opendgpa.site
    service: http://127.0.0.1:80
  - hostname: opendgpa.site
    service: http://127.0.0.1:80
  - service: http_status:404
```

重啟 Cloudflared：

```bash
sudo systemctl restart cloudflared
```

---

## 步驟三：修改 Nginx 設定

```bash
sudo nano /etc/nginx/sites-available/job_info_nuxt3
```

修改 `server_name`：

```nginx
server {
    listen 80;
    # 新增新網域，保留舊網域
    server_name opendgpa.shibaalin.com nuxt3.opendgpa.site;
    
    # ... 其他設定保持不變
}
```

測試並重新載入 Nginx：

```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

## 步驟四：更新後端環境變數

```bash
nano /home/chang/job_info_nuxt3/backend/.env
```

修改 `SITE_DOMAIN`：

```bash
SITE_DOMAIN=https://opendgpa.shibaalin.com
```

重啟後端服務：

```bash
sudo systemctl restart job_info_nuxt3-backend
```

---

## 步驟五：更新前端（如需要）

本專案前端已經從後端動態取得網域，通常不需要修改。

但如果有任何硬編碼的網域，可搜尋並替換：

```bash
cd /home/chang/job_info_nuxt3
grep -r "nuxt3.opendgpa.site" --include="*.vue" --include="*.ts" --include="*.js"
```

---

## 步驟六：（可選）設定舊網域重定向

如果想讓舊網域自動跳轉到新網域，創建 Nginx 設定：

```bash
sudo nano /etc/nginx/sites-available/old-domain-redirect
```

```nginx
server {
    listen 80;
    server_name nuxt3.opendgpa.site;
    return 301 https://opendgpa.shibaalin.com$request_uri;
}
```

```bash
sudo ln -s /etc/nginx/sites-available/old-domain-redirect /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 步驟七：驗證

1. 開啟 `https://opendgpa.shibaalin.com`
2. 確認網站正常運作
3. 確認留言功能正常（CSRF 和 Turnstile）
4. 確認 LINE Bot 連結正確

---

## Google Analytics

如果已整合 GA4，**不需要修改**。GA4 會自動追蹤新網域的流量。

---

## 完成後的清理（可選）

過渡期結束後，可移除舊網域設定：

1. 從 Cloudflare DNS 刪除舊的 CNAME
2. 從 cloudflared config.yml 移除舊 hostname
3. 從 Nginx 移除舊 server_name
