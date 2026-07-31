"""Тесты пользователей — CRUD, профиль, проверка доступа и прочие штуки."""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.exceptions import ConflictError, ForbiddenError
from app.models.user import User


@pytest.mark.asyncio
async def test_get_users_admin(async_client, override_admin, admin_user):
    """Админ запрашивает список юзеров — получает 200 и пагинацию, все красиво."""
    mock_result = {
        "items": [admin_user],
        "total": 1,
        "page": 1,
        "per_page": 20,
        "pages": 1,
    }

    with patch("app.api.v1.users.get_users", new_callable=AsyncMock, return_value=mock_result):
        response = await async_client.get(
            "/api/v1/users/",
            headers={"Authorization": "Bearer fake-token"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["page"] == 1


@pytest.mark.asyncio
async def test_get_users_forbidden(async_client, override_user):
    """Обычный юзер лезет в список пользователей — 403, руки прочь."""
    response = await async_client.get(
        "/api/v1/users/",
        headers={"Authorization": "Bearer fake-token"},
    )

    # require_admin не переопределен для обычного юзера — ловим 403
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_user_success(async_client, override_admin):
    """Админ создает юзера — получает 201 и данные нового пользователя."""
    new_user = MagicMock(spec=User)
    new_user.id = uuid.UUID("33333333-3333-3333-3333-333333333333")
    new_user.email = "newuser@test.com"
    new_user.name = "New User"
    new_user.role = "user"
    new_user.is_active = True
    new_user.created_at = datetime(2025, 1, 1, tzinfo=UTC)

    with patch(
        "app.api.v1.users.create_user",
        new_callable=AsyncMock,
        return_value=(new_user, "TempPass1"),
    ):
        response = await async_client.post(
            "/api/v1/users/",
            json={"email": "newuser@test.com", "name": "New User", "role": "user"},
            headers={"Authorization": "Bearer fake-token"},
        )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@test.com"
    assert data["temporary_password"] == "TempPass1"


@pytest.mark.asyncio
async def test_create_user_duplicate(async_client, override_admin):
    """Дубликат email — 409, такой юзер уже есть, не будем плодить клонов."""
    with patch(
        "app.api.v1.users.create_user",
        new_callable=AsyncMock,
        side_effect=ConflictError("Пользователь с email admin@test.com уже существует"),
    ):
        response = await async_client.post(
            "/api/v1/users/",
            json={"email": "admin@test.com", "name": "Duplicate", "role": "user"},
            headers={"Authorization": "Bearer fake-token"},
        )

    assert response.status_code == 409
    assert "уже существует" in response.json()["detail"]


@pytest.mark.asyncio
async def test_update_user(async_client, override_admin):
    """Обновление юзера — partial update, получаем 200 с обновленными данными."""
    updated_user = MagicMock(spec=User)
    updated_user.id = uuid.UUID("33333333-3333-3333-3333-333333333333")
    updated_user.email = "user@test.com"
    updated_user.name = "Updated Name"
    updated_user.role = "user"
    updated_user.is_active = True
    updated_user.created_at = datetime(2025, 1, 1, tzinfo=UTC)

    user_id = "33333333-3333-3333-3333-333333333333"

    with patch(
        "app.api.v1.users.update_user",
        new_callable=AsyncMock,
        return_value=updated_user,
    ):
        response = await async_client.patch(
            f"/api/v1/users/{user_id}",
            json={"name": "Updated Name"},
            headers={"Authorization": "Bearer fake-token"},
        )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"


@pytest.mark.asyncio
async def test_delete_user(async_client, override_admin):
    """Удаление юзера — 204, без тела в ответе, прощай юзер."""
    user_id = "33333333-3333-3333-3333-333333333333"

    with patch("app.api.v1.users.delete_user", new_callable=AsyncMock, return_value=None):
        response = await async_client.delete(
            f"/api/v1/users/{user_id}",
            headers={"Authorization": "Bearer fake-token"},
        )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_user_self(async_client, override_admin):
    """Админ пытается удалить сам себя — 403, нельзя стрелять себе в ногу."""
    user_id = "11111111-1111-1111-1111-111111111111"

    with patch(
        "app.api.v1.users.delete_user",
        new_callable=AsyncMock,
        side_effect=ForbiddenError("Нельзя удалить самого себя"),
    ):
        response = await async_client.delete(
            f"/api/v1/users/{user_id}",
            headers={"Authorization": "Bearer fake-token"},
        )

    assert response.status_code == 403
    assert "самого себя" in response.json()["detail"]


@pytest.mark.asyncio
async def test_update_profile(async_client, override_admin, admin_user):
    """Обновление своего профиля — меняем имя, все остальное не трогаем."""
    admin_user.name = "New Admin Name"

    with patch(
        "app.api.v1.users.update_profile",
        new_callable=AsyncMock,
        return_value=admin_user,
    ):
        response = await async_client.patch(
            "/api/v1/users/me/profile",
            json={"name": "New Admin Name"},
            headers={"Authorization": "Bearer fake-token"},
        )

    assert response.status_code == 200
    assert response.json()["name"] == "New Admin Name"
