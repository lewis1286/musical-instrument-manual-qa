"""
Synthesis knowledge base for modular synthesis techniques and capabilities
"""
from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml


class SynthesisKnowledgeBase:
    """Loads and provides access to synthesis domain knowledge"""

    def __init__(self):
        self.knowledge_path = Path(__file__).parent
        self._sound_types: Optional[Dict] = None
        self._module_taxonomy: Optional[Dict] = None
        self._patch_templates: Optional[Dict] = None

    @property
    def sound_types(self) -> Dict:
        """Get sound types database"""
        if self._sound_types is None:
            with open(self.knowledge_path / "sound_types.yaml") as f:
                self._sound_types = yaml.safe_load(f)
        return self._sound_types

    @property
    def module_taxonomy(self) -> Dict:
        """Get module capability taxonomy"""
        if self._module_taxonomy is None:
            with open(self.knowledge_path / "module_taxonomy.yaml") as f:
                self._module_taxonomy = yaml.safe_load(f)
        return self._module_taxonomy

    @property
    def patch_templates(self) -> Dict:
        """Get patch templates library"""
        if self._patch_templates is None:
            with open(self.knowledge_path / "patch_templates.yaml") as f:
                self._patch_templates = yaml.safe_load(f)
        return self._patch_templates

    def get_sound_type_info(self, sound_type: str) -> Optional[Dict]:
        """Get information about a specific sound type"""
        return self.sound_types.get("sound_types", {}).get(sound_type)

    def get_module_type_info(self, module_type: str) -> Optional[Dict]:
        """Get information about a specific module type"""
        return self.module_taxonomy.get("module_types", {}).get(module_type)

    def get_patch_template(self, template_name: str) -> Optional[Dict]:
        """Get a specific patch template"""
        return self.patch_templates.get("templates", {}).get(template_name)

    def find_templates_for_sound(self, sound_type: str) -> List[Dict]:
        """Find all patch templates suitable for a sound type"""
        matching_templates = []
        for template_name, template_data in self.patch_templates.get("templates", {}).items():
            if sound_type in template_data.get("sound_types", []):
                matching_templates.append({
                    "name": template_name,
                    **template_data
                })
        return matching_templates

    def get_module_detection_patterns(self, module_type: str) -> List[str]:
        """Get regex patterns for detecting a module type in text"""
        module_info = self.get_module_type_info(module_type)
        if module_info:
            return module_info.get("detection_patterns", [])
        return []

    def get_all_module_types(self) -> List[str]:
        """Get list of all module types"""
        return list(self.module_taxonomy.get("module_types", {}).keys())

    def get_all_sound_types(self) -> List[str]:
        """Get list of all sound types"""
        return list(self.sound_types.get("sound_types", {}).keys())

    def get_substitution_rules(self) -> List[Dict]:
        """Get module substitution rules"""
        return self.patch_templates.get("substitution_rules", [])

    def suggest_alternatives(self, missing_module: str) -> List[Dict]:
        """Get alternative modules if a required one is missing"""
        for rule in self.get_substitution_rules():
            if rule.get("if_missing") == missing_module:
                return rule.get("alternatives", [])
        return []
