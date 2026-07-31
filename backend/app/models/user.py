"""Модель пользователя — email, роль, статус, пароль."""

from sqlalchemy import Boolean, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class User(UUIDMixin, TimestampMixin, Base):
    """Зарегистрированный пользователь системы — admin или user."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="user", server_default="user")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    must_change_password: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")

    # Связи
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="uploaded_by_user")

    __table_args__ = (
        Index("ix_users_email", "email", unique=True),
        Index("ix_users_is_active", "is_active"),
    )
