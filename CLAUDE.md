# Musical Instrument Manual Q&A System

A RAG-powered Q&A system for musical instrument manuals with a React frontend and FastAPI backend.

## 🎯 Project Overview

This application allows musicians and audio engineers to upload PDF manuals for their musical instruments (synthesizers, keyboards, mixers, etc.) and ask natural language questions about them. The system uses Retrieval Augmented Generation (RAG) to provide accurate, context-aware answers with source citations.

## 🏗️ Architecture

```
📁 backend/
└── 📁 app/
    ├── 📁 api/
    │   ├── 📁 routes/        # API endpoints (manuals, qa, stats)
    │   └── 📁 models/        # Pydantic schemas
    ├── 📁 core/             # Configuration and dependencies
    ├── 📁 services/
    │   ├── 📁 pdf_processor/    # PDF text extraction and chunking
    │   ├── 📁 vector_db/        # ChromaDB vector database management
    │   └── 📁 rag_pipeline/     # Q&A system with LangChain + OpenAI
    └── 📄 main.py           # FastAPI application entry point

📁 frontend/
└── 📁 src/
    ├── 📄 App.tsx           # React application
    └── 📄 main.tsx          # Application entry point

📄 pyproject.toml        # Poetry dependencies and configuration
📄 test_setup.py         # Setup verification script
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+** with Poetry for backend dependencies
- **Node.js 18+** with npm for frontend dependencies

### Setup

1. **Install Poetry** (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Install backend dependencies**:
   ```bash
   poetry install
   ```

3. **Install frontend dependencies**:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Set up environment**:
   ```bash
   cp .env.template .env
   # Edit .env and add your OPENAI_API_KEY
   ```

5. **Test setup** (optional):
   ```bash
   poetry run python test_setup.py
   ```

### Running the Application

You need to run **both** the backend and frontend servers:

#### Option 1: Run both servers separately

**Terminal 1 - Backend (FastAPI)**:
```bash
cd backend
poetry run python -m app.main
# Backend runs on http://localhost:8000
```

**Terminal 2 - Frontend (React + Vite)**:
```bash
cd frontend
npm run dev
# Frontend runs on http://localhost:5173
```

#### Option 2: Use the startup script (coming soon)
```bash
./run.sh  # Will start both servers
```

Then open your browser to **http://localhost:5173** to use the application.

## 🔧 Development Commands

### Backend Commands

```bash
# Run setup verification
poetry run python test_setup.py

# Start backend server (development mode with auto-reload)
cd backend
poetry run python -m app.main
# Or with uvicorn directly:
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Code formatting
poetry run black backend/
poetry run isort backend/

# Type checking
poetry run mypy backend/

# Linting
poetry run flake8 backend/

# View API documentation
# Start the backend, then visit:
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
```

### Frontend Commands

```bash
cd frontend

# Start development server (with hot reload)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Linting
npm run lint
```

## 📁 Project Structure

### Backend Components (`backend/app/`)

- **API Routes** (`api/routes/`):
  - `manuals.py`: Manual upload, processing, save, list, delete endpoints
  - `qa.py`: Question answering, suggestions, conversation history
  - `stats.py`: Database statistics, filters, database reset

- **Services** (`services/`):
  - **PDF Processor** (`pdf_processor/`):
    - Extracts text from PDFs using PyMuPDF and PyPDF2
    - Intelligent chunking with overlap for better context
    - Metadata extraction (manufacturer, model, instrument type)
    - Section classification (specs, connections, operation, etc.)

  - **Vector Database** (`vector_db/`):
    - ChromaDB integration for semantic search
    - Hybrid search (semantic + keyword matching)
    - Metadata filtering by manufacturer, type, etc.
    - Database reset and management functions

  - **RAG Pipeline** (`rag_pipeline/`):
    - LangChain integration with OpenAI
    - Context-aware Q&A with conversation memory
    - Source citation with page references
    - Musical instrument domain expertise

- **Core** (`core/`):
  - `config.py`: Configuration management
  - `dependencies.py`: Dependency injection for FastAPI

- **Main** (`main.py`):
  - FastAPI application with CORS configuration
  - API documentation at `/docs` and `/redoc`
  - Health check endpoint at `/health`

### Frontend Components (`frontend/src/`)

- **React Application** (`App.tsx`):
  - Modern React 18+ with TypeScript
  - Vite for fast development and builds
  - Tailwind CSS for styling
  - Axios for API communication

- **Features**:
  - Two-stage upload with metadata editing
  - Real-time Q&A with source display
  - Manual management interface
  - Database statistics and filters

### Key Features

1. **Two-Stage Upload Process**:
   - Stage 1: Upload PDF → Auto-detect metadata
   - Stage 2: Review/edit metadata (manufacturer, model, type)
   - Stage 3: Save to vector database

2. **Flexible Metadata Editing**:
   - Quick-select dropdowns for common values
   - Custom text input for any manufacturer/instrument type
   - Display names for better source citations

3. **Advanced Search & Filtering**:
   - Semantic similarity search
   - Keyword-based filtering
   - Manufacturer and instrument type filters
   - Hybrid search combining multiple methods

4. **Source Citations**:
   - References specific manual pages
   - Shows manufacturer, model, and section type
   - Content previews for verification

## 🔑 Environment Variables

Create `.env` file with:

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
CHROMA_DB_PATH=./chroma_db
```

## 🗂️ Supported File Types

- **PDFs**: Primary format for instrument manuals
- **Text extraction**: Handles both text-based and image-based PDFs
- **OCR fallback**: Uses pytesseract for scanned documents

## 📊 Database Management

### ChromaDB Operations
- **Location**: `./chroma_db/` (configurable)
- **Collections**: `manual_chunks` with embeddings
- **Metadata**: Filename, display_name, manufacturer, model, etc.
- **Reset**: Complete database reset with confirmation

### Manual Management
- Upload new manuals with metadata editing
- View all uploaded manuals with statistics
- Delete individual manuals
- Database statistics (chunk count, manufacturers, etc.)

## 🎵 Supported Instruments

The system is optimized for musical equipment manuals:

- **Synthesizers**: Moog, Roland, Korg, Sequential, etc.
- **Keyboards**: Digital pianos, workstations, controllers
- **Drum Machines**: TR-series, MPC, etc.
- **Mixers**: Analog and digital mixing consoles
- **Audio Interfaces**: USB, Firewire, Thunderbolt
- **Modular Gear**: Eurorack modules, CV/Gate equipment
- **Effects**: Reverbs, delays, compressors, etc.

## 🔍 Example Questions

- "How do I set up MIDI connections on my Moog?"
- "What are the CV/Gate specifications?"
- "How do I save and load presets?"
- "How do I connect to my computer via USB?"
- "What is the power consumption?"
- "How do I perform a factory reset?"
- "How do the filters work on this synthesizer?"

## 🐛 Troubleshooting

### Common Issues

1. **OpenAI API Key Error**:
   ```bash
   # Check if .env file exists and contains OPENAI_API_KEY
   cat .env | grep OPENAI_API_KEY
   ```

2. **Import Errors**:
   ```bash
   # Reinstall dependencies
   poetry install --no-cache
   ```

3. **ChromaDB Issues**:
   ```bash
   # Reset database using the UI reset button
   # Or manually delete: rm -rf chroma_db/
   ```

4. **PDF Processing Errors**:
   ```bash
   # Install system dependencies for PyMuPDF
   # macOS: brew install mupdf
   # Ubuntu: apt-get install libmupdf-dev
   ```

### Performance Tips

- **Large PDFs**: The system automatically chunks large documents
- **Memory Usage**: ChromaDB keeps embeddings in memory for fast search
- **Batch Uploads**: Process multiple manuals sequentially for best results

## 📝 Development Notes

### Adding New Features

1. **New Instrument Types**: Update `instrument_keywords` in `pdf_extractor.py`
2. **New Manufacturers**: Add to suggestions in `main_interface.py`
3. **Custom Sections**: Extend `section_keywords` for better classification
4. **UI Improvements**: Modify `main_interface.py` Streamlit components

### Code Style

- **Formatting**: Black with 100-character line length
- **Imports**: isort with Black profile
- **Type Hints**: mypy for static type checking
- **Documentation**: Docstrings for all public methods

### Testing

Run the setup verification script to ensure all components work:

```bash
poetry run python test_setup.py
```

## 📄 License

This project was created with Claude Code assistance and follows best practices for RAG applications.

---

## 🌐 API Endpoints

The FastAPI backend provides the following REST API endpoints:

### Manuals
- `POST /api/manuals/process` - Upload and process PDF (Stage 1)
- `POST /api/manuals/save` - Save manual with metadata (Stage 2)
- `GET /api/manuals/` - List all manuals
- `DELETE /api/manuals/{filename}` - Delete a manual
- `POST /api/manuals/cancel/{filename}` - Cancel pending upload

### Q&A
- `POST /api/qa/ask` - Ask a question
- `POST /api/qa/suggestions` - Get suggested questions
- `GET /api/qa/history` - Get conversation history
- `DELETE /api/qa/history` - Clear conversation history

### Statistics & Filters
- `GET /api/stats` - Get database statistics
- `POST /api/database/reset` - Reset entire database
- `GET /api/filters/manufacturers` - Get unique manufacturers
- `GET /api/filters/instrument-types` - Get unique instrument types

### System
- `GET /` - API information
- `GET /health` - Health check
- `GET /docs` - Swagger UI documentation
- `GET /redoc` - ReDoc documentation

## 🤖 Claude Code Integration

This project is optimized for Claude Code development:

### Recommended Commands

```bash
# Quick setup verification
poetry run python test_setup.py

# Start backend development server
cd backend && poetry run python -m app.main

# Start frontend development server
cd frontend && npm run dev

# Format and check backend code
poetry run black backend/ && poetry run isort backend/ && poetry run mypy backend/

# Lint frontend code
cd frontend && npm run lint
```

### Project Conventions

- **Poetry**: Dependency management and virtual environments
- **Type Hints**: Full typing support for better Claude Code assistance
- **Modular Structure**: Clear separation of concerns for easy modifications
- **Comprehensive Logging**: Debug information for troubleshooting

This CLAUDE.md file serves as a complete reference for Claude Code to understand the project structure, run common commands, and assist with development tasks.