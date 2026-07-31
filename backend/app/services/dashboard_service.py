"""Сервис дашборда — считаем статистику, строим графики активности, топим за аналитику."""

from datetime import date, datetime, timedelta

from sqlalchemy import Date, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.conversation import Conversation
from app.models.document import Document
from app.models.message import Message
from app.models.user import User
from app.schemas.dashboard import (
    ActivityItem,
    ActivityResponse,
    StatsResponse,
    TopQuestionItem,
    TopQuestionsResponse,
)

logger = get_logger(__name__)


def _resolve_period_start(period: str) -> date:
    """Вычисляет начало периода по строковому ключу — today, 7d или 30d."""
    today = date.today()
    if period == "today":
        return today
    if period == "7d":
        return today - timedelta(days=6)
    # По дефолту — 30 дней, ну или если кто-то что-то странное передал
    return today - timedelta(days=29)


async def get_stats(db: AsyncSession, period: str = "30d") -> StatsResponse:
    """Собирает агрегированную статистику — юзеры, документы, разговоры и динамика вопросов."""
    # Подсчет пользователей — всех и активных
    total_users_q = await db.execute(select(func.count()).select_from(User))
    total_users = total_users_q.scalar_one()

    active_users_q = await db.execute(
        select(func.count()).select_from(User).where(User.is_active.is_(True))
    )
    active_users = active_users_q.scalar_one()

    # Подсчет документов — всего и проиндексированных
    total_documents_q = await db.execute(select(func.count()).select_from(Document))
    total_documents = total_documents_q.scalar_one()

    indexed_documents_q = await db.execute(
        select(func.count()).select_from(Document).where(Document.status == "indexed")
    )
    indexed_documents = indexed_documents_q.scalar_one()

    # Разговоры — только не удаленные
    total_conversations_q = await db.execute(
        select(func.count()).select_from(Conversation).where(Conversation.is_deleted.is_(False))
    )
    total_conversations = total_conversations_q.scalar_one()

    # Вопросы за текущий период
    period_start = _resolve_period_start(period)
    start_dt = datetime.combine(period_start, datetime.min.time())

    questions_q = await db.execute(
        select(func.count())
        .select_from(Message)
        .where(Message.role == "user", Message.created_at >= start_dt)
    )
    questions_in_period = questions_q.scalar_one()

    # Вопросы за предыдущий аналогичный период — для расчета процента изменений
    period_length = (date.today() - period_start).days + 1
    prev_start = period_start - timedelta(days=period_length)
    prev_end = period_start
    prev_start_dt = datetime.combine(prev_start, datetime.min.time())
    prev_end_dt = datetime.combine(prev_end, datetime.min.time())

    prev_questions_q = await db.execute(
        select(func.count())
        .select_from(Message)
        .where(
            Message.role == "user",
            Message.created_at >= prev_start_dt,
            Message.created_at < prev_end_dt,
        )
    )
    prev_questions = prev_questions_q.scalar_one()

    # Считаем процент изменений — если за прошлый период ноль, то None (делить на ноль не будем)
    questions_change_percent: float | None = None
    if prev_questions > 0:
        questions_change_percent = round(
            ((questions_in_period - prev_questions) / prev_questions) * 100, 1
        )

    logger.info("dashboard_stats_fetched", period=period, questions=questions_in_period)

    return StatsResponse(
        total_users=total_users,
        active_users=active_users,
        total_documents=total_documents,
        indexed_documents=indexed_documents,
        total_conversations=total_conversations,
        questions_in_period=questions_in_period,
        questions_change_percent=questions_change_percent,
    )


async def get_activity(db: AsyncSession, period: str = "30d") -> ActivityResponse:
    """Строит данные для графика активности — кол-во вопросов по дням, пустые дни заполняются нулями."""
    period_start = _resolve_period_start(period)
    start_dt = datetime.combine(period_start, datetime.min.time())

    # Группируем вопросы по дням
    message_date = cast(Message.created_at, Date)
    result = await db.execute(
        select(message_date.label("day"), func.count().label("cnt"))
        .where(Message.role == "user", Message.created_at >= start_dt)
        .group_by(message_date)
        .order_by(message_date)
    )
    rows = result.all()

    # Кидаем данные из БД в словарь — потом пройдемся по всем дням и заполним нулями пропуски
    data_map: dict[date, int] = {row.day: row.cnt for row in rows}

    today = date.today()
    items: list[ActivityItem] = []
    current_day = period_start
    while current_day <= today:
        items.append(
            ActivityItem(
                date=current_day.isoformat(),
                questions=data_map.get(current_day, 0),
            )
        )
        current_day += timedelta(days=1)

    logger.info("dashboard_activity_fetched", period=period, days=len(items))

    return ActivityResponse(data=items)


async def get_top_questions(db: AsyncSession) -> TopQuestionsResponse:
    """Топ-5 самых популярных вопросов — группируем по тексту, сортируем по частоте."""
    result = await db.execute(
        select(Message.content, func.count().label("cnt"))
        .where(Message.role == "user")
        .group_by(Message.content)
        .order_by(func.count().desc())
        .limit(5)
    )
    rows = result.all()

    items = [TopQuestionItem(question=row.content, count=row.cnt) for row in rows]

    logger.info("dashboard_top_questions_fetched", count=len(items))

    return TopQuestionsResponse(items=items)
