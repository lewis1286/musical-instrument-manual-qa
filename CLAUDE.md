# Musical Instrument Manual Q&A System

A RAG-powered Q&A system for musical instrument manuals using ChromaDB, OpenAI, and Streamlit.

## 🎯 Project Overview

This application allows musicians and audio engineers to upload PDF manuals for their musical instruments (synthesizers, keyboards, mixers, etc.) and ask natural language questions about them. The system uses Retrieval Augmented Generation (RAG) to provide accurate, context-aware answers with source citations.

## 🏗️ Architecture

```
📁 src/
├── 📁 pdf_processor/     # PDF text extraction and chunking
├── 📁 vector_db/        # ChromaDB vector database management
├── 📁 rag_pipeline/     # Q&A system with LangChain + OpenAI
└── 📁 ui/              # Streamlit web interface

📄 app.py               # Main application entry point
📄 pyproject.toml       # Poetry dependencies and configuration
📄 test_setup.py        # Setup verification script
```

## 🚀 Quick Start

1. **Install Poetry** (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Install dependencies**:
   ```bash
   poetry install
   ```

3. **Set up environment**:
   ```bash
   cp .env.template .env
   # Edit .env and add your OPENAI_API_KEY
   ```

4. **Test setup**:
   ```bash
   poetry run python test_setup.py
   ```

5. **Run application**:
   ```bash
   poetry run streamlit run app.py
   # Or use the convenience script:
   ./run.sh
   ```

## 🔧 Development Commands

### Testing and Quality
```bash
# Run setup verification
poetry run python test_setup.py

# Code formatting
poetry run black src/
poetry run isort src/

# Type checking
poetry run mypy src/

# Linting
poetry run flake8 src/
```

### Application Management
```bash
# Start application
poetry run streamlit run app.py

# Start with custom port
poetry run streamlit run app.py --server.port 8501

# Development mode (auto-reload)
poetry run streamlit run app.py --server.runOnSave true
```

## 📁 Project Structure

### Core Components

- **PDF Processor** (`src/pdf_processor/`):
  - Extracts text from PDFs using PyMuPDF and PyPDF2
  - Intelligent chunking with overlap for better context
  - Metadata extraction (manufacturer, model, instrument type)
  - Section classification (specs, connections, operation, etc.)

- **Vector Database** (`src/vector_db/`):
  - ChromaDB integration for semantic search
  - Hybrid search (semantic + keyword matching)
  - Metadata filtering by manufacturer, type, etc.
  - Database reset and management functions

- **RAG Pipeline** (`src/rag_pipeline/`):
  - LangChain integration with OpenAI
  - Context-aware Q&A with conversation memory
  - Source citation with page references
  - Musical instrument domain expertise

- **UI Interface** (`src/ui/`):
  - Streamlit web application
  - Two-stage upload with metadata editing
  - Real-time Q&A with source display
  - Manual management and database statistics

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

## 🤖 Claude Code Integration

This project is optimized for Claude Code development:

### Recommended Commands

```bash
# Quick setup verification
poetry run python test_setup.py

# Start development server
poetry run streamlit run app.py

# Format and check code
poetry run black src/ && poetry run isort src/ && poetry run mypy src/
```

### Project Conventions

- **Poetry**: Dependency management and virtual environments
- **Type Hints**: Full typing support for better Claude Code assistance
- **Modular Structure**: Clear separation of concerns for easy modifications
- **Comprehensive Logging**: Debug information for troubleshooting

This CLAUDE.md file serves as a complete reference for Claude Code to understand the project structure, run common commands, and assist with development tasks.