"""Pydantic-схемы для валидации запросов и ответов API."""

from app.schemas.auth import ChangePasswordRequest, LoginRequest, LoginResponse, UserInfo
from app.schemas.chat import (
    ConversationCreate,
    ConversationListItem,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
    SendMessageResponse,
)
from app.schemas.common import PaginatedResponse
from app.schemas.dashboard import ActivityItem, ActivityResponse, StatsResponse, TopQuestionItem, TopQuestionsResponse
from app.schemas.document import DocumentResponse, UploadedByInfo
from app.schemas.user import UserCreate, UserResponse, UserUpdate, UserWithPasswordResponse

__all__ = [
    "ActivityItem",
    "ActivityResponse",
    "ChangePasswordRequest",
    "ConversationCreate",
    "ConversationListItem",
    "ConversationResponse",
    "DocumentResponse",
    "LoginRequest",
    "LoginResponse",
    "MessageCreate",
    "MessageResponse",
    "PaginatedResponse",
    "SendMessageResponse",
    "StatsResponse",
    "TopQuestionItem",
    "TopQuestionsResponse",
    "UploadedByInfo",
    "UserCreate",
    "UserInfo",
    "UserResponse",
    "UserUpdate",
    "UserWithPasswordResponse",
]
