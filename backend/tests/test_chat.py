"""Тесты чата — создание разговоров, отправка сообщений, проверка доступа и прочее."""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.exceptions import ForbiddenError
from app.schemas.chat import MessageResponse, SendMessageResponse


@pytest.mark.asyncio
async def test_create_conversation(async_client, override_admin):
    """Создание нового разговора — получаем 201 с id и заголовком."""
    conversation = MagicMock()
    conversation.id = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    conversation.title = "Тестовый разговор"
    conversation.created_at = datetime(2025, 1, 1, tzinfo=UTC)
    conversation.updated_at = datetime(2025, 1, 1, tzinfo=UTC)

    with patch(
        "app.api.v1.chat.create_conversation",
        new_callable=AsyncMock,
        return_value=conversation,
    ):
        response = await async_client.post(
            "/api/v1/conversations/",
            json={"title": "Тестовый разговор"},
            headers={"Authorization": "Bearer fake-token"},
        )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Тестовый разговор"
    assert data["message_count"] == 0
    assert data["messages"] == []


@pytest.mark.asyncio
async def test_list_conversations(async_client, override_admin):
    """Список разговоров — получаем 200 с пагинацией, все на месте."""
    mock_result = {
        "items": [
            {
                "id": uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
                "title": "Разговор 1",
                "created_at": datetime(2025, 1, 1, tzinfo=UTC),
                "updated_at": datetime(2025, 1, 1, tzinfo=UTC),
                "message_count": 2,
                "last_message_preview": "Ответ от ассистента",
            }
        ],
        "total": 1,
        "page": 1,
        "per_page": 20,
        "pages": 1,
    }

    with patch(
        "app.api.v1.chat.list_conversations",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        response = await async_client.get(
            "/api/v1/conversations/",
            headers={"Authorization": "Bearer fake-token"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1


@pytest.mark.asyncio
async def test_get_conversation(async_client, override_admin):
    """Получение разговора по id — со всеми сообщениями, 200."""
    conversation_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    mock_result = {
        "id": uuid.UUID(conversation_id),
        "title": "Мой разговор",
        "created_at": datetime(2025, 1, 1, tzinfo=UTC),
        "updated_at": datetime(2025, 1, 1, tzinfo=UTC),
        "message_count": 0,
        "messages": [],
    }

    with patch(
        "app.api.v1.chat.get_conversation",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        response = await async_client.get(
            f"/api/v1/conversations/{conversation_id}",
            headers={"Authorization": "Bearer fake-token"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Мой разговор"


@pytest.mark.asyncio
async def test_delete_conversation(async_client, override_admin):
    """Удаление разговора — 204, мягкое удаление, данные не теряем."""
    conversation_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"

    with patch(
        "app.api.v1.chat.delete_conversation",
        new_callable=AsyncMock,
        return_value=None,
    ):
        response = await async_client.delete(
            f"/api/v1/conversations/{conversation_id}",
            headers={"Authorization": "Bearer fake-token"},
        )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_send_message(async_client, override_admin):
    """Отправка сообщения — получаем оба сообщения (user + assistant) и заголовок."""
    conversation_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"

    mock_response = SendMessageResponse(
        user_message=MessageResponse(
            id=uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
            role="user",
            content="Как дела?",
            model=None,
            sources=None,
            created_at=datetime(2025, 1, 1, tzinfo=UTC),
        ),
        assistant_message=MessageResponse(
            id=uuid.UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
            role="assistant",
            content="Все хорошо, спасибо!",
            model="claude",
            sources=None,
            created_at=datetime(2025, 1, 1, tzinfo=UTC),
        ),
        conversation_title="Как дела?",
    )

    with patch(
        "app.api.v1.chat.send_message",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        response = await async_client.post(
            f"/api/v1/conversations/{conversation_id}/messages",
            json={"content": "Как дела?", "model": "claude"},
            headers={"Authorization": "Bearer fake-token"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["user_message"]["content"] == "Как дела?"
    assert data["assistant_message"]["role"] == "assistant"
    assert data["conversation_title"] == "Как дела?"


@pytest.mark.asyncio
async def test_get_other_conversation_forbidden(async_client, override_admin):
    """Попытка залезть в чужой разговор — 403, не для тебя эта беседа."""
    conversation_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"

    with patch(
        "app.api.v1.chat.get_conversation",
        new_callable=AsyncMock,
        side_effect=ForbiddenError("Нет доступа к этому разговору"),
    ):
        response = await async_client.get(
            f"/api/v1/conversations/{conversation_id}",
            headers={"Authorization": "Bearer fake-token"},
        )

    assert response.status_code == 403
    assert "Нет доступа" in response.json()["detail"]
