"""
Pydantic models for API request/response schemas
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# Manual-related models
class ManualMetadataResponse(BaseModel):
    """Metadata extracted from a manual"""
    filename: str
    display_name: str
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    instrument_type: Optional[str] = None
    total_pages: int
    chunk_count: Optional[int] = None


class ManualProcessRequest(BaseModel):
    """Request for processing uploaded PDF (not used directly, handled as multipart)"""
    pass


class ManualSaveRequest(BaseModel):
    """Request for saving a manual with metadata"""
    filename: str
    display_name: str
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    instrument_type: Optional[str] = None


class ManualListItem(BaseModel):
    """Manual list item"""
    filename: str
    display_name: str
    manufacturer: str
    model: str
    instrument_type: str
    total_pages: int
    chunk_count: int


class ManualListResponse(BaseModel):
    """Response for listing all manuals"""
    manuals: List[ManualListItem]
    total_count: int


class ManualDeleteResponse(BaseModel):
    """Response for deleting a manual"""
    success: bool
    message: str
    filename: str


# Q&A related models
class QASource(BaseModel):
    """Source citation for QA answer"""
    filename: str
    display_name: str
    page_number: int
    manufacturer: str
    model: str
    instrument_type: str
    section_type: str
    content_preview: str


class QARequest(BaseModel):
    """Request for asking a question"""
    question: str = Field(..., min_length=1, max_length=500)
    max_sources: int = Field(default=5, ge=1, le=10)
    instrument_type: Optional[str] = None
    manufacturer: Optional[str] = None


class QAResponse(BaseModel):
    """Response for a question"""
    answer: str
    sources: List[QASource]
    query: str


class SuggestionsRequest(BaseModel):
    """Request for question suggestions"""
    instrument_type: Optional[str] = None


class SuggestionsResponse(BaseModel):
    """Response with suggested questions"""
    suggestions: List[str]


class ConversationHistoryResponse(BaseModel):
    """Response with conversation history"""
    history: List[Dict[str, str]]


# Stats related models
class DatabaseStats(BaseModel):
    """Database statistics"""
    total_manuals: int
    total_chunks: int
    manufacturers: List[str]
    instrument_types: List[str]
    section_types: List[str] = []


class ResetDatabaseResponse(BaseModel):
    """Response for database reset"""
    success: bool
    message: str


# General response models
class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None


class SuccessResponse(BaseModel):
    """Generic success response"""
    success: bool
    message: str


# Temporary storage for pending manual (session-like)
class PendingManual(BaseModel):
    """Pending manual awaiting metadata confirmation"""
    temp_file_path: str
    original_filename: str
    metadata: ManualMetadataResponse
    chunk_count: int
