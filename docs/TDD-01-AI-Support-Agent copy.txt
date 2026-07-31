# TDD-01: AI Support Agent

## Technical Design Document

**Версия**: 1.0
**Дата**: 2026-07-31
**Статус**: Draft
**Основание**: PRD-01 v2.0
**Роль**: Lead Software Architect

---

## 1. Общая архитектура системы

### Архитектурный стиль

Монолитная архитектура с четким разделением слоев (Layered Monolith). Выбрана вместо микросервисов, потому что:
- Один продукт, одна команда, один деплой
- Нет требований к независимому масштабированию отдельных сервисов
- MVP: скорость разработки важнее гибкости масштабирования
- Меньше операционной сложности (нет service discovery, distributed tracing, saga)
- При необходимости легко выделить RAG pipeline в отдельный сервис (post-MVP)

### Топология

```
Internet
    │
    ▼
┌───────────────────────────────────────────────────┐
│                   Nginx (port 80)                  │
│   Reverse Proxy + Static Files + Security Headers  │
│                                                    │
│   /* ──────────→ Frontend (SPA static)             │
│   /api/* ──────→ Backend (FastAPI :8000)            │
│   /docs ───────→ Backend (Swagger UI)              │
│   /openapi.json→ Backend (OpenAPI spec)             │
└─────────┬──────────────────────┬──────────────────┘
          │                      │
          ▼                      ▼
┌─────────────────┐   ┌─────────────────────────────┐
│   Backend       │   │  Frontend                    │
│   FastAPI       │   │  Nginx serving static files  │
│   Python 3.13   │   │  React SPA (dist/)           │
│   Port 8000     │   │  Port 80 (internal)          │
│                 │   └─────────────────────────────┘
│  ┌───────────┐  │
│  │ API Layer │  │   Внешние сервисы (Internet):
│  ├───────────┤  │   ┌─────────────────────────────┐
│  │ Service   │──┼──→│ Anthropic API (Claude)       │
│  │ Layer     │──┼──→│ OpenAI API (Embeddings, GPT) │
│  ├───────────┤  │   └─────────────────────────────┘
│  │ Data      │  │
│  │ Layer     │  │
│  └───────────┘  │
└──────┬─────┬────┘
       │     │
       ▼     ▼
┌──────────┐ ┌──────┐
│PostgreSQL│ │Redis │
│+ pgvector│ │      │
│Port 5432 │ │:6379 │
└──────────┘ └──────┘
```

### Границы системы

**Входные точки**:
- HTTP запросы через Nginx (единственная внешняя точка)

**Исходящие запросы**:
- Anthropic API (HTTPS) — генерация ответов Claude
- OpenAI API (HTTPS) — генерация embeddings, ответы GPT

**Хранилища**:
- PostgreSQL — основное хранилище (users, conversations, messages, documents, chunks+vectors)
- Redis — rate limiting counters (slowapi хранит counters в Redis)
- Файловая система — загруженные документы (uploads/ volume)

### Сетевая модель (Docker)

Единая сеть `app-network` (bridge driver):

| Сервис | Hostname внутри сети | Доступ извне |
|--------|---------------------|--------------|
| nginx | nginx | 0.0.0.0:80 → 80 |
| backend | backend | нет (только через nginx) |
| frontend | frontend | нет (только через nginx) |
| postgres | postgres | 0.0.0.0:5432 → 5432 (dev) |
| redis | redis | 0.0.0.0:6379 → 6379 (dev) |

Postgres и Redis порты открыты наружу только для удобства разработки. В production их следует закрыть.

---

## 2. Диаграмма компонентов

```
┌─ Frontend Container ─────────────────────────────────────────────────┐
│                                                                      │
│  ┌─ React Application ──────────────────────────────────────────┐    │
│  │                                                               │    │
│  │  ┌─────────┐   ┌────────────┐   ┌──────────┐                │    │
│  │  │ Pages   │──→│ Components │   │ Contexts  │                │    │
│  │  │         │   │            │   │ (Auth)    │                │    │
│  │  │ Login   │   │ Chat       │   └────┬─────┘                │    │
│  │  │ Chat    │   │ Dashboard  │        │                       │    │
│  │  │ Dash    │   │ Documents  │        ▼                       │    │
│  │  │ Docs    │   │ Users      │   ┌──────────┐                │    │
│  │  │ Users   │   │ Layout     │   │ Hooks    │                │    │
│  │  │ Settings│   └────────────┘   │ (React   │                │    │
│  │  └─────────┘                    │  Query)  │                │    │
│  │                                 └────┬─────┘                │    │
│  │                                      │                       │    │
│  │                                      ▼                       │    │
│  │                                 ┌──────────┐                │    │
│  │                                 │ API      │                │    │
│  │                                 │ Client   │                │    │
│  │                                 │ (Axios)  │                │    │
│  │                                 └────┬─────┘                │    │
│  └──────────────────────────────────────┼────────────────────────┘    │
└─────────────────────────────────────────┼────────────────────────────┘
                                          │ HTTP /api/v1/*
                                          ▼
┌─ Backend Container ──────────────────────────────────────────────────┐
│                                                                      │
│  ┌─ FastAPI Application ────────────────────────────────────────┐    │
│  │                                                               │    │
│  │  ┌─ Middleware ────────────────────────────────────────────┐  │    │
│  │  │ CORS │ RequestID │ Logging │ RateLimit │ ExceptionHandler│ │    │
│  │  └───────────────────────────┬─────────────────────────────┘  │    │
│  │                              │                                │    │
│  │  ┌─ API Layer (Routers) ─────┴──────────────────────────┐    │    │
│  │  │ auth.py │ chat.py │ documents.py │ users.py │ dashboard│   │    │
│  │  │         │         │              │          │ health   │   │    │
│  │  └─────────────────────────┬─────────────────────────────┘   │    │
│  │                            │                                  │    │
│  │  ┌─ Dependencies ─────────┤                                  │    │
│  │  │ get_db │ get_current_user │ require_admin                 │    │
│  │  └────────────────────────┘                                  │    │
│  │                            │                                  │    │
│  │  ┌─ Service Layer ─────────┴──────────────────────────┐      │    │
│  │  │ AuthService │ ChatService │ DocumentService         │      │    │
│  │  │ UserService │ DashboardService                      │      │    │
│  │  │                                                     │      │    │
│  │  │  ┌─ RAG Sub-system ─────────────────────────────┐  │      │    │
│  │  │  │ Processor │ Embeddings │ Retriever │ Generator│  │      │    │
│  │  │  └───────────────────────────────────────────────┘  │      │    │
│  │  └─────────────────────────┬───────────────────────────┘      │    │
│  │                            │                                  │    │
│  │  ┌─ Data Layer ────────────┴──────────────────────────┐      │    │
│  │  │ SQLAlchemy Models │ Pydantic Schemas                │      │    │
│  │  │ User │ Conversation │ Message │ Document │ Chunk    │      │    │
│  │  └─────────────────────────┬───────────────────────────┘      │    │
│  │                            │                                  │    │
│  │  ┌─ Core ──────────────────┤                                  │    │
│  │  │ Security (JWT, bcrypt) │ Exceptions │ Logging (structlog) │    │
│  │  └─────────────────────────┘                                  │    │
│  └───────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌─ Background Tasks ───────────────────────────────────────────┐    │
│  │ document_tasks.py (FastAPI BackgroundTasks)                    │    │
│  │ process_document → parse → chunk → embed → store              │    │
│  └───────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 3. Структура Backend (послойная)

### Слой 1: Middleware (Cross-cutting)

Выполняется для каждого HTTP запроса, в порядке:

```
Request → CORS → RequestID → RateLimit → Logging(start) → Router → Logging(end) → Response
```

| Middleware | Назначение | Реализация |
|-----------|-----------|------------|
| CORS | Разрешить cross-origin запросы | FastAPI CORSMiddleware |
| RequestID | Генерация UUID для трассировки | Custom middleware, header X-Request-ID |
| RateLimit | Ограничение частоты запросов | slowapi (uses Redis backend) |
| Logging | Логирование request/response | structlog, duration_ms |
| ExceptionHandler | Преобразование исключений в HTTP responses | FastAPI exception_handler |

### Слой 2: API (Routers)

Тонкие контроллеры. Обязанности:
- Принять HTTP запрос
- Валидировать через Pydantic schema (автоматически FastAPI)
- Извлечь зависимости (Depends)
- Вызвать соответствующий Service метод
- Вернуть HTTP ответ с правильным status code

Не содержат: бизнес-логику, прямые запросы к БД, вызовы внешних API.

### Слой 3: Dependencies (DI)

FastAPI Depends — инъекция зависимостей:

```
get_db() → AsyncSession
    └── Каждый запрос получает свою сессию. Commit/rollback управляется в finally.

get_current_user(token, db) → User
    ├── Извлечь token из Authorization header
    ├── Decode JWT, получить user_id
    ├── SELECT user FROM users WHERE id = user_id AND is_active = true
    └── Если не найден или token невалидный → 401

require_admin(user) → User
    └── Если user.role != 'admin' → 403
```

### Слой 4: Services

Содержат бизнес-логику. Каждый service — набор функций (не класс), принимающих `db: AsyncSession` как первый аргумент.

Обоснование "функции, не классы":
- FastAPI идиоматика: функции с Depends
- Нет состояния между вызовами
- Проще тестировать (нет self, нет mock конструктора)
- Явные зависимости (все в аргументах)

### Слой 5: Models + Schemas

- **Models** (SQLAlchemy): маппинг Python-объектов на таблицы PostgreSQL
- **Schemas** (Pydantic v2): валидация входных данных, сериализация выходных

Разделение Models/Schemas: модель знает о БД, схема знает о HTTP. Модель никогда не возвращается клиенту напрямую — всегда конвертируется в схему.

### Слой 6: Core

Утилиты, не привязанные к конкретному домену:
- `security.py`: JWT (создание, верификация), bcrypt (хеширование, проверка), генерация паролей
- `exceptions.py`: кастомные исключения (`NotFoundError`, `ForbiddenError`, `ConflictError`) + FastAPI handlers
- `logging.py`: настройка structlog, формат JSON, request_id context var

---

## 4. Структура Frontend (архитектурная)

### Дерево рендеринга React

```
<App>
  <QueryClientProvider>          ← React Query cache provider
    <AuthProvider>               ← Auth context (token, user)
      <Toaster />                ← Sonner toast container
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/change-password" element={
            <ProtectedRoute mustChangePassword>
              <ChangePasswordPage />
            </ProtectedRoute>
          } />

          {/* Chat has its own layout (ChatSidebar) */}
          <Route path="/chat" element={
            <ProtectedRoute>
              <ChatPage />         ← own sidebar inside
            </ProtectedRoute>
          } />
          <Route path="/chat/:id" element={
            <ProtectedRoute>
              <ChatPage />
            </ProtectedRoute>
          } />

          {/* Admin pages use AppLayout (navigation sidebar) */}
          <Route element={
            <ProtectedRoute requiredRole="admin">
              <AppLayout />        ← sidebar + <Outlet />
            </ProtectedRoute>
          }>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/documents" element={<DocumentsPage />} />
            <Route path="/users" element={<UsersPage />} />
          </Route>

          {/* Settings for all users */}
          <Route element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }>
            <Route path="/settings" element={<SettingsPage />} />
          </Route>

          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  </QueryClientProvider>
</App>
```

### Data Flow

```
User Action (click, type, submit)
    │
    ▼
Component (local state: useState)
    │
    ▼
Hook (useConversations, useMessages, etc.)
    │
    ├── useMutation() — для POST/PATCH/DELETE
    │   ├── Вызывает API function
    │   ├── onSuccess: invalidate queries, toast
    │   └── onError: toast error
    │
    └── useQuery() — для GET
        ├── Вызывает API function
        ├── Кеширует результат (staleTime: 5min)
        ├── Возвращает { data, isLoading, error }
        └── Автоматический refetch при focus/reconnect
    │
    ▼
API Function (api/chat.ts, api/users.ts, etc.)
    │
    ▼
Axios Client (api/client.ts)
    ├── Добавляет Authorization header
    ├── Базовый URL: /api/v1
    └── Interceptor: 401 → logout + redirect
    │
    ▼
HTTP Request → Nginx → Backend
```

### React Query — конфигурация кеша

| Query Key | staleTime | gcTime | refetchOnWindowFocus |
|-----------|-----------|--------|---------------------|
| ['conversations'] | 30s | 5min | true |
| ['conversation', id] | 0 (always fresh) | 5min | false |
| ['documents'] | 30s | 5min | true |
| ['users'] | 1min | 5min | true |
| ['dashboard', period] | 1min | 5min | true |

**Инвалидация** (когда данные устаревают):
- Создание разговора → invalidate `['conversations']`
- Отправка сообщения → invalidate `['conversation', id]` + `['conversations']` (preview)
- Удаление разговора → invalidate `['conversations']`
- Upload документа → invalidate `['documents']`
- Удаление документа → invalidate `['documents']`
- Создание/изменение/удаление пользователя → invalidate `['users']`

---

## 5. Структура Docker

### Граф зависимостей (порядок запуска)

```
postgres ──(healthy)──→ backend ──→ nginx
redis ────(healthy)──→ backend
                       frontend ──→ nginx
```

### Entrypoint Backend

```
#!/bin/sh
alembic upgrade head          # Применить миграции
exec uvicorn app.main:app \   # Запустить приложение
  --host 0.0.0.0 \
  --port 8000 \
  --workers 1                 # 1 worker для MVP (BackgroundTasks в том же процессе)
```

Почему 1 worker: FastAPI BackgroundTasks работают в том же event loop. С несколькими workers задачи будут дублироваться или теряться. Для масштабирования (post-MVP) — Celery.

### Build контексты

| Dockerfile | Build context | Размер образа (approx) |
|------------|---------------|----------------------|
| backend/Dockerfile | ./backend | ~250MB |
| frontend/Dockerfile | ./frontend | ~25MB (nginx + static) |

### Volumes

| Volume | Mount point | Назначение | Backup |
|--------|------------|-----------|--------|
| postgres_data | /var/lib/postgresql/data | Данные БД | Да (pg_dump) |
| redis_data | /data | Данные Redis (rate limit counters) | Нет (ephemeral) |
| uploads | /app/uploads | Загруженные документы | Да |

---

## 6. Структура базы данных

### Физическая модель

```
                    ┌─────────────────────────────────────────────┐
                    │             PostgreSQL 16                    │
                    │             + pgvector extension             │
                    │                                              │
                    │  ┌─────────┐     ┌───────────────┐          │
                    │  │ users   │────→│ conversations │          │
                    │  │         │     │               │          │
                    │  │         │     └───────┬───────┘          │
                    │  │         │             │                   │
                    │  │         │     ┌───────▼───────┐          │
                    │  │         │     │   messages    │          │
                    │  │         │     └───────────────┘          │
                    │  │         │                                 │
                    │  │         │     ┌───────────────┐          │
                    │  │         │────→│  documents    │          │
                    │  │         │     │               │          │
                    │  └─────────┘     └───────┬───────┘          │
                    │                          │                   │
                    │                  ┌───────▼───────┐          │
                    │                  │document_chunks│          │
                    │                  │ (+ HNSW idx)  │          │
                    │                  └───────────────┘          │
                    └─────────────────────────────────────────────┘
```

### Стратегия миграций

Alembic (async mode) с autogenerate:
- Одна начальная миграция `001_initial.py`: создание pgvector extension + все 5 таблиц + все индексы
- Последующие миграции: autogenerate (`alembic revision --autogenerate -m "description"`)
- Миграции запускаются в entrypoint backend-а при каждом старте (`alembic upgrade head` — идемпотентно)
- Downgrade миграций не пишем (в MVP нет такой необходимости)

### Стратегия подключений

- Async driver: `asyncpg` (через SQLAlchemy async)
- Connection pool: SQLAlchemy AsyncEngine defaults (pool_size=5, max_overflow=10)
- Session: `async_sessionmaker(expire_on_commit=False)` — объекты остаются доступны после commit
- Lifecycle: одна сессия на HTTP запрос (через `get_db` dependency)

---

## 7. Все сущности (Domain Model)

### User
- Представляет зарегистрированного пользователя системы
- Две роли: admin, user
- Может быть деактивирован (is_active=false) — не может логиниться, но данные сохраняются
- При создании получает временный пароль и must_change_password=true
- Владеет: conversations (1:N), uploaded documents (1:N)

### Conversation
- Единица диалога между пользователем и AI
- Принадлежит одному User
- Содержит Messages (1:N)
- Soft delete (is_deleted=true) — не удаляется из БД
- Title автоматически генерируется из первого вопроса (первые 50 символов)
- updated_at обновляется при каждом новом сообщении

### Message
- Одно сообщение в разговоре
- Два типа: user (вопрос), assistant (ответ AI)
- Assistant message хранит: model (какая AI модель ответила), sources (JSONB — откуда взята информация)
- Не редактируется, не удаляется (append-only)

### Document
- Загруженный файл базы знаний
- Статусы: uploaded → processing → indexed / error
- Физически файл хранится на диске (uploads/{uuid}.{ext}), в БД — метаданные
- Связан с DocumentChunks (1:N) через CASCADE delete

### DocumentChunk
- Фрагмент документа после разбиения (чанкинга)
- Содержит текст + embedding vector (1536 dim)
- Используется для vector similarity search
- Метаданные (JSONB): номер страницы, индекс параграфа

---

## 8. Все сервисы

### auth_service.py

| Функция | Вход | Выход | Что делает |
|---------|------|-------|-----------|
| `authenticate(db, email, password)` | email (str), password (str) | User or None | Ищет user по email (lowercase, trim), проверяет пароль bcrypt, проверяет is_active |
| `change_password(db, user, current_pw, new_pw)` | User, str, str | None | Проверяет текущий пароль, валидирует новый (regex), хеширует, обновляет, сбрасывает must_change_password |
| `create_initial_admin(db)` | db | None | Проверяет пустоту таблицы users, создает admin из env переменных, must_change_password=true |

### user_service.py

| Функция | Вход | Выход | Что делает |
|---------|------|-------|-----------|
| `get_users(db, page, per_page)` | db, int, int | PaginatedResponse[User] | SELECT с пагинацией, ORDER BY created_at DESC |
| `create_user(db, data)` | db, UserCreate | User + temp_password | Генерирует пароль, хеширует, создает user, must_change_password=true |
| `update_user(db, user_id, data, current_user)` | db, UUID, UserUpdate, User | User | Проверяет защитные правила (self-edit), обновляет поля |
| `delete_user(db, user_id, current_user)` | db, UUID, User | None | Проверяет self-delete и last-admin, удаляет (CASCADE) |
| `update_profile(db, user, name)` | db, User, str | User | Обновляет только имя текущего пользователя |

### document_service.py

| Функция | Вход | Выход | Что делает |
|---------|------|-------|-----------|
| `upload_document(db, file, user)` | db, UploadFile, User | Document | Валидирует тип/размер/MIME, сохраняет на диск, создает запись в БД, запускает background task |
| `list_documents(db, status, page, per_page)` | db, str?, int, int | PaginatedResponse[Document] | SELECT с фильтром и пагинацией |
| `get_document(db, doc_id)` | db, UUID | Document | SELECT по id |
| `delete_document(db, doc_id)` | db, UUID | None | Удаляет запись (CASCADE чанки), удаляет файл с диска |

### chat_service.py

| Функция | Вход | Выход | Что делает |
|---------|------|-------|-----------|
| `create_conversation(db, user, title?)` | db, User, str? | Conversation | Создает запись |
| `list_conversations(db, user, search?, page, per_page)` | db, User, str?, int, int | PaginatedResponse | SELECT WHERE user_id AND NOT is_deleted, ILIKE search |
| `get_conversation(db, conv_id, user)` | db, UUID, User | Conversation + Messages | Проверяет owner, загружает messages ordered by created_at |
| `delete_conversation(db, conv_id, user)` | db, UUID, User | None | Проверяет owner, is_deleted=true |
| `send_message(db, conv_id, user, content, model)` | db, UUID, User, str, str | {user_msg, assistant_msg, title} | Полный RAG pipeline (см. раздел 14) |

### dashboard_service.py

| Функция | Вход | Выход | Что делает |
|---------|------|-------|-----------|
| `get_stats(db, period)` | db, str | StatsResponse | Агрегирующие COUNT запросы с периодом |
| `get_activity(db, period)` | db, str | ActivityResponse | GROUP BY date, заполнение пустых дней нулями |
| `get_top_questions(db)` | db | TopQuestionsResponse | GROUP BY content WHERE role='user' AND первое сообщение, LIMIT 5 |

### RAG сервисы

**processor.py**:

| Функция | Вход | Выход |
|---------|------|-------|
| `parse_document(filepath, file_type)` | str, str | str (extracted text) |
| `parse_pdf(filepath)` | str | str |
| `parse_docx(filepath)` | str | str |
| `parse_txt(filepath)` | str | str |
| `clean_text(text)` | str | str (cleaned) |
| `chunk_text(text, chunk_size=512, overlap=50)` | str, int, int | list[str] |

**embeddings.py**:

| Функция | Вход | Выход |
|---------|------|-------|
| `generate_embedding(text)` | str | list[float] (1536 dim) |
| `generate_embeddings_batch(texts)` | list[str] | list[list[float]] |

**retriever.py**:

| Функция | Вход | Выход |
|---------|------|-------|
| `search_similar_chunks(db, query_embedding, top_k=5, threshold=0.3)` | db, list[float], int, float | list[DocumentChunk] |

**generator.py**:

| Функция | Вход | Выход |
|---------|------|-------|
| `build_prompt(chunks, conversation_history, question)` | list, list, str | dict (messages for LLM) |
| `generate_answer(prompt, model)` | dict, str | str (answer text) |
| `call_claude(messages)` | dict | str |
| `call_gpt(messages)` | dict | str |

---

## 9. Все репозитории (Data Access)

В данной архитектуре **отдельный слой Repository не используется**. Вместо этого сервисы работают с SQLAlchemy ORM напрямую через `db: AsyncSession`.

**Обоснование**:
- FastAPI + SQLAlchemy async — стандартный паттерн
- Repository pattern добавляет абстракцию без реальной пользы (мы не меняем БД)
- Сервисы уже достаточно тонкие
- Тестирование: мокаем на уровне DB session (fixture с тестовой БД), а не на уровне repository

**Типичный паттерн доступа к данным в сервисе**:
```
async def get_users(db: AsyncSession, page: int, per_page: int):
    query = select(User).order_by(User.created_at.desc())
    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    users = await db.scalars(query.offset((page-1) * per_page).limit(per_page))
    return PaginatedResponse(items=users.all(), total=total, page=page, ...)
```

---

## 10. Все API (маршрутизация)

### Router Tree

```
app = FastAPI()

app.include_router(v1_router, prefix="/api/v1")

v1_router:
├── auth_router     prefix="/auth"         tags=["Auth"]
│   ├── POST /login
│   └── POST /change-password
│
├── chat_router     prefix="/conversations" tags=["Chat"]
│   ├── POST /
│   ├── GET /
│   ├── GET /{id}
│   ├── DELETE /{id}
│   └── POST /{id}/messages
│
├── document_router prefix="/documents"     tags=["Documents"]
│   ├── POST /
│   ├── GET /
│   ├── GET /{id}
│   └── DELETE /{id}
│
├── user_router     prefix="/users"         tags=["Users"]
│   ├── GET /
│   ├── POST /
│   ├── PATCH /{id}
│   ├── DELETE /{id}
│   └── PATCH /me/profile
│
├── dashboard_router prefix="/dashboard"    tags=["Dashboard"]
│   ├── GET /stats
│   ├── GET /activity
│   └── GET /top-questions
│
└── health_router   prefix="/health"        tags=["Health"]
    └── GET /
```

### Матрица авторизации

| Endpoint | Auth | Role | Ownership |
|----------|------|------|-----------|
| POST /auth/login | нет | — | — |
| POST /auth/change-password | да | any | self |
| POST /conversations | да | any | — |
| GET /conversations | да | any | self (filtered) |
| GET /conversations/{id} | да | any | owner check |
| DELETE /conversations/{id} | да | any | owner check |
| POST /conversations/{id}/messages | да | any | owner check |
| POST /documents | да | admin | — |
| GET /documents | да | admin | — |
| GET /documents/{id} | да | admin | — |
| DELETE /documents/{id} | да | admin | — |
| GET /users | да | admin | — |
| POST /users | да | admin | — |
| PATCH /users/{id} | да | admin | self-check |
| DELETE /users/{id} | да | admin | self-check |
| PATCH /users/me/profile | да | any | self |
| GET /dashboard/* | да | admin | — |
| GET /health | нет | — | — |

---

## 11. Все фоновые задачи

### Единственная фоновая задача: process_document

**Механизм**: FastAPI `BackgroundTasks` (add_task в роутере upload)

**Триггер**: POST /api/v1/documents (после сохранения файла и записи в БД)

**Последовательность**:
```
process_document_task(document_id: UUID)
    │
    ├── 1. Получить новую DB session (не из запроса — запрос уже завершен)
    ├── 2. Загрузить Document из БД
    ├── 3. Обновить status → "processing"
    ├── 4. Прочитать файл с диска (uploads/{filename})
    ├── 5. parse_document(filepath, file_type) → text
    ├── 6. clean_text(text) → cleaned_text
    ├── 7. chunk_text(cleaned_text) → chunks[]
    ├── 8. generate_embeddings_batch(chunks) → embeddings[]
    ├── 9. Для каждого chunk: INSERT INTO document_chunks
    ├── 10. Обновить document: status → "indexed", chunk_count = len(chunks)
    ├── 11. Commit
    │
    └── При ошибке на любом шаге:
        ├── Rollback
        ├── Обновить document: status → "error", error_message = str(error)
        ├── Commit
        └── Log ERROR
```

**Важные детали**:
- Новая AsyncSession создается внутри задачи (запрос-родитель уже завершился)
- Задача обрабатывает ОДИН документ
- Если backend перезапустится во время обработки — документ останется в статусе "processing" навсегда (MVP ограничение; post-MVP: periodic cleanup job)
- Embeddings batch: до 100 чанков за один вызов OpenAI API
- Retry на OpenAI API: 3 попытки, exponential backoff (1s, 2s, 4s)

---

## 12. Очереди

**В MVP очереди не используются.**

FastAPI BackgroundTasks — это не очередь, а in-process async task. Документы обрабатываются последовательно в event loop.

**Почему не очередь (Celery, RQ)**:
- MVP: один инстанс backend, нагрузка минимальная
- Celery добавляет отдельный процесс (worker), broker (Redis уже есть, но конфигурация)
- Усложняет Docker setup
- Для 500 документов и одного пользователя, загружающего их — BackgroundTasks достаточно

**Post-MVP**: переход на Celery + Redis broker, когда:
- Нужна параллельная обработка документов
- Нужен retry с persistent queue
- Несколько backend instances

---

## 13. AI Pipeline (детальная архитектура)

### Компоненты и их взаимосвязи

```
┌──────────────────────────────────────────────────────────────┐
│                    AI Pipeline                                │
│                                                              │
│  ┌─────────────┐    ┌──────────────┐    ┌────────────────┐  │
│  │  Processor   │    │  Embeddings  │    │   Retriever    │  │
│  │              │    │              │    │                │  │
│  │ parse_pdf()  │    │ OpenAI API   │    │ pgvector query │  │
│  │ parse_docx() │    │ text-emb-3   │    │ cosine sim     │  │
│  │ parse_txt()  │    │ -small       │    │ top-5          │  │
│  │ chunk_text() │    │ 1536 dim     │    │ threshold 0.3  │  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬─────────┘  │
│         │                   │                    │            │
│         │ Ingestion flow    │ Both flows         │ Query flow │
│         ▼                   ▼                    ▼            │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                      Generator                           │ │
│  │                                                          │ │
│  │  build_prompt(chunks, history, question)                  │ │
│  │  ├── System prompt (hardcoded)                            │ │
│  │  ├── Context: chunks with [Source: name] labels           │ │
│  │  ├── History: last 6 messages (3 pairs)                   │ │
│  │  └── User question                                        │ │
│  │                                                          │ │
│  │  generate_answer(prompt, model_choice)                     │ │
│  │  ├── "claude" → Anthropic API (claude-sonnet-4-20250514) │ │
│  │  └── "gpt"   → OpenAI API (gpt-4o)                       │ │
│  │                                                          │ │
│  │  Config: temperature=0.1, max_tokens=2048, timeout=60s    │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

### Tokenization

Библиотека `tiktoken` используется для:
1. Подсчета размера чанков при chunking (модель: cl100k_base)
2. Контроля размера контекстного окна при построении prompt

Почему tiktoken, а не len(text.split()):
- Токены ≠ слова (субтокены, unicode, спецсимволы)
- OpenAI embedding model и LLM считают именно токены
- Точный подсчет предотвращает превышение лимитов API

### Error Handling в AI Pipeline

| Ошибка | Действие | Результат для пользователя |
|--------|----------|---------------------------|
| OpenAI Embedding API timeout | Retry 3x (1s, 2s, 4s) | Document status = error |
| OpenAI Embedding API 429 | Retry 3x с backoff | Document status = error |
| OpenAI Embedding API 500 | Retry 3x | Document status = error |
| LLM API timeout (60s) | Retry 1x (2s backoff) | HTTP 503 |
| LLM API 429 | No retry | HTTP 503 |
| LLM API 500 | Retry 1x | HTTP 503 |
| pgvector no results | Не ошибка | AI отвечает "I don't have enough info..." |
| Empty document (0 text) | Не ошибка | Document indexed, chunk_count=0 |
| Password-protected PDF | Exception caught | Document status = error, message |

---

## 14. Последовательность обработки пользовательского запроса (chat)

```
Client                    Nginx             Backend (FastAPI)                     PostgreSQL       OpenAI API    LLM API
  │                         │                      │                                 │                │            │
  │ POST /api/v1/conver-    │                      │                                 │                │            │
  │ sations/{id}/messages   │                      │                                 │                │            │
  │ {content, model}        │                      │                                 │                │            │
  │────────────────────────→│─────────────────────→│                                 │                │            │
  │                         │                      │                                 │                │            │
  │                         │                      │ 1. Middleware chain              │                │            │
  │                         │                      │    (CORS, RequestID,             │                │            │
  │                         │                      │     RateLimit, Logging)          │                │            │
  │                         │                      │                                 │                │            │
  │                         │                      │ 2. get_current_user(token)       │                │            │
  │                         │                      │──────────────────────────────────→│ SELECT user    │            │
  │                         │                      │←──────────────────────────────────│ WHERE id=...   │            │
  │                         │                      │                                 │                │            │
  │                         │                      │ 3. Validate input (Pydantic)     │                │            │
  │                         │                      │    content: 1-4000 chars         │                │            │
  │                         │                      │    model: "claude"|"gpt"         │                │            │
  │                         │                      │                                 │                │            │
  │                         │                      │ 4. chat_service.send_message()   │                │            │
  │                         │                      │                                 │                │            │
  │                         │                      │ 4a. Load conversation            │                │            │
  │                         │                      │──────────────────────────────────→│ SELECT conv    │            │
  │                         │                      │←──────────────────────────────────│ WHERE id=...   │            │
  │                         │                      │                                 │                │            │
  │                         │                      │ 4b. Verify owner                 │                │            │
  │                         │                      │     (conv.user_id == user.id)     │                │            │
  │                         │                      │                                 │                │            │
  │                         │                      │ 4c. Check indexed documents > 0   │                │            │
  │                         │                      │──────────────────────────────────→│ SELECT count   │            │
  │                         │                      │←──────────────────────────────────│ FROM documents │            │
  │                         │                      │                                 │ WHERE indexed  │            │
  │                         │                      │                                 │                │            │
  │                         │                      │ 4d. Save user message            │                │            │
  │                         │                      │──────────────────────────────────→│ INSERT message │            │
  │                         │                      │                                 │                │            │
  │                         │                      │ 4e. Embed question               │                │            │
  │                         │                      │────────────────────────────────────────────────────→│            │
  │                         │                      │←────────────────────────────────────────────────────│ vector     │
  │                         │                      │                                 │                │            │
  │                         │                      │ 4f. Vector search (top-5)        │                │            │
  │                         │                      │──────────────────────────────────→│ SELECT chunks  │            │
  │                         │                      │←──────────────────────────────────│ ORDER BY <=>   │            │
  │                         │                      │                                 │                │            │
  │                         │                      │ 4g. Load conversation history     │                │            │
  │                         │                      │──────────────────────────────────→│ SELECT msgs    │            │
  │                         │                      │←──────────────────────────────────│ LIMIT 6        │            │
  │                         │                      │                                 │                │            │
  │                         │                      │ 4h. Build prompt                 │                │            │
  │                         │                      │     (system + context +           │                │            │
  │                         │                      │      history + question)          │                │            │
  │                         │                      │                                 │                │            │
  │                         │                      │ 4i. Call LLM                     │                │            │
  │                         │                      │──────────────────────────────────────────────────────────────────→│
  │                         │                      │←──────────────────────────────────────────────────────────────────│
  │                         │                      │                                 │                │  answer     │
  │                         │                      │                                 │                │            │
  │                         │                      │ 4j. Save assistant message       │                │            │
  │                         │                      │──────────────────────────────────→│ INSERT message │            │
  │                         │                      │                                 │ (with sources) │            │
  │                         │                      │                                 │                │            │
  │                         │                      │ 4k. Update conversation          │                │            │
  │                         │                      │──────────────────────────────────→│ UPDATE conv    │            │
  │                         │                      │                                 │ title, updated │            │
  │                         │                      │                                 │                │            │
  │                         │                      │ 4l. Commit transaction           │                │            │
  │                         │                      │──────────────────────────────────→│ COMMIT         │            │
  │                         │                      │                                 │                │            │
  │                         │                      │ 5. Return response               │                │            │
  │←────────────────────────│←─────────────────────│   200 {user_msg, asst_msg, title}│                │            │
  │                         │                      │                                 │                │            │
```

---

## 15. Последовательность обработки загрузки документа

```
Client                Backend (HTTP handler)              Background Task                PostgreSQL    OpenAI     Disk
  │                        │                                    │                            │           │          │
  │ POST /documents        │                                    │                            │           │          │
  │ (multipart/form-data)  │                                    │                            │           │          │
  │───────────────────────→│                                    │                            │           │          │
  │                        │ 1. Validate file                   │                            │           │          │
  │                        │    (type, MIME, size)               │                            │           │          │
  │                        │                                    │                            │           │          │
  │                        │ 2. Save file to disk               │                            │           │          │
  │                        │──────────────────────────────────────────────────────────────────────────────────────────→│
  │                        │                                    │                            │           │     save │
  │                        │ 3. Create DB record                │                            │           │          │
  │                        │    (status="uploaded")              │                            │           │          │
  │                        │────────────────────────────────────────────────────────────────→│ INSERT    │          │
  │                        │                                    │                            │           │          │
  │                        │ 4. Add background task             │                            │           │          │
  │                        │───────────────────────────────────→│                            │           │          │
  │                        │                                    │                            │           │          │
  │←───────────────────────│ 5. Return 201 immediately          │                            │           │          │
  │  {id, status:"uploaded"}                                    │                            │           │          │
  │                        │                                    │                            │           │          │
  │                        │                                    │ 6. status → "processing"   │           │          │
  │                        │                                    │───────────────────────────→│ UPDATE    │          │
  │                        │                                    │                            │           │          │
  │                        │                                    │ 7. Read file from disk     │           │          │
  │                        │                                    │────────────────────────────────────────────────────→│
  │                        │                                    │←────────────────────────────────────────────────────│
  │                        │                                    │                            │           │          │
  │                        │                                    │ 8. Parse (PDF/DOCX/TXT)    │           │          │
  │                        │                                    │    → extracted text         │           │          │
  │                        │                                    │                            │           │          │
  │                        │                                    │ 9. Clean + Chunk text      │           │          │
  │                        │                                    │    → chunks[]              │           │          │
  │                        │                                    │                            │           │          │
  │                        │                                    │ 10. Batch embed chunks     │           │          │
  │                        │                                    │────────────────────────────────────────→│          │
  │                        │                                    │←────────────────────────────────────────│ vectors  │
  │                        │                                    │                            │           │          │
  │                        │                                    │ 11. Insert chunks + embeds │           │          │
  │                        │                                    │───────────────────────────→│ INSERT    │          │
  │                        │                                    │                            │ chunks    │          │
  │                        │                                    │                            │           │          │
  │                        │                                    │ 12. status → "indexed"     │           │          │
  │                        │                                    │    chunk_count = N         │           │          │
  │                        │                                    │───────────────────────────→│ UPDATE    │          │
  │                        │                                    │                            │           │          │
  │ (polling GET /documents)│                                   │                            │           │          │
  │───────────────────────→│                                    │                            │           │          │
  │←───────────────────────│ status: "indexed"                  │                            │           │          │
```

Frontend: polling каждые 5 секунд (`useQuery` с `refetchInterval: 5000`) пока есть документы со статусом "processing".

---

## 16. Последовательность поиска по знаниям (RAG)

Детальный flow внутри шага 4 из раздела 14:

```
ChatService.send_message(content="How to submit vacation?", model="claude")
    │
    ▼
┌─ Step 1: Embed Question ─────────────────────────────────────────┐
│  embeddings.generate_embedding("How to submit vacation?")         │
│  → OpenAI API: POST /v1/embeddings                               │
│    model: "text-embedding-3-small"                                │
│    input: "How to submit vacation?"                               │
│  → vector: [0.023, -0.041, 0.087, ...] (1536 floats)             │
└───────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─ Step 2: Vector Search ──────────────────────────────────────────┐
│  retriever.search_similar_chunks(db, query_embedding, top_k=5)    │
│                                                                   │
│  SQL (через SQLAlchemy):                                          │
│  SELECT dc.*, d.original_name                                     │
│  FROM document_chunks dc                                          │
│  JOIN documents d ON d.id = dc.document_id                        │
│  WHERE d.status = 'indexed'                                       │
│  ORDER BY dc.embedding <=> :query_embedding                       │
│  LIMIT 5                                                          │
│                                                                   │
│  Post-filter: убрать чанки с cosine distance > 0.7                │
│  (т.е. similarity < 0.3)                                          │
│                                                                   │
│  Результат: [                                                     │
│    {content: "...", document_name: "HR Policy.pdf", score: 0.87}, │
│    {content: "...", document_name: "Vacation.docx", score: 0.72}, │
│    ...                                                            │
│  ]                                                                │
└───────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─ Step 3: Build Prompt ───────────────────────────────────────────┐
│  generator.build_prompt(chunks, history, question)                │
│                                                                   │
│  messages = [                                                     │
│    {"role": "system", "content": SYSTEM_PROMPT + chunks_text},    │
│    {"role": "user",   "content": history[0].content},  # старый  │
│    {"role": "assistant", "content": history[1].content},          │
│    {"role": "user",   "content": history[2].content},             │
│    {"role": "assistant", "content": history[3].content},          │
│    {"role": "user",   "content": history[4].content},             │
│    {"role": "assistant", "content": history[5].content},          │
│    {"role": "user",   "content": "How to submit vacation?"}       │
│  ]                                                                │
│                                                                   │
│  chunks_text:                                                     │
│  [Source: HR Policy.pdf]                                          │
│  To submit a vacation request, employees must fill out Form V-1..│
│                                                                   │
│  [Source: Vacation Policy.docx]                                   │
│  Vacation requests should be submitted 14 days in advance...     │
└───────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─ Step 4: Call LLM ───────────────────────────────────────────────┐
│  model="claude" → generator.call_claude(messages)                 │
│                                                                   │
│  Anthropic API: POST /v1/messages                                 │
│    model: "claude-sonnet-4-20250514"                             │
│    messages: [system + context + history + question]               │
│    temperature: 0.1                                               │
│    max_tokens: 2048                                               │
│    timeout: 60s                                                   │
│                                                                   │
│  Response: "To submit a vacation request, you need to fill out   │
│  Form V-1, which is available on the HR portal. According to the │
│  vacation policy, requests should be submitted at least 14 days  │
│  in advance to your direct manager..."                            │
└───────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─ Step 5: Build Sources ──────────────────────────────────────────┐
│  sources = [                                                      │
│    {                                                              │
│      "document_id": "uuid-1",                                     │
│      "document_name": "HR Policy.pdf",                            │
│      "chunk_index": 3,                                            │
│      "relevance_score": 0.87,                                     │
│      "snippet": "To submit a vacation request, employees must..." │
│    },                                                             │
│    {                                                              │
│      "document_id": "uuid-2",                                     │
│      "document_name": "Vacation Policy.docx",                     │
│      "chunk_index": 1,                                            │
│      "relevance_score": 0.72,                                     │
│      "snippet": "Vacation requests should be submitted 14 days..." │
│    }                                                              │
│  ]                                                                │
│                                                                   │
│  snippet = первые 200 символов chunk.content                      │
└───────────────────────────────────────────────────────────────────┘
```

---

## 17. Авторизация (детальная реализация)

### JWT Flow

```
┌─ Login ──────────────────────────────────────────────────────────┐
│                                                                   │
│  Client                              Backend                      │
│    │                                    │                          │
│    │ POST /auth/login                   │                          │
│    │ {email, password}                  │                          │
│    │───────────────────────────────────→│                          │
│    │                                    │ 1. SELECT user by email  │
│    │                                    │ 2. bcrypt.verify(pw)     │
│    │                                    │ 3. Check is_active       │
│    │                                    │ 4. Create JWT:           │
│    │                                    │    sub=user.id           │
│    │                                    │    email=user.email      │
│    │                                    │    role=user.role        │
│    │                                    │    exp=now()+30min       │
│    │                                    │    iat=now()             │
│    │                                    │ 5. Sign with SECRET_KEY  │
│    │←───────────────────────────────────│                          │
│    │ {access_token, user}               │                          │
│    │                                    │                          │
│    │ localStorage.setItem(             │                          │
│    │   "access_token", token)          │                          │
│    │                                    │                          │
└───────────────────────────────────────────────────────────────────┘

┌─ Authenticated Request ──────────────────────────────────────────┐
│                                                                   │
│  Client                              Backend                      │
│    │                                    │                          │
│    │ GET /conversations                 │                          │
│    │ Authorization: Bearer <token>      │                          │
│    │───────────────────────────────────→│                          │
│    │                                    │ get_current_user():      │
│    │                                    │ 1. Extract token from    │
│    │                                    │    Authorization header  │
│    │                                    │ 2. jose.decode(token,    │
│    │                                    │    SECRET_KEY, HS256)    │
│    │                                    │ 3. Extract sub (user_id) │
│    │                                    │ 4. SELECT user WHERE     │
│    │                                    │    id=user_id AND        │
│    │                                    │    is_active=true        │
│    │                                    │ 5. If not found → 401   │
│    │                                    │ 6. Return User object    │
│    │←───────────────────────────────────│                          │
│    │ 200 {conversations}                │                          │
└───────────────────────────────────────────────────────────────────┘

┌─ Token Expiration ───────────────────────────────────────────────┐
│                                                                   │
│  Client                              Backend                      │
│    │                                    │                          │
│    │ Any request with expired token     │                          │
│    │───────────────────────────────────→│                          │
│    │                                    │ jose.decode() → expired  │
│    │←───────────────────────────────────│                          │
│    │ 401 {"detail": "Not authenticated"}│                          │
│    │                                    │                          │
│    │ Axios interceptor:                 │                          │
│    │ 1. localStorage.removeItem(token)  │                          │
│    │ 2. redirect("/login")             │                          │
│    │ 3. toast("Session expired")       │                          │
└───────────────────────────────────────────────────────────────────┘
```

---

## 18. Структура директорий

Полное дерево — см. PRD раздел 35. Здесь описываю только архитектурно значимые решения.

### Backend: почему так организовано

```
backend/app/
├── api/v1/          # Versioned API — возможность добавить v2 без ломающих изменений
├── models/          # Отдельно от schemas — разделение DB concern и HTTP concern
├── schemas/         # Pydantic отдельно от SQLAlchemy — можно менять API не трогая БД
├── services/        # Бизнес-логика отдельно от роутеров — тестируемость
│   └── rag/         # RAG как sub-package — логически сгруппирован, легко выделить в микросервис
├── core/            # Инфраструктура, не привязанная к домену
└── tasks/           # Фоновые задачи отделены — ясная граница sync/async
```

### Frontend: почему так организовано

```
frontend/src/
├── api/             # API вызовы отделены от UI — переиспользуемость, тестируемость
├── components/      # По фичам, не по типу (chat/, documents/ вместо buttons/, forms/)
│   ├── ui/          # shadcn компоненты — стандартная конвенция shadcn/ui
│   └── layout/      # Layout компоненты — общие для всех страниц
├── pages/           # 1:1 с URL маршрутами — легко найти
├── hooks/           # React Query hooks — кеш логика отделена от UI
├── contexts/        # Глобальное состояние (только Auth) — минимум глобального стейта
├── lib/             # Утилиты — чистые функции без побочных эффектов
└── types/           # TypeScript типы — единый source of truth для типов
```

---

## 19. Назначение каждого файла

### Backend

| Файл | Назначение |
|------|-----------|
| `app/main.py` | Создание FastAPI app, подключение middleware (CORS, RequestID, Logging), подключение роутеров, lifespan handler (создание initial admin при старте) |
| `app/config.py` | Pydantic BaseSettings — чтение всех env переменных с типизацией и default-ами. Единый источник конфигурации |
| `app/database.py` | Создание async engine (create_async_engine), async session factory (async_sessionmaker), dependency function get_db() |
| `app/api/deps.py` | FastAPI dependencies: get_db (session per request), get_current_user (JWT → User), require_admin (role check) |
| `app/api/v1/router.py` | Главный роутер v1 — включает все sub-routers с prefix и tags |
| `app/api/v1/auth.py` | Роутеры: POST /login (валидация, вызов auth_service, формирование JWT response), POST /change-password |
| `app/api/v1/chat.py` | Роутеры: CRUD conversations + POST messages (вызов chat_service.send_message) |
| `app/api/v1/documents.py` | Роутеры: POST upload (multipart, валидация файла), GET list, GET by id, DELETE |
| `app/api/v1/users.py` | Роутеры: CRUD users + PATCH me/profile |
| `app/api/v1/dashboard.py` | Роутеры: GET stats, GET activity, GET top-questions |
| `app/api/v1/health.py` | Роутер: GET /health — проверка DB (SELECT 1), Redis (PING), наличие API keys |
| `app/models/base.py` | DeclarativeBase с общими mapped columns (id UUID, created_at, updated_at) + event listener для auto-update updated_at |
| `app/models/user.py` | SQLAlchemy model User — поля, relationships (conversations, documents), table constraints |
| `app/models/conversation.py` | SQLAlchemy model Conversation — поля, relationship messages, indexes |
| `app/models/message.py` | SQLAlchemy model Message — поля, JSONB sources |
| `app/models/document.py` | SQLAlchemy model Document — поля, relationship chunks, status enum |
| `app/models/document_chunk.py` | SQLAlchemy model DocumentChunk — поля, Vector(1536) type, HNSW index |
| `app/schemas/auth.py` | Pydantic: LoginRequest, LoginResponse, ChangePasswordRequest |
| `app/schemas/chat.py` | Pydantic: ConversationResponse, ConversationListItem, MessageCreate, MessageResponse, SendMessageResponse |
| `app/schemas/document.py` | Pydantic: DocumentResponse, DocumentListResponse |
| `app/schemas/user.py` | Pydantic: UserCreate, UserUpdate, UserResponse, UserWithPassword |
| `app/schemas/dashboard.py` | Pydantic: StatsResponse, ActivityResponse, TopQuestionsResponse |
| `app/schemas/common.py` | Pydantic: PaginatedResponse[T] (generic) |
| `app/services/auth_service.py` | Бизнес-логика: authenticate (email/pw → user), change_password, create_initial_admin |
| `app/services/chat_service.py` | Бизнес-логика: CRUD conversations, send_message (оркестрация RAG pipeline) |
| `app/services/document_service.py` | Бизнес-логика: upload (save file, create DB record, trigger background), list, delete (remove file + DB) |
| `app/services/user_service.py` | Бизнес-логика: CRUD users с защитными проверками (self-edit, last admin) |
| `app/services/dashboard_service.py` | Бизнес-логика: SQL агрегации для статистики, activity, top questions |
| `app/services/rag/processor.py` | Парсинг документов (PDF, DOCX, TXT), очистка текста, чанкинг (512 tokens, 50 overlap) |
| `app/services/rag/embeddings.py` | Обертка над OpenAI Embeddings API: single embed, batch embed, retry logic |
| `app/services/rag/retriever.py` | pgvector search: cosine similarity query, threshold filtering, source metadata |
| `app/services/rag/generator.py` | Построение prompt (system + context + history + question), вызов Claude/GPT API, retry |
| `app/core/security.py` | JWT: create_access_token, verify_token. Password: hash_password, verify_password (bcrypt). generate_temp_password |
| `app/core/exceptions.py` | Кастомные exception classes (AppException, NotFoundError, ForbiddenError, ConflictError) + FastAPI exception_handlers |
| `app/core/logging.py` | Настройка structlog: processors, JSON renderer, request_id context variable, logging middleware |
| `app/tasks/document_tasks.py` | Background task: process_document (parse → chunk → embed → store). Создает свою DB session |
| `alembic/env.py` | Настройка Alembic для async SQLAlchemy: target_metadata, async engine |
| `alembic/versions/001_initial.py` | Начальная миграция: pgvector extension + все 5 таблиц + все индексы |
| `tests/conftest.py` | Fixtures: тестовая БД, test client, auth tokens, sample data |

### Frontend

| Файл | Назначение |
|------|-----------|
| `src/main.tsx` | Entry point: ReactDOM.createRoot, обертка провайдерами |
| `src/App.tsx` | Routing: BrowserRouter, Routes, layout routes |
| `src/api/client.ts` | Axios instance: baseURL, request interceptor (auth header), response interceptor (401 → logout) |
| `src/api/auth.ts` | API: login(email, pw) → {token, user}, changePassword(old, new, confirm) |
| `src/api/chat.ts` | API: getConversations, createConversation, getConversation, deleteConversation, sendMessage |
| `src/api/documents.ts` | API: uploadDocument(file), getDocuments(status, page), deleteDocument(id) |
| `src/api/users.ts` | API: getUsers, createUser, updateUser, deleteUser, updateProfile |
| `src/api/dashboard.ts` | API: getStats(period), getActivity(period), getTopQuestions() |
| `src/contexts/AuthContext.tsx` | React Context: token storage, user state, login/logout functions, isAdmin computed |
| `src/hooks/useAuth.ts` | Hook: useAuth() → {user, isAdmin, login, logout, isAuthenticated} |
| `src/hooks/useConversations.ts` | React Query: useConversations(search), useCreateConversation, useDeleteConversation |
| `src/hooks/useMessages.ts` | React Query: useConversation(id), useSendMessage |
| `src/hooks/useDocuments.ts` | React Query: useDocuments(status, page), useUploadDocument, useDeleteDocument |
| `src/hooks/useUsers.ts` | React Query: useUsers(page), useCreateUser, useUpdateUser, useDeleteUser |
| `src/hooks/useDashboard.ts` | React Query: useStats(period), useActivity(period), useTopQuestions |
| `src/components/layout/ProtectedRoute.tsx` | Route guard: redirect to /login if not authed, /change-password if must_change, /chat if not admin |
| `src/components/layout/AppLayout.tsx` | Layout: Sidebar (nav) + Outlet (content area) |
| `src/components/layout/Sidebar.tsx` | Navigation sidebar for non-chat pages: logo, nav links, user menu |
| `src/lib/utils.ts` | Utilities: cn (clsx+tailwind-merge), formatDate, formatFileSize, truncate |
| `src/lib/constants.ts` | Constants: MAX_MESSAGE_LENGTH=4000, MODELS, POLLING_INTERVAL=5000 |
| `src/types/index.ts` | TypeScript interfaces: User, Conversation, Message, Document, Source, etc. |

---

## 20. Используемые паттерны проектирования

| Паттерн | Где используется | Как реализован |
|---------|-----------------|----------------|
| **Layered Architecture** | Весь backend | API → Service → Model. Каждый слой зависит только от слоя ниже |
| **Dependency Injection** | FastAPI Depends | get_db, get_current_user, require_admin — инъектируются в роутеры |
| **Repository Pattern (implicit)** | Сервисы | Нет отдельных классов, но SQLAlchemy session абстрагирует доступ к данным |
| **Strategy** | RAG Generator | model="claude" → call_claude(), model="gpt" → call_gpt(). Одинаковый интерфейс, разные реализации |
| **Pipeline** | RAG | embed → search → build_prompt → generate → save. Каждый шаг — функция с входом и выходом |
| **Observer (React Query)** | Frontend | useQuery подписывается на данные, автоматически обновляет UI при invalidation |
| **Provider** | Frontend React | AuthProvider, QueryClientProvider, Toaster — предоставляют контекст дочерним компонентам |
| **Guard** | ProtectedRoute | Проверяет условия (auth, role, must_change_password) и решает: рендерить children или redirect |
| **Adapter** | api/client.ts | Axios adapter — единая точка конфигурации HTTP клиента (headers, interceptors, baseURL) |
| **Builder** | build_prompt() | Пошагово собирает промпт из частей (system, context, history, question) |
| **Background Task** | document_tasks.py | Асинхронная обработка документа после HTTP ответа (fire-and-forget) |
| **Soft Delete** | Conversations | is_deleted flag вместо физического удаления — данные сохраняются |
| **DTO (Data Transfer Object)** | Pydantic schemas | Отделяют формат API от внутренней модели данных |
| **Singleton** | Config, Engine | Pydantic Settings создается один раз, SQLAlchemy Engine — один на процесс |

---

## 21. Обоснование каждого архитектурного решения

### Почему монолит, а не микросервисы?
- Один продукт, один деплой, один репозиторий
- Нет требований к независимому масштабированию
- Проще для портфолио: `docker-compose up` и все работает
- RAG pipeline тесно интегрирован с Chat и Documents — разделение создаст overhead
- Можно выделить RAG в сервис позже без переписывания

### Почему FastAPI, а не Django/Flask?
- Async native — нужен для вызовов LLM API (10+ секунд)
- Automatic Swagger — бесплатная API документация
- Pydantic v2 — валидация и сериализация из коробки
- Type hints — IDE поддержка, самодокументирующийся код
- Высокая производительность (ASGI, uvicorn)

### Почему SQLAlchemy async, а не sync?
- FastAPI async — синхронная БД блокировала бы event loop
- asyncpg — самый быстрый PostgreSQL драйвер для Python
- Один event loop для HTTP + DB + external API — нет thread overhead

### Почему PostgreSQL + pgvector, а не отдельный vector DB (Pinecone, Qdrant)?
- Одна БД вместо двух — проще деплой, проще бекапы
- pgvector HNSW — production-ready для 100k-1M vectors
- Нет vendor lock-in (Pinecone — SaaS)
- JOIN между chunks и documents без межсервисного вызова
- Для MVP объем данных (до 100k vectors) — pgvector более чем достаточно

### Почему Redis в MVP, если нет кеша и нет очередей?
- slowapi (rate limiting) использует Redis как backend
- Redis уже нужен для production rate limiting
- Готовность к post-MVP: кеш, Celery broker
- Минимальный footprint (redis:7-alpine ~30MB RAM)

### Почему React Query, а не Redux/Zustand для серверного стейта?
- React Query спроектирован для серверного состояния (cache, invalidation, refetch)
- Redux требует ручного управления loading/error/data для каждого запроса
- Автоматический refetch при window focus — актуальные данные
- Declarative: useQuery вместо dispatch/action/reducer
- Zustand остается опцией для UI state, но в MVP не нужен (хватает useState + Context)

### Почему JWT без Refresh Token в MVP?
- Простота: один токен, один механизм
- 30 минут — достаточно для сессии (корпоративный продукт, не мобильное приложение)
- Refresh token добавляет: отдельный endpoint, хранение в HttpOnly cookie, rotation logic
- Post-MVP: добавить refresh token когда пользователи попросят "не разлогинивать каждые 30 минут"

### Почему файлы на диске, а не S3?
- MVP: один сервер, docker volume — достаточно
- S3 добавляет: зависимость от облака, IAM, presigned URLs, CORS для upload
- Docker volume: бекап через docker volume backup, восстановление простое
- Post-MVP: переход на S3/MinIO когда нужно горизонтальное масштабирование или >100GB файлов

### Почему BackgroundTasks, а не Celery?
- FastAPI BackgroundTasks — zero config, работает в том же процессе
- Celery: отдельный worker process, broker config, result backend
- Для MVP (один instance, последовательная обработка документов) — достаточно
- Post-MVP: Celery когда нужна параллельная обработка или persistent retry queue

### Почему text-embedding-3-small, а не text-embedding-3-large?
- small: 1536 dimensions, $0.02/1M tokens — в 5 раз дешевле large
- Для корпоративной документации разница в качестве минимальна (benchmark: <2% по MTEB)
- Меньший вектор — быстрее HNSW поиск, меньше storage
- Post-MVP: switch to large если качество поиска неудовлетворительное

### Почему HNSW индекс, а не IVFFlat?
- HNSW: лучше recall при том же размере данных
- HNSW: не требует training (IVFFlat нужен для кластеров)
- HNSW: стабильная производительность при INSERT (IVFFlat деградирует без re-training)
- Для MVP объемов (до 100k vectors) HNSW — оптимальный выбор
- m=16, ef_construction=64 — баланс speed/recall для <1M vectors

### Почему sonner, а не react-hot-toast?
- sonner: из shadcn/ui ecosystem (стилистически совместим)
- API совместим: toast.success(), toast.error()
- Animations из коробки, customizable
- shadcn/ui documentation рекомендует sonner

### Почему Nginx как reverse proxy?
- Стандарт индустрии для production Python apps
- Статические файлы: Nginx отдает статику в 10-100x быстрее чем Python
- Security headers: удобнее настроить в одном месте
- SPA routing: try_files → index.html
- Rate limiting (дополнительный уровень), file upload size limit
- Post-MVP: SSL termination (Let's Encrypt + certbot)

---

**Конец TDD-01: AI Support Agent v1.0**

Этот документ описывает архитектурные решения и их обоснования.
Используется совместно с PRD-01 v2.0 (источник требований).
Код не написан. Документ готов к реализации.
