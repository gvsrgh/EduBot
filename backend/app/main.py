"""
EduBot Backend - Multi-Model AI Chatbot

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
    print("🚀 Starting EduBot Backend...")
    print("📦 Initializing database...")
    await init_db()
    print("✅ Database initialized")
    print("🤖 LangGraph Agent ready")
    print("💬 Multi-model chatbot system active")
    
    yield
    
    # Shutdown
    print("👋 Shutting down EduBot Backend...")


# Create FastAPI app
app = FastAPI(
    title="EduBot API",
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
        "message": "EduBot API - Multi-Model AI Chatbot",
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
