"""Модель разговора — диалог между пользователем и AI."""

import uuid

from sqlalchemy import Boolean, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Conversation(UUIDMixin, TimestampMixin, Base):
    """Единица диалога — содержит историю сообщений, поддерживает soft delete."""

    __tablename__ = "conversations"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        default="New Conversation",
        server_default="New Conversation",
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")

    # Связи
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_conversations_user_id", "user_id"),
        Index("ix_conversations_user_deleted", "user_id", "is_deleted"),
        Index("ix_conversations_updated_at", "updated_at"),
    )
