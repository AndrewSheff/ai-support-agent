"""Безопасность — JWT-токены, хеширование паролей и всякие утилиты для авторизации."""

import re
import secrets
import string
from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# Контекст для bcrypt — стандартная связка passlib + bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Алгоритм подписи JWT
ALGORITHM = "HS256"


def create_access_token(data: dict) -> str:
    """Создает JWT-токен. Кидаем туда sub, email, role + exp и iat автоматом."""
    to_encode = data.copy()
    now = datetime.now(UTC)
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire, "iat": now})
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


def verify_token(token: str) -> dict:
    """Декодирует и проверяет JWT-токен. Если что-то не так — прилетит JWTError."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except JWTError:
        raise
    return payload


def hash_password(password: str) -> str:
    """Хеширует пароль через bcrypt — просто и надежно."""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Сверяет пароль с хешем — возвращает True если совпало."""
    return pwd_context.verify(plain, hashed)


def generate_temporary_password() -> str:
    """Генерирует временный пароль из 8 символов. Гарантированно будет хотя бы 1 буква и 1 цифра."""
    alphabet = string.ascii_letters + string.digits
    while True:
        password = "".join(secrets.choice(alphabet) for _ in range(8))
        if re.search(r"[a-zA-Z]", password) and re.search(r"\d", password):
            return password


def validate_password(password: str) -> bool:
    """Валидирует пароль: минимум 8 символов, максимум 128, хотя бы 1 буква и 1 цифра."""
    return bool(re.fullmatch(r"(?=.*[a-zA-Z])(?=.*\d).{8,128}", password))
