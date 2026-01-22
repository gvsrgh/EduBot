# EduBot - AI University Assistant

An intelligent chatbot that helps university students get answers about academic calendars, university information, and educational resources. The system uses AI language models to provide conversational responses powered by local LLMs (Ollama) or cloud providers (OpenAI/Gemini).

## What Does This Project Do?

EduBot is a web-based chatbot application designed for university students and staff. It provides:

- **Intelligent Q&A**: Ask questions about university schedules, policies, and resources
- **Multi-AI Support**: Choose between local AI (Ollama) or cloud services (OpenAI, Gemini)
- **Chat History**: Keep track of all your conversations
- **Role-Based Access**: Different features for students and administrators
- **Knowledge Base**: Pre-loaded with university information (academic calendar, policies, etc.)

## Prerequisites

Before you start, make sure you have:

- **Python 3.11 or higher** - For the backend server
- **Node.js 18 or higher** - For the frontend website
- **Ollama** (recommended) - For running AI models locally

## Quick Start Guide

### Step 1: Install Ollama (Recommended)

1. Download Ollama from [ollama.ai](https://ollama.ai)
2. Install it on your computer
3. Open a terminal and run:

```bash
ollama pull llama3.1:8b
```

This downloads an AI model to your computer.

### Step 2: Setup Backend

Open a terminal and run:

```bash
cd backend
pip install -r requirements.txt
```

This installs all the Python libraries needed for the backend.

### Step 3: Setup Frontend

Open a new terminal and run:

```bash
cd frontend
npm install
```

This installs all the Node.js libraries needed for the frontend.

### Step 4: Start the Application

**Terminal 1 - Start the Backend:**

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Start the Frontend:**

```bash
cd frontend
npm run dev
```

### Step 5: Open the Application

Open your web browser and go to:

- **Main App**: `http://localhost:3000`
- **API Documentation**: `http://localhost:8000/docs`

## Test Account

You can log in with these credentials:

- **Email**: `test@pvpsiddhartha.ac.in`
- **Password**: `test@pvpsiddhartha.ac.in`

Note: Accounts with email ending in `@pvpsiddhartha.ac.in` have admin access.

## How to Use Different AI Providers

1. Log in to the application
2. Go to the **Settings** page
3. Select your AI provider:
   - **Ollama** (local, free, requires Ollama installed)
   - **OpenAI** (cloud, requires API key)
   - **Gemini** (cloud, requires API key)
4. If using cloud providers, enter your API key
5. Select the AI model you want to use
6. Click **Test Connection** to verify it works
7. Click **Save Settings**

## Project Structure

```
Project/
├── backend/                  # Python backend server
│   ├── app/
│   │   ├── main.py          # Main application entry
│   │   ├── config.py        # Configuration settings
│   │   ├── auth.py          # User authentication
│   │   ├── llm_provider.py  # AI model provider logic
│   │   ├── graph.py         # LangGraph agent workflow
│   │   ├── tools.py         # Custom AI tools
│   │   ├── schemas.py       # Data validation schemas
│   │   ├── db/              # Database models and setup
│   │   └── routers/         # API endpoints
│   ├── data/                # University knowledge base
│   │   ├── Academic/        # Academic calendar info
│   │   ├── Administrative/  # University policies
│   │   └── Educational/     # Course information
│   └── requirements.txt     # Python dependencies
│
└── frontend/                # Next.js frontend website
    ├── app/
    │   ├── page.tsx         # Home page
    │   ├── layout.tsx       # App layout
    │   ├── chat/            # Chat interface
    │   ├── login/           # Login page
    │   ├── register/        # Registration page
    │   └── settings/        # Settings page
    ├── lib/                 # Utility functions
    │   ├── api.ts           # API client
    │   ├── auth-context.tsx # Authentication context
    │   └── types.ts         # TypeScript types
    └── package.json         # Node.js dependencies
```

## Technologies Used

### Backend
- **FastAPI** - Modern Python web framework
- **SQLite** - Lightweight database
- **LangChain** - Framework for AI applications
- **LangGraph** - Agent workflow orchestration
- **Ollama** - Local AI model runtime
- **JWT** - Secure authentication

### Frontend
- **Next.js 15** - React framework
- **TypeScript** - Type-safe JavaScript
- **React 18** - UI library
- **CSS Modules** - Component styling

## Configuration

The backend uses environment variables for configuration. Create a `.env` file in the `backend` folder:

```env
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRY=30
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
DEBUG=True
```

## API Documentation

When the backend is running, you can view the API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## For Developers

### Running Backend in Development Mode

```bash
cd backend
python -m uvicorn app.main:app --reload
```

The `--reload` flag automatically restarts the server when you change code.

### Running Frontend in Development Mode

```bash
cd frontend
npm run dev
```

This starts the Next.js development server with hot reload.

### Database Migrations

If you make changes to the database models:

```bash
cd backend
alembic revision --autogenerate -m "description of change"
alembic upgrade head
```

## License

This project is licensed under the MIT License.

## Support

For questions or issues, please contact the development team or open an issue on GitHub.
