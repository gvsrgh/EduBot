"""
EduBot+ Backend - Multi-Model AI Chatbot

Main FastAPI application with LangGraph agent workflow.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import CORS_ORIGINS, DEBUG
from app.db.database import init_db
from app.routers import auth_router, chat_router, settings_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print("🚀 Starting EduBot+ Backend...")
    print("📦 Initializing database...")
    await init_db()
    print("✅ Database initialized")

    # Initialize Qdrant vector store
    print("📐 Initializing Qdrant vector store...")
    try:
        from app.vector_store import ensure_collection, seed_existing_documents
        ensure_collection()
        seed_existing_documents()
        print("✅ Qdrant vector store ready")
    except Exception as e:
        print(f"⚠️ Qdrant initialization failed (non-fatal): {e}")
    
    # Seed existing data/ files into PostgreSQL Document table
    print("📄 Syncing document metadata to PostgreSQL...")
    try:
        from app.db.database import AsyncSessionLocal
        from app.db.models import Document
        from app.config import ACADEMIC_DIR, ADMINISTRATIVE_DIR, EDUCATIONAL_DIR
        from sqlalchemy import select, and_

        async with AsyncSessionLocal() as session:
            dirs = {
                "Academic": ACADEMIC_DIR,
                "Administrative": ADMINISTRATIVE_DIR,
                "Educational": EDUCATIONAL_DIR,
            }
            created = 0
            for category, dir_path in dirs.items():
                if not dir_path.exists():
                    continue
                for txt_file in sorted(dir_path.glob("*.txt")):
                    # Check if already tracked in DB
                    result = await session.execute(
                        select(Document).where(
                            and_(
                                Document.filename == txt_file.name,
                                Document.category == category,
                            )
                        )
                    )
                    if result.scalar_one_or_none():
                        continue
                    stat = txt_file.stat()
                    doc = Document(
                        filename=txt_file.name,
                        original_filename=txt_file.name,
                        category=category,
                        file_type=".txt",
                        file_size=stat.st_size,
                        chunk_count=0,  # already indexed in Qdrant above
                        vector_ids=[],
                    )
                    session.add(doc)
                    created += 1
            if created:
                await session.commit()
            print(f"✅ Document metadata synced ({created} new records)")
    except Exception as e:
        print(f"⚠️ Document metadata sync failed (non-fatal): {e}")
    
    print("🤖 LangGraph Agent ready")
    print("💬 Multi-model chatbot system active")

    # Refresh document expiry flags on startup
    print("⏰ Refreshing document expiry flags...")
    try:
        from app.db.database import AsyncSessionLocal as _ExpirySession
        from app.db.models import Document as _Doc
        from datetime import datetime as _dt, timezone as _tz
        from sqlalchemy import select as _sel

        async with _ExpirySession() as _sess:
            _now = _dt.now(_tz.utc)
            _res = await _sess.execute(_sel(_Doc))
            _docs = _res.scalars().all()
            _upd = 0
            for _d in _docs:
                _should = _d.expiry_date is not None and _d.expiry_date <= _now
                if _d.is_expired != _should:
                    _d.is_expired = _should
                    _upd += 1
            if _upd:
                await _sess.commit()
            print(f"✅ Expiry flags refreshed ({_upd} updated out of {len(_docs)})")
    except Exception as e:
        print(f"⚠️ Expiry flag refresh failed (non-fatal): {e}")
    
    yield
    
    # Shutdown
    print("👋 Shutting down EduBot+ Backend...")


# Create FastAPI app
app = FastAPI(
    title="EduBot+ API",
    description="Multi-Model AI Chatbot with LangGraph Agent Workflow",
    version="1.0.0",
    lifespan=lifespan,
    debug=DEBUG,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router.router, prefix="/api")
app.include_router(chat_router.router, prefix="/api")
app.include_router(settings_router.router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "EduBot+ API - Multi-Model AI Chatbot",
        "version": "1.0.0",
        "docs": "/docs",
        "agent": "LangGraph Agent",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "agent": "LangGraph Agent",
        "database": "connected",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=DEBUG,
    )
