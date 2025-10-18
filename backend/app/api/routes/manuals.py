"""
Manual management API routes
"""
import os
import tempfile
from typing import Dict
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse

from app.api.models.schemas import (
    ManualMetadataResponse,
    ManualSaveRequest,
    ManualListResponse,
    ManualListItem,
    ManualDeleteResponse,
    ErrorResponse,
    PendingManual,
)
from app.core.dependencies import get_chroma_manager, get_pdf_extractor
from app.services.vector_db.chroma_manager import ChromaManager
from app.services.pdf_processor.pdf_extractor import PDFExtractor

router = APIRouter()

# In-memory storage for pending manuals (in production, use Redis or similar)
pending_manuals: Dict[str, PendingManual] = {}


@router.post("/process", response_model=PendingManual)
async def process_manual(
    file: UploadFile = File(...),
    pdf_extractor: PDFExtractor = Depends(get_pdf_extractor),
):
    """
    Stage 1: Process uploaded PDF and extract metadata
    Returns: Pending manual with extracted metadata for user review
    """
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        # Process the PDF with original filename for better metadata extraction
        chunks, metadata = pdf_extractor.process_manual(tmp_file_path, original_filename=file.filename)

        # Create pending manual object
        pending = PendingManual(
            temp_file_path=tmp_file_path,
            original_filename=file.filename,
            metadata=ManualMetadataResponse(
                filename=metadata.filename,
                display_name=metadata.display_name,
                manufacturer=metadata.manufacturer,
                model=metadata.model,
                instrument_type=metadata.instrument_type,
                total_pages=metadata.total_pages,
            ),
            chunk_count=len(chunks),
        )

        # Store in memory (use session ID in production)
        session_id = tmp_file_path  # Simple key for now
        pending_manuals[session_id] = {
            "pending": pending,
            "chunks": chunks,
            "metadata_obj": metadata,
        }

        return pending

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing manual: {str(e)}")


@router.post("/save")
async def save_manual(
    request: ManualSaveRequest,
    chroma_manager: ChromaManager = Depends(get_chroma_manager),
):
    """
    Stage 2: Save manual with user-confirmed metadata
    """
    # Find pending manual by filename
    session_id = None
    for sid, data in pending_manuals.items():
        if data["pending"].original_filename == request.filename:
            session_id = sid
            break

    if not session_id:
        raise HTTPException(status_code=404, detail="Pending manual not found")

    try:
        data = pending_manuals[session_id]
        chunks = data["chunks"]
        metadata_obj = data["metadata_obj"]

        # Update metadata with user inputs
        metadata_obj.display_name = request.display_name
        metadata_obj.manufacturer = request.manufacturer
        metadata_obj.model = request.model
        metadata_obj.instrument_type = request.instrument_type

        # Update all chunks with new metadata
        for chunk in chunks:
            chunk.metadata = metadata_obj

        # Add to vector database
        chroma_manager.add_manual_chunks(chunks)

        # Clean up temporary file
        os.unlink(data["pending"].temp_file_path)

        # Remove from pending
        del pending_manuals[session_id]

        return {
            "success": True,
            "message": f"Manual '{request.display_name}' saved successfully",
            "filename": request.filename,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving manual: {str(e)}")


@router.get("/", response_model=ManualListResponse)
async def list_manuals(chroma_manager: ChromaManager = Depends(get_chroma_manager)):
    """Get list of all uploaded manuals"""
    try:
        manuals_data = chroma_manager.get_all_manuals()

        manuals = [
            ManualListItem(
                filename=m["filename"],
                display_name=m.get("display_name", m["filename"]),
                manufacturer=m.get("manufacturer", "unknown"),
                model=m.get("model", "unknown"),
                instrument_type=m.get("instrument_type", "unknown"),
                total_pages=m.get("total_pages", 0),
                chunk_count=m.get("chunk_count", 0),
            )
            for m in manuals_data
        ]

        return ManualListResponse(manuals=manuals, total_count=len(manuals))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing manuals: {str(e)}")


@router.delete("/{filename}", response_model=ManualDeleteResponse)
async def delete_manual(
    filename: str, chroma_manager: ChromaManager = Depends(get_chroma_manager)
):
    """Delete a manual by filename"""
    try:
        success = chroma_manager.delete_manual(filename)

        if success:
            return ManualDeleteResponse(
                success=True,
                message=f"Manual '{filename}' deleted successfully",
                filename=filename,
            )
        else:
            return ManualDeleteResponse(
                success=False,
                message=f"Manual '{filename}' not found",
                filename=filename,
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting manual: {str(e)}")


@router.post("/cancel/{filename}")
async def cancel_upload(filename: str):
    """Cancel a pending manual upload"""
    # Find and remove pending manual
    session_id = None
    for sid, data in pending_manuals.items():
        if data["pending"].original_filename == filename:
            session_id = sid
            break

    if not session_id:
        raise HTTPException(status_code=404, detail="Pending manual not found")

    try:
        # Clean up temporary file
        os.unlink(pending_manuals[session_id]["pending"].temp_file_path)

        # Remove from pending
        del pending_manuals[session_id]

        return {"success": True, "message": "Upload cancelled"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cancelling upload: {str(e)}")
