#!/bin/bash

# Musical Instrument Manual Q&A System Startup Script

echo "🎹 Starting Musical Instrument Manual Q&A System..."

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry not found. Please install Poetry first:"
    echo "   curl -sSL https://install.python-poetry.org | python3 -"
    echo "   Or visit: https://python-poetry.org/docs/#installation"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.template .env
    echo "📝 Please edit .env and add your OpenAI API key"
    echo "   Then run this script again"
    exit 1
fi

# Install dependencies with Poetry
echo "📦 Installing dependencies with Poetry..."
poetry install

# Create directories
mkdir -p chroma_db
mkdir -p uploaded_manuals

# Run the application
echo "🚀 Starting Streamlit application..."
echo "   Your browser should open automatically"
echo "   If not, go to: http://localhost:8501"
echo ""

poetry run streamlit run app.py