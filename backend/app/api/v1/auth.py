"""Роутер аутентификации — логин и смена пароля."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.api.deps import get_current_user
from app.core.rate_limit import login_limit
from app.database import get_db
from app.models.user import User
from app.schemas.auth import ChangePasswordRequest, LoginRequest, LoginResponse
from app.services.auth_service import authenticate, change_password

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResponse)
@login_limit
async def login(
    request: Request,
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    """Вход в систему — отдаем JWT-токен и данные юзера."""
    return await authenticate(db, body.email, body.password)


@router.post("/change-password")
async def change_password_endpoint(
    body: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Смена пароля — нужен текущий пароль и новый с подтверждением."""
    await change_password(
        db=db,
        user=user,
        current_password=body.current_password,
        new_password=body.new_password,
        confirm_password=body.confirm_password,
    )
    return {"message": "Пароль успешно изменен"}
