# 🐳 Docker 部署與重啟指南

當您修改了程式碼並推送至 GitHub 後，請依照以下步驟在主機上更新並重啟服務。

## 步驟一：連線至主機並拉取最新程式碼

1. 連線至您的主機 (SSH)：
   ```bash
   ssh username@your_server_ip
   ```
2. 切換至專案根目錄：
   ```bash
   cd ~/job_info_nuxt3
   ```
3. 拉取 GitHub 上的最新程式碼：
   ```bash
   git pull origin main
   ```

## 步驟二：重建並啟動 Docker 容器

**強烈建議**在程式碼更新後，使用以下指令重新構建映像檔並在背景啟動：
```bash
docker compose up -d --build
```
> **注意**：這會自動偵測有變更的 `backend` 或 `frontend` 並重新打包。

## 步驟三：重啟 Nginx 代理伺服器（重要防坑！）

當內部容器 (frontend/backend) 重啟時，Docker 會重新分配內部 IP。如果 Nginx 沒有跟著重啟，它會一直把請求送往舊的 IP，導致網頁出現 **502 Bad Gateway** 錯誤。

因此，**每次重建服務後，請務必重啟 nginx**：
```bash
docker compose restart nginx
```

---

## 其他實用指令

### 1. 只重啟單一服務 (不重新構建)
如果您只改了 `.env` 或不需編譯的設定，可以單獨重啟服務：
```bash
docker compose restart backend
docker compose restart frontend
```

### 2. 徹底關閉並重新啟動 (遇到不明卡死時使用)
```bash
docker compose down
docker compose up -d
docker compose restart nginx
```

### 3. 查看運行狀態
確認所有服務的 `STATUS` 是否都是 `Up`：
```bash
docker compose ps
```

### 4. 查看服務日誌 (排錯用)
如果網頁還是報錯，可以查看最新 100 行日誌來抓蟲 (按 `Ctrl + C` 退出)：
```bash
docker compose logs --tail=100 backend
docker compose logs --tail=100 frontend
docker compose logs --tail=100 nginx
```
