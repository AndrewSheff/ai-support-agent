"""Роутер здоровья — проверяем, что все компоненты системы дышат."""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.logging import get_logger
from app.database import get_db

router = APIRouter(prefix="/health", tags=["Health"])

logger = get_logger(__name__)


@router.get("/")
async def health_check(
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """Проверка здоровья системы — БД, Redis, наличие AI-ключей. Без авторизации, чтоб мониторинг мог дергать."""
    # Проверяем базу данных — простой SELECT 1
    db_status = "ok"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"
        logger.warning("health_check_db_failed")

    # Проверяем Redis — PING и ждем PONG
    redis_status = "ok"
    try:
        redis_client = Redis.from_url(settings.redis_url)
        try:
            await redis_client.ping()
        finally:
            await redis_client.aclose()
    except Exception:
        redis_status = "error"
        logger.warning("health_check_redis_failed")

    # Проверяем наличие API-ключей для AI-провайдеров — просто смотрим, заданы ли они
    ai_status = {
        "anthropic": bool(settings.anthropic_api_key),
        "openai": bool(settings.openai_api_key),
    }

    # Общий статус — healthy если БД в порядке, остальное некритично
    overall_status = "healthy" if db_status == "ok" else "unhealthy"
    status_code = 200 if db_status == "ok" else 503

    body = {
        "status": overall_status,
        "version": settings.app_version,
        "components": {
            "database": db_status,
            "redis": redis_status,
            "ai": ai_status,
        },
    }

    return JSONResponse(content=body, status_code=status_code)
