"""Кастомные исключения и обработчики ошибок для FastAPI — чтоб все было красиво и единообразно."""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.logging import get_logger

logger = get_logger(__name__)


class AppException(Exception):  # noqa: N818
    """Базовое исключение приложения — от него наследуются все остальные."""

    def __init__(self, detail: str, status_code: int = 500) -> None:
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


class NotFoundError(AppException):
    """Не нашли то, что искали — 404."""

    def __init__(self, detail: str = "Ресурс не найден") -> None:
        super().__init__(detail=detail, status_code=404)


class ForbiddenError(AppException):
    """Доступ запрещен — руки прочь, 403."""

    def __init__(self, detail: str = "Доступ запрещен") -> None:
        super().__init__(detail=detail, status_code=403)


class ConflictError(AppException):
    """Конфликт данных — такое уже есть, 409."""

    def __init__(self, detail: str = "Конфликт данных") -> None:
        super().__init__(detail=detail, status_code=409)


class BadRequestError(AppException):
    """Некорректный запрос — что-то не так с данными, 400."""

    def __init__(self, detail: str = "Некорректный запрос") -> None:
        super().__init__(detail=detail, status_code=400)


class ServiceUnavailableError(AppException):
    """Сервис недоступен — попробуйте позже, 503."""

    def __init__(self, detail: str = "Сервис временно недоступен") -> None:
        super().__init__(detail=detail, status_code=503)


def register_exception_handlers(app: FastAPI) -> None:
    """Регистрирует обработчики ошибок в FastAPI — AppException, валидация и все остальное."""

    @app.exception_handler(AppException)
    async def app_exception_handler(_request: Request, exc: AppException) -> JSONResponse:
        """Обработчик наших кастомных исключений — возвращает JSON с detail."""
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
        """Обработчик ошибок валидации Pydantic — 422 с подробностями, что именно не так."""
        # Pydantic V2 кидает в ctx объекты ValueError, которые не сериализуются в JSON,
        # поэтому убираем ctx и оставляем только полезное
        safe_errors = []
        for err in exc.errors():
            clean_err = {k: v for k, v in err.items() if k != "ctx"}
            safe_errors.append(clean_err)
        return JSONResponse(status_code=422, content={"detail": safe_errors})

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
        """Ловим все необработанные исключения — логируем и отдаем 500, чтоб внутренности не утекли."""
        logger.error("unhandled_exception", exc_type=type(exc).__name__, exc_detail=str(exc))
        return JSONResponse(status_code=500, content={"detail": "Внутренняя ошибка сервера"})
