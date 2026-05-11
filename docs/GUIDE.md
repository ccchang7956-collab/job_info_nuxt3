# 系統部署與維護指南

本文件完整保留了專案的各項部署與設定細節。

---

# 1. 部署教學：Docker 方案 (Ubuntu)

## Ubuntu Server Docker 部署教學

這份教學將帶領您如何在全新的 Ubuntu 伺服器上，使用 Docker 與 Nginx 部署您的 Nuxt 3 前端與 FastAPI 後端專案。

為了節省您的時間，我已經在您的專案中預先建立好必要的 Docker 檔案設定，您只需依照以下步驟在 Ubuntu 主機上操作即可。

### 目錄
1. [伺服器環境準備 (Ubuntu)](#1-伺服器環境準備-ubuntu)
2. [將專案放上伺服器](#2-將專案放上伺服器)
3. [設定環境變數](#3-設定環境變數)
4. [啟動服務](#4-啟動服務)
5. [後續維護與更新](#5-後續維護與更新)

---

### 1. 伺服器環境準備 (Ubuntu)

請先透過 SSH 連線至您的全新 Ubuntu 伺服器：

```bash
ssh username@your_server_ip
```

#### 安裝 Docker 與 Docker Compose

在 Ubuntu 終端機執行以下指令來自動安裝 Docker 與相關套件：

```bash
## 更新套件清單
sudo apt-get update

## 安裝必要的依賴工具
sudo apt-get install -y ca-certificates curl gnupg

## 新增 Docker 官方 GPG 金鑰
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

## 設定 Docker 軟體源
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

## 安裝 Docker 與 Docker Compose
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

## 啟動 Docker 並設定開機自動啟動
sudo systemctl enable docker
sudo systemctl start docker

## (可選) 將當前使用者加入 docker 群組，這樣以後就不用加 sudo
sudo usermod -aG docker $USER
## 請先登出再重新登入，或執行 `newgrp docker` 套用群組變更
```

#### 安裝 Git

```bash
sudo apt-get install -y git
```

---

### 2. 將專案放上伺服器

將您的專案透過 Git Clone 到伺服器上（您可能需要先在伺服器產生 SSH Key 並加入 Github）：

```bash
## 假設專案放在 /opt/job_info_nuxt3
cd /opt
sudo git clone https://github.com/ccchang7956-collab/job_info_nuxt3.git
cd job_info_nuxt3
```

> **注意：** 本專案已包含以下 Docker 化必要的檔案：
> - `backend/Dockerfile`
> - `frontend-nuxt/Dockerfile`
> - `docker-compose.yml`
> - `nginx/default.conf`
>
> （上述檔案已經由我幫您建立在專案中並推送到 Git，您 clone 下來就會有囉！）

---

### 3. 設定環境變數

請在專案根目錄 (`/opt/job_info_nuxt3`) 建立一個 `.env` 檔案給 Docker Compose 使用：

```bash
## 建立一個新的 .env 檔案
nano .env
```

**重點說明：** 您需要將原本開發環境中 **`backend/.env`** 與 **`frontend-nuxt/.env`** 的內容「合併」貼進這個根目錄的 `.env` 中。我已經修改了 Docker 設定，讓前後端容器都能自動讀取這個共用的 `.env` 檔案。

> ⚠️ **特別注意 (資料庫設定)：**
> 檢查您貼過來的環境變數中是否有 `DATABASE_URL=mysql+aiomysql://root...` 這一行。
> 因為您原本使用的是 SQLite 資料庫（位於 `backend/database/data/` 並且我們已經將它掛載到容器），**如果您想要繼續在 Docker 內使用原本的 SQLite 資料庫，請將 `.env` 中的 `DATABASE_URL` 註解掉或是刪除**，讓程式自動 fallback 去讀取 SQLite。
> 如果不刪除，Backend 容器啟動時會嘗試去連線 localhost 的 MySQL 而導致連線失敗。

---

### 4. 啟動服務

現在萬事俱備，只需使用 Docker Compose 來建立映像檔並啟動容器：

```bash
## 在專案根目錄下執行 (如果沒有加 docker 群組則需要 sudo docker compose)
docker compose up -d --build
```

這個指令會執行：
1. 編譯前端的 Nuxt 3 專案並打包成 Node.js 服務 (`frontend` 容器，內部跑在 3000 埠口)。
2. 安裝後端的 Python 相依套件並啟動 FastAPI (`backend` 容器，內部跑在 8002 埠口)。
3. 啟動 Nginx 代理伺服器 (`nginx` 容器，監聽外部的 80 埠口)。

啟動完成後，你可以透過指令查看容器狀態：

```bash
docker compose ps
```

檢查服務日誌 (例如檢查後端是否正常)：

```bash
docker compose logs -f backend
```

此時，只要在瀏覽器輸入您 **Ubuntu 伺服器的 IP 地址** (例如 `http://192.168.1.100`)，Nginx 就會自動將請求導向至前端 Nuxt 服務；如果是 `/api/` 請求則會幫您移除前綴轉交給 Backend。

---

### 5. 後續維護與更新

未來當您的程式碼更新並 push 到 Git 之後，要在伺服器上更新部署，只需執行：

```bash
## 進入專案目錄
cd /opt/job_info_nuxt3

## 拉取最新程式碼
git pull

## 重新建立映像檔並重啟容器 (不會中斷太久)
docker compose up -d --build
```

#### 關於 HTTPS (SSL 憑證)

目前 Nginx 預設設定是走 `http (80 埠)`，如果您有正式的網域名稱，強烈建議使用 **Certbot** 搭配 Nginx 產生免費的 HTTPS 憑證：

```bash
sudo apt install snapd
sudo snap install core; sudo snap refresh core
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot

## 執行 certbot 為 nginx 自動設定 SSL (必須先將網域 DNS 指向伺服器 IP)
sudo certbot --nginx
```

恭喜！您的系統已經成功容器化並部署完成！


---

# 2. 部署教學：Bare Metal 方案 (Debian + Nginx + Cloudflared + SQLite)

## 部署教學：Debian + Nginx + Cloudflared + SQLite

本文件說明如何將開放事求人專案部署到 Debian 主機上，使用 Nginx 作為反向代理，Cloudflared 進行安全隧道連接。

> **更新日期**: 2026-01-01
> 
> **資料庫**: SQLite（WAL 模式）

---

### 架構概覽

```
使用者 → Cloudflare Tunnel → Nginx → 前端 (Nuxt) / 後端 (FastAPI)
                                ↓
                           Port 3000 (Nuxt)
                           Port 8000 (FastAPI)
                                ↓
                           SQLite 資料庫
```

---

### 前置需求

- Debian 11/12 主機
- Root 或 sudo 權限
- Cloudflare 帳號
- 網域已加入 Cloudflare

---

### 步驟一：安裝基礎套件

```bash
## 更新系統
sudo apt update && sudo apt upgrade -y

## 安裝必要套件
sudo apt install -y git curl wget nginx python3 python3-pip python3-venv

## 安裝 Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

## 確認版本
node -v    # v20.x
npm -v     # 10.x
python3 --version  # 3.x
```

---

### 步驟二：安裝 Cloudflared

```bash
## 下載並安裝 cloudflared
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared.deb

## 驗證安裝
cloudflared --version
```

---

### 步驟三：建立專案目錄

```bash
## 建立應用程式目錄
sudo mkdir -p /home/chang/job_info_nuxt3
sudo chown $USER:$USER /home/chang/job_info_nuxt3
cd /home/chang/job_info_nuxt3

## Clone 專案（或從本機 scp 上傳）
git clone <你的 repo URL> .
## 或
scp -r /path/to/local/project user@server:/home/chang/job_info_nuxt3
```

---

### 步驟四：設定後端 (FastAPI + SQLite)

```bash
cd /home/chang/job_info_nuxt3/backend

## 建立虛擬環境
python3 -m venv venv
source venv/bin/activate

## 安裝依賴
pip install -r requirements.txt

## 建立資料庫目錄
mkdir -p database/data

## 複製 SQLite 資料庫（在本機 Mac 的終端機執行，不是伺服器上）
scp ~/Project/job_info_nuxt3/backend/database/data/job_info.db chang@100.102.52.24:/home/chang/job_info_nuxt3/backend/database/data/job_info.db

## 複製並編輯環境變數
cp .env.example .env
nano .env
```

#### `.env` 設定範例

```env
## 資料庫 (SQLite - 預設已配置，通常不需修改)
## DATABASE_URL=sqlite:////home/chang/job_info_nuxt3/backend/database/data/job_info.db

## 環境模式
ENVIRONMENT=production

## CORS 允許的來源
CORS_ORIGINS=https://your-domain.com

## CSRF
CSRF_SECRET_KEY=你的隨機密鑰（至少32字元）

## Cloudflare Turnstile
CLOUDFLARE_TURNSTILE_SECRET_KEY=你的密鑰

## 職缺同步 (選填)
JOB_DATA_URL=https://www.dgpa.gov.tw/op/want/wantjob_today.xml
```

#### 建立 Systemd 服務

```bash
sudo nano /etc/systemd/system/job_info_nuxt3-backend.service
```

```ini
[Unit]
Description=Job Info Nuxt3 FastAPI Backend
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/home/chang/job_info_nuxt3/backend
Environment="PATH=/home/chang/job_info_nuxt3/backend/venv/bin"
## 使用 Gunicorn + Uvicorn Worker (建議 Worker 數量: 2 × CPU 核心數 + 1)
ExecStart=/home/chang/job_info_nuxt3/backend/venv/bin/gunicorn app.Main:app \
  -w 3 \
  -k uvicorn.workers.UvicornWorker \
  --bind 127.0.0.1:8002 \
  --access-logfile - \
  --error-logfile -
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
## 啟動服務
sudo systemctl daemon-reload
sudo systemctl enable job_info_nuxt3-backend
sudo systemctl start job_info_nuxt3-backend
sudo systemctl status job_info_nuxt3-backend
```

---

### 步驟五：設定前端 (Nuxt)

```bash
cd /home/chang/job_info_nuxt3/frontend-nuxt

## 安裝依賴
npm ci

## 建立環境變數設定
nano .env
```

#### `.env` 設定

```env
NUXT_PUBLIC_TURNSTILE_SITE_KEY=你的_site_key
```

#### 建置生產版本

```bash
npm run build
```

#### 建立 Systemd 服務

```bash
sudo nano /etc/systemd/system/job_info_nuxt3-frontend.service
```

```ini
[Unit]
Description=Job Info Nuxt3 Frontend
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/home/chang/job_info_nuxt3/frontend-nuxt
ExecStart=/usr/bin/node .output/server/index.mjs
Environment="NODE_ENV=production"
Environment="HOST=127.0.0.1"
Environment="PORT=3000"
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable job_info_nuxt3-frontend
sudo systemctl start job_info_nuxt3-frontend
sudo systemctl status job_info_nuxt3-frontend
```

---

### 步驟六：設定 Nginx

```bash
sudo nano /etc/nginx/sites-available/job_info_nuxt3
```

```nginx
server {
    listen 80;
    server_name nuxt3.opendgpa.site;

    # Cloudflare 真實 IP 設定（搭配 Cloudflare Tunnel 使用）
    set_real_ip_from 127.0.0.1;
    real_ip_header CF-Connecting-IP;

    # 安全標頭
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # 前端 (Nuxt SSR - port 3001)
    location / {
        proxy_pass http://127.0.0.1:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
    }

    # 後端 API (FastAPI - port 8002)
    location /api/ {
        proxy_pass http://127.0.0.1:8002/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        client_max_body_size 10M;
    }
}
```

```bash
## 啟用網站設定
sudo ln -sf /etc/nginx/sites-available/job_info_nuxt3 /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

## 測試設定
sudo nginx -t

## 重新載入
sudo systemctl reload nginx
```

---

### 步驟七：設定 Cloudflared Tunnel

#### 登入 Cloudflare

```bash
cloudflared tunnel login
## 會開啟瀏覽器進行授權
```

#### 建立 Tunnel

```bash
## 建立 tunnel
cloudflared tunnel create job_info_nuxt3

## 會輸出 Tunnel ID，記下來
## 例如：Created tunnel job_info_nuxt3 with id xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

#### 設定 DNS

```bash
## 將網域指向 tunnel
cloudflared tunnel route dns job_info_nuxt3 your-domain.com
```

#### 建立設定檔

```bash
sudo mkdir -p /etc/cloudflared
sudo nano /etc/cloudflared/config.yml
```

```yaml
tunnel: <你的 Tunnel ID>
credentials-file: /root/.cloudflared/<Tunnel ID>.json

ingress:
  - hostname: your-domain.com
    service: http://localhost:80
  - service: http_status:404
```

#### 安裝為服務

```bash
sudo cloudflared service install
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
sudo systemctl status cloudflared
```

---

### 步驟八：設定檔案權限

```bash
## 設定正確的檔案權限
sudo chown -R www-data:www-data /home/chang/job_info_nuxt3
sudo chmod -R 755 /home/chang/job_info_nuxt3

## SQLite 資料庫需要寫入權限
sudo chmod 664 /home/chang/job_info_nuxt3/backend/database/data/job_info.db
sudo chmod 775 /home/chang/job_info_nuxt3/backend/database/data/
```

---

### 步驟九：設定定期同步（選填）

如果要自動同步職缺資料：

```bash
## 編輯 crontab
crontab -e

## 每天早上 8 點同步
0 8 * * * cd /home/chang/job_info_nuxt3/backend && ./venv/bin/python database/scripts/sync_jobs.py >> /var/log/job-sync.log 2>&1
```

---

### 驗證部署

```bash
## 檢查所有服務狀態
sudo systemctl status job_info_nuxt3-backend
sudo systemctl status job_info_nuxt3-frontend
sudo systemctl status nginx
sudo systemctl status cloudflared

## 本機測試
curl http://localhost:3000  # 前端
curl http://localhost:8002  # 後端 API

## 查看日誌
sudo journalctl -u job_info_nuxt3-backend -f
sudo journalctl -u job_info_nuxt3-frontend -f
sudo journalctl -u cloudflared -f
```

---

### 更新部署

當有新版本需要部署時：

```bash
cd /home/chang/job_info_nuxt3

## 拉取最新程式碼
git pull origin main

## 更新後端
cd backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart job_info_nuxt3-backend

## 更新前端
cd ../frontend-nuxt
npm ci
npm run build
sudo systemctl restart job_info_nuxt3-frontend
```

---

### SQLite 資料庫備份

```bash
## 手動備份
cp /home/chang/job_info_nuxt3/backend/database/data/job_info.db ~/backup/job_info_$(date +%Y%m%d).db

## 設定自動備份 (每天凌晨 3 點)
crontab -e
0 3 * * * cp /home/chang/job_info_nuxt3/backend/database/data/job_info.db /backup/job_info_$(date +\%Y\%m\%d).db
```

---

### 常見問題

#### 服務無法啟動

```bash
## 查看詳細錯誤
sudo journalctl -u job_info_nuxt3-backend -n 50 --no-pager
sudo journalctl -u job_info_nuxt3-frontend -n 50 --no-pager
```

#### SQLite 資料庫權限問題

```bash
## 確保 www-data 有權限讀寫
sudo chown www-data:www-data /home/chang/job_info_nuxt3/backend/database/data/job_info.db
sudo chmod 664 /home/chang/job_info_nuxt3/backend/database/data/job_info.db
```

#### Cloudflared 無法連線

```bash
## 重新驗證
cloudflared tunnel login

## 檢查 tunnel 狀態
cloudflared tunnel info job_info_nuxt3
```

---

### 安全建議

1. **防火牆**：只開放必要端口（443 由 Cloudflare 處理）
   ```bash
   sudo ufw allow ssh
   sudo ufw enable
   ```

2. **定期更新**：
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

3. **監控日誌**：定期檢查 `/var/log/nginx/` 和 systemd 日誌

4. **備份資料庫**：設定定期備份排程（見上方 SQLite 備份段落）

---

### 專案結構

```
/home/chang/job_info_nuxt3/
├── backend/
│   ├── app/                    # FastAPI 應用程式
│   ├── database/
│   │   ├── data/
│   │   │   └── job_info.db    # SQLite 資料庫
│   │   ├── migrations/         # SQL 遷移腳本
│   │   └── scripts/
│   │       └── sync_jobs.py   # 職缺同步腳本
│   ├── venv/                   # Python 虛擬環境
│   ├── .env                    # 環境變數
│   └── requirements.txt
└── frontend-nuxt/
    ├── .output/                # 建置輸出
    ├── .env.production
    └── package.json
```


---

# 3. 功能設定：Cloudflare Turnstile

## Cloudflare Turnstile 設定教學

本文件說明如何取得並設定 Cloudflare Turnstile 金鑰，用於取代 Google reCAPTCHA 進行機器人驗證。

### 什麼是 Cloudflare Turnstile？

Cloudflare Turnstile 是一個免費的 CAPTCHA 替代方案，具有以下優點：

- ✅ **完全免費**，無使用次數限制
- ✅ **隱私友善**，不追蹤使用者
- ✅ **使用者體驗佳**，通常不需要點選圖片
- ✅ **快速驗證**，大多數情況下無需使用者互動

---

### 步驟一：註冊/登入 Cloudflare

1. 前往 [Cloudflare Dashboard](https://dash.cloudflare.com)
2. 使用現有帳號登入，或註冊新帳號（免費）

---

### 步驟二：前往 Turnstile 頁面

1. 登入後，在左側選單找到並點擊 **「Turnstile」**
2. 或直接前往：https://dash.cloudflare.com/?to=/:account/turnstile

---

### 步驟三：建立 Widget

1. 點擊 **「Add Widget」** 按鈕

2. 填寫表單：

   | 欄位 | 說明 | 範例 |
   |------|------|------|
   | Widget name | 自訂名稱 | `job-portal-comments` |
   | Hostname | 網站網域 | `localhost`, `your-domain.com` |
   | Widget Mode | 驗證模式 | 選擇 **Managed**（推薦） |

3. 點擊 **「Create」** 建立

---

### 步驟四：取得金鑰

建立完成後，你會看到兩個金鑰：

#### Site Key（網站金鑰）
- 用於**前端**
- 可以公開
- 格式：`0x4AAAAAAA...`

#### Secret Key（密鑰）
- 用於**後端**
- ⚠️ **不可公開**
- 格式：`0x4AAAAAAA...`

---

### 步驟五：設定環境變數

#### 前端 (Nuxt)

在 `frontend-nuxt/.env` 或 `nuxt.config.ts` 的 `runtimeConfig` 中設定：

```env
NUXT_PUBLIC_TURNSTILE_SITE_KEY=你的_Site_Key
```

#### 後端 (FastAPI)

在 `backend/.env` 中設定：

```env
CLOUDFLARE_TURNSTILE_SECRET_KEY=你的_Secret_Key
```

---

### Widget 模式說明

| 模式 | 說明 | 適用場景 |
|------|------|----------|
| **Managed** | 自動決定是否需要挑戰 | 一般網站（推薦） |
| **Non-interactive** | 完全隱形，無需互動 | 低風險操作 |
| **Invisible** | 在需要時才顯示挑戰 | 表單提交 |

---

### 相關連結

- [Cloudflare Turnstile 官方文件](https://developers.cloudflare.com/turnstile/)
- [Turnstile Dashboard](https://dash.cloudflare.com/?to=/:account/turnstile)
- [Client-side API 參考](https://developers.cloudflare.com/turnstile/get-started/client-side-rendering/)
- [Server-side 驗證 API](https://developers.cloudflare.com/turnstile/get-started/server-side-validation/)

---

### 下一步

取得金鑰後，需要修改以下檔案來整合 Turnstile：

1. `nuxt.config.ts` - 載入 Turnstile 腳本
2. `composables/useComments.ts` - 替換 reCAPTCHA 邏輯
3. `components/CommentSection.vue` - 替換 widget 容器
4. `backend/app/Services/CommentService.py` - 替換驗證 API


---

# 4. 功能設定：Google Analytics 4 (GA4)

## Google Analytics 4 (GA4) 引入教學

本文說明如何在此 Nuxt 4 專案中引入 Google Analytics 4。

---

### 步驟一：建立 GA4 資源並取得測量 ID

#### 1. 登入 Google Analytics

前往 [analytics.google.com](https://analytics.google.com/) 並使用 Google 帳號登入。

#### 2. 建立帳戶（首次使用）

如果是首次使用，點擊「**開始測量**」，然後：

1. **帳戶名稱**：輸入你的組織或專案名稱（例如：`開放事求人`）
2. 勾選資料分享選項（可全選或依需求）
3. 點擊「**下一步**」

#### 3. 建立資源（Property）

1. **資源名稱**：輸入網站名稱（例如：`開放事求人網站`）
2. **報表時區**：選擇 `(GMT+08:00) 台北`
3. **貨幣**：選擇 `新台幣 (TWD)`
4. 點擊「**下一步**」

#### 4. 填寫商家資訊

1. **行業類別**：選擇最接近的（例如：`就業`）
2. **商家規模**：選擇適當的
3. 點擊「**下一步**」

#### 5. 選擇業務目標（可多選）

- ✅ 產生待開發客戶
- ✅ 提高品牌知名度
- ✅ 檢查使用者行為

點擊「**建立**」

#### 6. 設定資料串流

1. 選擇平台：點擊「**網頁**」
2. 輸入網站網址：`https://nuxt3.opendgpa.site`（或你的網域）
3. 輸入串流名稱：`主網站`
4. 點擊「**建立串流**」

#### 7. 取得測量 ID

建立完成後會看到：

```
測量 ID: G-XXXXXXXXXX
```

**複製這個 ID**，後續步驟會用到。

> 💡 也可以從：**管理** (齒輪圖示) → **資料串流** → 點擊你的串流 → 查看「測量 ID」

---

### 步驟二：安裝 Nuxt GA4 模組

```bash
cd frontend-nuxt
npm install nuxt-gtag
```

---

### 步驟三：設定 nuxt.config.ts

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

### 步驟四：設定環境變數

#### 開發環境 (frontend-nuxt/.env)

```bash
NUXT_PUBLIC_GTAG_ID=G-XXXXXXXXXX
```

#### 生產環境 (伺服器)

在伺服器的 `.env` 或 systemd 服務中設定：

```bash
NUXT_PUBLIC_GTAG_ID=G-XXXXXXXXXX
```

---

### 步驟五：更新 CSP 設定

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

### 步驟六：追蹤自訂事件（可選）

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

### 步驟七：驗證安裝確認

部署完成後，請依序進行以下檢查：

#### 1. 使用 Google Analytics 即時報表

最直接的方式：
1. 開啟您的網站：`https://opendgpa.shibaalin.com`
2. 同時開啟 [Google Analytics 後台](https://analytics.google.com)
3. 進入 **報表** > **即時**
4. 應該要在幾秒鐘內看到 "過去 30 分鐘內的使用者" 數字至少為 1

#### 2. 使用瀏覽器開發者工具 (Chrome DevTools)

1. 在網站上按 `F12` 或 `右鍵 > 檢查` 開啟開發者工具
2. 切換到 **Network (網路)** 分頁
3. 在搜尋過濾框輸入 `collect` 或 `google-analytics`
4. 重新整理頁面
5. 如果設定成功，應該會看到發往 `www.google-analytics.com/g/collect` 的請求，狀態碼為 `200` 或 `204`

#### 3. 使用 Google Analytics Debugger (Chrome 擴充功能)

更專業的除錯方式：
1. 安裝 Chrome 擴充功能：[Google Analytics Debugger](https://chrome.google.com/webstore/detail/google-analytics-debugger/jnkmfdileelhofjcijamephohjechjna)
2. 開啟擴充功能（點擊圖示顯示 ON）
3. 開啟開發者工具的 **Console (主控台)** 分頁
4. 重新整理頁面，您會看到詳細的 GA4 事件紀錄，例如 `Processing field: ...`

---

### 注意事項

- **GDPR/隱私**: 如果有歐洲用戶，考慮加入 Cookie 同意機制
- **測試環境**: 可設定不同的測量 ID 避免污染生產數據
- **Adblocker**: 部分用戶使用廣告阻擋器，GA 追蹤可能被阻擋

---

### 參考資源

- [nuxt-gtag 官方文件](https://nuxt.com/modules/gtag)
- [Google Analytics 4 說明](https://support.google.com/analytics/answer/9304153)


---

# 5. 維護指南：網域變更

## 網域變更指南：nuxt3.opendgpa.site → opendgpa.shibaalin.com

本文說明如何將此專案的網域從 `nuxt3.opendgpa.site` 變更為 `opendgpa.shibaalin.com`。

---

### 概覽：需要修改的地方

| 項目 | 說明 |
|------|------|
| Cloudflare DNS | 在新網域添加 CNAME 記錄 |
| Cloudflared Tunnel | 添加新 hostname 到 config.yml |
| Nginx | 修改或添加 server_name |
| 後端 .env | 更新 SITE_DOMAIN |
| 前端（可選） | 如有硬編碼網域需修改 |

---

### 步驟一：Cloudflare DNS 設定

#### 1. 登入 Cloudflare Dashboard

前往 [dash.cloudflare.com](https://dash.cloudflare.com) 並選擇 `shibaalin.com` 網域。

#### 2. 添加 DNS 記錄

- **類型**：`CNAME`
- **名稱**：`opendgpa`
- **目標**：`e81dbb08-e43f-4783-ad6b-02eea6388e45.cfargotunnel.com`（你的 Tunnel ID）
- **Proxy 狀態**：**已代理**（橘色雲朵）

---

### 步驟二：修改 Cloudflared Tunnel 設定

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
  
  # 其他網域...
  - hostname: autovoucher.opendgpa.site
    service: http://127.0.0.1:80
  - hostname: vego2.opendgpa.site
    service: http://127.0.0.1:80
  - service: http_status:404
```

重啟 Cloudflared：

```bash
sudo systemctl restart cloudflared
```

---

### 步驟三：修改 Nginx 設定

```bash
sudo nano /etc/nginx/sites-available/job_info_nuxt3
```

修改 `server_name`：

```nginx
server {
    listen 80;
    server_name opendgpa.shibaalin.com;
    
    # ... 其他設定保持不變
}
```

測試並重新載入 Nginx：

```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

### 步驟四：更新後端環境變數

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

### 步驟五：更新前端（如需要）

本專案前端已經從後端動態取得網域，通常不需要修改。

但如果有任何硬編碼的網域，可搜尋並替換：

```bash
cd /home/chang/job_info_nuxt3
grep -r "nuxt3.opendgpa.site" --include="*.vue" --include="*.ts" --include="*.js"
```

---

### 步驟六：驗證

1. 開啟 `https://opendgpa.shibaalin.com`
2. 確認網站正常運作
3. 確認留言功能正常（CSRF 和 Turnstile）
4. 確認 LINE Bot 連結正確

---

### Google Analytics

如果已整合 GA4，**不需要修改**。GA4 會自動追蹤新網域的流量。


---

