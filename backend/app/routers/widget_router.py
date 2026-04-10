"""
Guest Widget Router — Public chat endpoint for embeddable widget.

- No authentication required
- Per-IP and per-session rate limiting
- Unique guest session IDs via secure cookies
- Input validation and message length limits
- Isolated conversations (no shared thread IDs)
"""

import time
import uuid
import logging
from collections import defaultdict
from typing import Optional

from fastapi import APIRouter, Request, Response, HTTPException
from pydantic import BaseModel, Field

from app.graph import create_agent_graph
from app.llm_provider import llm_provider
from app.config import WIDGET_RATE_LIMIT_PER_MIN, WIDGET_RATE_LIMIT_PER_SESSION_MIN

logger = logging.getLogger("widget")

router = APIRouter(prefix="/widget", tags=["Widget"])

# Lazy-init agent graph (shared with main chat)
_agent_graph = None


def _get_agent_graph():
    global _agent_graph
    if _agent_graph is None:
        _agent_graph = create_agent_graph()
    return _agent_graph


# ── Rate-limiter (in-memory, sliding window) ────────────────────────

class _SlidingWindowLimiter:
    """Simple per-key sliding-window rate limiter."""

    def __init__(self):
        self._hits: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, key: str, max_hits: int, window_secs: int = 60) -> bool:
        now = time.monotonic()
        bucket = self._hits[key]
        # Prune expired entries
        cutoff = now - window_secs
        self._hits[key] = bucket = [t for t in bucket if t > cutoff]
        if len(bucket) >= max_hits:
            return False
        bucket.append(now)
        return True

    def cleanup(self, max_age: int = 600):
        """Remove keys with no recent hits (call periodically if needed)."""
        now = time.monotonic()
        stale = [k for k, v in self._hits.items() if not v or v[-1] < now - max_age]
        for k in stale:
            del self._hits[k]


_ip_limiter = _SlidingWindowLimiter()
_session_limiter = _SlidingWindowLimiter()


# ── Request / response schemas ──────────────────────────────────────

class WidgetMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None


class WidgetMessageResponse(BaseModel):
    success: bool
    message: str
    session_id: str


# ── Helpers ─────────────────────────────────────────────────────────

def _get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _get_or_create_session(request: Request, body_session_id: Optional[str]) -> str:
    """Return existing guest session ID from cookie/body, or create a new one."""
    session_id = request.cookies.get("edubot_guest_sid") or body_session_id
    if session_id and len(session_id) <= 64:
        return session_id
    return f"guest-{uuid.uuid4().hex}"


def _extract_answer(result: dict) -> str:
    """Extract text answer from agent graph result."""
    final_message = result["messages"][-1]
    content = final_message.content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and "text" in block:
                parts.append(block["text"])
        return "\n".join(parts) if parts else str(content)
    return str(content) if content else ""


# ── Endpoint ────────────────────────────────────────────────────────

@router.post("/message", response_model=WidgetMessageResponse)
async def widget_message(
    body: WidgetMessageRequest,
    request: Request,
    response: Response,
):
    """
    Public guest chat endpoint for the embeddable widget.
    No auth required. Rate-limited per IP and per session.
    """
    client_ip = _get_client_ip(request)
    session_id = _get_or_create_session(request, body.session_id)

    # ── Rate limiting ───────────────────────────────────────────
    if not _ip_limiter.is_allowed(f"ip:{client_ip}", WIDGET_RATE_LIMIT_PER_MIN):
        logger.warning("Widget rate-limit hit (IP): %s", client_ip)
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please wait a moment before trying again.",
        )

    if not _session_limiter.is_allowed(f"sess:{session_id}", WIDGET_RATE_LIMIT_PER_SESSION_MIN):
        logger.warning("Widget rate-limit hit (session): %s", session_id[:12])
        raise HTTPException(
            status_code=429,
            detail="You're sending messages too quickly. Please slow down.",
        )

    logger.info(
        "Widget request — ip=%s session=%s len=%d",
        client_ip, session_id[:12], len(body.message),
    )

    # ── Invoke agent ────────────────────────────────────────────
    # Each guest session gets its own thread_id for conversation isolation
    thread_config = {"configurable": {"thread_id": session_id}}

    try:
        graph = _get_agent_graph()
        result = await graph.ainvoke(
            {"messages": [("user", body.message)]},
            config=thread_config,
        )
        answer = _extract_answer(result)
    except Exception as e:
        logger.error("Widget agent error — session=%s: %s", session_id[:12], e)
        answer = (
            "I'm sorry, I'm having trouble processing your request right now. "
            "Please try again in a moment."
        )

    # ── Set session cookie ──────────────────────────────────────
    response.set_cookie(
        key="edubot_guest_sid",
        value=session_id,
        httponly=True,
        samesite="none",
        secure=True,
        max_age=86400,  # 24 hours
    )

    return WidgetMessageResponse(
        success=True,
        message=answer,
        session_id=session_id,
    )
