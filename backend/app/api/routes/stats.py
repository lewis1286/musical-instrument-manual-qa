"""
Statistics and database management API routes
"""
from fastapi import APIRouter, HTTPException, Depends

from app.api.models.schemas import DatabaseStats, ResetDatabaseResponse
from app.core.dependencies import get_chroma_manager, reset_singletons
from app.services.vector_db.chroma_manager import ChromaManager

router = APIRouter()


@router.get("/stats", response_model=DatabaseStats)
async def get_database_stats(chroma_manager: ChromaManager = Depends(get_chroma_manager)):
    """
    Get database statistics
    """
    try:
        stats = chroma_manager.get_database_stats()

        return DatabaseStats(
            total_manuals=stats.get("total_manuals", 0),
            total_chunks=stats.get("total_chunks", 0),
            manufacturers=stats.get("manufacturers", []),
            instrument_types=stats.get("instrument_types", []),
            section_types=stats.get("section_types", []),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")


@router.post("/database/reset", response_model=ResetDatabaseResponse)
async def reset_database(chroma_manager: ChromaManager = Depends(get_chroma_manager)):
    """
    Reset the entire database (delete all manuals and data)
    WARNING: This action cannot be undone!
    """
    try:
        success = chroma_manager.reset_database()

        if success:
            # Reset singleton instances to force recreation
            reset_singletons()

            return ResetDatabaseResponse(
                success=True, message="Database reset successfully"
            )
        else:
            return ResetDatabaseResponse(
                success=False, message="Failed to reset database"
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting database: {str(e)}")


@router.get("/filters/manufacturers")
async def get_manufacturers(chroma_manager: ChromaManager = Depends(get_chroma_manager)):
    """Get list of unique manufacturers"""
    try:
        manufacturers = chroma_manager.get_unique_values("manufacturer")
        return {"manufacturers": manufacturers}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting manufacturers: {str(e)}"
        )


@router.get("/filters/instrument-types")
async def get_instrument_types(
    chroma_manager: ChromaManager = Depends(get_chroma_manager)
):
    """Get list of unique instrument types"""
    try:
        types = chroma_manager.get_unique_values("instrument_type")
        return {"instrument_types": types}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting instrument types: {str(e)}"
        )
