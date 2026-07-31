"""Роутер дашборда — статистика, активность и топ вопросов для админов."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin
from app.database import get_db
from app.schemas.dashboard import ActivityResponse, StatsResponse, TopQuestionsResponse
from app.services.dashboard_service import get_activity, get_stats, get_top_questions

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=StatsResponse)
async def stats(
    period: str = Query("30d", pattern="^(today|7d|30d)$", description="Период: today, 7d или 30d"),
    _admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> StatsResponse:
    """Общая статистика системы — юзеры, документы, разговоры и динамика вопросов."""
    return await get_stats(db, period)


@router.get("/activity", response_model=ActivityResponse)
async def activity(
    period: str = Query("30d", pattern="^(7d|30d)$", description="Период: 7d или 30d"),
    _admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> ActivityResponse:
    """Данные для графика активности — вопросы по дням за выбранный период."""
    return await get_activity(db, period)


@router.get("/top-questions", response_model=TopQuestionsResponse)
async def top_questions(
    _admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> TopQuestionsResponse:
    """Топ-5 самых популярных вопросов — для понимания, что юзеров волнует больше всего."""
    return await get_top_questions(db)
