"""
Application configuration
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # API Settings
    app_name: str = "Musical Instrument Manual Q&A API"
    app_version: str = "0.1.0"
    api_prefix: str = "/api"

    # OpenAI Settings
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"

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
