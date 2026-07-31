"""Схемы документов — загрузка, статус обработки, метаданные."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UploadedByInfo(BaseModel):
    """Кто загрузил документ — id и имя, без лишних подробностей."""

    id: UUID
    name: str


class DocumentResponse(BaseModel):
    """Полная информация о документе — статус, размер, кто загрузил и прочее."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    original_name: str
    file_type: str
    file_size: int
    status: str
    page_count: int | None = None
    chunk_count: int
    uploaded_by: UploadedByInfo
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime
