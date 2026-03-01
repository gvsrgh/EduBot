from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx
from typing import Optional
from pathlib import Path
import shutil

from app.db.database import get_session
from app.db.models import Setting
from app.schemas import ProviderUpdate, ProviderResponse, SettingsResponse, SettingsUpdate, TestConnectionRequest
from app.auth import get_current_user, get_current_admin_user
from app.llm_provider import llm_provider
from app.config import ACADEMIC_DIR, ADMINISTRATIVE_DIR, EDUCATIONAL_DIR, ALLOWED_EXTENSIONS, MAX_FILE_SIZE

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("/provider/defaults")
async def get_provider_defaults():
    """
    Return which AI providers have server-side default API keys configured in .env.
    
    Does NOT expose the actual keys — only boolean flags so the frontend
    can show 'Default configured' badges and skip requiring user input.
    """
    return llm_provider.get_env_defaults()


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
        elif provider == "deepseek":
            if not api_key:
                return {"success": False, "message": "DeepSeek API key is required", "details": None}
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.deepseek.com/v1/models",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10.0
                )
                if response.status_code == 200:
                    model_count = len(response.json().get("data", []))
                    return {
                        "success": True,
                        "message": "Connected to DeepSeek successfully",
                        "details": f"Found {model_count} available models"
                    }
                else:
                    return {
                        "success": False,
                        "message": "Invalid API key or connection failed",
                        "details": f"Status code: {response.status_code}"
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
    
    # Update AI provider if provided
    if settings_data.ai_provider is not None:
        settings.ai_provider = settings_data.ai_provider
        # Update the global provider
        llm_provider.set_provider(settings_data.ai_provider)
    
    await session.commit()
    await session.refresh(settings)
    
    return SettingsResponse.model_validate(settings)


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    category: str = Form(...),
    current_user: dict = Depends(get_current_user),
):
    """
    Upload a text file to the knowledge base.
    
    Args:
        file: The file to upload (must be .txt)
        category: Category for the file ("Academic", "Administrative", or "Educational")
        
    Returns:
        Success message with file details
    """
    
    # Restrict file upload access for @pvpsit.ac.in users
    user_email = current_user.get("email", "")
    if user_email.endswith("@pvpsit.ac.in"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="File upload is not allowed for @pvpsit.ac.in users"
        )
    
    # Validate category
    valid_categories = {"Academic", "Administrative", "Educational"}
    if category not in valid_categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}"
        )
    
    # Get category directory
    category_dirs = {
        "Academic": ACADEMIC_DIR,
        "Administrative": ADMINISTRATIVE_DIR,
        "Educational": EDUCATIONAL_DIR
    }
    target_dir = category_dirs[category]
    
    # Ensure directory exists
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Sanitize filename to prevent path traversal
    safe_filename = Path(file.filename).name
    if not safe_filename or safe_filename.startswith('.'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename"
        )
    
    # Validate file extension
    file_ext = Path(safe_filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Only .txt files are allowed."
        )
    
    # Read file content to check size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum limit of {MAX_FILE_SIZE / (1024*1024)}MB"
        )
    
    # Save file
    file_path = target_dir / safe_filename
    
    # Check if file already exists
    if file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"File '{safe_filename}' already exists in {category} category"
        )
    
    try:
        # Write file content
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Index the document in Qdrant vector store for semantic search
        try:
            from app.vector_store import index_document
            chunk_count = index_document(extracted_text, output_filename, category)
            print(f"Indexed '{output_filename}' in Qdrant ({chunk_count} chunks)")
        except Exception as vec_err:
            print(f"Warning: Vector indexing failed for '{output_filename}': {vec_err}")
        
        original_ext = Path(safe_filename).suffix.lower()
        converted_note = ""
        if original_ext != '.txt':
            converted_note = f" (converted from {original_ext.upper().lstrip('.')})"
        
        return {
            "success": True,
            "message": f"File uploaded successfully to {category} category",
            "filename": safe_filename,
            "category": category,
            "size": len(content),
            "chunks_indexed": chunk_count
        }
        
    except Exception as e:
        # Clean up if file was partially written
        if file_path.exists():
            file_path.unlink()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving file: {str(e)}"
        )


@router.get("/files")
async def list_uploaded_files(
    current_user: dict = Depends(get_current_user),
):
    """
    List all uploaded files in the knowledge base, organized by category.
    
    Returns:
        List of files with their category, name, and size
    """
    category_dirs = {
        "Academic": ACADEMIC_DIR,
        "Administrative": ADMINISTRATIVE_DIR,
        "Educational": EDUCATIONAL_DIR,
    }
    
    files = []
    for category, dir_path in category_dirs.items():
        if not dir_path.exists():
            continue
        for file_path in sorted(dir_path.glob("*.txt")):
            stat = file_path.stat()
            files.append({
                "filename": file_path.name,
                "category": category,
                "size": stat.st_size,
                "modified": stat.st_mtime,
            })
    
    return {"files": files}


@router.delete("/files/{category}/{filename}")
async def delete_uploaded_file(
    category: str,
    filename: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Delete an uploaded file from the knowledge base.
    
    Args:
        category: File category ("Academic", "Administrative", or "Educational")
        filename: Name of the file to delete
        
    Returns:
        Success message
    """
    # Restrict delete access for @pvpsit.ac.in users
    user_email = current_user.get("email", "")
    if user_email.endswith("@pvpsit.ac.in"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="File deletion is not allowed for @pvpsit.ac.in users"
        )
    
    # Validate category
    valid_categories = {"Academic", "Administrative", "Educational"}
    if category not in valid_categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}"
        )
    
    category_dirs = {
        "Academic": ACADEMIC_DIR,
        "Administrative": ADMINISTRATIVE_DIR,
        "Educational": EDUCATIONAL_DIR,
    }
    target_dir = category_dirs[category]
    
    # Sanitize filename to prevent path traversal
    safe_filename = Path(filename).name
    if not safe_filename or safe_filename.startswith('.') or '/' in filename or '\\' in filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename"
        )
    
    file_path = target_dir / safe_filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File '{safe_filename}' not found in {category} category"
        )
    
    try:
        file_path.unlink()
        
        # Remove document vectors from Qdrant
        try:
            from app.vector_store import delete_document
            delete_document(safe_filename, category)
            print(f"Removed vectors for '{safe_filename}' from Qdrant")
        except Exception as vec_err:
            print(f"Warning: Vector deletion failed for '{safe_filename}': {vec_err}")
        
        return {
            "success": True,
            "message": f"File '{safe_filename}' deleted from {category} category",
            "filename": safe_filename,
            "category": category,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting file: {str(e)}"
        )
