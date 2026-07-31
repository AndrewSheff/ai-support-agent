"""Модель документа — загруженный файл базы знаний."""

import uuid

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Document(UUIDMixin, TimestampMixin, Base):
    """Документ базы знаний — PDF, DOCX или TXT с метаданными обработки."""

    __tablename__ = "documents"

    filename: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(10), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="uploaded",
        server_default="uploaded",
    )
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chunk_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Связи
    uploaded_by_user = relationship("User", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("file_size > 0", name="ck_documents_file_size_positive"),
        CheckConstraint(
            "file_type IN ('pdf', 'docx', 'txt')",
            name="ck_documents_file_type_valid",
        ),
        CheckConstraint(
            "status IN ('uploaded', 'processing', 'indexed', 'error')",
            name="ck_documents_status_valid",
        ),
        Index("ix_documents_status", "status"),
        Index("ix_documents_uploaded_by", "uploaded_by"),
        Index("ix_documents_created_at", "created_at"),
    )
