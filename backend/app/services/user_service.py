"""Сервис пользователей — CRUD, пагинация, профиль и всякие проверки на адекватность."""

import math

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.core.logging import get_logger
from app.core.security import generate_temporary_password, hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

logger = get_logger(__name__)


async def get_users(
    db: AsyncSession,
    page: int,
    per_page: int,
) -> dict:
    """Получает список юзеров с пагинацией — сортируем по дате создания, свежие сверху."""
    # Считаем общее количество
    count_result = await db.execute(select(func.count()).select_from(User))
    total = count_result.scalar_one()

    # Вычисляем количество страниц
    pages = math.ceil(total / per_page) if total > 0 else 1

    # Вытаскиваем юзеров с нужным offset
    offset = (page - 1) * per_page
    result = await db.execute(
        select(User).order_by(User.created_at.desc()).offset(offset).limit(per_page)
    )
    items = list(result.scalars().all())

    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": pages,
    }


async def create_user(
    db: AsyncSession,
    data: UserCreate,
) -> tuple[User, str]:
    """Создает нового юзера — проверяем дубликат email, генерим временный пароль, ставим must_change_password."""
    # Нормализуем email
    email = data.email.strip().lower()

    # Проверяем, не занят ли email
    existing = await db.execute(select(User).where(User.email == email))
    if existing.scalar_one_or_none() is not None:
        raise ConflictError(f"Пользователь с email {email} уже существует")

    # Генерируем временный пароль и хешируем
    temp_password = generate_temporary_password()
    password_hash = hash_password(temp_password)

    user = User(
        email=email,
        name=data.name,
        password_hash=password_hash,
        role=data.role,
        is_active=True,
        must_change_password=True,
    )
    db.add(user)
    await db.flush()

    logger.info("user_created", user_id=str(user.id), email=email, role=data.role)

    return user, temp_password


async def update_user(
    db: AsyncSession,
    user_id: str,
    data: UserUpdate,
    current_user: User,
) -> User:
    """Обновляет юзера частично — нельзя самому себе менять роль или деактивировать, это так не работает."""
    # Ищем юзера
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise NotFoundError("Пользователь не найден")

    # Проверяем, не пытается ли админ стрельнуть себе в ногу
    if str(current_user.id) == str(user.id):
        if data.role is not None:
            raise ForbiddenError("Нельзя менять свою роль")
        if data.is_active is not None:
            raise ForbiddenError("Нельзя деактивировать самого себя")

    # Partial update — обновляем только переданные поля
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    await db.flush()

    logger.info("user_updated", user_id=str(user.id), fields=list(update_data.keys()))

    return user


async def delete_user(
    db: AsyncSession,
    user_id: str,
    current_user: User,
) -> None:
    """Удаляет юзера насовсем — но не дадим удалить себя или последнего админа, это было бы больно."""
    # Ищем юзера
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise NotFoundError("Пользователь не найден")

    # Нельзя удалить самого себя
    if str(current_user.id) == str(user.id):
        raise ForbiddenError("Нельзя удалить самого себя")

    # Проверяем, не последний ли это активный админ
    if user.role == "admin" and user.is_active:
        admin_count_result = await db.execute(
            select(func.count())
            .select_from(User)
            .where(User.role == "admin", User.is_active.is_(True))
        )
        admin_count = admin_count_result.scalar_one()
        if admin_count <= 1:
            raise ForbiddenError("Нельзя удалить последнего активного администратора")

    await db.delete(user)
    await db.flush()

    logger.info("user_deleted", user_id=str(user.id), email=user.email)


async def update_profile(
    db: AsyncSession,
    user: User,
    name: str,
) -> User:
    """Обновляет имя текущего юзера — остальное трогать нельзя, только имечко."""
    user.name = name
    await db.flush()

    logger.info("profile_updated", user_id=str(user.id), name=name)

    return user
