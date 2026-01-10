from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os
from pathlib import Path

from app.db.database import get_session
from app.db.models import Setting
from app.schemas import ProviderUpdate, ProviderResponse, SettingsResponse, SettingsUpdate
from app.auth import get_current_user, get_current_admin_user
from app.llm_provider import llm_provider

router = APIRouter(prefix="/settings", tags=["Settings"])


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
    """Update application settings."""
    
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

