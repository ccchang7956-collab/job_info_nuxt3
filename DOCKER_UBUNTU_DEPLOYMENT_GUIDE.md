# Ubuntu Server Docker 部署教學

這份教學將帶領您如何在全新的 Ubuntu 伺服器上，使用 Docker 與 Nginx 部署您的 Nuxt 3 前端與 FastAPI 後端專案。

為了節省您的時間，我已經在您的專案中預先建立好必要的 Docker 檔案設定，您只需依照以下步驟在 Ubuntu 主機上操作即可。

## 目錄
1. [伺服器環境準備 (Ubuntu)](#1-伺服器環境準備-ubuntu)
2. [將專案放上伺服器](#2-將專案放上伺服器)
3. [設定環境變數](#3-設定環境變數)
4. [啟動服務](#4-啟動服務)
5. [後續維護與更新](#5-後續維護與更新)

---

## 1. 伺服器環境準備 (Ubuntu)

請先透過 SSH 連線至您的全新 Ubuntu 伺服器：

```bash
ssh username@your_server_ip
```

### 安裝 Docker 與 Docker Compose

在 Ubuntu 終端機執行以下指令來自動安裝 Docker 與相關套件：

```bash
# 更新套件清單
sudo apt-get update

# 安裝必要的依賴工具
sudo apt-get install -y ca-certificates curl gnupg

# 新增 Docker 官方 GPG 金鑰
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# 設定 Docker 軟體源
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安裝 Docker 與 Docker Compose
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 啟動 Docker 並設定開機自動啟動
sudo systemctl enable docker
sudo systemctl start docker

# (可選) 將當前使用者加入 docker 群組，這樣以後就不用加 sudo
sudo usermod -aG docker $USER
# 請先登出再重新登入，或執行 `newgrp docker` 套用群組變更
```

### 安裝 Git

```bash
sudo apt-get install -y git
```

---

## 2. 將專案放上伺服器

將您的專案透過 Git Clone 到伺服器上（您可能需要先在伺服器產生 SSH Key 並加入 Github）：

```bash
# 假設專案放在 /opt/job_info_nuxt3
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

## 3. 設定環境變數

請在專案根目錄 (`/opt/job_info_nuxt3`) 建立一個 `.env` 檔案給 Docker Compose 使用：

```bash
# 建立一個新的 .env 檔案
nano .env
```

**重點說明：** 您需要將原本開發環境中 **`backend/.env`** 與 **`frontend-nuxt/.env`** 的內容「合併」貼進這個根目錄的 `.env` 中。我已經修改了 Docker 設定，讓前後端容器都能自動讀取這個共用的 `.env` 檔案。

> ⚠️ **特別注意 (資料庫設定)：**
> 檢查您貼過來的環境變數中是否有 `DATABASE_URL=mysql+aiomysql://root...` 這一行。
> 因為您原本使用的是 SQLite 資料庫（位於 `backend/database/data/` 並且我們已經將它掛載到容器），**如果您想要繼續在 Docker 內使用原本的 SQLite 資料庫，請將 `.env` 中的 `DATABASE_URL` 註解掉或是刪除**，讓程式自動 fallback 去讀取 SQLite。
> 如果不刪除，Backend 容器啟動時會嘗試去連線 localhost 的 MySQL 而導致連線失敗。

---

## 4. 啟動服務

現在萬事俱備，只需使用 Docker Compose 來建立映像檔並啟動容器：

```bash
# 在專案根目錄下執行 (如果沒有加 docker 群組則需要 sudo docker compose)
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

## 5. 後續維護與更新

未來當您的程式碼更新並 push 到 Git 之後，要在伺服器上更新部署，只需執行：

```bash
# 進入專案目錄
cd /opt/job_info_nuxt3

# 拉取最新程式碼
git pull

# 重新建立映像檔並重啟容器 (不會中斷太久)
docker compose up -d --build
```

### 關於 HTTPS (SSL 憑證)

目前 Nginx 預設設定是走 `http (80 埠)`，如果您有正式的網域名稱，強烈建議使用 **Certbot** 搭配 Nginx 產生免費的 HTTPS 憑證：

```bash
sudo apt install snapd
sudo snap install core; sudo snap refresh core
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot

# 執行 certbot 為 nginx 自動設定 SSL (必須先將網域 DNS 指向伺服器 IP)
sudo certbot --nginx
```

恭喜！您的系統已經成功容器化並部署完成！
