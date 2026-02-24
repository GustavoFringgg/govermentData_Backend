FROM python:3.11-slim

# 安裝 Chromium 和對應的 ChromeDriver
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# 設定工作目錄
WORKDIR /app

# 先複製 requirements，利用 Docker layer cache 加速重建
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製所有程式碼
COPY . .

# Render 會自動注入 PORT 環境變數
EXPOSE 10000

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}"]
