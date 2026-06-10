FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY requirement.txt .

# 優化：利用快取先安裝依賴
RUN pip install --no-cache-dir -r requirement.txt

COPY . .

# 安全性：建立非 root 權限
RUN useradd -m appuser
USER appuser

EXPOSE 8000

# 啟動指令
CMD [ \
  "uvicorn", \
  "app.main:app", \
  "--host", \
  "0.0.0.0", \
  "--port", \
  "8000" \
]
