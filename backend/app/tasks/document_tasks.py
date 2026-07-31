"""Фоновые задачи обработки документов — полный RAG pipeline от файла до эмбеддингов."""

import asyncio
from pathlib import Path

from sqlalchemy import select

from app.config import settings
from app.core.logging import get_logger
from app.database import async_session
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.rag.embeddings import generate_embeddings_batch
from app.services.rag.processor import chunk_text, clean_text, parse_document

logger = get_logger(__name__)


async def process_document_task(document_id: str) -> None:
    """Полный pipeline обработки документа — парсинг, чанкинг, эмбеддинги, сохранение.

    Запускается как фоновая задача после загрузки файла.
    Сам создает сессию к БД — работает вне контекста запроса.
    """
    async with async_session() as db:
        try:
            # Грузим документ из базы
            result = await db.execute(
                select(Document).where(Document.id == document_id)
            )
            document = result.scalar_one_or_none()

            if document is None:
                logger.error("document_not_found", document_id=document_id)
                return

            # Ставим статус "processing" — пусть фронт знает, что мы работаем
            document.status = "processing"
            await db.commit()

            logger.info(
                "document_processing_started",
                document_id=document_id,
                filename=document.filename,
                file_type=document.file_type,
            )

            # Парсим файл — вытаскиваем текст
            filepath = str(Path(settings.upload_dir) / document.filename)
            raw_text = parse_document(filepath, document.file_type)

            # Чистим текст от мусора
            cleaned_text = clean_text(raw_text)

            # Режем на чанки
            chunks = chunk_text(cleaned_text)

            # Если текст пустой или слишком мелкий — ставим indexed и уходим
            if not chunks:
                document.status = "indexed"
                document.chunk_count = 0
                await db.commit()
                logger.info(
                    "document_indexed_empty",
                    document_id=document_id,
                    detail="Текст пустой или слишком короткий, чанков нет",
                )
                return

            # Генерим эмбеддинги — в отдельном потоке, т.к. клиент синхронный
            embeddings = await asyncio.to_thread(generate_embeddings_batch, chunks)

            # Создаем записи чанков в базе
            chunk_records = []
            for idx, (chunk_content, embedding) in enumerate(zip(chunks, embeddings, strict=True)):
                chunk_record = DocumentChunk(
                    document_id=document.id,
                    content=chunk_content,
                    chunk_index=idx,
                    embedding=embedding,
                    metadata_={"chunk_index": idx, "char_count": len(chunk_content)},
                )
                chunk_records.append(chunk_record)

            db.add_all(chunk_records)
            document.chunk_count = len(chunks)
            document.status = "indexed"
            await db.commit()

            logger.info(
                "document_processing_complete",
                document_id=document_id,
                chunk_count=len(chunks),
            )

        except Exception as exc:
            # Что-то пошло не так — ставим ошибку и логируем
            await db.rollback()

            try:
                result = await db.execute(
                    select(Document).where(Document.id == document_id)
                )
                document = result.scalar_one_or_none()
                if document is not None:
                    document.status = "error"
                    document.error_message = str(exc)
                    await db.commit()
            except Exception as commit_exc:
                logger.error(
                    "failed_to_set_error_status",
                    document_id=document_id,
                    error=str(commit_exc),
                )

            logger.error(
                "document_processing_failed",
                document_id=document_id,
                error=str(exc),
                exc_info=True,
            )
