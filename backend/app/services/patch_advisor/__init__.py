"""
Patch Advisor Service
Multi-agent system for intelligent modular synthesis patch design
"""
import logging
from typing import Dict, Optional
from langgraph.graph import StateGraph, END

from app.services.patch_advisor.state import PatchDesignState
from app.services.patch_advisor.agents import (
    SoundDesignAgent,
    PatchArchitectureAgent,
    ModuleMatchingAgent,
    InstructionGenerationAgent
)
from app.services.vector_db.module_inventory import ModuleInventoryManager

logger = logging.getLogger(__name__)


class PatchAdvisor:
    """Main patch advisor orchestrator using LangGraph"""

    def __init__(self, module_inventory: ModuleInventoryManager):
        self.module_inventory = module_inventory

        # Initialize agents
        self.sound_design_agent = SoundDesignAgent()
        self.patch_architecture_agent = PatchArchitectureAgent()
        self.module_matching_agent = ModuleMatchingAgent(module_inventory)
        self.instruction_generation_agent = InstructionGenerationAgent()

        # Build the workflow graph
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(PatchDesignState)

        # Add nodes for each agent
        workflow.add_node("sound_design", self.sound_design_agent)
        workflow.add_node("patch_architecture", self.patch_architecture_agent)
        workflow.add_node("module_matching", self.module_matching_agent)
        workflow.add_node("instruction_generation", self.instruction_generation_agent)

        # Define the flow
        workflow.set_entry_point("sound_design")

        workflow.add_edge("sound_design", "patch_architecture")
        workflow.add_edge("patch_architecture", "module_matching")
        workflow.add_edge("module_matching", "instruction_generation")
        workflow.add_edge("instruction_generation", END)

        return workflow.compile()

    def design_patch(
        self,
        user_query: str,
        user_preferences: Optional[Dict] = None
    ) -> Dict:
        """
        Design a modular synthesis patch based on user's sonic goal

        Args:
            user_query: Description of desired sound (e.g., "dark evolving drone")
            user_preferences: Optional user preferences for personalization

        Returns:
            Dict containing patch design, diagram, instructions, and module info
        """
        logger.info(f"Starting patch design for query: {user_query}")

        # Initialize state
        initial_state = {
            "user_query": user_query,
            "user_preferences": user_preferences,
            "sound_type": "",
            "sound_characteristics": [],
            "synthesis_approach": "",
            "required_modules": [],
            "patch_template": None,
            "signal_flow": [],
            "conceptual_diagram": "",
            "available_modules": [],
            "missing_modules": [],
            "suggested_alternatives": [],
            "match_quality": 0.0,
            "mermaid_diagram": "",
            "patch_connections": [],
            "instructions": [],
            "parameter_suggestions": {},
            "final_response": "",
            "messages": [],
            "errors": []
        }

        try:
            # Run the workflow
            final_state = self.workflow.invoke(initial_state)

            # Format response
            response = {
                "success": True,
                "query": user_query,
                "sound_type": final_state.get("sound_type"),
                "characteristics": final_state.get("sound_characteristics", []),
                "synthesis_approach": final_state.get("synthesis_approach", ""),
                "patch_template": final_state.get("patch_template"),
                "mermaid_diagram": final_state.get("mermaid_diagram", ""),
                "instructions": [
                    {
                        "step": instr.step_number,
                        "action": instr.action,
                        "module": instr.module,
                        "manual_reference": instr.manual_reference,
                        "settings": instr.settings or {}
                    }
                    for instr in final_state.get("instructions", [])
                ],
                "available_modules": [
                    {
                        "type": mod.module_type,
                        "name": mod.manual_name,
                        "manufacturer": mod.manufacturer,
                        "model": mod.model,
                        "confidence": mod.confidence,
                        "features": mod.features
                    }
                    for mod in final_state.get("available_modules", [])
                ],
                "missing_modules": [
                    {
                        "type": mod.module_type,
                        "role": mod.role,
                        "specifications": mod.specifications,
                        "optional": mod.optional
                    }
                    for mod in final_state.get("missing_modules", [])
                ],
                "suggested_alternatives": final_state.get("suggested_alternatives", []),
                "match_quality": final_state.get("match_quality", 0.0),
                "parameter_suggestions": final_state.get("parameter_suggestions", {}),
                "final_response": final_state.get("final_response", ""),
                "agent_messages": final_state.get("messages", []),
                "errors": final_state.get("errors", [])
            }

            logger.info(f"Patch design completed successfully. Match quality: {response['match_quality']:.1%}")
            return response

        except Exception as e:
            logger.error(f"Error in patch design workflow: {e}", exc_info=True)
            return {
                "success": False,
                "query": user_query,
                "error": str(e),
                "final_response": f"Error designing patch: {str(e)}"
            }

    def get_workflow_visualization(self) -> str:
        """Get a visualization of the workflow graph"""
        try:
            # LangGraph can generate Mermaid diagrams of the workflow
            return self.workflow.get_graph().draw_mermaid()
        except Exception as e:
            logger.error(f"Error generating workflow visualization: {e}")
            return "graph LR\n    A[Sound Design] --> B[Patch Architecture]\n    B --> C[Module Matching]\n    C --> D[Instruction Generation]"
