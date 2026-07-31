"""Общие схемы — пагинация и прочая переиспользуемая мелочь."""

from pydantic import BaseModel


class PaginatedResponse[T](BaseModel):
    """Обертка для постраничных ответов — кидаешь список и мету, получаешь красоту."""

    items: list[T]
    total: int
    page: int
    per_page: int
    pages: int
