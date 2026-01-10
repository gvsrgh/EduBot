# EduBot+ Backend - Python FastAPI with LangGraph
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy application code first
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    sqlalchemy[asyncio] \
    asyncpg \
    aiosqlite \
    alembic \
    python-jose[cryptography] \
    passlib[bcrypt] \
    python-multipart \
    pydantic[email] \
    pydantic-settings \
    langchain==0.3.27 \
    langchain-core==0.3.81 \
    langgraph==0.6.8 \
    langchain-openai \
    langchain-google-genai \
    langchain-ollama \
    langchain-huggingface==0.2.0 \
    python-dotenv

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
