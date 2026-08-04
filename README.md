<div align="center">

# AI Support Agent

### Enterprise AI Assistant with RAG & Knowledge Base

[![CI/CD](https://github.com/AndrewSheff/ai-support-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/AndrewSheff/ai-support-agent/actions)
[![Python 3.13](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React 19](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![TypeScript 6](https://img.shields.io/badge/TypeScript-6-3178C6?logo=typescript&logoColor=white)](https://typescriptlang.org)
[![PostgreSQL 16](https://img.shields.io/badge/PostgreSQL-16+pgvector-4169E1?logo=postgresql&logoColor=white)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Turn your company documents into an intelligent AI assistant.**
Upload PDFs, DOCX, and TXT files — the AI answers employee questions with cited sources using RAG.

[Quick Start](#-quick-start) &bull; [Features](#-features) &bull; [Architecture](#-architecture) &bull; [API](#-api-documentation) &bull; [Demo](#-demo)

</div>

---

## The Problem

> Companies lose **5+ hours per week per employee** searching for information across internal wikis, shared drives, and Slack channels. New hires take weeks to get up to speed. Support teams answer the same questions repeatedly.

**AI Support Agent** solves this by creating a single AI-powered knowledge base that instantly answers questions using your actual company documents — with source citations, so employees can trust and verify the answers.

---

## Screenshots

| Login | AI Chat with Sources |
|:---:|:---:|
| ![Login](screenshots/login.png) | ![Chat](screenshots/chat.png) |

| Admin Dashboard | Document Management |
|:---:|:---:|
| ![Dashboard](screenshots/dashboard.png) | ![Documents](screenshots/documents.png) |

| User Management | Settings |
|:---:|:---:|
| ![Users](screenshots/users.png) | ![Settings](screenshots/settings.png) |

---

## Key Features

### AI Chat with RAG
Ask questions in natural language. The AI searches through your documents, finds relevant passages, and generates accurate answers with clickable source citations. Supports multi-turn conversations with context awareness.

### Multi-Model Support
Choose between **Claude** (Anthropic) and **GPT** (OpenAI) for answer generation. Embeddings powered by OpenAI `text-embedding-3-small` (1536 dimensions) with pgvector HNSW indexing.

### Document Pipeline
Upload PDF, DOCX, and TXT files. Automatic processing pipeline: parse text, normalize Unicode, chunk into 512-token segments (50-token overlap via tiktoken), generate embeddings, store in PostgreSQL with vector index.

### Admin Dashboard
Real-time analytics: total users, documents, conversations. Question activity charts (7d/30d), top-5 most asked questions, document processing status monitoring.

### Enterprise Security
JWT authentication with bcrypt password hashing. Role-based access control (Admin/User). Redis-backed rate limiting. Security headers via Nginx. Password complexity validation. Temporary password generation for new users with forced change on first login.

### Production Infrastructure
Multi-stage Docker builds, Nginx reverse proxy with gzip and security headers, Alembic database migrations, structured JSON logging with request tracing, comprehensive health checks, CI/CD via GitHub Actions.

---

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                      Nginx                            │
│              Reverse Proxy + Headers                  │
├──────────────────────┬───────────────────────────────┤
│    Frontend (SPA)    │        Backend (API)           │
│    React 19 + Vite   │     FastAPI + Uvicorn          │
│    TailwindCSS v4    │     SQLAlchemy 2.0 (async)     │
│                      │                                │
│  8 pages             │   ┌────────────────────────┐   │
│  React Query cache   │   │     RAG Pipeline        │   │
│  Axios + JWT         │   │  Parse → Chunk → Embed  │   │
│                      │   │  Search → Generate      │   │
│                      │   └────────────────────────┘   │
├──────────────────────┴───────────────────────────────┤
│   PostgreSQL 16 + pgvector       Redis 7              │
│   Vector Search (HNSW)           Rate Limiting        │
│   5 models, Alembic migrations   Session Cache        │
└──────────────────────────────────────────────────────┘
```

### RAG Pipeline

```
Document Upload ─→ Parse (PDF/DOCX/TXT)
                ─→ Clean (Unicode NFC, remove artifacts)
                ─→ Chunk (tiktoken cl100k_base, 512 tokens, 50 overlap)
                ─→ Embed (OpenAI text-embedding-3-small, 1536d)
                ─→ Store (pgvector HNSW index)

User Question  ─→ Embed query
               ─→ Vector search (cosine similarity, top-5)
               ─→ Build prompt (system + context + last 6 messages)
               ─→ Generate answer (Claude / GPT)
               ─→ Return with source citations
```

---

## Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Backend** | Python, FastAPI, SQLAlchemy (async), Alembic | 3.13, 0.115, 2.0 |
| **Frontend** | React, TypeScript, Vite, TailwindCSS, shadcn/ui | 19, 6.0, 8, v4 |
| **Database** | PostgreSQL + pgvector (HNSW) | 16 |
| **Cache** | Redis | 7 |
| **AI** | Anthropic Claude, OpenAI GPT + Embeddings | Latest |
| **Auth** | JWT (python-jose) + bcrypt | HS256 |
| **Infra** | Docker Compose, Nginx, GitHub Actions | Multi-stage |
| **Logging** | structlog (JSON) | Request tracing |
| **Testing** | Pytest (async), 42 tests | 6 test files |

---

## Quick Start

### Prerequisites
- Docker & Docker Compose
- OpenAI API key (for embeddings)
- Anthropic and/or OpenAI API key (for chat)

### 1. Clone and configure

```bash
git clone https://github.com/AndrewSheff/ai-support-agent.git
cd ai-support-agent
cp .env.example .env
```

Edit `.env`:

```env
SECRET_KEY=your-random-32-char-secret-key-here
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
ADMIN_EMAIL=admin@yourcompany.com
ADMIN_DEFAULT_PASSWORD=SecurePass123
POSTGRES_PASSWORD=strong-db-password
```

### 2. Launch

```bash
docker compose up -d
```

### 3. Access

| Service | URL |
|---------|-----|
| Application | http://localhost |
| API Docs (Swagger) | http://localhost/docs |
| Health Check | http://localhost/api/v1/health |

Login with admin credentials from `.env`. You'll be prompted to change the password on first login.

### 4. Upload documents

Go to **Documents** tab, upload your PDF/DOCX/TXT files. The system automatically processes, chunks, and indexes them. Once status shows "Indexed" — start asking questions in the Chat.

---

## API Documentation

Interactive Swagger documentation at `/docs`. Key endpoints:

| Group | Endpoints | Auth | Description |
|-------|-----------|------|-------------|
| **Health** | `GET /health` | Public | System status with DB, Redis, AI checks |
| **Auth** | `POST /login`, `POST /change-password` | Public / User | JWT authentication |
| **Chat** | 5 endpoints | User | Conversations CRUD + RAG messages |
| **Documents** | 4 endpoints | Admin | Upload, list, detail, delete |
| **Users** | 5 endpoints | Admin / User | User CRUD + profile |
| **Dashboard** | 3 endpoints | Admin | Stats, activity charts, top questions |

**Total: 22 API endpoints**, all with Pydantic v2 validation, structured error responses, and rate limiting.

---

## Development

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

# Start dependencies
docker compose up -d postgres redis

# Run migrations & seed
alembic upgrade head
python -m scripts.seed

# Start dev server
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev    # http://localhost:5173
```

### Testing

```bash
cd backend && pytest tests/ -v
```

42 tests across 6 files covering auth, users, chat, documents, dashboard, and RAG utilities.

### Linting

```bash
ruff check backend/             # Python
cd frontend && npx eslint src/  # TypeScript
npx tsc --noEmit                # Type check
```

---

## Project Structure

```
ai-support-agent/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # REST endpoints (6 routers)
│   │   ├── core/            # Security, logging, exceptions, rate limiting
│   │   ├── models/          # SQLAlchemy models (5 entities)
│   │   ├── schemas/         # Pydantic v2 request/response schemas
│   │   ├── services/        # Business logic layer
│   │   │   └── rag/         # RAG pipeline (processor, embeddings, retriever, generator)
│   │   └── tasks/           # Background document processing
│   ├── alembic/             # Database migrations
│   ├── tests/               # 42 pytest tests
│   ├── Dockerfile           # Multi-stage, security-hardened
│   └── entrypoint.sh        # Migrations + server startup
├── frontend/
│   └── src/
│       ├── api/             # Axios clients with JWT interceptor
│       ├── components/      # React components (chat, dashboard, layout, ui)
│       ├── contexts/        # Auth context provider
│       ├── hooks/           # React Query custom hooks
│       ├── pages/           # 8 page components
│       └── types/           # TypeScript interfaces
├── docker/nginx/            # Nginx reverse proxy config
├── .github/workflows/       # CI (lint+test+build) + CD (GHCR push)
├── docker-compose.yml       # 5 services with health checks
└── .env.example
```

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | — | JWT signing key (min 32 chars) |
| `ADMIN_DEFAULT_PASSWORD` | Yes | — | Initial admin password |
| `OPENAI_API_KEY` | Yes | — | For embeddings + optional chat |
| `ANTHROPIC_API_KEY` | No | — | For Claude chat (recommended) |
| `DATABASE_URL` | No | Auto-configured | PostgreSQL async connection |
| `REDIS_URL` | No | Auto-configured | Redis connection |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `30` | JWT lifetime |
| `MAX_FILE_SIZE` | No | `52428800` | Upload limit (50 MB) |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity |

---

## License

[MIT](LICENSE) — free for commercial use.
