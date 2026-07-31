"""Точка входа FastAPI — инициализация приложения, middleware, lifespan."""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import RequestLoggingMiddleware, get_logger, setup_logging
from app.core.rate_limit import limiter, rate_limit_exceeded_handler

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Lifecycle приложения — старт и завершение."""
    setup_logging(settings.log_level)

    # Создаем директорию для загрузок
    os.makedirs(settings.upload_dir, exist_ok=True)

    # Создаем начального админа при первом запуске
    from app.database import async_session
    from app.services.auth_service import create_initial_admin

    async with async_session() as db:
        await create_initial_admin(db)

    logger.info(
        "app_startup",
        app_name=settings.app_name,
        version=settings.app_version,
        log_level=settings.log_level,
    )

    yield

    logger.info("app_shutdown")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    openapi_url="/openapi.json",
    docs_url="/docs",
    lifespan=lifespan,
)

# Rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Обработчики ошибок
register_exception_handlers(app)

# --- Middleware (порядок важен — последний добавленный выполняется первым) ---

# Логирование запросов
app.add_middleware(RequestLoggingMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# --- Роутеры ---
from app.api.v1.auth import router as auth_router  # noqa: E402
from app.api.v1.chat import router as chat_router  # noqa: E402
from app.api.v1.dashboard import router as dashboard_router  # noqa: E402
from app.api.v1.documents import router as documents_router  # noqa: E402
from app.api.v1.health import router as health_router  # noqa: E402
from app.api.v1.users import router as users_router  # noqa: E402

app.include_router(health_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")
