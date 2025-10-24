"""
Dependency injection for FastAPI
"""
from functools import lru_cache
from typing import Optional

from app.core.config import settings
from app.services.vector_db.chroma_manager import ChromaManager
from app.services.vector_db.module_inventory import ModuleInventoryManager
from app.services.rag_pipeline.qa_system import MusicalInstrumentQA
from app.services.pdf_processor.pdf_extractor import PDFExtractor
from app.services.patch_advisor import PatchAdvisor


# Singleton instances
_chroma_manager: Optional[ChromaManager] = None
_module_inventory: Optional[ModuleInventoryManager] = None
_qa_system: Optional[MusicalInstrumentQA] = None
_pdf_extractor: Optional[PDFExtractor] = None
_patch_advisor: Optional[PatchAdvisor] = None


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


def get_module_inventory() -> ModuleInventoryManager:
    """Get or create ModuleInventoryManager singleton"""
    global _module_inventory
    if _module_inventory is None:
        _module_inventory = ModuleInventoryManager(db_path=settings.chroma_db_path)
    return _module_inventory


def get_patch_advisor() -> Optional[PatchAdvisor]:
    """Get or create PatchAdvisor singleton"""
    global _patch_advisor
    if _patch_advisor is None:
        try:
            module_inventory = get_module_inventory()
            _patch_advisor = PatchAdvisor(module_inventory=module_inventory)
        except ValueError as e:
            # Anthropic API key not configured
            print(f"Patch Advisor initialization failed: {e}")
            return None
    return _patch_advisor


def reset_singletons():
    """Reset all singleton instances (useful for database reset)"""
    global _chroma_manager, _module_inventory, _qa_system, _pdf_extractor, _patch_advisor
    _chroma_manager = None
    _module_inventory = None
    _qa_system = None
    _pdf_extractor = None
    _patch_advisor = None
