"""Схемы пользователей — создание, обновление, ответы."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Создание нового пользователя — email, имя и роль."""

    email: EmailStr = Field(max_length=255)
    name: str = Field(min_length=2, max_length=100)
    role: Literal["admin", "user"] = "user"


class UserUpdate(BaseModel):
    """Частичное обновление пользователя — что передал, то и меняем."""

    name: str | None = Field(default=None, min_length=2, max_length=100)
    role: Literal["admin", "user"] | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    """Ответ с данными пользователя — без пароля, само собой."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    name: str
    role: str
    is_active: bool
    created_at: datetime


class UserWithPasswordResponse(UserResponse):
    """Ответ при создании юзера — с временным паролем, чтобы отдать админу."""

    temporary_password: str
