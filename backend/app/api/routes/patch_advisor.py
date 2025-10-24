"""
Patch Advisor API routes
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional

from app.api.models.schemas import (
    PatchDesignRequest,
    PatchDesignResponse,
    ModuleInventoryResponse,
    ModuleInventoryItem,
    ModuleCapabilityStats
)
from app.core.dependencies import get_patch_advisor, get_module_inventory
from app.services.patch_advisor import PatchAdvisor
from app.services.vector_db.module_inventory import ModuleInventoryManager

router = APIRouter()


@router.post("/design", response_model=PatchDesignResponse)
async def design_patch(
    request: PatchDesignRequest,
    patch_advisor: Optional[PatchAdvisor] = Depends(get_patch_advisor),
):
    """
    Design a modular synthesis patch based on user's sonic goal

    This endpoint uses a multi-agent system to:
    1. Analyze the desired sound type
    2. Design a conceptual patch architecture
    3. Match required modules to user's inventory (from uploaded manuals)
    4. Generate step-by-step patching instructions with Mermaid diagram
    """
    if patch_advisor is None:
        raise HTTPException(
            status_code=503,
            detail="Patch advisor not available. Please check Anthropic API key configuration.",
        )

    try:
        result = patch_advisor.design_patch(
            user_query=request.query,
            user_preferences=request.preferences
        )

        return PatchDesignResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error designing patch: {str(e)}"
        )


@router.get("/module-inventory", response_model=ModuleInventoryResponse)
async def get_module_inventory(
    module_inventory: ModuleInventoryManager = Depends(get_module_inventory),
):
    """
    Get list of all module inventories extracted from uploaded manuals
    """
    try:
        inventories = module_inventory.get_all_module_inventories()

        items = [
            ModuleInventoryItem(
                filename=inv["metadata"]["filename"],
                manual=inv["metadata"]["display_name"],
                manufacturer=inv["metadata"]["manufacturer"],
                model=inv["metadata"]["model"],
                capabilities=inv["metadata"]["top_capabilities"].split(",")
            )
            for inv in inventories
        ]

        return ModuleInventoryResponse(
            inventories=items,
            total_count=len(items)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving module inventory: {str(e)}"
        )


@router.get("/module-inventory/{filename}")
async def get_manual_modules(
    filename: str,
    module_inventory: ModuleInventoryManager = Depends(get_module_inventory),
):
    """
    Get module capabilities for a specific manual
    """
    try:
        inventory = module_inventory.get_module_inventory_for_manual(filename)

        if not inventory:
            raise HTTPException(
                status_code=404,
                detail=f"No module inventory found for {filename}"
            )

        return {
            "filename": filename,
            "manual": inventory["metadata"]["display_name"],
            "manufacturer": inventory["metadata"]["manufacturer"],
            "model": inventory["metadata"]["model"],
            "capabilities": inventory["metadata"]["top_capabilities"].split(","),
            "capability_text": inventory["capability_text"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving module inventory: {str(e)}"
        )


@router.get("/capability-stats", response_model=ModuleCapabilityStats)
async def get_capability_stats(
    module_inventory: ModuleInventoryManager = Depends(get_module_inventory),
):
    """
    Get statistics about detected module capabilities across all manuals
    """
    try:
        stats = module_inventory.get_capability_statistics()

        return ModuleCapabilityStats(**stats)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving capability stats: {str(e)}"
        )


@router.post("/search-modules")
async def search_modules_by_capability(
    query: str,
    n_results: int = 5,
    module_inventory: ModuleInventoryManager = Depends(get_module_inventory),
):
    """
    Search for modules by capability description

    Example queries:
    - "oscillator with FM input"
    - "filter with high resonance"
    - "envelope generator"
    """
    try:
        results = module_inventory.search_modules_by_capability(
            capability_query=query,
            n_results=n_results
        )

        return {
            "query": query,
            "results": results,
            "count": len(results)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching modules: {str(e)}"
        )


@router.get("/workflow-graph")
async def get_workflow_graph(
    patch_advisor: Optional[PatchAdvisor] = Depends(get_patch_advisor),
):
    """
    Get Mermaid diagram of the patch advisor workflow
    """
    if patch_advisor is None:
        raise HTTPException(
            status_code=503,
            detail="Patch advisor not available.",
        )

    try:
        diagram = patch_advisor.get_workflow_visualization()

        return {
            "mermaid_diagram": diagram,
            "description": "Multi-agent workflow: Sound Design → Patch Architecture → Module Matching → Instruction Generation"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating workflow graph: {str(e)}"
        )
