"""Роутер пользователей — CRUD для админов и обновление профиля для всех."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import Response

from app.api.deps import get_current_user, require_admin
from app.core.rate_limit import api_limit
from app.database import get_db
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.user import UserCreate, UserResponse, UserUpdate, UserWithPasswordResponse
from app.services.user_service import (
    create_user,
    delete_user,
    get_users,
    update_profile,
    update_user,
)

router = APIRouter(prefix="/users", tags=["Users"])


class ProfileUpdateRequest(BaseModel):
    """Запрос на обновление профиля — только имя, остальное не трогаем."""

    name: str = Field(min_length=2, max_length=100)


@router.get("/", response_model=PaginatedResponse[UserResponse])
@api_limit
async def list_users(
    request: Request,
    page: int = Query(default=1, ge=1, description="Номер страницы"),
    per_page: int = Query(default=20, ge=1, le=100, description="Записей на странице"),
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Получить список пользователей — только для админов, с пагинацией."""
    return await get_users(db, page, per_page)


@router.post("/", response_model=UserWithPasswordResponse, status_code=201)
@api_limit
async def create_user_endpoint(
    request: Request,
    body: UserCreate,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Создать нового пользователя — генерируем временный пароль, отдаем админу."""
    user, temp_password = await create_user(db, body)
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "temporary_password": temp_password,
    }


@router.patch("/me/profile", response_model=UserResponse)
@api_limit
async def update_my_profile(
    request: Request,
    body: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Обновить свой профиль — можно поменять только имя, и то ладно."""
    return await update_profile(db, current_user, body.name)


@router.patch("/{user_id}", response_model=UserResponse)
@api_limit
async def update_user_endpoint(
    request: Request,
    user_id: UUID,
    body: UserUpdate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Обновить пользователя — partial update, только для админов."""
    return await update_user(db, str(user_id), body, admin)


@router.delete("/{user_id}", status_code=204)
@api_limit
async def delete_user_endpoint(
    request: Request,
    user_id: UUID,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Удалить пользователя — насовсем, без возврата, только для админов."""
    await delete_user(db, str(user_id), admin)
    return Response(status_code=204)
