FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl sqlite3 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

ENV PORT=8080
ENV APP_VERSION=1.0.0
ENV APP_ENV=production
ENV APP_COLOR=#1E88E5
ENV DATABASE_PATH=/data/orders.db

RUN mkdir -p /data

EXPOSE 8080

HEALTHCHECK --interval=5s --timeout=3s --retries=3 CMD curl -f http://localhost:8080/health || exit 1

CMD ["python", "app.py"]
