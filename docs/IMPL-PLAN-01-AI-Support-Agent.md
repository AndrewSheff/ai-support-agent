# Implementation Plan: AI Support Agent

**Версия**: 1.0
**Дата**: 2026-07-31
**Основание**: PRD-01 v2.0, TDD-01 v1.0
**Общее количество задач**: 45
**Оценочное время**: ~95 часов

---

## Фаза 1: Инфраструктура и основа проекта

---

### TASK-01: Инициализация репозитория и структура проекта

**Описание**: Создать структуру директорий для всего проекта согласно TDD. Инициализировать backend (Python project) и frontend (Vite + React + TypeScript). Создать `.gitignore`, `LICENSE` (MIT), `.env.example` с заглушками, базовые конфигурационные файлы.

**Зависимости**: нет

**Критерии готовности**:
- Структура директорий backend/ и frontend/ создана по TDD
- `backend/requirements.txt` содержит все зависимости с зафиксированными версиями
- `backend/requirements-dev.txt` содержит pytest, httpx, pytest-asyncio
- `frontend/package.json` создан через Vite scaffolding (React + TypeScript)
- Все npm-зависимости из TDD установлены (axios, react-router-dom, @tanstack/react-query, tailwindcss, lucide-react, recharts, react-markdown, remark-gfm, sonner, date-fns, clsx, tailwind-merge)
- shadcn/ui инициализирован, базовые компоненты добавлены (Button, Input, Card, Table, Select, Dialog, AlertDialog, Tabs, Toggle, Progress, Textarea, Badge, Alert, Pagination, Skeleton, Tooltip)
- TailwindCSS настроен с globals.css
- `.gitignore` покрывает: `__pycache__`, `.env`, `node_modules`, `dist`, `uploads/`, `*.pyc`, `.venv`
- `LICENSE` — MIT
- `.env.example` создан со всеми переменными из PRD/TDD

**Время**: ~2 часа

---

### TASK-02: Docker-инфраструктура

**Описание**: Создать Dockerfiles для backend и frontend (multi-stage builds), docker-compose.yml со всеми сервисами (backend, frontend, postgres, redis, nginx), nginx.conf с проксированием и security headers.

**Зависимости**: TASK-01

**Критерии готовности**:
- `backend/Dockerfile`: multi-stage build (builder + runtime), non-root user `appuser`, HEALTHCHECK инструкция, конкретные версии базовых образов (python:3.13-slim)
- `frontend/Dockerfile`: multi-stage build (node:20-alpine для build, nginx:alpine для serve), конкретные версии
- `docker-compose.yml`: 5 сервисов (backend, frontend, postgres, redis, nginx), depends_on с healthcheck, volumes (postgres_data, redis_data, uploads), единая сеть `app-network`, restart policy, resource limits
- `docker/nginx/nginx.conf`: проксирование `/*` → frontend, `/api/*` → backend:8000, `/docs` → backend:8000, SPA fallback (try_files), security headers (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, Referrer-Policy, CSP)
- `backend/entrypoint.sh`: `alembic upgrade head` + `uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1`
- `.dockerignore` для backend и frontend
- `docker-compose up -d` запускает все сервисы без ошибок (postgres и redis стартуют, nginx обслуживает)

**Время**: ~2.5 часа

---

### TASK-03: Конфигурация бэкенда и подключение к БД

**Описание**: Реализовать `config.py` (Pydantic Settings), `database.py` (SQLAlchemy async engine + session), `main.py` (FastAPI app с lifespan, CORS middleware), структурированное логирование (structlog).

**Зависимости**: TASK-01

**Критерии готовности**:
- `app/config.py`: класс Settings на базе pydantic-settings, чтение всех переменных из .env (DATABASE_URL, REDIS_URL, SECRET_KEY, CORS_ORIGINS, ANTHROPIC_API_KEY, OPENAI_API_KEY, ADMIN_EMAIL, ADMIN_NAME, ADMIN_DEFAULT_PASSWORD, ACCESS_TOKEN_EXPIRE_MINUTES=30, LOG_LEVEL=INFO, UPLOAD_DIR=uploads, MAX_FILE_SIZE=52428800)
- `app/database.py`: create_async_engine с asyncpg, async_sessionmaker(expire_on_commit=False), async generator `get_db()` с yield session
- `app/main.py`: FastAPI app с title, version, openapi_url="/openapi.json", docs_url="/docs"; lifespan context manager; CORSMiddleware с настройками из config
- `app/core/logging.py`: structlog JSON processor, request_id context variable, настройка по LOG_LEVEL
- Middleware для request_id: генерация UUID4 для каждого запроса, добавление в structlog context, response header X-Request-ID
- Middleware для логирования: method, path, status, duration_ms, user_id, ip
- Приложение запускается без ошибок: `uvicorn app.main:app`

**Время**: ~2 часа

---

## Фаза 2: Модели данных и миграции

---

### TASK-04: SQLAlchemy модели

**Описание**: Создать все ORM-модели: User, Conversation, Message, Document, DocumentChunk. Базовый класс с общими полями. Event listener для updated_at.

**Зависимости**: TASK-03

**Критерии готовности**:
- `app/models/base.py`: DeclarativeBase с полями id (UUID, gen_random_uuid), created_at (TIMESTAMPTZ, server_default=now()), updated_at (TIMESTAMPTZ, server_default=now(), onupdate) через event listener before_flush
- `app/models/user.py`: email (VARCHAR 255, UNIQUE), name (VARCHAR 100), password_hash (VARCHAR 255), role (VARCHAR 20, CHECK admin/user, default user), is_active (BOOLEAN, default true), must_change_password (BOOLEAN, default false); relationship: conversations, documents
- `app/models/conversation.py`: user_id (FK → users CASCADE), title (VARCHAR 200, default 'New Conversation'), is_deleted (BOOLEAN, default false); relationship: messages, user; индексы: user_id, (user_id + is_deleted), updated_at DESC
- `app/models/message.py`: conversation_id (FK → conversations CASCADE), role (VARCHAR 20, CHECK user/assistant), content (TEXT), model (VARCHAR 50, nullable), sources (JSONB, nullable); индексы: conversation_id, (conversation_id + created_at)
- `app/models/document.py`: filename (VARCHAR 255, UNIQUE), original_name (VARCHAR 255), file_type (VARCHAR 10, CHECK pdf/docx/txt), file_size (INTEGER, CHECK >0), status (VARCHAR 20, CHECK uploaded/processing/indexed/error, default uploaded), page_count (INTEGER, nullable), chunk_count (INTEGER, default 0), uploaded_by (FK → users), error_message (TEXT, nullable); индексы: status, uploaded_by, created_at DESC
- `app/models/document_chunk.py`: document_id (FK → documents CASCADE), content (TEXT), chunk_index (INTEGER, CHECK >=0), embedding (VECTOR(1536)), metadata (JSONB, default {}); индексы: document_id, HNSW на embedding (vector_cosine_ops, m=16, ef_construction=64)
- `app/models/__init__.py`: импорт всех моделей (для Alembic autogenerate)

**Время**: ~2.5 часа

---

### TASK-05: Alembic миграции

**Описание**: Настроить Alembic в async-режиме, создать начальную миграцию с pgvector extension и всеми таблицами.

**Зависимости**: TASK-04

**Критерии готовности**:
- `alembic.ini`: настроен с async driver
- `alembic/env.py`: async migration context, импорт target_metadata из моделей
- `alembic/versions/001_initial.py`: `CREATE EXTENSION IF NOT EXISTS vector`, создание всех 5 таблиц со всеми индексами и ограничениями
- Миграция применяется без ошибок: `alembic upgrade head`
- Миграция идемпотентна (повторный запуск не падает)

**Время**: ~1.5 часа

---

### TASK-06: Pydantic-схемы

**Описание**: Создать все Pydantic v2 схемы для request/response валидации и сериализации.

**Зависимости**: TASK-04

**Критерии готовности**:
- `app/schemas/common.py`: PaginatedResponse (generic, T), содержит items, total, page, per_page, pages
- `app/schemas/auth.py`: LoginRequest (email: EmailStr, password: str min 1), LoginResponse (access_token, token_type, user: UserResponse), ChangePasswordRequest (current_password, new_password, confirm_password — валидация regex, match)
- `app/schemas/user.py`: UserCreate (email: EmailStr max 255, name: str 2-100, role: Literal["admin","user"] default "user"), UserUpdate (name?: str, role?: str, is_active?: bool), UserResponse (id, email, name, role, is_active, created_at), UserWithPasswordResponse (inherits UserResponse + temporary_password)
- `app/schemas/chat.py`: ConversationCreate (title?: str max 200), ConversationListItem (id, title, created_at, updated_at, message_count, last_message_preview), ConversationResponse (id, title, created_at, updated_at, message_count, messages: list[MessageResponse]), MessageCreate (content: str 1-4000 trimmed, model: Literal["claude","gpt"] default "claude"), MessageResponse (id, role, content, model, sources, created_at), SendMessageResponse (user_message, assistant_message, conversation_title)
- `app/schemas/document.py`: DocumentResponse (id, original_name, file_type, file_size, status, page_count, chunk_count, uploaded_by: {id, name}, error_message, created_at, updated_at)
- `app/schemas/dashboard.py`: StatsResponse (total_users, active_users, total_documents, indexed_documents, total_conversations, questions_in_period, questions_change_percent: float?), ActivityItem (date: str, questions: int), ActivityResponse (data: list[ActivityItem]), TopQuestionItem (question: str, count: int), TopQuestionsResponse (items: list[TopQuestionItem])
- Все схемы используют `model_config = ConfigDict(from_attributes=True)` где нужно

**Время**: ~2 часа

---

## Фаза 3: Core-модули бэкенда

---

### TASK-07: Модуль безопасности (JWT + bcrypt)

**Описание**: Реализовать security.py — создание и верификация JWT токенов, хеширование и проверка паролей, генерация временных паролей.

**Зависимости**: TASK-03

**Критерии готовности**:
- `app/core/security.py`:
  - `create_access_token(data: dict) → str`: создает JWT с payload (sub=user_id, email, role, exp, iat), алгоритм HS256, SECRET_KEY из config, время жизни ACCESS_TOKEN_EXPIRE_MINUTES
  - `verify_token(token: str) → dict`: декодирует JWT, проверяет exp, возвращает payload; при ошибке — raises exception
  - `hash_password(password: str) → str`: bcrypt хеширование через passlib CryptContext
  - `verify_password(plain: str, hashed: str) → bool`: проверка пароля
  - `generate_temporary_password() → str`: 8 символов [a-zA-Z0-9], гарантия мин 1 буква + 1 цифра
  - `validate_password(password: str) → bool`: regex `^(?=.*[a-zA-Z])(?=.*\d).{8,128}$`
- Все функции покрыты docstrings

**Время**: ~1.5 часа

---

### TASK-08: Обработка ошибок и кастомные исключения

**Описание**: Создать кастомные исключения и FastAPI exception handlers для единого формата ошибок.

**Зависимости**: TASK-03

**Критерии готовности**:
- `app/core/exceptions.py`:
  - Классы: `AppException(status_code, detail)`, `NotFoundError(detail)` → 404, `ForbiddenError(detail)` → 403, `ConflictError(detail)` → 409, `BadRequestError(detail)` → 400, `ServiceUnavailableError(detail)` → 503
  - FastAPI exception handlers, зарегистрированные в main.py
  - Формат ответа: `{"detail": "message"}`
  - Handler для RequestValidationError (422): преобразование в стандартный формат
  - Handler для непредвиденных ошибок (500): логирование traceback, возврат `{"detail": "Internal server error"}`

**Время**: ~1 час

---

### TASK-09: Dependencies (DI)

**Описание**: Реализовать FastAPI-зависимости для аутентификации и авторизации.

**Зависимости**: TASK-07, TASK-04

**Критерии готовности**:
- `app/api/deps.py`:
  - `get_db()`: async generator, yield AsyncSession
  - `get_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_db)) → User`: извлечь Bearer token, verify_token, SELECT user WHERE id AND is_active=true, 401 при ошибке
  - `require_admin(user = Depends(get_current_user)) → User`: проверка role == "admin", 403 при нарушении
  - OAuth2 scheme: `OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")`
- При невалидном/expired токене — ответ 401 с `{"detail": "Not authenticated"}`
- При отсутствии заголовка Authorization — 401
- При is_active=false — 401

**Время**: ~1.5 часа

---

### TASK-10: Rate Limiting

**Описание**: Настроить slowapi с Redis backend для ограничения частоты запросов.

**Зависимости**: TASK-03

**Критерии готовности**:
- slowapi интегрирован в main.py
- Redis используется как backend для хранения счетчиков
- Лимиты:
  - Login: 10 req/min per IP
  - API (authenticated): 60 req/min per user (по user_id из JWT)
  - Document upload: 10 req/min per user
- При превышении: HTTP 429 `{"detail": "Too many requests. Please try again later."}`
- При недоступности Redis: лимиты не применяются (graceful degradation), логируется warning

**Время**: ~1.5 часа

---

## Фаза 4: Бэкенд — сервисы и API

---

### TASK-11: Auth Service + Auth Router

**Описание**: Реализовать сервис аутентификации и API-эндпоинты: login, change-password, создание initial admin при первом запуске.

**Зависимости**: TASK-07, TASK-08, TASK-09, TASK-06, TASK-05

**Критерии готовности**:
- `app/services/auth_service.py`:
  - `authenticate(db, email, password)`: lowercase email, trim, SELECT user, verify_password, проверка is_active; возвращает User или raises 401/403
  - `change_password(db, user, current_pw, new_pw, confirm_pw)`: проверка текущего пароля, валидация нового (regex, не совпадает с текущим, пароли совпадают), хеширование, обновление, must_change_password=false
  - `create_initial_admin(db)`: вызывается в lifespan; если users пуста — создает admin из ADMIN_EMAIL/ADMIN_NAME/ADMIN_DEFAULT_PASSWORD с must_change_password=true
- `app/api/v1/auth.py`:
  - `POST /login`: LoginRequest → LoginResponse (access_token, token_type, user)
  - `POST /change-password`: auth required, ChangePasswordRequest → 200 message
- Router зарегистрирован в v1_router с prefix="/auth", tags=["Auth"]
- Все ошибки возвращаются в едином формате
- При старте приложения с пустой БД — admin создается автоматически

**Время**: ~2.5 часа

---

### TASK-12: User Service + User Router

**Описание**: Реализовать CRUD-сервис пользователей и API-эндпоинты: список, создание, обновление, удаление, обновление профиля.

**Зависимости**: TASK-11

**Критерии готовности**:
- `app/services/user_service.py`:
  - `get_users(db, page, per_page)`: SELECT с пагинацией, ORDER BY created_at DESC
  - `create_user(db, data)`: проверка дубликата email (409), генерация temp password, хеширование, создание с must_change_password=true; возвращает User + temp_password
  - `update_user(db, user_id, data, current_user)`: 404 если не найден, 403 при self-role-change / self-deactivate, partial update
  - `delete_user(db, user_id, current_user)`: 404, 403 self-delete, 403 last-admin check, hard delete CASCADE
  - `update_profile(db, user, name)`: обновление только name текущего пользователя
- `app/api/v1/users.py`:
  - `GET /` (admin): пагинированный список
  - `POST /` (admin): создание, возвращает UserWithPasswordResponse
  - `PATCH /{id}` (admin): partial update
  - `DELETE /{id}` (admin): удаление, 204
  - `PATCH /me/profile` (auth): обновление своего имени
- Все защитные проверки из PRD реализованы
- Пагинация работает корректно (total, pages)

**Время**: ~2.5 часа

---

### TASK-13: Document Service + Document Router

**Описание**: Реализовать сервис документов: загрузка файлов, список с фильтрацией, удаление. Без RAG-обработки (будет в TASK-16).

**Зависимости**: TASK-11

**Критерии готовности**:
- `app/services/document_service.py`:
  - `upload_document(db, file, user, background_tasks)`: валидация типа (расширение + MIME), размера (50MB), проверка дубликата original_name (409); сохранение файла на диск как `{uuid}.{ext}` в UPLOAD_DIR; создание записи в БД со статусом "uploaded"; добавление background task (заглушка, реальная обработка в TASK-16)
  - `list_documents(db, status, page, per_page)`: SELECT с опциональным фильтром по status, пагинация, ORDER BY created_at DESC, join uploaded_by для имени
  - `get_document(db, doc_id)`: SELECT по id, 404
  - `delete_document(db, doc_id)`: 404, удаление записи (CASCADE чанки), удаление файла с диска (warning если файл не существует)
- `app/api/v1/documents.py`:
  - `POST /` (admin): multipart/form-data, возвращает DocumentResponse (201)
  - `GET /` (admin): query param `status`, пагинация
  - `GET /{id}` (admin): один документ
  - `DELETE /{id}` (admin): удаление, 204
- Директория uploads/ создается автоматически при старте
- MIME-type проверяется через python-magic или по заголовку файла

**Время**: ~2.5 часа

---

### TASK-14: Conversation Service + Chat Router (без RAG)

**Описание**: Реализовать CRUD разговоров и отправку сообщений. Вместо RAG — заглушка, возвращающая "AI response placeholder". RAG подключится в TASK-17.

**Зависимости**: TASK-11

**Критерии готовности**:
- `app/services/chat_service.py`:
  - `create_conversation(db, user, title)`: создание записи
  - `list_conversations(db, user, search, page, per_page)`: SELECT WHERE user_id AND NOT is_deleted, ILIKE search по title, ORDER BY updated_at DESC, с last_message_preview (subquery: первые 100 символов последнего assistant message)
  - `get_conversation(db, conv_id, user)`: 404 (или is_deleted), 403 owner check, загрузка messages ORDER BY created_at
  - `delete_conversation(db, conv_id, user)`: 404, 403, soft delete (is_deleted=true)
  - `send_message(db, conv_id, user, content, model)`: 404, 403, сохранение user message, вызов RAG (заглушка), сохранение assistant message, обновление title (первое сообщение → первые 50 символов), обновление updated_at
- `app/api/v1/chat.py`:
  - `POST /` (auth): создание
  - `GET /` (auth): список с search
  - `GET /{id}` (auth): полный разговор с сообщениями
  - `DELETE /{id}` (auth): soft delete, 204
  - `POST /{id}/messages` (auth): отправка, возвращает SendMessageResponse
- Router с prefix="/conversations", tags=["Chat"]
- last_message_preview корректно вычисляется

**Время**: ~3 часа

---

### TASK-15: Dashboard Service + Dashboard Router

**Описание**: Реализовать аналитические эндпоинты: статистика, график активности, топ вопросов.

**Зависимости**: TASK-11

**Критерии готовности**:
- `app/services/dashboard_service.py`:
  - `get_stats(db, period)`: агрегирующие COUNT запросы — total_users, active_users (is_active=true), total_documents, indexed_documents (status=indexed), total_conversations (not is_deleted), questions_in_period (messages WHERE role=user за period), questions_change_percent (сравнение с предыдущим аналогичным периодом; null если нет данных)
  - `get_activity(db, period)`: GROUP BY DATE(created_at) для messages WHERE role=user, заполнение пустых дней нулями, формат YYYY-MM-DD
  - `get_top_questions(db)`: SELECT content, COUNT(*) FROM messages WHERE role='user' AND это первое сообщение в разговоре (MIN created_at в рамках conversation) GROUP BY content ORDER BY count DESC LIMIT 5
- `app/api/v1/dashboard.py`:
  - `GET /stats` (admin): query param period ("today", "7d", "30d" default)
  - `GET /activity` (admin): query param period ("7d", "30d" default)
  - `GET /top-questions` (admin): топ-5 за все время
- Router с prefix="/dashboard", tags=["Dashboard"]
- Пустые дни в activity заполняются нулями

**Время**: ~2.5 часа

---

### TASK-16: RAG Pipeline — Document Processing (background task)

**Описание**: Реализовать полный pipeline обработки документов: парсинг (PDF, DOCX, TXT), очистка текста, чанкинг (tiktoken), генерация embeddings (OpenAI API), сохранение чанков с векторами.

**Зависимости**: TASK-13, TASK-05

**Критерии готовности**:
- `app/services/rag/processor.py`:
  - `parse_document(filepath, file_type)`: диспатчер по типу файла
  - `parse_pdf(filepath)`: PyPDF2, извлечение текста по страницам
  - `parse_docx(filepath)`: python-docx, извлечение текста по параграфам
  - `parse_txt(filepath)`: чтение UTF-8
  - `clean_text(text)`: удаление лишних пробелов, непечатных символов, нормализация unicode
  - `chunk_text(text, chunk_size=512, overlap=50)`: разбиение по параграфам, потом по предложениям; размер в токенах (tiktoken, cl100k_base); overlap 50 токенов; минимальный размер чанка 50 токенов
- `app/services/rag/embeddings.py`:
  - `generate_embedding(text)`: OpenAI text-embedding-3-small, 1536 dim, один текст
  - `generate_embeddings_batch(texts)`: батч до 100 текстов, retry 3x с exponential backoff (1s, 2s, 4s)
- `app/tasks/document_tasks.py`:
  - `process_document_task(document_id)`: полный pipeline — новая AsyncSession, загрузка документа, status→processing, parse, clean, chunk, embed batch, INSERT chunks, status→indexed/error
- Заглушка из TASK-13 заменена на реальный вызов process_document_task
- Обработка ошибок: при ошибке на любом шаге — status=error, error_message=str(error)
- Password-protected PDF → error с понятным сообщением
- Пустой документ (0 текста) → indexed, chunk_count=0

**Время**: ~3 часа

---

### TASK-17: RAG Pipeline — Query (retriever + generator)

**Описание**: Реализовать поиск по векторной базе и генерацию ответов через LLM (Claude / GPT). Подключить к send_message.

**Зависимости**: TASK-16, TASK-14

**Критерии готовности**:
- `app/services/rag/retriever.py`:
  - `search_similar_chunks(db, query_embedding, top_k=5, threshold=0.3)`: SQL через SQLAlchemy — SELECT document_chunks JOIN documents WHERE status=indexed, ORDER BY embedding <=> query_embedding, LIMIT top_k; post-filter: cosine distance > 0.7 (similarity < 0.3) — отбросить; возвращает список чанков с document_name и relevance_score
- `app/services/rag/generator.py`:
  - `build_prompt(chunks, conversation_history, question)`: формирование messages[] с system prompt (точный текст из PRD), context (chunks с [Source: name]), history (последние 6 сообщений), user question
  - `generate_answer(prompt, model)`: диспатчер по модели
  - `call_claude(messages)`: Anthropic API, claude-sonnet-4-20250514, temperature=0.1, max_tokens=2048, timeout=60s, retry 1x
  - `call_gpt(messages)`: OpenAI API, gpt-4o, те же параметры
- Обновить `chat_service.send_message()`: заменить заглушку на полный RAG pipeline (embed question → search → build prompt → generate → build sources)
- Формирование sources JSONB: document_id, document_name, chunk_index, relevance_score, snippet (первые 200 символов чанка)
- Проверка наличия indexed документов перед RAG: если 0 → 503 "No documents have been indexed yet..."
- 0 результатов поиска → AI отвечает "I don't have enough information..."

**Время**: ~3 часа

---

### TASK-18: Health Check Endpoint

**Описание**: Реализовать публичный health endpoint с проверкой всех компонентов.

**Зависимости**: TASK-03

**Критерии готовности**:
- `app/api/v1/health.py`:
  - `GET /`: без авторизации
  - Проверка database: `SELECT 1`
  - Проверка redis: `PING`
  - Проверка AI: наличие API keys (не вызов API)
  - Формат ответа: `{"status": "healthy"/"unhealthy", "version": "1.0.0", "components": {...}}`
  - HTTP 200 если все healthy, 503 если хотя бы один unhealthy
- Router с prefix="/health", tags=["Health"]

**Время**: ~1 час

---

### TASK-19: Сборка API Router и Swagger

**Описание**: Собрать все роутеры в единый v1_router, проверить Swagger UI, добавить описания эндпоинтов и тегов.

**Зависимости**: TASK-11, TASK-12, TASK-13, TASK-14, TASK-15, TASK-18

**Критерии готовности**:
- `app/api/v1/router.py`: подключение всех sub-routers с правильными prefix и tags
- `app/main.py`: include_router(v1_router, prefix="/api/v1")
- Swagger UI доступен по `/docs`
- OpenAPI spec доступен по `/openapi.json`
- Все эндпоинты отображаются, сгруппированы по тегам (Auth, Chat, Documents, Users, Dashboard, Health)
- Каждый эндпоинт имеет description и response model
- Примеры запросов/ответов в схемах (Pydantic `json_schema_extra`)

**Время**: ~1.5 часа

---

## Фаза 5: Фронтенд — основа и авторизация

---

### TASK-20: Фронтенд — API-клиент и Auth Context

**Описание**: Настроить Axios-клиент с interceptors, AuthContext для управления токеном и пользователем, хук useAuth.

**Зависимости**: TASK-01

**Критерии готовности**:
- `src/api/client.ts`: Axios instance, baseURL `/api/v1`, interceptor для добавления Authorization header из localStorage, interceptor для 401 → удалить token + redirect /login
- `src/contexts/AuthContext.tsx`: AuthProvider, значения: token, user, isAuthenticated, isAdmin, login(), logout(); при загрузке: проверка token в localStorage, декодирование JWT для user info
- `src/hooks/useAuth.ts`: custom hook, обертка над AuthContext
- `src/api/auth.ts`: login(email, password), changePassword(current, new, confirm)
- `src/types/index.ts`: типы User, LoginResponse, Conversation, Message, Document, etc.
- `src/lib/constants.ts`: MAX_MESSAGE_LENGTH=4000, MODELS, etc.
- Типизация полная, без `any`

**Время**: ~2 часа

---

### TASK-21: Фронтенд — роутинг и Layout

**Описание**: Настроить React Router с защищенными маршрутами, AppLayout (sidebar для non-chat страниц), ProtectedRoute компонент.

**Зависимости**: TASK-20

**Критерии готовности**:
- `src/App.tsx`: BrowserRouter, QueryClientProvider, AuthProvider, Toaster (sonner), Routes по TDD (все маршруты)
- `src/components/layout/ProtectedRoute.tsx`: проверка isAuthenticated (→ /login), проверка must_change_password (→ /change-password), проверка requiredRole (→ /chat для user)
- `src/components/layout/AppLayout.tsx`: sidebar 280px bg-white + border-right, навигационные ссылки (Chat, Dashboard, Documents, Users, Settings) с иконками lucide, active state (bg-primary/10), admin-only пункты не рендерятся для user; User Menu внизу; Outlet
- `src/components/layout/Sidebar.tsx`: общий sidebar компонент
- Все redirects из PRD реализованы (таблица из раздела 13)
- React Query client настроен: staleTime, gcTime, refetchOnWindowFocus по таблице из TDD

**Время**: ~2.5 часа

---

### TASK-22: Фронтенд — Login Page

**Описание**: Реализовать страницу входа со всеми состояниями из PRD.

**Зависимости**: TASK-20, TASK-21

**Критерии готовности**:
- `src/pages/LoginPage.tsx`:
  - Layout: bg-slate-50, центрированная карточка 400px, shadow-lg, rounded-xl, mt-[20vh]
  - Логотип: Bot icon 40px text-primary + "AI Support Agent" text-2xl + подзаголовок
  - Форма: email + password с иконкой Eye/EyeOff + Sign In кнопка w-full
  - Валидация при blur: email format, password required
  - Кнопка disabled пока оба поля пустые
  - Submit по Enter
  - Автофокус на email
  - Все состояния: Default, Submitting (spinner "Signing in..."), Error credentials (Alert inline), Error deactivated, Error network, Success (redirect)
  - Redirect: авторизованный пользователь → /chat (user) или /dashboard (admin)
  - Tab order: Email → Password → Sign In
  - Футер: "Powered by AI Support Agent"

**Время**: ~2 часа

---

### TASK-23: Фронтенд — Change Password Page

**Описание**: Реализовать страницу принудительной смены пароля.

**Зависимости**: TASK-22

**Критерии готовности**:
- `src/pages/ChangePasswordPage.tsx`:
  - Layout: идентичен Login (карточка 400px)
  - Shield icon amber-500 + заголовок + подзаголовок
  - Форма: New Password + Confirm Password + иконки глаза
  - Индикаторы требований (в реальном времени): "At least 8 characters", "Contains a letter", "Contains a number" — Check зеленый / X красный
  - Кнопка disabled пока требования не соблюдены и пароли не совпадают
  - Проверка passwords mismatch при blur на Confirm
  - Все состояния из PRD
  - Успех: toast + redirect через 1 сек
  - Доступ: только must_change_password=true

**Время**: ~1.5 часа

---

## Фаза 6: Фронтенд — Chat

---

### TASK-24: Фронтенд — Chat API hooks

**Описание**: Создать API-функции и React Query hooks для чата.

**Зависимости**: TASK-20

**Критерии готовности**:
- `src/api/chat.ts`: getConversations(search?, page?), createConversation(title?), getConversation(id), deleteConversation(id), sendMessage(conversationId, content, model)
- `src/hooks/useConversations.ts`: useConversations(search) — useQuery; useCreateConversation — useMutation (invalidate conversations); useDeleteConversation — useMutation (invalidate conversations)
- `src/hooks/useMessages.ts`: useConversation(id) — useQuery (staleTime: 0); useSendMessage — useMutation (invalidate conversation + conversations)
- Правильные query keys: ['conversations'], ['conversation', id]
- Инвалидация кеша при мутациях по таблице из TDD

**Время**: ~1.5 часа

---

### TASK-25: Фронтенд — ChatSidebar

**Описание**: Реализовать левую панель чата: кнопка New Chat, поиск, список разговоров с группировкой по датам, user menu.

**Зависимости**: TASK-24, TASK-21

**Критерии готовности**:
- `src/components/chat/ChatSidebar.tsx`:
  - Ширина 280px, bg-slate-900, text-slate-100, border-r border-slate-800
  - Кнопка "New Chat": outline, Plus icon, onClick → createConversation + navigate
  - Поле поиска: Search icon, bg-slate-800, debounce 300ms, кнопка X для очистки
  - Список разговоров с группировкой: "Today", "Yesterday", "Previous 7 Days", "Previous 30 Days", "Older"
  - Заголовок группы: text-xs uppercase text-slate-500
  - Каждый элемент: title (ellipsis), preview, hover bg-slate-800, active border-l-2 border-primary
  - При hover: кнопка Trash2 (text-red-400)
  - User Menu внизу: аватар (буква), имя, роль, LogOut
- `src/components/chat/ConversationList.tsx`: отрисовка элементов с группировкой
- Мобильная версия (<768px): sidebar скрыта, гамбургер-меню, overlay bg-black/50, slide-in animation
- Удаление: AlertDialog подтверждение
- Клик на Logout: удаление token, redirect /login

**Время**: ~3 часа

---

### TASK-26: Фронтенд — ChatMessage + ChatSources + TypingIndicator

**Описание**: Реализовать компоненты отображения сообщений (user и AI), блок источников, индикатор набора.

**Зависимости**: TASK-20

**Критерии готовности**:
- `src/components/chat/ChatMessage.tsx`:
  - User message: аватар (буква, bg-slate-200), "You", время, текст (pre-wrap)
  - AI message: аватар (Bot icon, bg-primary), "AI Assistant", badge модели (зеленый Claude / синий GPT), время, markdown-рендер (react-markdown + remark-gfm), code blocks (bg-slate-100, моноширинный)
  - Блок Sources (если есть): заголовок "Sources" + FileText icon, pill badges bg-slate-100, tooltip с relevance score
- `src/components/chat/ChatSources.tsx`: отдельный компонент для источников
- `src/components/chat/TypingIndicator.tsx`: аватар AI + 3 bouncing dots (CSS animation) + "Thinking..."
- `src/components/chat/ModelSelector.tsx`: shadcn Select, Sparkles icon, "Claude" / "GPT", значение из localStorage
- Формат времени: "2:30 PM" через date-fns

**Время**: ~2.5 часа

---

### TASK-27: Фронтенд — ChatPage (сборка)

**Описание**: Собрать страницу чата: ChatSidebar + Main Content Area (Welcome Screen / Active Conversation), ChatInput, интеграция с hooks.

**Зависимости**: TASK-25, TASK-26, TASK-24

**Критерии готовности**:
- `src/pages/ChatPage.tsx`:
  - Двухколоночный layout: ChatSidebar (280px) + Main Content
  - URL `/chat` — Welcome Screen, `/chat/:id` — Active Conversation
- `src/components/chat/WelcomeScreen.tsx`:
  - MessageSquare 48px text-slate-300 + "How can I help you today?" + 3 карточки-примера
  - Клик на карточку: createConversation + sendMessage
  - Мобильный: карточки вертикально
- `src/components/chat/ChatInput.tsx`:
  - ModelSelector (120px) + Textarea (auto-resize, pill shape, max-height 120px) + Send button (круглая 40px)
  - Enter: отправить, Shift+Enter: новая строка
  - Disabled: пустой input или отправка
  - Placeholder: "Type your message..."
- Main Content Area:
  - Scrollable messages, max-width 768px mx-auto
  - Auto-scroll к последнему сообщению
  - Кнопка "scroll to bottom" при проскролле >200px вверх
  - Все состояния: Loading conversation (spinner), Empty conversation, Messages loaded, Sending (optimistic + typing), AI error (red bg + Retry), No documents, Conversation not found (redirect), Network error (toast)

**Время**: ~3 часа

---

## Фаза 7: Фронтенд — Admin Pages

---

### TASK-28: Фронтенд — Dashboard API hooks

**Описание**: Создать API-функции и React Query hooks для дашборда.

**Зависимости**: TASK-20

**Критерии готовности**:
- `src/api/dashboard.ts`: getStats(period), getActivity(period), getTopQuestions()
- `src/hooks/useDashboard.ts`: useStats(period), useActivity(period), useTopQuestions() — useQuery с staleTime 1min, refetchOnWindowFocus true
- Query keys: ['dashboard', 'stats', period], ['dashboard', 'activity', period], ['dashboard', 'top-questions']

**Время**: ~1 час

---

### TASK-29: Фронтенд — DashboardPage

**Описание**: Реализовать страницу дашборда: stat cards, activity chart, top questions, recent conversations.

**Зависимости**: TASK-28, TASK-21

**Критерии готовности**:
- `src/pages/DashboardPage.tsx`:
  - Header: "Dashboard" + Period Selector (Today / 7 Days / 30 Days toggle)
  - Переключение периода обновляет все данные
- `src/components/dashboard/StatCard.tsx`: иконка в цветном кружке, число text-3xl, доп инфо text-sm; 4 карточки grid (4 cols desktop, 2 tablet, 1 mobile)
- `src/components/dashboard/ActivityChart.tsx`: recharts LineChart, ось X даты (Jul 1), ось Y вопросы, primary цвет, tooltip, заливка, высота 300px (200px mobile)
- `src/components/dashboard/TopQuestions.tsx`: shadcn Table, 5 строк, #/Question/Count
- `src/components/dashboard/RecentConversations.tsx`: список 5 элементов, аватар + имя + превью + время
- Все состояния: Loading (skeleton loaders), Loaded, Empty (нули), Error (toast + retry)

**Время**: ~3 часа

---

### TASK-30: Фронтенд — Documents API hooks

**Описание**: Создать API-функции и React Query hooks для документов.

**Зависимости**: TASK-20

**Критерии готовности**:
- `src/api/documents.ts`: getDocuments(status?, page?), uploadDocument(file), deleteDocument(id)
- `src/hooks/useDocuments.ts`: useDocuments(status, page) — useQuery, staleTime 30s; useUploadDocument — useMutation; useDeleteDocument — useMutation; polling: refetchInterval 5000 когда есть processing документы
- Инвалидация: при upload/delete → invalidate ['documents']

**Время**: ~1 час

---

### TASK-31: Фронтенд — DocumentsPage

**Описание**: Реализовать страницу управления документами: upload zone, progress bars, таблица, фильтры, пагинация.

**Зависимости**: TASK-30, TASK-21

**Критерии готовности**:
- `src/pages/DocumentsPage.tsx`:
  - Header: "Documents" + кнопка "Upload Document"
- `src/components/documents/DocumentUpload.tsx`:
  - Drag & drop zone: dashed border, CloudUpload icon, "Drag & drop files here"
  - Drag over state: border-primary bg-primary/5
  - File picker: accept .pdf,.docx,.txt, multiple
  - Клиентская валидация: тип, размер 50MB
- `src/components/documents/UploadProgress.tsx`:
  - Для каждого файла: иконка типа, имя, размер, progress bar, статус
  - Статусы: Uploading (синий), Processing (желтый pulsating), Indexed (зеленый Check), Error (красный X)
- `src/components/documents/DocumentTable.tsx`:
  - shadcn Table: Name (icon + name), Type (badge), Size, Status (badge), Chunks, Uploaded (relative time), Actions (Trash2)
  - Hover строки bg-slate-50
  - Error tooltip при hover на Status Error
- `src/components/documents/StatusBadge.tsx`: цветные badges (Indexed/Processing/Error)
- Filter Tabs: All / Indexed / Processing / Error с count badges
- Пагинация: 20 на страницу
- Все состояния: Loading (skeleton 5 строк), Empty (empty state с кнопкой upload), Loaded, Uploading, Delete (AlertDialog)

**Время**: ~3 часа

---

### TASK-32: Фронтенд — Users API hooks

**Описание**: Создать API-функции и React Query hooks для управления пользователями.

**Зависимости**: TASK-20

**Критерии готовности**:
- `src/api/users.ts`: getUsers(page?), createUser(data), updateUser(id, data), deleteUser(id)
- `src/hooks/useUsers.ts`: useUsers(page) — useQuery, staleTime 1min; useCreateUser, useUpdateUser, useDeleteUser — useMutation с инвалидацией ['users']

**Время**: ~1 час

---

### TASK-33: Фронтенд — UsersPage

**Описание**: Реализовать страницу управления пользователями: таблица с inline-edit, модалка создания.

**Зависимости**: TASK-32, TASK-21

**Критерии готовности**:
- `src/pages/UsersPage.tsx`:
  - Header: "Users" + кнопка "Add User"
- `src/components/users/UserTable.tsx`:
  - shadcn Table: User (аватар + name + email), Role (inline Select), Status (toggle switch), Created, Actions (Trash2)
  - Текущий пользователь: bg-primary/5, "(you)", disabled select/toggle/no delete
  - Role change: мгновенный PATCH, toast, откат при ошибке
  - Status toggle: деактивация → AlertDialog, активация → сразу PATCH
  - Delete: AlertDialog
- `src/components/users/AddUserModal.tsx`:
  - shadcn Dialog 480px
  - Форма: Name, Email, Role (Select)
  - Валидация при blur
  - Success: НЕ закрывается, показывает credentials (email + temporary password + Copy button)
  - Предупреждение: "This password will only be shown once"
  - Кнопка Done закрывает + refetch
- Пагинация: 20 на страницу
- Все состояния из PRD

**Время**: ~3 часа

---

### TASK-34: Фронтенд — SettingsPage

**Описание**: Реализовать страницу настроек профиля и смены пароля.

**Зависимости**: TASK-20, TASK-21

**Критерии готовности**:
- `src/pages/SettingsPage.tsx`:
  - Layout: max-width 600px центрировано
  - Profile Section (Card): Name (editable), Email (disabled, bg-slate-50), Role (badge, read-only), Save Changes (disabled если не изменилось)
  - Change Password Section (Card): Current Password, New Password, Confirm + иконки глаза + индикаторы требований + Update Password
  - Toast при успехе/ошибке
  - PATCH /users/me/profile для имени
  - POST /auth/change-password для пароля

**Время**: ~2 часа

---

### TASK-35: Фронтенд — NotFoundPage (404)

**Описание**: Реализовать страницу 404.

**Зависимости**: TASK-21

**Критерии готовности**:
- `src/pages/NotFoundPage.tsx`:
  - "404" text-6xl text-slate-200 + "Page Not Found" + подтекст + кнопка "Go to Chat"
  - Если авторизован: AppLayout с Sidebar
  - Если нет: полный экран

**Время**: ~0.5 часа

---

## Фаза 8: Утилиты и полировка фронтенда

---

### TASK-36: Фронтенд — утилиты и общие компоненты

**Описание**: Реализовать утилитарные функции и пропущенные мелкие компоненты.

**Зависимости**: TASK-20

**Критерии готовности**:
- `src/lib/utils.ts`: cn() (clsx + tailwind-merge), formatDate(), formatRelativeTime() (date-fns: "2h ago", "Yesterday", "Jul 15"), formatFileSize() (KB/MB), truncate(str, maxLen)
- `src/styles/globals.css`: @tailwind directives, CSS-анимация bouncing dots для TypingIndicator, пульсирующий dot для processing status
- `public/favicon.svg`: Bot icon
- Sonner Toaster: позиция bottom-right, длительность 4s, max 3

**Время**: ~1.5 часа

---

### TASK-37: Фронтенд — адаптивная верстка и мобильная версия

**Описание**: Проверить и доработать responsive design для всех страниц: мобильные breakpoints, sidebar поведение, grid перестроение.

**Зависимости**: TASK-27, TASK-29, TASK-31, TASK-33, TASK-34, TASK-35

**Критерии готовности**:
- Chat Sidebar (<768px): скрыта, гамбургер, overlay, slide-in 200ms
- Dashboard stat cards: 4 cols > 2 cols > 1 col
- Dashboard chart: 300px → 200px на мобильных
- Dashboard нижний ряд: 2 cols → 1 col
- Documents/Users таблицы: горизонтальный скролл на мобильных
- Welcome Screen карточки: горизонтально → вертикально
- Login/Change Password: адаптивная ширина карточки (max-w-[400px] w-full mx-4)
- Settings: max-w-[600px] w-full px-4
- Все элементы минимум 44px touch target на мобильных

**Время**: ~2 часа

---

## Фаза 9: Интеграция и тестирование

---

### TASK-38: Интеграция фронтенда с бэкендом через Nginx

**Описание**: Проверить полную интеграцию всех компонентов через Docker Compose: Nginx проксирует, SPA работает, API работает, все flow проходят.

**Зависимости**: TASK-19, TASK-37, TASK-02

**Критерии готовности**:
- `docker-compose up -d` поднимает все 5 сервисов
- Nginx корректно проксирует: / → frontend, /api/* → backend, /docs → Swagger
- SPA routing работает (refresh на /chat/:id не дает 404)
- Frontend подключается к API без CORS ошибок
- Логин работает end-to-end: вход admin → dashboard → documents → upload → chat → вопрос → ответ
- Health endpoint доступен: curl http://localhost/api/v1/health

**Время**: ~2 часа

---

### TASK-39: Тесты бэкенда — Auth + Users

**Описание**: Написать автотесты для auth и users API.

**Зависимости**: TASK-11, TASK-12

**Критерии готовности**:
- `tests/conftest.py`: тестовая БД (async, PostgreSQL), fixtures: async_client (httpx.AsyncClient), test_db (AsyncSession), auth_headers (token admin), user_auth_headers (token user)
- `tests/test_auth.py`:
  - Login success
  - Login invalid credentials (401)
  - Login deactivated (403)
  - Change password success
  - Change password wrong current (401)
  - Change password mismatch (400)
  - Change password weak (400)
- `tests/test_users.py`:
  - Get users list (admin)
  - Get users forbidden (user → 403)
  - Create user success
  - Create user duplicate email (409)
  - Update user role
  - Self role change (403)
  - Self deactivate (403)
  - Delete user
  - Self delete (403)
  - Delete last admin (403)
  - Update profile (any user)
- Все тесты проходят: `pytest tests/test_auth.py tests/test_users.py`

**Время**: ~3 часа

---

### TASK-40: Тесты бэкенда — Chat + Documents + Dashboard

**Описание**: Написать автотесты для chat, documents и dashboard API.

**Зависимости**: TASK-14, TASK-13, TASK-15

**Критерии готовности**:
- `tests/test_chat.py`:
  - Create conversation
  - List conversations (own only)
  - Get conversation with messages
  - Get other user's conversation (403)
  - Delete conversation (soft delete)
  - Send message (с мокнутым RAG)
  - Access deleted conversation (404)
- `tests/test_documents.py`:
  - Upload PDF (с мокнутым background task)
  - Upload invalid type (400)
  - Upload too large (413)
  - List documents with filter
  - Delete document
  - Upload forbidden (user → 403)
- `tests/test_dashboard.py`:
  - Get stats
  - Get activity (проверка заполнения пустых дней)
  - Get top questions
  - Dashboard forbidden (user → 403)
- `tests/test_rag.py`:
  - chunk_text: проверка размеров чанков
  - clean_text: удаление лишних символов
  - parse_txt: чтение файла
- Все тесты проходят: `pytest`

**Время**: ~3 часа

---

## Фаза 10: DevOps и финализация

---

### TASK-41: GitHub Actions CI/CD

**Описание**: Создать CI/CD pipeline для автоматической проверки и сборки.

**Зависимости**: TASK-38

**Критерии готовности**:
- `.github/workflows/ci.yml` (on push/PR):
  - Checkout
  - Setup Python 3.13
  - Cache pip
  - Install dependencies (requirements.txt + requirements-dev.txt)
  - Lint (ruff check)
  - Setup Node.js 20
  - Cache npm
  - Install frontend deps
  - Lint frontend (eslint)
  - TypeScript check (tsc --noEmit)
  - Build frontend (vite build)
  - Setup PostgreSQL service (postgres:16 + pgvector)
  - Setup Redis service
  - Run backend tests (pytest)
  - Build Docker images (без push)
- `.github/workflows/cd.yml` (on push to main):
  - Все шаги CI
  - Login to GHCR
  - Push Docker images (ghcr.io) с тегами latest + SHA

**Время**: ~2 часа

---

### TASK-42: Linting и форматирование

**Описание**: Настроить линтеры и форматтеры для backend и frontend.

**Зависимости**: TASK-01

**Критерии готовности**:
- Backend: `ruff` (linter + formatter), `pyproject.toml` с конфигурацией ruff (line-length=120, Python 3.13 target)
- Frontend: `.eslintrc.cjs` или `eslint.config.js` (TypeScript + React rules), `.prettierrc` (semi, singleQuote, tabWidth 2)
- `ruff check backend/` проходит без ошибок
- `npx eslint src/` проходит без ошибок
- `npx tsc --noEmit` проходит без ошибок

**Время**: ~1.5 часа

---

### TASK-43: Seed Data (демо-данные)

**Описание**: Создать скрипт для заполнения БД демо-данными: пользователи, документы, разговоры с сообщениями. Для скриншотов и демо.

**Зависимости**: TASK-17

**Критерии готовности**:
- `backend/scripts/seed.py`: standalone скрипт
- Создает:
  - Admin user (из .env)
  - 3 обычных пользователя (разные имена)
  - 3 демо-документа (txt файлы с реалистичным бизнес-контентом: HR Policy, Vacation Policy, IT Guidelines)
  - Обработка документов (чанки + embeddings — либо мок, либо реальный вызов если API keys есть)
  - 5-7 разговоров с реалистичными вопросами и ответами
- Запуск: `python -m scripts.seed` из backend/
- Идемпотентный: проверяет существование данных перед вставкой

**Время**: ~2 часа

---

### TASK-44: Финальная проверка и .env.example

**Описание**: Полный прогон всего приложения, проверка всех flow, финализация .env.example.

**Зависимости**: TASK-38, TASK-39, TASK-40, TASK-41, TASK-42

**Критерии готовности**:
- `.env.example`: все переменные с описаниями, секреты помечены CHANGE_ME, разбиты по секциям (App, Database, Redis, Security, AI, Admin)
- `docker-compose up -d` → все сервисы поднимаются
- Admin создается автоматически
- Login → Change Password → Chat → Documents Upload → Processing → Indexed → Chat с RAG ответом → Sources → Dashboard → Users CRUD → Settings — весь flow работает
- Swagger UI доступен и актуален
- Health endpoint возвращает статусы всех компонентов
- Логи в JSON формате, содержат request_id
- Нет TODO в коде
- Нет placeholder логики
- Нет console.log в production коде frontend

**Время**: ~2 часа

---

### TASK-45: README.md

**Описание**: Создать профессиональный README для репозитория.

**Зависимости**: TASK-44

**Критерии готовности**:
- Структура README по Master Plan: Overview, Features, Screenshots (заглушки), Tech Stack, Architecture (диаграмма), Installation (Docker), Quick Start, API Documentation (ссылка на Swagger), Environment Variables (таблица), Project Structure, Development (локальный запуск), Testing, Future Improvements, License
- Английский язык
- Badges: Python, FastAPI, React, TypeScript, PostgreSQL, Docker, License
- Длина: 200-400 строк
- Профессиональный тон, без "demo" или "tutorial" — выглядит как реальный продукт

**Время**: ~2 часа

---

## Сводная таблица

| Фаза | Задачи | Время |
|------|--------|-------|
| 1. Инфраструктура | TASK-01 — TASK-03 | ~6.5 ч |
| 2. Модели и миграции | TASK-04 — TASK-06 | ~6 ч |
| 3. Core-модули | TASK-07 — TASK-10 | ~5.5 ч |
| 4. Сервисы и API | TASK-11 — TASK-19 | ~21.5 ч |
| 5. Фронтенд — основа | TASK-20 — TASK-23 | ~8 ч |
| 6. Фронтенд — Chat | TASK-24 — TASK-27 | ~10 ч |
| 7. Фронтенд — Admin | TASK-28 — TASK-35 | ~14.5 ч |
| 8. Утилиты и адаптив | TASK-36 — TASK-37 | ~3.5 ч |
| 9. Интеграция и тесты | TASK-38 — TASK-40 | ~8 ч |
| 10. DevOps и финал | TASK-41 — TASK-45 | ~9.5 ч |
| **Итого** | **45 задач** | **~93 часа** |

---

## Граф зависимостей (критический путь)

```
TASK-01 ──→ TASK-02
TASK-01 ──→ TASK-03 ──→ TASK-04 ──→ TASK-05
                    ├──→ TASK-07
                    ├──→ TASK-08
                    └──→ TASK-10

TASK-04 + TASK-07 ──→ TASK-09

TASK-05 + TASK-06 + TASK-08 + TASK-09 ──→ TASK-11

TASK-11 ──→ TASK-12
TASK-11 ──→ TASK-13 ──→ TASK-16
TASK-11 ──→ TASK-14 ──→ TASK-17 (зависит также от TASK-16)
TASK-11 ──→ TASK-15
TASK-03 ──→ TASK-18

TASK-11..18 ──→ TASK-19

TASK-01 ──→ TASK-20 ──→ TASK-21 ──→ TASK-22 ──→ TASK-23
                    ├──→ TASK-24 ──→ TASK-25
                    ├──→ TASK-28 ──→ TASK-29
                    ├──→ TASK-30 ──→ TASK-31
                    ├──→ TASK-32 ──→ TASK-33
                    ├──→ TASK-34
                    └──→ TASK-35

TASK-20 ──→ TASK-26

TASK-24 + TASK-25 + TASK-26 ──→ TASK-27

TASK-27 + TASK-29 + TASK-31 + TASK-33 + TASK-34 + TASK-35 ──→ TASK-37

TASK-19 + TASK-37 + TASK-02 ──→ TASK-38

TASK-11 + TASK-12 ──→ TASK-39
TASK-13 + TASK-14 + TASK-15 ──→ TASK-40

TASK-38 ──→ TASK-41
TASK-01 ──→ TASK-42
TASK-17 ──→ TASK-43

TASK-38..42 ──→ TASK-44 ──→ TASK-45
```

**Критический путь**:
```
TASK-01 → TASK-03 → TASK-04 → TASK-05 → TASK-11 → TASK-13 → TASK-16 → TASK-17 → TASK-43 → TASK-44 → TASK-45
```

---

## Порядок реализации (рекомендуемый)

Задачи сгруппированы в порядке выполнения. Внутри группы задачи можно выполнять параллельно.

1. **TASK-01** — инициализация
2. **TASK-02, TASK-03, TASK-42** — параллельно (Docker, config, linting)
3. **TASK-04, TASK-07, TASK-08, TASK-10** — параллельно (модели, security, exceptions, rate limit)
4. **TASK-05, TASK-06, TASK-09** — миграции, схемы, DI
5. **TASK-11** — auth (блокирует все API)
6. **TASK-12, TASK-13, TASK-14, TASK-15, TASK-18** — параллельно (все сервисы + health)
7. **TASK-16** — RAG processing
8. **TASK-17** — RAG query
9. **TASK-19** — сборка API
10. **TASK-20, TASK-36** — параллельно (фронтенд основа)
11. **TASK-21** — роутинг и layout
12. **TASK-22, TASK-24, TASK-26, TASK-28, TASK-30, TASK-32** — параллельно (страницы + hooks)
13. **TASK-23, TASK-25, TASK-29, TASK-31, TASK-33, TASK-34, TASK-35** — зависимые страницы
14. **TASK-27** — ChatPage сборка
15. **TASK-37** — адаптивная верстка
16. **TASK-38** — интеграция
17. **TASK-39, TASK-40, TASK-41, TASK-43** — параллельно (тесты, CI/CD, seed)
18. **TASK-44** — финальная проверка
19. **TASK-45** — README
