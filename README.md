# Musical Instrument Manual Q&A System

A RAG-powered system for asking questions about your musical instrument manuals.

## Prerequisites

- Python 3.8 or higher
- [Poetry](https://python-poetry.org/) for dependency management

## Setup

1. **Install Poetry** (if not already installed):
```bash
# On macOS/Linux
curl -sSL https://install.python-poetry.org | python3 -

# On Windows (PowerShell)
Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing | Invoke-Expression
```

2. **Install dependencies**:
```bash
poetry install
```

3. **Configure environment variables**:
```bash
cp .env.template .env
# Edit .env with your OpenAI API key
```

4. **Run the application**:
```bash
poetry run streamlit run app.py
```

### Quick Start Scripts

For convenience, use the provided startup scripts:

```bash
# macOS/Linux
./run.sh

# Windows
run.bat
```

## Features

- Upload PDF manuals for synthesizers, keyboards, mixers, etc.
- Ask natural language questions about your instruments
- Get answers with source citations from your manuals
- Semantic search across all uploaded manuals
- Conversation memory for follow-up questions

## Supported Formats

- PDF files (text-based and scanned with OCR)
- Extracts text, tables, and technical specifications
- Handles connection diagrams and MIDI mappings

## Usage

1. Upload your instrument manuals using the sidebar
2. Ask questions like:
   - "How do I connect my Moog to MIDI?"
   - "What are the filter specifications for the Roland Jupiter?"
   - "How do I set up CV sync between modules?"
3. Review answers with source citations from your manuals