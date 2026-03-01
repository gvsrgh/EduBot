# EduBot+ — Remaining Work (as of March 1, 2026)

> Auto-generated audit of the entire codebase across all branches.  
> Current branch: `feature/source-citations`

---

## 📌 Branch Status

| Branch | Merged to current? | Unique Work |
|---|---|---|
| `master` | ✅ Yes | — |
| `feature/multi-format-document-upload` | ✅ Yes (parent) | PDF/DOCX/TXT upload + OCR, Knowledge Base UI, conversation history (PostgresSaver), auto-generated chat titles |
| `feature/domain-aware-query-routing` | ✅ Yes (parent) | Domain-aware query routing with regex classification, dynamic tool binding, multi-domain support |
| `feature/rag-vector-embeddings` | ✅ Yes (parent) | Qdrant vector embeddings, semantic search, document chunking pipeline |
| `feature/multi-hop-reasoning` | ✅ Yes (parent) | Explicit parallel cross-domain retrieval + result aggregation in LangGraph agent graph |
| `feature/automatic-document-indexing` | ✅ Yes (parent) | PostgreSQL Document model, DB-backed upload/delete/listing, startup seed |
| `feature/source-citations` | *(current)* | Structured source tags in tools, citation rules in LLM prompt, styled source badges in chat UI |
| `feature/document-expiry-management` | ❌ **Not merged** | Document expiry: `expiry_date`/`is_expired` on Document model, PATCH/GET expiry endpoints, inline expiry editor in KB UI |
| `feature/streaming-responses` | ❌ **Not merged** | Frontend SSE streaming: `streamMessage()` in API client, real-time token rendering, tool-use status indicators, blinking cursor |
| `feature/vector-embeddings` | ✅ Superseded | `7c3447d` — Superseded by `feature/rag-vector-embeddings` (clean rewrite) |
| `docs/project-status` | ❌ **Not merged** | `d5c4e5c` — README with paper-accurate feature status |
| `bugfixes` | ❌ **Not merged** | `7655af5` — Security, bug, and code quality fixes |
| `feature/conversation-history-postgres` | ✅ Yes | Already in current branch |
| `feature/forgot-password-otp` | ❌ **Not merged** | `3b9c266` — Forgot password with OTP verification (backend routes, email template, frontend 4-step flow, login page link) |
| `deepseek-api` | ✅ Yes | — |
| `postgres` | ✅ Yes | — |
| `settings` | ✅ Yes | — |
| `vercel-deploy` / `vercel-deployment` | ✅ Yes | — |

### Action Items — Branches
- [x] ~~Merge `feature/vector-embeddings` into current branch~~ — Superseded by clean rewrite on `feature/rag-vector-embeddings`
- [x] Merge `bugfixes` into current branch (security & code quality fixes) — done on branch
- [x] Merge `docs/project-status` or supersede with updated README — done on branch
- [x] Merge `feature/forgot-password-otp` into current branch (forgot password flow) — done on branch; cherry-pick carefully (that branch removes chat methods and other files)
- [ ] Delete stale branches: `vercel-deploy`, `vercel-deployment`

---

## ✅ Recently Completed

### Domain-Aware Query Routing (Paper §3.2)
**Status:** ✅ Implemented on `feature/domain-aware-query-routing`  
**Branch:** `feature/domain-aware-query-routing` (commit `30881c2`)

- [x] Create `query_router.py` module with regex-based domain classification
- [x] Support 3 domains: Academic, Administrative (includes financial), Educational
- [x] Multi-domain query detection (e.g. "refund policy if I drop a course" → Administrative + Academic)
- [x] Dynamic tool binding — only relevant domain tools are bound per query
- [x] Routing context injected into LLM system prompt for each turn
- [x] Confidence scoring with hit counts per domain
- [x] Fallback to all tools when no domain matches
- [x] `TOOL_REGISTRY` added to `tools.py` for name-based lookup
- [x] Updated `graph.py` `agent_node` to use domain-aware routing

### RAG with Qdrant Vector Embeddings (Paper §3, §3.3, §3.4, §4)
**Status:** ✅ Implemented on `feature/rag-vector-embeddings`  
**Branch:** `feature/rag-vector-embeddings` (based on `feature/domain-aware-query-routing`)

- [x] Create `vector_store.py` — Qdrant Cloud integration with `all-MiniLM-L6-v2` (384-dim) embeddings
- [x] Document chunking (800 chars, 10% overlap) with `chunk_text()`
- [x] Semantic similarity search with cosine distance (threshold 0.20, top_k=5)
- [x] `index_document()` — chunk → embed → upsert to Qdrant
- [x] `delete_document()` — remove vectors by filename+category filter
- [x] `seed_existing_documents()` — index all files in `data/` on startup
- [x] `ensure_collection()` — create Qdrant collection if missing
- [x] Rewrite `tools.py` — replace keyword search with `search_documents()` semantic search
- [x] Add `search_all_domains` tool for cross-domain queries
- [x] Update `graph.py` — add `sanitize_messages()` to strip orphaned tool_calls
- [x] Update `settings_router.py` — `index_document()` on upload, `delete_document()` on delete
- [x] Update `query_router.py` — `search_all_domains` for multi-domain queries
- [x] Add `QDRANT_URL` and `QDRANT_API_KEY` to `config.py`
- [x] Add `qdrant-client`, `sentence-transformers` to `requirements.txt`
- [x] `main.py` — `ensure_collection()` + `seed_existing_documents()` on startup

### Multi-hop Reasoning (Paper §4.3)
**Status:** ✅ Implemented on `feature/multi-hop-reasoning`  
**Branch:** `feature/multi-hop-reasoning` (based on `feature/rag-vector-embeddings`)

- [x] Multi-domain query detection via `query_router.py`
- [x] System prompt instructs LLM to query all matched domains
- [x] Add `multi_hop_retrieval_node` to LangGraph workflow — parallel semantic search across domains using `concurrent.futures.ThreadPoolExecutor`
- [x] `_aggregate_multi_hop_results()` — merge, deduplicate, and sort cross-domain results
- [x] Inject aggregated context into agent system prompt as pre-retrieved block
- [x] Update `AgentState` with `multi_hop_context` field
- [x] Rewire graph: entry → `multi_hop_retrieval` → `agent` → tools/end
- [x] Single-domain queries pass through with zero overhead

### Source Citations in Responses (Paper §4.1)
**Status:** ✅ Implemented on `feature/source-citations`  
**Branch:** `feature/source-citations` (commit `bc8e22a`)

- [x] `tools.py`: structured `[SOURCE: filename | category | relevance]` tags in tool results
- [x] `graph.py`: citation rules in system prompt — inline citations + `Sources:` footer
- [x] `graph.py`: multi-hop aggregation uses same `[SOURCE: ...]` format
- [x] `chat.module.css`: styled source badges (pill badges with accent-colored filenames)

### Document Expiry Management (Paper — Settings)
**Status:** ✅ Implemented on `feature/document-expiry-management`  
**Branch:** `feature/document-expiry-management` (commit `002c731`)  
**Contributor:** gvsrgh

- [x] Add `expiry_date` (nullable DateTime) and `is_expired` (Boolean) columns to `Document` model
- [x] `PATCH /settings/files/{id}/expiry` — set or remove expiry date on a document
- [x] `GET /settings/files/expired` — list all expired documents
- [x] `POST /settings/files/refresh-expiry` — bulk-refresh `is_expired` flags
- [x] Upload endpoint accepts optional `expiry_date` form field
- [x] Expiry flags auto-refreshed on app startup in lifespan handler
- [x] KnowledgeBase UI: inline ⏰ expiry editor per document row
- [x] Color-coded expiry tags: red (expired), amber (≤7d), yellow (≤30d), green (active)
- [x] Expired docs sorted to top with red border highlight
- [x] Header badge shows count of expired documents

### Streaming Chat Responses (Paper §3.6)
**Status:** ✅ Implemented on `feature/streaming-responses`  
**Branch:** `feature/streaming-responses`  
**Contributor:** gvsrgh

- [x] `api.ts`: `streamMessage()` SSE method reading `ReadableStream` chunks with `onToken`/`onStatus`/`onComplete`/`onError` callbacks
- [x] `api.ts`: `getHeaders()` helper shared by JSON and streaming requests
- [x] `page.tsx`: `handleSubmit` rewritten — authenticated users stream via `/chat/prompt/stream`, with non-streaming fallback on error
- [x] `page.tsx`: real-time token-by-token rendering into assistant message bubble
- [x] `page.tsx`: tool-use status banners ("🔍 Searching ...") during streaming
- [x] `page.tsx`: blinking cursor `▊` while stream is in progress
- [x] `page.tsx`: unauthenticated users still use non-streaming `/chat/message`
- [x] `page.tsx`: "Thinking..." indicator hidden when a streaming message is active
- [x] `chat.module.css`: `.streamCursor` with blink animation, `.streamStatus` styled pill

---

## 🔴 Critical / High Priority

### 1. Vector Embeddings + Semantic Search (Paper §3, §4)
**Status:** ✅ Implemented on `feature/rag-vector-embeddings`  
**Paper requires:** `all-MiniLM-L6-v2` embeddings, cosine similarity, top-k retrieval  
**Current state:** `tools.py` uses `vector_store.search_documents()` for Qdrant semantic search; `vector_store.py` handles chunking, embedding, and upsert to Qdrant Cloud

- [x] Add `qdrant-client`, `sentence-transformers` to `requirements.txt`
- [x] Create embedding pipeline: extract text → chunk (800 chars, 10% overlap) → embed with `all-MiniLM-L6-v2`
- [x] Store embeddings in Qdrant Cloud (credentials in `.env`)
- [x] Store document metadata (filename, upload date, type, vector IDs) in PostgreSQL
- [x] Replace keyword search in `tools.py` with cosine similarity retrieval
- [x] Run embeddings on upload in `settings_router.py` upload endpoint
- [x] Re-embed existing `data/` files on startup via `seed_existing_documents()`

### 2. Multi-hop Reasoning (Paper §4.3)
**Status:** ✅ Implemented on `feature/multi-hop-reasoning`  
**Paper requires:** Parallel retrieval across domains + result aggregation (e.g., "refund policy if I drop a course" → Administrative + Academic)  
**Current state:** Query router detects multi-domain queries. A dedicated `multi_hop_retrieval_node` in the LangGraph workflow performs parallel semantic search across all matched domains using `concurrent.futures`, aggregates and deduplicates results, and injects them into the agent's system prompt. The LLM then synthesizes a cross-domain answer.

- [x] Multi-domain query detection via `query_router.py`
- [x] System prompt instructs LLM to query all matched domains
- [x] Implement explicit parallel retrieval + result aggregation in agent graph (beyond LLM tool-calling)
- [x] Test with cross-domain queries

### 3. Document Processing → Vector Embedding Pipeline (Paper §3.3)
**Status:** ✅ Implemented on `feature/rag-vector-embeddings` + `feature/automatic-document-indexing`  
**Current state:** Upload extracts text → saves as `.txt` → chunks and embeds via `vector_store.index_document()`; chunk-to-document mapping tracked in PostgreSQL `Document` model

- [x] Implement text chunking (800 chars, 10% overlap) in `vector_store.py`
- [x] Embed chunks on upload and store in Qdrant
- [x] Track chunk-to-document mapping in PostgreSQL (Document model with vector_ids)
- [x] Handle re-indexing when files are deleted (`delete_document()` in `settings_router.py`)

### 4. Automatic Document Indexing (Paper §3.4)
**Status:** ✅ Implemented on `feature/automatic-document-indexing`  
**Paper requires:** PostgreSQL stores filename, upload date, type with FK to vector IDs  
**Current state:** `Document` model in PostgreSQL tracks filename, category, upload_date, file_type, user_id, vector_ids. Upload creates DB record + Qdrant vectors. Delete removes both. Listing queries DB with filesystem fallback. Startup seeds existing `data/` files.

- [x] Auto-index documents in Qdrant on upload (`settings_router.py`)
- [x] Auto-index existing `data/` files on startup (`main.py`)
- [x] Remove vectors on file delete (`settings_router.py`)
- [x] Create `Document` model in `models.py` (filename, category, upload_date, file_type, user_id, vector_ids)
- [x] Update upload endpoint to create DB record alongside file storage
- [x] Update file listing to query from DB instead of filesystem glob

---

## 🟡 Medium Priority

### 5. Document Expiry Management (Paper — Settings)
**Status:** ✅ Implemented on `feature/document-expiry-management`

- [x] Add `expiry_date` and `is_expired` fields to Document model
- [x] Backend: PATCH endpoint to set/update/remove document expiry
- [x] Backend: GET endpoint to list expired documents
- [x] Backend: POST endpoint to bulk-refresh expiry flags
- [x] Frontend: inline expiry editor in Knowledge Base UI
- [x] Expiry flags auto-refreshed on app startup

### 7. Web Scraper — Official College Website (Issue #21)
**Status:** ❌ Not implemented

- [ ] Implement scraper (BeautifulSoup / Scrapy) for official college website
- [ ] Parse and clean scraped content
- [ ] Feed into knowledge base
- [ ] Schedule periodic sync
- [ ] Add admin UI to trigger manual scrape

### 8. Streaming Chat (Paper §3.6)
**Status:** ✅ Implemented on `feature/streaming-responses`

- [x] Update `apiClient` in `frontend/lib/api.ts` to support SSE streaming
- [x] Update `ChatPage` to use streaming endpoint with real-time token rendering
- [x] Show typing indicator / blinking cursor while streaming
- [x] Tool-use status banners during retrieval
- [x] Graceful fallback to non-streaming on error

---

## 🟢 Low Priority / Polish

### 9. Docker Containerization (Paper §5)
**Status:** ❌ Not implemented

- [ ] Create `backend/Dockerfile`
- [ ] Create `frontend/Dockerfile`
- [ ] Create `docker-compose.yml`
- [ ] Add `.dockerignore` files
- [ ] Document Docker setup in README

### 10. Production-ready Scaling (Paper §5.2)
**Status:** ❌ Not implemented

- [ ] Stateless API design verification
- [ ] Health check endpoint improvements
- [ ] Rate limiting middleware
- [ ] Request logging / monitoring
- [ ] Environment-specific configs (dev/staging/prod)

---

## 📊 Summary

| Priority | Count | Items |
|---|---|---|
| 🔴 Critical | 0 | — |
| 🟡 Medium | 1 | Web scraper |
| 🟢 Low | 2 | Docker, Production scaling |
| **Total** | **3** | |

### By Paper Alignment (IC-ECBE 2026)

| Paper Feature | Status |
|---|---|
| Multi-LLM Support | ✅ Done (OpenAI, Gemini, Ollama, DeepSeek) |
| LangGraph Agent | ✅ Done |
| RAG with Vector Embeddings | ✅ Done — Qdrant Cloud + all-MiniLM-L6-v2 on `feature/rag-vector-embeddings` |
| Semantic Similarity Search | ✅ Done — cosine similarity (threshold 0.20, top_k=5) |
| Domain-aware Query Routing (3 domains) | ✅ Done — `query_router.py` with Academic, Administrative, Educational |
| Multi-hop Reasoning | ✅ Done — parallel retrieval + aggregation in `multi_hop_retrieval_node` on `feature/multi-hop-reasoning` |
| PDF/DOCX Upload + OCR | ✅ Done |
| Document → Embedding Pipeline | ✅ Done — chunk → embed → upsert on upload + startup seed |
| Automatic Document Indexing | ✅ Done — PostgreSQL `Document` model + Qdrant vectors on `feature/automatic-document-indexing` |
| FastAPI Backend | ✅ Done |
| PostgreSQL Database | ✅ Done — Neon PostgreSQL Cloud |
| Conversation History (persistent) | ✅ Done (PostgresSaver) |
| OTP Authentication | ✅ Done |
| JWT Security | ✅ Done |
| Role-based Access Control | ✅ Done |
| Next.js Frontend | ✅ Done |
| Chat with History Sidebar | ✅ Done |
| Source Citations | ✅ Done — structured source tags + citation prompt + styled UI on `feature/source-citations` |
| Document Expiry Management | ✅ Done — `expiry_date`/`is_expired` on Document model, PATCH/GET/POST expiry endpoints, inline KB UI on `feature/document-expiry-management` |
| Streaming Responses | ✅ Done — SSE streaming with real-time token rendering, tool-use status, blinking cursor on `feature/streaming-responses` |
| Docker Containerization | ❌ Not implemented |
| Production Scaling | ❌ Not implemented |
