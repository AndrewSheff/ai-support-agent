"""Начальная миграция — все таблицы, расширение pgvector и индексы.

Revision ID: 001
Revises: -
Create Date: 2026-07-31

"""

from collections.abc import Sequence

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

from alembic import op

# идентификаторы ревизии для Alembic
revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Создаем расширение pgvector, все таблицы и индексы."""
    # Расширение pgvector — нужно для хранения embedding-векторов
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # -- users --
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False, server_default="user"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("must_change_password", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_is_active", "users", ["is_active"])

    # -- conversations --
    op.create_table(
        "conversations",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(200), nullable=False, server_default="New Conversation"),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_conversations_user_id", "conversations", ["user_id"])
    op.create_index("ix_conversations_user_deleted", "conversations", ["user_id", "is_deleted"])
    op.create_index("ix_conversations_updated_at", "conversations", ["updated_at"])

    # -- messages --
    op.create_table(
        "messages",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("conversation_id", sa.UUID(), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("model", sa.String(50), nullable=True),
        sa.Column("sources", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_messages_conversation_id", "messages", ["conversation_id"])
    op.create_index("ix_messages_conv_created", "messages", ["conversation_id", "created_at"])

    # -- documents --
    op.create_table(
        "documents",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("original_name", sa.String(255), nullable=False),
        sa.Column("file_type", sa.String(10), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="uploaded"),
        sa.Column("page_count", sa.Integer(), nullable=True),
        sa.Column("chunk_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("uploaded_by", sa.UUID(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("filename"),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"]),
        sa.CheckConstraint("file_size > 0", name="ck_documents_file_size_positive"),
        sa.CheckConstraint(
            "file_type IN ('pdf', 'docx', 'txt')",
            name="ck_documents_file_type_valid",
        ),
        sa.CheckConstraint(
            "status IN ('uploaded', 'processing', 'indexed', 'error')",
            name="ck_documents_status_valid",
        ),
    )
    op.create_index("ix_documents_status", "documents", ["status"])
    op.create_index("ix_documents_uploaded_by", "documents", ["uploaded_by"])
    op.create_index("ix_documents_created_at", "documents", ["created_at"])

    # -- document_chunks --
    op.create_table(
        "document_chunks",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("document_id", sa.UUID(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("embedding", Vector(1536), nullable=False),
        sa.Column("metadata", sa.dialects.postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.CheckConstraint("chunk_index >= 0", name="ck_chunks_index_non_negative"),
    )
    op.create_index("ix_chunks_document_id", "document_chunks", ["document_id"])
    op.create_index(
        "ix_chunks_embedding_hnsw",
        "document_chunks",
        ["embedding"],
        postgresql_using="hnsw",
        postgresql_with={"m": 16, "ef_construction": 64},
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )


def downgrade() -> None:
    """Удаляем все таблицы в обратном порядке и расширение pgvector."""
    op.drop_table("document_chunks")
    op.drop_table("documents")
    op.drop_table("messages")
    op.drop_table("conversations")
    op.drop_table("users")
    op.execute("DROP EXTENSION IF EXISTS vector")
