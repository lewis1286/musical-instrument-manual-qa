# Musical Instrument Manual Q&A System

A RAG-powered system for asking questions about your musical instrument manuals with a modern React frontend and FastAPI backend.

## Prerequisites

- **Python 3.11+** - Backend runtime
- **Node.js 18+** - Frontend runtime
- [Poetry](https://python-poetry.org/) - Python dependency management
- npm - JavaScript package manager (comes with Node.js)

## Setup

### 1. Install Poetry (if not already installed)

```bash
# On macOS/Linux
curl -sSL https://install.python-poetry.org | python3 -

# On Windows (PowerShell)
Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing | Invoke-Expression
```

### 2. Install Backend Dependencies

```bash
poetry install
```

### 3. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

### 4. Configure Environment Variables

```bash
cp .env.template .env
# Edit .env and add your OPENAI_API_KEY
```

## Running the Application

You need to run **both** the backend and frontend servers:

### Terminal 1 - Start Backend (FastAPI)

```bash
cd backend
poetry run python -m app.main
```

The backend API will be available at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Terminal 2 - Start Frontend (React + Vite)

```bash
cd frontend
npm run dev
```

The frontend will be available at:
- **Application**: http://localhost:5173

### Quick Start Script (Coming Soon)

```bash
# macOS/Linux
./run.sh

# Windows
run.bat
```

## Features

- **Two-stage upload process**: Upload PDF → Review/edit metadata → Save to database
- **Intelligent Q&A**: Ask natural language questions about your instruments
- **Source citations**: Get answers with page references from your manuals
- **Semantic search**: Advanced RAG-powered search across all uploaded manuals
- **Conversation memory**: Follow-up questions with context awareness
- **Filter by metadata**: Search by manufacturer, instrument type, or specific models
- **Database management**: View statistics, manage manuals, reset database

## Technology Stack

### Backend
- **FastAPI**: Modern, fast Python web framework
- **LangChain**: RAG pipeline orchestration
- **ChromaDB**: Vector database for semantic search
- **OpenAI**: LLM for question answering
- **PyMuPDF & PyPDF2**: PDF text extraction
- **Python 3.11+**: Runtime environment

### Frontend
- **React 18**: Modern UI framework
- **TypeScript**: Type-safe JavaScript
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first styling
- **Axios**: HTTP client for API calls

## Supported Formats

- PDF files (text-based and scanned with OCR)
- Extracts text, tables, and technical specifications
- Handles connection diagrams and MIDI mappings
- Auto-detects manufacturer, model, and instrument type

## Usage

1. **Upload manuals**:
   - Click upload button
   - Review auto-detected metadata (manufacturer, model, instrument type)
   - Edit metadata if needed
   - Save to database

2. **Ask questions**:
   - "How do I connect my Moog to MIDI?"
   - "What are the filter specifications for the Roland Jupiter?"
   - "How do I set up CV sync between modules?"
   - "What is the power consumption of my mixer?"

3. **Review answers**: Get detailed responses with source citations showing:
   - Manual name and page number
   - Manufacturer and model
   - Content preview from relevant sections

## API Documentation

Once the backend is running, view interactive API documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Development

### Backend Development

```bash
cd backend

# Start with auto-reload
poetry run python -m app.main

# Or with uvicorn directly
poetry run uvicorn app.main:app --reload

# Format code
poetry run black backend/
poetry run isort backend/

# Type checking
poetry run mypy backend/
```

### Frontend Development

```bash
cd frontend

# Start dev server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint
npm run lint
```

## Testing

The project has comprehensive test coverage for both backend and frontend.

### Backend Tests (pytest)

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Run only unit tests
poetry run pytest -m unit

# Run specific test file
poetry run pytest backend/tests/test_pdf_extractor.py
```

### Frontend Tests (Vitest)

```bash
cd frontend

# Run all tests
npm test

# Run with UI
npm test:ui

# Run with coverage
npm test:coverage
```

**For detailed testing documentation, see [TESTING.md](./TESTING.md)**

## Troubleshooting

### Backend Issues

**OpenAI API Key Error**:
```bash
# Verify .env file has OPENAI_API_KEY
cat .env | grep OPENAI_API_KEY
```

**Import Errors**:
```bash
# Reinstall dependencies
poetry install --no-cache
```

**ChromaDB Issues**:
```bash
# Reset database via API or manually delete
rm -rf chroma_db/
```

### Frontend Issues

**Port already in use**:
```bash
# Vite will automatically try the next available port
# Or specify a custom port in vite.config.ts
```

**Dependencies not installed**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## Project Structure

```
📁 backend/
└── 📁 app/
    ├── 📁 api/routes/      # API endpoints
    ├── 📁 services/        # Business logic
    ├── 📁 core/            # Config & dependencies
    └── 📄 main.py          # FastAPI app

📁 frontend/
└── 📁 src/
    ├── 📄 App.tsx          # Main React component
    └── 📄 main.tsx         # Entry point

📄 .env                     # Environment variables
📄 pyproject.toml          # Python dependencies
📄 package.json            # JavaScript dependencies
```

For more detailed documentation, see [CLAUDE.md](./CLAUDE.md).