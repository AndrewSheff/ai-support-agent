"""Обработка документов — парсинг, очистка текста и нарезка на чанки для RAG."""

import re
import unicodedata

import tiktoken
from docx import Document as DocxDocument
from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError

from app.core.logging import get_logger

logger = get_logger(__name__)

# Загружаем токенайзер один раз — не будем каждый раз дергать
_encoding = tiktoken.get_encoding("cl100k_base")


def parse_document(filepath: str, file_type: str) -> str:
    """Диспатчер по типу файла — выбирает правильный парсер и запускает его."""
    parsers = {
        "pdf": parse_pdf,
        "docx": parse_docx,
        "txt": parse_txt,
    }
    parser = parsers.get(file_type)
    if parser is None:
        raise ValueError(f"Неподдерживаемый тип файла: {file_type}")

    logger.info("parsing_document", filepath=filepath, file_type=file_type)
    return parser(filepath)


def parse_pdf(filepath: str) -> str:
    """Вытаскивает текст из PDF через PyPDF2 — все страницы подряд."""
    try:
        reader = PdfReader(filepath)
    except PdfReadError as exc:
        raise ValueError(
            f"Не удалось прочитать PDF: файл поврежден или защищен паролем ({filepath})"
        ) from exc

    pages_text = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages_text.append(text)

    result = "\n\n".join(pages_text)
    logger.info("pdf_parsed", filepath=filepath, pages=len(reader.pages), chars=len(result))
    return result


def parse_docx(filepath: str) -> str:
    """Собирает текст из DOCX — все параграфы в одну строку через переносы."""
    doc = DocxDocument(filepath)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    result = "\n\n".join(paragraphs)
    logger.info("docx_parsed", filepath=filepath, paragraphs=len(paragraphs), chars=len(result))
    return result


def parse_txt(filepath: str) -> str:
    """Читает текстовый файл в UTF-8 — тут все просто."""
    with open(filepath, encoding="utf-8") as f:
        result = f.read()
    logger.info("txt_parsed", filepath=filepath, chars=len(result))
    return result


def clean_text(text: str) -> str:
    """Чистит текст от мусора — лишние пробелы, непечатные символы, нормализация Unicode."""
    # Нормализуем Unicode в NFC-форму
    text = unicodedata.normalize("NFC", text)

    # Убираем непечатные символы, но оставляем переносы строк
    text = re.sub(r"[^\S\n]+", " ", text)

    # Убираем управляющие символы кроме \n
    text = "".join(ch for ch in text if ch == "\n" or not unicodedata.category(ch).startswith("C"))

    # Убираем пустые строки (больше двух переносов подряд)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Обрезаем пробелы по краям
    text = text.strip()

    return text


def _count_tokens(text: str) -> int:
    """Считает количество токенов в тексте — обертка над tiktoken."""
    return len(_encoding.encode(text))


def _split_into_sentences(text: str) -> list[str]:
    """Разбивает текст на предложения — по точке/вопросу/восклицанию + пробел."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s for s in sentences if s.strip()]


def chunk_text(
    text: str,
    chunk_size: int = 512,
    overlap: int = 50,
) -> list[str]:
    """Разбивает текст на чанки с перекрытием — основа RAG-а, короче.

    Логика:
    1. Разбиваем на параграфы по двойному переносу
    2. Если параграф влезает в chunk_size — кладем как есть
    3. Если нет — дробим по предложениям
    4. Overlap токенов между чанками для сохранения контекста
    5. Слишком мелкие чанки (<50 токенов) выбрасываем
    """
    if not text or not text.strip():
        return []

    min_chunk_tokens = 50
    paragraphs = text.split("\n\n")

    # Собираем все сегменты (параграфы или предложения)
    segments: list[str] = []
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        if _count_tokens(paragraph) <= chunk_size:
            segments.append(paragraph)
        else:
            # Параграф слишком жирный — режем по предложениям
            sentences = _split_into_sentences(paragraph)
            segments.extend(sentences)

    if not segments:
        return []

    # Собираем чанки из сегментов с учетом overlap
    chunks: list[str] = []
    current_segments: list[str] = []
    current_tokens = 0

    for segment in segments:
        segment_tokens = _count_tokens(segment)

        if current_tokens + segment_tokens <= chunk_size:
            # Влезает — добавляем в текущий чанк
            current_segments.append(segment)
            current_tokens += segment_tokens
        else:
            # Не влезает — сохраняем текущий чанк и начинаем новый
            if current_segments:
                chunk_text_str = "\n\n".join(current_segments)
                chunks.append(chunk_text_str)

            # Вычисляем overlap — берем последние сегменты на overlap токенов
            overlap_segments: list[str] = []
            overlap_tokens = 0
            for seg in reversed(current_segments):
                seg_tok = _count_tokens(seg)
                if overlap_tokens + seg_tok > overlap:
                    break
                overlap_segments.insert(0, seg)
                overlap_tokens += seg_tok

            current_segments = [*overlap_segments, segment]
            current_tokens = overlap_tokens + segment_tokens

    # Не забываем последний чанк
    if current_segments:
        chunk_text_str = "\n\n".join(current_segments)
        chunks.append(chunk_text_str)

    # Фильтруем мелочевку — меньше min_chunk_tokens не берем
    chunks = [c for c in chunks if _count_tokens(c) >= min_chunk_tokens]

    logger.info("text_chunked", total_chunks=len(chunks), chunk_size=chunk_size, overlap=overlap)
    return chunks
