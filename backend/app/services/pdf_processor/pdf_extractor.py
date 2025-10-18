import os
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import PyPDF2
import pytesseract
from PIL import Image
import fitz  # PyMuPDF for better PDF handling

@dataclass
class ManualMetadata:
    """Metadata extracted from manual"""
    filename: str
    display_name: str = ""
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    instrument_type: Optional[str] = None
    total_pages: int = 0
    language: str = "english"

@dataclass
class DocumentChunk:
    """A chunk of text from a manual with metadata"""
    content: str
    page_number: int
    chunk_index: int
    section_type: Optional[str] = None
    metadata: Optional[ManualMetadata] = None

class PDFExtractor:
    """Extract and process content from musical instrument manual PDFs"""

    def __init__(self):
        self.instrument_keywords = {
            'synthesizer': ['synthesizer', 'synth', 'moog', 'prophet', 'juno', 'jupiter', 'matrix'],
            'keyboard': ['keyboard', 'piano', 'electric piano', 'stage piano', 'workstation'],
            'drum_machine': ['drum machine', 'rhythm', 'beats', 'tr-', 'sp-', 'mpc'],
            'mixer': ['mixer', 'mixing', 'console', 'channels', 'eq', 'effects'],
            'interface': ['audio interface', 'usb interface', 'firewire', 'thunderbolt'],
            'controller': ['midi controller', 'control surface', 'launchpad', 'push'],
            'modular': ['modular', 'eurorack', 'cv', 'gate', 'patch', 'module'],
            'sampler': ['sampler', 'sampling', 'samples', 'multisampling']
        }

        self.section_keywords = {
            'specifications': ['specifications', 'specs', 'technical data', 'dimensions'],
            'connections': ['connections', 'inputs', 'outputs', 'midi', 'cv', 'audio'],
            'setup': ['setup', 'installation', 'getting started', 'quick start'],
            'operation': ['operation', 'using', 'controls', 'interface', 'display'],
            'programming': ['programming', 'editing', 'presets', 'patches', 'sounds'],
            'troubleshooting': ['troubleshooting', 'problems', 'issues', 'faq']
        }

    def extract_text_from_pdf(self, pdf_path: str) -> List[Tuple[str, int]]:
        """Extract text from PDF, returning list of (text, page_number) tuples"""
        pages_text = []

        try:
            # Try PyMuPDF first (better text extraction)
            doc = fitz.open(pdf_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                pages_text.append((text, page_num + 1))
            doc.close()

        except Exception as e:
            print(f"PyMuPDF failed, trying PyPDF2: {e}")
            # Fallback to PyPDF2
            try:
                with open(pdf_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for page_num, page in enumerate(reader.pages):
                        text = page.extract_text()
                        pages_text.append((text, page_num + 1))
            except Exception as e2:
                print(f"PyPDF2 also failed: {e2}")

        return pages_text

    def extract_metadata(self, pdf_path: str, text_content: str, original_filename: Optional[str] = None) -> ManualMetadata:
        """Extract metadata from PDF and text content"""
        filename = original_filename if original_filename else Path(pdf_path).name

        # Try to identify manufacturer and model from filename and text
        manufacturer = self._extract_manufacturer(filename, text_content)
        model = self._extract_model(filename, text_content)
        instrument_type = self._classify_instrument_type(filename, text_content)

        # Get page count
        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            doc.close()
        except:
            total_pages = 0

        # Create default display name (filename without .pdf extension)
        display_name = filename.replace('.pdf', '').replace('.PDF', '')

        return ManualMetadata(
            filename=filename,
            display_name=display_name,
            manufacturer=manufacturer,
            model=model,
            instrument_type=instrument_type,
            total_pages=total_pages
        )

    def _extract_manufacturer(self, filename: str, text: str) -> Optional[str]:
        """Extract manufacturer name from filename or text"""
        manufacturers = [
            'moog', 'roland', 'korg', 'yamaha', 'nord', 'dave smith', 'sequential',
            'arturia', 'novation', 'akai', 'elektron', 'teenage engineering',
            'behringer', 'doepfer', 'make noise', 'mutable instruments',
            'intellijel', 'expert sleepers', 'focusrite', 'presonus'
        ]

        combined_text = (filename + " " + text[:1000]).lower()

        for manufacturer in manufacturers:
            if manufacturer in combined_text:
                return manufacturer.title()

        return None

    def _extract_model(self, filename: str, text: str) -> Optional[str]:
        """Extract model name/number from filename or text"""
        # Look for model patterns in filename first
        filename_clean = filename.lower().replace('.pdf', '').replace('_', ' ').replace('-', ' ')

        # Common model patterns
        model_patterns = [
            r'(\w+[-_]?\d+[a-zA-Z]*)',  # Like TR-808, JP-8000, etc.
            r'(model \w+)',
            r'(\w+ \d+)',
            r'(mk\s*\d+)',  # Like MK2, MK II
        ]

        for pattern in model_patterns:
            match = re.search(pattern, filename_clean)
            if match:
                return match.group(1).upper()

        # Look in first part of text content
        text_start = text[:500].lower()
        for pattern in model_patterns:
            match = re.search(pattern, text_start)
            if match:
                return match.group(1).upper()

        return None

    def _classify_instrument_type(self, filename: str, text: str) -> Optional[str]:
        """Classify the type of musical instrument"""
        combined_text = (filename + " " + text[:1000]).lower()

        for instrument_type, keywords in self.instrument_keywords.items():
            for keyword in keywords:
                if keyword in combined_text:
                    return instrument_type

        return 'unknown'

    def _classify_section_type(self, text: str) -> Optional[str]:
        """Classify the type of manual section"""
        text_lower = text.lower()

        for section_type, keywords in self.section_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return section_type

        return None

    def chunk_text(self, pages_text: List[Tuple[str, int]], metadata: ManualMetadata,
                   max_chunk_size: int = 1000, overlap: int = 200) -> List[DocumentChunk]:
        """Split text into chunks suitable for vector embedding"""
        chunks = []
        chunk_index = 0

        for text, page_num in pages_text:
            # Clean the text
            text = self._clean_text(text)

            if len(text) < 50:  # Skip very short pages
                continue

            # Split into smaller chunks if needed
            if len(text) <= max_chunk_size:
                section_type = self._classify_section_type(text)
                chunks.append(DocumentChunk(
                    content=text,
                    page_number=page_num,
                    chunk_index=chunk_index,
                    section_type=section_type,
                    metadata=metadata
                ))
                chunk_index += 1
            else:
                # Split long text into overlapping chunks
                text_chunks = self._split_text_with_overlap(text, max_chunk_size, overlap)
                for chunk_text in text_chunks:
                    section_type = self._classify_section_type(chunk_text)
                    chunks.append(DocumentChunk(
                        content=chunk_text,
                        page_number=page_num,
                        chunk_index=chunk_index,
                        section_type=section_type,
                        metadata=metadata
                    ))
                    chunk_index += 1

        return chunks

    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove page numbers and headers/footers (simple heuristic)
        lines = text.split('\n')
        cleaned_lines = []

        for line in lines:
            line = line.strip()
            # Skip very short lines that might be page numbers
            if len(line) > 3 and not line.isdigit():
                cleaned_lines.append(line)

        return ' '.join(cleaned_lines)

    def _split_text_with_overlap(self, text: str, max_size: int, overlap: int) -> List[str]:
        """Split text into overlapping chunks"""
        if len(text) <= max_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + max_size

            if end >= len(text):
                chunks.append(text[start:])
                break

            # Try to break at sentence or word boundary
            chunk = text[start:end]
            last_period = chunk.rfind('.')
            last_space = chunk.rfind(' ')

            if last_period > len(chunk) * 0.8:  # Break at sentence if close to end
                end = start + last_period + 1
            elif last_space > len(chunk) * 0.8:  # Break at word boundary
                end = start + last_space

            chunks.append(text[start:end])
            start = end - overlap

        return chunks

    def process_manual(self, pdf_path: str, max_chunk_size: int = 1000,
                      overlap: int = 200, original_filename: Optional[str] = None) -> Tuple[List[DocumentChunk], ManualMetadata]:
        """Process a complete manual PDF"""
        print(f"Processing manual: {pdf_path}")

        # Extract text from all pages
        pages_text = self.extract_text_from_pdf(pdf_path)

        if not pages_text:
            raise ValueError(f"Could not extract text from {pdf_path}")

        # Combine all text for metadata extraction
        full_text = " ".join([text for text, _ in pages_text])

        # Extract metadata
        metadata = self.extract_metadata(pdf_path, full_text, original_filename)

        # Create chunks
        chunks = self.chunk_text(pages_text, metadata, max_chunk_size, overlap)

        print(f"Extracted {len(chunks)} chunks from {len(pages_text)} pages")
        print(f"Detected: {metadata.manufacturer} {metadata.model} ({metadata.instrument_type})")

        return chunks, metadata