"""Rate limiting — ограничение частоты запросов через slowapi + Redis."""

from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def _get_user_or_ip(request: Request) -> str:
    """Определяет ключ для лимита — user_id из JWT или IP-адрес."""
    # Если пользователь аутентифицирован, используем его id
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        try:
            from app.core.security import verify_token

            token = auth.split(" ", 1)[1]
            payload = verify_token(token)
            user_id = payload.get("sub")
            if user_id:
                return f"user:{user_id}"
        except Exception:  # noqa: BLE001, S110 — при ошибке JWT просто фоллбэк на IP
            pass
    return get_remote_address(request)


def _get_ip_only(request: Request) -> str:
    """Всегда возвращает IP — для логина лимитируем именно по IP."""
    return get_remote_address(request)


# Redis URI для slowapi (переводим из redis:// формата)
_storage_uri = settings.redis_url

# Создаем лимитер с Redis backend
limiter = Limiter(
    key_func=_get_user_or_ip,
    storage_uri=_storage_uri,
    strategy="fixed-window",
)


def rate_limit_exceeded_handler(_request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Обработчик превышения лимита — возвращает 429 с понятным сообщением."""
    logger.warning("rate_limit_exceeded", detail=str(exc))
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please try again later."},
    )


# Декораторы для разных лимитов
login_limit = limiter.limit("10/minute", key_func=_get_ip_only)
api_limit = limiter.limit("60/minute")
upload_limit = limiter.limit("10/minute")
