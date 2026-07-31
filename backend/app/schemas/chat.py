"""Схемы чата — разговоры, сообщения, отправка."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ConversationCreate(BaseModel):
    """Создание нового разговора — можно задать заголовок, а можно и нет."""

    title: str | None = Field(default=None, max_length=200)


class MessageResponse(BaseModel):
    """Одно сообщение — от юзера или от ассистента."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: str
    content: str
    model: str | None = None
    sources: list | None = None
    created_at: datetime


class ConversationListItem(BaseModel):
    """Элемент списка разговоров — краткая инфа для превью."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    last_message_preview: str | None = None


class ConversationResponse(BaseModel):
    """Полный разговор — с историей сообщений."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    messages: list[MessageResponse]


class MessageCreate(BaseModel):
    """Создание сообщения — текст и выбор модели."""

    content: str = Field(min_length=1, max_length=4000)
    model: Literal["claude", "gpt"] = "claude"

    @field_validator("content")
    @classmethod
    def strip_content(cls, v: str) -> str:
        """Убираем пробелы по краям — мало ли кто пробелами балуется."""
        stripped = v.strip()
        if not stripped:
            msg = "Сообщение не может быть пустым"
            raise ValueError(msg)
        return stripped


class SendMessageResponse(BaseModel):
    """Ответ на отправку сообщения — оба сообщения и заголовок разговора."""

    user_message: MessageResponse
    assistant_message: MessageResponse
    conversation_title: str
