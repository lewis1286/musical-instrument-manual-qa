"""
Q&A API routes
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends

from app.api.models.schemas import (
    QARequest,
    QAResponse,
    QASource,
    SuggestionsRequest,
    SuggestionsResponse,
    ConversationHistoryResponse,
)
from app.core.dependencies import get_qa_system, get_chroma_manager
from app.services.rag_pipeline.qa_system import MusicalInstrumentQA
from app.services.vector_db.chroma_manager import ChromaManager

router = APIRouter()


@router.post("/ask", response_model=QAResponse)
async def ask_question(
    request: QARequest,
    qa_system: Optional[MusicalInstrumentQA] = Depends(get_qa_system),
):
    """
    Ask a question about the uploaded manuals
    """
    if qa_system is None:
        raise HTTPException(
            status_code=503,
            detail="QA system not available. Please check Anthropic API key configuration.",
        )

    try:
        # Prepare filters
        filters = {}
        if request.instrument_type:
            filters["instrument_type"] = request.instrument_type
        if request.manufacturer:
            filters["manufacturer"] = request.manufacturer

        # Get answer
        response = qa_system.answer_question(
            query=request.question, max_sources=request.max_sources
        )

        # Convert sources to API model
        sources = [
            QASource(
                filename=source["filename"],
                display_name=source.get("display_name", source["filename"]),
                page_number=source["page_number"],
                manufacturer=source.get("manufacturer", "unknown"),
                model=source.get("model", "unknown"),
                instrument_type=source.get("instrument_type", "unknown"),
                section_type=source.get("section_type", "general"),
                content_preview=source["content_preview"],
            )
            for source in response.sources
        ]

        return QAResponse(
            answer=response.answer,
            sources=sources,
            query=request.question,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")


@router.post("/suggestions", response_model=SuggestionsResponse)
async def get_suggestions(
    request: SuggestionsRequest,
    qa_system: Optional[MusicalInstrumentQA] = Depends(get_qa_system),
    chroma_manager: ChromaManager = Depends(get_chroma_manager),
):
    """
    Get suggested questions based on available manuals
    """
    if qa_system is None:
        # Return basic suggestions if QA system not available
        return SuggestionsResponse(
            suggestions=[
                "How do I set up MIDI connections?",
                "What are the audio input specifications?",
                "How do I save presets?",
                "How do I connect to my computer?",
                "What is the power consumption?",
            ]
        )

    try:
        # Get instrument type from request or available manuals
        instrument_type = request.instrument_type
        if not instrument_type:
            # Get first available instrument type
            types = chroma_manager.get_unique_values("instrument_type")
            instrument_type = types[0] if types else None

        suggestions = qa_system.suggest_questions(instrument_type)

        return SuggestionsResponse(suggestions=suggestions)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting suggestions: {str(e)}"
        )


@router.get("/history", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    qa_system: Optional[MusicalInstrumentQA] = Depends(get_qa_system),
):
    """
    Get conversation history
    """
    if qa_system is None:
        return ConversationHistoryResponse(history=[])

    try:
        history = qa_system.get_conversation_history()
        return ConversationHistoryResponse(history=history)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting history: {str(e)}")


@router.delete("/history")
async def clear_conversation_history(
    qa_system: Optional[MusicalInstrumentQA] = Depends(get_qa_system),
):
    """
    Clear conversation history
    """
    if qa_system is None:
        return {"success": True, "message": "No history to clear"}

    try:
        qa_system.clear_conversation()
        return {"success": True, "message": "Conversation history cleared"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing history: {str(e)}")
