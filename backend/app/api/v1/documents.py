"""Роутер документов — загрузка, просмотр, удаление файлов базы знаний."""

from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import Response

from app.api.deps import require_admin
from app.core.rate_limit import upload_limit
from app.database import get_db
from app.models.user import User
from app.schemas.document import DocumentResponse, UploadedByInfo
from app.services.document_service import (
    delete_document,
    get_document,
    list_documents,
    upload_document,
)

router = APIRouter(prefix="/documents", tags=["Documents"])


def _to_response(doc) -> DocumentResponse:
    """Конвертим модель Document в DocumentResponse — подтягиваем uploaded_by_user в нужный формат."""
    return DocumentResponse(
        id=doc.id,
        original_name=doc.original_name,
        file_type=doc.file_type,
        file_size=doc.file_size,
        status=doc.status,
        page_count=doc.page_count,
        chunk_count=doc.chunk_count,
        uploaded_by=UploadedByInfo(
            id=doc.uploaded_by_user.id,
            name=doc.uploaded_by_user.name,
        ),
        error_message=doc.error_message,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )


@router.post("/", response_model=DocumentResponse, status_code=201)
@upload_limit
async def upload_document_endpoint(
    request: Request,
    file: UploadFile,
    background_tasks: BackgroundTasks,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> DocumentResponse:
    """Загрузка документа — принимает файл через multipart/form-data, возвращает инфу о созданном документе."""
    document = await upload_document(db, file, user, background_tasks)
    return _to_response(document)


@router.get("/")
async def list_documents_endpoint(
    status: str | None = None,
    page: int = 1,
    per_page: int = 20,
    _user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Список документов — с пагинацией и опциональным фильтром по статусу."""
    result = await list_documents(db, status=status, page=page, per_page=per_page)
    result["items"] = [_to_response(doc) for doc in result["items"]]
    return result


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document_endpoint(
    document_id: UUID,
    _user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> DocumentResponse:
    """Получение одного документа по id — со всеми подробностями."""
    document = await get_document(db, document_id)
    return _to_response(document)


@router.delete("/{document_id}", status_code=204)
async def delete_document_endpoint(
    document_id: UUID,
    _user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Удаление документа — прощай, файл, было приятно познакомиться."""
    await delete_document(db, document_id)
    return Response(status_code=204)
