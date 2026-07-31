"""Тесты аутентификации — логин, смена пароля и все что с этим связано."""

import uuid
from unittest.mock import AsyncMock, patch

import pytest

from app.core.exceptions import BadRequestError, ForbiddenError
from app.schemas.auth import LoginResponse, UserInfo


@pytest.mark.asyncio
async def test_login_success(async_client, mock_db):
    """Успешный логин — получаем токен и данные юзера, все четко."""
    login_response = LoginResponse(
        access_token="fake-jwt-token",
        token_type="bearer",
        user=UserInfo(
            id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
            email="admin@test.com",
            name="Test Admin",
            role="admin",
            must_change_password=False,
        ),
    )

    from app.database import get_db
    from app.main import app

    async def _mock_db():
        yield mock_db

    app.dependency_overrides[get_db] = _mock_db

    with patch("app.api.v1.auth.authenticate", new_callable=AsyncMock, return_value=login_response):
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": "admin@test.com", "password": "Admin123"},
        )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["access_token"] == "fake-jwt-token"
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "admin@test.com"


@pytest.mark.asyncio
async def test_login_invalid_credentials(async_client, mock_db):
    """Неверный пароль — ловим 400, как и положено при кривых кредах."""

    from app.database import get_db
    from app.main import app

    async def _mock_db():
        yield mock_db

    app.dependency_overrides[get_db] = _mock_db

    with patch(
        "app.api.v1.auth.authenticate",
        new_callable=AsyncMock,
        side_effect=BadRequestError("Неверный email или пароль"),
    ):
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": "admin@test.com", "password": "wrongpassword"},
        )

    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert "Неверный email или пароль" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_deactivated(async_client, mock_db):
    """Заблокированный аккаунт — 403, тут без вариантов."""

    from app.database import get_db
    from app.main import app

    async def _mock_db():
        yield mock_db

    app.dependency_overrides[get_db] = _mock_db

    with patch(
        "app.api.v1.auth.authenticate",
        new_callable=AsyncMock,
        side_effect=ForbiddenError("Аккаунт деактивирован"),
    ):
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": "blocked@test.com", "password": "Admin123"},
        )

    app.dependency_overrides.clear()

    assert response.status_code == 403
    assert "деактивирован" in response.json()["detail"]


@pytest.mark.asyncio
async def test_change_password_success(async_client, override_admin):
    """Смена пароля — все корректно, получаем сообщение об успехе."""
    with patch("app.api.v1.auth.change_password", new_callable=AsyncMock, return_value=None):
        response = await async_client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "OldPassword1",
                "new_password": "NewPassword1",
                "confirm_password": "NewPassword1",
            },
            headers={"Authorization": "Bearer fake-token"},
        )

    assert response.status_code == 200
    assert response.json()["message"] == "Пароль успешно изменен"


@pytest.mark.asyncio
async def test_change_password_wrong_current(async_client, override_admin):
    """Неверный текущий пароль — сервис кидает 400, и правильно делает."""
    with patch(
        "app.api.v1.auth.change_password",
        new_callable=AsyncMock,
        side_effect=BadRequestError("Неверный текущий пароль"),
    ):
        response = await async_client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "WrongPassword1",
                "new_password": "NewPassword1",
                "confirm_password": "NewPassword1",
            },
            headers={"Authorization": "Bearer fake-token"},
        )

    assert response.status_code == 400
    assert "Неверный текущий пароль" in response.json()["detail"]


@pytest.mark.asyncio
async def test_change_password_mismatch(async_client, override_admin):
    """Пароли не совпадают — Pydantic валидация поймает и отправит 422."""
    response = await async_client.post(
        "/api/v1/auth/change-password",
        json={
            "current_password": "OldPassword1",
            "new_password": "NewPassword1",
            "confirm_password": "DifferentPassword1",
        },
        headers={"Authorization": "Bearer fake-token"},
    )

    assert response.status_code == 422
