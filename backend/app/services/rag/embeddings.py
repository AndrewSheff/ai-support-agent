"""Генерация эмбеддингов через OpenAI API — синхронный клиент с retry и батчингом."""

import time

from openai import OpenAI

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Ленивая инициализация клиента — чтоб не падало при импорте без ключа
_client: OpenAI | None = None


def _get_client() -> OpenAI:
    """Получает или создает OpenAI клиент — один раз и навсегда."""
    global _client  # noqa: PLW0603
    if _client is None:
        _client = OpenAI(api_key=settings.openai_api_key)
    return _client


# Модель для эмбеддингов — маленькая, быстрая, дешевая
_EMBEDDING_MODEL = "text-embedding-3-small"
_EMBEDDING_DIMENSIONS = 1536
_MAX_BATCH_SIZE = 100
_MAX_RETRIES = 3
_BACKOFF_DELAYS = [1, 2, 4]  # секунды между попытками


def generate_embedding(text: str) -> list[float]:
    """Генерирует эмбеддинг для одного текста — вызывает OpenAI API и возвращает вектор."""
    client = _get_client()
    response = client.embeddings.create(
        input=text,
        model=_EMBEDDING_MODEL,
        dimensions=_EMBEDDING_DIMENSIONS,
    )
    embedding = response.data[0].embedding
    logger.info("embedding_generated", text_length=len(text), dimensions=len(embedding))
    return embedding


def generate_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """Генерирует эмбеддинги для пачки текстов — с retry и автоматическим разбиением на батчи.

    Если текстов больше 100 — бьем на батчи по 100 штук.
    При ошибке делаем до 3 попыток с exponential backoff (1, 2, 4 сек).
    """
    if not texts:
        return []

    all_embeddings: list[list[float]] = []

    # Разбиваем на батчи по _MAX_BATCH_SIZE
    batches = [texts[i : i + _MAX_BATCH_SIZE] for i in range(0, len(texts), _MAX_BATCH_SIZE)]

    logger.info(
        "embeddings_batch_start",
        total_texts=len(texts),
        batch_count=len(batches),
    )

    for batch_index, batch in enumerate(batches):
        batch_embeddings = _process_single_batch(batch, batch_index)
        all_embeddings.extend(batch_embeddings)

    logger.info(
        "embeddings_batch_complete",
        total_texts=len(texts),
        total_embeddings=len(all_embeddings),
    )
    return all_embeddings


def _process_single_batch(batch: list[str], batch_index: int) -> list[list[float]]:
    """Обрабатывает один батч с retry — если OpenAI ругается, пробуем снова."""
    last_error: Exception | None = None

    for attempt in range(_MAX_RETRIES):
        try:
            client = _get_client()
            response = client.embeddings.create(
                input=batch,
                model=_EMBEDDING_MODEL,
                dimensions=_EMBEDDING_DIMENSIONS,
            )
            # Сортируем по index — OpenAI может вернуть в другом порядке (вряд ли, но мало ли)
            sorted_data = sorted(response.data, key=lambda x: x.index)
            embeddings = [item.embedding for item in sorted_data]

            logger.info(
                "batch_processed",
                batch_index=batch_index,
                batch_size=len(batch),
                attempt=attempt + 1,
            )
            return embeddings

        except Exception as exc:
            last_error = exc
            if attempt < _MAX_RETRIES - 1:
                delay = _BACKOFF_DELAYS[attempt]
                logger.warning(
                    "batch_retry",
                    batch_index=batch_index,
                    attempt=attempt + 1,
                    delay=delay,
                    error=str(exc),
                )
                time.sleep(delay)
            else:
                logger.error(
                    "batch_failed",
                    batch_index=batch_index,
                    attempts=_MAX_RETRIES,
                    error=str(exc),
                )

    # Если все попытки провалились — бросаем последнюю ошибку
    msg = f"Не удалось сгенерировать эмбеддинги для батча {batch_index} после {_MAX_RETRIES} попыток"
    raise RuntimeError(msg) from last_error
