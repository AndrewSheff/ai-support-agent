"""Юнит-тесты утилит — RAG-процессор, пароли, хеширование, JWT-токены."""

import re

import pytest

from app.core.security import (
    create_access_token,
    generate_temporary_password,
    hash_password,
    validate_password,
    verify_password,
    verify_token,
)
from app.services.rag.processor import chunk_text, clean_text

# --- Тесты clean_text ---


def test_clean_text():
    """Очистка текста — убираем мусор, оставляем суть."""
    dirty_text = "  Hello   World  \n\n\n\n  Test  \x00\x01  "
    result = clean_text(dirty_text)

    # Лишние пробелы и пустые строки должны схлопнуться
    assert "  " not in result or result.count("  ") == 0
    # Управляющие символы убиты
    assert "\x00" not in result
    assert "\x01" not in result
    # Начало и конец без пробелов
    assert result == result.strip()


def test_clean_text_preserves_newlines():
    """Очистка текста сохраняет нормальные переносы строк — не выкидывает все подряд."""
    text = "Line 1\n\nLine 2\n\nLine 3"
    result = clean_text(text)
    assert "\n" in result


def test_clean_text_empty():
    """Пустая строка — ну, пустая и есть, без сюрпризов."""
    assert clean_text("") == ""
    assert clean_text("   ") == ""


# --- Тесты chunk_text ---


def test_chunk_text():
    """Разбиение текста на чанки — проверяем что все чанки непустые и в разумных пределах."""
    # Создаем текст побольше — чтоб точно разбился на несколько чанков
    paragraphs = []
    for i in range(20):
        paragraphs.append(
            f"Paragraph {i}. " + "This is a sentence with enough words to contribute tokens. " * 10
        )
    text = "\n\n".join(paragraphs)

    chunks = chunk_text(text, chunk_size=200, overlap=30)

    # Чанки должны быть
    assert len(chunks) > 1
    # Каждый чанк — непустая строка
    for chunk in chunks:
        assert len(chunk.strip()) > 0


def test_chunk_text_empty():
    """Пустой текст — пустой список чанков, логично."""
    assert chunk_text("") == []
    assert chunk_text("   ") == []
    assert chunk_text("\n\n\n") == []


def test_chunk_text_small():
    """Маленький текст — если меньше min_chunk_tokens (50), чанков вообще не будет."""
    tiny_text = "Short text."
    chunks = chunk_text(tiny_text, chunk_size=512)
    # Слишком маленький — отфильтруется по min_chunk_tokens
    assert len(chunks) == 0


# --- Тесты validate_password ---


def test_validate_password():
    """Корректный пароль — буквы + цифры, 8+ символов, все ок."""
    assert validate_password("Password1") is True
    assert validate_password("abc12345") is True
    assert validate_password("SuperSecure123") is True
    assert validate_password("a1b2c3d4") is True


def test_validate_password_weak():
    """Слабые пароли — короткие, без букв или без цифр, не пройдут."""
    # Слишком короткий
    assert validate_password("Ab1") is False
    # Без цифр
    assert validate_password("abcdefgh") is False
    # Без букв
    assert validate_password("12345678") is False
    # Пустой
    assert validate_password("") is False


# --- Тесты generate_temporary_password ---


def test_generate_temporary_password():
    """Временный пароль — 8 символов, есть буквы и цифры, готов к использованию."""
    password = generate_temporary_password()

    assert len(password) == 8
    assert re.search(r"[a-zA-Z]", password) is not None
    assert re.search(r"\d", password) is not None


def test_generate_temporary_password_uniqueness():
    """Каждый раз генерируем разные пароли — не хотим одинаковых."""
    passwords = {generate_temporary_password() for _ in range(10)}
    # С вероятностью ~100% все 10 будут разными
    assert len(passwords) > 5


# --- Тесты hash_password + verify_password ---


def test_hash_verify_password():
    """Хеширование и проверка — хешируем, потом верифицируем, должно совпасть."""
    password = "TestPassword123"
    hashed = hash_password(password)

    # Хеш не равен паролю в открытом виде
    assert hashed != password
    # Но верификация проходит
    assert verify_password(password, hashed) is True
    # А с неправильным паролем — нет
    assert verify_password("WrongPassword", hashed) is False


def test_hash_password_different_hashes():
    """Один пароль — разные хеши (bcrypt с солью), так и должно быть."""
    password = "TestPassword123"
    hash1 = hash_password(password)
    hash2 = hash_password(password)
    # Хеши разные из-за соли
    assert hash1 != hash2
    # Но оба валидные
    assert verify_password(password, hash1) is True
    assert verify_password(password, hash2) is True


# --- Тесты JWT (create + verify) ---


def test_create_verify_token():
    """Создание и проверка JWT — данные должны пережить round-trip."""
    token_data = {
        "sub": "test-user-id",
        "email": "test@example.com",
        "role": "admin",
    }
    token = create_access_token(token_data)

    # Токен — непустая строка
    assert isinstance(token, str)
    assert len(token) > 0

    # Декодируем и проверяем данные
    payload = verify_token(token)
    assert payload["sub"] == "test-user-id"
    assert payload["email"] == "test@example.com"
    assert payload["role"] == "admin"
    # Должны быть служебные поля
    assert "exp" in payload
    assert "iat" in payload


def test_verify_token_invalid():
    """Невалидный токен — verify_token кидает JWTError, что и требовалось."""
    from jose import JWTError

    with pytest.raises(JWTError):
        verify_token("this.is.not.a.valid.token")
