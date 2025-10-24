"""
Patch Advisor State Definition
Defines the state graph structure for the multi-agent patch design system
"""
from typing import TypedDict, List, Dict, Optional, Annotated
from dataclasses import dataclass
import operator


@dataclass
class RequiredModule:
    """A module required for the patch"""
    module_type: str
    role: str  # What this module does in the patch
    specifications: List[str]  # Required specs
    optional: bool = False


@dataclass
class AvailableModule:
    """A module available in user's inventory"""
    module_type: str
    manual_name: str
    manufacturer: str
    model: str
    page_numbers: List[int]
    confidence: float
    features: List[str]


@dataclass
class PatchConnection:
    """A connection between modules"""
    from_module: str
    from_output: str
    to_module: str
    to_input: str
    signal_type: str  # 'audio', 'cv', 'gate'
    note: Optional[str] = None


@dataclass
class PatchInstruction:
    """A single step in the patching instructions"""
    step_number: int
    action: str
    module: str
    manual_reference: Optional[str] = None  # e.g., "Moog Mother-32 p.12"
    settings: Optional[Dict[str, str]] = None


class PatchDesignState(TypedDict):
    """State for the patch design workflow"""

    # Input
    user_query: str
    user_preferences: Optional[Dict]

    # Sound Design Agent outputs
    sound_type: str
    sound_characteristics: List[str]
    synthesis_approach: str

    # Patch Architecture Agent outputs
    required_modules: List[RequiredModule]
    patch_template: Optional[str]
    signal_flow: List[Dict]
    conceptual_diagram: str  # Mermaid diagram

    # Module Matching Agent outputs
    available_modules: List[AvailableModule]
    missing_modules: List[RequiredModule]
    suggested_alternatives: List[Dict]
    match_quality: float  # 0.0 to 1.0

    # Instruction Generation Agent outputs
    mermaid_diagram: str  # Final diagram with actual module names
    patch_connections: List[PatchConnection]
    instructions: List[PatchInstruction]
    parameter_suggestions: Dict[str, str]

    # Final output
    final_response: str

    # Messages for agent communication
    messages: Annotated[List[str], operator.add]

    # Error handling
    errors: Annotated[List[str], operator.add]
