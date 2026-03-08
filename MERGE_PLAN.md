# Merge Plan

> Generated: March 7, 2026 — 14 unmerged branches into `master`

---

## Phase 1 — Foundation

| # | Branch | Owner | Reason |
|---|---|---|---|
| 1 | `feature/rag-vector-embeddings` | G. Venkata Sai Ram | Core dependency — RAG/vector store changes that 4 other branches build on (`graph.py`, `tools.py`, `settings_router.py`, `vector_store.py`) |
| 2 | `feature/domain-aware-query-routing` | Dheeraj | Touches `graph.py` + `tools.py` — merge early before other `graph.py` branches pile up |

---

## Phase 2 — Backend Models & Data Layer

| # | Branch | Owner | Reason |
|---|---|---|---|
| 3 | `feature/automatic-document-indexing` | Sreekar | Adds Document model to `models.py`, `main.py`, `settings_router.py` — needed before expiry management |
| 4 | `feature/conversation-history-postgres` | Chandu | Touches `graph.py`, `chat_router.py`, `schemas.py` — independent of #3 but merge after `graph.py` settles |

---

## Phase 3 — AI Behavior

> Depends on `graph.py` changes from Phases 1–2

| # | Branch | Owner | Reason |
|---|---|---|---|
| 5 | `feature/multi-hop-reasoning` | Chandu | Heavy `graph.py` rewrite — merge after routing + RAG are in |
| 6 | `feature/source-citations` | Sreekar | Also modifies `graph.py` + `tools.py` — merge after multi-hop |

---

## Phase 4 — Frontend Features & Document Management

| # | Branch | Owner | Reason |
|---|---|---|---|
| 7 | `feature/streaming-responses` | Sreekar | Touches `chat/page.tsx`, `chat.module.css`, `api.ts` — merge before conversation-history UI conflicts grow |
| 8 | `feature/forgot-password-otp` | Sreekar | Isolated (new page + auth routes), low conflict risk |
| 9 | `feature/multi-format-document-upload` | Dheeraj | Touches `settings_router.py`, `KnowledgeBase.tsx`, `settings.module.css` — merge before expiry & scraper |
| 10 | `feature/document-expiry-management` | Sreekar | Depends on Document model (#3) + overlaps `KnowledgeBase.tsx` with #9 |

---

## Phase 5 — New Features & Infrastructure

| # | Branch | Owner | Reason |
|---|---|---|---|
| 11 | `feature/web-scraper` | G. Venkata Sai Ram | Largest branch (1797 lines), touches `settings_router.py`, `models.py`, `settings.module.css` — merge last among features to minimize conflicts |

---

## Phase 6 — Stale Branches (Rebase Required)

> These branches are behind `master` and need `git rebase master` before merging.

| # | Branch | Owner | Behind | Action |
|---|---|---|---|---|
| 12 | `bugfixes` | G. Venkata Sai Ram | 8 commits | Rebase onto master, then merge |
| 13 | `docs/project-status` | G. Venkata Sai Ram | 7 commits | Rebase onto master, then merge (README only) |
| 14 | `vercel-deployment` | G. Venkata Sai Ram | 2 commits | Rebase onto master, then merge |

---

## Conflict Hotspots

| File | Touched By |
|---|---|
| `backend/app/graph.py` | rag-vector-embeddings, domain-aware-query-routing, conversation-history-postgres, multi-format-document-upload, multi-hop-reasoning, source-citations |
| `backend/app/routers/settings_router.py` | rag-vector-embeddings, automatic-document-indexing, document-expiry-management, multi-format-document-upload, web-scraper |
| `backend/app/schemas.py` | automatic-document-indexing, conversation-history-postgres, document-expiry-management, forgot-password-otp, web-scraper |
| `backend/app/db/models.py` | automatic-document-indexing, document-expiry-management, web-scraper |
| `frontend/app/settings/components/KnowledgeBase.tsx` | document-expiry-management, multi-format-document-upload |
| `frontend/app/settings/settings.module.css` | document-expiry-management, multi-format-document-upload, web-scraper |
| `frontend/app/chat/page.tsx` | conversation-history-postgres, streaming-responses |
| `frontend/app/chat/chat.module.css` | conversation-history-postgres, source-citations, streaming-responses |
