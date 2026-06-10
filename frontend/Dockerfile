# ============================================================================
# 多階段構建：Stage 1 - 構建階段（Builder）
# ============================================================================
FROM node:22-alpine as builder

WORKDIR /app

# 複製 package.json 和 package-lock.json（利用 Docker Layer Cache）
COPY package*.json ./

# 使用 npm ci 進行確定性依賴安裝（比 npm install 更適合容器環境）
# npm ci 會根據 package-lock.json 安裝確切版本，保證構建可重現性
RUN npm ci

# 複製原始碼和構建配置
COPY . .

# 構建 Vite React 應用（生成 dist 目錄）
RUN npm run build


# ============================================================================
# Stage 2 - 生產環境映像（Nginx）
# ============================================================================
FROM nginx:alpine

# 設定工作目錄
WORKDIR /usr/share/nginx/html

# 從 builder 階段複製已構建的靜態檔案（dist 目錄）
COPY --from=builder /app/dist .

# 複製自訂的 Nginx 配置（支援 React SPA 路由）
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 設定檔案權限（Nginx 用戶 (www-data) 可讀取）
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html

# 開放 80 Port（Nginx 預設埠）
EXPOSE 80

# 健康檢查（驗證 Nginx 是否正常運行）
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:80/ || exit 1

# 啟動 Nginx
# daemon off：保持 Nginx 在前景執行，便於 Docker 容器日誌收集
CMD ["nginx", "-g", "daemon off;"]
