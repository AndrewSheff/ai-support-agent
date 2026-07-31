"""Ретривер — ищет похожие чанки документов по эмбеддингу вопроса."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.document import Document
from app.models.document_chunk import DocumentChunk

logger = get_logger(__name__)


async def search_similar_chunks(
    db: AsyncSession,
    query_embedding: list[float],
    top_k: int = 5,
    threshold: float = 0.3,
) -> list[dict]:
    """
    Ищет чанки, похожие на вопрос пользователя.

    Берем top_k ближайших по cosine distance, потом фильтруем по порогу.
    Threshold = 0.3 означает similarity >= 0.3 (т.е. distance <= 0.7).
    """
    # Cosine distance — чем меньше, тем ближе
    cosine_dist = DocumentChunk.embedding.cosine_distance(query_embedding)

    query = (
        select(
            DocumentChunk.content,
            DocumentChunk.chunk_index,
            DocumentChunk.document_id,
            Document.original_name,
            cosine_dist.label("distance"),
        )
        .join(Document, DocumentChunk.document_id == Document.id)
        .where(Document.status == "indexed")
        .order_by(cosine_dist)
        .limit(top_k)
    )

    result = await db.execute(query)
    rows = result.all()

    # Отбрасываем чанки с distance > 0.7 (similarity < 0.3)
    max_distance = 1.0 - threshold
    relevant_chunks = []

    for row in rows:
        if row.distance > max_distance:
            continue

        relevant_chunks.append({
            "content": row.content,
            "document_name": row.original_name,
            "document_id": str(row.document_id),
            "chunk_index": row.chunk_index,
            "relevance_score": round(1 - row.distance, 4),
        })

    logger.info(
        "chunks_retrieved",
        total_found=len(rows),
        after_threshold=len(relevant_chunks),
        top_k=top_k,
        threshold=threshold,
    )

    return relevant_chunks
