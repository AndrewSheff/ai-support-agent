"""Роутер чата — CRUD разговоров и отправка сообщений."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.chat import (
    ConversationCreate,
    ConversationListItem,
    ConversationResponse,
    MessageCreate,
    SendMessageResponse,
)
from app.schemas.common import PaginatedResponse
from app.services.chat_service import (
    create_conversation,
    delete_conversation,
    get_conversation,
    list_conversations,
    send_message,
)

router = APIRouter(prefix="/conversations", tags=["Chat"])


@router.post("/", response_model=ConversationResponse, status_code=201)
async def create_conversation_endpoint(
    body: ConversationCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Создание нового разговора — пустой, с заголовком или без."""
    conversation = await create_conversation(db, user, body.title)
    return {
        "id": conversation.id,
        "title": conversation.title,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
        "message_count": 0,
        "messages": [],
    }


@router.get("/", response_model=PaginatedResponse[ConversationListItem])
async def list_conversations_endpoint(
    search: str | None = Query(default=None, description="Поиск по заголовку разговора"),
    page: int = Query(default=1, ge=1, description="Номер страницы"),
    per_page: int = Query(default=20, ge=1, le=100, description="Элементов на странице"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Список разговоров текущего юзера — с поиском и пагинацией."""
    return await list_conversations(db, user, search, page, per_page)


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation_endpoint(
    conversation_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Получение полного разговора со всеми сообщениями."""
    return await get_conversation(db, conversation_id, user)


@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation_endpoint(
    conversation_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Мягкое удаление разговора — помечаем как удаленный, данные не трогаем."""
    await delete_conversation(db, conversation_id, user)


@router.post("/{conversation_id}/messages", response_model=SendMessageResponse)
async def send_message_endpoint(
    conversation_id: UUID,
    body: MessageCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SendMessageResponse:
    """Отправка сообщения в разговор — получаем ответ от ассистента (пока заглушка)."""
    return await send_message(db, conversation_id, user, body.content, body.model)
