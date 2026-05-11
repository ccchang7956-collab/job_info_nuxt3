FROM python:3.10-slim

WORKDIR /app

# 安裝必要的系統依賴 (如果需要編譯套件)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 複製並安裝 Python 依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式原始碼
COPY . .

# 暴露 FastAPI 埠
EXPOSE 8002

# 使用 gunicorn + uvicorn worker 啟動（正式環境，不使用 reload）
CMD ["gunicorn", "app.Main:app", \
     "-w", "2", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8002", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
