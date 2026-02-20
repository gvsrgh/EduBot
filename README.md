# EduBot+ — AI University Assistant

> Intelligent chatbot for university students powered by LangGraph agents, multi-LLM support, and a RAG knowledge base.

---

## 📋 Project Status

> Last updated: February 2026 — tracked against the published paper (IC-ECBE 2026: *EduBot+: An NLP-Powered Chatbot for Multi-Domain Student Support*).

### Legend
| Badge | Meaning |
|---|---|
| ✅ Done | Fully implemented and working |
| ⚠️ Partial | Implemented but incomplete or simplified |
| ❌ Pending | Not yet implemented |

---

### 🤖 LLM & AI

| # | Feature | Status | Notes |
|---|---|---|---|
| 1 | Multi-LLM Provider Support (GPT-4, Gemini, Ollama, **DeepSeek**) | ✅ | OpenAI, Gemini, Ollama, DeepSeek fully wired with `auto` fallback chain. Paper specifies GPT-4, Gemini, Ollama. |
| 2 | Agent-based Architecture (LangGraph) | ✅ | `StateGraph` + tool nodes in `graph.py`. Paper: ReAct-inspired autonomous decision cycle. |
| 3 | Retrieval-Augmented Generation (RAG) | ✅ | Vector embeddings via `all-MiniLM-L6-v2` + Qdrant Cloud cosine similarity retrieval (top-k=5, threshold ≥ 0.70). |
| 4 | Semantic Similarity Search | ✅ | Qdrant Cloud vector DB. 800-char chunks with 10% overlap, `search_all_domains` tool for cross-domain queries. |
| 5 | Domain-aware Query Routing | ⚠️ | Routes to Academic / Administrative / Educational. Paper defines **3 domains: Administrative, Financial, Educational** — Financial is missing as a standalone domain. |
| 6 | Multi-hop Reasoning | ❌ | Not implemented. Paper: parallel retrieval across domains + result aggregation (e.g. "refund policy if I drop a course"). |

---

### 📄 Document Management

| # | Feature | Status | Notes |
|---|---|---|---|
| 7 | Faculty Document Upload | ⚠️ | Only `.txt`. Paper requires **PDF, DOCX, TXT**. Scanned PDFs need OCR (Tesseract / Azure CV). |
| 8 | Document Processing → Vector Embeddings | ✅ | Upload → 800-char chunks (10% overlap) → embed with `all-MiniLM-L6-v2` → store in Qdrant Cloud. Implemented in `vector_store.py`. |
| 9 | Automatic Document Indexing | ✅ | On upload: auto-indexed into Qdrant. On startup: existing `data/` files seeded via `seed_existing_documents()`. |

---

### ⚙️ Backend

| # | Feature | Status | Notes |
|---|---|---|---|
| 10 | FastAPI Backend | ✅ | Async routers, middleware, dependency injection fully implemented. |
| 11 | PostgreSQL Database | ✅ | PostgreSQL + Asyncpg + SQLAlchemy ORM fully configured. |
| 12 | Conversation History | ⚠️ | Messages saved to DB per chat. Paper requires **LangGraph PostgreSQL checkpoints** so sessions restore seamlessly across logins. |

---

### 🔐 Authentication

| # | Feature | Status | Notes |
|---|---|---|---|
| 13 | OTP Authentication | ✅ | Email OTP via SMTP. Paper: code expires after login or 10 min. Guest mode (no account) also supported. |
| 14 | JWT Token Security | ✅ | HS256 JWT, configurable expiry via `.env`. |
| 15 | Role-based Access Control | ✅ | Admin: `@pvpsiddhartha.ac.in`. Student: `@pvpsit.ac.in`. Guest: read-only chat. |

---

### 🖥️ Frontend

| # | Feature | Status | Notes |
|---|---|---|---|
| 16 | Next.js Responsive Web Interface | ✅ | Next.js 15, CSS Modules, mobile-friendly. |
| 17 | Chat Interface | ✅ | Streaming responses, history sidebar, rename/delete. Paper: responses include source citations ("According to…"). |
| 18 | Settings Page | ⚠️ | Provider / model / API key config done. **Forgot-password flow** and **document expiry management** missing. |

---

### 🚀 Deployment

| # | Feature | Status | Notes |
|---|---|---|---|
| 19 | Docker Containerization | ❌ | No `Dockerfile` or `docker-compose.yml`. Paper: separate containers for backend, frontend, PostgreSQL, and vector DB. |
| 20 | Production-ready Scaling | ❌ | Local dev only. Paper: stateless API + load balancer for horizontal scaling. |

---

### 🌐 Data & Automation

| # | Feature | Status | Notes |
|---|---|---|---|
| 21 | Web Scraper — Official College Website | ❌ | **New (professor suggestion).** Automatically fetch and sync data (notices, calendar, policies) from the official college website into the backend knowledge base. Assigned to **G. Venkata Sai Ram**. |

---

### 📊 Overall Progress

| Category | ✅ Done | ⚠️ Partial | ❌ Pending |
|---|---|---|---|
| LLM & AI | 4 | 1 | 1 |
| Document Management | 2 | 1 | 0 |
| Backend | 2 | 1 | 0 |
| Authentication | 3 | 0 | 0 |
| Frontend | 2 | 1 | 0 |
| Deployment | 0 | 0 | 2 |
| Data & Automation | 0 | 0 | 1 |
| **Total** | **13 / 21** | **4 / 21** | **4 / 21** |

---

## 👥 Team Assignments

| Member | Responsible For |
|---|---|
| **G. Venkata Sai Ram** | #1 Multi-LLM, #2 LangGraph Agent, #3 RAG, #19 Docker, #20 Production config, **#21 Web Scraper** |
| **Ananda Sreekar** (anandasreekar@gmail.com) | #8 Embedding pipeline ✅, #9 Document indexing ✅, #16 Frontend, #17 Chat UI, #18 Settings page |
| **Chandu** | #4 Semantic search ✅, #6 Multi-hop reasoning, #10 FastAPI, #11 PostgreSQL migration ✅, #12 Conversation history |
| **Dheeraj** | #5 Query routing (+ Financial domain), #7 Document upload (PDF/DOCX/OCR), #13 OTP auth, #14 JWT, #15 RBAC |

---

## 🏗️ What Needs to Be Built Next

### High Priority

1. ~~**Vector Embeddings + Semantic Search** (`#3`, `#4`, `#8`, `#9`) — *Sreekar + Chandu*~~ ✅ **DONE** — Qdrant Cloud + `all-MiniLM-L6-v2` embeddings, auto-indexing on upload & startup, cosine similarity retrieval (top-k=5, threshold ≥ 0.70).

2. **PDF / DOCX Upload + OCR** (`#7`, `#8`) — *Dheeraj + Sreekar*
   - Add `pypdf2`, `python-docx`, `pytesseract` to `requirements.txt`
   - Extend `settings_router.py` to accept `.pdf`, `.docx`
   - OCR path via Tesseract for scanned PDFs
   - Feed extracted text into the embedding pipeline on upload

3. **Financial Domain** (`#5`) — *Dheeraj*
   - Add `Financial` as a 3rd retrieval domain (tuition, fees, billing, financial aid)
   - Create `data/Financial/` folder seeded with financial services content
   - Update `tools.py` routing to classify and route financial queries separately

4. **Web Scraper — College Website** (`#21`) — *G. Venkata Sai Ram*
   - Scrape official PVP Siddhartha website (notices, academic calendar, policies)
   - Scheduled periodic sync (APScheduler / cron) to keep knowledge base current
   - Feed scraped content through the embedding pipeline into the vector DB

5. **PostgreSQL Migration** (`#11`) — *Chandu*
   - Update `DATABASE_URL` in `.env` to a Postgres connection string
   - Confirm `asyncpg` is in `requirements.txt` (already present)
   - Run `alembic upgrade head`

6. **Docker** (`#19`, `#20`) — *G. Venkata Sai Ram*
   - `Dockerfile` for backend (Python 3.11 + uvicorn)
   - `Dockerfile` for frontend (Node 18 + `next build`)
   - `docker-compose.yml`: backend + frontend + PostgreSQL + vector DB containers

### Medium Priority

7. **LangGraph Session Checkpoints** (`#12`) — *Chandu*
   - Configure `PostgresSaver` as LangGraph checkpoint backend
   - Resume full conversation context across logins

8. **Forgot Password Flow** (`#18`) — *Sreekar*
   - `POST /auth/forgot-password` → send reset OTP
   - Add `frontend/app/reset-password/` page

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Ollama *(optional — for local AI)*

### 1 — Clone & install

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### 2 — Configure environment

Create `backend/.env`:

```env
# Database (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/edubot
DATABASE_URL_SYNC=postgresql://user:pass@localhost:5432/edubot

# JWT
JWT_SECRET_KEY=change-me-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRY=30

# CORS
CORS_ORIGINS=http://localhost:3000

# Qdrant Vector Database
QDRANT_URL=https://your-cluster.cloud.qdrant.io:6333
QDRANT_API_KEY=your-qdrant-api-key

# Optional: University-level API keys (auto provider fallback)
# OPENAI_API_KEY=sk-...
# GOOGLE_API_KEY=AI...
# DEEPSEEK_API_KEY=sk-...

DEBUG=True
```

### 3 — Run

```bash
# Terminal 1 — Backend
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
npm run dev
```

- App: http://localhost:3000
- API docs: http://localhost:8000/docs

### 4 — AI Providers

Go to **Settings** after logging in to configure your provider:

| Provider | Requires | Models |
|---|---|---|
| Ollama | Ollama running locally | Any pulled model (e.g. `llama3.1:8b`) |
| OpenAI | API key | `gpt-4o-mini` |
| Google Gemini | API key | `gemini-2.5-flash`, `gemini-flash-latest` |
| DeepSeek | API key | `deepseek-chat`, `deepseek-reasoner` (R1) |
| Auto | — | Falls back: OpenAI → Gemini → DeepSeek → Ollama |

---

## 🗂️ Project Structure

```
Project/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app setup
│   │   ├── config.py         # Env config
│   │   ├── auth.py           # JWT auth helpers
│   │   ├── llm_provider.py   # Multi-provider LLM abstraction
│   │   ├── graph.py          # LangGraph agent workflow
│   │   ├── vector_store.py    # Qdrant vector DB integration
│   │   ├── tools.py          # RAG semantic search tools
│   │   ├── schemas.py        # Pydantic request/response models
│   │   ├── email_service.py  # OTP email sending
│   │   ├── db/
│   │   │   ├── database.py   # SQLAlchemy engine + session
│   │   │   └── models.py     # ORM models (User, Chat, Message, Setting)
│   │   └── routers/
│   │       ├── auth_router.py
│   │       ├── chat_router.py
│   │       └── settings_router.py
│   ├── data/
│   │   ├── Academic/         # Academic calendar .txt files
│   │   ├── Administrative/   # University info .txt files
│   │   └── Educational/      # Course info .txt files
│   └── requirements.txt
│
└── frontend/
    ├── app/
    │   ├── chat/             # Chat page
    │   ├── login/            # Login page
    │   ├── register/         # Register + OTP page
    │   ├── settings/         # Settings page (provider, upload)
    │   └── components/       # Shared UI components
    ├── lib/
    │   ├── api.ts            # API client (injects auth + API key headers)
    │   ├── auth-context.tsx  # Auth state provider
    │   └── types.ts          # Shared TypeScript types
    └── package.json
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 16, TypeScript, React 19, CSS Modules |
| Backend | FastAPI, Python 3.11, SQLAlchemy 2 (async), Asyncpg |
| Agent | LangChain, LangGraph, LangChain-Ollama |
| Database | PostgreSQL (asyncpg) |
| Vector DB | Qdrant Cloud, sentence-transformers (`all-MiniLM-L6-v2`) |
| Auth | JWT (python-jose), bcrypt (passlib), OTP via SMTP |
| AI Providers | OpenAI, Google Gemini, Ollama, DeepSeek |

---

## 📝 API Reference

When the backend is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📄 License

MIT
