@echo off
echo 🎹 Starting Musical Instrument Manual Q&A System...

REM Check if Poetry is installed
poetry --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Poetry not found. Please install Poetry first:
    echo    Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing ^| Invoke-Expression
    echo    Or visit: https://python-poetry.org/docs/#installation
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo ⚠️  .env file not found. Creating from template...
    copy .env.template .env
    echo 📝 Please edit .env and add your OpenAI API key
    echo    Then run this script again
    pause
    exit /b 1
)

REM Install dependencies with Poetry
echo 📦 Installing dependencies with Poetry...
poetry install

REM Create directories
if not exist chroma_db mkdir chroma_db
if not exist uploaded_manuals mkdir uploaded_manuals

REM Run the application
echo 🚀 Starting Streamlit application...
echo    Your browser should open automatically
echo    If not, go to: http://localhost:8501
echo.

poetry run streamlit run app.py