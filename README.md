# AI Support Agent

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-6-3178C6?logo=typescript&logoColor=white)](https://typescriptlang.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Enterprise-grade AI assistant platform that enables companies to build internal knowledge bases and provide intelligent support to employees. Upload company documents, and the AI answers questions using RAG (Retrieval-Augmented Generation) with source citations.

![AI Support Agent](screenshots/preview.png)

## Features

- **AI Chat with RAG** — Ask questions in natural language and get answers grounded in your company's documents with source citations
- **Multi-Model Support** — Choose between Claude (Anthropic) and GPT (OpenAI) for answer generation
- **Document Management** — Upload PDF, DOCX, and TXT files with automatic processing, chunking, and vector indexing
- **Conversation History** — Full conversation persistence with search, soft delete, and context-aware follow-ups
- **Admin Dashboard** — Real-time analytics: user stats, question activity charts, top questions, document status
- **User Management** — Role-based access control (Admin/User), user CRUD, temporary password generation
- **Rate Limiting** — Redis-backed request throttling with per-user and per-IP limits
- **Health Monitoring** — System health endpoint checking database, Redis, and AI provider connectivity

## Screenshots

| Login | Chat | Dashboard |
|:---:|:---:|:---:|
| ![Login](screenshots/login.png) | ![Chat](screenshots/chat.png) | ![Dashboard](screenshots/dashboard.png) |

| Documents | Users | Settings |
|:---:|:---:|:---:|
| ![Documents](screenshots/documents.png) | ![Users](screenshots/users.png) | ![Settings](screenshots/settings.png) |

## Tech Stack

### Backend
| Technology | Purpose |
|-----------|---------|
| Python 3.13 | Runtime |
| FastAPI | Web framework |
| SQLAlchemy 2.0 | Async ORM |
| Alembic | Database migrations |
| PostgreSQL 16 + pgvector | Database with vector search |
| Redis | Rate limiting & caching |
| Pydantic v2 | Data validation |
| JWT (python-jose) | Authentication |
| tiktoken | Token counting for chunking |
| structlog | Structured JSON logging |

### Frontend
| Technology | Purpose |
|-----------|---------|
| React 19 | UI library |
| TypeScript 6 | Type safety |
| Vite | Build tool |
| TailwindCSS v4 | Styling |
| shadcn/ui | Component library |
| React Query (TanStack) | Server state management |
| React Router v7 | Client-side routing |
| Recharts | Dashboard charts |
| react-markdown | Markdown rendering |

### Infrastructure
| Technology | Purpose |
|-----------|---------|
| Docker & Docker Compose | Containerization |
| Nginx | Reverse proxy & static serving |
| GitHub Actions | CI/CD pipeline |

## Architecture

```
┌─────────────────────────────────────────────────┐
│                    Nginx                         │
│            Reverse Proxy + TLS                   │
├────────────────────┬────────────────────────────┤
│                    │                             │
│   Frontend (SPA)   │      Backend (API)          │
│   React + Vite     │      FastAPI + Uvicorn      │
│   Port 3000        │      Port 8000              │
│                    │                             │
│                    │   ┌──────────────────────┐  │
│                    │   │    RAG Pipeline       │  │
│                    │   │  Parse → Chunk →      │  │
│                    │   │  Embed → Search →     │  │
│                    │   │  Generate             │  │
│                    │   └──────────────────────┘  │
│                    │                             │
├────────────────────┴────────────────────────────┤
│                                                  │
│   PostgreSQL 16          Redis 7                 │
│   + pgvector             Rate Limiting           │
│   Vector Search (HNSW)   Session Cache           │
│                                                  │
└─────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- OpenAI API key (for embeddings)
- Anthropic API key and/or OpenAI API key (for chat)

### 1. Clone and configure

```bash
git clone https://github.com/yourusername/ai-support-agent.git
cd ai-support-agent
cp .env.example .env
```

Edit `.env` and set your API keys and secrets:

```env
SECRET_KEY=your-random-32-char-secret-key
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
ADMIN_EMAIL=admin@yourcompany.com
ADMIN_DEFAULT_PASSWORD=YourSecurePassword123
POSTGRES_PASSWORD=your-db-password
```

### 2. Launch

```bash
docker compose up -d
```

### 3. Access

| Service | URL |
|---------|-----|
| Application | http://localhost |
| API Documentation | http://localhost/docs |
| Health Check | http://localhost/api/v1/health |

Default admin credentials are set in `.env`. You will be prompted to change the password on first login.

## API Documentation

Full interactive API documentation is available at `/docs` (Swagger UI) when the application is running.

### Endpoints Overview

| Group | Endpoints | Auth |
|-------|-----------|------|
| **Health** | `GET /api/v1/health` | Public |
| **Auth** | `POST /login`, `POST /change-password` | Public / User |
| **Chat** | CRUD conversations, send messages | User |
| **Documents** | Upload, list, delete documents | Admin |
| **Users** | CRUD users, update profile | Admin / User |
| **Dashboard** | Stats, activity, top questions | Admin |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://postgres:postgres@postgres:5432/ai_support_agent` |
| `REDIS_URL` | Redis connection string | `redis://redis:6379/0` |
| `SECRET_KEY` | JWT signing key (min 32 chars) | **Required** |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token lifetime | `30` |
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude | — |
| `OPENAI_API_KEY` | OpenAI API key for GPT & embeddings | — |
| `ADMIN_EMAIL` | Initial admin email | `admin@company.com` |
| `ADMIN_DEFAULT_PASSWORD` | Initial admin password | **Required** |
| `MAX_FILE_SIZE` | Max upload size in bytes | `52428800` (50MB) |
| `LOG_LEVEL` | Logging level | `INFO` |

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/v1/          # Route handlers (auth, chat, documents, users, dashboard, health)
│   │   ├── core/            # Security, logging, exceptions, rate limiting
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── services/        # Business logic layer
│   │   │   └── rag/         # RAG pipeline (processor, embeddings, retriever, generator)
│   │   └── tasks/           # Background tasks (document processing)
│   ├── alembic/             # Database migrations
│   ├── tests/               # Pytest test suite
│   └── scripts/             # Seed data and utilities
├── frontend/
│   └── src/
│       ├── api/             # Axios API client functions
│       ├── components/      # React components (chat, layout, ui)
│       ├── contexts/        # Auth context provider
│       ├── hooks/           # React Query hooks
│       ├── pages/           # Page components
│       ├── types/           # TypeScript type definitions
│       └── lib/             # Utilities and constants
├── docker/
│   └── nginx/               # Nginx configuration
├── .github/workflows/       # CI/CD pipelines
├── docker-compose.yml
└── .env.example
```

## Development

### Backend (local)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

# Start PostgreSQL and Redis (via Docker)
docker compose up -d postgres redis

# Run migrations
alembic upgrade head

# Seed demo data
python -m scripts.seed

# Start server
uvicorn app.main:app --reload --port 8000
```

### Frontend (local)

```bash
cd frontend
npm install
npm run dev    # http://localhost:5173
```

### Linting

```bash
# Backend
ruff check backend/

# Frontend
cd frontend && npx eslint src/
npx tsc --noEmit
```

## Testing

```bash
cd backend
pytest tests/ -v
```

42 tests covering authentication, user management, chat, documents, dashboard, and RAG utilities.

```
tests/test_auth.py       ✓ Login, change password, error handling
tests/test_users.py      ✓ CRUD, role changes, self-protection
tests/test_chat.py       ✓ Conversations, messages, access control
tests/test_documents.py  ✓ Upload, list, delete, authorization
tests/test_dashboard.py  ✓ Stats, activity, top questions
tests/test_rag.py        ✓ Text processing, chunking, security utils
```

## RAG Pipeline

```
Document Upload → Parse (PDF/DOCX/TXT)
                → Clean Text (normalize, remove artifacts)
                → Chunk (tiktoken, 512 tokens, 50 overlap)
                → Embed (OpenAI text-embedding-3-small, 1536d)
                → Store (pgvector HNSW index)

User Question  → Embed Query
               → Vector Search (cosine similarity, top 5)
               → Build Prompt (system + context + history)
               → Generate Answer (Claude / GPT)
               → Return with Source Citations
```

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
