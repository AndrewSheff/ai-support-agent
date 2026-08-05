<!--
  BANNER: см. github_resume/DESIGN_SYSTEM.md — AI Support Agent
  Сохранить как assets/banner.png и раскомментировать:
-->
<!-- <img src="assets/banner.png" alt="AI Support Agent" width="100%"> -->

> **[English version](README_EN.md)**

<div align="center">

# AI Support Agent

### Корпоративный AI-ассистент с RAG и базой знаний

[![CI](https://github.com/AndrewSheff/ai-support-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/AndrewSheff/ai-support-agent/actions)
[![Python 3.13](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React 19](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-3178C6?logo=typescript&logoColor=white)](https://typescriptlang.org)
[![pgvector](https://img.shields.io/badge/pgvector-HNSW-4169E1?logo=postgresql&logoColor=white)](https://github.com/pgvector/pgvector)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Загрузите документы компании. Сотрудники задают вопросы. AI отвечает со ссылками на источники.**

[Быстрый старт](#быстрый-старт) · [Возможности](#возможности) · [Скриншоты](#скриншоты) · [Архитектура](#архитектура) · [API](#документация-api)

</div>

---

> **Проблема:** Сотрудники тратят 5-8 часов в неделю на поиск информации во внутренних документах. Новички адаптируются 2-4 недели. HR и юристы отвечают на одни и те же вопросы. Внутренние вики устаревают и им никто не доверяет.

**AI Support Agent** — self-hosted AI-ассистент, который отвечает на вопросы сотрудников на основе реальных документов компании. Загрузите политики, инструкции и руководства — система построит RAG pipeline с векторными эмбеддингами и будет давать точные ответы со ссылками на источники.

<div align="center">

| Строк кода | Endpoint'ов API | Моделей БД | Страниц | Тестов | Сервисов Docker |
|:---:|:---:|:---:|:---:|:---:|:---:|
| **9 500+** | **22** | **6 + pgvector** | **10** | **42** | **5** |

</div>

---

## Скриншоты

| AI-чат с источниками |
|:--------------------:|
| ![Chat](screenshots/chat.png) |

---

## Возможности

**AI-чат с источниками** — сотрудники задают вопросы на естественном языке. Система ищет релевантные фрагменты документов, формирует контекст и генерирует точные ответы с указанием конкретных источников.

**Управление документами** — загрузка PDF, DOCX, TXT файлов. Автоматическое извлечение текста, разбивка на чанки и генерация векторных эмбеддингов. Отслеживание статуса обработки в реальном времени.

**RAG Pipeline** — Retrieval-Augmented Generation: векторный поиск находит релевантные фрагменты, формируется контекстное окно с метаданными, LLM генерирует ответ на основе реальных документов.

**История разговоров** — сохраняет контекст чата в рамках сессии. Уточняющие вопросы понимают предыдущий контекст. Полный лог переписки для администраторов.

**Семантический поиск** — pgvector с HNSW-индексированием. Поиск по смыслу по всем документам. Ранжирование по косинусному сходству с оценками релевантности.

**Панель администратора** — количество документов, объем вопросов, средняя оценка релевантности. Мониторинг использования системы и покрытия документами.

**Несколько AI-провайдеров** — переключение между OpenAI GPT и Anthropic Claude. Настройка модели, temperature и системного промпта из панели администратора.

**Ролевой доступ** — роли User (только чат) и Admin (управление документами, настройки, аналитика). JWT-аутентификация с bcrypt.

**Корпоративная безопасность** — rate limiting, CORS, структурированное JSON-логирование, трассировка запросов. Self-hosted: ваши данные остаются на ваших серверах.

---

## Архитектура

```
┌──────────────────────────────────────────────────┐
│                    Nginx :80                      │
│           Обратный прокси + заголовки             │
├──────────────────┬───────────────────────────────┤
│  Frontend :3000  │        Backend :8000           │
│  React 19 + Vite │     FastAPI + Uvicorn          │
│  TailwindCSS v4  │     SQLAlchemy 2.0 (async)     │
│  Интерфейс чата  │   ┌────────────────────────┐   │
│  10 страниц      │   │     RAG Pipeline        │   │
│                  │   │  Загрузка→Чанки→Эмбед  │   │
│                  │   │  Поиск→Контекст→LLM    │   │
│                  │   └────────────────────────┘   │
├──────────────────┴───────────────────────────────┤
│   PostgreSQL 16 + pgvector       Redis 7          │
│   Векторный поиск (HNSW)         Rate Limiting    │
│   6 моделей, Alembic             Кеш сессий       │
└──────────────────────────────────────────────────┘
```

### RAG Flow

```
Пользователь задает вопрос
        |
        v
  [Генерация эмбеддинга вопроса]
        |
        v
  [pgvector: поиск top-K релевантных чанков]
        |
        v
  [Формирование контекстного окна с метаданными]
  [Название документа, номер страницы, текст чанка]
        |
        v
  [LLM генерирует ответ на основе контекста]
        |
        v
  [Возврат ответа + ссылки на источники]
```

---

## Быстрый старт

### Требования
- Docker & Docker Compose v2+
- OpenAI API key (обязателен для эмбеддингов)
- (Опционально) Anthropic API key для Claude

### 1. Клонирование и настройка

```bash
git clone https://github.com/AndrewSheff/ai-support-agent.git
cd ai-support-agent
cp .env.example .env
```

Отредактируйте `.env`:

```env
SECRET_KEY=your-random-32-char-string    # обязательно
ADMIN_PASSWORD=SecurePass123             # обязательно
OPENAI_API_KEY=sk-...                    # обязательно для эмбеддингов
ANTHROPIC_API_KEY=sk-ant-...             # опционально
```

### 2. Запуск

```bash
docker compose up -d
```

### 3. Доступ

| Сервис | URL |
|:--------|:----|
| Приложение | http://localhost |
| Документация API (Swagger) | http://localhost/docs |

Войдите с данными администратора. Загрузите документы, затем перейдите в чат и задавайте вопросы.

---

## Технологический стек

| Слой | Технология | Версия |
|:------|:-----------|:--------|
| **Backend** | Python, FastAPI, SQLAlchemy (async), Alembic | 3.13, 0.115, 2.0 |
| **Эмбеддинги** | OpenAI text-embedding-3-small, pgvector (HNSW) | 1536 dims |
| **Frontend** | React, TypeScript, Vite, TailwindCSS, shadcn/ui | 19, 5+, 6, v4 |
| **База данных** | PostgreSQL + pgvector | 16 |
| **Кеш** | Redis | 7 |
| **AI** | Anthropic Claude, OpenAI GPT | Latest |
| **Аутентификация** | JWT + bcrypt | HS256 |
| **Инфраструктура** | Docker Compose, Nginx, GitHub Actions CI/CD | Multi-stage |
| **Логирование** | structlog (JSON) | Трассировка запросов |
| **Тестирование** | Pytest (async) | 42 теста |

---

## Документация API

Интерактивный Swagger по адресу `/docs`. **22 endpoint'а** в 6 группах:

| Группа | Префикс | Endpoint'ы |
|:------|:-------|:----------|
| Аутентификация | `/api/v1/auth` | Регистрация, вход, профиль |
| Чат | `/api/v1/chat` | Задать вопрос, история переписки |
| Документы | `/api/v1/documents` | Загрузка, список, удаление, переобработка |
| Поиск | `/api/v1/search` | Семантический поиск по документам |
| Дашборд | `/api/v1/dashboard` | Статистика использования и аналитика |
| Здоровье | `/api/v1/health` | Проверка доступности |

---

## Структура проекта

```
ai-support-agent/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI приложение с lifespan
│   │   ├── config.py            # Настройки Pydantic
│   │   ├── database.py          # Async SQLAlchemy + pgvector
│   │   ├── api/v1/              # 6 REST API роутеров
│   │   ├── models/              # 6 SQLAlchemy моделей
│   │   ├── schemas/             # Pydantic v2 схемы
│   │   ├── services/            # RAG, embedding, AI, поиск
│   │   └── core/                # Безопасность, логирование
│   ├── tests/                   # 42 pytest теста
│   ├── alembic/                 # Миграции
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/                 # Axios клиенты
│   │   ├── components/          # Интерфейс чата + layout
│   │   ├── contexts/            # Auth контекст
│   │   ├── pages/               # 10 компонентов страниц
│   │   └── lib/                 # Утилиты
│   └── Dockerfile
├── docker/nginx/
├── .github/workflows/           # CI/CD
├── docker-compose.yml           # 5 сервисов
└── .env.example
```

---

## Переменные окружения

| Переменная | Обязательна | По умолчанию | Описание |
|:---------|:---------|:--------|:------------|
| `SECRET_KEY` | Да | -- | Ключ подписи JWT |
| `ADMIN_PASSWORD` | Да | -- | Пароль первого администратора |
| `OPENAI_API_KEY` | Да | -- | Для эмбеддингов + опциональный чат |
| `ANTHROPIC_API_KEY` | Нет | -- | Для Claude |
| `DATABASE_URL` | Нет | Авто | Подключение к PostgreSQL |
| `REDIS_URL` | Нет | Авто | Подключение к Redis |
| `LOG_LEVEL` | Нет | `INFO` | Уровень логирования |

---

## Разработка

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
docker compose up -d postgres redis
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && npm install && npm run dev

# Тесты
cd backend && pytest tests/ -v

# Линтер
ruff check backend/
cd frontend && npm run lint && npx tsc --noEmit
```

---

## Лицензия

[MIT](LICENSE) — свободно для коммерческого использования.
