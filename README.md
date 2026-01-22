# EduBot+ - AI University Assistant

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
