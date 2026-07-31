"""Схемы авторизации — логин, токены, смена пароля."""

import re
from uuid import UUID

from pydantic import BaseModel, EmailStr, field_validator


class UserInfo(BaseModel):
    """Краткая инфа о пользователе — идет в ответе на логин."""

    id: UUID
    email: str
    name: str
    role: str
    must_change_password: bool


class LoginRequest(BaseModel):
    """Запрос на вход — email + пароль, ничего лишнего."""

    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_not_empty(cls, v: str) -> str:
        """Пустой пароль — это не пароль, извини."""
        if len(v) < 1:
            msg = "Пароль не может быть пустым"
            raise ValueError(msg)
        return v


class LoginResponse(BaseModel):
    """Ответ на успешный логин — токен и данные юзера."""

    access_token: str
    token_type: str
    user: UserInfo


class ChangePasswordRequest(BaseModel):
    """Запрос на смену пароля — текущий, новый и подтверждение."""

    current_password: str
    new_password: str
    confirm_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Пароль должен быть 8-128 символов, минимум одна буква и одна цифра."""
        pattern = r"^(?=.*[a-zA-Z])(?=.*\d).{8,128}$"
        if not re.match(pattern, v):
            msg = "Пароль должен содержать минимум 8 символов, хотя бы одну букву и одну цифру"
            raise ValueError(msg)
        return v

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        """Подтверждение должно совпадать с новым паролем, логично же."""
        if "new_password" in info.data and v != info.data["new_password"]:
            msg = "Пароли не совпадают"
            raise ValueError(msg)
        return v
