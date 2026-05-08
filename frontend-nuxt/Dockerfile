# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# 安裝依賴
COPY package*.json ./
RUN npm ci

# 複製原始碼並編譯
COPY . .
RUN npm run build

# Production stage
FROM node:18-alpine

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
