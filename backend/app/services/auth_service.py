"""Сервис аутентификации — логин, смена пароля, создание начального админа."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import BadRequestError, ForbiddenError
from app.core.logging import get_logger
from app.core.security import (
    create_access_token,
    hash_password,
    validate_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import LoginResponse, UserInfo

logger = get_logger(__name__)


async def authenticate(db: AsyncSession, email: str, password: str) -> LoginResponse:
    """Аутентификация по email и паролю. Возвращает токен и инфу о юзере."""
    # Нормализуем email — в нижний регистр и без пробелов по краям
    email = email.strip().lower()

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(password, user.password_hash):
        raise BadRequestError("Неверный email или пароль")

    if not user.is_active:
        raise ForbiddenError("Аккаунт деактивирован")

    # Генерируем JWT-токен
    token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
        }
    )

    logger.info("user_authenticated", user_id=str(user.id), email=user.email)

    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user=UserInfo(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role,
            must_change_password=user.must_change_password,
        ),
    )


async def change_password(
    db: AsyncSession,
    user: User,
    current_password: str,
    new_password: str,
    confirm_password: str,
) -> None:
    """Смена пароля — проверяем текущий, валидируем новый, сохраняем."""
    # Проверяем текущий пароль
    if not verify_password(current_password, user.password_hash):
        raise BadRequestError("Неверный текущий пароль")

    # Новый пароль не должен совпадать с текущим
    if verify_password(new_password, user.password_hash):
        raise BadRequestError("Новый пароль не должен совпадать с текущим")

    # Подтверждение должно совпадать (доп. проверка, схема тоже валидирует)
    if new_password != confirm_password:
        raise BadRequestError("Пароли не совпадают")

    # Валидация сложности
    if not validate_password(new_password):
        raise BadRequestError(
            "Пароль должен содержать минимум 8 символов, хотя бы одну букву и одну цифру"
        )

    # Обновляем пароль
    user.password_hash = hash_password(new_password)
    user.must_change_password = False
    await db.flush()

    logger.info("password_changed", user_id=str(user.id))


async def create_initial_admin(db: AsyncSession) -> None:
    """Создает админа при первом запуске, если таблица пользователей пуста."""
    result = await db.execute(select(func.count()).select_from(User))
    user_count = result.scalar_one()

    if user_count > 0:
        logger.info("initial_admin_skip", reason="users_exist", count=user_count)
        return

    admin = User(
        email=settings.admin_email.strip().lower(),
        name=settings.admin_name,
        password_hash=hash_password(settings.admin_default_password),
        role="admin",
        is_active=True,
        must_change_password=True,
    )
    db.add(admin)
    await db.commit()

    logger.info(
        "initial_admin_created",
        email=settings.admin_email,
        name=settings.admin_name,
    )
