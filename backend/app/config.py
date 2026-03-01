import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Database Configuration - PostgreSQL Only
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is required. "
        "Please set it in your .env file with your PostgreSQL connection string."
    )

# For sync operations (if needed)
DATABASE_URL_SYNC = os.getenv("DATABASE_URL_SYNC")

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not JWT_SECRET_KEY:
    raise ValueError(
        "JWT_SECRET_KEY environment variable is required. "
        "Please set it in your .env file with a strong secret key."
    )

JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRY = int(os.getenv("JWT_EXPIRY", "30"))  # days

# Application Settings
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

# Data Files
DATA_DIR = Path(__file__).parent.parent / "data"

# Category directories
ACADEMIC_DIR = DATA_DIR / "Academic"
ADMINISTRATIVE_DIR = DATA_DIR / "Administrative"
EDUCATIONAL_DIR = DATA_DIR / "Educational"

# Upload configuration
ALLOWED_EXTENSIONS = {'.txt', '.pdf', '.docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Qdrant Vector Database
QDRANT_URL = os.getenv("QDRANT_URL", "")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
