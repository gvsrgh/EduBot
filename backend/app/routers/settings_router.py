from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os
from pathlib import Path
import httpx
from typing import Optional

from app.db.database import get_session
from app.db.models import Setting
from app.schemas import ProviderUpdate, ProviderResponse, SettingsResponse, SettingsUpdate, TestConnectionRequest
from app.auth import get_current_user, get_current_admin_user
from app.llm_provider import llm_provider

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.post("/test-connection")
async def test_connection(
    request: TestConnectionRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Test connection to AI providers in real-time.
    
    Returns:
        - success: Boolean indicating if connection was successful
        - message: Status message
        - details: Additional details about the connection
    """
    
    provider = request.provider
    api_key = request.api_key
    ollama_url = request.ollama_url
    
    try:
        if provider == "openai":
            if not api_key:
                return {
                    "success": False,
                    "message": "OpenAI API key is required",
                    "details": None
                }
            
            # Test OpenAI connection
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.openai.com/v1/models",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    models = response.json()
                    model_count = len(models.get("data", []))
                    return {
                        "success": True,
                        "message": f"Connected to OpenAI successfully",
                        "details": f"Found {model_count} available models"
                    }
                else:
                    return {
                        "success": False,
                        "message": "Invalid API key or connection failed",
                        "details": f"Status code: {response.status_code}"
                    }
                    
        elif provider == "gemini":
            if not api_key:
                return {
                    "success": False,
                    "message": "Gemini API key is required",
                    "details": None
                }
            
            # Test Gemini connection
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://generativelanguage.googleapis.com/v1/models?key={api_key}",
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    models = response.json()
                    model_count = len(models.get("models", []))
                    return {
                        "success": True,
                        "message": "Connected to Gemini successfully",
                        "details": f"Found {model_count} available models"
                    }
                else:
                    return {
                        "success": False,
                        "message": "Invalid API key or connection failed",
                        "details": f"Status code: {response.status_code}"
                    }
                    
        elif provider == "ollama":
            url = ollama_url or "http://localhost:11434"
            
            # Convert localhost to host.docker.internal for Docker environments
            if "localhost" in url or "127.0.0.1" in url:
                url = url.replace("localhost", "host.docker.internal").replace("127.0.0.1", "host.docker.internal")
            
            # Test Ollama connection
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{url}/api/tags",
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    model_count = len(data.get("models", []))
                    return {
                        "success": True,
                        "message": "Connected to Ollama successfully",
                        "details": f"Found {model_count} model(s)"
                    }
                else:
                    return {
                        "success": False,
                        "message": "Cannot connect to Ollama",
                        "details": "Make sure Ollama is running"
                    }
        else:
            return {
                "success": False,
                "message": "Invalid provider",
                "details": f"Provider '{provider}' is not supported"
            }
            
    except httpx.TimeoutException:
        return {
            "success": False,
            "message": "Connection timeout",
            "details": "The request timed out. Check your network or service availability."
        }
    except Exception as e:
        return {
            "success": False,
            "message": "Connection failed",
            "details": str(e)
        }


@router.get("/provider", response_model=ProviderResponse)
async def get_provider_settings(
    current_user: dict = Depends(get_current_user),
):
    """Get current AI provider configuration."""
    
    current_provider = llm_provider.get_current_provider()
    available_providers = llm_provider.get_available_providers()
    
    return ProviderResponse(
        ai_provider=current_provider,
        available_providers=available_providers,
    )


@router.put("/provider", response_model=ProviderResponse)
async def update_provider_settings(
    provider_data: ProviderUpdate,
    current_user: dict = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Update AI provider configuration (Admin only).
    
    This endpoint allows switching between:
    - openai: OpenAI GPT-4
    - gemini: Google Gemini
    - ollama: Local Gemma via Ollama
    - auto: Automatic fallback selection
    """
    
    try:
        # Update provider in memory
        llm_provider.set_provider(provider_data.ai_provider)
        
        # Update in database
        result = await session.execute(
            select(Setting).order_by(Setting.updated_at.desc())
        )
        settings = result.scalar_one_or_none()
        
        if settings:
            settings.ai_provider = provider_data.ai_provider
        else:
            settings = Setting(ai_provider=provider_data.ai_provider)
            session.add(settings)
        
        await session.commit()
        
        # Get updated available providers
        available_providers = llm_provider.get_available_providers()
        
        return ProviderResponse(
            ai_provider=provider_data.ai_provider,
            available_providers=available_providers,
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating provider: {str(e)}"
        )


@router.get("/", response_model=SettingsResponse)
async def get_settings(
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Get all application settings."""
    
    result = await session.execute(
        select(Setting).order_by(Setting.updated_at.desc())
    )
    settings = result.scalar_one_or_none()
    
    if not settings:
        # Create default settings
        settings = Setting()
        session.add(settings)
        await session.commit()
        await session.refresh(settings)
    
    return SettingsResponse.model_validate(settings)


@router.put("/", response_model=SettingsResponse)
async def update_settings(
    settings_data: SettingsUpdate,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Update application settings and provider configuration."""
    
    result = await session.execute(
        select(Setting).order_by(Setting.updated_at.desc())
    )
    settings = result.scalar_one_or_none()
    
    if not settings:
        settings = Setting()
        session.add(settings)
    
    # Update fields if provided
    if settings_data.ai_provider is not None:
        settings.ai_provider = settings_data.ai_provider
        # Update the global provider
        llm_provider.set_provider(settings_data.ai_provider)
    
    if settings_data.deny_words is not None:
        settings.deny_words = settings_data.deny_words
    
    if settings_data.max_tokens is not None:
        settings.max_tokens = settings_data.max_tokens
    
    if settings_data.temperature is not None:
        settings.temperature = settings_data.temperature
    
    await session.commit()
    await session.refresh(settings)
    
    return SettingsResponse.model_validate(settings)


@router.post("/upload-content")
async def upload_content(
    file: UploadFile = File(...),
    category: str = Form(...),
    topic: str = Form(...),
    current_user: dict = Depends(get_current_admin_user),
):
    """
    Upload educational content files (Admin only).
    
    Categories:
    - academic: Academic Information
    - administrative: Administrative & Procedures
    - events: Events & Announcements
    """
    
    # Validate category
    valid_categories = ["academic", "administrative", "events"]
    if category not in valid_categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}"
        )
    
    # Validate file type
    allowed_extensions = [".txt", ".pdf", ".doc", ".docx", ".md"]
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    try:
        # Create category directory if it doesn't exist
        base_dir = Path("data")
        category_dir = base_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)
        
        # Create safe filename from topic
        safe_filename = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in topic)
        safe_filename = safe_filename.strip().replace(' ', '_')
        filename = f"{safe_filename}{file_ext}"
        
        # Save the file
        file_path = category_dir / filename
        content = await file.read()
        
        with open(file_path, 'wb') as f:
            f.write(content)
        
        return {
            "message": "Content uploaded successfully",
            "filename": filename,
            "category": category,
            "topic": topic,
            "path": str(file_path),
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {str(e)}"
        )

