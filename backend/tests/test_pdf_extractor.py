"""
Tests for PDF extraction and metadata processing
"""
import pytest
from pathlib import Path
from app.services.pdf_processor.pdf_extractor import PDFExtractor, ManualMetadata


@pytest.mark.unit
class TestPDFMetadataExtraction:
    """Test PDF metadata extraction"""

    def test_extract_manufacturer_from_filename(self, pdf_extractor):
        """Test manufacturer extraction from filename"""
        filename = "Moog-Minimoog-Manual.pdf"
        text = ""
        manufacturer = pdf_extractor._extract_manufacturer(filename, text)
        assert manufacturer == "Moog"

    def test_extract_manufacturer_from_text(self, pdf_extractor):
        """Test manufacturer extraction from text content"""
        filename = "manual.pdf"
        text = "This is a Roland Jupiter-8 synthesizer manual"
        manufacturer = pdf_extractor._extract_manufacturer(filename, text)
        assert manufacturer == "Roland"

    def test_extract_model_from_filename(self, pdf_extractor):
        """Test model extraction from filename"""
        filename = "Roland-TR-808-Manual.pdf"
        text = ""
        model = pdf_extractor._extract_model(filename, text)
        assert model is not None
        assert "808" in model.upper()

    def test_extract_model_with_dash(self, pdf_extractor):
        """Test model extraction with dash pattern"""
        filename = "JP-8000-manual.pdf"
        text = ""
        model = pdf_extractor._extract_model(filename, text)
        assert model is not None
        assert "8000" in model.upper()

    def test_classify_instrument_type_synthesizer(self, pdf_extractor):
        """Test instrument type classification for synthesizer"""
        filename = "moog-synthesizer.pdf"
        text = "This is a synthesizer with analog oscillators"
        instrument_type = pdf_extractor._classify_instrument_type(filename, text)
        assert instrument_type == "synthesizer"

    def test_classify_instrument_type_mixer(self, pdf_extractor):
        """Test instrument type classification for mixer"""
        filename = "mixer-manual.pdf"
        text = "24 channel mixing console with eq and effects"
        instrument_type = pdf_extractor._classify_instrument_type(filename, text)
        assert instrument_type == "mixer"

    def test_display_name_from_filename(self, pdf_extractor, temp_pdf_file):
        """Test display name generation from filename"""
        # Rename temp file
        new_name = temp_pdf_file.parent / "Test-Manual.pdf"
        temp_pdf_file.rename(new_name)

        text = "Sample text"
        metadata = pdf_extractor.extract_metadata(str(new_name), text, original_filename="Test-Manual.pdf")

        assert metadata.display_name == "Test-Manual"
        assert metadata.filename == "Test-Manual.pdf"

        # Cleanup
        new_name.unlink()

    def test_extract_metadata_with_original_filename(self, pdf_extractor, temp_pdf_file):
        """Test metadata extraction uses original filename when provided"""
        text = "Moog Minimoog synthesizer manual"
        original_filename = "Moog-Minimoog-V2.pdf"

        metadata = pdf_extractor.extract_metadata(str(temp_pdf_file), text, original_filename=original_filename)

        assert metadata.filename == original_filename
        assert metadata.display_name == "Moog-Minimoog-V2"
        assert metadata.manufacturer == "Moog"


@pytest.mark.unit
class TestTextProcessing:
    """Test text processing functions"""

    def test_clean_text_removes_extra_whitespace(self, pdf_extractor):
        """Test text cleaning removes extra whitespace"""
        text = "This  has   extra    spaces"
        cleaned = pdf_extractor._clean_text(text)
        assert "  " not in cleaned
        assert cleaned == "This has extra spaces"

    def test_split_text_with_overlap(self, pdf_extractor):
        """Test text splitting with overlap"""
        text = "a" * 1000  # 1000 character text
        chunks = pdf_extractor._split_text_with_overlap(text, max_size=500, overlap=50)

        assert len(chunks) > 1
        # Check that chunks overlap
        assert len(chunks[0]) <= 500
        assert len(chunks[1]) <= 500

    def test_classify_section_type_specifications(self, pdf_extractor):
        """Test section classification for specifications"""
        text = "Technical Specifications: Frequency Response 20Hz-20kHz"
        section_type = pdf_extractor._classify_section_type(text)
        assert section_type == "specifications"

    def test_classify_section_type_connections(self, pdf_extractor):
        """Test section classification for connections"""
        text = "Connect the MIDI IN port to your computer"
        section_type = pdf_extractor._classify_section_type(text)
        assert section_type == "connections"


@pytest.mark.integration
class TestPDFProcessing:
    """Integration tests for PDF processing"""

    def test_process_manual_returns_chunks_and_metadata(self, pdf_extractor, temp_pdf_file):
        """Test full manual processing returns chunks and metadata"""
        chunks, metadata = pdf_extractor.process_manual(
            str(temp_pdf_file),
            original_filename="Moog-Minimoog-Manual.pdf"
        )

        assert isinstance(chunks, list)
        assert len(chunks) > 0
        assert isinstance(metadata, ManualMetadata)
        assert metadata.filename == "Moog-Minimoog-Manual.pdf"
        assert metadata.total_pages > 0

    def test_chunks_have_correct_structure(self, pdf_extractor, temp_pdf_file):
        """Test that chunks have correct structure and metadata"""
        chunks, metadata = pdf_extractor.process_manual(
            str(temp_pdf_file),
            original_filename="Test-Manual.pdf"
        )

        for chunk in chunks:
            assert hasattr(chunk, 'content')
            assert hasattr(chunk, 'page_number')
            assert hasattr(chunk, 'chunk_index')
            assert hasattr(chunk, 'metadata')
            assert chunk.content  # Not empty
            assert chunk.page_number > 0
            assert chunk.metadata.filename == "Test-Manual.pdf"
