"""
Application configuration
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env file from project root (two levels up from this file)
# backend/app/core/config.py -> backend/app -> backend -> project_root
project_root = Path(__file__).parent.parent.parent.parent
env_file_path = project_root / ".env"
load_dotenv(dotenv_path=env_file_path)


class Settings(BaseSettings):
    """Application settings"""

    # API Settings
    app_name: str = "Musical Instrument Manual Q&A API"
    app_version: str = "0.1.0"
    api_prefix: str = "/api"

    # Anthropic Settings (for LLM)
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-haiku-4-5-20251001"

    # OpenAI Settings (for embeddings)
    openai_api_key: Optional[str] = None
    openai_embedding_model: str = "text-embedding-ada-002"

    # ChromaDB Settings
    chroma_db_path: str = "./chroma_db"

    # File Upload Settings
    max_upload_size: int = 50 * 1024 * 1024  # 50MB
    allowed_file_types: list = [".pdf"]

    # CORS Settings
    cors_origins: list = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env file


# Create global settings instance
settings = Settings()
