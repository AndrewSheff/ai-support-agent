"""Структурированное логирование через structlog — JSON формат, request_id трассировка."""

import logging
import sys
import time
import uuid
from contextvars import ContextVar
from typing import Any

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

# Контекстная переменная для request_id — доступна во всех логах в рамках запроса
request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)


def add_request_id(
    logger: logging.Logger, method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Процессор structlog — добавляет request_id в каждое лог-сообщение."""
    rid = request_id_ctx.get()
    if rid:
        event_dict["request_id"] = rid
    return event_dict


def setup_logging(log_level: str = "INFO") -> None:
    """Настройка structlog — вызывается при старте приложения."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            add_request_id,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Настройка стандартного logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper(), logging.INFO),
    )


def get_logger(name: str = __name__) -> structlog.stdlib.BoundLogger:
    """Получить логгер для модуля."""
    return structlog.get_logger(name)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware — генерирует request_id, логирует каждый HTTP-запрос."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        rid = str(uuid.uuid4())
        request_id_ctx.set(rid)

        logger = get_logger("http")
        start_time = time.monotonic()

        response = await call_next(request)

        duration_ms = round((time.monotonic() - start_time) * 1000, 2)

        logger.info(
            "http_request",
            method=request.method,
            path=str(request.url.path),
            status=response.status_code,
            duration_ms=duration_ms,
            ip=request.client.host if request.client else None,
        )

        response.headers["X-Request-ID"] = rid
        return response
