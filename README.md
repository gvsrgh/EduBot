# EduBot+ - AI University Assistant

An intelligent chatbot for university students powered by local LLMs (Ollama) or cloud providers (OpenAI/Gemini).

## Features

- 🤖 Multi-provider AI support (Ollama, OpenAI, Gemini)
- 💬 Real-time chat with conversation history
- 📚 University knowledge base integration
- 🔒 Secure authentication system
- ⚙️ Admin settings panel
- 🎨 Modern, responsive UI

## Prerequisites

- **Python 3.11+** - Backend runtime
- **Node.js 18+** - Frontend runtime
- **Ollama** - For local AI models (recommended)

## Quick Start

### 1. Install Ollama (Recommended)

Download and install from [ollama.ai](https://ollama.ai)

Pull a model:
```bash
ollama pull llama3.1:8b
```

### 2. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 4. Start the Application

**Option A: Using startup scripts (Windows)**
```bash
# Terminal 1 - Start Backend
start-backend.bat

# Terminal 2 - Start Frontend  
start-frontend.bat
```

**Option B: Manual start**
```bash
# Terminal 1 - Backend
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### 5. Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Configuration

### Backend (.env)

```env
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRY=30
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
DEBUG=True
```

### Using Different AI Providers

1. Go to **Settings** page
2. Select your provider (Ollama/OpenAI/Gemini)
3. Configure API keys (if using cloud providers)
4. Select model
5. Test connection
6. Save settings

## Default Credentials

For testing:
- Email: `test@pvpsiddhartha.ac.in`
- Password: `test@pvpsiddhartha.ac.in`

Admin accounts: `*@pvpsiddhartha.ac.in`

## Project Structure

```
edubot/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app
│   │   ├── config.py         # Configuration
│   │   ├── auth.py           # Authentication
│   │   ├── llm_provider.py   # AI provider management
│   │   ├── graph.py          # LangGraph agent
│   │   ├── tools.py          # Custom tools
│   │   ├── db/               # Database models
│   │   └── routers/          # API endpoints
│   ├── data/                 # Knowledge base files
│   └── requirements.txt
│
└── frontend/
    ├── app/                  # Next.js pages
    ├── lib/                  # Utilities
    └── package.json

## Tech Stack

### Backend
- **FastAPI** - Web framework
- **SQLite** - Database
- **LangChain** - LLM framework
- **LangGraph** - Agent workflow
- **Ollama** - Local LLM runtime

### Frontend
- **Next.js 15** - React framework
- **TypeScript** - Type safety
- **CSS Modules** - Styling

## Development

### Backend Development
```bash
cd backend
python -m uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### Database Migrations
```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## License

MIT License - See LICENSE file for details

Multi-Model AI Chatbot with LangGraph Agent Workflow for university information and support.

## Features

- 🤖 Multi-provider AI support (OpenAI, Google Gemini, Ollama)
- 🔐 User authentication with role-based access
- ⚙️ Admin settings panel for AI configuration
- 💬 Conversational chat interface with message history
- 🔍 Real-time connection testing for AI providers
- 📚 Content management for university information
- 🎨 Modern, responsive UI

## Tech Stack

### Frontend
- Next.js 15
- React 18
- TypeScript
- CSS Modules

### Backend
- FastAPI
- LangChain & LangGraph
- PostgreSQL
- Qdrant (Vector Database)
- SQLAlchemy (Async)
- Alembic (Migrations)

## Local Development

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Quick Start with Docker

1. Clone the repository:
```bash
git clone <repository-url>
cd Project
```

2. Copy environment files:
```bash
cp .env.example backend/.env
cp frontend/.env.example frontend/.env.local
```

3. Update environment variables in `backend/.env` with your API keys

4. Start all services:
```bash
docker-compose up -d
```

5. Access the application:
- Frontend: http://localhost:3001
- Backend API: http://localhost:8001
- API Docs: http://localhost:8001/docs

### Local Development (without Docker)

#### Backend

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run database migrations:
```bash
alembic upgrade head
```

5. Start the server:
```bash
uvicorn app.main:app --reload --port 8001
```

#### Frontend

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env.local` file:
```bash
echo "NEXT_PUBLIC_API_URL=http://localhost:8001/api" > .env.local
```

4. Start the development server:
```bash
npm run dev
```

## Deployment

### Vercel (Frontend)

1. Push your code to GitHub

2. Import the project in Vercel

3. Set the root directory to `frontend`

4. Add environment variable:
   - `NEXT_PUBLIC_API_URL`: Your backend API URL (e.g., https://your-backend.com/api)

5. Deploy!

### Backend Deployment

The backend can be deployed to:
- Railway
- Render
- DigitalOcean App Platform
- AWS/GCP/Azure with Docker

Make sure to:
1. Set up PostgreSQL database
2. Set up Qdrant instance
3. Configure all environment variables
4. Run database migrations
5. Set `DEBUG=False` in production

## Configuration

### AI Providers

The application supports multiple AI providers:

1. **OpenAI GPT-4**: Requires `OPENAI_API_KEY`
2. **Google Gemini**: Requires `GOOGLE_API_KEY`
3. **Ollama (Local)**: Requires running Ollama instance
4. **Auto**: Automatic fallback between providers

Configure in Settings page or via environment variables.

### User Roles

- **Admin** (@pvpsiddhartha.ac.in): Full access to settings and content management
- **Student** (@pvpsit.ac.in): Chat access only

### Environment Variables

See `.env.example` files for required environment variables.

## API Documentation

Access the interactive API documentation at:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## Project Structure

```
Project/
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── routers/      # API routes
│   │   ├── db/           # Database models
│   │   ├── main.py       # FastAPI app
│   │   ├── config.py     # Configuration
│   │   ├── auth.py       # Authentication
│   │   └── llm_provider.py  # AI provider management
│   ├── alembic/          # Database migrations
│   └── requirements.txt
├── frontend/             # Next.js frontend
│   ├── app/             # Next.js 13+ app directory
│   │   ├── chat/        # Chat page
│   │   ├── login/       # Login page
│   │   ├── register/    # Register page
│   │   └── settings/    # Settings page
│   ├── lib/             # Utilities
│   └── package.json
└── docker-compose.yml    # Docker configuration
```

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.
