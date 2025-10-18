"""
Pytest configuration and fixtures for Musical Instrument Manual Q&A tests
"""
import os
import tempfile
from pathlib import Path
from typing import Generator
import pytest
from fastapi.testclient import TestClient

# Set test environment variables
os.environ["OPENAI_API_KEY"] = "test-key-for-testing"
os.environ["CHROMA_DB_PATH"] = ":memory:"  # Use in-memory database for tests

from app.main import app
from app.services.pdf_processor.pdf_extractor import PDFExtractor
from app.services.vector_db.chroma_manager import ChromaManager


@pytest.fixture
def test_client() -> Generator[TestClient, None, None]:
    """Create a test client for FastAPI"""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def pdf_extractor() -> PDFExtractor:
    """Create a PDF extractor instance"""
    return PDFExtractor()


@pytest.fixture
def temp_pdf_file() -> Generator[Path, None, None]:
    """Create a temporary PDF file for testing"""
    # Create a minimal PDF content (this is a very basic PDF structure)
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/Resources <<
/Font <<
/F1 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
>>
>>
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 55
>>
stream
BT
/F1 24 Tf
100 700 Td
(Moog Minimoog Manual) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000366 00000 n
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
470
%%EOF"""

    with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as f:
        f.write(pdf_content)
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def sample_manual_metadata():
    """Sample manual metadata for testing"""
    return {
        "filename": "Moog-Minimoog-Manual.pdf",
        "display_name": "Moog Minimoog Manual",
        "manufacturer": "Moog",
        "model": "Minimoog",
        "instrument_type": "synthesizer",
        "total_pages": 50
    }


@pytest.fixture
def mock_chroma_manager(mocker):
    """Mock ChromaManager for testing without actual database"""
    mock = mocker.Mock(spec=ChromaManager)
    mock.add_manual_chunks.return_value = None
    mock.search_similar.return_value = []
    mock.get_all_manuals.return_value = []
    mock.delete_manual.return_value = True
    mock.get_database_stats.return_value = {
        "total_manuals": 0,
        "total_chunks": 0,
        "manufacturers": [],
        "instrument_types": [],
        "section_types": []
    }
    return mock
