import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/edubot")
DATABASE_URL_SYNC = os.getenv("DATABASE_URL_SYNC", "postgresql://user:password@localhost:5432/edubot")

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRY = int(os.getenv("JWT_EXPIRY", "30"))  # days

# AI Provider Configuration
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai").lower()  # openai, gemini, ollama, auto

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

# Google Gemini Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")

# Ollama Configuration (Local Model)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma:7b")

# Application Settings
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

# Data Files
DATA_DIR = Path(__file__).parent.parent / "data"
UNIVERSITY_INFO_FILE = DATA_DIR / "university_info.txt"
ACADEMIC_CALENDAR_FILE = DATA_DIR / "academic_calendar.txt"
