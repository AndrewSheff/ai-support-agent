"""Схемы дашборда — статистика, активность, топ вопросов."""

from pydantic import BaseModel


class StatsResponse(BaseModel):
    """Общая статистика системы — юзеры, документы, разговоры, динамика."""

    total_users: int
    active_users: int
    total_documents: int
    indexed_documents: int
    total_conversations: int
    questions_in_period: int
    questions_change_percent: float | None = None


class ActivityItem(BaseModel):
    """Одна точка на графике активности — дата и кол-во вопросов."""

    date: str
    questions: int


class ActivityResponse(BaseModel):
    """Данные для графика активности — список точек по дням."""

    data: list[ActivityItem]


class TopQuestionItem(BaseModel):
    """Популярный вопрос — текст и сколько раз задавали."""

    question: str
    count: int


class TopQuestionsResponse(BaseModel):
    """Список самых популярных вопросов — для аналитики."""

    items: list[TopQuestionItem]
