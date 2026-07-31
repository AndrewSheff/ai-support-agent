# ===================================
# Stage 1: Сборка зависимостей
# ===================================
FROM python:3.13-slim AS builder

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends libmagic1 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ===================================
# Stage 2: Runtime
# ===================================
FROM python:3.13-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends libmagic1 curl && \
    rm -rf /var/lib/apt/lists/*

RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

WORKDIR /app

COPY --from=builder /install /usr/local

COPY . .

RUN mkdir -p /app/uploads && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=40s \
  CMD curl -f http://localhost:8000/api/v1/health || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
