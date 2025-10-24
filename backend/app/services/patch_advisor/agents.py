"""
Patch Advisor Agents
Specialized agents for patch design workflow
"""
import os
import logging
from typing import Dict, List
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from app.services.synthesis_knowledge import SynthesisKnowledgeBase
from app.services.patch_advisor.state import (
    PatchDesignState,
    RequiredModule,
    AvailableModule,
    PatchConnection,
    PatchInstruction
)
from app.services.vector_db.module_inventory import ModuleInventoryManager
from app.core.config import settings

logger = logging.getLogger(__name__)


class SoundDesignAgent:
    """Analyzes user's sonic goal and determines synthesis approach"""

    def __init__(self):
        self.kb = SynthesisKnowledgeBase()
        self.llm = ChatAnthropic(
            model=settings.anthropic_model,
            temperature=0.3,
            max_tokens=1000
        )

    def __call__(self, state: PatchDesignState) -> Dict:
        """Analyze user query and determine sound type and approach"""
        logger.info("Sound Design Agent: Analyzing user query")

        user_query = state["user_query"]

        # Get all available sound types for context
        sound_types = self.kb.get_all_sound_types()
        sound_type_descriptions = []
        for st in sound_types:
            info = self.kb.get_sound_type_info(st)
            if info:
                sound_type_descriptions.append(
                    f"- {st}: {info.get('description', '')}"
                )

        # Create prompt for LLM
        system_prompt = """You are an expert in modular synthesis sound design.
Analyze the user's request and identify:
1. The primary sound type they want to create
2. Key sonic characteristics
3. The recommended synthesis approach

Available sound types:
{sound_types}

Respond in this exact format:
SOUND_TYPE: [one of the sound types above]
CHARACTERISTICS: [comma-separated list of sonic qualities]
APPROACH: [brief description of synthesis strategy]
"""

        prompt = system_prompt.format(
            sound_types="\n".join(sound_type_descriptions)
        )

        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=f"User wants to create: {user_query}")
        ]

        response = self.llm(messages)
        content = response.content

        # Parse response
        sound_type = "drone"  # default
        characteristics = []
        synthesis_approach = ""

        for line in content.split("\n"):
            if line.startswith("SOUND_TYPE:"):
                sound_type = line.split(":", 1)[1].strip().lower()
            elif line.startswith("CHARACTERISTICS:"):
                chars = line.split(":", 1)[1].strip()
                characteristics = [c.strip() for c in chars.split(",")]
            elif line.startswith("APPROACH:"):
                synthesis_approach = line.split(":", 1)[1].strip()

        logger.info(f"Identified sound type: {sound_type}")
        logger.info(f"Characteristics: {characteristics}")

        return {
            "sound_type": sound_type,
            "sound_characteristics": characteristics,
            "synthesis_approach": synthesis_approach,
            "messages": [f"Sound Design: Identified {sound_type} sound"]
        }


class PatchArchitectureAgent:
    """Designs conceptual patch architecture based on sound requirements"""

    def __init__(self):
        self.kb = SynthesisKnowledgeBase()
        self.llm = ChatAnthropic(
            model=settings.anthropic_model,
            temperature=0.2,
            max_tokens=2000
        )

    def __call__(self, state: PatchDesignState) -> Dict:
        """Design patch architecture"""
        logger.info("Patch Architecture Agent: Designing patch")

        sound_type = state["sound_type"]
        characteristics = state.get("sound_characteristics", [])

        # Get sound type requirements
        sound_info = self.kb.get_sound_type_info(sound_type)
        if not sound_info:
            logger.error(f"Unknown sound type: {sound_type}")
            return {
                "errors": [f"Unknown sound type: {sound_type}"],
                "messages": ["Patch Architecture: Error - unknown sound type"]
            }

        # Get matching patch templates
        templates = self.kb.find_templates_for_sound(sound_type)

        # Extract required modules from sound type
        required_modules = []
        for mod_req in sound_info.get("required_modules", []):
            required_modules.append(
                RequiredModule(
                    module_type=mod_req["type"],
                    role=f"Required for {sound_type}",
                    specifications=mod_req.get("specs", []),
                    optional=False
                )
            )

        # Add optional modules
        for opt_mod in sound_info.get("optional_modules", []):
            required_modules.append(
                RequiredModule(
                    module_type=opt_mod["type"],
                    role=f"Optional: {opt_mod.get('priority', 'low')} priority",
                    specifications=[],
                    optional=True
                )
            )

        # Choose best template or use generic
        patch_template = None
        conceptual_diagram = ""
        signal_flow = []

        if templates:
            # Use first matching template
            template = templates[0]
            patch_template = template["name"]
            signal_flow = template.get("signal_flow", [])
            conceptual_diagram = template.get("mermaid_template", "")

            logger.info(f"Using patch template: {patch_template}")
        else:
            # Generate basic signal flow
            logger.info("No template found, using sound type requirements")
            conceptual_diagram = self._generate_basic_diagram(required_modules)

        return {
            "required_modules": required_modules,
            "patch_template": patch_template,
            "signal_flow": signal_flow,
            "conceptual_diagram": conceptual_diagram,
            "messages": [f"Patch Architecture: Designed {patch_template or 'custom'} patch with {len(required_modules)} modules"]
        }

    def _generate_basic_diagram(self, modules: List[RequiredModule]) -> str:
        """Generate a basic Mermaid diagram from module list"""
        lines = ["graph LR"]

        # Create simple chain based on typical signal flow
        module_order = ["sequencer", "vco", "vcf", "vca", "reverb", "delay"]
        present_modules = [m.module_type for m in modules if m.module_type in module_order]

        for i in range(len(present_modules) - 1):
            from_mod = present_modules[i].upper()
            to_mod = present_modules[i + 1].upper()
            lines.append(f"    {from_mod} --> {to_mod}")

        # Add modulators
        if "lfo" in [m.module_type for m in modules]:
            lines.append("    LFO -.->|Mod| VCF")
        if "envelope" in [m.module_type for m in modules]:
            lines.append("    ENV -.->|Mod| VCA")

        return "\n".join(lines)


class ModuleMatchingAgent:
    """Matches required modules to user's available inventory"""

    def __init__(self, module_inventory: ModuleInventoryManager):
        self.module_inventory = module_inventory
        self.kb = SynthesisKnowledgeBase()

    def __call__(self, state: PatchDesignState) -> Dict:
        """Match required modules to available inventory"""
        logger.info("Module Matching Agent: Matching modules to inventory")

        required_modules = state["required_modules"]

        available_modules = []
        missing_modules = []
        suggested_alternatives = []

        # Search for each required module type
        for req_mod in required_modules:
            module_type = req_mod.module_type

            # Search inventory for this module type
            matches = self.module_inventory.search_modules_by_capability(
                f"{module_type} module",
                n_results=3
            )

            if matches:
                # Found matching modules
                for match in matches:
                    available_modules.append(
                        AvailableModule(
                            module_type=module_type,
                            manual_name=match["manual"],
                            manufacturer=match["manufacturer"],
                            model=match["model"],
                            page_numbers=[],  # Will be populated with specific pages
                            confidence=1.0 - (match.get("distance", 0) / 2.0),
                            features=match.get("capabilities", [])
                        )
                    )

                logger.info(f"Found {len(matches)} matches for {module_type}")
            else:
                # No matches found
                if not req_mod.optional:
                    missing_modules.append(req_mod)

                    # Look for substitutes
                    alternatives = self.kb.suggest_alternatives(module_type)
                    if alternatives:
                        suggested_alternatives.append({
                            "missing_module": module_type,
                            "alternatives": alternatives
                        })

                logger.warning(f"No matches found for {module_type}")

        # Calculate match quality
        total_required = len([m for m in required_modules if not m.optional])
        matched = total_required - len(missing_modules)
        match_quality = matched / total_required if total_required > 0 else 0.0

        logger.info(f"Match quality: {match_quality:.1%} ({matched}/{total_required} required modules)")

        return {
            "available_modules": available_modules,
            "missing_modules": missing_modules,
            "suggested_alternatives": suggested_alternatives,
            "match_quality": match_quality,
            "messages": [f"Module Matching: Found {len(available_modules)} modules, {len(missing_modules)} missing"]
        }


class InstructionGenerationAgent:
    """Generates patching instructions and Mermaid diagram with actual module names"""

    def __init__(self):
        self.kb = SynthesisKnowledgeBase()
        self.llm = ChatAnthropic(
            model=settings.anthropic_model,
            temperature=0.1,
            max_tokens=3000
        )

    def __call__(self, state: PatchDesignState) -> Dict:
        """Generate final instructions and diagram"""
        logger.info("Instruction Generation Agent: Creating instructions")

        sound_type = state["sound_type"]
        required_modules = state["required_modules"]
        available_modules = state["available_modules"]
        missing_modules = state["missing_modules"]
        signal_flow = state.get("signal_flow", [])
        conceptual_diagram = state.get("conceptual_diagram", "")

        # Create module mapping (module type -> actual module name)
        module_mapping = {}
        for avail in available_modules:
            if avail.module_type not in module_mapping:
                module_mapping[avail.module_type] = {
                    "name": f"{avail.manufacturer} {avail.model}",
                    "display_name": avail.manual_name,
                    "pages": avail.page_numbers
                }

        # Generate Mermaid diagram with actual module names
        mermaid_diagram = self._generate_final_diagram(
            conceptual_diagram,
            module_mapping,
            missing_modules
        )

        # Generate patch connections
        patch_connections = self._generate_connections(
            signal_flow,
            module_mapping
        )

        # Generate step-by-step instructions
        instructions = self._generate_instructions(
            signal_flow,
            module_mapping,
            missing_modules,
            sound_type
        )

        # Get parameter suggestions
        sound_info = self.kb.get_sound_type_info(sound_type)
        parameter_suggestions = sound_info.get("example_parameters", {}) if sound_info else {}

        # Generate final response text
        final_response = self._format_final_response(
            state,
            mermaid_diagram,
            instructions,
            parameter_suggestions,
            missing_modules
        )

        return {
            "mermaid_diagram": mermaid_diagram,
            "patch_connections": patch_connections,
            "instructions": instructions,
            "parameter_suggestions": parameter_suggestions,
            "final_response": final_response,
            "messages": ["Instruction Generation: Created final patch guide"]
        }

    def _generate_final_diagram(
        self,
        conceptual_diagram: str,
        module_mapping: Dict,
        missing_modules: List[RequiredModule]
    ) -> str:
        """Replace generic module names with actual module names in diagram"""
        diagram = conceptual_diagram

        # Clean the diagram - ensure proper Mermaid syntax
        for module_type, info in module_mapping.items():
            old_name = module_type.upper()
            display_name = info['display_name'].replace(' ', '_')

            # Replace node definitions: VCO[...] -> VCO["VCO: Display Name"]
            import re
            pattern = rf'{old_name}\[([^\]]*)\]'
            replacement = f'{old_name}["{old_name}: {info["display_name"]}"]'
            diagram = re.sub(pattern, replacement, diagram)

        return diagram

    def _generate_connections(
        self,
        signal_flow: List[Dict],
        module_mapping: Dict
    ) -> List[PatchConnection]:
        """Generate connection list from signal flow"""
        connections = []

        for i, step in enumerate(signal_flow):
            if "connections" in step:
                for conn in step["connections"]:
                    from_mod = conn.get("from", "")
                    to_input = conn.get("to_input", "")
                    signal_type = conn.get("signal_type", "cv")

                    connections.append(
                        PatchConnection(
                            from_module=from_mod,
                            from_output="main",
                            to_module=step.get("module_type", ""),
                            to_input=to_input,
                            signal_type=signal_type,
                            note=conn.get("note")
                        )
                    )

        return connections

    def _generate_instructions(
        self,
        signal_flow: List[Dict],
        module_mapping: Dict,
        missing_modules: List[RequiredModule],
        sound_type: str
    ) -> List[PatchInstruction]:
        """Generate step-by-step patching instructions"""
        instructions = []

        for i, step in enumerate(signal_flow, 1):
            module_type = step.get("module_type", "")
            action = step.get("action", "")

            # Get actual module name if available
            module_name = module_type
            manual_ref = None
            if module_type in module_mapping:
                module_info = module_mapping[module_type]
                module_name = module_info["display_name"]
                if module_info.get("pages"):
                    manual_ref = f"{module_name} p.{module_info['pages'][0]}"

            # Get settings if specified
            settings = step.get("settings")

            instructions.append(
                PatchInstruction(
                    step_number=i,
                    action=action,
                    module=module_name,
                    manual_reference=manual_ref,
                    settings=settings
                )
            )

        return instructions

    def _format_final_response(
        self,
        state: PatchDesignState,
        mermaid_diagram: str,
        instructions: List[PatchInstruction],
        parameters: Dict,
        missing: List[RequiredModule]
    ) -> str:
        """Format the complete response"""
        lines = []

        # Header
        sound_type = state["sound_type"]
        lines.append(f"# {sound_type.title()} Patch Design\n")

        # Sound analysis
        characteristics = state.get("sound_characteristics", [])
        if characteristics:
            lines.append(f"**Sound Characteristics:** {', '.join(characteristics)}\n")

        # Approach
        approach = state.get("synthesis_approach", "")
        if approach:
            lines.append(f"**Synthesis Approach:** {approach}\n")

        # Match quality
        match_quality = state.get("match_quality", 0.0)
        lines.append(f"**Match Quality:** {match_quality:.0%}\n")

        # Missing modules warning
        if missing:
            lines.append("\n## ⚠️ Missing Modules\n")
            lines.append("You'll need these modules (not found in your manuals):\n")
            for mod in missing:
                lines.append(f"- **{mod.module_type.upper()}**: {mod.role}")
            lines.append("")

        # Signal flow diagram
        lines.append("\n## Signal Flow\n")
        lines.append(f"```mermaid\n{mermaid_diagram}\n```\n")

        # Instructions
        lines.append("\n## Patching Instructions\n")
        for instr in instructions:
            manual_ref = f" *(see {instr.manual_reference})*" if instr.manual_reference else ""
            lines.append(f"{instr.step_number}. **{instr.module}**: {instr.action}{manual_ref}")

            if instr.settings:
                for param, value in instr.settings.items():
                    lines.append(f"   - {param}: {value}")

        # Parameter suggestions
        if parameters:
            lines.append("\n## Suggested Parameters\n")
            for param, value in parameters.items():
                lines.append(f"- **{param}**: {value}")

        return "\n".join(lines)
