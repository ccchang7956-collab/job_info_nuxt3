# 部署教學：Debian + Nginx + Cloudflared + SQLite

本文件說明如何將開放事求人專案部署到 Debian 主機上，使用 Nginx 作為反向代理，Cloudflared 進行安全隧道連接。

> **更新日期**: 2026-01-01
> 
> **資料庫**: SQLite（WAL 模式）

---

## 架構概覽

```
使用者 → Cloudflare Tunnel → Nginx → 前端 (Nuxt) / 後端 (FastAPI)
                                ↓
                           Port 3000 (Nuxt)
                           Port 8000 (FastAPI)
                                ↓
                           SQLite 資料庫
```

---

## 前置需求

- Debian 11/12 主機
- Root 或 sudo 權限
- Cloudflare 帳號
- 網域已加入 Cloudflare

---

## 步驟一：安裝基礎套件

```bash
# 更新系統
sudo apt update && sudo apt upgrade -y

# 安裝必要套件
sudo apt install -y git curl wget nginx python3 python3-pip python3-venv

# 安裝 Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# 確認版本
node -v    # v20.x
npm -v     # 10.x
python3 --version  # 3.x
```

---

## 步驟二：安裝 Cloudflared

```bash
# 下載並安裝 cloudflared
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared.deb

# 驗證安裝
cloudflared --version
```

---

## 步驟三：建立專案目錄

```bash
# 建立應用程式目錄
sudo mkdir -p /home/chang/job_info_nuxt3
sudo chown $USER:$USER /home/chang/job_info_nuxt3
cd /home/chang/job_info_nuxt3

# Clone 專案（或從本機 scp 上傳）
git clone <你的 repo URL> .
# 或
scp -r /path/to/local/project user@server:/home/chang/job_info_nuxt3
```

---

## 步驟四：設定後端 (FastAPI + SQLite)

```bash
cd /home/chang/job_info_nuxt3/backend

# 建立虛擬環境
python3 -m venv venv
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt

# 建立資料庫目錄
mkdir -p database/data

# 複製 SQLite 資料庫（從本機 Mac 上傳到伺服器）
scp ~/Project/job_info_nuxt3/backend/database/data/job_info.db chang@伺服器IP:/home/chang/job_info_nuxt3/backend/database/data/job_info.db

# 複製並編輯環境變數
cp .env.example .env
nano .env
```

### `.env` 設定範例

```env
# 資料庫 (SQLite - 預設已配置，通常不需修改)
# DATABASE_URL=sqlite:////home/chang/job_info_nuxt3/backend/database/data/job_info.db

# 環境模式
ENVIRONMENT=production

# CORS 允許的來源
CORS_ORIGINS=https://your-domain.com

# CSRF
CSRF_SECRET_KEY=你的隨機密鑰（至少32字元）

# reCAPTCHA
GOOGLE_RECAPTCHA_SECRET_KEY=你的密鑰

# 職缺同步 (選填)
JOB_DATA_URL=https://www.dgpa.gov.tw/op/want/wantjob_today.xml
```

### 建立 Systemd 服務

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
# 使用 Gunicorn + Uvicorn Worker (建議 Worker 數量: 2 × CPU 核心數 + 1)
ExecStart=/home/chang/job_info_nuxt3/backend/venv/bin/gunicorn app.Main:app \
  -w 3 \
  -k uvicorn.workers.UvicornWorker \
  --bind 127.0.0.1:8000 \
  --access-logfile - \
  --error-logfile -
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# 啟動服務
sudo systemctl daemon-reload
sudo systemctl enable job_info_nuxt3-backend
sudo systemctl start job_info_nuxt3-backend
sudo systemctl status job_info_nuxt3-backend
```

---

## 步驟五：設定前端 (Nuxt)

```bash
cd /home/chang/job_info_nuxt3/frontend-nuxt

# 安裝依賴
npm ci

# 建立生產環境設定
nano .env.production
```

### `.env.production` 設定

```env
NUXT_PUBLIC_RECAPTCHA_SITE_KEY=你的_site_key
```

### 建置生產版本

```bash
npm run build
```

### 建立 Systemd 服務

```bash
sudo nano /etc/systemd/system/job_info_nuxt3-frontend.service
```

```ini
[Unit]
Description=Job Portal Nuxt Frontend
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

## 步驟六：設定 Nginx

```bash
sudo nano /etc/nginx/sites-available/job_info_nuxt3
```

```nginx
server {
    listen 80;
    server_name localhost;  # Cloudflared 會處理 HTTPS

    # 安全標頭
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # 前端 (Nuxt)
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # 後端 API 代理（由 Nuxt 處理，這裡是備用）
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# 啟用網站設定
sudo ln -sf /etc/nginx/sites-available/job_info_nuxt3 /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# 測試設定
sudo nginx -t

# 重新載入
sudo systemctl reload nginx
```

---

## 步驟七：設定 Cloudflared Tunnel

### 登入 Cloudflare

```bash
cloudflared tunnel login
# 會開啟瀏覽器進行授權
```

### 建立 Tunnel

```bash
# 建立 tunnel
cloudflared tunnel create job_info_nuxt3

# 會輸出 Tunnel ID，記下來
# 例如：Created tunnel job_info_nuxt3 with id xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### 設定 DNS

```bash
# 將網域指向 tunnel
cloudflared tunnel route dns job_info_nuxt3 your-domain.com
```

### 建立設定檔

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

### 安裝為服務

```bash
sudo cloudflared service install
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
sudo systemctl status cloudflared
```

---

## 步驟八：設定檔案權限

```bash
# 設定正確的檔案權限
sudo chown -R www-data:www-data /home/chang/job_info_nuxt3
sudo chmod -R 755 /home/chang/job_info_nuxt3

# SQLite 資料庫需要寫入權限
sudo chmod 664 /home/chang/job_info_nuxt3/backend/database/data/job_info.db
sudo chmod 775 /home/chang/job_info_nuxt3/backend/database/data/
```

---

## 步驟九：設定定期同步（選填）

如果要自動同步職缺資料：

```bash
# 編輯 crontab
crontab -e

# 每天早上 8 點同步
0 8 * * * cd /home/chang/job_info_nuxt3/backend && ./venv/bin/python database/scripts/sync_jobs.py >> /var/log/job-sync.log 2>&1
```

---

## 驗證部署

```bash
# 檢查所有服務狀態
sudo systemctl status job_info_nuxt3-backend
sudo systemctl status job_info_nuxt3-frontend
sudo systemctl status nginx
sudo systemctl status cloudflared

# 本機測試
curl http://localhost:3000  # 前端
curl http://localhost:8000  # 後端 API

# 查看日誌
sudo journalctl -u job_info_nuxt3-backend -f
sudo journalctl -u job_info_nuxt3-frontend -f
sudo journalctl -u cloudflared -f
```

---

## 更新部署

當有新版本需要部署時：

```bash
cd /home/chang/job_info_nuxt3

# 拉取最新程式碼
git pull origin main

# 更新後端
cd backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart job_info_nuxt3-backend

# 更新前端
cd ../frontend-nuxt
npm ci
npm run build
sudo systemctl restart job_info_nuxt3-frontend
```

---

## SQLite 資料庫備份

```bash
# 手動備份
cp /home/chang/job_info_nuxt3/backend/database/data/job_info.db ~/backup/job_info_$(date +%Y%m%d).db

# 設定自動備份 (每天凌晨 3 點)
crontab -e
0 3 * * * cp /home/chang/job_info_nuxt3/backend/database/data/job_info.db /backup/job_info_$(date +\%Y\%m\%d).db
```

---

## 常見問題

### 服務無法啟動

```bash
# 查看詳細錯誤
sudo journalctl -u job_info_nuxt3-backend -n 50 --no-pager
sudo journalctl -u job_info_nuxt3-frontend -n 50 --no-pager
```

### SQLite 資料庫權限問題

```bash
# 確保 www-data 有權限讀寫
sudo chown www-data:www-data /home/chang/job_info_nuxt3/backend/database/data/job_info.db
sudo chmod 664 /home/chang/job_info_nuxt3/backend/database/data/job_info.db
```

### Cloudflared 無法連線

```bash
# 重新驗證
cloudflared tunnel login

# 檢查 tunnel 狀態
cloudflared tunnel info job_info_nuxt3
```

---

## 安全建議

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

## 專案結構

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
