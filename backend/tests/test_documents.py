"""Тесты документов — загрузка, список, удаление и проверка прав доступа."""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.document import Document
from app.models.user import User


def _make_mock_document(admin_user):
    """Создает мок документа с привязанным юзером — чтоб не дублировать код."""
    doc = MagicMock(spec=Document)
    doc.id = uuid.UUID("dddddddd-dddd-dddd-dddd-dddddddddddd")
    doc.original_name = "test.pdf"
    doc.file_type = "pdf"
    doc.file_size = 1024
    doc.status = "uploaded"
    doc.page_count = 5
    doc.chunk_count = 10
    doc.error_message = None
    doc.created_at = datetime(2025, 1, 1, tzinfo=UTC)
    doc.updated_at = datetime(2025, 1, 1, tzinfo=UTC)

    # Подтягиваем uploaded_by_user — нужен для _to_response
    uploaded_by_user = MagicMock(spec=User)
    uploaded_by_user.id = admin_user.id
    uploaded_by_user.name = admin_user.name
    doc.uploaded_by_user = uploaded_by_user

    return doc


@pytest.mark.asyncio
async def test_upload_document(async_client, override_admin, admin_user):
    """Загрузка документа — multipart, получаем 201 с инфой о документе."""
    mock_doc = _make_mock_document(admin_user)

    with patch(
        "app.api.v1.documents.upload_document",
        new_callable=AsyncMock,
        return_value=mock_doc,
    ):
        response = await async_client.post(
            "/api/v1/documents/",
            files={"file": ("test.pdf", b"fake-pdf-content", "application/pdf")},
            headers={"Authorization": "Bearer fake-token"},
        )

    assert response.status_code == 201
    data = response.json()
    assert data["original_name"] == "test.pdf"
    assert data["file_type"] == "pdf"
    assert data["status"] == "uploaded"


@pytest.mark.asyncio
async def test_list_documents(async_client, override_admin, admin_user):
    """Список документов — 200, с пагинацией, документы на месте."""
    mock_doc = _make_mock_document(admin_user)
    mock_result = {
        "items": [mock_doc],
        "total": 1,
        "page": 1,
        "per_page": 20,
        "pages": 1,
    }

    with patch(
        "app.api.v1.documents.list_documents",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        response = await async_client.get(
            "/api/v1/documents/",
            headers={"Authorization": "Bearer fake-token"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["original_name"] == "test.pdf"


@pytest.mark.asyncio
async def test_delete_document(async_client, override_admin):
    """Удаление документа — 204, прощай файл, было приятно."""
    doc_id = "dddddddd-dddd-dddd-dddd-dddddddddddd"

    with patch(
        "app.api.v1.documents.delete_document",
        new_callable=AsyncMock,
        return_value=None,
    ):
        response = await async_client.delete(
            f"/api/v1/documents/{doc_id}",
            headers={"Authorization": "Bearer fake-token"},
        )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_upload_forbidden_user(async_client, override_user):
    """Обычный юзер пытается загрузить документ — 403, только для админов."""
    response = await async_client.post(
        "/api/v1/documents/",
        files={"file": ("test.pdf", b"fake-pdf-content", "application/pdf")},
        headers={"Authorization": "Bearer fake-token"},
    )

    assert response.status_code == 403
