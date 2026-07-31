"""Тесты дашборда — статистика, активность, топ вопросов и проверка прав."""

from unittest.mock import AsyncMock, patch

import pytest

from app.schemas.dashboard import (
    ActivityItem,
    ActivityResponse,
    StatsResponse,
    TopQuestionItem,
    TopQuestionsResponse,
)


@pytest.mark.asyncio
async def test_get_stats(async_client, override_admin):
    """Получение статистики — 200, все цифры на месте."""
    mock_stats = StatsResponse(
        total_users=10,
        active_users=8,
        total_documents=5,
        indexed_documents=3,
        total_conversations=20,
        questions_in_period=50,
        questions_change_percent=15.5,
    )

    with patch(
        "app.api.v1.dashboard.get_stats",
        new_callable=AsyncMock,
        return_value=mock_stats,
    ):
        response = await async_client.get(
            "/api/v1/dashboard/stats?period=30d",
            headers={"Authorization": "Bearer fake-token"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["total_users"] == 10
    assert data["active_users"] == 8
    assert data["questions_in_period"] == 50
    assert data["questions_change_percent"] == 15.5


@pytest.mark.asyncio
async def test_get_activity(async_client, override_admin):
    """Данные для графика активности — 200, получаем список точек по дням."""
    mock_activity = ActivityResponse(
        data=[
            ActivityItem(date="2025-01-01", questions=5),
            ActivityItem(date="2025-01-02", questions=3),
            ActivityItem(date="2025-01-03", questions=8),
        ]
    )

    with patch(
        "app.api.v1.dashboard.get_activity",
        new_callable=AsyncMock,
        return_value=mock_activity,
    ):
        response = await async_client.get(
            "/api/v1/dashboard/activity?period=7d",
            headers={"Authorization": "Bearer fake-token"},
        )

    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 3
    assert data["data"][0]["date"] == "2025-01-01"
    assert data["data"][2]["questions"] == 8


@pytest.mark.asyncio
async def test_get_top_questions(async_client, override_admin):
    """Топ вопросов — 200, видим самые популярные вопросы юзеров."""
    mock_top = TopQuestionsResponse(
        items=[
            TopQuestionItem(question="Как подключить VPN?", count=15),
            TopQuestionItem(question="Где документация?", count=10),
            TopQuestionItem(question="Как сбросить пароль?", count=7),
        ]
    )

    with patch(
        "app.api.v1.dashboard.get_top_questions",
        new_callable=AsyncMock,
        return_value=mock_top,
    ):
        response = await async_client.get(
            "/api/v1/dashboard/top-questions",
            headers={"Authorization": "Bearer fake-token"},
        )

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 3
    assert data["items"][0]["question"] == "Как подключить VPN?"
    assert data["items"][0]["count"] == 15


@pytest.mark.asyncio
async def test_dashboard_forbidden(async_client, override_user):
    """Обычный юзер лезет в дашборд — 403, аналитика только для админов."""
    response = await async_client.get(
        "/api/v1/dashboard/stats",
        headers={"Authorization": "Bearer fake-token"},
    )

    assert response.status_code == 403
