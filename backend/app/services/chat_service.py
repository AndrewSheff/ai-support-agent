"""Сервис чата — создание разговоров, отправка сообщений, вот это вот все."""

import asyncio
import math
from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import ForbiddenError, NotFoundError, ServiceUnavailableError
from app.core.logging import get_logger
from app.models.conversation import Conversation
from app.models.document import Document
from app.models.message import Message
from app.models.user import User
from app.schemas.chat import MessageResponse, SendMessageResponse
from app.services.rag.embeddings import generate_embedding
from app.services.rag.generator import build_prompt, generate_answer
from app.services.rag.retriever import search_similar_chunks

logger = get_logger(__name__)


async def create_conversation(
    db: AsyncSession,
    user: User,
    title: str | None = None,
) -> Conversation:
    """Создает новый разговор. Если title не задан — будет 'Новый разговор', ничего криминального."""
    conversation = Conversation(
        user_id=user.id,
        title=title or "Новый разговор",
    )
    db.add(conversation)
    await db.flush()
    await db.refresh(conversation)

    logger.info(
        "conversation_created",
        conversation_id=str(conversation.id),
        user_id=str(user.id),
    )

    return conversation


async def list_conversations(
    db: AsyncSession,
    user: User,
    search: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> dict:
    """Список разговоров юзера — с поиском, пагинацией и превью последнего сообщения. Короче, все как надо."""
    # Базовый фильтр — свои и не удаленные
    base_filter = (
        Conversation.user_id == user.id,
        Conversation.is_deleted.is_(False),
    )

    # Если ищем — добавляем ILIKE по title (экранируем LIKE-спецсимволы)
    if search:
        escaped_search = search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        base_filter = (*base_filter, Conversation.title.ilike(f"%{escaped_search}%"))

    # Считаем общее количество
    count_query = select(func.count()).select_from(Conversation).where(*base_filter)
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Считаем количество страниц
    pages = math.ceil(total / per_page) if total > 0 else 1

    # Получаем разговоры с сортировкой и пагинацией
    offset = (page - 1) * per_page
    conversations_query = (
        select(Conversation)
        .where(*base_filter)
        .order_by(desc(Conversation.updated_at))
        .offset(offset)
        .limit(per_page)
    )
    conversations_result = await db.execute(conversations_query)
    conversations = conversations_result.scalars().all()

    # Для каждого разговора подсчитываем message_count и last_message_preview
    items = []
    for conv in conversations:
        # Считаем сообщения
        msg_count_query = (
            select(func.count())
            .select_from(Message)
            .where(Message.conversation_id == conv.id)
        )
        msg_count_result = await db.execute(msg_count_query)
        message_count = msg_count_result.scalar_one()

        # Последнее сообщение ассистента — берем первые 100 символов для превью
        last_msg_query = (
            select(Message.content)
            .where(
                Message.conversation_id == conv.id,
                Message.role == "assistant",
            )
            .order_by(desc(Message.created_at))
            .limit(1)
        )
        last_msg_result = await db.execute(last_msg_query)
        last_msg_content = last_msg_result.scalar_one_or_none()

        last_message_preview = None
        if last_msg_content:
            last_message_preview = last_msg_content[:100]

        items.append({
            "id": conv.id,
            "title": conv.title,
            "created_at": conv.created_at,
            "updated_at": conv.updated_at,
            "message_count": message_count,
            "last_message_preview": last_message_preview,
        })

    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": pages,
    }


async def get_conversation(
    db: AsyncSession,
    conversation_id: UUID,
    user: User,
) -> dict:
    """Получает разговор со всеми сообщениями. Проверяет что юзер — владелец, а не просто мимо проходил."""
    # Загружаем разговор с сообщениями одним запросом
    query = (
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(Conversation.id == conversation_id)
    )
    result = await db.execute(query)
    conversation = result.scalar_one_or_none()

    # Не нашли или удален — 404
    if conversation is None or conversation.is_deleted:
        raise NotFoundError("Разговор не найден")

    # Чужой разговор — 403, руки прочь
    if conversation.user_id != user.id:
        raise ForbiddenError("Нет доступа к этому разговору")

    # Сортируем сообщения по дате создания
    sorted_messages = sorted(conversation.messages, key=lambda m: m.created_at)

    return {
        "id": conversation.id,
        "title": conversation.title,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
        "message_count": len(sorted_messages),
        "messages": sorted_messages,
    }


async def delete_conversation(
    db: AsyncSession,
    conversation_id: UUID,
    user: User,
) -> None:
    """Мягкое удаление разговора — ставим флаг is_deleted, данные не трогаем."""
    query = select(Conversation).where(Conversation.id == conversation_id)
    result = await db.execute(query)
    conversation = result.scalar_one_or_none()

    if conversation is None or conversation.is_deleted:
        raise NotFoundError("Разговор не найден")

    if conversation.user_id != user.id:
        raise ForbiddenError("Нет доступа к этому разговору")

    conversation.is_deleted = True
    await db.flush()

    logger.info(
        "conversation_deleted",
        conversation_id=str(conversation_id),
        user_id=str(user.id),
    )


async def send_message(
    db: AsyncSession,
    conversation_id: UUID,
    user: User,
    content: str,
    model: str,
) -> SendMessageResponse:
    """Отправка сообщения — полный RAG pipeline: embedding -> retriever -> generator."""
    # Проверяем что разговор существует и принадлежит юзеру
    query = (
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(Conversation.id == conversation_id)
    )
    result = await db.execute(query)
    conversation = result.scalar_one_or_none()

    if conversation is None or conversation.is_deleted:
        raise NotFoundError("Разговор не найден")

    if conversation.user_id != user.id:
        raise ForbiddenError("Нет доступа к этому разговору")

    # Проверяем есть ли вообще проиндексированные документы
    indexed_count_query = (
        select(func.count())
        .select_from(Document)
        .where(Document.status == "indexed")
    )
    indexed_result = await db.execute(indexed_count_query)
    indexed_count = indexed_result.scalar_one()

    if indexed_count == 0:
        raise ServiceUnavailableError(
            "No documents have been indexed yet. Please upload and process documents first."
        )

    # Сохраняем сообщение пользователя
    user_message = Message(
        conversation_id=conversation_id,
        role="user",
        content=content,
        model=None,
    )
    db.add(user_message)
    await db.flush()
    await db.refresh(user_message)

    # Получаем embedding вопроса в отдельном потоке — чтоб не блокировать event loop
    query_embedding = await asyncio.to_thread(generate_embedding, content)

    # Ищем похожие чанки в базе знаний
    relevant_chunks = await search_similar_chunks(db, query_embedding)

    # Берем историю разговора — последние 6 сообщений (3 пары user/assistant)
    sorted_messages = sorted(conversation.messages, key=lambda m: m.created_at)
    conversation_history = sorted_messages[-6:]

    # Собираем промпт для LLM
    llm_messages = build_prompt(relevant_chunks, conversation_history, content)

    # Генерируем ответ от AI
    assistant_content = await generate_answer(llm_messages, model)

    # Формируем sources — если чанки нашлись, собираем метаинфу
    sources = None
    if relevant_chunks:
        sources = [
            {
                "document_id": chunk["document_id"],
                "document_name": chunk["document_name"],
                "chunk_index": chunk["chunk_index"],
                "relevance_score": chunk["relevance_score"],
                "snippet": chunk["content"][:200],
            }
            for chunk in relevant_chunks
        ]

    # Сохраняем ответ ассистента с источниками
    assistant_message = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=assistant_content,
        model=model,
        sources=sources,
    )
    db.add(assistant_message)
    await db.flush()
    await db.refresh(assistant_message)

    # Обновляем title, если это первое сообщение — берем первые 50 символов
    is_first_message = len(conversation.messages) <= 2  # user + assistant только что добавленные
    if is_first_message and conversation.title == "Новый разговор":
        new_title = content[:50] + "..." if len(content) > 50 else content
        conversation.title = new_title

    # Обновляем updated_at — SQLAlchemy onupdate сделает это за нас при flush
    conversation.updated_at = func.now()
    await db.flush()
    await db.refresh(conversation)

    logger.info(
        "message_sent",
        conversation_id=str(conversation_id),
        user_id=str(user.id),
        model=model,
        chunks_found=len(relevant_chunks),
        has_sources=sources is not None,
    )

    return SendMessageResponse(
        user_message=MessageResponse.model_validate(user_message),
        assistant_message=MessageResponse.model_validate(assistant_message),
        conversation_title=conversation.title,
    )
