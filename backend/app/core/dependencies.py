"""
Dependency injection for FastAPI
"""
from functools import lru_cache
from typing import Optional

from app.core.config import settings
from app.services.vector_db.chroma_manager import ChromaManager
from app.services.rag_pipeline.qa_system import MusicalInstrumentQA
from app.services.pdf_processor.pdf_extractor import PDFExtractor


# Singleton instances
_chroma_manager: Optional[ChromaManager] = None
_qa_system: Optional[MusicalInstrumentQA] = None
_pdf_extractor: Optional[PDFExtractor] = None


def get_chroma_manager() -> ChromaManager:
    """Get or create ChromaManager singleton"""
    global _chroma_manager
    if _chroma_manager is None:
        _chroma_manager = ChromaManager(db_path=settings.chroma_db_path)
    return _chroma_manager


def get_qa_system() -> Optional[MusicalInstrumentQA]:
    """Get or create MusicalInstrumentQA singleton"""
    global _qa_system
    if _qa_system is None:
        try:
            chroma_manager = get_chroma_manager()
            _qa_system = MusicalInstrumentQA(
                chroma_manager=chroma_manager,
                model_name=settings.anthropic_model
            )
        except ValueError as e:
            # Anthropic API key not configured
            print(f"QA System initialization failed: {e}")
            return None
    return _qa_system


def get_pdf_extractor() -> PDFExtractor:
    """Get or create PDFExtractor singleton"""
    global _pdf_extractor
    if _pdf_extractor is None:
        _pdf_extractor = PDFExtractor()
    return _pdf_extractor


def reset_singletons():
    """Reset all singleton instances (useful for database reset)"""
    global _chroma_manager, _qa_system, _pdf_extractor
    _chroma_manager = None
    _qa_system = None
    _pdf_extractor = None
