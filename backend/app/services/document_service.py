"""Сервис документов — загрузка, получение, удаление файлов базы знаний."""

import math
import os
import uuid
from pathlib import Path

from fastapi import UploadFile
from fastapi.background import BackgroundTasks
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.config import settings
from app.core.exceptions import BadRequestError, ConflictError, NotFoundError
from app.core.logging import get_logger
from app.models.document import Document
from app.models.user import User
from app.tasks.document_tasks import process_document_task

logger = get_logger(__name__)

# Допустимые расширения и соответствующие MIME-типы
ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
}

# Пробуем импортнуть python-magic, если его нет — ну и ладно, обойдемся расширениями
try:
    import magic

    _magic_available = True
except ImportError:
    _magic_available = False
    logger.warning("python_magic_not_available", detail="Валидация MIME будет только по расширению")


def _get_file_extension(filename: str) -> str:
    """Вытаскивает расширение файла, в нижнем регистре, без точки."""
    return Path(filename).suffix.lstrip(".").lower()


def _validate_mime_type(file_content: bytes) -> str | None:
    """Проверяет MIME-тип файла через python-magic. Если magic нет — вернет None, и ок."""
    if not _magic_available:
        return None
    detected = magic.from_buffer(file_content, mime=True)
    return detected


async def upload_document(
    db: AsyncSession,
    file: UploadFile,
    user: User,
    background_tasks: BackgroundTasks,
) -> Document:
    """Загрузка документа — валидация, сохранение на диск, создание записи в БД."""
    if not file.filename:
        raise BadRequestError("Имя файла не указано")

    # Проверяем расширение
    extension = _get_file_extension(file.filename)
    if extension not in ALLOWED_EXTENSIONS:
        raise BadRequestError(
            f"Недопустимый тип файла '.{extension}'. Разрешены: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Читаем содержимое файла
    content = await file.read()
    file_size = len(content)

    # Проверяем размер
    if file_size == 0:
        raise BadRequestError("Файл пустой")
    if file_size > settings.max_file_size:
        max_mb = settings.max_file_size // (1024 * 1024)
        raise BadRequestError(f"Файл слишком большой. Максимальный размер: {max_mb}MB")

    # Проверяем MIME-тип через magic, если он доступен
    detected_mime = _validate_mime_type(content)
    if detected_mime is not None and detected_mime not in ALLOWED_MIME_TYPES:
        raise BadRequestError(
            f"MIME-тип файла '{detected_mime}' не соответствует допустимым форматам"
        )

    # Проверяем дубликат по original_name
    existing = await db.execute(
        select(Document).where(Document.original_name == file.filename)
    )
    if existing.scalar_one_or_none() is not None:
        raise ConflictError(f"Документ с именем '{file.filename}' уже существует")

    # Генерируем уникальное имя для хранения
    stored_filename = f"{uuid.uuid4()}.{extension}"

    # Создаем директорию для загрузок, если ее нет
    upload_path = Path(settings.upload_dir)
    upload_path.mkdir(parents=True, exist_ok=True)

    # Сохраняем файл на диск
    file_path = upload_path / stored_filename
    file_path.write_bytes(content)

    logger.info(
        "file_saved_to_disk",
        filename=stored_filename,
        original_name=file.filename,
        size=file_size,
    )

    # Создаем запись в БД
    document = Document(
        filename=stored_filename,
        original_name=file.filename,
        file_type=extension,
        file_size=file_size,
        status="uploaded",
        chunk_count=0,
        uploaded_by=user.id,
    )
    db.add(document)
    await db.flush()

    # Подгружаем связь с юзером, чтоб в ответе было имя загрузившего
    await db.refresh(document, attribute_names=["uploaded_by_user"])

    logger.info(
        "document_uploaded",
        document_id=str(document.id),
        original_name=file.filename,
        file_type=extension,
        file_size=file_size,
        user_id=str(user.id),
    )

    # Запускаем обработку документа в фоне — парсинг, чанкинг, эмбеддинги
    background_tasks.add_task(process_document_task, str(document.id))

    return document


async def list_documents(
    db: AsyncSession,
    status: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> dict:
    """Список документов с пагинацией и фильтром по статусу — ничего сложного."""
    # Базовый запрос
    query = select(Document).options(joinedload(Document.uploaded_by_user))

    # Фильтр по статусу (если передан)
    if status is not None:
        query = query.where(Document.status == status)

    # Считаем общее количество
    count_query = select(func.count()).select_from(Document)
    if status is not None:
        count_query = count_query.where(Document.status == status)
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Сортировка и пагинация
    offset = (page - 1) * per_page
    query = query.order_by(Document.created_at.desc()).offset(offset).limit(per_page)

    result = await db.execute(query)
    items = list(result.scalars().unique().all())

    pages = math.ceil(total / per_page) if per_page > 0 else 0

    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": pages,
    }


async def get_document(db: AsyncSession, doc_id: uuid.UUID) -> Document:
    """Получение одного документа по id — с подтянутым юзером. Если нет — 404."""
    result = await db.execute(
        select(Document)
        .options(joinedload(Document.uploaded_by_user))
        .where(Document.id == doc_id)
    )
    document = result.scalar_one_or_none()

    if document is None:
        raise NotFoundError(f"Документ {doc_id} не найден")

    return document


async def delete_document(db: AsyncSession, doc_id: uuid.UUID) -> None:
    """Удаление документа — из БД и с диска. Чанки удалятся каскадно, не переживай."""
    result = await db.execute(
        select(Document).where(Document.id == doc_id)
    )
    document = result.scalar_one_or_none()

    if document is None:
        raise NotFoundError(f"Документ {doc_id} не найден")

    # Удаляем файл с диска
    file_path = Path(settings.upload_dir) / document.filename
    if file_path.exists():
        os.remove(file_path)
        logger.info("file_deleted_from_disk", filename=document.filename)
    else:
        logger.warning(
            "file_not_found_on_disk",
            filename=document.filename,
            detail="Файл уже удален или никогда не существовал, ну и ладно",
        )

    # Удаляем запись из БД (CASCADE прибьет чанки)
    await db.delete(document)
    await db.flush()

    logger.info(
        "document_deleted",
        document_id=str(doc_id),
        original_name=document.original_name,
    )
