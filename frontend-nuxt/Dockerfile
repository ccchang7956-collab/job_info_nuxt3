# Build stage（需要 Node 20+ 以支援 Nuxt 4 / Vite 7）
FROM node:20-alpine AS builder

WORKDIR /app

# BACKEND_URL 必須在 build time 傳入，nuxt.config.ts 的 routeRules proxy 在建置時固化
ARG BACKEND_URL=http://backend:8002
ARG NUXT_PUBLIC_SITE_URL=https://opendgpa.shibaalin.com
ENV BACKEND_URL=$BACKEND_URL
ENV NUXT_PUBLIC_SITE_URL=$NUXT_PUBLIC_SITE_URL

# 安裝依賴（用 npm install 避免 Alpine musl 上 optional deps 的 bug）
COPY package*.json ./
RUN npm install

# 複製原始碼並編譯
COPY . .
RUN npm run build

# Production stage
FROM node:20-alpine

WORKDIR /app

# 複製編譯結果與 package.json
COPY --from=builder /app/.output ./.output
COPY --from=builder /app/package*.json ./

# Nuxt 預設執行的通訊埠
EXPOSE 3000

# 設定環境變數
ENV HOST=0.0.0.0
ENV PORT=3000
ENV NODE_ENV=production

# 啟動 Nuxt 伺服器
CMD ["node", ".output/server/index.mjs"]
