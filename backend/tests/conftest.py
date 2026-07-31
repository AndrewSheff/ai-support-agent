"""Тестовая инфраструктура — фикстуры, моки и прочая магия для запуска без реальной БД."""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.deps import get_current_user, require_admin
from app.core.rate_limit import limiter
from app.database import get_db
from app.main import app
from app.models.user import User

# Вырубаем rate limiter для тестов — нам Redis не нужен, мы тут по-быстрому
limiter.enabled = False


@pytest.fixture
def admin_user() -> User:
    """Фейковый админ — для тестов где нужен доступ к защищенным роутам."""
    user = MagicMock(spec=User)
    user.id = uuid.UUID("11111111-1111-1111-1111-111111111111")
    user.email = "admin@test.com"
    user.name = "Test Admin"
    user.role = "admin"
    user.is_active = True
    user.must_change_password = False
    user.password_hash = "$2b$12$fakehashfakehashfakehashfakehashfakehashfakehash"
    user.created_at = datetime(2025, 1, 1, tzinfo=UTC)
    user.updated_at = datetime(2025, 1, 1, tzinfo=UTC)
    return user


@pytest.fixture
def regular_user() -> User:
    """Обычный юзер — без привилегий, просто пользователь."""
    user = MagicMock(spec=User)
    user.id = uuid.UUID("22222222-2222-2222-2222-222222222222")
    user.email = "user@test.com"
    user.name = "Test User"
    user.role = "user"
    user.is_active = True
    user.must_change_password = False
    user.password_hash = "$2b$12$fakehashfakehashfakehashfakehashfakehashfakehash"
    user.created_at = datetime(2025, 1, 1, tzinfo=UTC)
    user.updated_at = datetime(2025, 1, 1, tzinfo=UTC)
    return user


@pytest.fixture
def mock_db() -> AsyncMock:
    """Мок-сессия БД — ничего никуда не ходит, все понарошку."""
    session = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.delete = AsyncMock()
    return session


@pytest.fixture
def override_admin(admin_user, mock_db):
    """Переопределяет зависимости FastAPI — текущий юзер = админ, БД = мок."""

    async def _get_admin():
        return admin_user

    async def _get_db():
        yield mock_db

    app.dependency_overrides[get_current_user] = _get_admin
    app.dependency_overrides[require_admin] = _get_admin
    app.dependency_overrides[get_db] = _get_db

    yield

    app.dependency_overrides.clear()


@pytest.fixture
def override_user(regular_user, mock_db):
    """Переопределяет зависимости FastAPI — текущий юзер = обычный, БД = мок."""

    async def _get_user():
        return regular_user

    async def _get_db():
        yield mock_db

    app.dependency_overrides[get_current_user] = _get_user
    app.dependency_overrides[get_db] = _get_db

    yield

    app.dependency_overrides.clear()


@pytest.fixture
async def async_client() -> AsyncClient:
    """HTTP-клиент для тестов — общается с приложением через ASGI, без сети."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
