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
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
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

# Legacy file paths (for backward compatibility)
UNIVERSITY_INFO_FILE = ADMINISTRATIVE_DIR / "university_info.txt"
ACADEMIC_CALENDAR_FILE = ACADEMIC_DIR / "academic_calendar.txt"

# Upload configuration
ALLOWED_EXTENSIONS = {'.txt'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
