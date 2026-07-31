"""Импорт всех моделей — нужно для Alembic autogenerate."""

from app.models.base import Base
from app.models.conversation import Conversation
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.message import Message
from app.models.user import User

__all__ = [
    "Base",
    "Conversation",
    "Document",
    "DocumentChunk",
    "Message",
    "User",
]
